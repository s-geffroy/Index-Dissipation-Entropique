#!/usr/bin/env python3
"""Fige le chapeau des articles du catalogue, entrée unique de l'annotation manuelle.

Ce script ne lit **aucune** série de consultations. C'est sa raison d'être : il produit le
seul matériau que l'annotateur est censé voir, et son résultat est figé dans
``data/extracts.json`` avec une empreinte, de sorte qu'on sache après coup ce qui a été lu.

Usage :

    docker compose run --rm lab python scripts/fetch_extracts.py
    docker compose run --rm lab python scripts/fetch_extracts.py --force
"""

from __future__ import annotations

import argparse
import sys

from ide.annotation import (
    EXTRACT_CHARS,
    EXTRACTS_PATH,
    digest_extracts,
    fetch_extracts,
    save_extracts,
)
from ide.catalogue import load_catalogue


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force", action="store_true", help="écrase des chapeaux déjà figés"
    )
    arguments = parser.parse_args()

    if EXTRACTS_PATH.exists() and not arguments.force:
        print(f"Chapeaux déjà figés : {EXTRACTS_PATH}")
        print("Les régénérer changerait le matériau d'annotation. Utiliser --force si voulu.")
        return 0

    entries, _ = load_catalogue()
    titles = [entry.label for entry in entries]
    print(f"{len(titles)} sujets au catalogue. Récupération des chapeaux "
          f"({EXTRACT_CHARS} caractères)…\n")

    extracts = fetch_extracts(titles)
    missing = [title for title in titles if title not in extracts]

    path = save_extracts(extracts)
    print(f"  chapeaux obtenus : {len(extracts)}/{len(titles)}")
    if missing:
        print(f"  sans chapeau exploitable : {len(missing)}")
        for title in missing[:10]:
            print(f"    · {title}")
        if len(missing) > 10:
            print(f"    … et {len(missing) - 10} autres")

    print(f"\nÉcrit : {path}")
    print(f"Empreinte SHA-256 : {digest_extracts()}")
    print("Étape suivante : annotation manuelle → data/annotations.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
