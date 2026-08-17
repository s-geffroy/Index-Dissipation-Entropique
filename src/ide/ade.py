"""ADE — Algorithme de Dissipation Entropique.

Un algorithme de recommandation classique maximise l'engagement immédiat. Sous les
équations de :mod:`ide.resonance`, cette fonction de coût est exactement celle qui
produit un amortissement négatif : elle récompense mécaniquement les contenus à
forte charge émotionnelle, donc la désinformation, et pousse le système vers la
résonance destructive.

L'ADE remplace cette fonction de coût. Le score d'un contenu :math:`c` pour un
utilisateur :math:`i` devient :

.. math:: S(i, c) = \\mathrm{Pertinence}(i, c) + \\mu \\cdot \\Delta H(i, c)

où :math:`\\Delta H(i, c) = H_{\\text{futur}}(c) - H_{\\text{actuelle}}` mesure ce
que l'affichage du contenu ferait à la diversité du fil de l'utilisateur, et
:math:`\\mu \\geq 0` est le coefficient de régulation thermodynamique — la
« viscosité » du flux.

Le terme de pertinence est conservé : un algorithme qui servirait de la diversité
sans pertinence serait abandonné par ses utilisateurs, ce qui ne dissiperait aucune
entropie. L'ADE n'est pas un filtre de censure, c'est un rééquilibrage.

.. note::
    Le fil de travail d'origine écrivait d'abord :math:`S = \\mathrm{Pertinence}
    - \\mu \\Delta H`, puis se corrigeait quelques lignes plus loin en
    :math:`+\\mu \\Delta H`. Le signe **positif** est le bon : avec
    :math:`\\Delta H > 0` pour un contenu qui diversifie le fil, seul un
    coefficient positif le fait remonter au classement. La forme négative
    récompenserait au contraire l'enfermement.

**Recuit.** :math:`\\mu` n'est pas constant. Tant que le fil de l'utilisateur reste
diversifié, l'algorithme n'a pas à intervenir et :math:`\\mu` demeure à sa valeur
de repos. Dès que l'IDE passe sous le seuil critique — signal d'une bulle qui se
referme — :math:`\\mu` monte et l'algorithme entre en « mode recuit » : il
sur-classe délibérément les contenus divergents le temps de réchauffer le fil.
C'est la transposition du recuit simulé de la métallurgie, décrite dans la note :
un pic de température ponctuel pour casser un état figé, suivi d'un
refroidissement.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ide.entropy import entropic_dissipation_index

__all__ = [
    "Candidate",
    "EntropicScorer",
    "ScoredCandidate",
    "annealing_coefficient",
    "entropic_score",
]


def entropic_score(relevance: float, delta_entropy: float, mu: float) -> float:
    """Score de recommandation :math:`S = \\mathrm{Pertinence} + \\mu \\cdot \\Delta H`.

    Args:
        relevance: score de pertinence classique, dans :math:`[0, 1]` par convention.
        delta_entropy: variation d'IDE qu'entraînerait l'affichage du contenu.
            Positive pour un contenu qui diversifie, négative pour un contenu qui
            renforce la bulle.
        mu: coefficient de régulation, positif ou nul.

    Returns:
        Le score de classement.

    Raises:
        ValueError: si ``mu`` est négatif — un coefficient négatif inverserait la
            politique de l'algorithme et récompenserait l'enfermement.

    Examples:
        >>> entropic_score(relevance=0.5, delta_entropy=0.2, mu=2.0)
        0.9
    """
    if mu < 0.0:
        raise ValueError(
            "le coefficient de régulation μ doit être positif ou nul : "
            "une valeur négative récompenserait la fermeture du fil"
        )

    return float(relevance + mu * delta_entropy)


def annealing_coefficient(
    current_index: float,
    critical_index: float = 0.4,
    resting_mu: float = 0.5,
    annealing_mu: float = 4.0,
) -> float:
    """Coefficient de régulation :math:`\\mu` en fonction de l'état du fil.

    La montée est **progressive** plutôt qu'en tout ou rien : un seuil dur ferait
    osciller l'algorithme entre deux régimes de part et d'autre de la valeur
    critique, chaque intervention rétablissant l'index juste assez pour désactiver
    l'intervention suivante. L'interpolation linéaire entre le seuil et zéro évite
    ce battement.

    Args:
        current_index: IDE mesuré du fil, dans :math:`[0, 1]`.
        critical_index: seuil :math:`H_{\\text{critique}}` en dessous duquel la
            bulle est réputée en train de geler.
        resting_mu: valeur de repos, appliquée quand le fil est sain.
        annealing_mu: valeur maximale, atteinte quand l'index tombe à zéro.

    Returns:
        Le coefficient à appliquer.

    Examples:
        Fil sain : régime de repos.

        >>> annealing_coefficient(0.8)
        0.5

        Bulle totalement gelée : recuit à pleine puissance.

        >>> annealing_coefficient(0.0)
        4.0
    """
    if not 0.0 <= current_index <= 1.0:
        raise ValueError("l'IDE doit appartenir à [0, 1]")
    if not 0.0 < critical_index <= 1.0:
        raise ValueError("le seuil critique doit appartenir à (0, 1]")
    if resting_mu < 0.0 or annealing_mu < resting_mu:
        raise ValueError("il faut 0 ≤ resting_mu ≤ annealing_mu")

    if current_index >= critical_index:
        return float(resting_mu)

    severity = (critical_index - current_index) / critical_index

    return float(resting_mu + severity * (annealing_mu - resting_mu))


@dataclass(frozen=True)
class Candidate:
    """Contenu candidat à l'affichage.

    Args:
        identifier: identifiant du contenu.
        viewpoint: étiquette de point de vue, l'unité dont l'IDE mesure la
            diversité. Deux contenus de même étiquette sont interchangeables du
            point de vue entropique.
        relevance: score de pertinence produit par le moteur classique.
    """

    identifier: str
    viewpoint: str
    relevance: float


@dataclass(frozen=True)
class ScoredCandidate:
    """Contenu candidat, une fois évalué par l'ADE.

    Attributes:
        candidate: le contenu évalué.
        delta_entropy: variation d'IDE qu'entraînerait son affichage.
        mu: coefficient de régulation appliqué.
        score: score final de classement.
    """

    candidate: Candidate
    delta_entropy: float
    mu: float
    score: float

    @property
    def identifier(self) -> str:
        """Identifiant du contenu évalué."""
        return self.candidate.identifier

    @property
    def viewpoint(self) -> str:
        """Point de vue du contenu évalué."""
        return self.candidate.viewpoint


@dataclass
class EntropicScorer:
    """Classement de contenus par l'Algorithme de Dissipation Entropique.

    Args:
        catalogue_size: nombre :math:`k` de points de vue que la plateforme est en
            mesure de servir. Sert de dénominateur à l'IDE ; sans référence fixe,
            une bulle fermée obtiendrait un index flatteur (voir
            :func:`ide.entropy.entropic_dissipation_index`).
        critical_index: seuil de déclenchement du recuit.
        resting_mu: coefficient de repos.
        annealing_mu: coefficient maximal en mode recuit.

    Examples:
        Un utilisateur enfermé dans une bulle, et deux contenus candidats : l'un
        prolonge la bulle avec une pertinence élevée, l'autre la rompt.

        >>> scorer = EntropicScorer(catalogue_size=4)
        >>> feed = ["complot"] * 10
        >>> candidates = [
        ...     Candidate("a", "complot", relevance=0.90),
        ...     Candidate("b", "factuel", relevance=0.55),
        ... ]
        >>> ranked = scorer.rank(feed, candidates)
        >>> ranked[0].identifier  # le contenu divergent remonte
        'b'

        Avec un coefficient nul, l'ADE se réduit exactement au tri par pertinence :

        >>> neutral = EntropicScorer(catalogue_size=4, resting_mu=0.0, annealing_mu=0.0)
        >>> neutral.rank(feed, candidates)[0].identifier
        'a'
    """

    catalogue_size: int
    critical_index: float = 0.4
    resting_mu: float = 0.5
    annealing_mu: float = 4.0

    def __post_init__(self) -> None:
        if self.catalogue_size < 2:
            raise ValueError("un catalogue doit offrir au moins deux points de vue")
        # Valide les bornes de μ dès la construction, sans attendre un appel.
        annealing_coefficient(0.5, self.critical_index, self.resting_mu, self.annealing_mu)

    def current_index(self, feed: Sequence[str]) -> float:
        """IDE du fil actuel de l'utilisateur."""
        return entropic_dissipation_index(feed, catalogue_size=self.catalogue_size)

    def delta_entropy(self, feed: Sequence[str], viewpoint: str) -> float:
        """Variation d'IDE qu'entraînerait l'ajout d'un contenu au fil.

        Positive si le contenu diversifie l'exposition, négative s'il renforce la
        modalité déjà dominante.
        """
        before = self.current_index(feed)
        after = entropic_dissipation_index(
            [*feed, viewpoint], catalogue_size=self.catalogue_size
        )

        return after - before

    def mu(self, feed: Sequence[str]) -> float:
        """Coefficient de régulation applicable à l'état courant du fil."""
        return annealing_coefficient(
            self.current_index(feed),
            critical_index=self.critical_index,
            resting_mu=self.resting_mu,
            annealing_mu=self.annealing_mu,
        )

    def rank(
        self, feed: Sequence[str], candidates: Sequence[Candidate]
    ) -> list[ScoredCandidate]:
        """Classe les contenus candidats par score décroissant.

        Args:
            feed: points de vue déjà servis à l'utilisateur sur la fenêtre
                d'observation.
            candidates: contenus disponibles.

        Returns:
            Les candidats évalués, du meilleur score au moins bon. À score égal,
            l'ordre d'entrée est préservé — le tri est stable, ce qui rend le
            classement reproductible.
        """
        if len(candidates) == 0:
            return []

        coefficient = self.mu(feed)

        # L'impact entropique est mis en cache par point de vue : deux contenus
        # portant la même étiquette ont, par construction de l'IDE, le même ΔH.
        impact_by_viewpoint: dict[str, float] = {}
        scored = []
        for candidate in candidates:
            if candidate.viewpoint not in impact_by_viewpoint:
                impact_by_viewpoint[candidate.viewpoint] = self.delta_entropy(
                    feed, candidate.viewpoint
                )
            impact = impact_by_viewpoint[candidate.viewpoint]

            scored.append(
                ScoredCandidate(
                    candidate=candidate,
                    delta_entropy=impact,
                    mu=coefficient,
                    score=entropic_score(candidate.relevance, impact, coefficient),
                )
            )

        return sorted(scored, key=lambda item: item.score, reverse=True)

    def serve(self, feed: Sequence[str], candidates: Sequence[Candidate]) -> list[str]:
        """Simule un cycle complet : classe, sert le meilleur contenu, met à jour le fil.

        Returns:
            Le nouveau fil, contenu servi inclus. Un fil vide de candidats est
            renvoyé inchangé.
        """
        ranked = self.rank(feed, candidates)
        if not ranked:
            return list(feed)

        return [*feed, ranked[0].viewpoint]
