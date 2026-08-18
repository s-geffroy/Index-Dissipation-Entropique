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
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import numpy as np

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


@dataclass(frozen=True)
class Impressions:
    """Un journal d'impressions mis à plat : une ligne par contenu servi.

    Attributes:
        items: identifiant du contenu servi, ou ``None`` quand l'identité des contenus n'a
            pas été conservée — c'est le cas du condensé versionné, qui retient l'ordre des
            fils mais pas ce qui y était servi.
        ranks: position dans la liste **enregistrée**, à partir de 1. Que cette position
            soit celle de l'affichage est précisément ce que ce module met à l'épreuve.
        clicks: 1 si le contenu a été cliqué.
        feeds: indice du fil auquel appartient la ligne.
        feed_lengths: longueur de chaque fil, indexée par ``feeds``.
    """

    items: np.ndarray | None
    ranks: np.ndarray
    clicks: np.ndarray
    feeds: np.ndarray
    feed_lengths: np.ndarray

    def __post_init__(self) -> None:
        served = self.ranks.shape
        if not (self.clicks.shape == self.feeds.shape == served):
            raise ValueError("les relevés doivent porter sur les mêmes lignes servies")
        if self.items is not None and self.items.shape != served:
            raise ValueError("les relevés doivent porter sur les mêmes lignes servies")
        if self.ranks.size and int(self.feeds.max()) >= self.feed_lengths.size:
            raise ValueError("un fil servi n'a pas de longueur déclarée")

    @property
    def served(self) -> int:
        """Nombre de contenus servis, toutes impressions confondues."""
        return int(self.ranks.size)

    @property
    def feed_count(self) -> int:
        """Nombre de fils."""
        return int(self.feed_lengths.size)

    @property
    def distinct_items(self) -> int:
        """Nombre de contenus distincts apparus au moins une fois."""
        if self.items is None:
            raise ValueError("ce journal ne retient pas l'identité des contenus servis")
        return int(np.unique(self.items).size)

    @property
    def click_rate(self) -> float:
        """Taux de clic global, par contenu servi."""
        return float(self.clicks.mean()) if self.served else float("nan")


@dataclass(frozen=True)
class ExchangeabilityTest:
    """Le verdict du test d'échangeabilité intra-fil.

    L'hypothèse nulle est que, **à fil donné**, les clics sont répartis indépendamment de la
    position enregistrée. C'est exactement ce qu'un mélange produit, et exactement ce qu'un
    biais de position viole.

    Attributes:
        statistic: somme des rangs normalisés des contenus cliqués.
        expectation: son espérance sous l'hypothèse d'échangeabilité.
        deviation: écart réduit :math:`z`. Un biais de position le rend **négatif** : les
            clics se concentrent en haut.
        p_value: probabilité bilatérale d'un écart au moins aussi grand.
        feeds_used: nombre de fils informatifs — au moins deux positions, au moins un clic,
            et pas que des clics. Les autres ne contraignent rien.
    """

    statistic: float
    expectation: float
    deviation: float
    p_value: float
    feeds_used: int

    @property
    def exchangeable(self) -> bool:
        """Vrai si l'ordre enregistré est indiscernable d'un mélange, au seuil de 5 %."""
        return self.p_value >= 0.05


@dataclass(frozen=True)
class Coverage:
    """De quoi juger si :math:`\\eta` est estimable — et pourquoi cela ne suffit pas.

    Attributes:
        items: contenus distincts servis.
        items_above_threshold: contenus dont au moins une cellule (contenu, rang) atteint le
            seuil d'impressions.
        items_with_variation: contenus vus à **plusieurs** rangs distincts au-dessus du seuil.
            C'est la seule variation qui identifie la sévérité.
        median_distinct_ranks: nombre médian de rangs distincts par contenu retenu.
        maximum_rank: plus grande position observée.
    """

    items: int
    items_above_threshold: int
    items_with_variation: int
    median_distinct_ranks: float
    maximum_rank: int


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


