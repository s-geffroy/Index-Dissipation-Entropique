"""Validation du test adverse repris sur des fils ordonnés.

L'optimisation y est exhaustive, ce qui rend les tests exigeants d'une façon utile : un
optimum manqué ne peut pas être imputé au solveur, seulement au modèle.
"""

from __future__ import annotations

import numpy as np
import pytest

from ide.gaming import canonical_positions, position_entropy, rao_entropy
from ide.ranking import (
    MAX_ENUMERATION,
    all_rankings,
    aware_weights,
    blind_weights,
    burial_signature,
    optimal_ranking_under,
    ranking_engagement,
)

VIEWPOINTS = 4
SLOTS = 6
CATALOGUE = canonical_positions(VIEWPOINTS)
REFERENCE = float(np.ptp(CATALOGUE))
# Un lecteur qui préfère nettement le premier point de vue : sans cette préférence, il n'y
# aurait aucun intérêt à enterrer quoi que ce soit.
RELEVANCE = np.array([0.90, 0.45, 0.25, 0.15])


def _entropy(weights: np.ndarray) -> float:
    return position_entropy(weights, CATALOGUE, CATALOGUE)


def _rao(weights: np.ndarray) -> float:
    return rao_entropy(weights, CATALOGUE, REFERENCE)


class TestEnumeration:
    def test_every_feed_is_enumerated_exactly_once(self) -> None:
        rankings = all_rankings(3, 3)

        assert rankings.shape == (27, 3)
        assert len({tuple(row) for row in rankings}) == 27

    def test_an_oversized_enumeration_is_refused_rather_than_approximated(self) -> None:
        with pytest.raises(ValueError, match="limite"):
            all_rankings(40, 4)

    def test_the_limit_is_declared(self) -> None:
        assert MAX_ENUMERATION > 0


class TestWeights:
    def test_the_blind_weights_ignore_the_order(self) -> None:
        forward = blind_weights(np.array([0, 1, 2, 3]), VIEWPOINTS)
        backward = blind_weights(np.array([3, 2, 1, 0]), VIEWPOINTS)

        assert forward == pytest.approx(backward)

    def test_the_aware_weights_do_not(self) -> None:
        forward = aware_weights(np.array([0, 1, 2, 3]), VIEWPOINTS)
        backward = aware_weights(np.array([3, 2, 1, 0]), VIEWPOINTS)

        assert not np.allclose(forward, backward)

    def test_engagement_rewards_putting_the_preferred_viewpoint_first(self) -> None:
        first = ranking_engagement(np.array([0, 3]), RELEVANCE)
        last = ranking_engagement(np.array([3, 0]), RELEVANCE)

        assert first > last


class TestBurial:
    def test_a_buried_feed_shows_a_positive_signature(self) -> None:
        buried = np.array([0, 0, 0, 0, 1, 2])

        assert burial_signature(_entropy, buried, VIEWPOINTS) > 0.1

    def test_a_feed_that_leads_with_diversity_does_not(self) -> None:
        """La signature doit distinguer l'enterrement, non pénaliser tout déséquilibre."""
        buried = np.array([0, 0, 0, 0, 1, 2])
        surfaced = np.array([1, 2, 0, 0, 0, 0])

        assert burial_signature(_entropy, surfaced, VIEWPOINTS) < burial_signature(
            _entropy, buried, VIEWPOINTS
        )

    @pytest.mark.parametrize("measure", [_entropy, _rao], ids=["entropie de position", "rao"])
    def test_a_blind_floor_is_met_by_burying(self, measure) -> None:
        """Le résultat central : sous plancher aveugle, l'optimum relègue la diversité."""
        best = optimal_ranking_under(measure, RELEVANCE, SLOTS, 0.6, rank_aware=False)

        assert best is not None
        assert best.blind >= 0.6 - 1e-9
        assert best.aware < 0.6, "un plancher aveugle laisse passer un fil moins divers qu'affiché"
        assert best.burial > 0.15

    @pytest.mark.parametrize("measure", [_entropy, _rao], ids=["entropie de position", "rao"])
    def test_a_rank_aware_floor_closes_it(self, measure) -> None:
        best = optimal_ranking_under(measure, RELEVANCE, SLOTS, 0.6, rank_aware=True)

        assert best is not None
        assert best.aware >= 0.6 - 1e-9

    def test_closing_the_loophole_costs_engagement(self) -> None:
        """Une norme qui ne coûterait rien de plus ne fermerait rien."""
        blind = optimal_ranking_under(_entropy, RELEVANCE, SLOTS, 0.6, rank_aware=False)
        aware = optimal_ranking_under(_entropy, RELEVANCE, SLOTS, 0.6, rank_aware=True)

        assert aware.engagement < blind.engagement

    def test_an_unreachable_floor_returns_nothing_rather_than_a_default(self) -> None:
        assert optimal_ranking_under(_entropy, RELEVANCE, SLOTS, 1.01, rank_aware=True) is None


class TestOptimality:
    def test_the_optimum_is_exact_and_beats_every_alternative(self) -> None:
        best = optimal_ranking_under(_entropy, RELEVANCE, 4, 0.5, rank_aware=True)

        for assignment in all_rankings(4, VIEWPOINTS):
            if _entropy(aware_weights(assignment, VIEWPOINTS)) < 0.5 - 1e-9:
                continue
            assert ranking_engagement(assignment, RELEVANCE) <= best.engagement + 1e-12

    def test_a_null_floor_lets_the_platform_serve_its_favourite_only(self) -> None:
        best = optimal_ranking_under(_entropy, RELEVANCE, 4, 0.0, rank_aware=True)

        assert set(best.assignment.tolist()) == {0}
