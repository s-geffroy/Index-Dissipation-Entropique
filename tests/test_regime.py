"""Validation de la détection de changement de régime et de l'identification associée.

Deux résultats distincts sont testés séparément, parce qu'ils ne réussissent pas
également :

* la **détection** — repérer un déplacement durable du niveau d'attention, et le distinguer
  d'un pic comme d'un bruit stationnaire. Elle fonctionne, y compris sur données réelles ;
* l'**identification** — retrouver :math:`\\gamma\\alpha`, :math:`\\lambda` et
  :math:`W_{\\text{sat}}` sur la transition. Elle est exacte sur trajectoire propre et
  devient inexploitable dès que la dispersion résiduelle dépasse quelques pourcents.

Les tapisser ensemble ferait passer une limite de l'estimateur pour une absence de
phénomène. Plusieurs tests figent donc explicitement les **échecs** attendus.
"""

from __future__ import annotations

import numpy as np
import pytest

from ide.regime import (
    RegimeCriteria,
    _integrate,
    _longest_positive_run,
    detect_change_points,
    expected_precision,
    fit_saturated_growth,
    scan_regime_shifts,
    weekly_adjust,
)


def transition(
    ratio: float = 5.0,
    damping: float = 0.2,
    saturation: float = 3_000.0,
    days: int = 120,
) -> np.ndarray:
    """Transition vers un palier, engendrée par l'équation du modèle."""
    grid = np.arange(0.0, float(days))

    return _integrate(ratio * damping, damping, saturation, 0.01 * saturation, grid, "quadratic")


def regime_series(
    ratio: float = 5.0,
    baseline: float = 500.0,
    length: int = 900,
    shift: int = 300,
    noise: float = 0.0,
    seed: int = 1,
) -> np.ndarray:
    """Série complète : ancien régime, transition engendrée par le modèle, palier installé."""
    series = np.full(length, baseline)
    series[shift:] = baseline + transition(ratio=ratio, days=length - shift)

    if noise <= 0.0:
        return series

    return series * np.random.default_rng(seed).lognormal(0.0, noise, size=length)


class TestWeeklyAdjustment:
    def test_removes_pure_weekly_modulation(self) -> None:
        """Le rythme hebdomadaire est un effet systématique, non du bruit."""
        weekday = np.array([1.3, 1.2, 1.1, 1.0, 0.9, 0.7, 0.8])
        raw = 1_000.0 * np.tile(weekday, 40)

        adjusted = weekly_adjust(raw)

        assert adjusted[14:-14].std() < 1.0

    def test_preserves_the_overall_level(self) -> None:
        weekday = np.array([1.4, 1.2, 1.1, 1.0, 0.9, 0.6, 0.8])
        raw = 800.0 * np.tile(weekday, 30)

        assert weekly_adjust(raw).mean() == pytest.approx(raw.mean(), rel=0.05)

    def test_leaves_a_flat_series_untouched(self) -> None:
        flat = np.full(120, 640.0)

        assert np.allclose(weekly_adjust(flat), flat)

    def test_reduces_residual_scatter(self) -> None:
        """C'est la raison d'être de la correction : la dispersion pilote l'incertitude."""
        weekday = np.array([1.25, 1.15, 1.1, 1.0, 0.95, 0.75, 0.8])
        raw = 2_000.0 * np.tile(weekday, 30)

        before = float(np.std(np.log(raw)))
        after = float(np.std(np.log(weekly_adjust(raw))))

        assert after < 0.1 * before

    @pytest.mark.parametrize(
        "invalid", [np.full(10, 100.0), np.array([*np.full(40, 10.0), 0.0])]
    )
    def test_invalid_series_are_rejected(self, invalid: np.ndarray) -> None:
        with pytest.raises(ValueError):
            weekly_adjust(invalid)


