"""Validation du test adverse de l'index.

Ces tests portent sur un résultat **négatif** — l'IDE se sature sans coût — et c'est ce qui
les rend délicats : une erreur de modèle qui exagérerait la manipulabilité donnerait le
résultat attendu. Chaque propriété est donc vérifiée dans les deux sens, y compris celles qui
vont contre la thèse : que la contrainte a bien un coût sur un catalogue honnête, et que
l'optimiseur sature effectivement le plancher au lieu de le contourner.
"""

from __future__ import annotations

import numpy as np
import pytest

from ide.gaming import (
    Feed,
    canonical_positions,
    centre_share,
    engagement,
    excess_signature,
    gaussian_ild,
    ide_of_feed,
    largest_gap,
    max_achievable_rao,
    optimal_feed_under,
    optimal_feed_under_ide,
    optimal_feed_under_rao,
    position_entropy,
    rao_entropy,
    served_positions,
    target_divergence,
)

CATALOGUE = canonical_positions(VIEWPOINTS := 8)
REFERENCE = float(np.ptp(CATALOGUE))
BANDWIDTH = float(CATALOGUE[1] - CATALOGUE[0])


def _bimodal() -> np.ndarray:
    """Fil polarisé : la moitié de la masse à chaque bord, rien entre les deux."""
    weights = np.zeros(VIEWPOINTS)
    weights[0] = weights[-1] = 0.5
    return weights


def _uniform() -> np.ndarray:
    return np.full(VIEWPOINTS, 1.0 / VIEWPOINTS)

USER = 0.6
WIDTH = 0.5


class TestBuildingBlocks:
    def test_a_catalogue_needs_at_least_two_viewpoints(self) -> None:
        with pytest.raises(ValueError, match="deux points de vue"):
            canonical_positions(1)

    def test_engagement_peaks_at_the_reader(self) -> None:
        values = engagement(np.array([USER, USER + 0.5, USER - 0.9]), USER, WIDTH)

        assert values[0] == pytest.approx(1.0)
        assert values[0] > values[1] > values[2]

    def test_full_decoupling_collapses_every_label_onto_the_reader(self) -> None:
        positions = served_positions(canonical_positions(VIEWPOINTS), USER, decoupling=1.0)

        assert positions == pytest.approx(np.full(VIEWPOINTS, USER))

    def test_no_decoupling_leaves_the_catalogue_untouched(self) -> None:
        canonical = canonical_positions(VIEWPOINTS)

        assert served_positions(canonical, USER, 0.0) == pytest.approx(canonical)

    @pytest.mark.parametrize("decoupling", [-0.1, 1.1])
    def test_decoupling_stays_within_bounds(self, decoupling: float) -> None:
        with pytest.raises(ValueError, match="découplage"):
            served_positions(canonical_positions(VIEWPOINTS), USER, decoupling)


class TestIndices:
    def test_the_ide_is_one_on_a_uniform_feed_and_zero_on_a_frozen_one(self) -> None:
        assert ide_of_feed(np.full(4, 0.25)) == pytest.approx(1.0)
        assert ide_of_feed(np.array([1.0, 0.0, 0.0, 0.0])) == pytest.approx(0.0)

    def test_rao_is_maximal_at_the_two_extremes_of_the_reference(self) -> None:
        positions = canonical_positions(VIEWPOINTS)
        reference = float(positions.max() - positions.min())
        weights = np.zeros(VIEWPOINTS)
        weights[0] = weights[-1] = 0.5

        assert rao_entropy(weights, positions, reference) == pytest.approx(1.0)

    def test_rao_is_zero_when_every_served_item_coincides(self) -> None:
        """C'est la propriété qui distingue Rao de l'IDE, et toute la thèse en dépend."""
        positions = served_positions(canonical_positions(VIEWPOINTS), USER, decoupling=1.0)
        reference = float(np.ptp(canonical_positions(VIEWPOINTS)))

        assert rao_entropy(np.full(VIEWPOINTS, 1 / VIEWPOINTS), positions, reference) == (
            pytest.approx(0.0, abs=1e-12)
        )

    def test_rao_is_not_normalised_by_the_reach_actually_served(self) -> None:
        """Garde-fou : une normalisation par l'étalement servi ferait marquer 1 à un point.

        C'est le défaut qu'une première version du module portait, et il aurait produit la
        conclusion inverse — celle que l'entropie de Rao est manipulable elle aussi.
        """
        narrow = np.array([0.0, 1e-9])
        weights = np.array([0.5, 0.5])

        assert rao_entropy(weights, narrow, reference=2.0) < 1e-8

    def test_the_reachable_rao_bounds_what_a_catalogue_allows(self) -> None:
        canonical = canonical_positions(VIEWPOINTS)
        reference = float(np.ptp(canonical))

        assert max_achievable_rao(canonical, reference) == pytest.approx(1.0)
        half = served_positions(canonical, USER, decoupling=0.5)
        assert max_achievable_rao(half, reference) == pytest.approx(0.5)

    @pytest.mark.parametrize("reference", [0.0, -1.0])
    def test_a_degenerate_reference_is_refused(self, reference: float) -> None:
        with pytest.raises(ValueError, match="étendue de référence"):
            rao_entropy(np.array([0.5, 0.5]), np.array([0.0, 1.0]), reference)


