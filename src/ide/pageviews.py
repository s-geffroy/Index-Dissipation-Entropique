"""Accès aux séries de consultation de Wikipédia, avec cache sur disque.

Pourquoi cette source
---------------------

La calibration du modèle de résonance demande des séries temporelles d'attention
publiques, complètes et horodatées. L'API de consultations de Wikimedia est la seule qui
réunisse les quatre conditions nécessaires : **accès libre** sans authentification ni clé,
**granularité quotidienne**, **profondeur historique** depuis juillet 2015, et
**stabilité** — les archives Reddit ont fermé, l'API de X est devenue payante, et Google
Trends ne publie que des indices normalisés dont l'échelle absolue est masquée.

Ce que la source n'est pas
--------------------------

Wikipédia **n'a pas d'algorithme de recommandation**. Le gain :math:`\\gamma` estimé sur
ces séries est celui de l'écosystème informationnel dans son ensemble — moteurs de
recherche, partage social, reprise médiatique — et non la fonction de classement d'une
plateforme. C'est une mesure écosystémique, à ne pas confondre avec l'audit de plateforme
que recommande le mémorandum.

Par ailleurs, une consultation n'est pas une exposition : le modèle décrit la visibilité
:math:`V` d'un contenu, c'est-à-dire ce qui est *servi*, tandis que ces séries mesurent ce
qui est *consulté*. C'est un observable en aval, dont la dynamique est celle de l'attention
plutôt que celle de la diffusion.

Le cache
--------

Les séries téléchargées sont enregistrées sous ``data/pageviews/`` et **versionnées dans
le dépôt**. L'analyse du notebook 09 est donc reproductible hors ligne, et un résultat
publié ne dépend pas de la disponibilité future d'un service tiers. Le format de cache est
compact — une date de départ et un tableau d'entiers — plutôt que la réponse brute de
l'API, qui répète ses métadonnées à chaque jour.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import numpy as np

__all__ = [
    "CACHE_DIRECTORY",
    "PageviewSeries",
    "fetch_pageviews",
    "load_cached",
    "load_or_fetch",
    "save_cached",
]

#: Emplacement du cache versionné, à la racine du dépôt.
CACHE_DIRECTORY = Path(__file__).resolve().parents[2] / "data" / "pageviews"

_ENDPOINT = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"

#: Filtre d'agent appliqué par défaut. Wikimedia distingue les consultations humaines des
#: passages de robots et d'outils automatisés. Le modèle décrit une dynamique d'attention
#: humaine : retenir ``all-agents`` y injecterait des artefacts massifs — l'article
#: OSIRIS-REx présente ainsi un pic à 17 millions de consultations en une journée, sans
#: aucun rapport avec un épisode d'attention réel.
DEFAULT_AGENT = "user"

_VALID_AGENTS = ("user", "all-agents", "spider", "automated")

# L'API de Wikimedia demande un agent utilisateur descriptif et limite le débit ; les
# requêtes anonymes trop rapprochées reçoivent un code 429.
_USER_AGENT = "IDE-research/0.1 (https://github.com/s-geffroy/Index-Dissipation-Entropique)"


@dataclass(frozen=True)
class PageviewSeries:
    """Série de consultations quotidiennes d'un article.

    Attributes:
        project: projet Wikimedia, par exemple ``"fr.wikipedia"``.
        article: titre de l'article, tel qu'il apparaît dans l'URL.
        start: premier jour de la série.
        views: consultations quotidiennes. Les jours manquants valent ``NaN`` — l'API
            omet purement et simplement les jours sans données, et les remplacer par zéro
            introduirait de faux effondrements d'attention.
        agent: filtre d'agent appliqué à la requête. Voir :data:`DEFAULT_AGENT`.
    """

    project: str
    article: str
    start: date
    views: np.ndarray
    agent: str = DEFAULT_AGENT

    def __post_init__(self) -> None:
        if self.views.ndim != 1 or self.views.size == 0:
            raise ValueError("une série de consultations doit être un vecteur non vide")
        if self.agent not in _VALID_AGENTS:
            raise ValueError(f"agent inconnu : {self.agent}")

    @property
    def end(self) -> date:
        """Dernier jour de la série."""
        return self.start + timedelta(days=int(self.views.size) - 1)

    @property
    def label(self) -> str:
        """Identifiant lisible, projet inclus."""
        return f"{self.article} ({self.project})"

    def day(self, index: int) -> date:
        """Date correspondant à une position dans la série."""
        if not 0 <= index < self.views.size:
            raise IndexError("position hors de la série")

        return self.start + timedelta(days=int(index))

    def filled(self) -> np.ndarray:
        """Série avec les jours manquants interpolés linéairement.

        L'interpolation est nécessaire aux ajustements, qui supposent un pas régulier.
        Elle reste préférable à l'exclusion des trous, qui décalerait l'échelle de temps
        et donc les taux estimés.
        """
        series = np.array(self.views, dtype=float)
        missing = np.isnan(series)

        if not missing.any():
            return series
        if missing.all():
            raise ValueError("la série ne contient aucune donnée")

        positions = np.arange(series.size, dtype=float)
        series[missing] = np.interp(positions[missing], positions[~missing], series[~missing])

        return series


def _slug(project: str, article: str, cache_dir: Path | None = None) -> Path:
    """Chemin de cache d'une série. Les caractères d'URL sont conservés tels quels."""
    root = CACHE_DIRECTORY if cache_dir is None else cache_dir

    return root / project / f"{article}.json"


def save_cached(series: PageviewSeries, cache_dir: Path | None = None) -> Path:
    """Enregistre une série dans le cache et renvoie le chemin du fichier."""
    destination = _slug(series.project, series.article, cache_dir)
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "project": series.project,
        "article": series.article,
        "agent": series.agent,
        "start": series.start.isoformat(),
        "views": [None if np.isnan(value) else int(value) for value in series.views],
    }
    destination.write_text(json.dumps(payload, separators=(",", ":")) + "\n")

    return destination


def load_cached(
    project: str, article: str, cache_dir: Path | None = None
) -> PageviewSeries | None:
    """Charge une série depuis le cache, ou renvoie ``None`` si elle n'y figure pas."""
    source = _slug(project, article, cache_dir)

    if not source.exists():
        return None

    payload = json.loads(source.read_text())
    views = np.array(
        [np.nan if value is None else float(value) for value in payload["views"]],
        dtype=float,
    )

    return PageviewSeries(
        project=payload["project"],
        article=payload["article"],
        start=date.fromisoformat(payload["start"]),
        views=views,
        agent=payload.get("agent", "all-agents"),
    )