class TestChangePointDetection:
    def test_finds_a_single_step(self) -> None:
        series = np.concatenate([np.full(300, 500.0), np.full(300, 4_000.0)])

        assert detect_change_points(series) == [300]

    def test_no_false_positive_on_a_flat_series(self) -> None:
        assert detect_change_points(np.full(600, 500.0)) == []

    def test_no_false_positive_on_stationary_noise(self) -> None:
        """Le critère décisif d'un détecteur : ne pas inventer de rupture."""
        noise = np.random.default_rng(1).lognormal(np.log(800.0), 0.12, 900)

        assert detect_change_points(noise) == []

    def test_finds_two_steps(self) -> None:
        series = np.concatenate([np.full(250, 200.0), np.full(250, 2_000.0), np.full(250, 400.0)])
        found = detect_change_points(series)

        assert len(found) == 2
        assert found[0] == pytest.approx(250, abs=5)
        assert found[1] == pytest.approx(500, abs=5)

    def test_operates_multiplicatively(self) -> None:
        """Un doublement compte autant à mille qu'à cent mille consultations par jour."""
        low = np.concatenate([np.full(300, 100.0), np.full(300, 200.0)])
        high = low * 500.0

        assert detect_change_points(low) == detect_change_points(high)

    def test_respects_the_minimum_segment(self) -> None:
        series = np.concatenate([np.full(300, 500.0), np.full(300, 4_000.0)])

        for point in detect_change_points(series, min_segment=100):
            assert 100 <= point <= 500

    def test_a_high_penalty_suppresses_detection(self) -> None:
        series = np.concatenate([np.full(300, 500.0), np.full(300, 700.0)])

        assert detect_change_points(series, penalty=100.0) == []

    @pytest.mark.parametrize(
        ("kwargs", "series"),
        [
            ({}, np.full(50, 100.0)),
            ({}, np.array([*np.full(300, 1.0), *np.full(300, -1.0)])),
            ({"min_segment": 1}, np.full(600, 100.0)),
        ],
    )
    def test_invalid_input_is_rejected(self, kwargs: dict, series: np.ndarray) -> None:
        with pytest.raises(ValueError):
            detect_change_points(series, **kwargs)


class TestPositiveRun:
    def test_selects_the_longest_run(self) -> None:
        values = np.array([-1.0, 2.0, 3.0, -1.0, 4.0, 5.0, 6.0])

        assert np.array_equal(_longest_positive_run(values), [4.0, 5.0, 6.0])

    def test_empty_when_nothing_is_positive(self) -> None:
        assert _longest_positive_run(np.array([-1.0, 0.0, -2.0])).size == 0


class TestIdentification:
    @pytest.mark.parametrize("ratio", [1.5, 2.0, 5.0, 10.0, 40.0])
    def test_recovers_the_ratio_exactly(self, ratio: float) -> None:
        """Récupération sur trajectoire propre : la condition minimale de crédibilité."""
        fit = fit_saturated_growth(transition(ratio=ratio))

        assert fit.ratio == pytest.approx(ratio, rel=1e-3)
        assert fit.damping == pytest.approx(0.2, rel=1e-3)
        assert fit.is_usable

    def test_recovers_the_saturation_scale(self) -> None:
        fit = fit_saturated_growth(transition(saturation=1_500.0))

        assert fit.saturation == pytest.approx(1_500.0, rel=1e-2)

    def test_recovers_through_a_declared_baseline(self) -> None:
        """L'ajustement porte sur la série observée, niveau de base compris."""
        fit = fit_saturated_growth(500.0 + transition(ratio=5.0), baseline=500.0)

        assert fit.ratio == pytest.approx(5.0, rel=1e-2)

    def test_plateau_matches_the_trajectory_end(self) -> None:
        curve = transition(ratio=5.0, saturation=3_000.0, days=400)
        fit = fit_saturated_growth(curve)

        assert fit.plateau == pytest.approx(float(curve[-1]), rel=0.02)

    def test_scatter_is_negligible_on_a_clean_trajectory(self) -> None:
        assert fit_saturated_growth(transition()).scatter < 1e-6

    def test_scatter_tracks_injected_noise(self) -> None:
        clean = transition()
        noisy = clean * np.random.default_rng(0).lognormal(0.0, 0.12, size=clean.size)

        assert fit_saturated_growth(noisy).scatter == pytest.approx(0.12, abs=0.05)

    def test_excessive_scatter_makes_the_fit_unusable(self) -> None:
        """Au-delà du seuil, les paramètres sont refusés plutôt que rapportés."""
        clean = transition()
        noisy = clean * np.random.default_rng(0).lognormal(0.0, 0.45, size=clean.size)

        assert not fit_saturated_growth(noisy).is_usable

    @pytest.mark.parametrize(
        ("series", "baseline"),
        [
            (np.full(5, 100.0), 0.0),
            (np.array([*np.full(20, 100.0), -1.0]), 0.0),
            (np.full(20, 100.0), 200.0),
        ],
        ids=["trop-court", "valeur-négative", "excédent-négatif"],
    )
    def test_invalid_input_is_rejected(self, series: np.ndarray, baseline: float) -> None:
        with pytest.raises(ValueError):
            fit_saturated_growth(series, baseline=baseline)