class TestOptimisationUnderIde:
    def test_without_a_floor_the_platform_serves_its_single_best_item(self) -> None:
        feed = optimal_feed_under_ide(VIEWPOINTS, USER, floor=0.0, width=WIDTH)

        assert feed.weights.max() == pytest.approx(1.0)
        assert feed.ide == pytest.approx(0.0)

    @pytest.mark.parametrize("floor", [0.3, 0.5, 0.8, 0.95])
    def test_the_floor_is_saturated_exactly(self, floor: float) -> None:
        """Une plateforme rationnelle ne dépasse jamais la contrainte : elle l'atteint."""
        feed = optimal_feed_under_ide(VIEWPOINTS, USER, floor=floor, width=WIDTH)

        assert feed.ide == pytest.approx(floor, abs=1e-6)

    def test_an_honest_catalogue_pays_a_real_price(self) -> None:
        """La thèse serait vide si la contrainte ne coûtait rien même sans manipulation."""
        free = optimal_feed_under_ide(VIEWPOINTS, USER, floor=0.0, width=WIDTH)
        bound = optimal_feed_under_ide(VIEWPOINTS, USER, floor=0.8, width=WIDTH)

        assert bound.engagement < free.engagement
        assert 1.0 - bound.engagement / free.engagement > 0.10

    def test_the_price_grows_with_the_floor(self) -> None:
        engagements = [
            optimal_feed_under_ide(VIEWPOINTS, USER, floor=floor, width=WIDTH).engagement
            for floor in (0.2, 0.5, 0.8, 1.0)
        ]

        assert engagements == sorted(engagements, reverse=True)

    def test_full_decoupling_makes_the_constraint_free(self) -> None:
        """Le résultat central : un IDE parfait, à engagement maximal."""
        free = optimal_feed_under_ide(VIEWPOINTS, USER, floor=0.0, decoupling=1.0, width=WIDTH)
        bound = optimal_feed_under_ide(VIEWPOINTS, USER, floor=1.0, decoupling=1.0, width=WIDTH)

        assert bound.ide == pytest.approx(1.0)
        assert bound.engagement == pytest.approx(free.engagement)
        assert bound.rao == pytest.approx(0.0, abs=1e-12)

    def test_the_price_falls_monotonically_with_decoupling(self) -> None:
        costs = []
        for decoupling in (0.0, 0.25, 0.5, 0.75, 1.0):
            free = optimal_feed_under_ide(
                VIEWPOINTS, USER, floor=0.0, decoupling=decoupling, width=WIDTH
            )
            bound = optimal_feed_under_ide(
                VIEWPOINTS, USER, floor=0.8, decoupling=decoupling, width=WIDTH
            )
            costs.append(1.0 - bound.engagement / free.engagement)

        assert costs == sorted(costs, reverse=True)
        assert costs[-1] == pytest.approx(0.0, abs=1e-9)

    @pytest.mark.parametrize("floor", [-0.1, 1.5])
    def test_an_impossible_floor_is_refused(self, floor: float) -> None:
        with pytest.raises(ValueError, match="plancher"):
            optimal_feed_under_ide(VIEWPOINTS, USER, floor=floor)


