#!/usr/bin/env python3
"""Récupère les deux journaux publics qui enregistrent le rang servi, et les vérifie.

* **Baidu-ULTR** — une tranche de 0,9 Go, redistribuée par l'université d'Amsterdam pour
  l'étude de reproductibilité de Hager et al. (SIGIR 2024). Licence CC BY-NC 4.0.
* **Open Bandit Dataset** — trois seaux, 2,2 Go au total : la campagne « all » sous politique
  aléatoire, et la paire « men » aléatoire / Bernoulli TS. Licence CC BY 4.0.

Aucun de ces fichiers n'est versionné. Le dépôt ne porte que leur condensé, construit ensuite
par ``scripts/build_exposure_digest.py``.

Usage :

    docker compose run --rm lab python scripts/fetch_exposure.py
    docker compose run --rm lab python scripts/fetch_exposure.py --only baidu
"""

from __future__ import annotations

import argparse
import shutil
import sys
import urllib.request

from ide.exposure import BAIDU_SOURCE, OBD_BUCKETS, OBD_SOURCE, SOURCES, source_path, verify_source


def url_of(name: str) -> str:
    if name == "baidu":
        return BAIDU_SOURCE
    return f"{OBD_SOURCE}/{OBD_BUCKETS[name]}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=sorted(SOURCES), help="ne récupérer qu'un journal")
    parser.add_argument("--force", action="store_true", help="retélécharge un journal déjà là")
    arguments = parser.parse_args()

    names = [arguments.only] if arguments.only else list(SOURCES)
    failed = False

    for name in names:
        destination = source_path(name)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and not arguments.force:
            print(f"{name} : déjà présent ({destination})")
        else:
            url = url_of(name)
            print(f"{name} : téléchargement depuis {url}")
            with urllib.request.urlopen(url, timeout=900) as response:
                with open(destination, "wb") as handle:
                    shutil.copyfileobj(response, handle, 1 << 20)

        conforms, size, digest = verify_source(name)
        print(f"  taille    : {size} octets (attendu {SOURCES[name][1]})")
        print(f"  empreinte : {digest}")
        if conforms:
            print("  vérification : conforme")
        else:
            failed = True
            print("  vérification : NON CONFORME")
            print(f"    empreinte attendue : {SOURCES[name][2]}")
            print("    le miroir a changé — ne rien mesurer sur ce fichier.")

    if failed:
        return 1
    print("\nÉtape suivante : docker compose run --rm lab python scripts/build_exposure_digest.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
