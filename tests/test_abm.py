"""Validation du modèle à agents « compas politique ».

Trois familles de propriétés sont vérifiées :

* la **reproductibilité** — deux exécutions de même graine doivent être identiques,
  sans quoi aucun résultat du dépôt n'est citable ;
* les **corrections apportées au prototype** du fil — radicalisation progressive au
  lieu d'une téléportation dans les coins, vérification probabiliste, bords
  réfléchissants, et surtout présence d'une température sociale ;
* la **réponse aux leviers de régulation** — l'IDE mesuré doit varier avec le seuil
  de bulle, qui est le paramètre que l'algorithme de recommandation contrôle.
"""

from __future__ import annotations

import numpy as np
import pytest

from ide.abm import (
    Citizen,
    FactChecker,
    MediaOutlet,
    SocietyMetrics,
    SocietyModel,
    SocietyParameters,
    csv_header,
    measure,
    quadrant_label,
)


def _final_state(steps: int = 120, seed: int = 4, **overrides: float) -> SocietyMetrics:
    """Exécute une société et renvoie son dernier instantané."""
    settings: dict[str, float] = {"population": 150, "social_temperature": 0.03, **overrides}

    return SocietyModel(SocietyParameters(**settings), seed=seed).run(steps)[-1]


class TestQuadrants:
    @pytest.mark.parametrize(
        ("opinion", "expected"),
        [
            ((0.4, 0.2), "droite-autoritaire"),
            ((0.4, -0.2), "droite-libertaire"),
            ((-0.4, 0.2), "gauche-autoritaire"),
            ((-0.4, -0.2), "gauche-libertaire"),
        ],
    )
    def test_labels_cover_the_four_quadrants(
        self, opinion: tuple[float, float], expected: str
    ) -> None:
        assert quadrant_label(np.array(opinion)) == expected


class TestCitizen:
    def test_opinion_is_clamped_to_the_compass(self) -> None:
        citizen = Citizen(identifier=0, opinion=np.array([3.0, -2.0]))

        assert np.all(np.abs(citizen.opinion) <= 1.0)

    def test_conformity_never_overshoots_its_target(self) -> None:
        citizen = Citizen(identifier=0, opinion=np.array([0.0, 0.0]))
        citizen.move_towards(np.array([1.0, 1.0]), strength=0.25)

        assert np.allclose(citizen.opinion, [0.25, 0.25])

    def test_infection_radicalises_without_teleporting(self) -> None:
        """Correction du prototype : la contamination déplace, elle ne téléporte pas.

        Le code d'origine plaçait instantanément l'individu dans un coin du compas,
        ce qui supprimait toute dynamique ultérieure.
        """
        citizen = Citizen(identifier=0, opinion=np.array([0.2, -0.3]))
        citizen.infect(radicalisation=0.1)

        assert citizen.infected
        assert citizen.radicalism > 0.0
        # La position a bougé vers le coin, sans l'atteindre.
        assert np.all(np.abs(citizen.opinion) < 1.0)
        assert citizen.opinion[0] > 0.2
        assert citizen.opinion[1] < -0.3

    def test_cure_removes_the_belief_but_not_the_opinion(self) -> None:
        """Le fact-checking corrige une information, il ne convertit pas quelqu'un."""
        citizen = Citizen(identifier=0, opinion=np.array([0.6, 0.6]))
        citizen.infect(radicalisation=0.1)
        position = citizen.opinion.copy()
        citizen.cure()

        assert not citizen.infected
        assert np.array_equal(citizen.opinion, position)

    def test_agitation_reflects_off_the_boundaries(self) -> None:
        """Bords réfléchissants, non absorbants : sinon les agents s'y accumulent.

        Avec une simple troncature, une température élevée piégeait les individus
        dans les coins et faisait chuter l'IDE mesuré — un artefact numérique qui
        contredisait le comportement attendu.
        """
        rng = np.random.default_rng(0)
        citizen = Citizen(identifier=0, opinion=np.array([0.99, -0.99]))

        for _ in range(200):
            citizen.agitate(rng, temperature=0.2)
            assert np.all(np.abs(citizen.opinion) <= 1.0)

        assert np.any(np.abs(citizen.opinion) < 0.99)

    def test_zero_temperature_leaves_the_opinion_untouched(self) -> None:
        rng = np.random.default_rng(0)
        citizen = Citizen(identifier=0, opinion=np.array([0.3, 0.4]))
        citizen.agitate(rng, temperature=0.0)

        assert np.array_equal(citizen.opinion, [0.3, 0.4])

    def test_exposure_window_is_bounded(self) -> None:
        citizen = Citizen(identifier=0, opinion=np.zeros(2), exposure_window=5)
        for _ in range(20):
            citizen.record_exposure("gauche-libertaire")

        assert len(citizen.exposure) == 5


