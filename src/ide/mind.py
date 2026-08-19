"""L'exploration réellement enregistrée dans MIND, et pourquoi elle n'y est pas.

Ce que cette mesure devait décider
----------------------------------

Le [module contrefactuel](offpolicy.py) a établi qu'évaluer un réordonnancement sur des clics
enregistrés exige de connaître l'exposition qu'avait reçue chaque contenu, donc la
**sévérité** :math:`\\eta` du biais de position. Le [module de rang adverse](ranking.py) a
montré que la poser au lieu de l'estimer coûte jusqu'à **+179 %** sur le chiffre publié, et
que :func:`ide.offpolicy.estimate_position_bias` sait la retrouver — à une condition, que la
plateforme n'ait pas toujours classé les mêmes contenus aux mêmes places.

Cette condition est une propriété du **jeu de données**, pas de la méthode. D'où le préalable
inscrit à la [feuille de route §3.1](../../docs/feuille-de-route.md) : mesurer l'exploration
réelle du jeu de données public avant d'y évaluer quoi que ce soit. MIND (*Microsoft News
Dataset*, Wu et al., ACL 2020) est le jeu de référence de la recommandation d'actualité ;
c'est là que l'évaluation était prévue.

Ce que la mesure trouve
-----------------------

L'ordre enregistré dans ``behaviors.tsv`` **n'est pas l'ordre d'affichage**. La documentation
du jeu le dit d'ailleurs en une ligne — *« the orders of news in a impressions have been
shuffled »* — mais une ligne de documentation ne dit ni ce qu'il en reste, ni ce que la mesure
donne quand on l'ignore. Les deux se mesurent :

* le test d'échangeabilité intra-fil (:func:`exchangeability_test`) ne détecte **aucune**
  dépendance entre position enregistrée et clic, dans un jeu où il détecterait
  :math:`\\eta = 0{,}02` à douze écarts-types ;
* l'ajustement naïf du taux de clic sur la position (:func:`naive_severity_fit`) renvoie
  pourtant :math:`\\hat\\eta \\approx 0{,}39`, une courbe de biais de position d'allure
  parfaitement canonique — qui n'est qu'un effet de composition, les positions élevées
  n'existant que dans les fils longs, dont le taux de clic par contenu est mécaniquement
  plus bas.

.. danger::
    Le mélange ne débiaise pas les clics : il détruit la variable qui permettrait de les
    corriger. Les clics de MIND ont bien été produits sous un ordre d'affichage réel, donc
    sous biais de position ; ce que le mélange a retiré, c'est le **rang**, seul régresseur
    qui aurait permis d'en tenir compte. Un jeu de données mélangé n'est pas un jeu de
    données non biaisé : c'est un jeu de données non corrigible.

Ce que la mesure corrige dans l'outil
-------------------------------------

:func:`ide.offpolicy.estimate_position_bias` accepte MIND sans broncher : son contrôle
d'identifiabilité voit des milliers de contenus servis à des rangs variés et renvoie
``identifiable=True``. Il renvoie même un chiffre confiant — et **trois chiffres
incompatibles** selon le seuil d'impressions retenu, dont un négatif. Le contrôle
d'identifiabilité est donc nécessaire et **non suffisant** : la variation de rang peut être
abondante et artificielle. Le test d'échangeabilité de ce module est le contrôle manquant, et
il doit précéder toute estimation de :math:`\\eta` sur un journal public.

Les mesures elles-mêmes ne sont pas propres à MIND : elles vivent dans :mod:`ide.logs`, et ce
module ne porte plus que la lecture des journaux de MIND et son condensé. Deux journaux qui,
eux, **enregistrent** le rang servi sont mesurés par :mod:`ide.exposure`.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from pathlib import Path

import numpy as np

from ide.logs import (
    DIGEST_MINIMUM_IMPRESSIONS,
    Coverage,
    Digest,
    ExchangeabilityTest,
    Impressions,
    click_rate_by_rank,
    detectable_severity,
    digest_split,
    exchangeability_test,
    naive_severity_fit,
    rank_coverage,
    save_digest,
    simulate_feeds,
)
from ide.logs import load_digest as _load_digest

__all__ = [
    "DIGEST_MINIMUM_IMPRESSIONS",
    "DIGEST_PATH",
    "EXPECTED_SPLITS",
    "MIND_DIRECTORY",
    "MIND_MIRROR",
    "Coverage",
    "Digest",
    "ExchangeabilityTest",
    "Impressions",
    "build_digest",
    "click_rate_by_rank",
    "detectable_severity",
    "exchangeability_test",
    "load_digest",
    "load_split",
    "naive_severity_fit",
    "parse_behaviours",
    "rank_coverage",
    "save_digest",
    "simulate_feeds",
    "split_path",
    "verify_split",
]

#: Répertoire du jeu brut. Il n'est **pas** versionné : MIND est distribué sous licence de
#: recherche Microsoft, et ses journaux pèsent 135 Mo. Seules les empreintes le sont.
MIND_DIRECTORY = Path(__file__).resolve().parents[2] / "data" / "mind"

#: Le lien officiel (``mind201910small.blob.core.windows.net``) répond aujourd'hui *409 Public
#: access is not permitted on this storage account* : le jeu n'est plus téléchargeable à sa
#: source. Ce miroir en tient lieu, et les empreintes ci-dessous sont là pour qu'un miroir
#: soit vérifiable au lieu d'être cru.
MIND_MIRROR = "https://huggingface.co/datasets/huyva/MIND-small/resolve/main"

#: Nombre de fils et empreinte SHA-256 attendus par découpage. Les nombres de fils sont ceux
#: publiés avec MIND-small ; les empreintes sont celles du miroir, relevées à la récupération.
EXPECTED_SPLITS: dict[str, tuple[int, str]] = {
    "train": (
        156_965,
        "a424547c8fa17c9ea4879c2110221c2b2f2709f4f7615ede0b0d8e4765158658",
    ),
    "dev": (
        73_152,
        "b6c460e33b1a8693252ded6e626da7d3ccf78920eea2ec11889020bb7d8443ef",
    ),
}


def split_path(split: str, directory: Path | None = None) -> Path:
    """Chemin attendu du journal d'un découpage."""
    if split not in EXPECTED_SPLITS:
        raise ValueError(f"découpage inconnu : {split!r}")
    base = MIND_DIRECTORY if directory is None else directory
    return base / f"{split}_behaviors.tsv"


