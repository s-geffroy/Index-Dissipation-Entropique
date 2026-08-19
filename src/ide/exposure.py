"""Deux journaux publics qui enregistrent ce que MIND avait effacé.

Ce que ce module cherchait
--------------------------

La mesure sur [MIND](mind.py) a conclu par une exigence : il faut un jeu de données qui
**enregistre le rang servi**, faute de quoi l'exposition n'est pas identifiable et
l'évaluation contrefactuelle d'un réordonnancement est vide. Ce module va chercher ces
journaux-là, et les soumet aux mêmes contrôles.

Deux répondent, et pas à la même exigence.

**Baidu-ULTR** (Zou et al., 2022) enregistre le **rang d'affichage** de chaque document dans
une page de résultats, avec le clic et la session. C'est la structure que MIND avait détruite :
des fils ordonnés, groupés, dont l'ordre est celui que le lecteur a vu. Le test
d'échangeabilité y rejette à :math:`z = -206`, du bon côté, et la sévérité :math:`\\eta` s'y
estime autour de 1,1.

**L'Open Bandit Dataset** (Saito et al., 2020) ne publie pas seulement la position : il publie
la **propension vraie** de chaque affichage, et il contient un seau où la politique de service
est **uniformément aléatoire**. C'est le seul jeu où la condition la plus coûteuse des
estimateurs contrefactuels — connaître :math:`\\pi_0` au lieu de la modéliser — est satisfaite
littéralement, et où la valeur d'une politique non déployée peut être **vérifiée** contre une
mesure directe.

Ce que la vérification donne
----------------------------

Sur l'Open Bandit Dataset, l'estimation IPS de la valeur de la politique uniforme, calculée sur
les seules données d'une politique **différente**, tombe à 2,5 % de la valeur mesurée
directement dans le seau aléatoire — là où l'estimation naïve se trompe de 32 %.

.. warning::
    Le même calcul livre la raison de ne pas s'en réjouir : la **taille d'échantillon
    effective** vaut 1 513 pour 4 077 727 impressions, soit 0,04 %. L'estimation est sans biais
    et repose sur l'équivalent de mille cinq cents observations. C'est exactement le diagnostic
    que :mod:`ide.offpolicy` impose de publier à côté du chiffre, et voici le cas réel qui
    montre pourquoi : sans lui, on croirait tenir une mesure sur quatre millions de lignes.

Et la sévérité n'est pas une constante universelle
--------------------------------------------------

Les deux jeux ne donnent pas la même. Une page de résultats de recherche décroît en
:math:`R^{-1{,}1}` ; un bandeau horizontal de trois vignettes décroît en :math:`R^{-0{,}1}`,
et la différence entre la première et la troisième vignette y tient dans deux écarts-types.

:math:`\\eta` est donc une propriété de la **surface**, pas du genre humain. Poser la valeur
d'un fil vertical sur un bandeau horizontal se trompe d'un ordre de grandeur, ce qui est
précisément l'ampleur d'erreur que le [rang adverse](ranking.py) avait chiffrée.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from ide.logs import (
    DIGEST_MINIMUM_IMPRESSIONS,
    Digest,
    Impressions,
    digest_split,
)
from ide.logs import (
    load_digest as _load_digest,
)
from ide.offpolicy import clipped_ips, effective_sample_size, ips, snips

__all__ = [
    "BAIDU_SOURCE",
    "DIGEST_PATH",
    "EXPOSURE_DIRECTORY",
    "OBD_BUCKETS",
    "OBD_SOURCE",
    "SOURCES",
    "OffPolicyCheck",
    "bucket_from_digest",
    "build_digest",
    "load_baidu_part",
    "load_digest",
    "load_obd_bucket",
    "obd_cells",
    "obd_click_rates",
    "off_policy_check",
    "source_path",
    "verify_source",
]

#: Les journaux bruts. Ils ne sont **pas** versionnés : 2,2 Go pour l'Open Bandit Dataset,
#: 0,9 Go pour la tranche de Baidu-ULTR, et deux licences distinctes.
EXPOSURE_DIRECTORY = Path(__file__).resolve().parents[2] / "data"

#: Baidu-ULTR, tranche redistribuée par l'université d'Amsterdam pour l'étude de
#: reproductibilité de Hager et al. (SIGIR 2024). Licence CC BY-NC 4.0.
BAIDU_SOURCE = (
    "https://huggingface.co/datasets/philipphager/baidu-ultr_uva-mlm-ctr/resolve/main/"
    "parts/part-0_split-0.feather"
)

#: Open Bandit Dataset, campagne et politique par fichier. Licence CC BY 4.0.
OBD_SOURCE = "https://huggingface.co/datasets/zozonext/open-bandit/resolve/main"

#: Les trois seaux employés : la campagne « all » sous politique aléatoire, qui donne la mesure
#: causale de l'effet de position, et la paire « men » — aléatoire et Bernoulli TS — sans
#: laquelle une estimation contrefactuelle n'aurait rien à quoi se comparer.
OBD_BUCKETS: dict[str, str] = {
    "obd_random_all": "random/all/all.csv",
    "obd_random_men": "random/men/men.csv",
    "obd_bts_men": "bts/men/men.csv",
}

#: Taille et empreinte SHA-256 attendues de chaque fichier, relevées à la récupération. Un
#: miroir se vérifie plutôt qu'il ne se croit.
SOURCES: dict[str, tuple[str, int, str]] = {
    "baidu": (
        "baidu/part-0_split-0.feather",
        932_578_418,
        "3ffee6ef4c644e30168eed8c6533a4346c604a63b5bd89c4ef85fe075726066b",
    ),
    "obd_random_all": (
        "obd/random_all_all.csv",
        695_501_426,
        "f24fdf91e38de41dcd15f2482279358766556be04155b35882e327b465d104b7",
    ),
    "obd_random_men": (
        "obd/random_men_men.csv",
        151_946_449,
        "c4b6f65e62bf2c683914703ab6b875cc3e1b4ef0403a5779f548f5578cc34d6d",
    ),
    "obd_bts_men": (
        "obd/bts_men_men.csv",
        1_332_891_122,
        "f116bb11bd0b18f02ca69d313c790c63c006728b3fae28a562d7309e20a0e4b5",
    ),
}

#: Le condensé versionné des deux journaux.
DIGEST_PATH = EXPOSURE_DIRECTORY / "exposure_digest.npz"


@dataclass(frozen=True)
class OffPolicyCheck:
    """Une estimation contrefactuelle **confrontée à la valeur qu'elle prétend estimer**.

    C'est le seul endroit de ce dépôt où la confrontation est possible : elle exige un jeu qui
    publie ses propensions et qui contient, en parallèle, un seau servi par la politique
    qu'on cherche à évaluer.

    Attributes:
        truth: valeur de la politique cible, **mesurée directement** dans le seau aléatoire.
        truth_error: son erreur type binomiale.
        naive: taux de clic observé sous la politique d'enregistrement. C'est ce que
            mesurerait une évaluation par *replay*, et ce n'est pas la même politique.
        importance_sampling: estimation IPS depuis le seul seau d'enregistrement.
        self_normalised: estimation SNIPS.
        clipped: estimations à poids plafonnés, par plafond.
        effective_size: nombre d'observations dont l'estimation IPS a réellement la précision.
        logged_size: nombre d'impressions employées.
    """

    truth: float
    truth_error: float
    naive: float
    importance_sampling: float
    self_normalised: float
    clipped: dict[float, float]
    effective_size: float
    logged_size: int

    def relative_error(self, estimate: float) -> float:
        """Écart relatif d'une estimation à la valeur mesurée directement."""
        return estimate / self.truth - 1.0

    @property
    def effective_share(self) -> float:
        """Part des impressions qui porte réellement l'estimation."""
        return self.effective_size / self.logged_size