def click_rate_by_rank(
    impressions: Impressions,
    maximum_rank: int = 20,
    feed_length: int | None = None,
) -> np.ndarray:
    """Taux de clic observé à chaque position, des rangs 1 à ``maximum_rank``.

    Args:
        impressions: le journal.
        maximum_rank: dernière position rapportée.
        feed_length: si fourni, restreint aux fils de cette longueur **exacte**. C'est le
            contrôle qui compte : sans lui, les positions élevées ne sont peuplées que par
            les fils longs, dont le taux de clic par contenu est plus faible, et la courbe
            décroît pour cette seule raison.

    Returns:
        Taux de clic par position, ``nan`` là où aucune impression n'a été observée.
    """
    if maximum_rank < 1:
        raise ValueError("il faut au moins une position")
    selected = np.ones(impressions.served, dtype=bool)
    if feed_length is not None:
        selected = impressions.feed_lengths[impressions.feeds] == feed_length

    ranks = impressions.ranks[selected]
    clicks = impressions.clicks[selected]
    rates = np.full(maximum_rank, np.nan)
    for position in range(1, maximum_rank + 1):
        at_position = ranks == position
        if at_position.any():
            rates[position - 1] = float(clicks[at_position].mean())
    return rates


def naive_severity_fit(
    impressions: Impressions,
    maximum_rank: int = 20,
    feed_length: int | None = None,
) -> float:
    """Ajuste :math:`\\log \\mathrm{CTR}(R) = c - \\eta \\log R` sur le taux de clic agrégé.

    C'est l'estimation qu'on obtient en traçant la courbe la plus naturelle du monde, et c'est
    le piège : agrégée sur des fils de longueurs différentes, elle mesure la composition du
    mélange de longueurs, pas l'exposition. Fournir ``feed_length`` la rend honnête et, sur
    MIND, la ramène à zéro.

    Returns:
        La sévérité apparente. Positive quand le taux de clic décroît avec le rang.
    """
    rates = click_rate_by_rank(impressions, maximum_rank, feed_length=feed_length)
    positions = np.arange(1, maximum_rank + 1, dtype=float)
    usable = np.isfinite(rates) & (rates > 0.0)
    if usable.sum() < 2:
        return float("nan")
    slope, _ = np.polyfit(np.log(positions[usable]), np.log(rates[usable]), 1)
    return float(-slope)


def exchangeability_test(impressions: Impressions) -> ExchangeabilityTest:
    """Teste si les clics sont indifférents à la position enregistrée, à fil donné.

    Pour chaque fil de longueur :math:`L` portant :math:`k` clics, on somme les rangs
    normalisés :math:`u_R = (R - 1/2)/L` des contenus cliqués. Sous l'hypothèse
    d'échangeabilité, ces :math:`k` positions sont un tirage sans remise parmi les :math:`L`
    positions du fil : l'espérance et la variance de la somme sont connues exactement,

    .. math:: \\mathbb{E} = k\\,\\bar{u}, \\qquad
              \\mathbb{V} = \\frac{k(L-k)}{L-1}\\,\\sigma^2_u.

    Le conditionnement au fil est ce qui rend le test immunisé au mélange des longueurs — le
    confondant qui fabrique à lui seul la courbe de :func:`naive_severity_fit` — ainsi qu'à
    la qualité moyenne des contenus d'un fil et à l'appétit de clic de son lecteur.

    Returns:
        Le verdict, avec de quoi juger sur quoi il repose.
    """
    lengths = impressions.feed_lengths.astype(float)
    if impressions.served == 0:
        return ExchangeabilityTest(float("nan"), float("nan"), float("nan"), float("nan"), 0)

    per_row_length = lengths[impressions.feeds]
    normalised = (impressions.ranks - 0.5) / per_row_length

    count = impressions.feed_count
    clicks_per_feed = np.bincount(impressions.feeds, weights=impressions.clicks, minlength=count)
    clicked_sum = np.bincount(
        impressions.feeds, weights=impressions.clicks * normalised, minlength=count
    )
    mean_position = np.bincount(impressions.feeds, weights=normalised, minlength=count) / lengths
    mean_square = (
        np.bincount(impressions.feeds, weights=normalised**2, minlength=count) / lengths
    )
    variance_position = np.maximum(mean_square - mean_position**2, 0.0)

    informative = (lengths >= 2) & (clicks_per_feed > 0) & (clicks_per_feed < lengths)
    if not informative.any():
        return ExchangeabilityTest(float("nan"), float("nan"), float("nan"), float("nan"), 0)

    clicks_kept = clicks_per_feed[informative]
    lengths_kept = lengths[informative]
    statistic = float(clicked_sum[informative].sum())
    expectation = float((clicks_kept * mean_position[informative]).sum())
    variance = float(
        (
            clicks_kept
            * (lengths_kept - clicks_kept)
            / (lengths_kept - 1.0)
            * variance_position[informative]
        ).sum()
    )
    if variance <= 0.0:
        return ExchangeabilityTest(statistic, expectation, float("nan"), float("nan"),
                                   int(informative.sum()))

    deviation = (statistic - expectation) / math.sqrt(variance)
    p_value = math.erfc(abs(deviation) / math.sqrt(2.0))
    return ExchangeabilityTest(statistic, expectation, deviation, p_value, int(informative.sum()))


