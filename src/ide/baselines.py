"""Ce que vaut le filtre proposé, comparé à des heuristiques triviales.

La question jamais posée
-----------------------

Le [filtre entropique](ade.py) a toujours été comparé à un seul adversaire : le classement par
pertinence pure, dont il se distingue par construction. Personne ne lui a demandé s'il faisait
mieux qu'une **heuristique triviale** — servir les points de vue à tour de rôle, tirer au sort,
ou appliquer la diversification standard de la recherche d'information.

C'est la dette la plus ancienne du programme d'évaluation, et elle ne demande aucune donnée :
elle se règle par énumération.

Ce que ce module mesure
-----------------------

Un fil se juge sur deux grandeurs en tension : l'**engagement** qu'il produit et la
**diversité qu'il expose**, toutes deux pondérées par l'attention de chaque rang. Un
réordonnanceur n'est donc pas « bon » ou « mauvais » : il occupe un point du plan
(diversité, engagement), et la seule question qui vaille est **de combien il rate la
frontière atteignable**.

Cette frontière n'est pas estimée ici, elle est **calculée exactement** : toutes les manières
ordonnées de tirer :math:`n` contenus d'un vivier de :math:`m` sont énumérées, et l'on retient
pour chaque niveau de diversité l'engagement maximal. Le résultat est une borne supérieure, pas
un concurrent de plus.

Les concurrents
---------------

* :func:`engagement_ranking` — pertinence décroissante, le classement de référence ;
* :func:`random_ranking` — tirage sans remise, la ligne de base qu'on oublie de tracer ;
* :func:`round_robin_ranking` — les points de vue à tour de rôle, le meilleur contenu de chacun.
  Aucune sophistication, et un plancher de composition garanti ;
* :func:`mmr_ranking` — *maximal marginal relevance* (Carbonell & Goldstein, 1998), la
  diversification standard de la recherche d'information ;
* :func:`boltzmann_ranking` — tirage proportionnel à :math:`e^{r/T}`, la relaxation qu'un
  physicien écrirait d'abord ;
* :func:`entropic_ranking` — le filtre du dépôt, gourmand sur
  :math:`\\text{pertinence} + \\mu\\,\\Delta H`, ici sous la mesure **retenue** : entropie des
  contenus servis, pondérée par le rang.

Chacun a un paramètre à balayer, et c'est ce balayage qui produit une courbe comparable à la
frontière plutôt qu'un point isolé.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np

from ide.gaming import canonical_positions, position_entropy
from ide.radio import rank_weights

__all__ = [
    "MAX_ARRANGEMENTS",
    "Feed",
    "Pool",
    "best_under_floor",
    "boltzmann_ranking",
    "engagement_ranking",
    "evaluate",
    "evaluate_many",
    "entropic_ranking",
    "exact_frontier",
    "frontier",
    "mmr_ranking",
    "random_ranking",
    "reachable_engagement",
    "round_robin_ranking",
    "shortfall",
]

#: Au-delà de ce nombre d'arrangements, l'énumération exacte cesse d'être raisonnable et le
#: module refuse — plutôt que de basculer en silence sur une frontière approchée, qui ôterait
#: au résultat sa seule garantie.
MAX_ARRANGEMENTS = 3_000_000


@dataclass(frozen=True)
class Pool:
    """Le vivier de contenus dans lequel un réordonnanceur puise.

    Attributes:
        viewpoints: point de vue de chaque contenu, indice dans le catalogue.
        relevance: pertinence de chaque contenu pour le lecteur.
        catalogue_size: nombre de points de vue que la plateforme pourrait servir.
    """

    viewpoints: np.ndarray
    relevance: np.ndarray
    catalogue_size: int

    def __post_init__(self) -> None:
        if self.viewpoints.shape != self.relevance.shape:
            raise ValueError("chaque contenu doit avoir un point de vue et une pertinence")
        if self.catalogue_size < 2:
            raise ValueError("un catalogue doit offrir au moins deux points de vue")
        if self.viewpoints.size and int(self.viewpoints.max()) >= self.catalogue_size:
            raise ValueError("un contenu porte un point de vue hors catalogue")

    @property
    def size(self) -> int:
        """Nombre de contenus disponibles."""
        return int(self.relevance.size)

    @property
    def catalogue(self) -> np.ndarray:
        """Positions canoniques des points de vue du catalogue."""
        return canonical_positions(self.catalogue_size)


@dataclass(frozen=True)
class Feed:
    """Un fil servi, et les deux grandeurs sur lesquelles il se juge.

    Attributes:
        selection: indices des contenus retenus, dans l'ordre où ils sont servis.
        exposure: diversité **exposée** — l'indice retenu, pondéré par l'attention du rang.
        engagement: engagement produit, pondéré par la même attention.
    """

    selection: np.ndarray
    exposure: float
    engagement: float


def _attention(slots: int, discount: str = "mrr") -> np.ndarray:
    return rank_weights(slots, discount=discount)


def evaluate(pool: Pool, selection: Sequence[int], discount: str = "mrr") -> Feed:
    """Mesure un fil : sa diversité exposée et son engagement.

    Les deux grandeurs emploient la **même** remise de rang. C'est ce qui rend la comparaison
    honnête : ce qui rend l'enterrement rentable est exactement ce qui le rend invisible à une
    mesure aveugle, et les deux courbes doivent donc partager leur pondération.
    """
    chosen = np.asarray(selection, dtype=int)
    attention = _attention(chosen.size, discount)
    served = pool.catalogue[pool.viewpoints[chosen]]

    return Feed(
        selection=chosen,
        exposure=position_entropy(attention / attention.sum(), served, pool.catalogue),
        engagement=float(np.sum(attention * pool.relevance[chosen])),
    )


# --------------------------------------------------------------------------------------
# Les réordonnanceurs. Signature commune : (pool, slots, paramètre) -> indices ordonnés.
# --------------------------------------------------------------------------------------


def engagement_ranking(pool: Pool, slots: int) -> np.ndarray:
    """Pertinence décroissante — le classement dont tous les autres s'écartent."""
    return np.argsort(-pool.relevance, kind="stable")[:slots]


