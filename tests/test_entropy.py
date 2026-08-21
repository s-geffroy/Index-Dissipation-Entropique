"""Validation des mesures d'entropie et de l'Indice de Diversité Exposée."""

from __future__ import annotations

import numpy as np
import pytest

from ide.entropy import (
    label_diversity_index,
    shannon_entropy,
    shannon_entropy_from_counts,
    von_neumann_entropy,
)


class TestShannonEntropy:
    def test_degenerate_distribution_carries_no_uncertainty(self) -> None:
        """Un accord unanime : l'entropie est nulle, et positivement nulle."""
        entropy = shannon_entropy([1.0, 0.0, 0.0, 0.0])

        assert entropy == 0.0
        # Un zéro négatif se propagerait jusque dans les exports CSV.
        assert np.copysign(1.0, entropy) > 0.0

    @pytest.mark.parametrize("modalities", [2, 4, 8, 16])
    def test_uniform_distribution_reaches_maximal_entropy(self, modalities: int) -> None:
        """L'uniforme sur k modalités vaut exactement log2(k) bits."""
        uniform = np.ones(modalities)

        assert shannon_entropy(uniform) == pytest.approx(np.log2(modalities))

    def test_counts_are_normalised(self) -> None:
        """Effectifs et probabilités doivent donner le même résultat."""
        assert shannon_entropy([3, 1]) == pytest.approx(shannon_entropy([0.75, 0.25]))

    def test_natural_base_matches_conversion(self) -> None:
        in_bits = shannon_entropy([0.3, 0.7], base=2.0)
        in_nats = shannon_entropy([0.3, 0.7], base=np.e)

        assert in_nats == pytest.approx(in_bits * np.log(2.0))

    @pytest.mark.parametrize(
        "invalid",
        [[], [0.0, 0.0], [0.5, -0.1]],
        ids=["vide", "masse-nulle", "probabilité-négative"],
    )
    def test_invalid_distributions_are_rejected(self, invalid: list[float]) -> None:
        with pytest.raises(ValueError):
            shannon_entropy(invalid)

    def test_from_counts_handles_empty_sample(self) -> None:
        """Un fil sans contenu ne porte aucune diversité, sans lever d'exception."""
        assert shannon_entropy_from_counts([]) == 0.0

    def test_from_counts_matches_manual_distribution(self) -> None:
        labels = ["complot", "complot", "complot", "factuel"]

        assert shannon_entropy_from_counts(labels) == pytest.approx(shannon_entropy([3, 1]))


class TestVonNeumannEntropy:
    def test_pure_state_has_zero_entropy(self) -> None:
        """Un état pur : aucune incertitude sur l'état du système."""
        pure = np.array([[1.0, 0.0], [0.0, 0.0]])

        assert von_neumann_entropy(pure) == pytest.approx(0.0, abs=1e-12)

    def test_superposition_is_still_pure(self) -> None:
        """Le point clé de l'analogie : une superposition cohérente reste pure.

        L'entropie ne mesure pas l'existence de plusieurs possibilités, elle mesure
        la **perte de cohérence** entre elles. C'est la décohérence, pas la
        superposition, qui produit de l'entropie.
        """
        amplitudes = np.array([1.0, 1.0]) / np.sqrt(2.0)
        coherent = np.outer(amplitudes, amplitudes.conj())

        assert von_neumann_entropy(coherent) == pytest.approx(0.0, abs=1e-12)

    def test_decohered_mixture_reaches_maximal_entropy(self) -> None:
        """La même superposition, décohérée : les termes croisés s'annulent."""
        decohered = np.eye(2) / 2.0

        assert von_neumann_entropy(decohered) == pytest.approx(np.log(2.0))

    @pytest.mark.parametrize("dimension", [2, 3, 5])
    def test_maximal_mixture_scales_with_dimension(self, dimension: int) -> None:
        maximal = np.eye(dimension) / dimension

        assert von_neumann_entropy(maximal) == pytest.approx(np.log(dimension))

    def test_bit_base_matches_shannon_of_eigenvalues(self) -> None:
        density = np.diag([0.7, 0.3])

        assert von_neumann_entropy(density, base=2.0) == pytest.approx(
            shannon_entropy([0.7, 0.3])
        )

    @pytest.mark.parametrize(
        "invalid",
        [
            np.array([[1.0, 0.0]]),
            np.array([[1.0, 1.0], [0.0, 0.0]]),
            np.array([[0.5, 0.0], [0.0, 0.2]]),
        ],
        ids=["non-carrée", "non-hermitienne", "trace-non-unitaire"],
    )
    def test_invalid_density_matrices_are_rejected(self, invalid: np.ndarray) -> None:
        with pytest.raises(ValueError):
            von_neumann_entropy(invalid)


