"""Agents du modèle « compas politique ».

Chaque individu occupe une position dans un espace d'opinion continu à deux
dimensions — l'axe économique (gauche/droite) et l'axe sociétal
(autoritaire/libertaire) — plutôt que le spin binaire :math:`\\pm 1` des modèles
d'Ising. C'est l'une des limites que le fil de travail identifiait lui-même : la
pensée humaine est multidimensionnelle, et un modèle qui la réduit à deux valeurs
ne peut pas représenter la modération.

Trois espèces d'agents peuplent le modèle, transposant les trois règles du modèle
des *Boids* de Reynolds en forces sociales :

* :class:`Citizen` — l'individu, soumis au conformisme (alignement) et au besoin
  d'appartenance (cohésion) ;
* :class:`MediaOutlet` — une source d'information immobile, qui exerce une
  attraction sur les individus passant à sa portée ;
* :class:`FactChecker` — un agent de vérification qui patrouille l'espace
  d'opinion et tente de dissiper les croyances fausses qu'il rencontre.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

import numpy as np

__all__ = [
    "Citizen",
    "FactChecker",
    "MediaOutlet",
    "quadrant_label",
]

# Les quatre quadrants du compas, dans l'ordre (économique, sociétal).
_ECONOMIC_LABELS = ("gauche", "droite")
_SOCIETAL_LABELS = ("libertaire", "autoritaire")


def _reflect(position: np.ndarray) -> np.ndarray:
    """Replie une position sortie du compas par réflexion sur ses bords.

    Les bords du compas ne sont pas absorbants : un individu poussé au-delà de
    l'extrême revient vers l'intérieur, comme une bille rebondissant sur une paroi.
    Le repliement est appliqué en boucle pour couvrir le cas — rare mais possible
    à haute température — d'un déplacement supérieur à la largeur du domaine.
    """
    folded = np.asarray(position, dtype=float)

    while np.any(np.abs(folded) > 1.0):
        folded = np.where(folded > 1.0, 2.0 - folded, folded)
        folded = np.where(folded < -1.0, -2.0 - folded, folded)

    return folded


def quadrant_label(opinion: np.ndarray) -> str:
    """Étiquette de quadrant d'une position d'opinion.

    C'est la discrétisation qui permet de calculer un IDE : l'index mesure la
    diversité d'une distribution de **modalités**, il faut donc convertir une
    position continue en point de vue nommé. Quatre quadrants forment le catalogue
    de référence du modèle.

    Args:
        opinion: vecteur ``[économique, sociétal]``, chaque composante dans
            :math:`[-1, 1]`.

    Returns:
        Une étiquette de la forme ``"droite-autoritaire"``.

    Examples:
        >>> import numpy as np
        >>> quadrant_label(np.array([0.4, -0.2]))
        'droite-libertaire'
    """
    economic = _ECONOMIC_LABELS[int(opinion[0] > 0.0)]
    societal = _SOCIETAL_LABELS[int(opinion[1] > 0.0)]

    return f"{economic}-{societal}"


@dataclass
class Citizen:
    """Un individu positionné dans l'espace d'opinion.

    Args:
        identifier: identifiant unique dans la population.
        opinion: position initiale ``[économique, sociétal]``.
        exposure_window: nombre d'interactions récentes retenues pour calculer
            l'IDE individuel. C'est la fenêtre d'observation du mémorandum,
            transposée à l'échelle de l'agent.
    """

    identifier: int
    opinion: np.ndarray
    exposure_window: int = 20

    infected: bool = False
    exposure: deque[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.exposure_window < 1:
            raise ValueError("la fenêtre d'exposition doit compter au moins une interaction")

        self.opinion = np.clip(np.asarray(self.opinion, dtype=float), -1.0, 1.0)
        self.exposure = deque(maxlen=self.exposure_window)

    @property
    def quadrant(self) -> str:
        """Quadrant du compas occupé par l'individu."""
        return quadrant_label(self.opinion)

    @property
    def radicalism(self) -> float:
        """Distance à la modération, dans :math:`[0, \\sqrt{2}]`.

        Zéro décrit un individu parfaitement centriste ; la valeur maximale, un
        individu réfugié dans un coin du compas.
        """
        return float(np.linalg.norm(self.opinion))

    def record_exposure(self, viewpoint: str) -> None:
        """Mémorise un point de vue rencontré, pour le calcul de l'IDE individuel."""
        self.exposure.append(viewpoint)

    def move_towards(self, target: np.ndarray, strength: float) -> None:
        """Déplace l'opinion vers une cible, d'une fraction ``strength`` de l'écart.

        C'est la règle d'alignement des *Boids*, devenue conformisme : l'individu
        ajuste sa position idéologique pour réduire l'écart avec ce qu'il perçoit,
        sans jamais l'atteindre d'un coup.
        """
        if strength < 0.0:
            raise ValueError("une force d'influence ne peut pas être négative")

        self.opinion = np.clip(
            self.opinion + strength * (np.asarray(target, dtype=float) - self.opinion),
            -1.0,
            1.0,
        )

    def agitate(self, rng: np.random.Generator, temperature: float) -> None:
        """Applique l'agitation thermique individuelle : doute, humeur, hasard.

        C'est le pendant microscopique de la température sociale :math:`T` des
        modèles d'Ising et de Fokker-Planck. Sans elle, le conformisme est une
        force purement contractante et la population s'effondre irréversiblement
        sur un point unique.
        """
        if temperature < 0.0:
            raise ValueError("la température sociale ne peut pas être négative")
        if temperature == 0.0:
            return

        # Réflexion, et non troncature, sur les bords du compas. Rabattre par
        # ``clip`` reviendrait à rendre les bords absorbants : les individus
        # agités s'y accumuleraient et finiraient piégés dans les coins, ce qui
        # ferait chuter l'IDE mesuré à haute température — l'inverse du
        # comportement attendu, pour une raison purement numérique.
        self.opinion = _reflect(self.opinion + rng.normal(0.0, temperature, size=2))

    def infect(self, radicalisation: float) -> None:
        """Contamine l'individu par une fausse information.

        La croyance fausse ne remplace pas l'opinion : elle la **radicalise** en
        poussant l'individu vers le coin du compas qu'il occupe déjà.

        .. note::
            Le code d'origine (``legacy/simulation_thread_2026-08.py``) écrivait
            ``self.opinion.x = 1.0 if self.opinion.x > 0 else -1.0`` : l'individu
            était instantanément téléporté dans un coin. Cela supprimait toute
            dynamique fine — un individu contaminé n'avait plus d'histoire, et la
            mesure de polarisation devenait un simple décompte de contaminations.
            La radicalisation progressive retenue ici conserve la dynamique tout en
            produisant le même effet asymptotique.
        """
        self.infected = True

        # Direction du coin le plus proche, en évitant de figer un individu
        # exactement centré (signe nul) dans une position neutre.
        corner = np.where(self.opinion >= 0.0, 1.0, -1.0)
        self.move_towards(corner, radicalisation)

    def cure(self) -> None:
        """Dissipe la croyance fausse, sans modifier la position d'opinion.

        Le fait-checking corrige une information, il ne convertit pas quelqu'un à
        une autre idéologie : la position reste où elle est, seule l'étiquette de
        contamination tombe.
        """
        self.infected = False