def rank_coverage(impressions: Impressions, minimum_impressions: int = 5) -> Coverage:
    """Compte ce que :func:`ide.offpolicy.estimate_position_bias` trouverait à exploiter.

    Cette couverture est **nécessaire** pour estimer la sévérité, et pas suffisante : elle
    compte une variation de rang sans dire d'où elle vient. Sur un journal mélangé elle est
    maximale, et l'estimation qui s'ensuit est un artefact. Le contrôle qui manque est
    :func:`exchangeability_test`.
    """
    if impressions.items is None:
        raise ValueError("la couverture par contenu exige l'identité des contenus servis")
    keys, inverse = np.unique(
        np.stack([impressions.items, impressions.ranks], axis=1), axis=0, return_inverse=True
    )
    exposures = np.bincount(inverse, minlength=len(keys))
    successes = np.bincount(inverse, weights=impressions.clicks, minlength=len(keys))

    usable = (exposures >= minimum_impressions) & (successes > 0)
    kept_items = keys[usable, 0]
    kept_ranks = keys[usable, 1]

    distinct_ranks = [
        int(np.unique(kept_ranks[kept_items == item]).size) for item in np.unique(kept_items)
    ]
    varying = [value for value in distinct_ranks if value > 1]
    return Coverage(
        items=impressions.distinct_items,
        items_above_threshold=len(distinct_ranks),
        items_with_variation=len(varying),
        median_distinct_ranks=float(np.median(distinct_ranks)) if distinct_ranks else float("nan"),
        maximum_rank=int(impressions.ranks.max()) if impressions.served else 0,
    )


def simulate_feeds(
    feed_lengths: Iterable[int],
    severity: float,
    catalogue: int = 20_000,
    base_rate: float = 0.06,
    dispersion: float = 0.8,
    rng: np.random.Generator | None = None,
) -> Impressions:
    """Fabrique un journal de même structure de fils, sous un biais de position **connu**.

    Le modèle est celui du reste du chantier :
    :math:`P(\\text{clic} \\mid i, R) = g(i)\\,R^{-\\eta}`, la qualité :math:`g(i)` étant un
    effet fixe de contenu tiré une fois pour toutes.

    C'est l'étalon du test : appliqué à ce journal, :func:`exchangeability_test` doit rejeter,
    et d'autant plus nettement que :math:`\\eta` est grand. Sans cet étalonnage, un test qui
    ne rejette jamais rien serait indiscernable d'un test qui ne rejette pas MIND.

    Args:
        feed_lengths: longueurs des fils à reproduire.
        severity: sévérité vraie du biais de position.
        catalogue: taille du catalogue de contenus.
        base_rate: taux de clic médian d'un contenu en première position.
        dispersion: dispersion log-normale de la qualité entre contenus.
        rng: générateur, pour la reproductibilité.

    Returns:
        Le journal simulé.
    """
    generator = np.random.default_rng() if rng is None else rng
    lengths = np.asarray(list(feed_lengths), dtype=np.int64)
    if np.any(lengths < 1):
        raise ValueError("un fil compte au moins une position")

    total = int(lengths.sum())
    feeds = np.repeat(np.arange(lengths.size), lengths)
    ranks = np.concatenate([np.arange(1, length + 1) for length in lengths])

    quality = base_rate * generator.lognormal(0.0, dispersion, size=catalogue)
    items = generator.integers(0, catalogue, size=total)
    probability = np.clip(quality[items] * ranks.astype(float) ** (-severity), 0.0, 1.0)
    clicks = (generator.random(total) < probability).astype(float)

    return Impressions(
        items=items.astype(np.int64),
        ranks=ranks.astype(np.int64),
        clicks=clicks,
        feeds=feeds.astype(np.int64),
        feed_lengths=lengths,
    )


