"""Les deux journaux qui enregistrent le rang servi, et ce qu'ils permettent de vérifier."""

from __future__ import annotations

import numpy as np
import pytest

from ide.exposure import (
    SOURCES,
    Digest,
    bucket_from_digest,
    load_digest,
    obd_cells,
    obd_click_rates,
    off_policy_check,
    source_path,
    verify_source,
)
from ide.logs import exchangeability_test, naive_severity_fit
from ide.offpolicy import estimate_position_bias


def synthetic_bucket(rows, catalogue=4, severity=0.0, seed=0):
    """Un seau de service à propensions **connues**, pour éprouver la confrontation."""
    generator = np.random.default_rng(seed)
    quality = generator.uniform(0.05, 0.4, catalogue)
    positions = generator.integers(1, 4, rows)
    weights = generator.dirichlet(np.full(catalogue, 0.6))
    items = generator.choice(catalogue, size=rows, p=weights)
    probability = quality[items] * positions.astype(float) ** (-severity)
    return {
        "items": items.astype(np.int64),
        "positions": positions.astype(np.int64),
        "clicks": (generator.random(rows) < probability).astype(float),
        "propensities": weights[items],
        "item_count": np.asarray(catalogue),
    }


def test_un_journal_inconnu_est_refuse():
    with pytest.raises(ValueError, match="journal inconnu"):
        source_path("gallica")
    with pytest.raises(ValueError, match="journal inconnu"):
        verify_source("gallica")


def test_un_journal_absent_indique_comment_le_recuperer(tmp_path):
    with pytest.raises(FileNotFoundError, match="fetch_exposure"):
        verify_source("baidu", directory=tmp_path)


def test_les_empreintes_attendues_sont_bien_formees():
    for name, (relative, size, digest) in SOURCES.items():
        assert relative.count("/") == 1, name
        assert size > 100_000_000, name
        assert len(digest) == 64, name


def test_le_taux_de_clic_par_position_porte_son_erreur_type():
    bucket = synthetic_bucket(6000, severity=0.0, seed=3)

    rates = obd_click_rates(bucket)

    assert set(rates) == {1, 2, 3}
    for exposures, successes, rate, error in rates.values():
        assert successes <= exposures
        assert rate == pytest.approx(successes / exposures)
        assert error == pytest.approx(np.sqrt(rate * (1 - rate) / exposures))


def test_les_cellules_redeployees_rendent_le_seau_d_origine():
    bucket = synthetic_bucket(20_000, severity=0.3, seed=7)
    digest = Digest(sources={"b": "sha"}, minimum_impressions=1, splits={"b": obd_cells(bucket)})

    rebuilt = bucket_from_digest(digest, "b")

    assert rebuilt["clicks"].size == bucket["clicks"].size
    assert rebuilt["clicks"].sum() == bucket["clicks"].sum()
    assert obd_click_rates(rebuilt) == obd_click_rates(bucket)
    assert estimate_position_bias(
        rebuilt["items"], rebuilt["positions"], rebuilt["clicks"]
    ).severity == pytest.approx(
        estimate_position_bias(bucket["items"], bucket["positions"], bucket["clicks"]).severity
    )


def test_la_confrontation_retrouve_la_valeur_de_la_politique_cible():
    """Le cas d'école : la cible est uniforme, le journal ne l'est pas, et l'IPS le corrige."""
    logged = synthetic_bucket(400_000, severity=0.0, seed=11)
    generator = np.random.default_rng(12)
    catalogue = int(logged["item_count"])
    items = generator.integers(0, catalogue, 200_000)
    quality = np.array([logged["clicks"][logged["items"] == item].mean()
                        for item in range(catalogue)])
    target = {
        "items": items,
        "positions": generator.integers(1, 4, items.size),
        "clicks": (generator.random(items.size) < quality[items]).astype(float),
        "propensities": np.full(items.size, 1.0 / catalogue),
        "item_count": np.asarray(catalogue),
    }

    check = off_policy_check(target, logged)

    assert abs(check.relative_error(check.importance_sampling)) < 0.05
    assert abs(check.relative_error(check.naive)) > abs(
        check.relative_error(check.importance_sampling)
    )
    assert 0.0 < check.effective_share <= 1.0
    assert set(check.clipped) == {10.0, 100.0, 1000.0}


def test_baidu_enregistre_bien_le_rang_servi():
    """Le contrôle positif que MIND avait échoué, sur le condensé versionné.

    L'écart réduit doit être **négatif** : un biais de position concentre les clics en haut.
    Un test qui rejetterait du mauvais côté signalerait une erreur de signe, pas une découverte.
    """
    impressions = load_digest().impressions("baidu")

    verdict = exchangeability_test(impressions)

    assert verdict.deviation < -100.0
    assert verdict.p_value < 1e-12
    assert not verdict.exchangeable


def test_la_severite_de_baidu_se_situe_autour_de_un():
    digest = load_digest()
    items, ranks, clicks = digest.rows("baidu")

    fixed_effects = estimate_position_bias(items, ranks, clicks, minimum_impressions=5)
    aggregate = naive_severity_fit(digest.impressions("baidu"), maximum_rank=10)

    assert fixed_effects.severity == pytest.approx(1.10, abs=0.05)
    assert fixed_effects.standard_error < 0.1
    # L'ajustement agrégé surestime : la plateforme place les meilleurs documents en tête, et
    # cette qualité-là entre dans la pente tant qu'on ne l'élimine pas par effets fixes.
    assert aggregate > fixed_effects.severity + 0.3


def test_le_bandeau_de_l_open_bandit_dataset_a_un_biais_bien_plus_faible():
    """Trois vignettes horizontales, allocation aléatoire : l'effet de position y est ténu.

    C'est la mesure qui interdit de traiter $\\eta$ comme une constante : la même grandeur vaut
    1,1 sur une page de résultats verticale et un dixième de cela sur un bandeau de trois.
    """
    rates = obd_click_rates(bucket_from_digest(load_digest(), "obd_random_all"))

    first, last = rates[1], rates[3]
    assert first[2] > last[2]
    # L'écart entre la première et la dernière vignette ne dépasse pas deux erreurs types
    # cumulées : mesurable en tendance, pas concluant vignette à vignette.
    assert first[2] - last[2] < 2 * (first[3] + last[3])


def test_l_estimation_contrefactuelle_est_confrontee_a_une_mesure_directe():
    """Le seul endroit du dépôt où l'estimateur est jugé contre la valeur qu'il estime."""
    digest = load_digest()

    check = off_policy_check(
        bucket_from_digest(digest, "obd_random_men"),
        bucket_from_digest(digest, "obd_bts_men"),
    )

    assert check.truth == pytest.approx(0.00512, abs=0.0001)
    assert abs(check.relative_error(check.importance_sampling)) < 0.05
    assert check.relative_error(check.naive) > 0.25
    # Et le diagnostic qui interdit de crier victoire : l'estimation sans biais repose sur
    # l'équivalent de mille cinq cents observations, pour quatre millions d'impressions.
    assert check.effective_size < 3_000
    assert check.effective_share < 0.001