def random_ranking(pool: Pool, slots: int, rng: np.random.Generator) -> np.ndarray:
    """Tirage sans remise, ordre aléatoire.

    C'est la ligne de base qu'on oublie de tracer, et elle n'est pas triviale : sur un vivier
    riche en points de vue, le hasard produit une diversité élevée. Ce qu'il coûte en
    engagement est précisément ce qu'une méthode doit économiser pour valoir mieux que lui.
    """
    return rng.choice(pool.size, size=slots, replace=False)


def round_robin_ranking(pool: Pool, slots: int, cycles: int | None = None) -> np.ndarray:
    """Les points de vue à tour de rôle, le meilleur contenu disponible de chacun.

    Args:
        cycles: nombre de positions de tête réparties à tour de rôle. Au-delà, le fil est
            complété par pertinence décroissante. C'est le paramètre qui fait de cette
            heuristique une courbe et non un point : à ``0`` elle est le classement par
            pertinence, à ``slots`` elle impose l'alternance sur tout le fil.
    """
    limit = slots if cycles is None else max(0, min(cycles, slots))
    order = np.argsort(-pool.relevance, kind="stable")
    remaining = list(order)
    selection: list[int] = []

    turn = 0
    while len(selection) < limit and remaining:
        viewpoint = turn % pool.catalogue_size
        candidate = next((item for item in remaining if pool.viewpoints[item] == viewpoint), None)
        if candidate is not None:
            selection.append(candidate)
            remaining.remove(candidate)
        turn += 1
        if turn > pool.catalogue_size * (slots + 1):  # plus aucun point de vue à servir
            break

    for item in remaining:
        if len(selection) >= slots:
            break
        selection.append(item)

    return np.asarray(selection[:slots], dtype=int)


def mmr_ranking(pool: Pool, slots: int, trade_off: float) -> np.ndarray:
    """*Maximal marginal relevance* : la diversification standard de 1998.

    À chaque position, le contenu retenu maximise
    :math:`\\lambda\\, r_i - (1-\\lambda) \\max_{j \\in \\text{déjà servi}} \\mathrm{sim}(i, j)`,
    la similarité étant ici la proximité des points de vue sur le catalogue de référence.

    Args:
        trade_off: :math:`\\lambda`. À ``1`` la méthode est le classement par pertinence ; à
            ``0`` elle ne regarde plus que l'écartement.
    """
    if not 0.0 <= trade_off <= 1.0:
        raise ValueError("le compromis de MMR vit dans [0, 1]")

    positions = pool.catalogue[pool.viewpoints]
    span = float(np.ptp(pool.catalogue)) or 1.0
    selection: list[int] = []

    for _ in range(min(slots, pool.size)):
        best, best_score = None, -np.inf
        for item in range(pool.size):
            if item in selection:
                continue
            if selection:
                distance = np.abs(positions[item] - positions[selection]).min() / span
                similarity = 1.0 - float(distance)
            else:
                similarity = 0.0
            score = trade_off * pool.relevance[item] - (1.0 - trade_off) * similarity
            if score > best_score:
                best, best_score = item, score
        selection.append(int(best))

    return np.asarray(selection, dtype=int)


