"""La représentation commune d'un journal, et ce que son condensé garantit."""

from __future__ import annotations

import numpy as np
import pytest

from ide.logs import (
    Digest,
    Impressions,
    digest_split,
    exchangeability_test,
    load_digest,
    save_digest,
)


def feed_impressions(ranks_per_feed, clicks_per_feed, items_per_feed):
    lengths = np.asarray([len(ranks) for ranks in ranks_per_feed], dtype=np.int64)
    return Impressions(
        items=np.concatenate(items_per_feed).astype(np.int64),
        ranks=np.concatenate(ranks_per_feed).astype(np.int64),
        clicks=np.concatenate(clicks_per_feed).astype(float),
        feeds=np.repeat(np.arange(lengths.size), lengths),
        feed_lengths=lengths,
    )


def round_trip(impressions, tmp_path):
    digest = Digest(sources={"x": "sha"}, minimum_impressions=1,
                    splits={"x": digest_split(impressions, minimum_impressions=1)})
    return load_digest(save_digest(digest, tmp_path / "d.npz")).impressions("x")


def test_un_journal_canonique_se_resume_a_ses_longueurs(tmp_path):
    impressions = feed_impressions(
        [np.arange(1, 4), np.arange(1, 3)],
        [[0, 1, 0], [1, 0]],
        [[10, 11, 12], [11, 13]],
    )

    arrays = digest_split(impressions, minimum_impressions=1)
    assert "clicked_ranks" in arrays and "served_ranks" not in arrays

    rebuilt = round_trip(impressions, tmp_path)
    assert list(rebuilt.ranks) == list(impressions.ranks)
    assert list(rebuilt.clicks) == list(impressions.clicks)


def test_un_journal_dont_les_rangs_sautent_conserve_ses_rangs(tmp_path):
    """Le défaut que Baidu-ULTR a révélé : une page de résultats peut sauter des rangs.

    Supposer qu'un fil de longueur $L$ occupe les rangs 1 à $L$ produisait alors un condensé
    faux — et faux d'une façon indolore, puisqu'il rendait des chiffres du bon ordre de
    grandeur.
    """
    impressions = feed_impressions(
        [np.asarray([1, 2, 5]), np.asarray([3, 7])],
        [[1, 0, 0], [0, 1]],
        [[10, 11, 12], [11, 13]],
    )

    arrays = digest_split(impressions, minimum_impressions=1)
    assert "served_ranks" in arrays and "clicked_ranks" not in arrays

    rebuilt = round_trip(impressions, tmp_path)
    assert list(rebuilt.ranks) == [1, 2, 5, 3, 7]
    assert list(rebuilt.clicks) == [1, 0, 0, 0, 1]
    assert exchangeability_test(rebuilt).deviation == pytest.approx(
        exchangeability_test(impressions).deviation, nan_ok=True
    )


def test_un_condense_indique_comment_le_reconstruire(tmp_path):
    with pytest.raises(FileNotFoundError, match="reconstruire-moi"):
        load_digest(tmp_path / "absent.npz", rebuild_with="reconstruire-moi")


def test_un_condense_sans_structure_de_fils_le_dit(tmp_path):
    digest = Digest(sources={"x": "sha"}, minimum_impressions=1,
                    splits={"x": {"cell_items": np.asarray([1])}})

    with pytest.raises(ValueError, match="structure des fils"):
        digest.impressions("x")
