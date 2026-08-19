"""Les quatre tableaux demandés au titre de l'article 40, et la preuve qu'ils suffisent."""

from __future__ import annotations

import numpy as np
import pytest

from ide.aggregates import (
    aggregate,
    blind_distribution,
    exchangeability_from,
    served_distribution,
    severity_from,
    suppression_sensitivity,
)
from ide.exposure import load_digest as load_exposure_digest
from ide.logs import Impressions, exchangeability_test
from ide.mind import load_digest as load_mind_digest
from ide.offpolicy import estimate_position_bias
from ide.radio import rank_weights


def make_feeds(ranks_per_feed, clicks_per_feed, items_per_feed):
    lengths = np.asarray([len(ranks) for ranks in ranks_per_feed], dtype=np.int64)
    return Impressions(
        items=np.concatenate(items_per_feed).astype(np.int64),
        ranks=np.concatenate(ranks_per_feed).astype(np.int64),
        clicks=np.concatenate(clicks_per_feed).astype(float),
        feeds=np.repeat(np.arange(lengths.size), lengths),
        feed_lengths=lengths,
    )


def random_feeds(feeds=800, slots=6, seed=0, severity=0.8):
    generator = np.random.default_rng(seed)
    ranks = np.tile(np.arange(1, slots + 1), feeds)
    quality = generator.uniform(0.1, 0.5, 40)
    items = generator.integers(0, 40, feeds * slots)
    probability = np.clip(quality[items] * ranks ** (-severity), 0, 1)
    return Impressions(
        items=items.astype(np.int64),
        ranks=ranks.astype(np.int64),
        clicks=(generator.random(feeds * slots) < probability).astype(float),
        feeds=np.repeat(np.arange(feeds), slots).astype(np.int64),
        feed_lengths=np.full(feeds, slots, dtype=np.int64),
    )


def test_l_agregat_exige_l_identite_des_contenus():
    feeds = random_feeds(feeds=10)
    anonymous = Impressions(items=None, ranks=feeds.ranks, clicks=feeds.clicks,
                            feeds=feeds.feeds, feed_lengths=feeds.feed_lengths)

    with pytest.raises(ValueError, match="identité des contenus"):
        aggregate(anonymous)


def test_un_seuil_de_suppression_negatif_est_refuse():
    with pytest.raises(ValueError, match="ne peut être négatif"):
        aggregate(random_feeds(feeds=10), suppression=-1)


def test_le_test_d_echangeabilite_se_recalcule_a_l_identique():
    feeds = random_feeds(seed=3)

    assert exchangeability_from(aggregate(feeds)).deviation == pytest.approx(
        exchangeability_test(feeds).deviation
    )


def test_il_se_recalcule_aussi_quand_les_rangs_sautent():
    """Une page de résultats saute des rangs : les tableaux sont indexés par profil, pas par
    longueur, et c'est ce qui les rend exacts sur autre chose qu'un fil canonique."""
    feeds = make_feeds(
        [np.asarray([1, 2, 5]), np.asarray([3, 7]), np.asarray([1, 2, 5])],
        [[1, 0, 0], [0, 1], [0, 1, 1]],
        [[10, 11, 12], [11, 13], [14, 11, 12]],
    )

    assert exchangeability_from(aggregate(feeds)).deviation == pytest.approx(
        exchangeability_test(feeds).deviation, nan_ok=True
    )


def test_un_fil_entierement_clique_ne_doit_pas_entrer_dans_la_somme():
    """Le défaut trouvé sur Baidu-ULTR, figé ici.

    Un fil dont *tout* a été cliqué ne contraint rien — la position des clics y est forcée — et
    ses clics doivent être écartés. Sans le nombre de clics du fil en second index du tableau 2,
    l'agrégat ne sait pas les distinguer, et l'écart réduit se décale.
    """
    feeds = make_feeds(
        [np.arange(1, 4), np.arange(1, 4), np.arange(1, 4)],
        [[1, 1, 1], [1, 0, 0], [0, 0, 1]],
        [[1, 2, 3], [1, 2, 3], [1, 2, 3]],
    )

    request = aggregate(feeds)
    entirely_clicked = request.click_feed_clicks == 3
    assert entirely_clicked.any(), "le cas à écarter doit exister dans le tableau"
    assert exchangeability_from(request).deviation == pytest.approx(
        exchangeability_test(feeds).deviation
    )