def fetch_pageviews(
    project: str,
    article: str,
    start: date,
    end: date,
    agent: str = DEFAULT_AGENT,
    timeout: float = 30.0,
) -> PageviewSeries:
    """Télécharge une série de consultations quotidiennes depuis l'API de Wikimedia.

    Args:
        project: projet, par exemple ``"en.wikipedia"``.
        article: titre de l'article, encodé comme dans l'URL.
        start: premier jour demandé.
        end: dernier jour demandé.
        agent: filtre d'agent. ``"user"`` par défaut, pour exclure les robots.
        timeout: délai maximal de la requête, en secondes.

    Returns:
        La série, les jours absents de la réponse étant marqués ``NaN``.

    Raises:
        RuntimeError: si l'API refuse la requête. Le code 429 signale une limitation de
            débit : il faut espacer les appels, non les réessayer immédiatement.
        ValueError: si la réponse ne contient aucune donnée.
    """
    if end < start:
        raise ValueError("la date de fin précède la date de début")
    if agent not in _VALID_AGENTS:
        raise ValueError(f"agent inconnu : {agent}")

    url = (
        f"{_ENDPOINT}/{project}/all-access/{agent}/{article}/daily/"
        f"{start.strftime('%Y%m%d')}/{end.strftime('%Y%m%d')}"
    )
    request = Request(url, headers={"User-Agent": _USER_AGENT, "Accept": "application/json"})

    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 — URL construite ici
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = "débit limité par l'API" if error.code == 429 else error.reason
        raise RuntimeError(f"{project}/{article} : HTTP {error.code} — {detail}") from error
    except URLError as error:
        raise RuntimeError(f"{project}/{article} : réseau indisponible — {error.reason}") from error

    items = payload.get("items", [])
    if not items:
        raise ValueError(f"{project}/{article} : aucune donnée sur la période demandée")

    span = (end - start).days + 1
    views = np.full(span, np.nan)
    for item in items:
        # Les horodatages de l'API sont au format YYYYMMDD00.
        stamp = item["timestamp"]
        day = date(int(stamp[0:4]), int(stamp[4:6]), int(stamp[6:8]))
        offset = (day - start).days
        if 0 <= offset < span:
            views[offset] = float(item["views"])

    return PageviewSeries(
        project=project, article=article, start=start, views=views, agent=agent
    )


def load_or_fetch(
    project: str,
    article: str,
    start: date,
    end: date,
    agent: str = DEFAULT_AGENT,
    cache_dir: Path | None = None,
    allow_network: bool = False,
) -> PageviewSeries:
    """Charge une série depuis le cache, en la téléchargeant si nécessaire.

    Le téléchargement doit être demandé explicitement. C'est délibéré : les notebooks et
    l'intégration continue doivent échouer de façon lisible si le cache est incomplet,
    plutôt que dépendre silencieusement d'un service extérieur.

    Args:
        project: projet Wikimedia.
        article: titre de l'article.
        start: premier jour demandé.
        end: dernier jour demandé.
        cache_dir: emplacement du cache. Par défaut, ``data/pageviews/``.
        allow_network: autorise le téléchargement en cas d'absence du cache.

    Raises:
        FileNotFoundError: si la série n'est pas en cache et que le réseau n'est pas
            autorisé.
    """
    cached = load_cached(project, article, cache_dir=cache_dir)
    if cached is not None:
        if cached.agent != agent:
            # Comparer des séries filtrées différemment fausserait l'analyse en silence.
            raise ValueError(
                f"{project}/{article} : le cache contient l'agent '{cached.agent}', "
                f"or '{agent}' est demandé. Relancer le script de collecte avec --force."
            )
        return cached

    if not allow_network:
        raise FileNotFoundError(
            f"{project}/{article} absent du cache. "
            "Relancer scripts/fetch_pageviews.py pour le constituer."
        )

    series = fetch_pageviews(project, article, start, end, agent=agent)
    save_cached(series, cache_dir=cache_dir)

    return series
