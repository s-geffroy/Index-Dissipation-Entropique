"""Le test adverse repris sur des fils **ordonnés**, et non sur des compositions.

Ce que le test adverse n'avait pas éprouvé
------------------------------------------

Le [test adverse](gaming.py) a comparé quatre mesures de diversité sous contrainte. Toutes
portaient sur la **composition** du fil — quelle part de l'attention va à quel point de vue —
et aucune ne regardait l'**ordre**.

Or [le rang compte](radio.py) : un lecteur consulte le premier élément bien plus souvent que le
dernier. Une plateforme tenue à un plancher portant sur la seule composition peut donc s'y
conformer en plaçant les contenus divergents **en bas**, où ils ne coûtent presque rien. C'est
un quatrième adversaire, et les quatre mesures ont été jugées sans lui.

Ce module reprend la comparaison sur des fils ordonnés.

L'optimisation est exhaustive, à dessein
-----------------------------------------

Le fil compte :math:`n` positions à remplir depuis un catalogue de :math:`k` points de vue, ce
qui fait :math:`k^n` fils possibles. Pour les tailles employées ici, ils sont **tous
énumérés** : l'optimum retenu est exact, non le résultat d'une heuristique.

Ce n'est pas un luxe. Le [test adverse](gaming.py) portait déjà sur des résultats négatifs —
des normes qui échouent — et un optimum manqué par un solveur y aurait produit exactement la
même apparence qu'une norme qui tient. L'énumération retire cette ambiguïté.

Les deux façons de mesurer le même fil
--------------------------------------

* **à l'aveugle du rang** : la distribution mesurée est la composition du fil, chaque position
  comptant pour une. C'est ce que faisaient les quatre mesures du test adverse ;
* **consciente du rang** : la distribution est pondérée par l'attention qu'appelle chaque
  position, selon la remise de :func:`ide.radio.rank_weights`.

La même mesure, appliquée aux deux distributions, donne deux normes différentes. C'est
l'écart entre les deux que ce module met à l'épreuve.
"""

from __future__ import annotations

import itertools
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from ide.radio import rank_aware_distribution, rank_weights

__all__ = [
    "Ranking",
    "all_rankings",
    "aware_weights",
    "blind_weights",
    "burial_signature",
    "optimal_ranking_under",
    "ranking_engagement",
]

#: Au-delà de ce nombre de fils possibles, l'énumération exhaustive cesse d'être raisonnable
#: et le module refuse plutôt que de basculer silencieusement sur une heuristique.
MAX_ENUMERATION = 2_000_000


@dataclass(frozen=True)
class Ranking:
    """Un fil ordonné et ce qu'il vaut.

    Attributes:
        assignment: point de vue servi à chaque position, dans l'ordre du fil.
        engagement: engagement produit, pondéré par l'attention de chaque rang.
        blind: valeur de la mesure appliquée à la composition.
        aware: valeur de la même mesure appliquée à la distribution escomptée.
    """

    assignment: np.ndarray
    engagement: float
    blind: float
    aware: float

    @property
    def burial(self) -> float:
        """Écart entre diversité affichée et diversité effectivement exposée.

        Positif quand le fil paraît plus divers qu'il n'est vu, c'est-à-dire quand les
        contenus divergents ont été relégués. C'est la signature de l'enterrement, et son
        analogue exact pour l'étiquetage était l'excès de signature du test adverse.
        """
        return self.blind - self.aware


def all_rankings(slots: int, viewpoint_count: int) -> np.ndarray:
    """Tous les fils possibles de ``slots`` positions sur ``viewpoint_count`` points de vue.

    Raises:
        ValueError: si l'énumération dépasse :data:`MAX_ENUMERATION`. Le refus est délibéré :
            retomber en silence sur une heuristique retirerait au résultat sa seule garantie.
    """
    if slots < 1 or viewpoint_count < 2:
        raise ValueError("il faut au moins une position et deux points de vue")

    total = viewpoint_count**slots
    if total > MAX_ENUMERATION:
        raise ValueError(
            f"{total} fils à énumérer, au-delà de la limite de {MAX_ENUMERATION} : "
            "réduire le nombre de positions ou de points de vue"
        )

    return np.array(list(itertools.product(range(viewpoint_count), repeat=slots)), dtype=int)


