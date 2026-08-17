"""Validation du corpus étendu dérivé de catégories.

Aucun test n'accède au réseau : la construction du manifeste est un acte unique, dont le
résultat est versionné. Ce qui est testé ici, c'est la **mécanique de sélection** — car c'est
elle qui décide de la validité de la comparaison entre registres, et une erreur y serait
invisible dans une liste de plusieurs centaines de titres.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ide.catalogue import (
    CATALOGUE_PATH,
    MIN_ARTICLE_BYTES,
    REGISTERS,
    CategorySource,
    _fingerprint,
    _to_entry,
    load_catalogue,
    save_catalogue,
)
from ide.corpus import CorpusEntry
from ide.pageviews import load_cached


class TestCategorySource:
    def test_requires_the_category_prefix(self) -> None:
        with pytest.raises(ValueError, match="Category:"):
            CategorySource("Conspiracy theories", "accusation")

    def test_rejects_an_unknown_register(self) -> None:
        with pytest.raises(ValueError, match="registre"):
            CategorySource("Category:X", "neutre")

    @pytest.mark.parametrize("depth", [-1, 3])
    def test_rejects_excessive_depth(self, depth: int) -> None:
        """Au-delà de deux niveaux, l'arborescence de Wikipédia dérive hors sujet."""
        with pytest.raises(ValueError, match="profondeur"):
            CategorySource("Category:X", "accusation", depth=depth)


class TestDeclaredRegisters:
    def test_both_registers_are_declared(self) -> None:
        registers = {source.register for source in REGISTERS}

        assert registers == {"accusation", "discovery"}

    def test_each_register_draws_on_several_categories(self) -> None:
        """Une seule catégorie par registre ferait dépendre le résultat d'un choix unique."""
        for register in ("accusation", "discovery"):
            count = sum(1 for source in REGISTERS if source.register == register)
            assert count >= 5, register

    def test_no_category_is_declared_twice(self) -> None:
        titles = [source.category for source in REGISTERS]

        assert len(set(titles)) == len(titles)


class TestTitleConversion:
    def test_spaces_become_underscores(self) -> None:
        entry = _to_entry("Panama Papers", "accusation")

        assert entry.article == "Panama_Papers"
        assert entry.label == "Panama Papers"

    def test_accents_are_percent_encoded(self) -> None:
        entry = _to_entry("Affaire Élysée", "accusation")

        assert "%" in entry.article
        assert " " not in entry.article

    def test_parentheses_are_preserved(self) -> None:
        """L'API de consultations accepte les parenthèses telles quelles."""
        entry = _to_entry("Pegasus (spyware)", "accusation")

        assert entry.article == "Pegasus_(spyware)"


class TestFingerprintSampling:
    def test_is_deterministic(self) -> None:
        assert _fingerprint("QAnon") == _fingerprint("QAnon")

    def test_differs_between_titles(self) -> None:
        assert _fingerprint("QAnon") != _fingerprint("Pizzagate")

    def test_ordering_is_not_alphabetical(self) -> None:
        """Le motif du tirage par empreinte : une troncature alphabétique surreprésenterait
        les premières lettres, donc certains sujets — les listes, les articles en « A » — de
        façon systématique et différente d'un registre à l'autre."""
        titles = [f"Article {letter}" for letter in "ABCDEFGHIJKLMNOP"]
        by_fingerprint = sorted(titles, key=_fingerprint)

        assert by_fingerprint != sorted(titles)

    def test_truncation_keeps_a_stable_subset(self) -> None:
        titles = [f"Sujet {index:03d}" for index in range(200)]

        first = sorted(titles, key=_fingerprint)[:50]
        second = sorted(titles, key=_fingerprint)[:50]

        assert first == second


class TestManifest:
    def test_round_trip(self, tmp_path: Path) -> None:
        entries = [
            CorpusEntry("en.wikipedia", "QAnon", "QAnon", "accusation"),
            CorpusEntry("en.wikipedia", "LIGO", "LIGO", "discovery"),
        ]
        report = {"available": {"accusation": 10, "discovery": 12}}

        path = save_catalogue(entries, report, path=tmp_path / "catalogue.json")
        restored, restored_report = load_catalogue(path=path)

        assert restored == entries
        assert restored_report["available"]["accusation"] == 10

    def test_absent_manifest_is_not_rebuilt_silently(self, tmp_path: Path) -> None:
        """Un corpus qui se régénérerait à chaque exécution ne serait pas pré-enregistré."""
        with pytest.raises(FileNotFoundError, match="build_catalogue"):
            load_catalogue(path=tmp_path / "absent.json")

    def test_manifest_records_its_own_construction(self, tmp_path: Path) -> None:
        path = save_catalogue([], {"kept": {"accusation": 0}}, path=tmp_path / "c.json")
        payload = json.loads(path.read_text())

        assert len(payload["sources"]) == len(REGISTERS)
        assert "report" in payload


class TestVersionedCatalogue:
    """Contrôles sur le manifeste effectivement versionné dans le dépôt."""

    def test_manifest_exists(self) -> None:
        assert CATALOGUE_PATH.exists(), "construire avec scripts/build_catalogue.py"

    def test_registers_are_balanced(self) -> None:
        """Des effectifs déséquilibrés affaibliraient la comparaison sans la rendre fausse ;
        l'équilibre est obtenu par troncature, il doit donc être exact."""
        entries, _ = load_catalogue()
        counts = {
            register: sum(1 for entry in entries if entry.category == register)
            for register in ("accusation", "discovery")
        }

        assert counts["accusation"] == counts["discovery"]
        assert counts["accusation"] >= 200

    def test_entries_are_unique(self) -> None:
        entries, _ = load_catalogue()
        keys = [(entry.project, entry.article) for entry in entries]

        assert len(set(keys)) == len(keys)

    def test_registers_are_disjoint(self) -> None:
        """Un article des deux registres est écarté, non arbitré."""
        entries, _ = load_catalogue()
        by_register = {
            register: {entry.label for entry in entries if entry.category == register}
            for register in ("accusation", "discovery")
        }

        assert by_register["accusation"] & by_register["discovery"] == set()

    def test_report_documents_the_truncation(self) -> None:
        """Sans le rapport, on ne saurait pas combien de sujets ont été laissés de côté."""
        _, report = load_catalogue()

        assert report["min_article_bytes"] == MIN_ARTICLE_BYTES
        for register in ("accusation", "discovery"):
            assert report["available"][register] > report["substantial"][register]
            assert report["substantial"][register] > report["kept"][register]

    @pytest.mark.slow
    def test_every_subject_is_cached(self) -> None:
        """Le corpus étendu doit être intégralement disponible hors ligne, comme le pilote."""
        entries, _ = load_catalogue()
        missing = [
            entry.label
            for entry in entries
            if load_cached(entry.project, entry.article) is None
        ]

        assert missing == [], f"{len(missing)} séries absentes du cache"
