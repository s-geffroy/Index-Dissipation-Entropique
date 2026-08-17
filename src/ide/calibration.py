"""Calibration empirique de la cinétique de résonance sur des séries d'attention.

Ce module répond au point le plus faible du travail : les paramètres du modèle de
:mod:`ide.resonance` n'avaient aucune procédure d'estimation sur données réelles. Le
critère d'instabilité :math:`\\gamma\\alpha > \\lambda`, présenté comme la recommandation
la plus opérationnelle du mémorandum, restait une inégalité formelle dont personne ne
savait si les systèmes réels s'y trouvaient.

Réduction au premier ordre
--------------------------

L'équation complète

.. math::
    \\ddot V + \\big(\\lambda - \\gamma\\alpha\\,\\sigma(V)\\big)\\dot V + \\omega_0^2 V = \\xi(t)

décrit un oscillateur, et son contenu oscillatoire n'est pertinent que dans le régime de
cycle limite. Pour un **pic d'attention isolé**, non oscillatoire, la dynamique se réduit
à sa forme du premier ordre — celle que le fil de travail d'origine écrivait avant de
passer au second ordre :

.. math:: \\frac{dV}{dt} = \\gamma\\alpha\\,\\sigma(V)\\,V - \\lambda V

Cette forme se sépare en deux régimes mesurables :

* **montée** — tant que :math:`V \\ll V_{\\text{sat}}`, la saturation est inactive
  (:math:`\\sigma \\approx 1`) et :math:`V \\propto e^{(\\gamma\\alpha - \\lambda)t}` ;
* **décroissance** — une fois la saturation atteinte ou le déclencheur passé,
  l'amplification s'éteint et :math:`V \\propto e^{-\\lambda t}`.

Deux régressions log-linéaires sur un même épisode suffisent donc :

.. math::
    \\lambda = r_{\\text{down}}, \\qquad
    \\gamma\\alpha = r_{\\text{up}} + r_{\\text{down}}, \\qquad
    \\frac{\\gamma\\alpha}{\\lambda} = 1 + \\frac{r_{\\text{up}}}{r_{\\text{down}}}

Ce que cette identification ne peut pas faire
---------------------------------------------

**Le critère de signe est vide.** Avec cette procédure,
:math:`\\gamma\\alpha/\\lambda > 1` dès que :math:`r_{\\text{up}} > 0`, c'est-à-dire pour
**tout contenu qui a connu une montée**. Constater que le seuil est franchi n'apprend donc
rien : tout épisode d'attention observable l'a franchi par construction.

La grandeur informative est la **marge** au-dessus du seuil, soit le rapport
:math:`r_{\\text{up}}/r_{\\text{down}}`. Cela déplace la recommandation du mémorandum : un
régulateur ne peut pas se contenter de vérifier le signe de
:math:`\\gamma\\alpha - \\lambda`, il doit **plafonner le rapport**.

**La mesure ne porte pas sur un algorithme de recommandation.** Les séries employées ici
(consultations d'articles encyclopédiques) sont dépourvues de moteur de recommandation :
le :math:`\\gamma` estimé est le gain composite de l'écosystème informationnel — moteurs
de recherche, partage social, couverture médiatique — et non la fonction de classement
d'une plateforme. C'est une borne écosystémique, pas un audit de plateforme.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = [
    "AttentionEpisode",
    "DetectionReport",
    "EpisodeCriteria",
    "ExponentialFit",
    "detect_episodes",
    "fit_exponential_rate",
    "rolling_baseline",
    "scan_series",
]

# Plancher appliqué au niveau de fond lors du test de proéminence, pour éviter une
# division par zéro sur un sujet dont l'attention habituelle est nulle. Il n'est
# volontairement PAS appliqué aux valeurs ajustées : rabattre une décroissance sur un
# plancher l'aplatirait et produirait un taux nul sans le signaler.
_BASELINE_FLOOR = 1.0


@dataclass(frozen=True)
class ExponentialFit:
    """Ajustement log-linéaire d'un segment de série temporelle.

    Attributes:
        rate: taux exponentiel par pas de temps (par jour pour des données
            quotidiennes). Positif pour une croissance, négatif pour une décroissance.
        intercept: logarithme de la valeur ajustée à l'origine du segment.
        r_squared: qualité de l'ajustement dans l'espace logarithmique.
        n_points: nombre de points utilisés.

    Examples:
        >>> import numpy as np
        >>> fit = fit_exponential_rate(np.exp(0.3 * np.arange(10)))
        >>> round(fit.rate, 6)
        0.3
        >>> round(fit.r_squared, 6)
        1.0
    """

    rate: float
    intercept: float
    r_squared: float
    n_points: int

    @property
    def timescale(self) -> float:
        """Temps caractéristique :math:`1/|r|`, en pas de temps.

        Pour une décroissance, c'est la durée au bout de laquelle l'attention retombe
        d'un facteur :math:`e` — l'échelle de l'oubli.
        """
        if self.rate == 0.0:
            return float("inf")

        return float(1.0 / abs(self.rate))

    @property
    def doubling_time(self) -> float:
        """Temps de doublement (croissance) ou de demi-vie (décroissance)."""
        return float(np.log(2.0) * self.timescale)


def fit_exponential_rate(values: np.ndarray) -> ExponentialFit:
    """Ajuste :math:`V(t) \\propto e^{rt}` par régression linéaire sur :math:`\\log V`.

    La régression est menée dans l'espace logarithmique, ce qui suppose un bruit
    multiplicatif — hypothèse raisonnable pour des comptages d'audience, dont la
    dispersion croît avec le niveau.

    Args:
        values: valeurs **strictement positives**, régulièrement espacées.

    Returns:
        L'ajustement, avec son :math:`r^2`.

    Raises:
        ValueError: si le segment compte moins de trois points, ou si une valeur est
            nulle ou négative. L'appelant doit avoir délimité une fenêtre valide plutôt
            que compter sur un rabattement silencieux, qui aplatirait la pente.

    Examples:
        Une décroissance donne un taux négatif :

        >>> import numpy as np
        >>> fit = fit_exponential_rate(np.exp(-0.1 * np.arange(20)))
        >>> round(fit.rate, 6)
        -0.1
    """
    series = np.asarray(values, dtype=float)

    if series.ndim != 1 or series.size < 3:
        raise ValueError("un ajustement exponentiel demande au moins 3 points")
    if np.any(series <= 0.0) or not np.all(np.isfinite(series)):
        raise ValueError("un ajustement logarithmique exige des valeurs finies et positives")

    times = np.arange(series.size, dtype=float)
    logarithms = np.log(series)

    slope, intercept = np.polyfit(times, logarithms, deg=1)

    residuals = logarithms - (slope * times + intercept)
    total_variation = float(np.sum((logarithms - logarithms.mean()) ** 2))

    # La platitude est testée sur l'étendue des logarithmes, non sur la variation totale :
    # celle-ci vaut typiquement 1e-30 sur une série constante — non nulle en arithmétique
    # flottante — et le rapport de deux résidus d'arrondi produirait un r² arbitraire.
    spread = float(np.ptp(logarithms))
    if spread <= 1e-12 * max(1.0, abs(float(logarithms.mean()))):
        # Série exactement plate en échelle logarithmique : la pente est nulle par
        # construction, et le résidu numérique de la régression n'est que du bruit
        # d'arrondi. On la fixe à zéro et on déclare l'ajustement sans pouvoir
        # explicatif, plutôt que parfait.
        return ExponentialFit(
            rate=0.0, intercept=float(intercept), r_squared=0.0, n_points=int(series.size)
        )

    return ExponentialFit(
        rate=float(slope),
        intercept=float(intercept),
        r_squared=1.0 - float(np.sum(residuals**2)) / total_variation,
        n_points=int(series.size),
    )


def rolling_baseline(views: np.ndarray, window: int = 181) -> np.ndarray:
    """Niveau d'attention de fond, par médiane glissante.

    La médiane, et non la moyenne : un pic d'attention est précisément la valeur
    aberrante que le niveau de fond ne doit pas absorber.

    La fenêtre est large — un semestre par défaut — pour une raison précise : un épisode
    peut s'étaler sur plusieurs semaines, et une fenêtre trop courte le verrait occuper
    la majorité de ses propres points. La médiane absorberait alors le pic qu'elle est
    censée servir de référence, et les taux ajustés seraient sous-estimés.

    Args:
        views: série de consultations quotidiennes.
        window: largeur de la fenêtre, en jours. Ramenée à un nombre impair.

    Returns:
        Le niveau de fond, de même longueur que l'entrée.

    Examples:
        >>> import numpy as np
        >>> flat = np.full(200, 50.0)
        >>> flat[100] = 5000.0
        >>> float(rolling_baseline(flat)[100])
        50.0
    """
    series = np.asarray(views, dtype=float)
    if series.ndim != 1 or series.size == 0:
        raise ValueError("la série doit être un vecteur non vide")
    if window < 3:
        raise ValueError("la fenêtre doit couvrir au moins 3 jours")

    span = window if window % 2 == 1 else window + 1
    half = span // 2
    # Bords prolongés par réflexion, pour que le niveau de fond soit défini partout
    # sans introduire de fausse chute aux extrémités.
    padded = np.pad(series, half, mode="reflect")
    windows = np.lib.stride_tricks.sliding_window_view(padded, span)

    return np.nanmedian(windows, axis=-1)


@dataclass(frozen=True)
class EpisodeCriteria:
    """Critères de détection et de validation d'un épisode d'attention.

    Chaque seuil est un choix méthodologique, et non un réglage neutre : les valeurs par
    défaut sont celles employées dans le notebook 09, et l'analyse doit rester stable
    quand on les fait varier — c'est ce que vérifie l'étude de sensibilité.

    Args:
        prominence: facteur multiplicatif minimal du pic par rapport au niveau de fond.
            À 4, un épisode doit quadrupler l'attention habituelle du sujet.
        min_points: nombre minimal de points de part et d'autre du pic. En deçà de 4,
            une pente ajustée sur des données quotidiennes n'est pas identifiable.
        min_r_squared: qualité minimale exigée des deux ajustements. Écarte les épisodes
            dont la forme n'est pas exponentielle — plateaux, pics multiples,
            décroissances en escalier.
        max_rise: durée maximale de la fenêtre de montée, en jours.
        max_decay: durée maximale de la fenêtre de décroissance, en jours.
        return_factor: seuil de retour au calme, en multiple du niveau de fond. La
            fenêtre de décroissance s'arrête quand l'attention repasse en dessous.
        separation: nombre minimal de jours entre deux pics retenus, pour ne pas
            compter plusieurs fois le même épisode.
        baseline_window: largeur de la fenêtre du niveau de fond.
        min_peak_views: trafic minimal au sommet du pic, en consultations par jour.

            Ce seuil contrôle le **bruit de comptage**, non l'intérêt du sujet : les
            consultations suivant une loi de Poisson, l'incertitude relative au sommet
            vaut :math:`1/\\sqrt{n}`, soit 7 % à 200 consultations et 38 % à 7. En deçà,
            la pente ajustée n'est plus distinguable du bruit, quelle que soit la qualité
            apparente de l'ajustement.
        horizon: si renseigné, force les deux fenêtres à cette durée exacte, en jours.

            Ce réglage répond à un **artefact grave de l'estimateur adaptatif**. Quand les
            fenêtres sont délimitées par le retour au niveau de fond, leur durée varie
            d'un épisode à l'autre — de six à quarante-six jours dans le corpus — et
            :math:`\\lambda`, ajusté sur une exponentielle unique, décroît mécaniquement
            avec cette durée : la corrélation de rang mesurée atteint :math:`-0{,}94`. Le
            rapport :math:`\\gamma\\alpha/\\lambda` reflète alors autant la longueur de la
            fenêtre que la dynamique du sujet.

            À horizon fixe, :math:`\\lambda` devient « le taux d'oubli moyen sur les
            :math:`H` premiers jours après le pic » : une grandeur comparable entre
            épisodes. Le prix est le rejet des épisodes trop brefs pour couvrir
            l'horizon.
    """

    prominence: float = 4.0
    min_points: int = 4
    min_r_squared: float = 0.80
    max_rise: int = 21
    max_decay: int = 45
    return_factor: float = 1.5
    separation: int = 60
    baseline_window: int = 181
    min_peak_views: float = 200.0
    horizon: int | None = None

    def __post_init__(self) -> None:
        if self.prominence <= 1.0:
            raise ValueError("la proéminence doit être strictement supérieure à 1")
        if self.min_points < 3:
            raise ValueError("un ajustement demande au moins 3 points")
        if not 0.0 <= self.min_r_squared <= 1.0:
            raise ValueError("le r² minimal doit appartenir à [0, 1]")
        if self.max_rise < self.min_points or self.max_decay < self.min_points:
            raise ValueError("les fenêtres doivent pouvoir contenir min_points")
        if self.return_factor < 1.0:
            raise ValueError("le seuil de retour au calme doit être au moins 1")
        if self.min_peak_views < 0.0:
            raise ValueError("le trafic minimal ne peut pas être négatif")
        if self.horizon is not None and self.horizon < self.min_points:
            raise ValueError("l'horizon fixe doit couvrir au moins min_points")


@dataclass(frozen=True)
class AttentionEpisode:
    """Un pic d'attention, avec sa montée et sa décroissance ajustées.

    Attributes:
        label: identifiant de la série d'origine.
        peak_index: position du maximum dans la série.
        peak_value: valeur au maximum.
        baseline: niveau de fond local.
        rise: ajustement de la phase de montée.
        decay: ajustement de la phase de décroissance.
    """

    label: str
    peak_index: int
    peak_value: float
    baseline: float
    rise: ExponentialFit
    decay: ExponentialFit

    @property
    def damping(self) -> float:
        """Amortissement naturel :math:`\\lambda`, l'oubli, par jour."""
        return float(-self.decay.rate)

    @property
    def amplification(self) -> float:
        """Amplification :math:`\\gamma\\alpha`, par jour."""
        return float(self.rise.rate + self.damping)

    @property
    def resonance_ratio(self) -> float:
        """Rapport :math:`\\gamma\\alpha/\\lambda = 1 + r_{\\text{up}}/r_{\\text{down}}`.

        C'est la grandeur informative : la marge au-dessus du seuil d'instabilité. Un
        rapport de 3 signifie que l'amplification est trois fois plus rapide que l'oubli.
        """
        if self.damping <= 0.0:
            # Décroissance nulle ou croissante : l'épisode ne s'est pas refermé et
            # l'oubli n'est pas mesurable sur la fenêtre observée.
            return float("inf")

        return float(self.amplification / self.damping)

    @property
    def is_resonant(self) -> bool:
        """Vrai si :math:`\\gamma\\alpha > \\lambda`.

        Rappel de la limite d'identification : cette condition est équivalente à
        « la montée a été observée », donc satisfaite par construction pour tout épisode
        détecté. Elle est exposée pour la traçabilité, non comme un résultat.
        """
        return self.amplification > self.damping

    @property
    def amplitude(self) -> float:
        """Amplitude du pic, en multiple du niveau de fond."""
        if self.baseline <= 0.0:
            return float("inf")

        return float(self.peak_value / self.baseline)


