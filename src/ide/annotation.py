"""Annotation manuelle du registre émotionnel, en aveugle des séries d'attention.

Ce que ce module doit trancher
------------------------------

Le [corpus étendu](catalogue.py) a mesuré un résultat nul : la persistance ne diffère pas
entre registres émotionnels (×3,04 contre ×2,90, :math:`p = 0{,}53`). Mais il a aussi exposé
le défaut de son propre protocole — l'appartenance à une catégorie de Wikipédia est un
indicateur **bruité** du registre. « Lil Tay » figure dans une catégorie de canulars à cause
d'un canular sur sa mort, alors que l'attention portée à cet article est celle d'une
célébrité.

Or un bruit d'étiquetage n'introduit pas de biais directionnel : il **attire tout écart vers
zéro**. Le résultat nul est donc compatible avec deux lectures que ces données ne séparent
pas — absence d'effet, ou effet dilué.

Ce module produit l'étiquette manquante : le registre de chaque sujet, codé à la main, à
partir du seul couple **titre + chapeau d'article**.

La cécité, et ce qu'elle vaut
-----------------------------

L'annotation ne doit rien devoir au résultat qu'elle sert à mesurer. Trois dispositions y
concourent, et il faut dire ce que chacune garantit :

* **la grille est écrite avant les données.** Ce module — labels, définitions, règles de
  départage — est versionné dans un commit antérieur à la première annotation.
  L'historique git l'atteste, et c'est la seule des trois dispositions qui soit
  vérifiable par un tiers ;
* **l'entrée de l'annotateur est réduite et enregistrée.** Les chapeaux sont figés dans
  ``data/extracts.json`` et l'annotation retient l'empreinte SHA-256 de ce fichier. On sait
  donc exactement ce que l'annotateur a lu ;
* **les séries de consultations ne sont pas chargées** pendant l'annotation. C'est une
  propriété du processus, non une garantie cryptographique : elle se déclare, elle ne se
  prouve pas.

La contamination résiduelle est nommée, et non pas niée : cinq sujets ont été cités avec
leur élévation dans la page [corpus étendu](../../docs/corpus-etendu.md), et l'annotateur
les connaît donc. Ils sont listés dans :data:`CONTAMINATED` et l'analyse est reprise sans
eux, en contrôle de sensibilité.

Un annotateur unique ne donne pas d'accord inter-juges. Ce travail corrige donc le bruit
d'étiquetage, il ne mesure pas la fiabilité du codage — la distinction est reportée dans les
limites.

La grille
---------

**Question posée à chaque sujet** : *qu'est-ce qui mobiliserait l'attention du public sur cet
article ?* Non pas de quoi parle l'article, mais quelle émotion porterait sa consultation.

* :data:`ACCUSATION` — une **faute, une menace ou une tromperie attribuée à quelqu'un** :
  scandale, complot, corruption, atrocité, manipulation. Registre à :math:`\\alpha` élevé
  dans le modèle.
* :data:`DISCOVERY` — une **découverte, une exploration ou une réussite** : résultat
  scientifique, mission spatiale, distinction. Registre à :math:`\\alpha` faible.
* :data:`NEITHER` — **ni l'un ni l'autre**. Un produit de divertissement, une célébrité, une
  institution ordinaire, une entrée de catalogue, un concept technique. C'est l'étiquette
  qui fait le travail : elle retire du corpus les sujets qu'une catégorie a capturés pour
  des raisons thématiques, sans que leur audience relève du registre.

Cinq règles de départage, arrêtées avant lecture, pour que les cas limites ne se décident pas
au cas par cas :

1. **Une œuvre de fiction portant sur un scandale est** :data:`NEITHER`. Son public est un
   public de fiction. Cela vaut pour les romans, films, séries et jeux vidéo, quel que soit
   leur sujet.
2. **Une personne est codée par ce qui la rend notable** selon son chapeau : un lauréat de
   prix scientifique est :data:`DISCOVERY`, une personnalité mise en cause est
   :data:`ACCUSATION`, une célébrité est :data:`NEITHER`.
3. **Une atrocité, un massacre ou un attentat est** :data:`ACCUSATION`. Le registre est
   celui de la faute et de la menace, indépendamment de l'existence d'une accusation
   formelle.
4. **Un objet de catalogue ou un instrument sans annonce** reste :data:`DISCOVERY` si sa
   notabilité tient à ce qu'il a permis d'observer, et devient :data:`NEITHER` s'il n'est
   qu'une entrée technique parmi des milliers.
5. **Un concept abstrait nommant la faute elle-même** — « désinformation », « corruption
   politique » — est :data:`ACCUSATION`. La règle 1 ne s'y applique pas : ce n'est pas une
   œuvre.

Une seconde dimension est codée en même temps, sans coût supplémentaire : le **type** de
sujet (:data:`KINDS`). Elle permet de vérifier après coup que la comparaison n'oppose pas des
événements à des concepts — le confondant que le corpus étendu s'était efforcé d'éviter par
le choix des catégories, sans pouvoir le mesurer.

Enfin, chaque annotation porte une **confiance** binaire. Les sujets marqués incertains ne
sont pas écartés : ils servent à un contrôle de sensibilité, car écarter au vu du résultat
serait exactement ce que le pré-enregistrement interdit.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from ide.corpus import CorpusEntry

__all__ = [
    "ACCUSATION",
    "ANNOTATIONS_PATH",
    "CONTAMINATED",
    "DISCOVERY",
    "EXTRACTS_PATH",
    "KINDS",
    "NEITHER",
    "REGISTERS",
    "RUBRIC_VERSION",
    "Annotation",
    "annotated_entries",
    "confusion_matrix",
    "digest_extracts",
    "fetch_extracts",
    "load_annotations",
    "load_extracts",
    "save_annotations",
    "save_extracts",
]

#: Version de la grille. Toute modification des définitions ou des règles de départage
#: l'incrémente : une annotation se rapporte à une grille, et deux grilles ne se mélangent
#: pas.
RUBRIC_VERSION = "1.0"

ACCUSATION = "accusation"
DISCOVERY = "discovery"
NEITHER = "neither"

#: Les trois registres admis. L'ordre est celui de la grille, non un ordre de préférence.
REGISTERS: tuple[str, ...] = (ACCUSATION, DISCOVERY, NEITHER)

#: Types de sujet, codés pour contrôler après coup que la comparaison n'oppose pas des
#: natures d'objets différentes.
KINDS: tuple[str, ...] = ("event", "person", "organisation", "work", "concept", "object")

#: Niveaux de confiance. Binaire à dessein : une échelle plus fine inviterait à graduer
#: après coup.
CONFIDENCES: tuple[str, ...] = ("sure", "unsure")

#: Sujets dont l'annotateur connaissait le résultat avant d'annoter, pour les avoir cités
#: avec leur élévation dans la page du corpus étendu. La contamination se déclare et se
#: teste : l'analyse est reprise sans eux.
CONTAMINATED: tuple[str, ...] = (
    "Lil Tay",
    "Watch Dogs (video game)",
    "Million Dollar Extreme",
    "The Capture (TV series)",
    "Mossack Fonseca",
    "Illuminati (game)",
)

#: Chapeaux d'articles figés, entrée unique de l'annotateur.
EXTRACTS_PATH = Path(__file__).resolve().parents[2] / "data" / "extracts.json"

#: Annotations manuelles, avec l'empreinte des chapeaux dont elles proviennent.
ANNOTATIONS_PATH = Path(__file__).resolve().parents[2] / "data" / "annotations.json"

_ENDPOINT = "https://en.wikipedia.org/w/api.php"
_USER_AGENT = "IDE-research/0.1 (https://github.com/s-geffroy/Index-Dissipation-Entropique)"
_DELAY_SECONDS = 0.4

#: Longueur retenue du chapeau. Assez pour savoir de quoi il s'agit, assez court pour que
#: l'annotation reste une lecture de chapeau et non une enquête.
EXTRACT_CHARS = 600


@dataclass(frozen=True)
class Annotation:
    """Le codage manuel d'un sujet.

    Attributes:
        title: titre de l'article, clé de jointure avec le catalogue.
        register: l'un de :data:`REGISTERS`.
        kind: l'un de :data:`KINDS`.
        confidence: ``"sure"`` ou ``"unsure"``.
        note: justification brève, obligatoire pour les cas incertains ou contre-intuitifs.
    """

    title: str
    register: str
    kind: str
    confidence: str = "sure"
    note: str = ""

    def __post_init__(self) -> None:
        if self.register not in REGISTERS:
            raise ValueError(f"registre inconnu : {self.register!r}")
        if self.kind not in KINDS:
            raise ValueError(f"type inconnu : {self.kind!r}")
        if self.confidence not in CONFIDENCES:
            raise ValueError(f"confiance inconnue : {self.confidence!r}")


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


def fetch_extracts(titles: list[str], chars: int = EXTRACT_CHARS) -> dict[str, str]:
    """Récupère le chapeau des articles demandés.

    Le chapeau — première section, texte brut — est ce qu'un lecteur voit avant de décider
    s'il lit la suite. C'est la bonne granularité pour coder ce qui mobiliserait son
    attention.

    Args:
        titles: titres d'articles, tels qu'ils figurent dans le catalogue.
        chars: troncature du chapeau.

    Returns:
        Un dictionnaire titre → chapeau. Les articles sans extrait exploitable sont absents,
        et leur absence est une donnée : elle sera reportée, non comblée.
    """
    extracts: dict[str, str] = {}

    # L'API plafonne les extraits à vingt titres par appel pour un client anonyme.
    for start in range(0, len(titles), 20):
        batch = titles[start : start + 20]
        payload = _api(
            action="query",
            prop="extracts",
            exintro=1,
            explaintext=1,
            exlimit=20,
            redirects=1,
            titles="|".join(batch),
        )
        for page in payload.get("query", {}).get("pages", {}).values():
            text = (page.get("extract") or "").strip()
            if text:
                extracts[page["title"]] = " ".join(text.split())[:chars]
        time.sleep(_DELAY_SECONDS)

    return extracts


def save_extracts(extracts: dict[str, str], path: Path | None = None) -> Path:
    """Fige les chapeaux dans un fichier versionné."""
    destination = EXTRACTS_PATH if path is None else path
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {"chars": EXTRACT_CHARS, "extracts": dict(sorted(extracts.items()))}
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
    return destination


def load_extracts(path: Path | None = None) -> dict[str, str]:
    """Charge les chapeaux figés."""
    source = EXTRACTS_PATH if path is None else path
    if not source.exists():
        raise FileNotFoundError(
            f"chapeaux absents ({source}). Les récupérer avec scripts/fetch_extracts.py."
        )
    return dict(json.loads(source.read_text())["extracts"])


def digest_extracts(path: Path | None = None) -> str:
    """Empreinte SHA-256 du fichier de chapeaux.

    Elle est enregistrée avec les annotations : on sait ainsi de quel texte exact chaque
    codage provient, et une modification silencieuse des chapeaux se voit.
    """
    source = EXTRACTS_PATH if path is None else path
    return hashlib.sha256(source.read_bytes()).hexdigest()


def save_annotations(
    annotations: list[Annotation],
    extracts_digest: str,
    path: Path | None = None,
) -> Path:
    """Écrit les annotations et l'empreinte des chapeaux dont elles proviennent."""
    destination = ANNOTATIONS_PATH if path is None else path
    destination.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "rubric_version": RUBRIC_VERSION,
        "extracts_sha256": extracts_digest,
        "registers": list(REGISTERS),
        "kinds": list(KINDS),
        "annotations": [
            {
                "title": item.title,
                "register": item.register,
                "kind": item.kind,
                "confidence": item.confidence,
                "note": item.note,
            }
            for item in sorted(annotations, key=lambda item: item.title)
        ],
    }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
    return destination


