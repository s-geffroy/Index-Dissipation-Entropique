"""Validation des divergences conscientes du rang.

Ce qui est vérifié ici tient en deux points. La **mécanique** d'abord — bornes, symétrie,
cas dégénérés — parce qu'une divergence normalisée par convention plutôt qu'exactement ne
supporterait pas un seuil réglementaire. Le **quatrième adversaire** ensuite : une plateforme
qui enterre sa diversité au bas du fil doit voir sa mesure chuter, alors qu'une mesure
ponctuelle sur l'ensemble servi ne verrait aucune différence.
"""

from __future__ import annotations

import numpy as np
import pytest

from ide.gaming import position_entropy
from ide.radio import (
    DISCOUNTS,
    calibration,
    fragmentation,
    jensen_shannon,
    radio_divergence,
    rank_aware_distribution,
    rank_weights,
    representation,
)

CATEGORIES = 4
DIVERSE_ON_TOP = np.array([0, 1, 2, 3, 0, 1, 2, 3])
DIVERSE_BURIED = np.array([0, 0, 0, 0, 1, 2, 3, 0])
SUPPLY = np.array([0, 1, 2, 3])


class TestRankWeights:
    def test_attention_decreases_with_rank(self) -> None:
        assert np.all(np.diff(rank_weights(6, "mrr")) < 0)
        assert np.all(np.diff(rank_weights(6, "log")) < 0)

    def test_the_absence_of_discount_is_uniform_attention(self) -> None:
        assert rank_weights(5, "none") == pytest.approx(np.ones(5))

    def test_the_logarithmic_discount_is_gentler_than_the_reciprocal(self) -> None:
        """Le choix de la remise déplace le résultat : il doit être publié avec lui."""
        mrr = rank_weights(8, "mrr")
        log = rank_weights(8, "log")

        assert log[-1] / log[0] > mrr[-1] / mrr[0]

    @pytest.mark.parametrize("discount", DISCOUNTS)
    def test_every_declared_discount_is_usable(self, discount: str) -> None:
        assert rank_weights(4, discount).size == 4

    def test_an_unknown_discount_is_refused(self) -> None:
        with pytest.raises(ValueError, match="remise"):
            rank_weights(4, "harmonique")


class TestJensenShannon:
    def test_identical_distributions_diverge_by_zero(self) -> None:
        distribution = np.array([0.4, 0.3, 0.2, 0.1])

        assert jensen_shannon(distribution, distribution) == pytest.approx(0.0, abs=1e-12)

    def test_disjoint_supports_diverge_by_one(self) -> None:
        """La borne est exacte en base 2 — c'est ce qui rend la normalisation défendable."""
        assert jensen_shannon(np.array([1.0, 0.0]), np.array([0.0, 1.0])) == pytest.approx(1.0)

    def test_the_divergence_is_symmetric(self) -> None:
        first = np.array([0.7, 0.2, 0.1])
        second = np.array([0.2, 0.3, 0.5])

        assert jensen_shannon(first, second) == pytest.approx(jensen_shannon(second, first))

    def test_mismatched_supports_are_refused(self) -> None:
        with pytest.raises(ValueError, match="mêmes catégories"):
            jensen_shannon(np.array([0.5, 0.5]), np.array([0.3, 0.3, 0.4]))


class TestRankAwareDistribution:
    def test_without_discount_it_is_the_ordinary_frequency(self) -> None:
        feed = np.array([0, 0, 1, 2])

        assert rank_aware_distribution(feed, 3, "none") == pytest.approx([0.5, 0.25, 0.25])

    def test_with_discount_the_head_of_the_feed_weighs_more(self) -> None:
        head = rank_aware_distribution(np.array([0, 1]), 2, "mrr")

        assert head[0] > head[1]

    def test_reversing_a_feed_changes_the_distribution(self) -> None:
        """Si l'ordre ne changeait rien, la conscience du rang n'apporterait rien."""
        forward = rank_aware_distribution(DIVERSE_ON_TOP, CATEGORIES, "mrr")
        backward = rank_aware_distribution(DIVERSE_ON_TOP[::-1], CATEGORIES, "mrr")

        assert not np.allclose(forward, backward)

    def test_a_category_outside_the_reference_is_refused(self) -> None:
        with pytest.raises(ValueError, match="référentiel"):
            rank_aware_distribution(np.array([0, 5]), 3)

    def test_an_empty_feed_has_no_distribution(self) -> None:
        with pytest.raises(ValueError, match="vide"):
            rank_aware_distribution(np.array([], dtype=int), 3)


