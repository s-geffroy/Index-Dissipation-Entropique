#!/usr/bin/env python3
"""Construit le manifeste du corpus étendu depuis les catégories déclarées.

Ce script interroge l'API MediaWiki, énumère les articles des catégories de
:data:`ide.catalogue.REGISTERS`, écarte ceux qui appartiennent aux deux registres, équilibre
les effectifs par empreinte de titre, et écrit ``data/catalogue.json``.

Le manifeste est **versionné** : c'est lui qui constitue le pré-enregistrement du corpus. Il
n'est pas régénéré à chaque analyse, et le relancer alors que les catégories de Wikipédia ont
évolué produirait un corpus différent — donc une autre étude.

Usage :

    docker compose run --rm lab python scripts/build_catalogue.py
    docker compose run --rm lab python scripts/build_catalogue.py --per-register 300 --force
"""

from __future__ import annotations

import argparse
import sys

from ide.catalogue import CATALOGUE_PATH, REGISTERS, build_catalogue, save_catalogue


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--per-register", type=int, default=220, help="effectif retenu par registre"
    )
    parser.add_argument(
        "--force", action="store_true", help="écrase un manifeste déjà présent"
    )
    arguments = parser.parse_args()

    if CATALOGUE_PATH.exists() and not arguments.force:
        print(f"Manifeste déjà présent : {CATALOGUE_PATH}")
        print("Le régénérer changerait le corpus pré-enregistré. Utiliser --force si voulu.")
        return 0

    print(f"{len(REGISTERS)} catégories déclarées. Énumération…\n")
    entries, report = build_catalogue(sources=REGISTERS, per_register=arguments.per_register)

    for category, count in sorted(report["per_category"].items()):
        register = next(s.register for s in REGISTERS if s.category == category)
        print(f"  {register:11s} {category:52s} {count:5d} articles")

    print(f"\n  articles écartés (présents dans les deux registres) : "
          f"{len(report['overlap_discarded'])}")
    print(f"  filtre de substance : au moins {report['min_article_bytes']} octets\n")
    for register in ("accusation", "discovery"):
        available = report["available"][register]
        substantial = report["substantial"][register]
        kept = report["kept"][register]
        print(f"  {register:11s} {available:5d} disponibles → {substantial:5d} substantiels "
              f"→ {kept:4d} retenus")

    path = save_catalogue(entries, report)
    print(f"\nManifeste écrit : {path}  ({len(entries)} sujets)")
    print("Étape suivante : scripts/fetch_pageviews.py --catalogue")

    return 0


if __name__ == "__main__":
    sys.exit(main())