def load_annotations(path: Path | None = None) -> dict[str, Annotation]:
    """Charge les annotations, indexées par titre.

    Raises:
        FileNotFoundError: si le fichier n'existe pas. Il n'est pas régénéré à la volée —
            une annotation manuelle ne se recalcule pas.
        ValueError: si la grille utilisée n'est pas :data:`RUBRIC_VERSION`.
    """
    source = ANNOTATIONS_PATH if path is None else path
    if not source.exists():
        raise FileNotFoundError(f"annotations absentes ({source}).")

    payload = json.loads(source.read_text())
    if payload.get("rubric_version") != RUBRIC_VERSION:
        raise ValueError(
            f"annotations produites avec la grille {payload.get('rubric_version')!r}, "
            f"la grille courante est {RUBRIC_VERSION!r}"
        )

    return {
        item["title"]: Annotation(
            title=item["title"],
            register=item["register"],
            kind=item["kind"],
            confidence=item.get("confidence", "sure"),
            note=item.get("note", ""),
        )
        for item in payload["annotations"]
    }


def annotated_entries(
    entries: list[CorpusEntry],
    annotations: dict[str, Annotation],
) -> list[CorpusEntry]:
    """Réétiquette un corpus avec les registres annotés à la main.

    Les sujets codés :data:`NEITHER` sont retirés — c'est la correction que l'annotation
    apporte. Ils ne disparaissent pas pour autant de l'analyse : ils restent décrits par
    :func:`confusion_matrix`, et le manifeste les conserve. Le type :class:`CorpusEntry` ne
    connaît que les deux registres comparables, et cet invariant est laissé intact.

    Args:
        entries: le corpus issu du catalogue, étiqueté par catégorie.
        annotations: le codage manuel, indexé par titre.

    Returns:
        Les entrées annotées, dans l'ordre d'entrée. Une entrée sans annotation est écartée
        et son absence doit être rapportée.
    """
    result: list[CorpusEntry] = []
    for entry in entries:
        annotation = annotations.get(entry.label)
        if annotation is None or annotation.register == NEITHER:
            continue
        result.append(
            CorpusEntry(
                project=entry.project,
                article=entry.article,
                label=entry.label,
                category=annotation.register,
            )
        )
    return result


def confusion_matrix(
    entries: list[CorpusEntry], annotations: dict[str, Annotation]
) -> dict[str, Counter[str]]:
    """Croise l'étiquette de catégorie et l'étiquette annotée.

    C'est la mesure directe du bruit d'étiquetage que le corpus étendu avait diagnostiqué
    sans pouvoir le quantifier.

    Args:
        entries: corpus étiqueté par catégorie.
        annotations: codage manuel.

    Returns:
        Un dictionnaire ``catégorie → compteur de registres annotés``.
    """
    matrix: dict[str, Counter[str]] = {}
    for entry in entries:
        annotation = annotations.get(entry.label)
        if annotation is None:
            continue
        matrix.setdefault(entry.category, Counter())[annotation.register] += 1
    return matrix
