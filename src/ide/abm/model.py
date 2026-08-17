"""Modèle à agents : société sur un compas politique sous flux algorithmique.

Réimplémentation du modèle esquissé dans le fil de travail (dont le prototype
``pygame`` est conservé sous ``legacy/``), débarrassée de sa couche graphique afin
d'être déterministe, testable et exécutable en conteneur.

Le pas de temps enchaîne quatre mécanismes :

1. **Conformisme filtré.** Chaque individu cherche un interlocuteur dont l'opinion
   se situe à moins de ``bubble_threshold`` de la sienne, et s'en rapproche. Ce
   seuil *est* la bulle de filtres : c'est le paramètre que l'algorithme de
   recommandation contrôle, et le réduire revient à abaisser la température
   sociale locale.
2. **Contagion.** Un individu contaminé transmet sa croyance fausse avec une
   probabilité fixe, et la contamination radicalise sa cible.
3. **Influence médiatique.** Les sources fixes attirent les individus passant à
   leur portée — le champ :math:`H` du modèle d'Ising, rendu local.
4. **Vérification.** Les fact-checkers patrouillent et tentent de dissiper les
   croyances fausses qu'ils croisent.

Le modèle produit à chaque pas les observables de :mod:`ide.abm.metrics`, dont
l'IDE moyen : c'est le lien direct entre le modèle à agents et la métrique de
régulation proposée au régulateur.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ide.abm.agents import Citizen, FactChecker, MediaOutlet, quadrant_label
from ide.abm.metrics import SocietyMetrics, measure

__all__ = [
    "SocietyModel",
    "SocietyParameters",
    "default_media_landscape",
]


def default_media_landscape(reach: float = 0.5) -> tuple[MediaOutlet, ...]:
    """Paysage médiatique par défaut : une source par quadrant du compas.

    Reproduit les quatre médias du prototype d'origine, en remplaçant leurs noms
    de couleurs par leur position idéologique.
    """
    return (
        MediaOutlet("média gauche-libertaire", np.array([-0.8, -0.8]), reach),
        MediaOutlet("média gauche-autoritaire", np.array([-0.8, 0.8]), reach),
        MediaOutlet("média droite-libertaire", np.array([0.8, -0.8]), reach),
        MediaOutlet("média droite-autoritaire", np.array([0.8, 0.8]), reach),
    )


@dataclass
class SocietyParameters:
    """Paramètres d'une société simulée.

    Args:
        population: nombre d'individus.
        bubble_threshold: distance maximale d'opinion au-delà de laquelle deux
            individus ne se rencontrent jamais. Grand, la société est ouverte ;
            petit, chacun est enfermé avec ses semblables.
        social_temperature: écart-type de l'agitation individuelle appliquée à
            chaque pas. C'est le :math:`T` des modèles d'Ising et de Fokker-Planck,
            porté à l'échelle de l'agent : la part de fluctuation, de doute et
            d'irrationalité qui empêche une opinion de se figer.

            Ce paramètre était **absent du prototype d'origine**, et cette absence
            n'était pas anodine : sans agitation, le conformisme fait converger
            toute la population vers un point unique, la société se fige
            définitivement et son IDE tombe à zéro quels que soient les autres
            réglages. Le modèle ne pouvait donc représenter ni le débat fluide, ni
            l'effet du bruit thermique que la note propose précisément d'injecter.
        conformity: force d'attraction vers l'interlocuteur (règle d'alignement).
        media_force: force d'attraction vers une source d'information à portée.
        fake_news_probability: probabilité de transmission par interaction.
        radicalisation: intensité du déplacement vers le coin lors d'une
            contamination.
        fact_checkers: nombre d'agents de vérification.
        fact_checker_efficacy: probabilité qu'une vérification emporte la conviction.
        interactions_per_step: nombre de tours d'interaction par pas de temps.
        exposure_window: fenêtre d'observation de l'IDE individuel.
        critical_index: seuil de bulle gelée.
        initial_spread: amplitude de la dispersion initiale des opinions. La valeur
            par défaut décrit une société initialement modérée, cohérente avec la
            condition initiale du solveur de Fokker-Planck.
    """

    population: int = 200
    bubble_threshold: float = 0.4
    social_temperature: float = 0.02
    conformity: float = 0.02
    media_force: float = 0.01
    fake_news_probability: float = 0.01
    radicalisation: float = 0.05
    fact_checkers: int = 5
    fact_checker_efficacy: float = 0.5
    interactions_per_step: int = 2
    exposure_window: int = 20
    critical_index: float = 0.4
    initial_spread: float = 0.1

    def __post_init__(self) -> None:
        if self.population < 2:
            raise ValueError("il faut au moins deux individus")
        if self.bubble_threshold <= 0.0:
            raise ValueError("le seuil de bulle doit être strictement positif")
        if self.social_temperature < 0.0:
            raise ValueError("la température sociale ne peut pas être négative")
        if not 0.0 <= self.fake_news_probability <= 1.0:
            raise ValueError("la probabilité de contagion doit appartenir à [0, 1]")
        if self.interactions_per_step < 1:
            raise ValueError("il faut au moins un tour d'interaction par pas")
        if not 0.0 <= self.initial_spread <= 1.0:
            raise ValueError("la dispersion initiale doit appartenir à [0, 1]")


@dataclass
class SocietyModel:
    """Société d'agents évoluant sur un compas politique.

    Args:
        parameters: paramètres du modèle.
        media: paysage médiatique. Par défaut, une source par quadrant.
        seed: graine du générateur. À graine égale, deux exécutions sont identiques.

    Examples:
        >>> model = SocietyModel(SocietyParameters(population=60), seed=0)
        >>> history = model.run(steps=30)
        >>> len(history)
        30
        >>> 0.0 <= history[-1].exposure_index <= 1.0
        True
    """

    parameters: SocietyParameters = field(default_factory=SocietyParameters)
    media: tuple[MediaOutlet, ...] = field(default_factory=default_media_landscape)
    seed: int | None = None

    citizens: list[Citizen] = field(init=False, repr=False)
    fact_checkers: list[FactChecker] = field(init=False, repr=False)
    step_count: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        self._rng = np.random.default_rng(self.seed)
        spread = self.parameters.initial_spread

        self.citizens = [
            Citizen(
                identifier=index,
                opinion=self._rng.uniform(-spread, spread, size=2),
                exposure_window=self.parameters.exposure_window,
            )
            for index in range(self.parameters.population)
        ]
        self.fact_checkers = [
            FactChecker(
                opinion=self._rng.uniform(-0.8, 0.8, size=2),
                velocity=self._rng.uniform(-0.01, 0.01, size=2),
                efficacy=self.parameters.fact_checker_efficacy,
            )
            for _ in range(self.parameters.fact_checkers)
        ]

    @property
    def infected_count(self) -> int:
        """Nombre d'individus porteurs d'une fausse croyance."""
        return sum(citizen.infected for citizen in self.citizens)

    def inject_fake_news(self, count: int = 1) -> list[int]:
        """Contamine ``count`` individus tirés au hasard — le « patient zéro ».

        Returns:
            Les identifiants des individus contaminés par cette injection.
        """
        if count < 1:
            raise ValueError("il faut injecter au moins une contamination")

        chosen = self._rng.choice(len(self.citizens), size=min(count, len(self.citizens)),
                                  replace=False)
        infected = []
        for index in np.atleast_1d(chosen):
            citizen = self.citizens[int(index)]
            citizen.infect(self.parameters.radicalisation)
            infected.append(citizen.identifier)

        return infected

    def _find_interlocutor(self, citizen: Citizen, max_attempts: int = 20) -> Citizen | None:
        """Cherche un interlocuteur compatible avec la bulle de l'individu.

        Le tirage est répété faute de structure d'index spatial : au-delà de
        ``max_attempts`` échecs, on considère que l'individu n'a personne à qui
        parler ce tour-ci. C'est un comportement voulu et non un abandon technique —
        un seuil de bulle très bas doit effectivement produire de l'isolement.
        """
        for _ in range(max_attempts):
            candidate = self.citizens[int(self._rng.integers(len(self.citizens)))]
            if candidate.identifier == citizen.identifier:
                continue

            distance = float(np.linalg.norm(candidate.opinion - citizen.opinion))
            if distance <= self.parameters.bubble_threshold:
                return candidate

        return None

    def _interact(self, citizen: Citizen) -> None:
        """Une interaction sociale : conformisme, exposition, contagion éventuelle."""
        interlocutor = self._find_interlocutor(citizen)
        if interlocutor is None:
            return

        citizen.record_exposure(interlocutor.quadrant)
        citizen.move_towards(interlocutor.opinion, self.parameters.conformity)

        if (
            interlocutor.infected
            and not citizen.infected
            and self._rng.random() < self.parameters.fake_news_probability
        ):
            citizen.infect(self.parameters.radicalisation)

    def _expose_to_media(self, citizen: Citizen) -> None:
        """Applique l'influence des sources d'information à portée."""
        for outlet in self.media:
            if not outlet.influences(citizen):
                continue

            citizen.record_exposure(quadrant_label(outlet.opinion))
            citizen.move_towards(outlet.opinion, self.parameters.media_force)

    def step(self) -> SocietyMetrics:
        """Avance la société d'un pas de temps et renvoie ses observables."""
        for citizen in self.citizens:
            citizen.agitate(self._rng, self.parameters.social_temperature)

        for _ in range(self.parameters.interactions_per_step):
            for citizen in self.citizens:
                self._interact(citizen)
                self._expose_to_media(citizen)

        for checker in self.fact_checkers:
            checker.patrol(self._rng)
            for citizen in self.citizens:
                checker.attempt_cure(citizen, self._rng)

        self.step_count += 1

        return measure(
            self.citizens,
            step=self.step_count,
            critical_index=self.parameters.critical_index,
        )

    def run(
        self,
        steps: int,
        inject_at: dict[int, int] | None = None,
    ) -> list[SocietyMetrics]:
        """Simule ``steps`` pas de temps.

        Args:
            steps: nombre de pas.
            inject_at: injections de fausses informations, sous la forme
                ``{pas: nombre_de_contaminations}``. Permet de reproduire le
                scénario du mémorandum — crise médiatique, puis démenti — de
                manière scriptée et reproductible, là où le prototype d'origine
                exigeait une frappe au clavier.

        Returns:
            L'historique des observables, un élément par pas.
        """
        if steps < 1:
            raise ValueError("il faut simuler au moins un pas")

        schedule = inject_at or {}
        history = []

        for _ in range(steps):
            upcoming = self.step_count + 1
            if upcoming in schedule:
                self.inject_fake_news(schedule[upcoming])

            history.append(self.step())

        return history

    def opinion_cloud(self) -> np.ndarray:
        """Positions d'opinion de toute la population, de forme ``(N, 2)``.

        Sert au tracé du nuage de points sur le compas, dans le notebook.
        """
        return np.array([citizen.opinion for citizen in self.citizens])
