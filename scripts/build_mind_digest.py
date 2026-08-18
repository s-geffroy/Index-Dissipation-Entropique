#!/usr/bin/env python3
"""Réduit MIND-small au condensé versionnable, seul dérivé que ce dépôt puisse porter.

Le jeu brut est sous licence de recherche Microsoft et pèse 135 Mo : il n'est pas versionné.
Le condensé retient la structure d'ordre des fils et les cellules (contenu, rang)
suffisamment observées — de quoi reproduire à l'identique toutes les mesures publiées, et
rien de plus. L'empreinte du journal source est inscrite dedans.

Usage :

    docker compose run --rm lab python scripts/fetch_mind.py
    docker compose run --rm lab python scripts/build_mind_digest.py
"""

from __future__ import annotations

import argparse
import sys

from ide.mind import DIGEST_PATH, build_digest, save_digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="écrase un condensé déjà présent")
    arguments = parser.parse_args()

    if DIGEST_PATH.exists() and not arguments.force:
        print(f"Condensé déjà présent : {DIGEST_PATH}")
        print("Utiliser --force pour le reconstruire.")
        return 0

    digest = build_digest()
    for split, source in digest.sources.items():
        arrays = digest.splits[split]
        print(f"{split} :")
        print(f"  source (SHA-256)   : {source}")
        print(f"  fils               : {arrays['feed_lengths'].size}")
        print(f"  clics              : {arrays['clicked_ranks'].size}")
        print(f"  cellules retenues  : {arrays['cell_items'].size} "
              f"(≥ {digest.minimum_impressions} impressions)")

    path = save_digest(digest)
    print(f"\nÉcrit : {path} ({path.stat().st_size / 1e6:.1f} Mo)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