#: Motifs de rejet d'un pic candidat, dans l'ordre où ils sont évalués.
_REJECTIONS = ("proximité", "trafic", "fenêtre", "forme")


@dataclass(frozen=True)
class DetectionReport:
    """Compte rendu de la détection sur une série.

    Les épisodes écartés sont comptés par motif. C'est délibéré : une série sans épisode
    exploitable est un résultat, et la raison de cette absence détermine s'il s'agit d'une
    propriété du sujet ou d'une limite de la méthode.

    Attributes:
        label: identifiant de la série.
        episodes: épisodes retenus, par ordre chronologique.
        candidates: nombre de pics ayant franchi le critère de proéminence.
        rejections: nombre de rejets par motif —

            * ``proximité`` : pic trop proche d'un épisode déjà retenu ;
            * ``trafic`` : sommet en dessous du seuil de bruit de comptage ;
            * ``fenêtre`` : montée ou décroissance trop courte pour ajuster une pente ;
            * ``forme`` : ajustement de qualité insuffisante, ou pente du mauvais signe —
              typiquement un plateau, un pic multiple ou une décroissance en escalier.
    """

    label: str
    episodes: list[AttentionEpisode]
    candidates: int
    rejections: dict[str, int]

    @property
    def is_exploitable(self) -> bool:
        """Vrai si au moins un épisode a été retenu."""
        return len(self.episodes) > 0

    @property
    def dominant_rejection(self) -> str | None:
        """Motif de rejet majoritaire, ou ``None`` si la série a livré des épisodes."""
        if self.is_exploitable or not any(self.rejections.values()):
            return None

        return max(self.rejections, key=lambda motif: self.rejections[motif])


