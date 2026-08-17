#!/usr/bin/env python3
"""Constitue le cache local des séries de consultation du corpus pré-enregistré.

Ce script est le **seul** point du dépôt qui accède au réseau. Il est exécuté une fois,
son résultat est versionné sous ``data/pageviews/``, et l'analyse du notebook 09 s'appuie
ensuite exclusivement sur ce cache. Un résultat publié ne dépend donc pas de la
disponibilité future d'un service tiers.

Usage :

    docker compose run --rm lab python scripts/fetch_pageviews.py
    docker compose run --rm lab python scripts/fetch_pageviews.py --force
"""

from __future__ import annotations

import argparse
import sys
import time

import numpy as np

from ide.corpus import CORPUS, CORPUS_END, CORPUS_START
from ide.pageviews import fetch_pageviews, load_cached, save_cached

# L'API de Wikimedia limite le débit des requêtes anonymes ; un intervalle d'une seconde
# suffit à ne jamais recevoir de code 429 sur un corpus de cette taille.
_DELAY_SECONDS = 1.2
_MAX_ATTEMPTS = 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="retélécharge les séries déjà présentes dans le cache",
    )
    arguments = parser.parse_args()

    fetched, skipped, failed = 0, 0, []

    for entry in CORPUS:
        if not arguments.force and load_cached(entry.project, entry.article) is not None:
            print(f"  déjà en cache  {entry.project}/{entry.article}")
            skipped += 1
            continue

        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                series = fetch_pageviews(
                    entry.project, entry.article, CORPUS_START, CORPUS_END
                )
            except (RuntimeError, ValueError) as error:
                if attempt == _MAX_ATTEMPTS:
                    print(f"  ÉCHEC          {entry.project}/{entry.article} : {error}")
                    failed.append(entry.label)
                else:
                    # Un échec est le plus souvent une limitation de débit : on attend
                    # plus longtemps à chaque tentative.
                    time.sleep(_DELAY_SECONDS * 4 * attempt)
                continue

            save_cached(series)
            observed = int((~np.isnan(series.views)).sum())
            print(
                f"  téléchargé     {entry.project}/{entry.article} "
                f"— {observed} jours observés"
            )
            fetched += 1
            break

        time.sleep(_DELAY_SECONDS)

    print(f"\n{fetched} téléchargées, {skipped} déjà en cache, {len(failed)} en échec")
    if failed:
        print("En échec : " + ", ".join(failed))
        print(
            "Ces sujets restent dans le corpus pré-enregistré et sont rapportés comme "
            "non exploitables dans l'analyse."
        )

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
