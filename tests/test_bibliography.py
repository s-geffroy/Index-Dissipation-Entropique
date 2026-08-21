"""La bibliographie publiée doit être celle que compilent les notes, sans dérive possible."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_bibliography.py"

specification = importlib.util.spec_from_file_location("build_bibliography", SCRIPT)
bibliography = importlib.util.module_from_spec(specification)
sys.modules["build_bibliography"] = bibliography
specification.loader.exec_module(bibliography)


def test_les_pages_publiees_correspondent_au_fichier_bibtex():
    """Le verrou : modifier ``refs.bib`` sans régénérer les pages fait échouer la suite.

    C'est la seule garantie qu'une bibliographie publiée ne mente pas sur ce que citent
    réellement les notes.
    """
    for path, expected in bibliography.build().items():
        assert path.exists(), f"{path.name} n'a pas été généré"
        assert path.read_text(encoding="utf-8") == expected, (
            f"{path.name} diverge de refs.bib — régénérer avec "
            "docker compose run --rm lab python scripts/build_bibliography.py"
        )


def test_chaque_reference_declare_ce_quelle_sert():
    entries = bibliography.parse_bib(bibliography.BIB_PATH.read_text(encoding="utf-8"))

    assert set(entries) == set(bibliography.USES), (
        "toute référence doit déclarer son usage, et tout usage déclaré doit exister"
    )
    for key, (french, english) in bibliography.USES.items():
        assert french.strip() and english.strip(), key


def test_chaque_reference_est_classee_dans_un_theme():
    entries = bibliography.parse_bib(bibliography.BIB_PATH.read_text(encoding="utf-8"))
    classified = {key for keys, _, _ in bibliography.THEMES for key in keys}

    assert classified == set(entries)


def test_une_reference_absente_du_fichier_est_signalee():
    entries = bibliography.parse_bib(bibliography.BIB_PATH.read_text(encoding="utf-8"))
    entries.pop("shannon1948")

    with pytest.raises(KeyError, match="référence absente"):
        bibliography.render(entries, "fr")


def test_les_liens_publies_sont_des_adresses_completes():
    for key, link in bibliography.LINKS.items():
        assert link.startswith("https://"), key
        assert " " not in link, key