def detectable_severity(
    feed_lengths: Iterable[int],
    probe: float = 0.02,
    confidence: float = 1.96,
    rng: np.random.Generator | None = None,
    **simulation: float,
) -> float:
    """Sévérité minimale que le test aurait détectée, à structure de fils donnée.

    Un test qui ne rejette pas ne dit rien tant qu'on ignore ce qu'il aurait su rejeter. On
    simule donc un biais de position de sévérité ``probe``, on relève l'écart réduit obtenu,
    et on extrapole linéairement — :math:`z` est proportionnel à :math:`\\eta` au voisinage de
    zéro, ce que le [notebook 16](../../notebooks/16_exploration_mind.ipynb) vérifie sur
    plusieurs sévérités.

    Returns:
        La sévérité au-delà de laquelle le test aurait rejeté, au seuil demandé.
    """
    if probe <= 0.0:
        raise ValueError("la sévérité d'essai doit être strictement positive")
    simulated = simulate_feeds(feed_lengths, severity=probe, rng=rng, **simulation)
    deviation = abs(exchangeability_test(simulated).deviation)
    if not math.isfinite(deviation) or deviation <= 0.0:
        return float("nan")
    return float(confidence * probe / deviation)


#: Le condensé versionné, seul dérivé de MIND que ce dépôt puisse porter. Il suffit à
#: reproduire toutes les mesures publiées, et il se reconstruit depuis le jeu brut par
#: ``scripts/build_mind_digest.py``.
DIGEST_PATH = Path(__file__).resolve().parents[2] / "data" / "mind_digest.npz"

#: Seuil d'impressions en deçà duquel une cellule (contenu, rang) n'est pas conservée dans le
#: condensé. Les estimations publiées emploient toutes un seuil au moins égal, de sorte que
#: le condensé donne exactement les mêmes chiffres que le jeu brut.
DIGEST_MINIMUM_IMPRESSIONS = 5


