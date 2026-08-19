"""Corpus étendu, dérivé de catégories Wikipédia déclarées à l'avance.

Pourquoi ne pas simplement allonger la liste
--------------------------------------------

Le [corpus pilote](corpus.py) compte vingt-quatre sujets choisis à la main. À cette taille,
le choix manuel se relit et se conteste. À plusieurs centaines, il ne se relit plus — et
c'est précisément là que le biais de sélection devient invisible : rien ne distingue, dans
une liste de trois cents titres, ceux qui ont été retenus pour ce qu'ils montrent.

Ce module remplace donc le choix des **sujets** par le choix des **catégories**. Les
catégories sont peu nombreuses, déclarées ici en clair, et l'appartenance d'un article à
l'une d'elles est décidée par les contributeurs de Wikipédia, non par l'auteur de cette
analyse. Tout ce qu'une catégorie contient entre dans le corpus.

Ce que ce déplacement ne supprime pas
-------------------------------------

La correspondance catégorie → registre reste un choix, et c'est **le** choix déterminant de
l'analyse. Il est déclaré dans :data:`REGISTERS`, et une correspondance différente pourrait
donner un résultat différent. Ce qui change, c'est que ce choix porte sur une vingtaine de
catégories vérifiables plutôt que sur trois cents titres, et qu'il est arrêté avant toute
mesure.

Trois précautions sont prises contre les confondants les plus évidents :

* **des événements de part et d'autre.** Si le registre « accusation » ne contenait que des
  affaires — donc des événements datés — et le registre « découverte » que des concepts
  abstraits, la comparaison opposerait des types de sujets et non des registres émotionnels.
  Les catégories retenues côté découverte portent donc sur des objets à annonce : missions
  spatiales, expériences, exoplanètes, lauréats de prix.
* **des classes disjointes.** Un article présent dans les deux registres — un scandale
  impliquant un scientifique, par exemple — est **écarté** plutôt qu'attribué arbitrairement.
* **un échantillonnage déterministe.** Pour équilibrer les effectifs, la troncature se fait
  par empreinte SHA-256 du titre et non par ordre alphabétique, qui surreprésenterait les
  premières lettres. Le tirage est reproductible à l'identique.
* **un filtre de notabilité aveugle au registre.** Les catégories des deux registres ne
  contiennent pas des articles de même nature : « Astronomical surveys » explorée à
  profondeur 1 ramène près de quatre mille entrées de catalogue d'objets célestes, et
  « Exoplanets » plus de mille planètes individuelles, tous à trafic quasi nul. Sans filtre,
  le tirage puiserait massivement dans ces entrées, le détecteur les écarterait faute de
  régime antérieur mesurable, et le registre « découverte » serait décimé quand l'autre
  survivrait. Les deux pools sont donc restreints aux articles d'au moins
  :data:`MIN_ARTICLE_BYTES` octets — critère de substance appliqué identiquement de part et
  d'autre, et obtenu en une requête par cinquantaine de titres.

Le manifeste
------------

La liste finalement retenue est écrite dans ``data/catalogue.json`` et **versionnée**. C'est
elle qui constitue le pré-enregistrement : une fois écrite, elle n'est pas régénérée
silencieusement, et un résultat publié se rapporte à un corpus consultable.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from ide.corpus import CorpusEntry

__all__ = [
    "CATALOGUE_PATH",
    "MIN_ARTICLE_BYTES",
    "REGISTERS",
    "CategorySource",
    "build_catalogue",
    "fetch_category_members",
    "filter_by_size",
    "load_catalogue",
    "save_catalogue",
]

#: Taille minimale d'un article, en octets de wikitexte. Sert de mesure de substance, non de
#: qualité : un article de dix mille octets a été rédigé, relu et étoffé, ce qui en fait un
#: sujet susceptible d'avoir une audience mesurable. Le seuil est appliqué identiquement aux
#: deux registres.
MIN_ARTICLE_BYTES = 10_000

#: Emplacement du manifeste versionné.
CATALOGUE_PATH = Path(__file__).resolve().parents[2] / "data" / "catalogue.json"

_ENDPOINT = "https://en.wikipedia.org/w/api.php"
_USER_AGENT = "IDE-research/0.1 (https://github.com/s-geffroy/Indice-Diversite-Exposee)"

# L'API MediaWiki tolère un rythme soutenu, mais la courtoisie veut qu'on l'espace.
_DELAY_SECONDS = 0.4


@dataclass(frozen=True)
class CategorySource:
    """Une catégorie déclarée comme source d'un registre.

    Attributes:
        category: titre complet de la catégorie, préfixe ``Category:`` compris.
        register: ``"accusation"`` ou ``"discovery"``.
        depth: profondeur d'exploration des sous-catégories. À 0, seuls les articles
            directement rattachés sont retenus ; à 1, ceux des sous-catégories immédiates
            aussi. Au-delà, l'arborescence de Wikipédia dérive vite hors sujet — une
            sous-sous-catégorie de « Théories du complot » peut porter sur la filmographie
            d'un réalisateur.
    """

    category: str
    register: str
    depth: int = 1

    def __post_init__(self) -> None:
        if not self.category.startswith("Category:"):
            raise ValueError("le titre doit commencer par 'Category:'")
        if self.register not in ("accusation", "discovery"):
            raise ValueError("le registre doit valoir 'accusation' ou 'discovery'")
        if not 0 <= self.depth <= 2:
            raise ValueError("la profondeur doit appartenir à [0, 2]")


#: Correspondance catégorie → registre. **C'est le choix déterminant de l'analyse**, et il
#: est arrêté avant toute mesure.
#:
#: Registre *accusation* : l'attention est mobilisée par une accusation, une menace ou un
#: scandale. Registre *découverte* : par une découverte ou une réussite. Les catégories du
#: second sont choisies pour porter, comme celles du premier, sur des objets à annonce
#: datable — non sur des concepts abstraits.
REGISTERS: tuple[CategorySource, ...] = (
    # — accusation ————————————————————————————————————————————————————————————
    CategorySource("Category:Conspiracy theories", "accusation"),
    CategorySource("Category:Disinformation", "accusation"),
    CategorySource("Category:Misinformation", "accusation"),
    CategorySource("Category:Fake news", "accusation"),
    CategorySource("Category:Hoaxes", "accusation"),
    CategorySource("Category:Political scandals", "accusation"),
    CategorySource("Category:Corruption", "accusation"),
    CategorySource("Category:Propaganda", "accusation"),
    CategorySource("Category:Moral panic", "accusation"),
    # — découverte ——————————————————————————————————————————————————————————
    CategorySource("Category:Space probes", "discovery"),
    CategorySource("Category:Space missions", "discovery"),
    CategorySource("Category:Physics experiments", "discovery"),
    CategorySource("Category:Astronomical surveys", "discovery"),
    CategorySource("Category:Exoplanets", "discovery"),
    CategorySource("Category:Nobel laureates in Physics", "discovery", depth=0),
    CategorySource("Category:Nobel laureates in Chemistry", "discovery", depth=0),
    CategorySource("Category:Nobel laureates in Physiology or Medicine", "discovery", depth=0),
)


def _api(**params: object) -> dict:
    """Appelle l'API MediaWiki, avec quelques tentatives en cas d'échec réseau."""
    params.setdefault("format", "json")
    url = f"{_ENDPOINT}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})

    last: Exception | None = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
                return json.loads(response.read().decode("utf-8"))
        except OSError as error:
            last = error
            time.sleep(2.0 * (attempt + 1))

    raise RuntimeError(f"API MediaWiki injoignable : {last}")


def _members(category: str, kind: str, cap: int = 3_000) -> list[str]:
    """Membres d'une catégorie, articles (``page``) ou sous-catégories (``subcat``)."""
    collected: list[str] = []
    continuation: dict[str, object] = {}

    while len(collected) < cap:
        payload = _api(
            action="query",
            list="categorymembers",
            cmtitle=category,
            cmlimit=500,
            cmtype=kind,
            **continuation,
        )
        collected.extend(item["title"] for item in payload["query"]["categorymembers"])

        if "continue" not in payload:
            break
        continuation = dict(payload["continue"])
        time.sleep(_DELAY_SECONDS)

    return collected[:cap]


