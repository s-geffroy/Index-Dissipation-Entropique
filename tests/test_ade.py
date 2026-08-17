"""Validation de l'Algorithme de Dissipation Entropique.

Le test décisif est celui du signe : avec :math:`\\mu = 0`, l'ADE doit se réduire
**exactement** au filtre d'engagement qu'il prétend remplacer, et avec
:math:`\\mu > 0` il doit faire remonter un contenu divergent dans le fil d'un
utilisateur enfermé. C'est ce qui distingue la version retenue
(:math:`+\\mu \\Delta H`) de la version erronée du fil (:math:`-\\mu \\Delta H`),
laquelle refermerait la bulle au lieu de l'ouvrir.
"""

from __future__ import annotations

import pytest

from ide.ade import Candidate, EntropicScorer, annealing_coefficient, entropic_score


@pytest.fixture
def frozen_feed() -> list[str]:
    """Fil d'un utilisateur enfermé dans une bulle : une seule modalité, vingt fois."""
    return ["complot"] * 20


@pytest.fixture
def balanced_feed() -> list[str]:
    """Fil équilibré sur les quatre points de vue du catalogue."""
    return ["complot", "factuel", "opinion", "satire"] * 5


@pytest.fixture
def candidates() -> list[Candidate]:
    """Deux contenus : l'un très pertinent mais enfermant, l'autre divergent."""
    return [
        Candidate("prolonge-la-bulle", "complot", relevance=0.90),
        Candidate("fact-check", "factuel", relevance=0.55),
    ]


class TestEntropicScore:
    def test_score_adds_the_weighted_entropic_impact(self) -> None:
        assert entropic_score(relevance=0.5, delta_entropy=0.2, mu=2.0) == pytest.approx(0.9)

    def test_zero_coefficient_reduces_to_pure_relevance(self) -> None:
        assert entropic_score(relevance=0.42, delta_entropy=0.9, mu=0.0) == pytest.approx(0.42)

    def test_diversifying_content_is_rewarded(self) -> None:
        """Signe retenu : ΔH > 0 doit augmenter le score, pas le diminuer."""
        enclosing = entropic_score(relevance=0.5, delta_entropy=-0.2, mu=1.0)
        diversifying = entropic_score(relevance=0.5, delta_entropy=0.2, mu=1.0)

        assert diversifying > enclosing

    def test_negative_coefficient_is_refused(self) -> None:
        """Un μ négatif inverserait la politique de l'algorithme."""
        with pytest.raises(ValueError, match="positif ou nul"):
            entropic_score(relevance=0.5, delta_entropy=0.2, mu=-1.0)


class TestAnnealingCoefficient:
    def test_healthy_feed_stays_at_rest(self) -> None:
        assert annealing_coefficient(0.8, critical_index=0.4) == 0.5

    def test_frozen_bubble_triggers_full_annealing(self) -> None:
        assert annealing_coefficient(0.0, critical_index=0.4) == 4.0

    def test_coefficient_rises_progressively_below_the_threshold(self) -> None:
        """La montée est continue : un seuil dur ferait battre l'algorithme.

        Avec un déclenchement en tout ou rien, chaque intervention relèverait
        l'index juste au-dessus du seuil, désactivant l'intervention suivante, qui
        le laisserait retomber — un cycle d'oscillations sans stabilisation.
        """
        coefficients = [
            annealing_coefficient(index, critical_index=0.4) for index in (0.4, 0.3, 0.2, 0.1, 0.0)
        ]

        assert coefficients == sorted(coefficients)
        assert len(set(coefficients)) == len(coefficients)

    def test_coefficient_is_continuous_at_the_threshold(self) -> None:
        just_below = annealing_coefficient(0.3999, critical_index=0.4)

        assert just_below == pytest.approx(0.5, abs=1e-3)

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"current_index": 1.5},
            {"current_index": -0.1},
            {"current_index": 0.5, "critical_index": 0.0},
            {"current_index": 0.5, "resting_mu": 5.0, "annealing_mu": 1.0},
        ],
    )
    def test_invalid_parameters_are_rejected(self, kwargs: dict[str, float]) -> None:
        with pytest.raises(ValueError):
            annealing_coefficient(**kwargs)