@dataclass(frozen=True)
class MediaOutlet:
    """Source d'information fixe dans l'espace d'opinion.

    Args:
        name: nom de la source.
        opinion: position éditoriale ``[économique, sociétal]``.
        reach: portée :math:`d` au-delà de laquelle la source n'influence plus
            personne. C'est le champ :math:`H` du modèle d'Ising, rendu local.
    """

    name: str
    opinion: np.ndarray
    reach: float = 0.5

    def influences(self, citizen: Citizen) -> bool:
        """Vrai si l'individu se trouve dans la portée de la source."""
        return bool(np.linalg.norm(self.opinion - citizen.opinion) < self.reach)


@dataclass
class FactChecker:
    """Agent de vérification patrouillant l'espace d'opinion.

    Args:
        opinion: position initiale.
        velocity: vitesse de patrouille initiale.
        radius: rayon d'action.
        efficacy: probabilité de dissiper une croyance fausse rencontrée dans le
            rayon d'action.

    .. note::
        Le modèle d'origine soignait **systématiquement** tout individu contaminé
        passant à portée. C'est une hypothèse très forte : elle suppose qu'un
        démenti factuel emporte toujours la conviction, ce que la littérature sur
        l'hystérésis des croyances contredit précisément. L'efficacité est donc
        rendue probabiliste et paramétrable, et sa valeur par défaut inférieure à 1.
    """

    opinion: np.ndarray
    velocity: np.ndarray
    radius: float = 0.15
    efficacy: float = 0.5

    def __post_init__(self) -> None:
        if not 0.0 <= self.efficacy <= 1.0:
            raise ValueError("l'efficacité doit appartenir à [0, 1]")
        if self.radius <= 0.0:
            raise ValueError("le rayon d'action doit être strictement positif")

        self.opinion = np.clip(np.asarray(self.opinion, dtype=float), -1.0, 1.0)
        self.velocity = np.asarray(self.velocity, dtype=float)

    def patrol(self, rng: np.random.Generator, max_speed: float = 0.015) -> None:
        """Avance d'un pas, avec rebond sur les bords du compas."""
        self.velocity = self.velocity + rng.uniform(-0.002, 0.002, size=2)

        speed = float(np.linalg.norm(self.velocity))
        if speed > max_speed:
            self.velocity *= max_speed / speed

        self.opinion = self.opinion + self.velocity
        # Rebond : l'agent reste dans le compas au lieu d'en sortir silencieusement.
        outside = np.abs(self.opinion) > 1.0
        self.velocity = np.where(outside, -self.velocity, self.velocity)
        self.opinion = np.clip(self.opinion, -1.0, 1.0)

    def attempt_cure(self, citizen: Citizen, rng: np.random.Generator) -> bool:
        """Tente de dissiper une croyance fausse. Renvoie vrai en cas de succès."""
        if not citizen.infected:
            return False
        if float(np.linalg.norm(self.opinion - citizen.opinion)) >= self.radius:
            return False
        if rng.random() >= self.efficacy:
            return False

        citizen.cure()

        return True
