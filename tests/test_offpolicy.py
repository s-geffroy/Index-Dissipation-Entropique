"""Validation des estimateurs contrefactuels.

Un estimateur sans biais se vérifie, il ne se déclare pas : chaque test compare l'estimation
à une valeur **vraie** que seule la simulation rend accessible. C'est aussi l'argument du
module — sur données réelles, cette valeur est précisément celle qu'on cherche et qu'on n'a
pas.
"""

from __future__ import annotations

import numpy as np
import pytest

from ide.offpolicy import (
    clipped_ips,
    doubly_robust,
    effective_sample_size,
    estimate_position_bias,
    importance_weights,
    ips,
    naive,
    naive_replay,
    position_bias,
    rank_propensities,
    simulate_logged_feedback,
    simulate_ranked_feedback,
    snips,
    value_under_policy,
)

ITEMS = 12
IMPRESSIONS = 120_000


def _setup(seed: int = 3, severity: float = 1.0, diversity_weight: float = 0.6):
    """Une plateforme qui classe par pertinence, et un réordonnancement qui la contrarie."""
    rng = np.random.default_rng(seed)
    relevance = rng.uniform(0.05, 0.95, ITEMS)
    diversity = rng.uniform(0.0, 1.0, ITEMS)

    logged_ranks = np.argsort(np.argsort(-relevance)) + 1
    score = (1.0 - diversity_weight) * relevance + diversity_weight * diversity
    target_ranks = np.argsort(np.argsort(-score)) + 1

    logged = rank_propensities(logged_ranks, severity)
    target = rank_propensities(target_ranks, severity)
    examined, clicks = simulate_logged_feedback(relevance, logged, IMPRESSIONS, rng)

    return relevance, logged, target, examined, clicks


class TestPositionBias:
    def test_attention_decreases_with_rank(self) -> None:
        exposure = position_bias(np.array([1, 2, 5, 10]))

        assert exposure[0] == pytest.approx(1.0)
        assert np.all(np.diff(exposure) < 0)

    def test_a_null_severity_removes_the_bias(self) -> None:
        assert position_bias(np.array([1, 4, 9]), severity=0.0) == pytest.approx(1.0)

    def test_ranks_start_at_one(self) -> None:
        with pytest.raises(ValueError, match="rangs"):
            position_bias(np.array([0, 1]))

    def test_propensities_form_a_policy(self) -> None:
        assert rank_propensities(np.arange(1, 6)).sum() == pytest.approx(1.0)


class TestImportanceWeights:
    def test_identical_policies_give_unit_weights(self) -> None:
        policy = np.array([0.5, 0.3, 0.2])

        assert importance_weights(policy, policy) == pytest.approx(1.0)

    def test_a_coverage_failure_is_refused_rather_than_worked_around(self) -> None:
        """Publier un chiffre là où les données ne contiennent rien serait pire que refuser."""
        with pytest.raises(ValueError, match="recouvrement"):
            importance_weights(np.array([0.5, 0.5]), np.array([1.0, 0.0]))

    def test_an_unused_action_does_not_trigger_a_coverage_failure(self) -> None:
        assert importance_weights(np.array([1.0, 0.0]), np.array([1.0, 0.0]))[1] == 0.0


