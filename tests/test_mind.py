"""L'exploration enregistrée dans MIND : ce que le journal contient, et ce qu'il n'a plus."""

from __future__ import annotations

import numpy as np
import pytest

from ide.mind import (
    DIGEST_MINIMUM_IMPRESSIONS,
    EXPECTED_SPLITS,
    Impressions,
    build_digest,
    click_rate_by_rank,
    detectable_severity,
    exchangeability_test,
    load_digest,
    load_split,
    naive_severity_fit,
    parse_behaviours,
    rank_coverage,
    save_digest,
    simulate_feeds,
    split_path,
    verify_split,
)
from ide.offpolicy import estimate_position_bias

FIXTURE = (
    "1\tU1\t11/10/2019 9:48:49 PM\tN10 N11\tN20-0 N21-1 N22-0\n"
    "2\tU2\t11/10/2019 9:49:00 PM\tN12\tN21-0 N23-1\n"
)


def write_behaviours(directory, split="train", content=FIXTURE):
    path = directory / f"{split}_behaviors.tsv"
    path.write_text(content, encoding="utf-8")
    return path


def test_le_journal_est_mis_a_plat_ligne_a_ligne(tmp_path):
    impressions = parse_behaviours(write_behaviours(tmp_path))

    assert impressions.served == 5
    assert impressions.feed_count == 2
    assert list(impressions.items) == [20, 21, 22, 21, 23]
    assert list(impressions.ranks) == [1, 2, 3, 1, 2]
    assert list(impressions.clicks) == [0, 1, 0, 0, 1]
    assert list(impressions.feeds) == [0, 0, 0, 1, 1]
    assert list(impressions.feed_lengths) == [3, 2]
    assert impressions.distinct_items == 4
    assert impressions.click_rate == pytest.approx(0.4)


def test_une_colonne_manquante_est_refusee(tmp_path):
    path = write_behaviours(tmp_path, content="1\tU1\t11/10/2019\tN10\n")
    with pytest.raises(ValueError, match="cinq colonnes"):
        parse_behaviours(path)


def test_le_journal_absent_indique_comment_le_recuperer(tmp_path):
    with pytest.raises(FileNotFoundError, match="fetch_mind"):
        load_split("train", directory=tmp_path)


def test_un_decoupage_inconnu_est_refuse():
    with pytest.raises(ValueError, match="découpage inconnu"):
        split_path("validation")


def test_un_miroir_qui_a_change_est_signale(tmp_path):
    conforms, feeds, digest = verify_split(write_behaviours(tmp_path), "train")

    assert not conforms
    assert feeds == 2 != EXPECTED_SPLITS["train"][0]
    assert len(digest) == 64


def test_le_test_ne_rejette_pas_un_journal_sans_biais_de_position():
    feeds = simulate_feeds([12] * 4000, severity=0.0, rng=np.random.default_rng(0))

    verdict = exchangeability_test(feeds)

    assert abs(verdict.deviation) < 3.0
    assert verdict.exchangeable


def test_le_test_rejette_un_biais_de_position_et_le_rejette_du_bon_cote():
    feeds = simulate_feeds([12] * 4000, severity=1.0, rng=np.random.default_rng(0))

    verdict = exchangeability_test(feeds)

    # Un biais de position concentre les clics en haut : la somme des rangs cliqués tombe
    # sous son espérance, donc l'écart réduit est négatif. Un écart positif dirait autre chose.
    assert verdict.deviation < -10.0
    assert verdict.p_value < 1e-6
    assert not verdict.exchangeable


def test_le_rejet_se_renforce_avec_la_severite():
    deviations = [
        exchangeability_test(
            simulate_feeds([12] * 3000, severity=severity, rng=np.random.default_rng(3))
        ).deviation
        for severity in (0.1, 0.5, 1.0)
    ]

    assert deviations[0] > deviations[1] > deviations[2]


def test_la_severite_detectable_est_petite_et_positive():
    threshold = detectable_severity([12] * 5000, rng=np.random.default_rng(5))

    assert 0.0 < threshold < 0.1


def test_a_longueur_fixee_l_ajustement_naif_retrouve_la_severite():
    feeds = simulate_feeds([20] * 8000, severity=0.8, rng=np.random.default_rng(1))

    assert naive_severity_fit(feeds, maximum_rank=20) == pytest.approx(0.8, abs=0.1)


def test_le_melange_de_longueurs_fabrique_a_lui_seul_une_courbe_de_biais():
    """Le confondant qui a produit les 0,39 apparents de MIND, reconstruit à dessein.

    Aucun biais de position n'est simulé : la position n'entre nulle part dans la probabilité
    de clic. Seules les longueurs diffèrent, et le taux de clic par contenu est plus faible
    dans les fils longs — ce qui suffit à faire décroître la courbe agrégée.
    """
    generator = np.random.default_rng(11)
    lengths, clicks = [], []
    for length, rate in ((5, 0.30), (40, 0.03)):
        for _ in range(3000):
            lengths.append(length)
            clicks.append((generator.random(length) < rate).astype(float))

    lengths = np.asarray(lengths, dtype=np.int64)
    impressions = Impressions(
        items=None,
        ranks=np.concatenate([np.arange(1, length + 1) for length in lengths]),
        clicks=np.concatenate(clicks),
        feeds=np.repeat(np.arange(lengths.size), lengths),
        feed_lengths=lengths,
    )

    assert naive_severity_fit(impressions, maximum_rank=20) > 0.3
    assert naive_severity_fit(impressions, maximum_rank=5, feed_length=5) == pytest.approx(
        0.0, abs=0.15
    )
    assert exchangeability_test(impressions).exchangeable