class TestSaturationForm:
    def test_logistic_saturation_makes_the_ratio_unidentifiable(self) -> None:
        """Démonstration d'une non-identifiabilité structurelle, et non d'un défaut numérique.

        Sous saturation logistique :math:`\\sigma = 1 - W/W_{\\text{sat}}`, l'équation devient
        :math:`\\dot W = (\\gamma\\alpha - \\lambda)\\,W\\,(1 - W/K)` avec
        :math:`K = W_{\\text{sat}}(1 - \\lambda/\\gamma\\alpha)`. La trajectoire ne dépend donc
        que de **deux** combinaisons des trois paramètres : aucun ajustement, aussi précis
        soit-il, ne peut séparer :math:`\\gamma\\alpha` de :math:`\\lambda`.

        Ce test construit deux triplets de paramètres aux rapports très différents — 5,0 et
        1,67 — et vérifie qu'ils produisent la **même** trajectoire.

        La conséquence porte sur toute la démarche : l'identifiabilité de
        :math:`\\gamma\\alpha/\\lambda` sur un changement de régime n'est pas une propriété des
        données, c'est une hypothèse sur la forme de la saturation.
        """
        grid = np.arange(0.0, 120.0)

        first = _integrate(1.0, 0.2, 3_000.0, 30.0, grid, "logistic")
        # Second triplet de mêmes invariants : A = γα − λ = 0,8 et γα/W_sat = 1/3000.
        second = _integrate(2.0, 1.2, 6_000.0, 30.0, grid, "logistic")

        assert np.allclose(first, second, rtol=1e-3)
        assert 1.0 / 0.2 == pytest.approx(5.0)
        assert 2.0 / 1.2 == pytest.approx(1.667, abs=0.01)

    def test_quadratic_saturation_is_identifiable(self) -> None:
        """La forme du modèle, elle, sépare bien les trois paramètres.

        C'est ce qui rend l'identification possible — et ce qui la rend entièrement
        dépendante de cette hypothèse de forme.
        """
        grid = np.arange(0.0, 160.0)
        first = _integrate(1.0, 0.2, 3_000.0, 30.0, grid, "quadratic")
        second = _integrate(2.0, 1.2, 6_000.0, 30.0, grid, "quadratic")

        assert not np.allclose(first, second, rtol=0.05)
        assert fit_saturated_growth(first).ratio == pytest.approx(5.0, rel=1e-2)

    def test_correct_form_fits_better(self) -> None:
        grid = np.arange(0.0, 120.0)
        curve = _integrate(1.0, 0.2, 3_000.0, 30.0, grid, "quadratic")

        assert (
            fit_saturated_growth(curve, form="quadratic").scatter
            < fit_saturated_growth(curve, form="logistic").scatter
        )

class TestPrecisionTable:
    def test_is_monotone_and_anchored_at_zero(self) -> None:
        assert expected_precision(0.0) == 0.0
        assert expected_precision(0.05) < expected_precision(0.10) < expected_precision(0.25)

    def test_negative_scatter_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            expected_precision(-0.1)

    @pytest.mark.slow
    def test_precision_matches_synthetic_recovery(self) -> None:
        """La table annoncée doit reproduire la récupération qu'elle décrit.

        Sans ce test, la table pourrait dériver silencieusement de la procédure — ce qui
        s'est effectivement produit dans une première version de ce module, où une table de
        biais héritée d'un prototype mal initialisé annonçait une correction qui n'existait
        pas.
        """
        scatter = 0.10
        ratios = []
        for seed in range(12):
            series = regime_series(ratio=5.0, noise=scatter, seed=seed)
            report = scan_regime_shifts(series, adjust_weekly=False)
            ratios.extend(shift.ratio for shift in report.shifts)

        assert len(ratios) >= 8
        values = np.array(ratios)
        observed = (np.percentile(values, 75) - np.percentile(values, 25)) / np.median(values)

        assert observed == pytest.approx(expected_precision(scatter), abs=0.30)


