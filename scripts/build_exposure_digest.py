#!/usr/bin/env python3
"""Réduit les deux journaux au condensé versionnable.

Les fichiers bruts pèsent 3,1 Go et portent deux licences distinctes : ils ne sont pas
versionnés. Le condensé retient la structure d'ordre des sessions de Baidu-ULTR et les
cellules (contenu, position, propension) de l'Open Bandit Dataset — de quoi reproduire à
l'identique toutes les mesures publiées, et rien de plus.

Usage :

    docker compose run --rm lab python scripts/fetch_exposure.py
    docker compose run --rm lab python scripts/build_exposure_digest.py
"""

from __future__ import annotations

import argparse
import sys

from ide.exposure import DIGEST_PATH, build_digest
from ide.logs import save_digest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="écrase un condensé déjà présent")
    arguments = parser.parse_args()

    if DIGEST_PATH.exists() and not arguments.force:
        print(f"Condensé déjà présent : {DIGEST_PATH}")
        print("Utiliser --force pour le reconstruire.")
        return 0

    digest = build_digest()
    for name, source in digest.sources.items():
        arrays = digest.splits[name]
        print(f"{name} :")
        print(f"  source (SHA-256)  : {source}")
        if "feed_lengths" in arrays:
            clicks = arrays["clicked_rows"] if "clicked_rows" in arrays else arrays["clicked_ranks"]
            structure = "rangs servis conservés" if "served_ranks" in arrays else "fils canoniques"
            print(f"  sessions          : {arrays['feed_lengths'].size}  ({structure})")
            print(f"  clics             : {clicks.size}")
        print(f"  cellules retenues : {arrays['cell_items'].size}")

    path = save_digest(digest, DIGEST_PATH)
    print(f"\nÉcrit : {path} ({path.stat().st_size / 1e6:.1f} Mo)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