def test_la_severite_se_recalcule_a_l_identique():
    feeds = random_feeds(feeds=4000, seed=5)

    direct = estimate_position_bias(feeds.items, feeds.ranks, feeds.clicks,
                                    minimum_impressions=5)
    from_tables = severity_from(aggregate(feeds), minimum_impressions=5)

    assert from_tables.severity == pytest.approx(direct.severity)
    assert from_tables.standard_error == pytest.approx(direct.standard_error)


def test_les_deux_distributions_de_points_de_vue_se_recalculent_a_l_identique():
    generator = np.random.default_rng(7)
    feeds, slots, viewpoints = 600, 8, 4
    categories = generator.integers(0, viewpoints, feeds * slots)
    impressions = Impressions(
        items=categories.astype(np.int64),
        ranks=np.tile(np.arange(1, slots + 1), feeds).astype(np.int64),
        clicks=(generator.random(feeds * slots) < 0.1).astype(float),
        feeds=np.repeat(np.arange(feeds), slots).astype(np.int64),
        feed_lengths=np.full(feeds, slots, dtype=np.int64),
    )

    request = aggregate(impressions, categories=categories)
    attention = np.tile(rank_weights(slots), feeds)
    expected_served = np.bincount(categories, weights=attention, minlength=viewpoints)

    assert blind_distribution(request) == pytest.approx(
        np.bincount(categories, minlength=viewpoints) / categories.size
    )
    assert served_distribution(request) == pytest.approx(
        expected_served / expected_served.sum()
    )


def test_les_distributions_exigent_le_quatrieme_tableau():
    request = aggregate(random_feeds(feeds=50))

    for compute in (blind_distribution, served_distribution):
        with pytest.raises(ValueError, match="quatrième tableau"):
            compute(request)


def test_la_demande_est_bien_plus_petite_que_le_journal():
    """La proportionnalité n'est pas une intention, c'est un rapport de tailles."""
    feeds = random_feeds(feeds=5000, slots=10, seed=9)

    request = aggregate(feeds)

    assert request.rows < feeds.served / 5


def test_le_seuil_de_confidentialite_deplace_l_estimation():
    """Supprimer les faibles effectifs n'est pas neutre : le seuil doit être publié."""
    feeds = random_feeds(feeds=6000, slots=10, seed=13)

    measured = suppression_sensitivity(feeds, thresholds=(0, 5, 200))

    assert measured[0][2] > measured[200][2]  # moins de lignes demandées
    assert measured[0][0] != pytest.approx(measured[200][0], abs=1e-6)


def test_l_echangeabilite_agregee_rend_les_chiffres_publies_sur_les_deux_journaux():
    """Le verrou sur données réelles : mêmes chiffres, sans aucune donnée individuelle."""
    mind = load_mind_digest().impressions("train")
    baidu = load_exposure_digest().impressions("baidu")

    for impressions, expected in ((mind, 0.1159), (baidu, -205.72)):
        # Le condensé ne retient pas l'identité ligne à ligne ; les tableaux 1 et 2 n'en
        # dépendent pas, et c'est d'eux seuls que vient le test.
        with_placeholder = Impressions(
            items=impressions.ranks, ranks=impressions.ranks, clicks=impressions.clicks,
            feeds=impressions.feeds, feed_lengths=impressions.feed_lengths,
        )
        from_tables = exchangeability_from(aggregate(with_placeholder))
        assert from_tables.deviation == pytest.approx(
            exchangeability_test(impressions).deviation
        )
        assert from_tables.deviation == pytest.approx(expected, abs=0.01)