def boltzmann_ranking(
    pool: Pool, slots: int, temperature: float, rng: np.random.Generator
) -> np.ndarray:
    """Tirage sans remise proportionnel à :math:`e^{r/T}`.

    C'est la relaxation qu'un physicien écrirait d'abord, et elle a le mérite d'être la seule
    dont l'optimalité soit connue : à entropie fixée, la distribution de Boltzmann maximise la
    forme linéaire. Ce module la met en concurrence avec les autres pour voir si cet argument
    survit au passage aux fils ordonnés.

    Args:
        temperature: à :math:`T \\to 0` le tirage est déterministe et rend le classement par
            pertinence ; à :math:`T \\to \\infty` il devient uniforme.
    """
    if temperature <= 0.0:
        return engagement_ranking(pool, slots)

    scores = pool.relevance / temperature
    weights = np.exp(scores - scores.max())
    selection: list[int] = []
    available = weights.copy()

    for _ in range(min(slots, pool.size)):
        total = available.sum()
        if total <= 0.0:
            break
        drawn = int(rng.choice(pool.size, p=available / total))
        selection.append(drawn)
        available[drawn] = 0.0

    return np.asarray(selection, dtype=int)


def entropic_ranking(pool: Pool, slots: int, mu: float, discount: str = "mrr") -> np.ndarray:
    """Le filtre du dépôt : gourmand sur pertinence :math:`+\\ \\mu\\,\\Delta H`.

    À chaque position, le contenu retenu maximise sa pertinence augmentée du gain de diversité
    exposée qu'il apporte au fil partiel, pondéré par :math:`\\mu`. C'est la règle de
    :mod:`ide.ade`, transposée à la mesure retenue --- entropie des contenus servis, pondérée
    par l'attention de chaque rang --- au lieu de l'entropie des étiquettes.

    Args:
        mu: coefficient de régulation. À ``0``, le classement est **exactement** celui de la
            pertinence : la transformation est un ajout paramétré, pas une refonte.
    """
    if mu < 0.0:
        raise ValueError("le coefficient de régulation ne peut être négatif")

    attention = _attention(slots, discount)
    selection: list[int] = []

    for _ in range(min(slots, pool.size)):
        partial = np.asarray(selection, dtype=int)
        current = 0.0
        if partial.size:
            served = pool.catalogue[pool.viewpoints[partial]]
            share = attention[: partial.size] / attention[: partial.size].sum()
            current = position_entropy(share, served, pool.catalogue)

        best, best_score = None, -np.inf
        for item in range(pool.size):
            if item in selection:
                continue
            extended = np.append(partial, item)
            served = pool.catalogue[pool.viewpoints[extended]]
            share = attention[: extended.size] / attention[: extended.size].sum()
            gain = position_entropy(share, served, pool.catalogue) - current
            score = pool.relevance[item] + mu * gain
            if score > best_score:
                best, best_score = item, score
        selection.append(int(best))

    return np.asarray(selection, dtype=int)


# --------------------------------------------------------------------------------------
# La frontière exacte, et l'écart qui la sépare de chaque méthode.
# --------------------------------------------------------------------------------------