class TestUnbiasedness:
    def test_ips_recovers_the_true_value(self) -> None:
        relevance, logged, target, examined, clicks = _setup()
        truth = value_under_policy(relevance, target)

        estimate = ips(clicks, target[examined], logged[examined])

        assert estimate == pytest.approx(truth, rel=0.03)

    def test_snips_recovers_the_true_value(self) -> None:
        relevance, logged, target, examined, clicks = _setup()
        truth = value_under_policy(relevance, target)

        assert snips(clicks, target[examined], logged[examined]) == pytest.approx(truth, rel=0.03)

    def test_the_naive_average_measures_the_logging_policy_instead(self) -> None:
        """Il n'est pas imprécis : il répond à une autre question."""
        relevance, logged, target, examined, clicks = _setup()

        assert naive(clicks) == pytest.approx(value_under_policy(relevance, logged), rel=0.03)
        assert naive(clicks) != pytest.approx(value_under_policy(relevance, target), rel=0.03)

    def test_doubly_robust_survives_a_wrong_reward_model(self) -> None:
        """Sa robustesse est double en un sens précis : il suffit que l'un des deux tienne."""
        relevance, logged, target, examined, clicks = _setup()
        truth = value_under_policy(relevance, target)
        wrong_model = np.full(ITEMS, 0.5)

        estimate = doubly_robust(
            clicks,
            target[examined],
            logged[examined],
            wrong_model[examined],
            np.full(clicks.size, float(target @ wrong_model)),
        )

        assert estimate == pytest.approx(truth, rel=0.03)

    def test_clipping_trades_bias_for_variance_and_says_so(self) -> None:
        relevance, logged, target, examined, clicks = _setup()
        truth = value_under_policy(relevance, target)

        tight = clipped_ips(clicks, target[examined], logged[examined], cap=1.5)
        loose = clipped_ips(clicks, target[examined], logged[examined], cap=1e6)

        assert abs(tight - truth) > abs(loose - truth)


class TestTheReplayTrap:
    def test_replay_is_biased_where_the_corrected_estimators_are_not(self) -> None:
        relevance, logged, target, examined, clicks = _setup()
        rates = np.bincount(examined, weights=clicks, minlength=ITEMS) / clicks.size

        true_cost = 1.0 - value_under_policy(relevance, target) / value_under_policy(
            relevance, logged
        )
        replay_cost = 1.0 - naive_replay(rates, target) / naive_replay(rates, logged)
        corrected = 1.0 - snips(clicks, target[examined], logged[examined]) / naive(clicks)

        assert corrected == pytest.approx(true_cost, abs=0.01)
        assert abs(replay_cost - true_cost) > 0.01

    def test_the_direction_of_the_replay_error_is_not_stable(self) -> None:
        """Le point qui interdit de plaider la prudence : le signe de l'erreur change.

        Si le biais était toujours conservateur — s'il surestimait toujours le coût — un
        résultat favorable obtenu naïvement resterait défendable. Il ne l'est pas : à
        configuration identique, le sens dépend du jeu de contenus, donc de données qu'on ne
        choisit pas.
        """
        signs = {}
        for seed in (3, 11):
            relevance, logged, target, examined, clicks = _setup(seed=seed)
            rates = np.bincount(examined, weights=clicks, minlength=ITEMS) / clicks.size
            true_cost = 1.0 - value_under_policy(relevance, target) / value_under_policy(
                relevance, logged
            )
            replay_cost = 1.0 - naive_replay(rates, target) / naive_replay(rates, logged)
            signs[seed] = replay_cost > true_cost

        assert set(signs.values()) == {True, False}, signs


class TestDiagnostics:
    def test_identical_policies_keep_every_observation(self) -> None:
        policy = np.array([0.4, 0.35, 0.25])
        drawn = np.array([0, 1, 2, 0, 1])

        assert effective_sample_size(policy[drawn], policy[drawn]) == pytest.approx(drawn.size)

    def test_divergent_policies_lose_observations(self) -> None:
        logged = np.array([0.9, 0.05, 0.05])
        target = np.array([0.05, 0.05, 0.9])
        drawn = np.array([0, 0, 0, 0, 1, 2])

        assert effective_sample_size(target[drawn], logged[drawn]) < drawn.size

    def test_a_simulated_policy_must_be_a_policy(self) -> None:
        with pytest.raises(ValueError, match="somme à 1"):
            simulate_logged_feedback(np.array([0.5, 0.5]), np.array([0.5, 0.9]), 10)

    def test_a_relevance_is_a_probability(self) -> None:
        with pytest.raises(ValueError, match="probabilité"):
            simulate_logged_feedback(np.array([1.5, 0.5]), np.array([0.5, 0.5]), 10)