class TestEntropicDissipationIndex:
    def test_balanced_feed_reaches_the_maximum(self) -> None:
        assert label_diversity_index(["a", "b", "c", "d"], catalogue_size=4) == 1.0

    def test_frozen_bubble_collapses_to_zero(self) -> None:
        """Bulle fermée face à un catalogue de quatre points de vue."""
        index = label_diversity_index(["complot"] * 20, catalogue_size=4)

        assert index == 0.0
        assert np.copysign(1.0, index) > 0.0

    def test_index_stays_within_unit_interval(self) -> None:
        feed = ["a"] * 9 + ["b"] * 3 + ["c"]

        assert 0.0 < label_diversity_index(feed, catalogue_size=4) < 1.0

    def test_index_decreases_as_the_bubble_closes(self) -> None:
        """Monotonie attendue : plus le fil se referme, plus l'index baisse."""
        open_feed = ["a", "b", "c", "d"] * 5
        narrowing = ["a"] * 12 + ["b", "c", "d"]
        closed = ["a"] * 20

        indices = [
            label_diversity_index(feed, catalogue_size=4)
            for feed in (open_feed, narrowing, closed)
        ]

        assert indices == sorted(indices, reverse=True)

    def test_default_catalogue_flatters_a_closed_bubble(self) -> None:
        """Sans catalogue de référence, une bulle fermée obtient un index nul mais
        un fil à deux modalités obtient 1 — d'où l'exigence d'un k imposé par le
        régulateur, documentée dans le mémorandum."""
        assert label_diversity_index(["a", "a", "b", "b"]) == 1.0
        assert label_diversity_index(["a", "a", "b", "b"], catalogue_size=4) == 0.5

    def test_empty_feed_is_index_zero(self) -> None:
        assert label_diversity_index([], catalogue_size=4) == 0.0

    def test_catalogue_smaller_than_observation_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="inférieur"):
            label_diversity_index(["a", "b", "c"], catalogue_size=2)


def test_le_nombre_effectif_de_points_de_vue_est_lineaire_en_diversite():
    """Ce que l'entropie normalisée ne dit pas, et que sa conversion dit (Jost, 2006).

    Un fil parfaitement équilibré sur k points de vue en expose k ; un fil gelé n'en expose
    qu'un. Entre les deux, le nombre effectif se lit sans formation, l'entropie non.
    """
    from ide.entropy import effective_viewpoints

    assert effective_viewpoints(1.0, 4) == pytest.approx(4.0)
    assert effective_viewpoints(0.0, 4) == pytest.approx(1.0)
    assert effective_viewpoints(0.5, 4) == pytest.approx(2.0)
    # le plancher proposé et ce que le fil enterrant expose réellement
    assert effective_viewpoints(0.70, 4) == pytest.approx(2.64, abs=0.01)
    assert effective_viewpoints(0.44, 4) == pytest.approx(1.85, abs=0.01)


def test_un_indice_hors_bornes_ou_un_catalogue_degenere_sont_refuses():
    from ide.entropy import effective_viewpoints

    with pytest.raises(ValueError, match="au moins deux points de vue"):
        effective_viewpoints(0.5, 1)
    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        effective_viewpoints(1.5, 4)