@dataclass(frozen=True)
class Digest:
    """Ce qu'il reste de MIND une fois retiré ce qu'on n'a pas le droit de redistribuer.

    Le jeu brut ne peut pas être versionné — licence de recherche Microsoft, 135 Mo. Le
    condensé retient deux choses, et rien d'autre :

    * la **structure d'ordre** des fils : leur longueur, et la position des clics. C'est ce
      dont vit :func:`exchangeability_test`, qui ne regarde jamais *quoi* a été servi ;
    * les **cellules (contenu, rang)** au-dessus du seuil d'impressions, sous la forme
      anonymisée d'un identifiant entier. C'est ce dont vit l'estimation de la sévérité.

    Attributes:
        sources: empreinte SHA-256 du journal dont chaque découpage est tiré.
        minimum_impressions: seuil appliqué aux cellules conservées.
        splits: les tableaux, par découpage.
    """

    sources: dict[str, str]
    minimum_impressions: int
    splits: dict[str, dict[str, np.ndarray]]

    def impressions(self, split: str) -> Impressions:
        """Reconstruit le journal au niveau du fil, sans l'identité des contenus."""
        arrays = self.splits[split]
        lengths = arrays["feed_lengths"].astype(np.int64)
        feeds = np.repeat(np.arange(lengths.size), lengths)
        ranks = np.concatenate([np.arange(1, length + 1) for length in lengths])
        clicks = np.zeros(ranks.size, dtype=float)
        offsets = np.concatenate([[0], np.cumsum(lengths)[:-1]])
        clicked = offsets[arrays["clicked_feeds"].astype(np.int64)] + (
            arrays["clicked_ranks"].astype(np.int64) - 1
        )
        clicks[clicked] = 1.0
        return Impressions(
            items=None,
            ranks=ranks.astype(np.int64),
            clicks=clicks,
            feeds=feeds.astype(np.int64),
            feed_lengths=lengths,
        )

    def coverage(self, split: str) -> Coverage:
        """Ce que :func:`ide.offpolicy.estimate_position_bias` trouverait à exploiter.

        Calculée directement sur les cellules conservées, donc identique à
        :func:`rank_coverage` appliquée au jeu brut au seuil du condensé.
        """
        arrays = self.splits[split]
        kept_items = arrays["cell_items"].astype(np.int64)
        kept_ranks = arrays["cell_ranks"].astype(np.int64)
        clicked = arrays["cell_clicks"] > 0
        kept_items, kept_ranks = kept_items[clicked], kept_ranks[clicked]
        distinct_ranks = [
            int(np.unique(kept_ranks[kept_items == item]).size) for item in np.unique(kept_items)
        ]
        return Coverage(
            items=int(arrays["distinct_items"]),
            items_above_threshold=len(distinct_ranks),
            items_with_variation=len([value for value in distinct_ranks if value > 1]),
            median_distinct_ranks=(
                float(np.median(distinct_ranks)) if distinct_ranks else float("nan")
            ),
            maximum_rank=int(arrays["maximum_rank"]),
        )

    def rows(self, split: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Redéploie les cellules conservées en lignes ``(contenu, rang, clic)``.

        L'estimation de :math:`\\eta` n'agrège de toute façon les lignes qu'en cellules : ce
        redéploiement rend donc à :func:`ide.offpolicy.estimate_position_bias` exactement ce
        qu'elle aurait vu sur le jeu brut, à seuil au moins égal à
        :data:`DIGEST_MINIMUM_IMPRESSIONS`.
        """
        arrays = self.splits[split]
        exposures = arrays["cell_exposures"].astype(np.int64)
        successes = arrays["cell_clicks"].astype(np.int64)
        items = np.repeat(arrays["cell_items"].astype(np.int64), exposures)
        ranks = np.repeat(arrays["cell_ranks"].astype(np.int64), exposures)
        clicks = np.concatenate(
            [
                np.concatenate([np.ones(hit), np.zeros(seen - hit)])
                for seen, hit in zip(exposures, successes, strict=True)
            ]
        )
        return items, ranks, clicks


def build_digest(splits: Iterable[str] = ("train", "dev"),
                 directory: Path | None = None) -> Digest:
    """Construit le condensé depuis le jeu brut."""
    sources: dict[str, str] = {}
    tables: dict[str, dict[str, np.ndarray]] = {}

    for split in splits:
        path = split_path(split, directory=directory)
        _, _, digest = verify_split(path, split)
        sources[split] = digest

        impressions = parse_behaviours(path)
        if impressions.items is None:  # pragma: no cover - parse_behaviours les conserve
            raise ValueError("le jeu brut doit porter l'identité des contenus")

        clicked = impressions.clicks > 0
        keys, inverse = np.unique(
            np.stack([impressions.items, impressions.ranks], axis=1), axis=0, return_inverse=True
        )
        exposures = np.bincount(inverse, minlength=len(keys))
        successes = np.bincount(inverse, weights=impressions.clicks, minlength=len(keys))
        kept = exposures >= DIGEST_MINIMUM_IMPRESSIONS

        tables[split] = {
            "feed_lengths": impressions.feed_lengths.astype(np.int32),
            "clicked_feeds": impressions.feeds[clicked].astype(np.int32),
            "clicked_ranks": impressions.ranks[clicked].astype(np.int32),
            "cell_items": keys[kept, 0].astype(np.int32),
            "cell_ranks": keys[kept, 1].astype(np.int32),
            "cell_exposures": exposures[kept].astype(np.int32),
            "cell_clicks": successes[kept].astype(np.int32),
            "distinct_items": np.asarray(impressions.distinct_items, dtype=np.int32),
            "maximum_rank": np.asarray(impressions.ranks.max(), dtype=np.int32),
        }

    return Digest(sources=sources, minimum_impressions=DIGEST_MINIMUM_IMPRESSIONS, splits=tables)


def save_digest(digest: Digest, path: Path | None = None) -> Path:
    """Écrit le condensé, empreintes des sources comprises."""
    destination = DIGEST_PATH if path is None else path
    payload: dict[str, np.ndarray] = {
        "minimum_impressions": np.asarray(digest.minimum_impressions),
        "splits": np.asarray(sorted(digest.splits)),
    }
    for split, arrays in digest.splits.items():
        payload[f"{split}__source"] = np.asarray(digest.sources[split])
        for name, values in arrays.items():
            payload[f"{split}__{name}"] = values
    destination.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(destination, **payload)
    return destination


def load_digest(path: Path | None = None) -> Digest:
    """Relit le condensé versionné."""
    source = DIGEST_PATH if path is None else path
    if not source.exists():
        raise FileNotFoundError(
            f"{source} absent. Le reconstruire : "
            "docker compose run --rm lab python scripts/build_mind_digest.py"
        )
    with np.load(source, allow_pickle=False) as stored:
        splits = [str(name) for name in stored["splits"]]
        sources = {split: str(stored[f"{split}__source"]) for split in splits}
        tables = {
            split: {
                name: stored[f"{split}__{name}"]
                for name in (
                    "feed_lengths",
                    "clicked_feeds",
                    "clicked_ranks",
                    "cell_items",
                    "cell_ranks",
                    "cell_exposures",
                    "cell_clicks",
                    "distinct_items",
                    "maximum_rank",
                )
            }
            for split in splits
        }
        minimum = int(stored["minimum_impressions"])
    return Digest(sources=sources, minimum_impressions=minimum, splits=tables)