class TestOptimisationUnderRao:
    def test_an_honest_catalogue_can_comply(self) -> None:
        feed = optimal_feed_under_rao(VIEWPOINTS, USER, floor=0.5, width=WIDTH)

        assert feed.rao >= 0.5 - 1e-6

    def test_a_gamed_catalogue_cannot_reach_the_floor_at_all(self) -> None:
        """Là où l'IDE se sature gratuitement, le plancher de Rao devient inatteignable."""
        feed = optimal_feed_under_rao(VIEWPOINTS, USER, floor=0.5, decoupling=1.0, width=WIDTH)

        assert feed.reachable_rao == pytest.approx(0.0, abs=1e-12)
        assert feed.rao < 0.5

    def test_gaming_makes_the_rao_constraint_bite_harder_not_softer(self) -> None:
        """Propriété inverse de celle de l'IDE, et c'est ce qui en fait une norme tenable."""
        costs = []
        for decoupling in (0.0, 0.25, 0.5):
            free = optimal_feed_under_rao(
                VIEWPOINTS, USER, floor=0.0, decoupling=decoupling, width=WIDTH
            )
            bound = optimal_feed_under_rao(
                VIEWPOINTS, USER, floor=0.5, decoupling=decoupling, width=WIDTH
            )
            costs.append(1.0 - bound.engagement / free.engagement)

        assert costs == sorted(costs)

    def test_the_result_is_reproducible(self) -> None:
        """L'optimisation est numérique et à départs aléatoires : la graine doit suffire."""
        first = optimal_feed_under_rao(VIEWPOINTS, USER, floor=0.5, width=WIDTH, seed=3)
        second = optimal_feed_under_rao(VIEWPOINTS, USER, floor=0.5, width=WIDTH, seed=3)

        assert first.weights == pytest.approx(second.weights)


class TestSignature:
    def test_an_honest_platform_shows_no_excess(self) -> None:
        assert excess_signature(VIEWPOINTS, USER, 0.8, decoupling=0.0) == pytest.approx(0.0)

    def test_the_excess_grows_with_decoupling(self) -> None:
        excesses = [
            excess_signature(VIEWPOINTS, USER, 0.8, decoupling=decoupling)
            for decoupling in (0.0, 0.25, 0.5, 0.75, 1.0)
        ]

        assert excesses == sorted(excesses)
        assert excesses[-1] > 0.5

    def test_the_raw_gap_is_not_a_usable_threshold(self) -> None:
        """Un fil parfaitement honnête affiche déjà un écart brut substantiel.

        C'est pourquoi le module ne publie pas de seuil sur l'écart brut : il faudrait
        l'inventer, et le dépôt a déjà eu à retirer un chiffre fabriqué de cette nature.
        """
        honest = optimal_feed_under_ide(VIEWPOINTS, USER, floor=0.8, width=WIDTH)

        assert honest.signature > 0.3


class TestFeed:
    def test_a_feed_reports_both_indices_on_the_same_object(self) -> None:
        feed = Feed(
            weights=np.array([0.5, 0.5]),
            positions=np.array([-1.0, 1.0]),
            user=0.0,
            width=WIDTH,
            catalogue=np.array([-1.0, 1.0]),
        )

        assert feed.ide == pytest.approx(1.0)
        assert feed.rao == pytest.approx(1.0)
        assert feed.signature == pytest.approx(0.0)


