"""Validation du modèle d'Ising : température critique et hystérésis sociale.

Ces tests jouent un rôle particulier dans le projet. L'analogie physique-social
n'est pas falsifiable en tant que telle, mais l'implémentation qui la porte l'est :
un modèle d'Ising 2D correct **doit** retrouver la température critique exacte
d'Onsager. C'est le seul point du dépôt où une prédiction théorique indépendante
de nos hypothèses sociologiques peut valider le code.
"""

from __future__ import annotations

import numpy as np
import pytest

from ide.ising import IsingModel, hysteresis_loop, onsager_critical_temperature


class TestOnsagerTemperature:
    def test_matches_the_exact_solution(self) -> None:
        assert onsager_critical_temperature() == pytest.approx(2.269185, abs=1e-5)

    def test_scales_linearly_with_conformity(self) -> None:
        assert onsager_critical_temperature(3.0) == pytest.approx(
            3.0 * onsager_critical_temperature(1.0)
        )

    def test_non_positive_conformity_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            onsager_critical_temperature(0.0)


class TestIsingModel:
    def test_population_counts_every_individual(self) -> None:
        assert IsingModel(size=8, seed=0).population == 64

    def test_aligned_start_is_a_perfect_consensus(self) -> None:
        assert IsingModel(size=8, initial_state="aligned").magnetisation == 1.0

    def test_random_start_has_no_dominant_opinion(self) -> None:
        model = IsingModel(size=64, initial_state="random", seed=0)

        assert abs(model.magnetisation) < 0.05

    def test_same_seed_gives_identical_trajectories(self) -> None:
        first = IsingModel(size=16, temperature=2.0, seed=42)
        second = IsingModel(size=16, temperature=2.0, seed=42)
        first.run(20)
        second.run(20)

        assert np.array_equal(first.spins, second.spins)

    def test_spins_remain_binary(self) -> None:
        model = IsingModel(size=16, temperature=2.3, field=0.2, seed=1)
        model.run(30)

        assert set(np.unique(model.spins)).issubset({-1, 1})

    def test_zero_temperature_is_rejected(self) -> None:
        """T = 0 est un gel total : la dynamique de Metropolis n'y est pas définie."""
        with pytest.raises(ValueError, match="température"):
            IsingModel(temperature=0.0)

    @pytest.mark.parametrize("bad_state", ["frozen", ""])
    def test_unknown_initial_state_is_rejected(self, bad_state: str) -> None:
        with pytest.raises(ValueError, match="initial_state"):
            IsingModel(initial_state=bad_state)


class TestPhaseTransition:
    def test_cold_society_freezes_into_consensus(self) -> None:
        """Bien en dessous de T_c : le conformisme impose une opinion unique."""
        measures = IsingModel(size=24, temperature=1.5, seed=5, initial_state="aligned").sample(
            sweeps=300, burn_in=300
        )

        assert measures["abs_magnetisation"] > 0.85

    def test_hot_society_never_settles(self) -> None:
        """Bien au-dessus de T_c : l'agitation empêche tout accord stable."""
        measures = IsingModel(size=24, temperature=3.5, seed=5, initial_state="aligned").sample(
            sweeps=300, burn_in=300
        )

        assert measures["abs_magnetisation"] < 0.25

    def test_external_field_breaks_the_symmetry(self) -> None:
        """Un champ médiatique positif aligne la population dans sa direction."""
        measures = IsingModel(
            size=24, temperature=2.6, field=0.4, seed=7, initial_state="random"
        ).sample(sweeps=200, burn_in=200)

        assert measures["magnetisation"] > 0.5

    @pytest.mark.slow
    def test_susceptibility_peak_locates_the_critical_temperature(self) -> None:
        """La susceptibilité culmine au voisinage de la valeur d'Onsager.

        La tolérance est délibérément large : sur un réseau de 24×24, le maximum de
        susceptibilité est décalé vers le haut par les effets de taille finie, et
        ne converge vers 2,269 que dans la limite thermodynamique. Exiger ±0,05
        ici testerait la taille du réseau, pas la justesse du modèle.
        """
        temperatures = np.round(np.arange(2.0, 3.01, 0.1), 2)
        susceptibilities = [
            IsingModel(
                size=24, temperature=float(temperature), seed=3, initial_state="aligned"
            ).sample(sweeps=400, burn_in=400)["susceptibility"]
            for temperature in temperatures
        ]

        peak = float(temperatures[int(np.argmax(susceptibilities))])

        assert peak == pytest.approx(onsager_critical_temperature(), abs=0.25)


class TestHysteresis:
    @pytest.mark.slow
    def test_cold_society_keeps_a_memory_of_the_field(self) -> None:
        """Sous T_c, couper le champ ne ramène pas l'opinion à la neutralité.

        C'est la formalisation numérique de la persistance d'une croyance après
        démenti officiel — et la justification du contre-champ du mémorandum.
        """
        loop = hysteresis_loop(temperature=1.5, steps=13, size=20, sweeps_per_step=40, seed=1)

        assert loop.area > 0.3
        assert loop.remanent_magnetisation > 0.8

    @pytest.mark.slow
    def test_hot_society_forgets_immediately(self) -> None:
        """Au-dessus de T_c, l'agitation dissipe la mémoire : le cycle se referme."""
        loop = hysteresis_loop(temperature=3.5, steps=13, size=20, sweeps_per_step=40, seed=1)

        assert loop.area < 0.15
        assert loop.remanent_magnetisation < 0.15

    @pytest.mark.slow
    def test_memory_shrinks_as_temperature_rises(self) -> None:
        """L'aire du cycle décroît avec la température sociale, puis s'annule.

        Traduction directe de la recommandation d'injection de bruit thermique :
        réchauffer le débat réduit mécaniquement la mémoire des fausses croyances.

        La décroissance n'est testée que jusqu'au voisinage de T_c. Au-delà, l'aire
        est déjà nulle à la précision de la mesure, et son ordre relatif n'est plus
        que du bruit d'échantillonnage — exiger une monotonie stricte dans ce régime
        testerait le générateur aléatoire, pas la physique.
        """
        areas = [
            hysteresis_loop(
                temperature=temperature, steps=11, size=16, sweeps_per_step=30, seed=2
            ).area
            for temperature in (1.2, 1.8, 2.4)
        ]

        assert areas == sorted(areas, reverse=True)
        # Au-delà de la transition, la mémoire a disparu.
        assert areas[-1] < 0.1 * areas[0]

    def test_loop_returns_to_its_starting_field(self) -> None:
        loop = hysteresis_loop(temperature=2.0, steps=7, size=12, sweeps_per_step=10, seed=0)

        assert loop.fields[0] == pytest.approx(-loop.fields[len(loop.fields) // 2])
        assert len(loop.fields) == len(loop.magnetisations) == 14

    @pytest.mark.parametrize(
        ("max_field", "steps"), [(0.0, 11), (1.0, 2)], ids=["champ-nul", "trop-peu-de-paliers"]
    )
    def test_degenerate_parameters_are_rejected(self, max_field: float, steps: int) -> None:
        with pytest.raises(ValueError):
            hysteresis_loop(temperature=2.0, max_field=max_field, steps=steps)
