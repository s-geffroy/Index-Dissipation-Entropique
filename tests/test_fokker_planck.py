"""Validation du solveur de Fokker-Planck et du paysage de l'opinion publique.

Deux exigences distinctes sont vérifiées ici :

* la **correction numérique** — masse de probabilité conservée, densité positive,
  convergence vers la solution stationnaire exacte du problème posé ;
* la **pertinence physique** — existence d'une transition de phase à
  :math:`T_c = J`, rupture de symétrie sous champ, et rigidification de la société
  quand :math:`N` croît.

La seconde famille de tests est celle qui porte les corrections des points 3 et 4
de l'audit.
"""

from __future__ import annotations

import numpy as np
import pytest

from ide.fokker_planck import (
    FokkerPlanckSolver,
    diffusion_term,
    drift_term,
    mean_field_critical_temperature,
    mean_field_free_energy,
    stationary_distribution,
    zero_flux_stationary,
)


def _local_maxima(grid: np.ndarray, density: np.ndarray) -> np.ndarray:
    interior = density[1:-1]

    return grid[1:-1][(interior > density[:-2]) & (interior > density[2:])]


class TestDriftAndDiffusion:
    def test_moderation_is_a_fixed_point_without_field(self) -> None:
        assert float(drift_term(0.0)) == 0.0

    def test_entropic_recall_bounds_the_dynamics(self) -> None:
        """Correction du point 4 : la dérive du fil, Jx + H, ne borne rien.

        Aux opinions extrêmes, le rappel entropique -T·artanh(x) doit dominer le
        conformisme Jx et ramener vers l'intérieur, faute de quoi la dynamique
        s'échappe de l'intervalle [-1, 1].
        """
        near_unanimity = 0.99

        assert float(drift_term(near_unanimity, coupling=1.0, temperature=1.0)) < 0.0

    def test_conformity_amplifies_the_majority_near_the_centre(self) -> None:
        """En revanche, à faible polarisation et basse température, le conformisme
        l'emporte : c'est l'effet d'entraînement."""
        assert float(drift_term(0.2, coupling=1.0, temperature=0.3)) > 0.0

    def test_media_field_shifts_the_fixed_point(self) -> None:
        assert float(drift_term(0.0, field=0.3)) == pytest.approx(0.3)

    def test_diffusion_vanishes_at_unanimity(self) -> None:
        """Plus de désaccord à échantillonner : le bruit s'éteint."""
        assert float(diffusion_term(1.0)) == 0.0
        assert float(diffusion_term(-1.0)) == 0.0

    def test_diffusion_decreases_with_population(self) -> None:
        """Le point 3 de l'audit, sous sa forme la plus directe.

        Une grande population n'est pas plus bruyante : les fluctuations de sa
        moyenne sont **plus faibles**. La « pompe à entropie » agit sur l'entropie
        de configuration totale, pas sur le bruit de la variable macroscopique.
        """
        small = float(diffusion_term(0.0, population=100))
        large = float(diffusion_term(0.0, population=10_000))

        assert large < small
        assert large == pytest.approx(small / 100.0)

    @pytest.mark.parametrize("population", [0, -5])
    def test_invalid_population_is_rejected(self, population: int) -> None:
        with pytest.raises(ValueError):
            diffusion_term(0.0, population=population)


class TestFreeEnergy:
    def test_symmetric_without_field(self) -> None:
        energies = mean_field_free_energy(np.array([-0.7, 0.7]), temperature=0.5)

        assert energies[0] == pytest.approx(energies[1])

    def test_field_favours_its_own_direction(self) -> None:
        """Un champ positif rend l'opinion +x moins coûteuse que -x."""
        energies = mean_field_free_energy(np.array([-0.7, 0.7]), field=0.3, temperature=0.5)

        assert energies[1] < energies[0]

    def test_finite_at_unanimity(self) -> None:
        """La limite 0·ln 0 doit être prise, pas produire un NaN."""
        assert np.all(np.isfinite(mean_field_free_energy(np.array([-1.0, 1.0]))))

    def test_cold_society_has_two_minima(self) -> None:
        grid = np.linspace(-0.99, 0.99, 601)
        energies = mean_field_free_energy(grid, temperature=0.5)
        minima = _local_maxima(grid, -energies)

        assert len(minima) == 2
        assert minima[0] == pytest.approx(-minima[1], abs=1e-6)

    def test_hot_society_has_a_single_minimum_at_moderation(self) -> None:
        grid = np.linspace(-0.99, 0.99, 601)
        energies = mean_field_free_energy(grid, temperature=2.0)
        minima = _local_maxima(grid, -energies)

        assert len(minima) == 1
        assert minima[0] == pytest.approx(0.0, abs=0.01)