def _fit_window(
    excess: np.ndarray,
    criteria: EpisodeCriteria,
    peak_index: int,
) -> tuple[ExponentialFit, ExponentialFit] | str:
    """Ajuste les deux phases autour d'un pic, ou renvoie le motif de rejet."""
    limit = len(excess) - 1

    if criteria.horizon is not None:
        # Horizon fixe : les deux fenêtres ont exactement la même durée pour tous les
        # épisodes, au prix du rejet de ceux qui ne la couvrent pas entièrement.
        span = criteria.horizon
        start, end = peak_index - span, peak_index + span
        if start < 0 or end > limit:
            return "fenêtre"
        if np.any(excess[start : end + 1] <= 0.0):
            return "fenêtre"
    else:
        # Estimateur adaptatif : les fenêtres suivent la forme de l'épisode, délimitées
        # par le retour au niveau de fond.
        start = peak_index
        while start > 0 and peak_index - start < criteria.max_rise and excess[start - 1] > 0.0:
            start -= 1

        end = peak_index
        while end < limit and end - peak_index < criteria.max_decay and excess[end + 1] > 0.0:
            end += 1

    rise_segment = excess[start : peak_index + 1]
    decay_segment = excess[peak_index : end + 1]

    if rise_segment.size < criteria.min_points or decay_segment.size < criteria.min_points:
        return "fenêtre"

    rise = fit_exponential_rate(rise_segment)
    decay = fit_exponential_rate(decay_segment)

    if rise.r_squared < criteria.min_r_squared or decay.r_squared < criteria.min_r_squared:
        return "forme"
    # Une montée qui décroît ou une décroissance qui croît signalent un pic mal isolé.
    if rise.rate <= 0.0 or decay.rate >= 0.0:
        return "forme"

    return rise, decay