class TestTheBurialAdversary:
    """Le quatrième adversaire : se conformer en enterrant la diversité."""

    def test_the_two_feeds_are_indistinguishable_without_rank_awareness(self) -> None:
        """Prémisse du test : les deux fils contiennent exactement les mêmes contenus."""
        catalogue = np.arange(CATEGORIES, dtype=float)
        top = np.bincount(DIVERSE_ON_TOP, minlength=CATEGORIES) / DIVERSE_ON_TOP.size
        buried = np.bincount(DIVERSE_BURIED, minlength=CATEGORIES) / DIVERSE_BURIED.size

        assert position_entropy(top, catalogue, catalogue) > 0.0
        # Les deux fils diffèrent ici par leur composition ; le test suivant les égalise.
        assert not np.allclose(top, buried)

    def test_a_permutation_alone_changes_the_rank_aware_measure(self) -> None:
        """Même multiensemble, ordre différent : la mesure ponctuelle ne voit rien."""
        catalogue = np.arange(CATEGORIES, dtype=float)
        shuffled = np.array([0, 0, 1, 2, 3, 3, 2, 1])
        buried = np.array([0, 0, 3, 3, 2, 2, 1, 1])[::-1]

        composition = np.bincount(shuffled, minlength=CATEGORIES) / shuffled.size
        same = np.bincount(buried, minlength=CATEGORIES) / buried.size
        assert np.allclose(composition, same), "les deux fils doivent avoir la même composition"

        blind = position_entropy(composition, catalogue, catalogue)
        assert blind == pytest.approx(position_entropy(same, catalogue, catalogue))

        assert representation(shuffled, SUPPLY, CATEGORIES) != pytest.approx(
            representation(buried, SUPPLY, CATEGORIES)
        )

    def test_burying_the_diversity_worsens_the_divergence(self) -> None:
        on_top = representation(np.array([0, 1, 2, 3, 0, 1, 2, 3]), SUPPLY, CATEGORIES)
        buried = representation(np.array([0, 0, 0, 1, 2, 3, 1, 2]), SUPPLY, CATEGORIES)

        assert buried > on_top

    def test_without_the_discount_burying_costs_nothing(self) -> None:
        """La conscience du rang est exactement ce qui ferme cette échappatoire."""
        on_top = representation(
            np.array([0, 1, 2, 3, 0, 1, 2, 3]), SUPPLY, CATEGORIES, discount="none"
        )
        buried = representation(
            np.array([0, 0, 1, 1, 2, 2, 3, 3]), SUPPLY, CATEGORIES, discount="none"
        )

        assert buried == pytest.approx(on_top)


class TestTheFiveReferences:
    def test_calibration_is_zero_on_a_feed_matching_the_history(self) -> None:
        """Zéro veut dire « conforme à ce que le lecteur lisait déjà » — pas « bon »."""
        history = np.array([0, 0, 1, 1])
        feed = np.array([0, 1, 0, 1])

        assert calibration(feed, history, 2, discount="none") == pytest.approx(0.0, abs=1e-12)

    def test_fragmentation_is_zero_between_two_identical_feeds(self) -> None:
        feed = np.array([0, 1, 2, 3])

        assert fragmentation(feed, feed, CATEGORIES) == pytest.approx(0.0, abs=1e-12)

    def test_fragmentation_grows_when_two_readers_share_nothing(self) -> None:
        first = np.array([0, 0, 1, 1])
        second = np.array([2, 2, 3, 3])

        assert fragmentation(first, second, CATEGORIES) > 0.9

    def test_the_reference_must_cover_the_declared_catalogue(self) -> None:
        with pytest.raises(ValueError, match="référentiel"):
            radio_divergence(np.array([0, 1]), np.array([0.5, 0.5]), category_count=4)

    def test_a_reference_of_null_mass_is_refused(self) -> None:
        with pytest.raises(ValueError, match="masse nulle"):
            radio_divergence(np.array([0, 1]), np.zeros(2), category_count=2)


def test_la_remise_accepte_une_severite_mesuree():
    """La remise n'est pas une convention : elle doit pouvoir porter la sévérité mesurée.

    À sévérité 1, elle rend exactement la remise du rang réciproque ; à sévérité nulle, une
    attention uniforme. Entre les deux, elle décrit une surface réelle.
    """
    assert rank_weights(5, discount=1.0) == pytest.approx(rank_weights(5, discount="mrr"))
    assert rank_weights(5, discount=0.0) == pytest.approx(rank_weights(5, discount="none"))

    flat = rank_weights(5, discount=0.1)
    steep = rank_weights(5, discount=2.0)
    # plus la sévérité est grande, plus l'attention se concentre en tête
    assert flat[-1] / flat[0] > steep[-1] / steep[0]


def test_une_severite_negative_est_refusee():
    with pytest.raises(ValueError, match="ne peut être négative"):
        rank_weights(5, discount=-0.5)