class TestThePolarisationPathology:
    """Le défaut de l'entropie de Rao, et ce qui l'en préserve.

    L'entropie de Rao est la distance intra-liste, dont Ohsaka et Togashi (SIGIR 2023) ont
    montré qu'elle admet des optima dégénérés. Sur un axe d'opinion, le dégénéré porte un
    nom : c'est le fil bimodal, qui sert les deux bords et vide le centre. Une norme qui le
    préfère prescrirait exactement ce que ce dépôt cherche à mesurer.
    """

    def test_rao_prefers_a_polarised_feed_to_a_spread_one(self) -> None:
        """Le défaut, énoncé comme un test : il est reproductible, donc il est réel."""
        polarised = rao_entropy(_bimodal(), CATALOGUE, REFERENCE)
        spread = rao_entropy(_uniform(), CATALOGUE, REFERENCE)

        assert polarised == pytest.approx(1.0)
        assert polarised > spread

    @pytest.mark.parametrize(
        "measure",
        [
            lambda q, x: position_entropy(q, x, CATALOGUE),
            lambda q, x: gaussian_ild(q, x, BANDWIDTH),
            lambda q, x: target_divergence(q, x, CATALOGUE),
        ],
        ids=["entropie de position", "gaussian ILD", "proximité à la cible"],
    )
    def test_the_replacements_prefer_a_spread_feed(self, measure) -> None:
        assert measure(_bimodal(), CATALOGUE) < measure(_uniform(), CATALOGUE)

    @pytest.mark.parametrize(
        "measure",
        [
            lambda q, x: rao_entropy(q, x, REFERENCE),
            lambda q, x: position_entropy(q, x, CATALOGUE),
            lambda q, x: gaussian_ild(q, x, BANDWIDTH),
            lambda q, x: target_divergence(q, x, CATALOGUE),
        ],
        ids=["rao", "entropie de position", "gaussian ILD", "proximité à la cible"],
    )
    def test_every_candidate_still_resists_label_stuffing(self, measure) -> None:
        """La correction ne doit pas rouvrir la faille qu'elle vient de fermer."""
        collapsed = served_positions(CATALOGUE, USER, decoupling=1.0)

        best = max(measure(w, collapsed) for w in (_uniform(), _bimodal(), np.eye(VIEWPOINTS)[0]))

        assert best < 0.6

    def test_the_optimum_under_rao_empties_the_centre(self) -> None:
        """Ce n'est pas une manipulation : c'est la réponse optimale à la contrainte."""
        feed = optimal_feed_under(
            lambda q, x: rao_entropy(q, x, REFERENCE), VIEWPOINTS, USER, 0.8, width=WIDTH
        )

        assert feed.largest_gap > 0.5
        assert int(np.sum(feed.weights > 0.01)) < VIEWPOINTS

    def test_the_optimum_under_position_entropy_does_not(self) -> None:
        feed = optimal_feed_under(
            lambda q, x: position_entropy(q, x, CATALOGUE), VIEWPOINTS, USER, 0.8, width=WIDTH
        )

        assert feed.largest_gap < 0.2
        assert feed.centre_share > 0.5