class TestRegimeDetection:
    def test_detects_a_synthetic_regime_shift(self) -> None:
        report = scan_regime_shifts(regime_series(noise=0.05), adjust_weekly=False)

        assert len(report.shifts) == 1
        shift = report.shifts[0]
        assert shift.index == pytest.approx(300, abs=25)
        assert shift.lift > 5.0

    def test_recovers_the_ratio_at_low_noise(self) -> None:
        report = scan_regime_shifts(regime_series(ratio=5.0, noise=0.03), adjust_weekly=False)

        assert report.identified
        assert report.identified[0].ratio == pytest.approx(5.0, rel=0.35)

    def test_rejects_a_peak(self) -> None:
        """Le critère qui sépare les deux méthodes : un pic retombe, un régime tient."""
        series = np.full(900, 500.0)
        series[400:460] = 500.0 + 6_000.0 * np.exp(-0.10 * np.arange(60))
        series *= np.random.default_rng(3).lognormal(0.0, 0.06, 900)

        report = scan_regime_shifts(series, adjust_weekly=False)

        assert report.shifts == []
        assert report.dominant_rejection in ("élévation", "maintien")

    def test_no_false_positive_on_stationary_noise(self) -> None:
        noise = np.random.default_rng(1).lognormal(np.log(800.0), 0.12, 900)
        report = scan_regime_shifts(noise, adjust_weekly=False)

        assert report.candidates == 0
        assert report.shifts == []

    def test_a_gradual_ramp_is_reported_once(self) -> None:
        """Une segmentation en moyenne découpe une montée graduelle en escalier.

        Sans déduplication, la même transition serait ajustée deux ou trois fois, avec des
        fenêtres décalées produisant des rapports incohérents.
        """
        report = scan_regime_shifts(regime_series(ratio=2.5, noise=0.05), adjust_weekly=False)

        assert len(report.shifts) == 1
        assert report.rejections["doublon"] >= 1

    def test_article_creation_is_not_a_regime_shift(self) -> None:
        """Il faut un ancien régime pour qu'il y ait changement de régime.

        Une série passant de deux à trois cents consultations par jour décrit un article
        qui vient d'être rédigé. Sans garde-fou, ces créations produisent des élévations de
        plusieurs centaines qui écrasent toute comparaison.
        """
        series = np.full(900, 2.0)
        series[300:] = 300.0
        series *= np.random.default_rng(5).lognormal(0.0, 0.05, 900)

        report = scan_regime_shifts(series, adjust_weekly=False)

        assert report.shifts == []
        assert report.rejections["niveau"] >= 1

    def test_detection_survives_when_identification_fails(self) -> None:
        """Le résultat central du module : les deux réussites sont dissociées.

        À forte dispersion — le régime des séries réelles — le changement de régime reste
        détecté, avec sa date et son ampleur, tandis que les paramètres sont refusés. Les
        confondre ferait passer une limite de l'estimateur pour une absence de phénomène.
        """
        report = scan_regime_shifts(regime_series(noise=0.30, seed=4), adjust_weekly=False)

        assert report.shifts, "le changement de niveau doit rester détecté"
        assert report.identified == [], "les paramètres doivent être refusés"
        assert report.rejections["ajustement"] >= 1
        assert report.shifts[0].lift > 3.0

    def test_uncertainty_grows_with_scatter(self) -> None:
        quiet = scan_regime_shifts(regime_series(noise=0.03), adjust_weekly=False).shifts[0]
        noisy = scan_regime_shifts(regime_series(noise=0.15, seed=2), adjust_weekly=False).shifts[0]

        assert noisy.relative_spread > quiet.relative_spread

    def test_report_accounts_for_every_candidate(self) -> None:
        report = scan_regime_shifts(regime_series(noise=0.05), label="synthétique",
                                    adjust_weekly=False)

        assert report.label == "synthétique"
        assert report.candidates >= len(report.shifts)
        assert report.is_exploitable

    def test_series_too_short_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="jours"):
            scan_regime_shifts(np.full(100, 500.0))

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"min_lift": 1.0},
            {"min_level": -1.0},
            {"return_tolerance": 1.5},
            {"transition": 5},
            {"lead": -1},
        ],
    )
    def test_invalid_criteria_are_rejected(self, kwargs: dict[str, float]) -> None:
        with pytest.raises(ValueError):
            RegimeCriteria(**kwargs)
