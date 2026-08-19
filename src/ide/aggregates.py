"""Ce qu'il faut demander à une plateforme, et de quoi prouver que cela suffit.

Pourquoi une demande doit être une spécification
------------------------------------------------

Les trois journaux publics mesurés jusqu'ici ne permettent pas l'évaluation annoncée :
[MIND](mind.py) a les catégories éditoriales mais pas le rang, [Baidu-ULTR](exposure.py) le rang
mais aucune étiquette, l'Open Bandit Dataset le rang et la propension mais des attributs
anonymisés. Il reste une voie, prévue par l'article 40 du *Digital Services Act* : **demander la
donnée**.

Une demande de données n'est recevable que si elle est **nécessaire et proportionnée**
(art. 40(8)(e) du DSA, art. 8(d) du règlement délégué (UE) 2025/2050). Or « donnez-nous vos
journaux » n'est ni l'un ni l'autre : cela réclame des données personnelles dont l'analyse n'a
aucun besoin, et cela offre à la plateforme le motif de refus le plus facile — la sécurité du
service et le secret des affaires (art. 40(5) du DSA).

Ce module retourne la question. Il définit les **quatre tableaux agrégés** dont les mesures de
ce dépôt ont réellement besoin, et fournit de quoi vérifier qu'elles s'y retrouvent **à
l'identique**. Ce qui est demandé n'est alors plus un accès, c'est un livrable :

===  Les quatre tableaux

1. **Profils de fils** — pour chaque forme de fil servie (la liste des rangs qu'elle occupe) et
   chaque nombre de clics, le nombre de fils. Aucune ligne ne désigne un lecteur.
2. **Clics par rang** — pour chaque profil, chaque **nombre de clics du fil** et chaque rang, le
   nombre de clics. Le deuxième index n'est pas un ornement : sans lui, les fils dont *tout* a
   été cliqué — qui ne contraignent rien — ne peuvent pas être écartés du calcul, et le test
   d'échangeabilité se décale (:math:`z = -203{,}9` au lieu de :math:`-205{,}7` sur
   Baidu-ULTR).
3. **Cellules (contenu, rang)** — impressions et clics, et la **propension de service** si la
   plateforme la connaît.
4. **Exposition par (rang, point de vue)** — impressions et clics, sur le catalogue de points de
   vue **déclaré par le régulateur**.

Ce que chacun permet, et rien de plus
--------------------------------------

* le test d'échangeabilité de :func:`ide.logs.exchangeability_test` — celui qui décide si un
  journal est corrigible — se recalcule **exactement** depuis les tableaux 1 et 2 ;
* la sévérité :math:`\\eta` du biais de position, depuis le tableau 3 ;
* l'estimation contrefactuelle et sa taille d'échantillon effective, depuis le tableau 3 avec
  ses propensions ;
* la diversité servie, aveugle au rang **et** consciente du rang — donc l'écart d'enterrement
  qui est la grandeur de contrôle du [mémorandum](../../docs/memorandum.md) — depuis le
  tableau 4.

.. warning::
    Un agrégat est une **hypothèse sur les données**, et celle-ci est explicite : les tableaux 1
    et 2 sont indexés par le **profil de rangs** du fil, non par sa seule longueur. C'est la
    correction qu'a imposée Baidu-ULTR, où une page de résultats saute des rangs — et où
    résumer un fil à sa longueur produisait un chiffre faux, du bon ordre de grandeur.

Ce que les tableaux ne contiennent pas
--------------------------------------

Aucun identifiant de lecteur, aucune séquence de navigation, aucun contenu, aucun texte. Un fil
n'y figure que par sa forme et par le nombre de clics qu'il a reçus. La plus petite unité est la
**cellule**, et :func:`aggregate` sait en supprimer les effectifs faibles — dont
:func:`suppression_sensitivity` mesure ce que la suppression coûte à l'estimation, parce qu'un
seuil de confidentialité déplace les chiffres et doit être publié avec eux.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from ide.logs import ExchangeabilityTest, Impressions
from ide.offpolicy import PositionBiasEstimate, estimate_position_bias
from ide.radio import rank_weights

__all__ = [
    "AggregateRequest",
    "aggregate",
    "blind_distribution",
    "exchangeability_from",
    "served_distribution",
    "severity_from",
    "suppression_sensitivity",
]


@dataclass(frozen=True)
class AggregateRequest:
    """Les quatre tableaux demandés, et rien d'autre.

    Attributes:
        profile_offsets: bornes de chaque profil de rangs dans ``profile_ranks``.
        profile_ranks: rangs servis, profil par profil.
        feed_profiles: profil de chaque ligne du tableau 1.
        feed_clicks: nombre de clics de la ligne.
        feed_counts: nombre de fils de ce profil ayant reçu ce nombre de clics.
        click_profiles: profil de chaque ligne du tableau 2.
        click_feed_clicks: nombre de clics du fil dont la ligne provient.
        click_ranks: rang de la ligne.
        click_counts: clics observés à ce rang, pour ce profil et ce nombre de clics.
        cell_items: contenu de chaque cellule du tableau 3.
        cell_ranks: rang de la cellule.
        cell_exposures: impressions de la cellule.
        cell_clicks: clics de la cellule.
        cell_propensities: propension de service, ou ``None`` si la plateforme ne la publie pas.
        category_ranks: rang de chaque ligne du tableau 4.
        category_labels: point de vue de la ligne, sur le catalogue déclaré.
        category_exposures: impressions de la ligne.
        suppression: effectif en deçà duquel une ligne a été supprimée.
    """

    profile_offsets: np.ndarray
    profile_ranks: np.ndarray
    feed_profiles: np.ndarray
    feed_clicks: np.ndarray
    feed_counts: np.ndarray
    click_profiles: np.ndarray
    click_feed_clicks: np.ndarray
    click_ranks: np.ndarray
    click_counts: np.ndarray
    cell_items: np.ndarray
    cell_ranks: np.ndarray
    cell_exposures: np.ndarray
    cell_clicks: np.ndarray
    cell_propensities: np.ndarray | None
    category_ranks: np.ndarray | None
    category_labels: np.ndarray | None
    category_exposures: np.ndarray | None
    suppression: int

    @property
    def rows(self) -> int:
        """Nombre total de lignes demandées — la grandeur qui rend la demande proportionnée."""
        total = self.feed_counts.size + self.click_counts.size + self.cell_items.size
        if self.category_exposures is not None:
            total += self.category_exposures.size
        return int(total)

    def profile(self, index: int) -> np.ndarray:
        """Les rangs servis par un profil de fil."""
        start, stop = self.profile_offsets[index], self.profile_offsets[index + 1]
        return self.profile_ranks[start:stop]


def aggregate(
    impressions: Impressions,
    categories: np.ndarray | None = None,
    propensities: np.ndarray | None = None,
    suppression: int = 0,
) -> AggregateRequest:
    """Construit les quatre tableaux demandés depuis un journal d'impressions.

    C'est l'opération que la plateforme aurait à faire. La coder ici sert à deux choses :
    éprouver que les tableaux suffisent, et chiffrer ce qu'ils pèsent.

    Args:
        impressions: le journal.
        categories: point de vue de chaque ligne servie, sur le catalogue déclaré. Sans lui, le
            quatrième tableau n'est pas produit.
        propensities: propension de service de chaque ligne, si la plateforme la connaît.
        suppression: effectif en deçà duquel une ligne agrégée est supprimée. C'est le seuil de
            confidentialité, et il déplace les estimations : :func:`suppression_sensitivity`
            mesure de combien.

    Returns:
        Les tableaux, prêts à être confrontés aux mesures directes.
    """
    if impressions.items is None:
        raise ValueError("l'agrégat par contenu exige l'identité des contenus servis")
    if suppression < 0:
        raise ValueError("un seuil de suppression ne peut être négatif")

    order = np.argsort(impressions.feeds, kind="stable")
    ranks = impressions.ranks[order]
    clicks = impressions.clicks[order]
    lengths = impressions.feed_lengths
    bounds = np.concatenate([[0], np.cumsum(lengths)])

    # --- profils de rangs : la forme des fils servis, indépendamment de leur contenu ---
    signatures: dict[bytes, int] = {}
    profile_of_feed = np.empty(lengths.size, dtype=np.int64)
    profile_ranks: list[np.ndarray] = []
    for index in range(lengths.size):
        served = ranks[bounds[index]:bounds[index + 1]]
        key = served.astype(np.int32).tobytes()
        if key not in signatures:
            signatures[key] = len(profile_ranks)
            profile_ranks.append(served.astype(np.int32))
        profile_of_feed[index] = signatures[key]

    profile_offsets = np.concatenate(
        [[0], np.cumsum([profile.size for profile in profile_ranks])]
    ).astype(np.int64)
    flat_profiles = (np.concatenate(profile_ranks) if profile_ranks
                     else np.zeros(0, dtype=np.int32))

    clicks_per_feed = np.array(
        [clicks[bounds[index]:bounds[index + 1]].sum() for index in range(lengths.size)],
        dtype=np.int64,
    )

    # --- tableau 1 : combien de fils de tel profil ont reçu tel nombre de clics ---
    pairs, counts = np.unique(
        np.stack([profile_of_feed, clicks_per_feed], axis=1), axis=0, return_counts=True
    )
    feed_profiles, feed_clicks, feed_counts = pairs[:, 0], pairs[:, 1], counts

    # --- tableau 2 : combien de clics à tel rang, pour tel profil et tel total de clics ---
    row_profiles = np.repeat(profile_of_feed, lengths)
    row_feed_clicks = np.repeat(clicks_per_feed, lengths)
    clicked = clicks > 0
    click_keys, click_counts = np.unique(
        np.stack([row_profiles[clicked], row_feed_clicks[clicked], ranks[clicked]], axis=1),
        axis=0, return_counts=True,
    )
    click_profiles, click_feed_clicks, click_ranks = (
        click_keys[:, 0], click_keys[:, 1], click_keys[:, 2]
    )

    # --- tableau 3 : cellules (contenu, rang), avec propension si elle est connue ---
    columns = [impressions.items, impressions.ranks]
    if propensities is not None:
        propensity_values, propensity_index = np.unique(propensities, return_inverse=True)
        columns.append(propensity_index)
    keys, inverse = np.unique(np.stack(columns, axis=1), axis=0, return_inverse=True)
    cell_exposures = np.bincount(inverse, minlength=len(keys))
    cell_clicks = np.bincount(inverse, weights=impressions.clicks, minlength=len(keys))
    cell_propensities = (propensity_values[keys[:, 2]] if propensities is not None else None)

    # --- tableau 4 : exposition par (rang, point de vue) ---
    category_ranks = category_labels = category_exposures = None
    if categories is not None:
        category_keys, category_index = np.unique(
            np.stack([impressions.ranks, np.asarray(categories)], axis=1), axis=0,
            return_inverse=True,
        )
        category_exposures = np.bincount(category_index, minlength=len(category_keys))
        category_ranks, category_labels = category_keys[:, 0], category_keys[:, 1]

    request = AggregateRequest(
        profile_offsets=profile_offsets,
        profile_ranks=flat_profiles,
        feed_profiles=feed_profiles.astype(np.int64),
        feed_clicks=feed_clicks.astype(np.int64),
        feed_counts=feed_counts.astype(np.int64),
        click_profiles=click_profiles.astype(np.int64),
        click_feed_clicks=click_feed_clicks.astype(np.int64),
        click_ranks=click_ranks.astype(np.int64),
        click_counts=click_counts.astype(np.int64),
        cell_items=keys[:, 0].astype(np.int64),
        cell_ranks=keys[:, 1].astype(np.int64),
        cell_exposures=cell_exposures.astype(np.int64),
        cell_clicks=cell_clicks.astype(np.int64),
        cell_propensities=cell_propensities,
        category_ranks=category_ranks,
        category_labels=category_labels,
        category_exposures=category_exposures,
        suppression=suppression,
    )
    return _suppress(request, suppression) if suppression else request


def _suppress(request: AggregateRequest, threshold: int) -> AggregateRequest:
    """Retire les lignes dont l'effectif est inférieur au seuil de confidentialité."""
    feeds = request.feed_counts >= threshold
    clicks = request.click_counts >= threshold
    cells = request.cell_exposures >= threshold
    categories = (request.category_exposures >= threshold
                  if request.category_exposures is not None else None)

    return AggregateRequest(
        profile_offsets=request.profile_offsets,
        profile_ranks=request.profile_ranks,
        feed_profiles=request.feed_profiles[feeds],
        feed_clicks=request.feed_clicks[feeds],
        feed_counts=request.feed_counts[feeds],
        click_profiles=request.click_profiles[clicks],
        click_feed_clicks=request.click_feed_clicks[clicks],
        click_ranks=request.click_ranks[clicks],
        click_counts=request.click_counts[clicks],
        cell_items=request.cell_items[cells],
        cell_ranks=request.cell_ranks[cells],
        cell_exposures=request.cell_exposures[cells],
        cell_clicks=request.cell_clicks[cells],
        cell_propensities=(request.cell_propensities[cells]
                           if request.cell_propensities is not None else None),
        category_ranks=(request.category_ranks[categories]
                        if categories is not None else None),
        category_labels=(request.category_labels[categories]
                         if categories is not None else None),
        category_exposures=(request.category_exposures[categories]
                            if categories is not None else None),
        suppression=threshold,
    )