class TestStationaryDistribution:
    def test_critical_temperature_is_the_coupling(self) -> None:
        assert mean_field_critical_temperature(1.0) == 1.0

    def test_fluid_society_peaks_on_moderation(self) -> None:
        """Scénario A : T > T_c, un pic unique centré — débat fluide."""
        grid = np.linspace(-0.98, 0.98, 401)
        density = stationary_distribution(grid, temperature=2.0, population=200)

        assert len(_local_maxima(grid, density)) == 1
        assert grid[int(np.argmax(density))] == pytest.approx(0.0, abs=0.01)

    def test_polarised_society_splits_in_two(self) -> None:
        """Scénario B : T < T_c et H = 0, deux pics symétriques."""
        grid = np.linspace(-0.98, 0.98, 401)
        density = stationary_distribution(grid, temperature=0.7, population=200)
        peaks = _local_maxima(grid, density)

        assert len(peaks) == 2
        assert peaks[0] == pytest.approx(-peaks[1], abs=0.01)

    def test_field_makes_the_polarisation_asymmetric(self) -> None:
        """Faux consensus : le pic du côté de la désinformation écrase l'autre."""
        grid = np.linspace(-0.98, 0.98, 401)
        density = stationary_distribution(grid, temperature=0.7, field=0.1, population=200)

        assert grid[int(np.argmax(density))] > 0.0
        assert float(np.trapezoid(grid * density, grid)) > 0.0

    def test_moderation_collapses_when_population_grows(self) -> None:
        """La probabilité de trouver un modéré s'effondre avec la taille du système."""
        grid = np.linspace(-0.98, 0.98, 401)
        centre = len(grid) // 2

        densities = [
            stationary_distribution(grid, temperature=0.7, population=population)[centre]
            for population in (50, 200, 800)
        ]

        assert densities == sorted(densities, reverse=True)

    def test_normalisation(self) -> None:
        grid = np.linspace(-0.98, 0.98, 401)
        density = stationary_distribution(grid, temperature=0.7, population=500)

        assert float(np.trapezoid(density, grid)) == pytest.approx(1.0)

    def test_large_population_does_not_overflow(self) -> None:
        """Le décalage par le minimum d'énergie libre doit rendre le calcul robuste."""
        grid = np.linspace(-0.98, 0.98, 401)
        density = stationary_distribution(grid, temperature=0.5, population=100_000)

        assert np.all(np.isfinite(density))

    def test_degenerate_grid_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="grille"):
            stationary_distribution(np.array([0.0, 0.5]))


class TestSolver:
    def test_probability_mass_is_conserved_exactly(self) -> None:
        """Le schéma en volumes finis à flux nul aux bords ne perd pas de masse."""
        solution = FokkerPlanckSolver(points=401, temperature=0.8, population=400).solve(
            total_time=60.0
        )

        assert solution.mass_drift < 1e-9

    def test_density_stays_positive(self) -> None:
        """Propriété du décentrement amont : aucune densité négative ne peut naître."""
        solution = FokkerPlanckSolver(points=401, temperature=0.8, population=400).solve(
            total_time=60.0
        )

        assert np.all(solution.density >= -1e-12)

    def test_converges_towards_the_exact_stationary_state(self) -> None:
        """Le régime asymptotique doit rejoindre la solution exacte à flux nul."""
        solver = FokkerPlanckSolver(points=401, temperature=0.8, population=400)
        numerical = solver.solve(total_time=200.0).density
        numerical = numerical / solver.mass(numerical)
        exact = zero_flux_stationary(solver.grid, solver.drift, solver.diffusion)

        distance = float(np.sum(np.abs(numerical - exact)) * (solver.grid[1] - solver.grid[0]))

        assert distance < 0.1

    def test_cold_society_becomes_bimodal(self) -> None:
        solution = FokkerPlanckSolver(points=401, temperature=0.8, population=400).solve(
            total_time=60.0
        )

        assert solution.is_bimodal
        assert len(solution.modes) == 2

    def test_hot_society_stays_unimodal(self) -> None:
        solution = FokkerPlanckSolver(points=401, temperature=2.0, population=400).solve(
            total_time=60.0
        )

        assert not solution.is_bimodal
        assert solution.modes[0] == pytest.approx(0.0, abs=0.02)

    def test_field_pulls_the_whole_distribution(self) -> None:
        """Sous T_c, un champ suffisant supprime le pic opposé : consensus forcé."""
        solution = FokkerPlanckSolver(
            points=401, temperature=0.8, field=0.15, population=400
        ).solve(total_time=60.0)

        assert solution.mean_opinion() > 0.5
        assert len(solution.modes) == 1

    def test_stable_time_step_is_positive_and_finite(self) -> None:
        solver = FokkerPlanckSolver(points=201, temperature=1.0, population=1_000)
        step = solver.stable_time_step()

        assert 0.0 < step < np.inf

    def test_history_records_the_requested_snapshots(self) -> None:
        solution = FokkerPlanckSolver(points=101, temperature=1.0).solve(
            total_time=10.0, snapshots=6
        )

        assert solution.history.shape[0] == len(solution.times)
        assert solution.times[0] == 0.0
        assert solution.times[-1] == pytest.approx(10.0)

    @pytest.mark.parametrize(
        ("points", "domain_limit"),
        [(5, 0.98), (101, 1.5)],
        ids=["grille-trop-fine", "domaine-invalide"],
    )
    def test_invalid_configuration_is_rejected(self, points: int, domain_limit: float) -> None:
        with pytest.raises(ValueError):
            FokkerPlanckSolver(points=points, domain_limit=domain_limit)

    def test_mismatched_initial_condition_is_rejected(self) -> None:
        solver = FokkerPlanckSolver(points=101)

        with pytest.raises(ValueError, match="forme de la grille"):
            solver.solve(total_time=1.0, density=np.ones(50))
