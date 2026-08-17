"""Validation de la procédure de calibration sur des épisodes synthétiques.

La stratégie de test est la même que pour le reste du dépôt : on construit des séries dont
les taux sont **connus par construction**, et on vérifie que la procédure les retrouve. Une
méthode d'estimation qui ne récupère pas ses propres paramètres sur des données simulées ne
peut rien affirmer sur des données réelles.

Deux propriétés méritent une attention particulière :

* le **rapport** :math:`\\gamma\\alpha/\\lambda` doit être retrouvé exactement sur un
  épisode idéal, puisque c'est la grandeur publiée ;
* l'estimateur à **horizon fixe** doit produire des fenêtres de durée identique, sans quoi
  il ne corrige pas l'artefact pour lequel il a été introduit.
"""

from __future__ import annotations

import numpy as np
import pytest

from ide.calibration import (
    EpisodeCriteria,
    detect_episodes,
    fit_exponential_rate,
    rolling_baseline,
    scan_series,
)


def synthetic_episode(
    rise_rate: float = 0.5,
    decay_rate: float = 0.2,
    rise_days: int = 12,
    decay_days: int = 40,
    baseline: float = 500.0,
    peak_index: int = 200,
    length: int = 500,
) -> np.ndarray:
    """Série plate portant un unique épisode exponentiel de taux connus."""
    series = np.full(length, baseline)
    start = peak_index - rise_days + 1

    rise = baseline * np.exp(rise_rate * np.arange(rise_days))
    series[start : peak_index + 1] += rise
    series[peak_index + 1 : peak_index + 1 + decay_days] += rise[-1] * np.exp(
        -decay_rate * np.arange(1, decay_days + 1)
    )

    return series


class TestExponentialFit:
    @pytest.mark.parametrize("rate", [0.05, 0.3, 1.2, -0.1, -0.7])
    def test_recovers_a_known_rate(self, rate: float) -> None:
        fit = fit_exponential_rate(1_000.0 * np.exp(rate * np.arange(15)))

        assert fit.rate == pytest.approx(rate, abs=1e-9)
        assert fit.r_squared == pytest.approx(1.0)

    def test_timescale_is_the_inverse_rate(self) -> None:
        fit = fit_exponential_rate(1_000.0 * np.exp(-0.25 * np.arange(20)))

        assert fit.timescale == pytest.approx(4.0)
        assert fit.doubling_time == pytest.approx(4.0 * np.log(2.0))

    def test_flat_series_has_no_explanatory_power(self) -> None:
        """Une série logarithmiquement plate ne doit pas obtenir un r² de 1."""
        fit = fit_exponential_rate(np.full(10, 800.0))

        assert fit.rate == pytest.approx(0.0)
        assert fit.r_squared == 0.0
        assert fit.timescale == float("inf")

    def test_noise_degrades_the_fit_quality(self) -> None:
        rng = np.random.default_rng(0)
        clean = 1_000.0 * np.exp(0.3 * np.arange(20))
        noisy = clean * rng.lognormal(0.0, 0.5, size=clean.size)

        assert fit_exponential_rate(noisy).r_squared < fit_exponential_rate(clean).r_squared

    def test_too_few_points_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="3 points"):
            fit_exponential_rate(np.array([100.0, 200.0]))


class TestRollingBaseline:
    def test_median_ignores_an_isolated_spike(self) -> None:
        series = np.full(400, 80.0)
        series[200] = 90_000.0

        assert float(rolling_baseline(series)[200]) == 80.0

    def test_wide_window_survives_a_broad_episode(self) -> None:
        """Le motif de la fenêtre large : un épisode de 50 jours ne doit pas se noyer.

        Avec une fenêtre trimestrielle, un tel épisode occuperait la majorité de ses
        propres points et la médiane absorberait le pic qu'elle sert à mesurer.
        """
        series = synthetic_episode()
        wide = float(rolling_baseline(series, window=181)[200])
        narrow = float(rolling_baseline(series, window=91)[200])

        assert wide == pytest.approx(500.0)
        assert narrow > wide

    def test_edges_are_defined(self) -> None:
        baseline = rolling_baseline(np.full(100, 42.0), window=31)

        assert baseline.shape == (100,)
        assert np.allclose(baseline, 42.0)

    @pytest.mark.parametrize("window", [0, 2])
    def test_degenerate_window_is_rejected(self, window: int) -> None:
        with pytest.raises(ValueError):
            rolling_baseline(np.full(100, 1.0), window=window)