def verify_source(name: str, directory: Path | None = None) -> tuple[bool, int, str]:
    """Vérifie taille et empreinte d'un journal récupéré.

    Returns:
        Conformité, taille lue, empreinte SHA-256.
    """
    if name not in SOURCES:
        raise ValueError(f"journal inconnu : {name!r}")
    relative, expected_size, expected_digest = SOURCES[name]
    base = EXPOSURE_DIRECTORY if directory is None else directory
    path = base / relative
    if not path.exists():
        raise FileNotFoundError(
            f"{path} absent. Récupérer les journaux : "
            "docker compose run --rm lab python scripts/fetch_exposure.py"
        )

    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 22), b""):
            digest.update(chunk)
    size = path.stat().st_size
    fingerprint = digest.hexdigest()
    return (size == expected_size and fingerprint == expected_digest, size, fingerprint)


def source_path(name: str, directory: Path | None = None) -> Path:
    """Chemin attendu d'un journal."""
    if name not in SOURCES:
        raise ValueError(f"journal inconnu : {name!r}")
    base = EXPOSURE_DIRECTORY if directory is None else directory
    return base / SOURCES[name][0]


def load_baidu_part(path: Path | None = None) -> Impressions:
    """Lit une tranche de Baidu-ULTR et la met à plat.

    Quatre colonnes suffisent, sur les vingt-neuf que porte le fichier : la session
    (``query_no``), le **rang d'affichage** (``position``), le clic, et l'identité du document
    (``url_md5``). Les embeddings, qui font tout le poids du fichier, ne sont pas lus.

    Returns:
        Le journal mis à plat, fils groupés par session.
    """
    import pyarrow.feather as feather  # dépendance de laboratoire, pas du noyau

    source = source_path("baidu") if path is None else path
    table = feather.read_table(source, columns=["query_no", "position", "click", "url_md5"])

    sessions = np.asarray(table["query_no"])
    _, feeds = np.unique(sessions, return_inverse=True)
    lengths = np.bincount(feeds)
    documents = np.unique(np.asarray(table["url_md5"].to_pylist()), return_inverse=True)[1]

    return Impressions(
        items=documents.astype(np.int64),
        ranks=np.asarray(table["position"]).astype(np.int64),
        clicks=np.asarray(table["click"]).astype(float),
        feeds=feeds.astype(np.int64),
        feed_lengths=lengths.astype(np.int64),
    )