class TestEntropicScorer:
    def test_index_of_a_frozen_feed_is_zero(self, frozen_feed: list[str]) -> None:
        scorer = EntropicScorer(catalogue_size=4)

        assert scorer.current_index(frozen_feed) == 0.0

    def test_index_of_a_balanced_feed_is_maximal(self, balanced_feed: list[str]) -> None:
        scorer = EntropicScorer(catalogue_size=4)

        assert scorer.current_index(balanced_feed) == pytest.approx(1.0)

    def test_annealing_engages_on_a_frozen_feed(self, frozen_feed: list[str]) -> None:
        scorer = EntropicScorer(catalogue_size=4)

        assert scorer.mu(frozen_feed) == scorer.annealing_mu

    def test_annealing_stays_idle_on_a_balanced_feed(self, balanced_feed: list[str]) -> None:
        scorer = EntropicScorer(catalogue_size=4)

        assert scorer.mu(balanced_feed) == scorer.resting_mu

    def test_divergent_content_has_a_positive_entropic_impact(
        self, frozen_feed: list[str]
    ) -> None:
        scorer = EntropicScorer(catalogue_size=4)

        assert scorer.delta_entropy(frozen_feed, "factuel") > 0.0

    def test_confirming_content_has_no_positive_impact(self, frozen_feed: list[str]) -> None:
        """Un énième contenu conforme au biais ne diversifie rien."""
        scorer = EntropicScorer(catalogue_size=4)

        assert scorer.delta_entropy(frozen_feed, "complot") == pytest.approx(0.0)

    def test_fact_check_outranks_a_more_relevant_but_enclosing_content(
        self, frozen_feed: list[str], candidates: list[Candidate]
    ) -> None:
        """Le résultat attendu de l'ADE : désaimantation organique de la bulle."""
        ranked = EntropicScorer(catalogue_size=4).rank(frozen_feed, candidates)

        assert ranked[0].identifier == "fact-check"
        assert ranked[0].score > ranked[1].score

    def test_zero_coefficient_reproduces_the_engagement_filter(
        self, frozen_feed: list[str], candidates: list[Candidate]
    ) -> None:
        """À μ = 0, l'ADE doit être indiscernable d'un tri par pertinence."""
        neutral = EntropicScorer(catalogue_size=4, resting_mu=0.0, annealing_mu=0.0)
        ranked = neutral.rank(frozen_feed, candidates)

        assert [item.identifier for item in ranked] == ["prolonge-la-bulle", "fact-check"]
        assert ranked[0].score == pytest.approx(0.90)

    def test_balanced_feed_keeps_relevance_in_charge(
        self, balanced_feed: list[str], candidates: list[Candidate]
    ) -> None:
        """Sur un fil sain, l'algorithme n'a pas à intervenir : la pertinence tranche.

        L'ADE n'est pas un filtre de diversité permanent — il ne se réveille que
        lorsque l'index descend, ce qui limite son coût en pertinence perçue.
        """
        ranked = EntropicScorer(catalogue_size=4).rank(balanced_feed, candidates)

        assert ranked[0].identifier == "prolonge-la-bulle"

    def test_identical_viewpoints_share_the_same_impact(self, frozen_feed: list[str]) -> None:
        """Deux contenus de même étiquette ont, par construction, le même ΔH."""
        duplicates = [
            Candidate("a", "factuel", relevance=0.5),
            Candidate("b", "factuel", relevance=0.4),
        ]
        ranked = EntropicScorer(catalogue_size=4).rank(frozen_feed, duplicates)

        assert ranked[0].delta_entropy == ranked[1].delta_entropy
        assert ranked[0].identifier == "a"

    def test_serving_repeatedly_reopens_a_frozen_bubble(self, frozen_feed: list[str]) -> None:
        """Boucle complète : le mode recuit fait remonter l'index au fil des cycles."""
        scorer = EntropicScorer(catalogue_size=4)
        catalogue = [
            Candidate("bulle", "complot", relevance=0.95),
            Candidate("check", "factuel", relevance=0.50),
            Candidate("tribune", "opinion", relevance=0.45),
            Candidate("satire", "satire", relevance=0.40),
        ]

        feed = list(frozen_feed)
        before = scorer.current_index(feed)
        for _ in range(12):
            feed = scorer.serve(feed, catalogue)

        assert scorer.current_index(feed) > before

    def test_empty_candidate_list_is_handled(self, frozen_feed: list[str]) -> None:
        scorer = EntropicScorer(catalogue_size=4)

        assert scorer.rank(frozen_feed, []) == []
        assert scorer.serve(frozen_feed, []) == frozen_feed

    def test_degenerate_catalogue_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="deux points de vue"):
            EntropicScorer(catalogue_size=1)