def test_le_taux_de_clic_par_rang_se_restreint_a_une_longueur():
    generator = np.random.default_rng(2)
    lengths = np.asarray([3, 5, 3], dtype=np.int64)
    impressions = Impressions(
        items=None,
        ranks=np.concatenate([np.arange(1, length + 1) for length in lengths]),
        clicks=(generator.random(int(lengths.sum())) < 0.5).astype(float),
        feeds=np.repeat(np.arange(lengths.size), lengths),
        feed_lengths=lengths,
    )

    rates = click_rate_by_rank(impressions, maximum_rank=5, feed_length=3)

    assert np.isfinite(rates[:3]).all()
    assert np.isnan(rates[3:]).all()


def test_la_couverture_par_contenu_exige_l_identite_des_contenus():
    feeds = simulate_feeds([4] * 10, severity=0.0, rng=np.random.default_rng(0))
    anonymous = Impressions(
        items=None,
        ranks=feeds.ranks,
        clicks=feeds.clicks,
        feeds=feeds.feeds,
        feed_lengths=feeds.feed_lengths,
    )

    with pytest.raises(ValueError, match="identité des contenus"):
        rank_coverage(anonymous)
    with pytest.raises(ValueError, match="identité des contenus"):
        _ = anonymous.distinct_items


def test_la_couverture_compte_les_contenus_vus_a_plusieurs_rangs():
    impressions = Impressions(
        items=np.asarray([1, 2, 2, 1, 1, 2] * 3),
        ranks=np.asarray([1, 2, 1, 2, 1, 2] * 3),
        clicks=np.ones(18),
        feeds=np.repeat(np.arange(9), 2),
        feed_lengths=np.full(9, 2),
    )

    coverage = rank_coverage(impressions, minimum_impressions=3)

    assert coverage.items == 2
    assert coverage.items_with_variation == 2
    assert coverage.median_distinct_ranks == 2.0
    assert coverage.maximum_rank == 2


def test_le_condense_rend_les_memes_chiffres_que_le_journal_brut(tmp_path):
    generator = np.random.default_rng(4)
    lines = []
    for feed in range(400):
        length = int(generator.integers(4, 12))
        served = generator.integers(0, 40, size=length)
        clicked = generator.random(length) < 0.2
        tokens = " ".join(f"N{item}-{int(hit)}" for item, hit in zip(served, clicked, strict=True))
        lines.append(f"{feed}\tU{feed}\t11/10/2019\tN1 N2\t{tokens}")
    write_behaviours(tmp_path, content="\n".join(lines) + "\n")

    digest = build_digest(splits=("train",), directory=tmp_path)
    reloaded = load_digest(save_digest(digest, tmp_path / "digest.npz"))

    raw = parse_behaviours(split_path("train", directory=tmp_path))
    assert exchangeability_test(reloaded.impressions("train")).deviation == pytest.approx(
        exchangeability_test(raw).deviation
    )

    items, ranks, clicks = reloaded.rows("train")
    for minimum in (DIGEST_MINIMUM_IMPRESSIONS, 8):
        from_digest = estimate_position_bias(items, ranks, clicks, minimum_impressions=minimum)
        from_raw = estimate_position_bias(
            raw.items, raw.ranks, raw.clicks, minimum_impressions=minimum
        )
        assert from_digest.severity == pytest.approx(from_raw.severity, nan_ok=True)
        assert from_digest.items_with_variation == from_raw.items_with_variation


def test_un_condense_absent_indique_comment_le_reconstruire(tmp_path):
    with pytest.raises(FileNotFoundError, match="build_mind_digest"):
        load_digest(tmp_path / "absent.npz")


def test_l_ordre_enregistre_dans_mind_est_indiscernable_d_un_melange():
    """Le résultat publié, verrouillé sur le condensé versionné.

    Les deux découpages disent la même chose, et la disent sans ambiguïté : les clics tombent
    exactement là où le hasard les mettrait. Ce test échouerait si le condensé changeait de
    source ou si le test d'échangeabilité perdait son conditionnement au fil.
    """
    digest = load_digest()

    for split in ("train", "dev"):
        verdict = exchangeability_test(digest.impressions(split))
        assert verdict.exchangeable
        assert abs(verdict.deviation) < 0.5
        assert verdict.p_value > 0.5


def test_l_ajustement_naif_sur_mind_fabrique_une_severite_qui_n_existe_pas():
    """Le piège, verrouillé lui aussi : la courbe agrégée décroît alors que rien ne la creuse."""
    impressions = load_digest().impressions("train")

    assert naive_severity_fit(impressions, maximum_rank=20) == pytest.approx(0.388, abs=0.01)
    assert naive_severity_fit(impressions, maximum_rank=20, feed_length=30) == pytest.approx(
        0.0, abs=0.05
    )


def test_l_estimation_de_la_severite_sur_mind_depend_du_seuil_qu_on_lui_donne():
    """Trois seuils, trois sévérités incompatibles, dont une négative — et toutes « sûres ».

    C'est la démonstration que le contrôle d'identifiabilité de
    :func:`ide.offpolicy.estimate_position_bias` ne suffit pas : il accepte un journal dont
    l'ordre ne veut rien dire, et l'estimation qui suit n'estime que du bruit de composition.
    """
    items, ranks, clicks = load_digest().rows("train")

    estimates = {
        minimum: estimate_position_bias(items, ranks, clicks, minimum_impressions=minimum)
        for minimum in (5, 20, 50)
    }

    assert all(estimate.identifiable for estimate in estimates.values())
    assert estimates[5].severity < 0.0 < estimates[50].severity
    assert all(estimate.standard_error < 0.01 for estimate in estimates.values())