def blind_weights(assignment: np.ndarray, viewpoint_count: int) -> np.ndarray:
    """Composition du fil : chaque position compte pour une, quel que soit son rang."""
    return np.bincount(np.asarray(assignment, dtype=int), minlength=viewpoint_count) / len(
        assignment
    )


def aware_weights(
    assignment: np.ndarray, viewpoint_count: int, discount: str = "mrr"
) -> np.ndarray:
    """Distribution du fil pondérée par l'attention accordée à chaque rang."""
    return rank_aware_distribution(assignment, viewpoint_count, discount=discount)


def ranking_engagement(
    assignment: np.ndarray, relevance: np.ndarray, discount: str = "mrr"
) -> float:
    """Engagement produit par un fil ordonné.

    Chaque position rapporte la pertinence du point de vue qu'elle sert, pondérée par
    l'attention que son rang reçoit. C'est la même remise que celle de la mesure : ce qui rend
    l'enterrement rentable est exactement ce qui le rend invisible à une mesure aveugle.
    """
    assignment = np.asarray(assignment, dtype=int)
    attention = rank_weights(assignment.size, discount=discount)

    return float(np.sum(attention * np.asarray(relevance, dtype=float)[assignment]))


def optimal_ranking_under(
    measure: Callable[[np.ndarray], float],
    relevance: np.ndarray,
    slots: int,
    floor: float,
    rank_aware: bool,
    discount: str = "mrr",
    catalogue_size: int | None = None,
) -> Ranking | None:
    """Fil ordonné maximisant l'engagement sous un plancher, par énumération exhaustive.

    Args:
        measure: fonction d'une distribution sur les points de vue vers :math:`[0, 1]`.
        relevance: pertinence de chaque point de vue pour le lecteur.
        slots: nombre de positions du fil.
        floor: plancher imposé.
        rank_aware: si vrai, le plancher porte sur la distribution escomptée ; sinon sur la
            composition. C'est la seule différence entre les deux normes comparées.
        discount: remise de rang employée par la mesure **et** par l'engagement.
        catalogue_size: nombre de points de vue. À défaut, la taille de ``relevance``.

    Returns:
        Le meilleur fil satisfaisant le plancher, ou ``None`` si aucun ne le satisfait —
        auquel cas le plancher est inatteignable, ce qui est une information et non un échec.
    """
    relevance = np.asarray(relevance, dtype=float)
    viewpoints = relevance.size if catalogue_size is None else catalogue_size

    best: Ranking | None = None
    for assignment in all_rankings(slots, viewpoints):
        constrained = (
            measure(aware_weights(assignment, viewpoints, discount))
            if rank_aware
            else measure(blind_weights(assignment, viewpoints))
        )
        if constrained < floor - 1e-9:
            continue

        value = ranking_engagement(assignment, relevance, discount)
        if best is not None and value <= best.engagement:
            continue

        best = Ranking(
            assignment=assignment,
            engagement=value,
            blind=measure(blind_weights(assignment, viewpoints)),
            aware=measure(aware_weights(assignment, viewpoints, discount)),
        )

    return best


def burial_signature(
    measure: Callable[[np.ndarray], float],
    assignment: np.ndarray,
    viewpoint_count: int,
    discount: str = "mrr",
) -> float:
    """Écart entre la mesure aveugle et la mesure consciente du rang, sur un même fil.

    Nul pour un fil dont l'ordre ne concentre pas l'attention sur un point de vue ; il croît
    à mesure que la diversité est reléguée. Contrairement à l'écart brut entre deux indices
    différents — que le test adverse a dû renoncer à seuiller — celui-ci compare **la même
    mesure à elle-même**, ce qui le rend directement interprétable.
    """
    assignment = np.asarray(assignment, dtype=int)

    return measure(blind_weights(assignment, viewpoint_count)) - measure(
        aware_weights(assignment, viewpoint_count, discount)
    )
