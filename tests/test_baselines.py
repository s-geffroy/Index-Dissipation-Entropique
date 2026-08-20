"""Les lignes de base, et la frontière exacte qui les juge."""

from __future__ import annotations

import numpy as np
import pytest

from ide.baselines import (
    MAX_ARRANGEMENTS,
    Pool,
    best_under_floor,
    boltzmann_ranking,
    engagement_ranking,
    entropic_ranking,
    evaluate,
    evaluate_many,
    exact_frontier,
    frontier,
    mmr_ranking,
    random_ranking,
    reachable_engagement,
    round_robin_ranking,
    shortfall,
)

SLOTS = 4


def make_pool(seed: int = 0, size: int = 8, catalogue: int = 4) -> Pool:
    generator = np.random.default_rng(seed)
    viewpoints = generator.integers(0, catalogue, size)
    if np.unique(viewpoints).size < 2:
        viewpoints[0] = (viewpoints[0] + 1) % catalogue
    return Pool(
        viewpoints=viewpoints,
        relevance=generator.uniform(0.1, 1.0, size),
        catalogue_size=catalogue,
    )


def test_un_vivier_incoherent_est_refuse():
    with pytest.raises(ValueError, match="point de vue et une pertinence"):
        Pool(viewpoints=np.zeros(3, dtype=int), relevance=np.zeros(2), catalogue_size=4)
    with pytest.raises(ValueError, match="au moins deux points de vue"):
        Pool(viewpoints=np.zeros(2, dtype=int), relevance=np.zeros(2), catalogue_size=1)
    with pytest.raises(ValueError, match="hors catalogue"):
        Pool(viewpoints=np.asarray([0, 9]), relevance=np.zeros(2), catalogue_size=4)


def test_le_chemin_vectorise_rend_la_meme_chose_que_la_mesure_de_reference():
    """La frontière exacte passe par un chemin rapide ; il doit être exact, pas approché."""
    pool = make_pool(3, size=9)
    selections = np.asarray([[0, 1, 2, 3], [3, 2, 1, 0], [0, 0 + 4, 5, 6], [7, 7 - 1, 2, 2]])

    exposure, engagement = evaluate_many(pool, selections)

    for index, selection in enumerate(selections):
        reference = evaluate(pool, selection)
        assert exposure[index] == pytest.approx(reference.exposure)
        assert engagement[index] == pytest.approx(reference.engagement)


def test_le_classement_par_pertinence_maximise_l_engagement():
    pool = make_pool(1, size=9)
    best = evaluate(pool, engagement_ranking(pool, SLOTS))

    for _ in range(200):
        other = evaluate(pool, random_ranking(pool, SLOTS, np.random.default_rng(_)))
        assert other.engagement <= best.engagement + 1e-12


def test_le_filtre_entropique_a_coefficient_nul_est_le_classement_par_pertinence():
    """La propriété qui rend la proposition déployable : un ajout paramétré, pas une refonte."""
    pool = make_pool(2, size=9)

    assert list(entropic_ranking(pool, SLOTS, mu=0.0)) == list(engagement_ranking(pool, SLOTS))


def test_mmr_a_compromis_maximal_est_le_classement_par_pertinence():
    pool = make_pool(4, size=9)

    assert list(mmr_ranking(pool, SLOTS, trade_off=1.0)) == list(engagement_ranking(pool, SLOTS))


def test_un_compromis_hors_bornes_est_refuse():
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        mmr_ranking(make_pool(), SLOTS, trade_off=1.5)


def test_un_coefficient_negatif_est_refuse():
    with pytest.raises(ValueError, match="ne peut être négatif"):
        entropic_ranking(make_pool(), SLOTS, mu=-1.0)


def test_boltzmann_a_temperature_nulle_est_le_classement_par_pertinence():
    pool = make_pool(5, size=9)
    ranking = boltzmann_ranking(pool, SLOTS, temperature=0.0, rng=np.random.default_rng(0))

    assert list(ranking) == list(engagement_ranking(pool, SLOTS))


def test_le_tour_de_role_sert_les_points_de_vue_a_tour_de_role():
    pool = Pool(
        viewpoints=np.asarray([0, 0, 0, 1, 1, 2, 3]),
        relevance=np.asarray([0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]),
        catalogue_size=4,
    )

    served = pool.viewpoints[round_robin_ranking(pool, 4)]

    assert list(served) == [0, 1, 2, 3]