def load_obd_bucket(name: str, directory: Path | None = None) -> dict[str, np.ndarray]:
    """Lit un seau de l'Open Bandit Dataset, réduit à ce qui sert.

    Le jeu enregistre une ligne par impression : le contenu recommandé, la **position** où il
    l'a été — 1, 2 ou 3, de gauche à droite dans un bandeau de trois vignettes — le clic, et la
    **propension vraie** de ce choix.

    Returns:
        Les quatre relevés, et le nombre de contenus du catalogue.
    """
    import pandas as pd  # dépendance de laboratoire, pas du noyau

    frame = pd.read_csv(
        source_path(name, directory=directory),
        usecols=["item_id", "position", "click", "propensity_score"],
    )
    return {
        "items": frame["item_id"].to_numpy(dtype=np.int64),
        "positions": frame["position"].to_numpy(dtype=np.int64),
        "clicks": frame["click"].to_numpy(dtype=float),
        "propensities": frame["propensity_score"].to_numpy(dtype=float),
        "item_count": np.asarray(frame["item_id"].nunique(), dtype=np.int64),
    }


def obd_click_rates(bucket: dict[str, np.ndarray]) -> dict[int, tuple[int, int, float, float]]:
    """Taux de clic par position, avec son erreur type binomiale.

    Dans un seau **aléatoire**, l'affectation des contenus aux positions est indépendante du
    contenu : la différence de taux de clic entre positions est alors un effet **causal** de la
    position, sans qu'aucun modèle n'ait à être posé. C'est ce qui manquait partout ailleurs.

    Returns:
        Par position : impressions, clics, taux, erreur type.
    """
    rates: dict[int, tuple[int, int, float, float]] = {}
    for position in np.unique(bucket["positions"]):
        selected = bucket["positions"] == position
        exposures = int(selected.sum())
        successes = int(bucket["clicks"][selected].sum())
        rate = successes / exposures
        rates[int(position)] = (
            exposures,
            successes,
            rate,
            float(np.sqrt(rate * (1.0 - rate) / exposures)),
        )
    return rates


def off_policy_check(
    target_bucket: dict[str, np.ndarray],
    logged_bucket: dict[str, np.ndarray],
    caps: tuple[float, ...] = (10.0, 100.0, 1000.0),
) -> OffPolicyCheck:
    """Estime la valeur de la politique cible depuis le seul seau d'enregistrement, et compare.

    La politique cible est ici la politique **uniforme** : chaque contenu du catalogue a la même
    chance d'être servi à chaque position. Sa valeur est estimée sur les données d'une politique
    différente — Bernoulli TS — puis confrontée à la valeur mesurée directement dans le seau où
    la politique uniforme a réellement servi.

    Args:
        target_bucket: le seau servi par la politique cible, qui fournit la vérité terrain.
        logged_bucket: le seau servi par la politique d'enregistrement.
        caps: plafonds de poids à rapporter.

    Returns:
        Les estimations et de quoi juger ce qu'elles valent.
    """
    truth = float(target_bucket["clicks"].mean())
    exposures = int(target_bucket["clicks"].size)
    truth_error = float(np.sqrt(truth * (1.0 - truth) / exposures))

    catalogue = int(logged_bucket["item_count"])
    clicks = logged_bucket["clicks"]
    logged = logged_bucket["propensities"]
    target = np.full(clicks.size, 1.0 / catalogue)

    return OffPolicyCheck(
        truth=truth,
        truth_error=truth_error,
        naive=float(clicks.mean()),
        importance_sampling=ips(clicks, target, logged),
        self_normalised=snips(clicks, target, logged),
        clipped={cap: clipped_ips(clicks, target, logged, cap) for cap in caps},
        effective_size=effective_sample_size(target, logged),
        logged_size=int(clicks.size),
    )