class TestPositionBiasEstimation:
    """Estimer la sévérité plutôt que la poser — et savoir quand on ne le peut pas."""

    @pytest.mark.parametrize("severity", [0.5, 1.0, 1.5])
    def test_the_true_severity_is_recovered(self, severity: float) -> None:
        rng = np.random.default_rng(5)
        relevance = rng.uniform(0.15, 0.9, 12)

        items, ranks, clicks = simulate_ranked_feedback(
            relevance, 40_000, severity, exploration=0.5, rng=rng
        )
        estimate = estimate_position_bias(items, ranks, clicks)

        assert estimate.identifiable
        assert estimate.severity == pytest.approx(severity, rel=0.06)

    def test_a_deterministic_platform_makes_it_unidentifiable(self) -> None:
        """Sans variation de rang à contenu fixé, le paramètre n'est pas dans les données.

        C'est le cas où poser la valeur au lieu de l'estimer serait indétectable dans les
        résultats — la fonction refuse donc de renvoyer un chiffre.
        """
        rng = np.random.default_rng(5)
        relevance = rng.uniform(0.15, 0.9, 12)

        items, ranks, clicks = simulate_ranked_feedback(
            relevance, 20_000, 1.0, exploration=0.0, rng=rng
        )
        estimate = estimate_position_bias(items, ranks, clicks)

        assert not estimate.identifiable
        assert np.isnan(estimate.severity)
        assert estimate.items_with_variation == 0

    def test_thin_exploration_shows_up_in_the_standard_error(self) -> None:
        """L'erreur type doit dire qu'une estimation ne repose sur presque rien."""
        rng = np.random.default_rng(5)
        relevance = rng.uniform(0.15, 0.9, 12)

        errors = []
        for exploration in (0.05, 0.5):
            items, ranks, clicks = simulate_ranked_feedback(
                relevance, 40_000, 1.0, exploration=exploration, rng=rng
            )
            errors.append(estimate_position_bias(items, ranks, clicks).standard_error)

        assert errors[0] > errors[1]

    def test_mismatched_records_are_refused(self) -> None:
        with pytest.raises(ValueError, match="mêmes impressions"):
            estimate_position_bias(np.array([0, 1]), np.array([1]), np.array([0, 1]))

    def test_ranks_start_at_one(self) -> None:
        with pytest.raises(ValueError, match="rangs"):
            estimate_position_bias(np.array([0]), np.array([0]), np.array([1]))

    def test_a_misposited_severity_wrecks_the_correction(self) -> None:
        """Ce qui justifie d'estimer : corriger avec le mauvais paramètre corrige mal."""
        rng = np.random.default_rng(11)
        items_count = 20
        relevance = rng.uniform(0.05, 0.95, items_count)
        diversity = rng.uniform(0.0, 1.0, items_count)
        logged_ranks = np.argsort(np.argsort(-relevance)) + 1
        target_ranks = np.argsort(np.argsort(-(0.4 * relevance + 0.6 * diversity))) + 1

        logged = rank_propensities(logged_ranks, 1.0)
        target = rank_propensities(target_ranks, 1.0)
        examined, clicks = simulate_logged_feedback(relevance, logged, 200_000, rng)
        truth = 1.0 - value_under_policy(relevance, target) / value_under_policy(
            relevance, logged
        )

        def cost_assuming(severity: float) -> float:
            assumed_logged = rank_propensities(logged_ranks, severity)
            assumed_target = rank_propensities(target_ranks, severity)
            return 1.0 - snips(
                clicks, assumed_target[examined], assumed_logged[examined]
            ) / naive(clicks)

        assert cost_assuming(1.0) == pytest.approx(truth, rel=0.05)
        assert abs(cost_assuming(2.0) - truth) / truth > 1.0