def test_le_tour_de_role_sans_cycle_est_le_classement_par_pertinence():
    pool = make_pool(6, size=9)

    assert list(round_robin_ranking(pool, SLOTS, cycles=0)) == list(engagement_ranking(pool, SLOTS))


def test_toute_methode_est_dominee_ou_egale_par_la_frontiere_exacte():
    """La frontière est une borne supérieure : aucun manque à gagner ne peut être négatif."""
    pool = make_pool(7, size=8)
    front = exact_frontier(pool, SLOTS)

    methods = [
        engagement_ranking(pool, SLOTS),
        round_robin_ranking(pool, SLOTS),
        mmr_ranking(pool, SLOTS, 0.5),
        entropic_ranking(pool, SLOTS, 1.0),
        boltzmann_ranking(pool, SLOTS, 0.2, np.random.default_rng(0)),
    ]
    for selection in methods:
        assert shortfall(evaluate(pool, selection), front) >= -1e-9


def test_la_frontiere_est_strictement_decroissante():
    """Un fil de la frontière n'est dominé par aucun autre : plus de diversité coûte."""
    front = exact_frontier(make_pool(8, size=8), SLOTS)

    exposures = [feed.exposure for feed in front]
    engagements = [feed.engagement for feed in front]
    assert exposures == sorted(exposures, reverse=True)
    assert engagements == sorted(engagements)


def test_une_enumeration_trop_grande_est_refusee():
    pool = make_pool(9, size=30)

    with pytest.raises(ValueError, match="au-delà de la limite"):
        exact_frontier(pool, 8)
    assert MAX_ARRANGEMENTS > 1_000_000


def test_le_plancher_inatteignable_le_dit():
    pool = Pool(viewpoints=np.zeros(6, dtype=int), relevance=np.linspace(1, 0.5, 6),
                catalogue_size=4)
    front = exact_frontier(pool, SLOTS)

    assert np.isnan(reachable_engagement(front, 0.5))
    assert best_under_floor(frontier(lambda _: engagement_ranking(pool, SLOTS), [0], pool),
                            0.5) is None


def test_le_filtre_entropique_se_tient_sur_la_frontiere_aux_planchers_eleves():
    """Le résultat que la comparaison devait établir, figé sur des viviers tirés au sort.

    Ce que le filtre doit démontrer n'est pas qu'il diversifie — n'importe quel tirage au sort
    le fait — mais qu'il diversifie **sans laisser d'engagement sur la table**.
    """
    losses = []
    for seed in range(12):
        pool = make_pool(100 + seed, size=9)
        front = exact_frontier(pool, SLOTS)
        if not np.isfinite(reachable_engagement(front, 0.8)):
            continue
        sweep = frontier(lambda mu, chosen=pool: entropic_ranking(chosen, SLOTS, mu),
                         (0.0, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0), pool)
        choice = best_under_floor(sweep, 0.8)
        if choice is not None:
            losses.append(shortfall(choice, front))

    assert losses, "aucun vivier exploitable : le test ne mesure rien"
    assert np.median(losses) < 0.03


def test_le_tirage_au_sort_laisse_beaucoup_plus_d_engagement_sur_la_table():
    """La ligne de base qu'on oublie de tracer, et pourquoi il faut la tracer."""
    entropic_losses, random_losses = [], []
    for seed in range(12):
        pool = make_pool(200 + seed, size=9)
        front = exact_frontier(pool, SLOTS)
        if not np.isfinite(reachable_engagement(front, 0.7)):
            continue
        entropic = best_under_floor(
            frontier(lambda mu, chosen=pool: entropic_ranking(chosen, SLOTS, mu),
                     (0.5, 1.0, 2.0, 4.0), pool), 0.7
        )
        drawn = best_under_floor(
            frontier(lambda seed, chosen=pool: random_ranking(
                chosen, SLOTS, np.random.default_rng(int(seed))), range(12), pool), 0.7
        )
        if entropic is not None and drawn is not None:
            entropic_losses.append(shortfall(entropic, front))
            random_losses.append(shortfall(drawn, front))

    assert np.median(random_losses) > np.median(entropic_losses) + 0.05