class TestReplacementMeasures:
    def test_position_entropy_keeps_the_index_conventions(self) -> None:
        """Un fil gelé vaut 0, l'uniforme vaut 1 : c'est l'IDE, sur les contenus."""
        frozen = np.zeros(VIEWPOINTS)
        frozen[0] = 1.0

        assert position_entropy(frozen, CATALOGUE, CATALOGUE) == pytest.approx(0.0)
        assert position_entropy(_uniform(), CATALOGUE, CATALOGUE) == pytest.approx(1.0)

    def test_position_entropy_is_nominal_and_blind_to_geometry(self) -> None:
        """Limite à déclarer : elle compte les bacs occupés, elle n'en voit pas l'écartement.

        C'est pourquoi le plus grand vide est publié à côté d'elle plutôt qu'à sa place.
        """
        clustered = np.zeros(VIEWPOINTS)
        clustered[[0, 1, 2, 3]] = 0.25
        spread = np.zeros(VIEWPOINTS)
        spread[[0, 2, 5, 7]] = 0.25

        assert position_entropy(clustered, CATALOGUE, CATALOGUE) == pytest.approx(
            position_entropy(spread, CATALOGUE, CATALOGUE)
        )
        assert largest_gap(clustered, CATALOGUE, CATALOGUE) < largest_gap(
            spread, CATALOGUE, CATALOGUE
        )

    def test_gaussian_ild_sees_the_geometry_the_entropy_misses(self) -> None:
        clustered = np.zeros(VIEWPOINTS)
        clustered[[0, 1, 2, 3]] = 0.25
        spread = np.zeros(VIEWPOINTS)
        spread[[0, 2, 5, 7]] = 0.25

        assert gaussian_ild(spread, CATALOGUE, BANDWIDTH) > gaussian_ild(
            clustered, CATALOGUE, BANDWIDTH
        )

    def test_gaussian_ild_cannot_reach_one_which_bars_it_as_a_threshold(self) -> None:
        """Sa borne dépend de k et de la bande : un seuil chiffré n'y serait pas lisible."""
        assert gaussian_ild(_uniform(), CATALOGUE, BANDWIDTH) < 0.8

    def test_a_degenerate_bandwidth_is_refused(self) -> None:
        with pytest.raises(ValueError, match="largeur de bande"):
            gaussian_ild(_uniform(), CATALOGUE, 0.0)

    def test_the_target_divergence_is_one_on_its_own_target(self) -> None:
        assert target_divergence(_uniform(), CATALOGUE, CATALOGUE) == pytest.approx(1.0)

    def test_a_declared_target_changes_the_verdict(self) -> None:
        """C'est l'intérêt de la mesure : la forme visée est déclarée, non supposée."""
        target = np.zeros(VIEWPOINTS)
        target[0] = target[-1] = 0.5

        assert target_divergence(_bimodal(), CATALOGUE, CATALOGUE, target) == pytest.approx(1.0)
        assert target_divergence(_uniform(), CATALOGUE, CATALOGUE, target) < 0.6

    def test_sprinkling_a_crumb_in_every_bin_does_not_buy_compliance(self) -> None:
        """Troisième adversaire : la diversité de façade, une miette partout."""
        crumbs = np.full(VIEWPOINTS, 0.01)
        crumbs[VIEWPOINTS - 2] = 1.0 - 0.01 * (VIEWPOINTS - 1)

        assert position_entropy(crumbs, CATALOGUE, CATALOGUE) < 0.3
        assert gaussian_ild(crumbs, CATALOGUE, BANDWIDTH) < 0.3


class TestShapeDiagnostics:
    def test_the_centre_share_is_zero_on_a_bimodal_feed(self) -> None:
        assert centre_share(_bimodal(), CATALOGUE, CATALOGUE) == pytest.approx(0.0)
        assert centre_share(_uniform(), CATALOGUE, CATALOGUE) > 0.7

    def test_the_largest_gap_is_maximal_on_a_bimodal_feed(self) -> None:
        assert largest_gap(_bimodal(), CATALOGUE, CATALOGUE) == pytest.approx(1.0)

    def test_a_crumb_does_not_fill_a_gap(self) -> None:
        """Sans seuil, saupoudrer une miette effacerait le diagnostic."""
        crumbed = _bimodal() * 0.99
        crumbed[VIEWPOINTS // 2] = 0.01

        assert largest_gap(crumbed, CATALOGUE, CATALOGUE) == pytest.approx(1.0)


class TestGenericOptimiser:
    def test_it_reproduces_the_dedicated_rao_solver(self) -> None:
        generic = optimal_feed_under(
            lambda q, x: rao_entropy(q, x, REFERENCE), VIEWPOINTS, USER, 0.5, width=WIDTH
        )
        dedicated = optimal_feed_under_rao(VIEWPOINTS, USER, floor=0.5, width=WIDTH)

        assert generic.weights == pytest.approx(dedicated.weights)

    def test_it_saturates_the_floor_it_is_given(self) -> None:
        feed = optimal_feed_under(
            lambda q, x: position_entropy(q, x, CATALOGUE), VIEWPOINTS, USER, 0.7, width=WIDTH
        )

        assert feed.position_entropy >= 0.7 - 1e-6

    @pytest.mark.parametrize("floor", [-0.1, 1.5])
    def test_an_impossible_floor_is_refused(self, floor: float) -> None:
        with pytest.raises(ValueError, match="plancher"):
            optimal_feed_under(lambda q, x: 1.0, VIEWPOINTS, USER, floor)
