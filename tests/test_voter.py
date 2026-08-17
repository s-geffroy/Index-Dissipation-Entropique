"""Validation du Voter Model : lois d'échelle et effet du champ de désinformation.

Ces tests portent l'argument corrigé du point 12 de l'audit. Le fil de travail
soutenait que la connectivité globale des réseaux sociaux empêche le consensus ;
les lois d'échelle du Voter Model montrent l'inverse — elle l'accélère. Ce qui
fragmente une société, c'est la direction imposée par le biais, pas la densité des
liens.
"""

from __future__ import annotations

import numpy as np
import pytest

from ide.voter import VoterModel, consensus_time_scaling


class TestVoterModel:
    def test_initial_fraction_is_respected(self) -> None:
        model = VoterModel(population=100, initial_fraction=0.3, seed=0)

        assert model.fraction == pytest.approx(0.3)

    def test_unanimity_is_absorbing(self) -> None:
        """Une population unanime ne peut plus changer d'avis : personne à imiter."""
        model = VoterModel(population=50, initial_fraction=1.0, seed=0)
        model.sweep()

        assert model.fraction == 1.0
        assert model.has_consensus

    @pytest.mark.parametrize("topology", ["mean_field", "ring"])
    def test_consensus_is_eventually_reached(self, topology: str) -> None:
        model = VoterModel(population=60, topology=topology, seed=3)
        model.run_until_consensus(max_sweeps=50_000)

        assert model.has_consensus

    def test_same_seed_gives_identical_consensus_time(self) -> None:
        times = [
            VoterModel(population=80, seed=17).run_until_consensus(max_sweeps=20_000)
            for _ in range(2)
        ]

        assert times[0] == times[1]

    def test_fraction_stays_within_bounds(self) -> None:
        history = VoterModel(population=50, bias=0.05, seed=1).trajectory(sweeps=40)

        assert np.all((history >= 0.0) & (history <= 1.0))

    @pytest.mark.parametrize(
        ("population", "bias", "topology"),
        [(1, 0.0, "mean_field"), (50, 1.5, "mean_field"), (50, 0.0, "small_world")],
        ids=["population-trop-petite", "biais-hors-bornes", "topologie-inconnue"],
    )
    def test_invalid_parameters_are_rejected(
        self, population: int, bias: float, topology: str
    ) -> None:
        with pytest.raises(ValueError):
            VoterModel(population=population, bias=bias, topology=topology)


class TestDisinformationBias:
    def test_bias_drives_the_population_towards_the_field(self) -> None:
        """Un biais positif force la convergence vers l'opinion qu'il pousse."""
        converged = []
        for seed in range(6):
            model = VoterModel(population=80, bias=0.05, seed=seed)
            model.run_until_consensus(max_sweeps=5_000)
            converged.append(model.fraction)

        # Sans biais, l'issue serait équiprobable entre 0 et 1 ; avec biais, elle
        # est systématiquement 1.
        assert all(fraction == 1.0 for fraction in converged)

    def test_bias_accelerates_consensus(self) -> None:
        """La dérive forcée atteint l'unanimité plus vite qu'une marche symétrique."""
        unbiased = np.mean(
            [
                VoterModel(population=120, seed=seed).run_until_consensus(max_sweeps=20_000)
                for seed in range(6)
            ]
        )
        biased = np.mean(
            [
                VoterModel(population=120, bias=0.1, seed=seed).run_until_consensus(
                    max_sweeps=20_000
                )
                for seed in range(6)
            ]
        )

        assert biased < unbiased

    def test_maximal_bias_never_produces_negative_probabilities(self) -> None:
        """Contrôle de la correction apportée aux transitions asymétriques.

        La formulation du fil, ``P(x → x - 1/N) = x(1-x) - hx``, devient négative
        dès que ``h > 1 - x``. La forme retenue reste une probabilité valide sur
        tout l'intervalle de biais, ce que vérifie ici l'exécution à ``h = 1``.
        """
        model = VoterModel(population=40, bias=1.0, seed=0)
        model.run_until_consensus(max_sweeps=1_000)

        assert model.fraction == 1.0


class TestConsensusScaling:
    @pytest.mark.slow
    def test_mean_field_consensus_is_linear_in_population(self) -> None:
        """Réseau globalisé : ⟨τ⟩ ∝ N."""
        scaling = consensus_time_scaling(
            populations=(32, 64, 128), topology="mean_field", repeats=8, seed=0
        )

        assert scaling.exponent == pytest.approx(1.0, abs=0.35)

    @pytest.mark.slow
    def test_ring_consensus_is_quadratic_in_population(self) -> None:
        """Voisinage local : ⟨τ⟩ ∝ N², bien plus lent."""
        scaling = consensus_time_scaling(
            populations=(32, 64, 128), topology="ring", repeats=8, seed=0
        )

        assert scaling.exponent == pytest.approx(2.0, abs=0.45)

    @pytest.mark.slow
    def test_global_connectivity_accelerates_consensus(self) -> None:
        """Le point 12 de l'audit, vérifié numériquement.

        À taille égale, un réseau globalisé converge **plus vite** qu'un voisinage
        géographique. La topologie « petit monde » n'empêche donc pas le consensus :
        elle le précipite. Attribuer la fragmentation à la connectivité seule est
        une erreur d'analyse — c'est le biais directionnel qui fragmente.
        """
        global_network = consensus_time_scaling(
            populations=(64, 128), topology="mean_field", repeats=8, seed=1
        )
        local_network = consensus_time_scaling(
            populations=(64, 128), topology="ring", repeats=8, seed=1
        )

        assert np.all(global_network.mean_times < local_network.mean_times)

    def test_a_single_population_size_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="deux tailles"):
            consensus_time_scaling(populations=(64,))