def evaluate_many(
    pool: Pool, selections: np.ndarray, discount: str = "mrr"
) -> tuple[np.ndarray, np.ndarray]:
    """Mesure un lot de fils d'un coup : diversité exposée et engagement.

    Le chemin est vectorisé parce que la frontière exacte en demande des centaines de
    milliers. Il donne exactement ce que rendrait :func:`evaluate` fil par fil --- un test le
    vérifie --- parce que les contenus servis occupent par construction les positions
    canoniques du catalogue, et que leur projection sur les bacs est alors l'identité.
    """
    selections = np.asarray(selections, dtype=int)
    count, slots = selections.shape
    attention = _attention(slots, discount)
    share = attention / attention.sum()

    engagement = pool.relevance[selections] @ attention

    bins = pool.viewpoints[selections] + pool.catalogue_size * np.arange(count)[:, None]
    mass = np.bincount(
        bins.ravel(),
        weights=np.broadcast_to(share, selections.shape).ravel(),
        minlength=count * pool.catalogue_size,
    ).reshape(count, pool.catalogue_size)

    with np.errstate(divide="ignore", invalid="ignore"):
        terms = np.where(mass > 0.0, mass * np.log2(mass), 0.0)
    exposure = -terms.sum(axis=1) / np.log2(pool.catalogue_size)

    return exposure, engagement


def exact_frontier(pool: Pool, slots: int, discount: str = "mrr") -> list[Feed]:
    """Frontière de Pareto exacte du plan (diversité exposée, engagement).

    Tous les arrangements ordonnés de ``slots`` contenus tirés du vivier sont énumérés. La
    frontière retenue est l'ensemble des fils qu'aucun autre ne domine sur les deux grandeurs
    à la fois.

    Raises:
        ValueError: si le nombre d'arrangements dépasse :data:`MAX_ARRANGEMENTS`.
    """
    arrangements = math.perm(pool.size, slots)
    if arrangements > MAX_ARRANGEMENTS:
        raise ValueError(
            f"{arrangements} arrangements à énumérer, au-delà de la limite de "
            f"{MAX_ARRANGEMENTS} : réduire le vivier ou le nombre de positions"
        )

    selections = np.fromiter(
        itertools.chain.from_iterable(itertools.permutations(range(pool.size), slots)),
        dtype=np.int64,
        count=arrangements * slots,
    ).reshape(arrangements, slots)
    exposure, engagement = evaluate_many(pool, selections, discount)

    order = np.lexsort((-engagement, -exposure))
    frontier_feeds: list[Feed] = []
    best_engagement = -np.inf
    for index in order:
        if engagement[index] > best_engagement:
            frontier_feeds.append(
                Feed(selection=selections[index],
                     exposure=float(exposure[index]),
                     engagement=float(engagement[index]))
            )
            best_engagement = float(engagement[index])
    return frontier_feeds


def best_under_floor(feeds: Sequence[Feed], floor: float) -> Feed | None:
    """Le meilleur fil qu'une méthode atteint à diversité au moins égale à ``floor``.

    Comparer des méthodes sur la diversité où chacune tombe serait injuste : les paramètres ne
    se correspondent pas. On fixe donc le plancher et l'on demande à chacune ce qu'elle sait
    faire de mieux en s'y conformant --- exactement la question que pose un régulateur.

    Returns:
        Le fil retenu, ou ``None`` si la méthode n'atteint jamais le plancher.
    """
    admissible = [feed for feed in feeds if feed.exposure >= floor - 1e-12]
    return max(admissible, key=lambda feed: feed.engagement) if admissible else None


def reachable_engagement(frontier_feeds: Sequence[Feed], exposure: float) -> float:
    """Engagement maximal atteignable à diversité exposée au moins égale à ``exposure``."""
    reachable = [feed.engagement for feed in frontier_feeds if feed.exposure >= exposure - 1e-12]
    return max(reachable) if reachable else float("nan")


def shortfall(feed: Feed, frontier_feeds: Sequence[Feed]) -> float:
    """Part d'engagement perdue par rapport au meilleur fil de même diversité.

    C'est la grandeur qui juge un réordonnanceur : non pas sa diversité, ni son engagement,
    mais **l'engagement qu'il laisse sur la table** à la diversité qu'il atteint. Elle vaut
    zéro pour un fil sur la frontière.
    """
    best = reachable_engagement(frontier_feeds, feed.exposure)
    if not math.isfinite(best) or best <= 0.0:
        return float("nan")
    return float(1.0 - feed.engagement / best)


def frontier(
    method: Callable[[float], np.ndarray],
    parameters: Sequence[float],
    pool: Pool,
    discount: str = "mrr",
) -> list[Feed]:
    """Balaie le paramètre d'une méthode et rend les fils correspondants.

    Un réordonnanceur ne se juge pas sur un point : c'est le balayage de son paramètre qui
    produit une courbe comparable à la frontière exacte.
    """
    return [evaluate(pool, method(parameter), discount) for parameter in parameters]