def verify_split(path: Path, split: str) -> tuple[bool, int, str]:
    """Vérifie qu'un fichier récupéré est bien le journal attendu.

    Le jeu n'étant plus téléchargeable à sa source officielle, il vient d'un miroir. Un
    miroir se vérifie : le nombre de fils est celui publié avec MIND-small, l'empreinte est
    celle relevée à la récupération.

    Returns:
        Conformité, nombre de fils lus, empreinte SHA-256.
    """
    expected_feeds, expected_digest = EXPECTED_SPLITS[split]
    digest = hashlib.sha256()
    feeds = 0
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
            feeds += chunk.count(b"\n")
    fingerprint = digest.hexdigest()
    return (feeds == expected_feeds and fingerprint == expected_digest, feeds, fingerprint)


def parse_behaviours(path: Path, limit: int | None = None) -> Impressions:
    """Lit un ``behaviors.tsv`` de MIND et le met à plat.

    Le format est celui publié avec le jeu : cinq colonnes séparées par des tabulations, dont
    la cinquième liste les contenus présentés sous la forme ``N12345-1`` (cliqué) ou
    ``N12345-0``. La position dans cette liste est prise pour rang — c'est l'hypothèse que
    :func:`exchangeability_test` met à l'épreuve, non un acquis.

    Args:
        path: chemin du journal.
        limit: nombre de fils à lire, pour un essai rapide. ``None`` les lit tous.

    Returns:
        Le journal mis à plat.
    """
    items: list[int] = []
    ranks: list[int] = []
    clicks: list[int] = []
    feeds: list[int] = []
    lengths: list[int] = []

    with open(path, encoding="utf-8") as handle:
        for feed_index, line in enumerate(handle):
            if limit is not None and feed_index >= limit:
                break
            columns = line.rstrip("\n").split("\t")
            if len(columns) < 5:
                raise ValueError(f"ligne {feed_index + 1} : cinq colonnes attendues")
            served = columns[4].split()
            lengths.append(len(served))
            for rank, token in enumerate(served, start=1):
                identifier, label = token.rsplit("-", 1)
                items.append(int(identifier.lstrip("Nn")))
                ranks.append(rank)
                clicks.append(int(label))
                feeds.append(feed_index)

    return Impressions(
        items=np.asarray(items, dtype=np.int64),
        ranks=np.asarray(ranks, dtype=np.int64),
        clicks=np.asarray(clicks, dtype=float),
        feeds=np.asarray(feeds, dtype=np.int64),
        feed_lengths=np.asarray(lengths, dtype=np.int64),
    )


def load_split(split: str, limit: int | None = None, directory: Path | None = None) -> Impressions:
    """Charge un découpage de MIND-small depuis ``data/mind``.

    Le jeu brut n'est pas versionné ; ``scripts/fetch_mind.py`` le récupère.
    """
    path = split_path(split, directory=directory)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} absent. Récupérer le jeu : "
            "docker compose run --rm lab python scripts/fetch_mind.py"
        )
    return parse_behaviours(path, limit=limit)


#: Le condensé versionné, seul dérivé de MIND que ce dépôt puisse porter. Il suffit à
#: reproduire toutes les mesures publiées, et il se reconstruit depuis le jeu brut par
#: ``scripts/build_mind_digest.py``.
DIGEST_PATH = Path(__file__).resolve().parents[2] / "data" / "mind_digest.npz"


def build_digest(splits: Iterable[str] = ("train", "dev"),
                 directory: Path | None = None) -> Digest:
    """Construit le condensé depuis le jeu brut."""
    sources: dict[str, str] = {}
    tables: dict[str, dict[str, np.ndarray]] = {}

    for split in splits:
        path = split_path(split, directory=directory)
        _, _, digest = verify_split(path, split)
        sources[split] = digest
        tables[split] = digest_split(parse_behaviours(path))

    return Digest(sources=sources, minimum_impressions=DIGEST_MINIMUM_IMPRESSIONS, splits=tables)


def load_digest(path: Path | None = None) -> Digest:
    """Relit le condensé versionné de MIND."""
    return _load_digest(
        DIGEST_PATH if path is None else path,
        rebuild_with="docker compose run --rm lab python scripts/build_mind_digest.py",
    )
