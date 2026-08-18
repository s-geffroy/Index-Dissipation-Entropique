#!/usr/bin/env python3
"""Récupère les journaux d'impressions de MIND-small, et vérifie qu'ils sont les bons.

Le jeu n'est plus téléchargeable à sa source officielle — ``mind201910small.blob.core.
windows.net`` répond *409 Public access is not permitted on this storage account*. Ce script
passe donc par un miroir, et **vérifie** ce qu'il en reçoit : nombre de fils publié avec
MIND-small, empreinte SHA-256 relevée à la première récupération.

Le jeu brut n'est pas versionné (licence de recherche Microsoft, 135 Mo). Seules les
empreintes le sont, dans :mod:`ide.mind`.

Usage :

    docker compose run --rm lab python scripts/fetch_mind.py
    docker compose run --rm lab python scripts/fetch_mind.py --force
"""

from __future__ import annotations

import argparse
import shutil
import sys
import urllib.request

from ide.mind import EXPECTED_SPLITS, MIND_DIRECTORY, MIND_MIRROR, split_path, verify_split


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="retélécharge un journal déjà là")
    arguments = parser.parse_args()

    MIND_DIRECTORY.mkdir(parents=True, exist_ok=True)
    failed = False

    for split, (expected_feeds, expected_digest) in EXPECTED_SPLITS.items():
        destination = split_path(split)
        if destination.exists() and not arguments.force:
            print(f"{split} : déjà présent ({destination})")
        else:
            url = f"{MIND_MIRROR}/{split}/behaviors.tsv"
            print(f"{split} : téléchargement depuis {url}")
            with urllib.request.urlopen(url, timeout=300) as response:
                with open(destination, "wb") as handle:
                    shutil.copyfileobj(response, handle)

        conforms, feeds, digest = verify_split(destination, split)
        print(f"  fils lus      : {feeds} (attendu {expected_feeds})")
        print(f"  empreinte     : {digest}")
        if conforms:
            print("  vérification  : conforme")
        else:
            failed = True
            print("  vérification  : NON CONFORME")
            print(f"    empreinte attendue : {expected_digest}")
            print("    le miroir a changé — ne rien mesurer sur ce fichier.")

    if failed:
        return 1
    print("\nÉtape suivante : notebook 16 — l'exploration réellement enregistrée.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