def fetch_category_members(source: CategorySource) -> list[str]:
    """Titres d'articles d'une catégorie, sous-catégories incluses selon sa profondeur.

    Args:
        source: catégorie déclarée.

    Returns:
        Les titres d'articles, dédupliqués et triés — l'ordre de l'API dépend de clés de
        tri internes, un tri explicite rend le résultat reproductible.
    """
    titles = set(_members(source.category, "page"))
    frontier = [source.category]

    for _ in range(source.depth):
        children: list[str] = []
        for parent in frontier:
            children.extend(_members(parent, "subcat"))
            time.sleep(_DELAY_SECONDS)
        for child in children:
            titles.update(_members(child, "page"))
            time.sleep(_DELAY_SECONDS)
        frontier = children

    return sorted(titles)


def filter_by_size(titles: list[str], min_bytes: int = MIN_ARTICLE_BYTES) -> list[str]:
    """Restreint une liste de titres aux articles d'au moins ``min_bytes`` octets.

    Les tailles sont demandées par lots de cinquante, la limite de l'API pour un appel
    anonyme, ce qui rend l'opération praticable sur plusieurs milliers de titres.

    Args:
        titles: titres à filtrer.
        min_bytes: taille minimale du wikitexte.

    Returns:
        Les titres retenus, dans l'ordre d'entrée.
    """
    if min_bytes <= 0:
        return list(titles)

    sizes: dict[str, int] = {}
    for start in range(0, len(titles), 50):
        batch = titles[start : start + 50]
        payload = _api(action="query", prop="info", titles="|".join(batch))
        for page in payload.get("query", {}).get("pages", {}).values():
            if "missing" not in page:
                sizes[page["title"]] = int(page.get("length", 0))
        time.sleep(_DELAY_SECONDS)

    return [title for title in titles if sizes.get(title, 0) >= min_bytes]