class TestEpisodeDetection:
    def test_recovers_both_rates_and_the_ratio(self) -> None:
        """Le test central : les deux taux et leur rapport, sur un épisode idéal."""
        episodes = detect_episodes(synthetic_episode(rise_rate=0.5, decay_rate=0.2))

        assert len(episodes) == 1
        episode = episodes[0]
        assert episode.rise.rate == pytest.approx(0.5, abs=1e-9)
        assert episode.damping == pytest.approx(0.2, abs=1e-9)
        assert episode.amplification == pytest.approx(0.7, abs=1e-9)
        assert episode.resonance_ratio == pytest.approx(3.5, abs=1e-6)

    @pytest.mark.parametrize(
        ("rise_rate", "decay_rate", "expected"),
        [(0.4, 0.2, 3.0), (0.9, 0.3, 4.0), (0.2, 0.4, 1.5), (1.0, 0.1, 11.0)],
    )
    def test_ratio_formula_holds_across_regimes(
        self, rise_rate: float, decay_rate: float, expected: float
    ) -> None:
        episodes = detect_episodes(
            synthetic_episode(rise_rate=rise_rate, decay_rate=decay_rate)
        )

        assert episodes[0].resonance_ratio == pytest.approx(expected, rel=1e-4)

    def test_peak_position_and_amplitude(self) -> None:
        episode = detect_episodes(synthetic_episode(peak_index=180))[0]

        assert episode.peak_index == 180
        assert episode.baseline == pytest.approx(500.0)
        assert episode.amplitude > 4.0

    def test_flat_series_yields_no_episode(self) -> None:
        assert detect_episodes(np.full(300, 1_000.0)) == []

    def test_pure_noise_yields_no_episode(self) -> None:
        rng = np.random.default_rng(1)
        noise = rng.poisson(1_000.0, size=600).astype(float)

        assert detect_episodes(noise) == []

    def test_two_separated_episodes_are_both_found(self) -> None:
        series = synthetic_episode(peak_index=150, length=700)
        second = synthetic_episode(peak_index=450, length=700) - 500.0
        series = series + second

        episodes = detect_episodes(series)

        assert len(episodes) == 2
        assert [episode.peak_index for episode in episodes] == [150, 450]

    def test_low_traffic_episode_is_rejected_as_counting_noise(self) -> None:
        """Un pic de quelques consultations ne peut pas porter d'inférence.

        L'épisode est de forme parfaitement exponentielle — il passerait tous les autres
        critères. Seul son niveau absolu le disqualifie : à une vingtaine de consultations
        au sommet, le bruit de comptage poissonien atteint 20 %.
        """
        tiny = synthetic_episode(baseline=2.0, rise_rate=0.3, rise_days=8)
        report = scan_series(tiny, criteria=EpisodeCriteria(min_peak_views=200.0))

        assert report.episodes == []
        assert report.rejections["trafic"] > 0
        # Le même épisode, à trafic suffisant, passe.
        assert len(detect_episodes(synthetic_episode(baseline=500.0))) == 1

    def test_series_too_short_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="30 jours"):
            detect_episodes(np.full(10, 100.0))


