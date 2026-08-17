"""Validation de la cinétique de résonance algorithmique.

Le critère :math:`\\gamma\\alpha > \\lambda` est la recommandation la plus
directement opérationnelle du mémorandum : un régulateur peut, en principe,
mesurer un gain algorithmique et un taux d'amortissement, et interdire les
configurations où le premier dépasse le second. Ces tests vérifient que le critère
sépare effectivement les deux régimes, et que la saturation ajoutée au modèle du
fil borne bien le phénomène.
"""

from __future__ import annotations

import numpy as np
import pytest

from ide.resonance import ResonanceParameters, simulate_resonance


class TestInstabilityCriterion:
    def test_moderate_gain_is_stable(self) -> None:
        parameters = ResonanceParameters(damping=1.0, gain=1.0, emotion=0.5)

        assert parameters.amplification == pytest.approx(0.5)
        assert not parameters.is_unstable

    def test_excessive_gain_is_unstable(self) -> None:
        parameters = ResonanceParameters(damping=0.2, gain=3.0, emotion=0.5)

        assert parameters.is_unstable

    def test_emotional_charge_alone_can_trigger_instability(self) -> None:
        """À gain algorithmique constant, un contenu plus émotionnel franchit le seuil.

        C'est le mécanisme central : la plateforme n'a pas besoin de favoriser
        explicitement la désinformation, il suffit que son gain soit uniforme et que
        la fausse information soit plus émotionnelle qu'un fait vérifié.
        """
        factual = ResonanceParameters(damping=1.0, gain=1.5, emotion=0.4)
        outrageous = ResonanceParameters(damping=1.0, gain=1.5, emotion=0.9)

        assert not factual.is_unstable
        assert outrageous.is_unstable

    def test_effective_damping_is_negative_when_unstable(self) -> None:
        parameters = ResonanceParameters(damping=0.2, gain=3.0, emotion=0.5, saturation=None)

        assert float(parameters.effective_damping(0.0)) < 0.0

    def test_saturation_restores_positive_damping_at_high_visibility(self) -> None:
        """L'attention étant finie, l'amplification s'éteint aux fortes visibilités."""
        parameters = ResonanceParameters(damping=0.2, gain=3.0, emotion=0.5, saturation=1.0)

        assert float(parameters.effective_damping(0.0)) < 0.0
        assert float(parameters.effective_damping(50.0)) > 0.0

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"damping": -0.1},
            {"gain": -1.0},
            {"frequency": 0.0},
            {"saturation": 0.0},
            {"noise": -0.5},
        ],
    )
    def test_invalid_parameters_are_rejected(self, kwargs: dict[str, float]) -> None:
        with pytest.raises(ValueError):
            ResonanceParameters(**kwargs)


class TestSimulation:
    def test_stable_content_fades_away(self) -> None:
        solution = simulate_resonance(
            ResonanceParameters(damping=1.0, gain=0.5, emotion=0.5), total_time=40.0
        )

        assert not solution.diverged
        assert solution.late_amplitude() < 0.01

    def test_unbounded_model_diverges(self) -> None:
        """Sans saturation — le modèle du fil — la visibilité explose sans limite.

        Le comportement est mathématiquement conforme à la solution
        :math:`V(t) \\propto e^{(\\gamma\\alpha - \\lambda)t}`, et c'est précisément
        ce qui rend le modèle non exploitable : une visibilité infinie n'existe pas.
        """
        solution = simulate_resonance(
            ResonanceParameters(damping=0.2, gain=3.0, emotion=0.5, saturation=None),
            total_time=120.0,
        )

        assert solution.diverged
        assert solution.peak_visibility > 1e6

    def test_saturated_model_settles_into_a_limit_cycle(self) -> None:
        """Avec attention finie : oscillation permanente d'amplitude bornée."""
        solution = simulate_resonance(
            ResonanceParameters(damping=0.2, gain=3.0, emotion=0.5, saturation=1.0),
            total_time=120.0,
        )

        assert not solution.diverged
        assert np.all(np.isfinite(solution.visibility))
        # Le contenu ne disparaît pas — il devient un sujet récurrent.
        assert solution.late_amplitude() > 0.5

    def test_limit_cycle_amplitude_is_stationary(self) -> None:
        """Un cycle limite se reconnaît à une amplitude qui cesse de croître."""
        solution = simulate_resonance(
            ResonanceParameters(damping=0.2, gain=2.0, emotion=0.5, saturation=1.0),
            total_time=200.0,
        )

        midpoint = len(solution.visibility) // 2
        first_half = float(np.max(np.abs(solution.visibility[midpoint // 2 : midpoint])))
        second_half = float(np.max(np.abs(solution.visibility[midpoint:])))

        assert second_half == pytest.approx(first_half, rel=0.15)

    def test_larger_gain_produces_a_larger_cycle(self) -> None:
        """Réduire le gain algorithmique réduit l'amplitude du phénomène.

        C'est l'effet attendu de la recommandation d'audit : le régulateur n'a pas
        besoin de supprimer le contenu, il suffit qu'il contraigne γ.
        """
        amplitudes = [
            simulate_resonance(
                ResonanceParameters(damping=0.2, gain=gain, emotion=0.5, saturation=1.0),
                total_time=150.0,
            ).late_amplitude()
            for gain in (1.0, 2.0, 4.0)
        ]

        assert amplitudes == sorted(amplitudes)

    def test_noise_is_reproducible_from_a_seed(self) -> None:
        parameters = ResonanceParameters(damping=1.0, gain=0.5, emotion=0.5, noise=0.1)
        trajectories = [
            simulate_resonance(parameters, total_time=10.0, seed=99).visibility for _ in range(2)
        ]

        assert np.array_equal(trajectories[0], trajectories[1])

    def test_different_seeds_give_different_noise(self) -> None:
        parameters = ResonanceParameters(damping=1.0, gain=0.5, emotion=0.5, noise=0.1)
        first = simulate_resonance(parameters, total_time=10.0, seed=1).visibility
        second = simulate_resonance(parameters, total_time=10.0, seed=2).visibility

        assert not np.array_equal(first, second)

    @pytest.mark.parametrize(
        ("total_time", "time_step"), [(0.0, 1e-3), (10.0, 0.0), (1.0, 2.0)]
    )
    def test_invalid_integration_windows_are_rejected(
        self, total_time: float, time_step: float
    ) -> None:
        with pytest.raises(ValueError):
            simulate_resonance(ResonanceParameters(), total_time=total_time, time_step=time_step)

    def test_late_amplitude_fraction_is_validated(self) -> None:
        solution = simulate_resonance(ResonanceParameters(), total_time=5.0)

        with pytest.raises(ValueError, match="fraction"):
            solution.late_amplitude(fraction=0.0)