def _fingerprint(title: str) -> str:
    """Empreinte stable d'un titre, pour un échantillonnage reproductible et non alphabétique."""
    return hashlib.sha256(title.encode("utf-8")).hexdigest()


def _to_entry(title: str, register: str) -> CorpusEntry:
    """Convertit un titre MediaWiki en entrée de corpus, prête pour l'API de consultations."""
    return CorpusEntry(
        project="en.wikipedia",
        article=urllib.parse.quote(title.replace(" ", "_"), safe="_(),-.!*'"),
        label=title,
        category=register,
    )


def build_catalogue(
    sources: tuple[CategorySource, ...] = REGISTERS,
    per_register: int = 220,
    min_bytes: int = MIN_ARTICLE_BYTES,
) -> tuple[list[CorpusEntry], dict[str, object]]:
    """Construit le corpus étendu à partir des catégories déclarées.

    Args:
        sources: catégories et leur registre.
        per_register: effectif retenu par registre. La troncature équilibre les deux
            classes ; elle se fait par empreinte du titre, donc sans préférence
            alphabétique.

    Returns:
        Le corpus et un rapport de construction — effectifs par catégorie, nombre
        d'articles écartés pour appartenance aux deux registres, effectifs avant et après
        troncature. Ce rapport accompagne le manifeste : sans lui, on ne saurait pas
        combien de sujets la troncature a laissés de côté.
    """
    if per_register < 1:
        raise ValueError("l'effectif par registre doit être positif")

    by_register: dict[str, set[str]] = {"accusation": set(), "discovery": set()}
    per_category: dict[str, int] = {}

    for source in sources:
        titles = fetch_category_members(source)
        per_category[source.category] = len(titles)
        by_register[source.register].update(titles)

    # Classes disjointes : un article des deux registres est écarté plutôt qu'arbitré.
    overlap = by_register["accusation"] & by_register["discovery"]
    for register in by_register:
        by_register[register] -= overlap

    entries: list[CorpusEntry] = []
    kept: dict[str, int] = {}
    available: dict[str, int] = {}
    substantial: dict[str, int] = {}

    for register, titles in by_register.items():
        available[register] = len(titles)
        eligible = filter_by_size(sorted(titles), min_bytes=min_bytes)
        substantial[register] = len(eligible)
        selected = sorted(eligible, key=_fingerprint)[:per_register]
        kept[register] = len(selected)
        entries.extend(_to_entry(title, register) for title in sorted(selected))

    report = {
        "per_category": per_category,
        "overlap_discarded": sorted(overlap),
        "available": available,
        "substantial": substantial,
        "kept": kept,
        "per_register_cap": per_register,
        "min_article_bytes": min_bytes,
    }

    return entries, report


def save_catalogue(
    entries: list[CorpusEntry], report: dict[str, object], path: Path | None = None
) -> Path:
    """Écrit le manifeste versionné et renvoie son chemin."""
    destination = CATALOGUE_PATH if path is None else path
    destination.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "sources": [
            {"category": source.category, "register": source.register, "depth": source.depth}
            for source in REGISTERS
        ],
        "report": report,
        "entries": [
            {
                "project": entry.project,
                "article": entry.article,
                "label": entry.label,
                "category": entry.category,
            }
            for entry in entries
        ],
    }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n")

    return destination


def load_catalogue(path: Path | None = None) -> tuple[list[CorpusEntry], dict[str, object]]:
    """Charge le manifeste versionné.

    Raises:
        FileNotFoundError: si le manifeste n'a pas été construit. Il n'est **pas** reconstruit
            à la volée : un corpus qui se régénérerait à chaque exécution ne serait pas
            pré-enregistré.
    """
    source = CATALOGUE_PATH if path is None else path

    if not source.exists():
        raise FileNotFoundError(
            f"manifeste absent ({source}). Le construire avec scripts/build_catalogue.py."
        )

    payload = json.loads(source.read_text())
    entries = [
        CorpusEntry(
            project=item["project"],
            article=item["article"],
            label=item["label"],
            category=item["category"],
        )
        for item in payload["entries"]
    ]

    return entries, payload.get("report", {})