def exchangeability_from(request: AggregateRequest) -> ExchangeabilityTest:
    """Recalcule le test d'échangeabilité depuis les seuls tableaux 1 et 2.

    Le test somme les rangs normalisés des contenus cliqués et les compare à ce qu'un tirage
    sans remise donnerait, fil par fil. Or cette somme ne dépend du fil que par son **profil de
    rangs** et par son **nombre de clics** — donc les deux tableaux agrégés y suffisent, sans
    qu'aucune ligne ne désigne un lecteur.

    C'est la démonstration qui rend la demande proportionnée : le contrôle qui décide si un
    journal est corrigible n'exige aucune donnée individuelle.
    """
    profiles = request.profile_offsets.size - 1
    normalised_mean = np.zeros(profiles)
    normalised_variance = np.zeros(profiles)
    normalised_of_rank: list[dict[int, float]] = []
    lengths = np.zeros(profiles)

    for index in range(profiles):
        served = request.profile(index).astype(float)
        length = served.size
        lengths[index] = length
        normalised = (served - 0.5) / length
        normalised_mean[index] = normalised.mean()
        normalised_variance[index] = normalised.var()
        normalised_of_rank.append(dict(zip(served.astype(int), normalised, strict=True)))

    informative = (lengths[request.feed_profiles] >= 2) & (request.feed_clicks > 0) & (
        request.feed_clicks < lengths[request.feed_profiles]
    )
    kept_profiles = request.feed_profiles[informative]
    kept_clicks = request.feed_clicks[informative].astype(float)
    kept_counts = request.feed_counts[informative].astype(float)
    kept_lengths = lengths[kept_profiles]

    if kept_counts.sum() == 0:
        return ExchangeabilityTest(float("nan"), float("nan"), float("nan"), float("nan"), 0)

    # Les clics d'un fil non informatif — aucun clic, ou que des clics — ne contraignent rien
    # et ne doivent pas entrer dans la somme. C'est ce que le second index du tableau 2 permet.
    informative_click_rows = (
        (lengths[request.click_profiles] >= 2)
        & (request.click_feed_clicks > 0)
        & (request.click_feed_clicks < lengths[request.click_profiles])
    )
    statistic = 0.0
    for profile, rank, count in zip(
        request.click_profiles[informative_click_rows],
        request.click_ranks[informative_click_rows],
        request.click_counts[informative_click_rows],
        strict=True,
    ):
        statistic += count * normalised_of_rank[profile][int(rank)]

    expectation = float((kept_counts * kept_clicks * normalised_mean[kept_profiles]).sum())
    variance = float(
        (
            kept_counts
            * kept_clicks
            * (kept_lengths - kept_clicks)
            / (kept_lengths - 1.0)
            * normalised_variance[kept_profiles]
        ).sum()
    )
    if variance <= 0.0:
        return ExchangeabilityTest(statistic, expectation, float("nan"), float("nan"),
                                   int(kept_counts.sum()))

    deviation = (statistic - expectation) / np.sqrt(variance)
    p_value = math.erfc(abs(deviation) / math.sqrt(2.0))
    return ExchangeabilityTest(float(statistic), expectation, float(deviation), p_value,
                               int(kept_counts.sum()))