def obd_cells(bucket: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Réduit un seau aux cellules (contenu, position, propension), sans perte pour les mesures.

    Aucun seuil n'est appliqué : les estimateurs contrefactuels sont des moyennes sur toutes les
    impressions, et écarter une cellule rare les biaiserait. La réduction est exacte parce que
    le poids d'importance ne dépend que de la propension.
    """
    keys, inverse = np.unique(
        np.stack([bucket["items"], bucket["positions"]], axis=1), axis=0, return_inverse=True
    )
    propensities, propensity_index = np.unique(bucket["propensities"], return_inverse=True)
    combined = inverse.astype(np.int64) * propensities.size + propensity_index
    cells, cell_index = np.unique(combined, return_inverse=True)

    exposures = np.bincount(cell_index, minlength=cells.size)
    successes = np.bincount(cell_index, weights=bucket["clicks"], minlength=cells.size)
    key_index, propensity_of_cell = np.divmod(cells, propensities.size)

    return {
        "cell_items": keys[key_index, 0].astype(np.int32),
        "cell_ranks": keys[key_index, 1].astype(np.int32),
        "cell_propensities": propensities[propensity_of_cell],
        "cell_exposures": exposures.astype(np.int64),
        "cell_clicks": successes.astype(np.int64),
        "item_count": np.asarray(bucket["item_count"], dtype=np.int32),
        "distinct_items": np.asarray(np.unique(bucket["items"]).size, dtype=np.int32),
        "maximum_rank": np.asarray(bucket["positions"].max(), dtype=np.int32),
    }


def bucket_from_digest(digest: Digest, name: str) -> dict[str, np.ndarray]:
    """Redéploie un seau de l'Open Bandit Dataset depuis le condensé.

    Le redéploiement est **exact** : chaque cellule porte son nombre d'impressions et de clics,
    et le poids d'importance ne dépend que de la propension. Un test le vérifie contre le
    journal brut.
    """
    arrays = digest.splits[name]
    exposures = arrays["cell_exposures"].astype(np.int64)
    successes = arrays["cell_clicks"].astype(np.int64)
    clicks = np.concatenate(
        [
            np.concatenate([np.ones(hit), np.zeros(seen - hit)])
            for seen, hit in zip(exposures, successes, strict=True)
        ]
    )
    return {
        "items": np.repeat(arrays["cell_items"].astype(np.int64), exposures),
        "positions": np.repeat(arrays["cell_ranks"].astype(np.int64), exposures),
        "clicks": clicks,
        "propensities": np.repeat(arrays["cell_propensities"], exposures),
        "item_count": arrays["item_count"],
    }


def build_digest(directory: Path | None = None) -> Digest:
    """Construit le condensé des deux journaux depuis les fichiers bruts."""
    sources: dict[str, str] = {}
    tables: dict[str, dict[str, np.ndarray]] = {}

    _, _, fingerprint = verify_source("baidu", directory=directory)
    sources["baidu"] = fingerprint
    tables["baidu"] = digest_split(load_baidu_part(source_path("baidu", directory=directory)))

    for name in OBD_BUCKETS:
        _, _, fingerprint = verify_source(name, directory=directory)
        sources[name] = fingerprint
        tables[name] = obd_cells(load_obd_bucket(name, directory=directory))

    return Digest(sources=sources, minimum_impressions=DIGEST_MINIMUM_IMPRESSIONS, splits=tables)


def load_digest(path: Path | None = None) -> Digest:
    """Relit le condensé versionné des deux journaux."""
    return _load_digest(
        DIGEST_PATH if path is None else path,
        rebuild_with="docker compose run --rm lab python scripts/build_exposure_digest.py",
    )