class TestFactChecker:
    def test_cure_requires_proximity(self) -> None:
        rng = np.random.default_rng(0)
        checker = FactChecker(opinion=np.array([0.9, 0.9]), velocity=np.zeros(2), efficacy=1.0)
        distant = Citizen(identifier=0, opinion=np.array([-0.9, -0.9]))
        distant.infect(radicalisation=0.0)

        assert not checker.attempt_cure(distant, rng)
        assert distant.infected

    def test_cure_succeeds_within_reach_at_full_efficacy(self) -> None:
        rng = np.random.default_rng(0)
        checker = FactChecker(opinion=np.array([0.5, 0.5]), velocity=np.zeros(2), efficacy=1.0)
        nearby = Citizen(identifier=0, opinion=np.array([0.52, 0.51]))
        nearby.infect(radicalisation=0.0)

        assert checker.attempt_cure(nearby, rng)
        assert not nearby.infected

    def test_zero_efficacy_never_convinces(self) -> None:
        """L'hypothèse forte du prototype — un démenti convainc toujours — est
        remplacée par une efficacité paramétrable."""
        rng = np.random.default_rng(0)
        checker = FactChecker(opinion=np.array([0.5, 0.5]), velocity=np.zeros(2), efficacy=0.0)
        nearby = Citizen(identifier=0, opinion=np.array([0.5, 0.5]))
        nearby.infect(radicalisation=0.0)

        assert not checker.attempt_cure(nearby, rng)

    def test_patrol_stays_inside_the_compass(self) -> None:
        rng = np.random.default_rng(1)
        checker = FactChecker(opinion=np.array([0.98, -0.98]), velocity=np.array([0.02, -0.02]))

        for _ in range(300):
            checker.patrol(rng)
            assert np.all(np.abs(checker.opinion) <= 1.0)

    def test_invalid_efficacy_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            FactChecker(opinion=np.zeros(2), velocity=np.zeros(2), efficacy=1.5)


class TestMediaOutlet:
    def test_influence_is_limited_by_reach(self) -> None:
        outlet = MediaOutlet("test", np.array([0.8, 0.8]), reach=0.3)
        nearby = Citizen(identifier=0, opinion=np.array([0.7, 0.7]))
        distant = Citizen(identifier=1, opinion=np.array([0.0, 0.0]))

        assert outlet.influences(nearby)
        assert not outlet.influences(distant)


class TestMetrics:
    def test_header_matches_the_row(self) -> None:
        metrics = measure([Citizen(identifier=0, opinion=np.zeros(2))], step=1)

        assert len(csv_header()) == len(metrics.as_row())
        assert csv_header()[0] == "step"

    def test_empty_population_returns_zeros(self) -> None:
        metrics = measure([], step=7)

        assert metrics.step == 7
        assert metrics.polarisation == 0.0
        assert metrics.exposure_index == 0.0

    def test_polarisation_is_a_percentage_of_the_maximum(self) -> None:
        corner = Citizen(identifier=0, opinion=np.array([1.0, 1.0]))
        centre = Citizen(identifier=1, opinion=np.zeros(2))

        assert measure([corner], step=0).polarisation == pytest.approx(100.0)
        assert measure([centre], step=0).polarisation == pytest.approx(0.0)

    def test_exposure_index_reflects_what_an_individual_sees(self) -> None:
        blinkered = Citizen(identifier=0, opinion=np.zeros(2))
        open_minded = Citizen(identifier=1, opinion=np.zeros(2))
        for _ in range(8):
            blinkered.record_exposure("gauche-libertaire")
        for label in ("gauche-libertaire", "droite-autoritaire", "gauche-autoritaire",
                      "droite-libertaire") * 2:
            open_minded.record_exposure(label)

        assert measure([blinkered], step=0).exposure_index == 0.0
        assert measure([open_minded], step=0).exposure_index == pytest.approx(1.0)