class TestDetectionReport:
    def test_report_accounts_for_every_candidate(self) -> None:
        report = scan_series(synthetic_episode(), label="synthétique")

        assert report.label == "synthétique"
        assert report.is_exploitable
        assert report.candidates >= len(report.episodes)
        assert report.dominant_rejection is None

    def test_permanent_regime_shift_is_invisible_to_detection(self) -> None:
        """La limite structurelle de la méthode, sous sa forme la plus forte.

        Un changement de régime durable — le comportement typique d'une théorie du complot
        qui s'installe — ne produit **aucun pic candidat** : le niveau de fond glissant
        suit le nouveau palier, et le critère de proéminence n'est jamais franchi.

        La méthode ne se contente donc pas de mal ajuster ces cas, elle ne les voit pas.
        Elle sélectionne contre le phénomène même que la théorie cherche à décrire, ce qui
        biaise le corpus retenu vers les épisodes les moins représentatifs de la classe
        « accusation ».
        """
        series = np.full(600, 200.0)
        series[300:] = 4_000.0  # changement de régime permanent

        report = scan_series(series, label="palier")

        assert report.candidates == 0
        assert report.episodes == []

    def test_sharp_spike_is_rejected_on_window(self) -> None:
        """Un pic d'un seul jour n'est pas ajustable en données quotidiennes."""
        series = np.full(400, 500.0)
        series[200] = 50_000.0

        report = scan_series(series, label="pic-instantané")

        assert report.episodes == []
        assert report.rejections["fenêtre"] > 0


class TestFixedHorizon:
    def test_windows_have_identical_length(self) -> None:
        """La raison d'être de l'horizon fixe : des fenêtres comparables."""
        episode = detect_episodes(synthetic_episode(), criteria=EpisodeCriteria(horizon=7))[0]

        assert episode.rise.n_points == episode.decay.n_points == 8

    def test_recovers_the_known_rates(self) -> None:
        episode = detect_episodes(
            synthetic_episode(rise_rate=0.6, decay_rate=0.15),
            criteria=EpisodeCriteria(horizon=7),
        )[0]

        assert episode.rise.rate == pytest.approx(0.6, abs=1e-6)
        assert episode.damping == pytest.approx(0.15, abs=1e-6)

    def test_short_episode_is_rejected_rather_than_truncated(self) -> None:
        """Un épisode plus bref que l'horizon est écarté, non ajusté sur des zéros."""
        brief = synthetic_episode(rise_days=5, decay_days=6)
        report = scan_series(brief, criteria=EpisodeCriteria(horizon=14))

        assert report.episodes == []
        assert report.rejections["fenêtre"] > 0

    def test_adaptive_estimator_confounds_window_length_with_damping(self) -> None:
        """Démonstration de l'artefact qui a motivé l'estimateur à horizon fixe.

        Deux épisodes de même taux de décroissance réel mais de durées différentes
        reçoivent, avec l'estimateur adaptatif, des λ différents — parce que la fenêtre
        s'étend jusqu'au retour au niveau de fond, donc plus loin dans la queue. À horizon
        fixe, les deux λ coïncident.
        """
        short = synthetic_episode(decay_rate=0.30, decay_days=20)
        long = synthetic_episode(decay_rate=0.30, decay_days=45)

        adaptive = [
            detect_episodes(series)[0].decay.n_points for series in (short, long)
        ]
        fixed = [
            detect_episodes(series, criteria=EpisodeCriteria(horizon=7))[0].decay.n_points
            for series in (short, long)
        ]

        assert adaptive[0] != adaptive[1]
        assert fixed[0] == fixed[1]

    def test_horizon_shorter_than_min_points_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="horizon"):
            EpisodeCriteria(horizon=2)


class TestCriteria:
    @pytest.mark.parametrize(
        "kwargs",
        [
            {"prominence": 1.0},
            {"min_points": 2},
            {"min_r_squared": 1.5},
            {"max_decay": 2},
            {"return_factor": 0.5},
            {"min_peak_views": -1.0},
        ],
    )
    def test_invalid_criteria_are_rejected(self, kwargs: dict[str, float]) -> None:
        with pytest.raises(ValueError):
            EpisodeCriteria(**kwargs)

    def test_stricter_shape_requirement_retains_fewer_episodes(self) -> None:
        rng = np.random.default_rng(3)
        series = synthetic_episode()
        series = series * rng.lognormal(0.0, 0.25, size=series.size)

        lenient = detect_episodes(series, criteria=EpisodeCriteria(min_r_squared=0.5))
        strict = detect_episodes(series, criteria=EpisodeCriteria(min_r_squared=0.99))

        assert len(strict) <= len(lenient)
