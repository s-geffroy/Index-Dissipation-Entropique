"""Validation du cache et du corpus de calibration.

Aucun test n'accède au réseau. C'est délibéré : une suite de tests qui dépend d'un service
extérieur échoue pour des raisons sans rapport avec le code, et l'accès réseau est confiné
au script de collecte, exécuté une fois et dont le résultat est versionné.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pytest

from ide.corpus import CORPUS, CORPUS_END, CORPUS_START, by_category
from ide.pageviews import (
    CACHE_DIRECTORY,
    DEFAULT_AGENT,
    PageviewSeries,
    load_cached,
    load_or_fetch,
    save_cached,
)


@pytest.fixture
def series() -> PageviewSeries:
    return PageviewSeries(
        project="fr.wikipedia",
        article="Entropie",
        start=date(2020, 1, 1),
        views=np.array([100.0, np.nan, 300.0, 400.0]),
    )


class TestPageviewSeries:
    def test_end_date_follows_the_length(self, series: PageviewSeries) -> None:
        assert series.end == date(2020, 1, 4)

    def test_day_lookup(self, series: PageviewSeries) -> None:
        assert series.day(2) == date(2020, 1, 3)

    def test_out_of_range_day_is_rejected(self, series: PageviewSeries) -> None:
        with pytest.raises(IndexError):
            series.day(99)

    def test_missing_days_are_interpolated_not_zeroed(self, series: PageviewSeries) -> None:
        """Remplacer un jour manquant par zéro créerait un faux effondrement d'attention."""
        filled = series.filled()

        assert filled[1] == pytest.approx(200.0)
        assert not np.isnan(filled).any()

    def test_filled_leaves_complete_series_untouched(self) -> None:
        complete = PageviewSeries(
            project="en.wikipedia",
            article="Entropy",
            start=date(2020, 1, 1),
            views=np.array([1.0, 2.0, 3.0]),
        )

        assert np.array_equal(complete.filled(), [1.0, 2.0, 3.0])

    def test_fully_missing_series_is_rejected(self) -> None:
        empty = PageviewSeries(
            project="en.wikipedia",
            article="Vide",
            start=date(2020, 1, 1),
            views=np.array([np.nan, np.nan]),
        )

        with pytest.raises(ValueError, match="aucune donnée"):
            empty.filled()

    def test_default_agent_excludes_robots(self, series: PageviewSeries) -> None:
        assert series.agent == DEFAULT_AGENT == "user"

    def test_unknown_agent_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="agent"):
            PageviewSeries(
                project="en.wikipedia",
                article="X",
                start=date(2020, 1, 1),
                views=np.array([1.0]),
                agent="bots",
            )


class TestCache:
    def test_round_trip_preserves_the_series(
        self, series: PageviewSeries, tmp_path: Path
    ) -> None:
        save_cached(series, cache_dir=tmp_path)
        restored = load_cached(series.project, series.article, cache_dir=tmp_path)

        assert restored is not None
        assert restored.project == series.project
        assert restored.start == series.start
        assert restored.agent == series.agent
        assert np.array_equal(restored.views, series.views, equal_nan=True)

    def test_absent_series_returns_none(self, tmp_path: Path) -> None:
        assert load_cached("en.wikipedia", "Inexistant", cache_dir=tmp_path) is None

    def test_compressed_by_default(self, series: PageviewSeries, tmp_path: Path) -> None:
        """Le corpus étendu compte plusieurs centaines de séries : la compression divise
        par cinq le poids qu'elles occupent dans le dépôt."""
        path = save_cached(series, cache_dir=tmp_path)

        assert path.suffix == ".gz"

    def test_uncompressed_form_is_still_readable(
        self, series: PageviewSeries, tmp_path: Path
    ) -> None:
        """Les séries du corpus pilote, écrites avant la compression, restent lisibles."""
        save_cached(series, cache_dir=tmp_path, compress=False)
        restored = load_cached(series.project, series.article, cache_dir=tmp_path)

        assert restored is not None
        assert np.array_equal(restored.views, series.views, equal_nan=True)

    def test_compression_shrinks_the_payload(self, tmp_path: Path) -> None:
        long_series = PageviewSeries(
            project="en.wikipedia",
            article="Long",
            start=date(2015, 7, 1),
            views=np.tile(np.arange(100.0, 200.0), 40),
        )

        compressed = save_cached(long_series, cache_dir=tmp_path)
        plain = save_cached(long_series, cache_dir=tmp_path, compress=False)

        assert compressed.stat().st_size < 0.5 * plain.stat().st_size

    def test_missing_cache_refuses_to_reach_the_network_silently(self, tmp_path: Path) -> None:
        """Sans autorisation explicite, un cache incomplet doit échouer de façon lisible."""
        with pytest.raises(FileNotFoundError, match="fetch_pageviews"):
            load_or_fetch(
                "en.wikipedia",
                "Inexistant",
                CORPUS_START,
                CORPUS_END,
                cache_dir=tmp_path,
            )

    def test_agent_mismatch_is_refused(self, series: PageviewSeries, tmp_path: Path) -> None:
        """Comparer des séries filtrées différemment fausserait l'analyse en silence."""
        save_cached(series, cache_dir=tmp_path)

        with pytest.raises(ValueError, match="agent"):
            load_or_fetch(
                series.project,
                series.article,
                CORPUS_START,
                CORPUS_END,
                agent="all-agents",
                cache_dir=tmp_path,
            )


class TestCorpus:
    def test_both_classes_are_populated(self) -> None:
        assert len(by_category("accusation")) >= 10
        assert len(by_category("discovery")) >= 10

    def test_categories_partition_the_corpus(self) -> None:
        assert len(by_category("accusation")) + len(by_category("discovery")) == len(CORPUS)

    def test_entries_are_unique(self) -> None:
        keys = [(entry.project, entry.article) for entry in CORPUS]

        assert len(set(keys)) == len(keys)

    def test_unknown_category_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="catégorie"):
            by_category("neutre")

    def test_every_entry_is_cached(self) -> None:
        """Le corpus pré-enregistré doit être intégralement disponible hors ligne.

        Ce test est ce qui garantit que le notebook 09 reste reproductible : si une série
        disparaissait du cache, l'analyse publiée ne serait plus vérifiable.
        """
        missing = [
            entry.label
            for entry in CORPUS
            if load_cached(entry.project, entry.article) is None
        ]

        assert missing == []
        assert CACHE_DIRECTORY.exists()

    def test_cached_series_cover_the_declared_window(self) -> None:
        for entry in CORPUS:
            cached = load_cached(entry.project, entry.article)
            assert cached is not None, entry.label
            assert cached.start == CORPUS_START, entry.label
            assert cached.agent == DEFAULT_AGENT, entry.label