class TestSocietyModel:
    def test_same_seed_gives_identical_histories(self) -> None:
        first = SocietyModel(SocietyParameters(population=80), seed=11).run(40)
        second = SocietyModel(SocietyParameters(population=80), seed=11).run(40)

        assert first == second

    def test_different_seeds_diverge(self) -> None:
        first = SocietyModel(SocietyParameters(population=80), seed=1).run(40)
        second = SocietyModel(SocietyParameters(population=80), seed=2).run(40)

        assert first != second

    def test_history_length_matches_the_request(self) -> None:
        history = SocietyModel(SocietyParameters(population=40), seed=0).run(25)

        assert len(history) == 25
        assert [record.step for record in history] == list(range(1, 26))

    def test_metrics_stay_within_their_bounds(self) -> None:
        history = SocietyModel(SocietyParameters(population=60), seed=3).run(50)

        for record in history:
            assert 0.0 <= record.exposure_index <= 1.0
            assert 0.0 <= record.polarisation <= 100.0
            assert 0.0 <= record.infected_fraction <= 1.0
            assert 0.0 <= record.frozen_fraction <= 1.0

    def test_scheduled_injection_contaminates_the_population(self) -> None:
        """Propagation isolée : sans vérificateurs, la contagion doit prendre.

        Les fact-checkers sont désactivés à dessein — avec la configuration par
        défaut ils éteignent souvent les trois contaminations initiales avant
        qu'elles ne se diffusent, et le test mesurerait alors leur efficacité
        plutôt que le mécanisme d'injection.
        """
        model = SocietyModel(
            SocietyParameters(population=120, fake_news_probability=0.05, fact_checkers=0),
            seed=6,
        )
        history = model.run(60, inject_at={10: 3})

        assert history[8].infected_fraction == 0.0
        assert history[-1].infected_fraction > 0.0

    def test_opinion_cloud_has_one_row_per_citizen(self) -> None:
        model = SocietyModel(SocietyParameters(population=30), seed=0)

        assert model.opinion_cloud().shape == (30, 2)

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"population": 1},
            {"bubble_threshold": 0.0},
            {"social_temperature": -0.1},
            {"fake_news_probability": 1.5},
            {"interactions_per_step": 0},
        ],
    )
    def test_invalid_parameters_are_rejected(self, kwargs: dict[str, float]) -> None:
        with pytest.raises(ValueError):
            SocietyParameters(**kwargs)


class TestRegulationLevers:
    @pytest.mark.slow
    def test_narrow_bubbles_collapse_the_exposure_index(self) -> None:
        """Le levier central : resserrer le filtre effondre l'IDE des individus.

        C'est ce que le mémorandum propose de rendre constatable — la plateforme
        contrôle ce seuil, et l'index en dépend de façon mesurable.
        """
        narrow = _final_state(bubble_threshold=0.1)
        wide = _final_state(bubble_threshold=0.8)

        assert narrow.exposure_index < 0.5 < wide.exposure_index
        assert narrow.frozen_fraction > wide.frozen_fraction

    @pytest.mark.slow
    def test_narrow_bubbles_radicalise_the_population(self) -> None:
        """Corollaire : le compartimentage maintient les blocs éloignés du centre."""
        narrow = _final_state(bubble_threshold=0.1)
        wide = _final_state(bubble_threshold=0.8)

        assert narrow.polarisation > wide.polarisation

    @pytest.mark.slow
    def test_zero_temperature_freezes_the_whole_society(self) -> None:
        """Sans agitation, le conformisme fige tout le monde : IDE nul, gel total.

        C'est la raison d'être du paramètre de température, absent du prototype.
        """
        frozen = _final_state(social_temperature=0.0, bubble_threshold=0.3)

        assert frozen.exposure_index == 0.0
        assert frozen.frozen_fraction == 1.0

    @pytest.mark.slow
    def test_a_little_noise_is_what_restores_diversity(self) -> None:
        """Un bruit modéré maximise l'IDE ; un bruit excessif le dégrade à nouveau.

        Ce résultat conforte l'argument du recuit simulé formulé dans la note :
        injecter du bruit en permanence rend la société « chaotique et illisible ».
        Ce n'est donc pas la quantité de bruit qui compte, mais son dosage.
        """
        indices = {
            temperature: _final_state(
                social_temperature=temperature, bubble_threshold=0.3
            ).exposure_index
            for temperature in (0.0, 0.01, 0.15)
        }

        assert indices[0.01] > indices[0.0]
        assert indices[0.01] > indices[0.15]

    @pytest.mark.slow
    def test_more_fact_checkers_reduce_contamination(self) -> None:
        """La vérification reste efficace, mais son rendement est décroissant."""
        contaminations = []
        for checkers in (0, 20):
            history = SocietyModel(
                SocietyParameters(
                    population=150,
                    bubble_threshold=0.3,
                    social_temperature=0.02,
                    fake_news_probability=0.05,
                    fact_checkers=checkers,
                ),
                seed=6,
            ).run(120, inject_at={10: 3})
            contaminations.append(history[-1].infected_fraction)

        assert contaminations[1] < contaminations[0]