def severity_from(request: AggregateRequest,
                  minimum_impressions: int = 5) -> PositionBiasEstimate:
    """Recalcule la sévérité du biais de position depuis le seul tableau 3."""
    items = np.repeat(request.cell_items, request.cell_exposures)
    ranks = np.repeat(request.cell_ranks, request.cell_exposures)
    clicks = np.concatenate(
        [
            np.concatenate([np.ones(hit), np.zeros(seen - hit)])
            for seen, hit in zip(request.cell_exposures, request.cell_clicks, strict=True)
        ]
    ) if request.cell_items.size else np.zeros(0)
    return estimate_position_bias(items, ranks, clicks, minimum_impressions=minimum_impressions)


def blind_distribution(request: AggregateRequest) -> np.ndarray:
    """Distribution des points de vue servis, **aveugle au rang**, depuis le tableau 4."""
    if request.category_exposures is None:
        raise ValueError("le quatrième tableau — exposition par point de vue — n'a pas été fourni")
    labels = request.category_labels
    weights = np.bincount(labels, weights=request.category_exposures.astype(float))
    total = weights.sum()
    return weights / total if total else weights


def served_distribution(request: AggregateRequest, discount: str = "mrr") -> np.ndarray:
    """Distribution des points de vue **pondérée par l'attention** de chaque rang.

    C'est la mesure que le mémorandum impose, et l'écart avec :func:`blind_distribution` est la
    grandeur de contrôle de l'enterrement. Les deux se calculent sur le même tableau agrégé.
    """
    if request.category_exposures is None:
        raise ValueError("le quatrième tableau — exposition par point de vue — n'a pas été fourni")
    maximum_rank = int(request.category_ranks.max())
    attention = rank_weights(maximum_rank, discount=discount)[request.category_ranks - 1]
    weights = np.bincount(
        request.category_labels, weights=request.category_exposures.astype(float) * attention
    )
    total = weights.sum()
    return weights / total if total else weights


def suppression_sensitivity(
    impressions: Impressions,
    thresholds: tuple[int, ...] = (0, 5, 20, 50),
    minimum_impressions: int = 5,
) -> dict[int, tuple[float, float, int]]:
    """Ce que le seuil de confidentialité coûte aux estimations.

    Supprimer les faibles effectifs protège les lecteurs et **déplace les chiffres** : les
    cellules rares sont aussi celles des rangs profonds, dont l'estimation de :math:`\\eta` tire
    l'essentiel de son information. Le seuil doit donc être publié avec le résultat, et son
    effet mesuré plutôt que supposé.

    Returns:
        Par seuil : la sévérité estimée, son erreur type, et le nombre de lignes demandées.
    """
    measured: dict[int, tuple[float, float, int]] = {}
    for threshold in thresholds:
        request = aggregate(impressions, suppression=threshold)
        estimate = severity_from(request, minimum_impressions=minimum_impressions)
        measured[threshold] = (estimate.severity, estimate.standard_error, request.rows)
    return measured