def scan_series(
    views: np.ndarray,
    label: str = "série",
    criteria: EpisodeCriteria | None = None,
) -> DetectionReport:
    """Détecte les épisodes d'une série et rend compte des pics écartés.

    La procédure : soustraction du niveau de fond, recherche des maxima suffisamment
    proéminents, puis ajustement log-linéaire de part et d'autre de chaque maximum.

    Args:
        views: consultations quotidiennes, sans valeur manquante.
        label: identifiant reporté sur les épisodes et le compte rendu.
        criteria: critères de détection. Par défaut, ceux du notebook 09.

    Returns:
        Le compte rendu complet, épisodes retenus et rejets par motif.
    """
    series = np.asarray(views, dtype=float)
    if series.ndim != 1 or series.size < 30:
        raise ValueError("la détection demande une série d'au moins 30 jours")

    rules = criteria or EpisodeCriteria()
    baseline = rolling_baseline(series, window=rules.baseline_window)
    excess = series - baseline

    # Un pic candidat dépasse la proéminence exigée et domine ses voisins immédiats.
    is_prominent = series >= rules.prominence * np.clip(baseline, _BASELINE_FLOOR, None)
    interior = np.zeros_like(series, dtype=bool)
    interior[1:-1] = (series[1:-1] >= series[:-2]) & (series[1:-1] >= series[2:])
    candidates = np.flatnonzero(is_prominent & interior)

    episodes: list[AttentionEpisode] = []
    rejections = dict.fromkeys(_REJECTIONS, 0)

    # Les candidats sont examinés du plus fort au plus faible : en cas de pics
    # rapprochés, l'épisode retenu est le principal, non le premier venu.
    for peak_index in sorted(candidates, key=lambda index: -series[index]):
        position = int(peak_index)

        if any(abs(position - other.peak_index) < rules.separation for other in episodes):
            rejections["proximité"] += 1
            continue

        if series[position] < rules.min_peak_views:
            rejections["trafic"] += 1
            continue

        fitted = _fit_window(excess, rules, position)
        if isinstance(fitted, str):
            rejections[fitted] += 1
            continue

        rise, decay = fitted
        episodes.append(
            AttentionEpisode(
                label=label,
                peak_index=position,
                peak_value=float(series[position]),
                baseline=float(baseline[position]),
                rise=rise,
                decay=decay,
            )
        )

    return DetectionReport(
        label=label,
        episodes=sorted(episodes, key=lambda episode: episode.peak_index),
        candidates=int(candidates.size),
        rejections=rejections,
    )


def detect_episodes(
    views: np.ndarray,
    label: str = "série",
    criteria: EpisodeCriteria | None = None,
) -> list[AttentionEpisode]:
    """Épisodes retenus d'une série, sans le détail des rejets.

    Raccourci sur :func:`scan_series` pour les usages qui n'ont pas besoin du compte rendu.

    Returns:
        Les épisodes retenus, par ordre chronologique. La liste peut être vide : c'est le
        cas normal pour un sujet sans pic net, et cette absence est une donnée en soi.

    Examples:
        Un pic exponentiel synthétique est retrouvé, avec ses deux taux :

        >>> import numpy as np
        >>> series = np.full(400, 100.0)
        >>> rise = 100.0 * np.exp(0.5 * np.arange(15))
        >>> series[186:201] += rise
        >>> series[201:241] += rise[-1] * np.exp(-0.2 * np.arange(1, 41))
        >>> episodes = detect_episodes(series, label="test")
        >>> len(episodes)
        1
        >>> round(episodes[0].rise.rate, 3), round(episodes[0].damping, 3)
        (0.5, 0.2)
        >>> round(episodes[0].resonance_ratio, 1)
        3.5
    """
    return scan_series(views, label=label, criteria=criteria).episodes
