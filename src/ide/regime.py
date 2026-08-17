"""Détection de changement de régime et identification du rapport d'amplification.

Pourquoi ce module existe
-------------------------

La calibration par pic (:mod:`ide.calibration`) a livré un chiffre, mais elle a surtout
révélé sa propre limite : elle ne voit que les emballements passagers. Onze des vingt-quatre
sujets du corpus n'ont livré aucun épisode exploitable, et ce sont **les cas archétypaux** —
QAnon, désinformation sanitaire, hésitation vaccinale. Leur attention ne forme pas un pic
suivi d'une décroissance : elle **change de niveau et s'installe**. Le niveau de fond
glissant suit ce palier, et le critère de proéminence n'est jamais franchi.

Un modèle de la polarisation qui ne mesure que les flambées passagères n'atteint pas son
objet. Ce module traite l'autre cas.

Pourquoi l'estimateur par pic ne peut pas être réutilisé
--------------------------------------------------------

L'identification par pic repose sur deux pentes : une montée à
:math:`\\gamma\\alpha - \\lambda` et une décroissance à :math:`\\lambda`. Dans un régime
installé, **la décroissance n'existe pas** : le système est à son point fixe, où par
définition :math:`\\gamma\\alpha\\,\\sigma(V^*) = \\lambda`. Le niveau du palier ne dit donc
rien à lui seul, et il n'y a pas de seconde pente à mesurer.

L'information est ailleurs : dans la **forme de la transition**. Elle contraint les trois
paramètres à la fois, parce qu'elle traverse tout le domaine de la saturation.

Identification : linéaire en les paramètres
-------------------------------------------

Avec :math:`W = V - V_{\\text{avant}}` l'excédent au-dessus de l'ancien niveau, la réduction
au premier ordre s'écrit

.. math:: \\frac{\\dot W}{W} = \\frac{\\gamma\\alpha}{1 + (W/W_{\\text{sat}})^2} - \\lambda

En posant :math:`y = \\dot W / W` et :math:`x = W^2`, un réarrangement **exact** — sans
approximation ni développement limité — donne une forme linéaire en trois coefficients :

.. math:: y = A - B\\,xy - C\\,x
   \\qquad\\text{avec}\\qquad
   A = \\gamma\\alpha - \\lambda, \\quad B = \\frac{1}{W_{\\text{sat}}^2},
   \\quad C = \\frac{\\lambda}{W_{\\text{sat}}^2}

d'où :math:`\\lambda = C/B`, :math:`\\gamma\\alpha = A + C/B`, et

.. math:: \\frac{\\gamma\\alpha}{\\lambda} = 1 + \\frac{AB}{C}

Cette régression retrouve les trois paramètres à la précision machine sur une trajectoire
propre, y compris pour :math:`\\rho = 40`. Elle sert ici d'**initialisation**, et non
d'estimateur final, pour une raison précise : :math:`y` apparaît à la fois comme réponse et
dans le régresseur :math:`-xy`, et il est obtenu en dérivant des données bruitées. C'est un
problème d'erreurs sur les variables, et il est dévastateur — à un bruit multiplicatif de
10 %, l'estimation de :math:`\\rho` passe de 5,0 à 1,7.

Estimation retenue : ajustement de trajectoire
----------------------------------------------

L'estimateur final n'utilise **aucune dérivée**. Il intègre l'équation et ajuste la
trajectoire aux observations en échelle logarithmique, ce qui correspond au bruit
multiplicatif des données d'audience.

La récupération sur trajectoires de synthèse montre qu'il est **quasi non biaisé** jusqu'à
35 % de bruit multiplicatif — les facteurs mesurés vont de 1,00 à 1,07, et leur sens dépend
de :math:`\\rho` plutôt que du bruit. Ce n'est donc pas le biais qui limite l'estimation mais
sa **dispersion**, qui croît comme le double de la dispersion résiduelle
(:func:`expected_precision`). Au-delà d'une dispersion résiduelle de 30 %, l'ajustement est
refusé plutôt que rapporté avec une barre d'erreur illusoire.

.. note::
    Une première version de ce module publiait une table de correction de biais indiquant
    une sous-estimation de 20 % à 10 % de bruit. Cette table était fausse : elle provenait
    d'un prototype dont l'initialisation, un lissage par moyenne glissante aux bords
    corrompus, dégradait l'ajustement bien plus que le bruit lui-même. Corriger
    l'initialisation — filtre de Savitzky-Golay — a supprimé le biais qu'il fallait soi-disant
    corriger. C'est une illustration exacte du principe que ce dépôt applique par ailleurs :
    un chiffre non mesuré ne doit pas être publié, même quand il paraît prudent.

Ce que cet estimateur suppose, et que le précédent ne supposait pas
-------------------------------------------------------------------

L'identification par pic ne dépendait pas de la **forme** de la saturation : elle n'utilisait
que les deux régimes asymptotiques. Ici, la forme intervient — et bien plus profondément
qu'un simple biais.

Sous la forme du modèle, :math:`\\sigma = 1/(1+(W/W_{\\text{sat}})^2)`, les trois paramètres
façonnent la courbe de trois manières distinctes et sont séparables : la récupération est
exacte sur trajectoire propre, y compris pour :math:`\\rho = 40`.

Sous une saturation **logistique** :math:`\\sigma = 1 - W/W_{\\text{sat}}`, en revanche,
l'équation se réduit à

.. math:: \\dot W = (\\gamma\\alpha - \\lambda)\\,W\\left(1 - \\frac{W}{K}\\right),
   \\qquad K = W_{\\text{sat}}\\left(1 - \\frac{\\lambda}{\\gamma\\alpha}\\right)

La trajectoire ne dépend plus que de **deux** combinaisons des trois paramètres. Le rapport
:math:`\\gamma\\alpha/\\lambda` y est alors **structurellement non identifiable** : deux
triplets de rapports 5,0 et 1,67 produisent exactement la même courbe, et aucune précision
de mesure n'y changera rien. Le test
``test_logistic_saturation_makes_the_ratio_unidentifiable`` en fait la démonstration.

La conséquence dépasse le choix d'un estimateur : **l'identifiabilité de**
:math:`\\gamma\\alpha/\\lambda` **sur un changement de régime n'est pas une propriété des
données, c'est une hypothèse sur la forme de la saturation.** Les deux formes sont donc
ajustées côte à côte, et :meth:`RegimeShift.is_form_identified` signale les cas où les
données ne tranchent pas — cas dans lesquels le rapport rapporté ne mesure rien.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares
from scipy.signal import savgol_filter

__all__ = [
    "RegimeCriteria",
    "RegimeReport",
    "RegimeShift",
    "SaturatedFit",
    "SaturationForm",
    "detect_change_points",
    "expected_precision",
    "fit_saturated_growth",
    "scan_regime_shifts",
    "weekly_adjust",
]

SaturationForm = Literal["quadratic", "logistic"]

# Plancher de sécurité avant tout passage au logarithme.
_FLOOR = 1e-9

# Dispersion résiduelle au-delà de laquelle les paramètres sont refusés. Le seuil est
# délibérément sévère : la récupération synthétique montre qu'à 15 % de dispersion,
# l'incertitude relative sur rho atteint déjà 77 % (voir :func:`expected_precision`).
# Au-delà, un chiffre publié n'informerait sur rien — et les séries réelles se situent
# précisément au-delà, ce qui est le résultat principal de ce module.
_MAX_SCATTER = 0.15


def weekly_adjust(views: np.ndarray) -> np.ndarray:
    """Retire la périodicité hebdomadaire d'une série de consultations.

    Le rythme jour de semaine / week-end est un effet **systématique**, non du bruit : il
    atteint couramment 20 à 30 % d'amplitude sur une audience encyclopédique. Le laisser en
    place le fait passer pour de la dispersion aléatoire, or l'estimateur de trajectoire est
    précisément biaisé par la dispersion. Le retirer est donc la préparation la plus
    rentable.

    La correction est multiplicative : pour chaque jour de la semaine, on calcule le rapport
    médian entre la valeur observée et une moyenne glissante sur sept jours, puis on divise.

    Args:
        views: série quotidienne, sans valeur manquante.

    Returns:
        La série corrigée, de même longueur et de même niveau moyen.

    Examples:
        Une série plate portant une modulation hebdomadaire pure est rendue plate :

        >>> import numpy as np
        >>> weekday = np.array([1.3, 1.2, 1.1, 1.0, 0.9, 0.7, 0.8])
        >>> raw = 1000.0 * np.tile(weekday, 40)
        >>> adjusted = weekly_adjust(raw)
        >>> bool(adjusted[7:-7].std() < 1.0)
        True
    """
    series = np.asarray(views, dtype=float)
    if series.ndim != 1 or series.size < 28:
        raise ValueError("la correction hebdomadaire demande au moins quatre semaines")
    if np.any(series <= 0.0):
        raise ValueError("la série doit être strictement positive")

    kernel = np.ones(7) / 7.0
    padded = np.pad(series, 3, mode="reflect")
    trend = np.convolve(padded, kernel, mode="valid")

    ratios = series / np.clip(trend, _FLOOR, None)
    factors = np.ones(7)
    for weekday in range(7):
        sample = ratios[weekday::7]
        if sample.size:
            factors[weekday] = float(np.median(sample))

    # Normalisation : la correction ne doit pas déplacer le niveau global de la série.
    factors /= float(np.exp(np.mean(np.log(np.clip(factors, _FLOOR, None)))))

    return series / factors[np.arange(series.size) % 7]


def _segment_cost(cumulative: np.ndarray, squared: np.ndarray, start: int, end: int) -> float:
    """Coût d'un segment : somme des écarts au carré à sa moyenne, en temps constant."""
    count = end - start
    if count <= 0:
        return 0.0
    total = cumulative[end] - cumulative[start]

    return float(squared[end] - squared[start] - total * total / count)


def detect_change_points(
    values: np.ndarray,
    penalty: float | None = None,
    min_segment: int = 60,
    max_points: int = 6,
) -> list[int]:
    """Détecte des ruptures de niveau par segmentation binaire.

    La segmentation opère sur les **logarithmes** des consultations : une audience évolue de
    façon multiplicative, et un doublement doit compter autant qu'il survienne à mille ou à
    cent mille consultations par jour.

    À chaque étape, la coupure qui réduit le plus le coût quadratique total est retenue, si et
    seulement si cette réduction dépasse la pénalité. La procédure s'arrête d'elle-même,
    ce qui évite de fixer à l'avance un nombre de ruptures.

    Args:
        values: série strictement positive.
        penalty: pénalité par rupture. Par défaut, :math:`3\\,\\hat\\sigma^2 \\ln n`, où
            :math:`\\hat\\sigma` est estimé de façon robuste sur les différences premières —
            un estimateur insensible aux ruptures elles-mêmes, contrairement à l'écart-type
            global qu'elles gonfleraient.
        min_segment: longueur minimale d'un segment, en jours. Une rupture ne se distingue
            d'un pic que si le nouveau niveau se maintient.
        max_points: nombre maximal de ruptures retenues.

    Returns:
        Les positions de rupture, par ordre croissant.

    Examples:
        >>> import numpy as np
        >>> series = np.concatenate([np.full(300, 500.0), np.full(300, 4_000.0)])
        >>> detect_change_points(series)
        [300]
        >>> detect_change_points(np.full(600, 500.0))
        []
    """
    series = np.asarray(values, dtype=float)
    if series.ndim != 1 or series.size < 2 * min_segment:
        raise ValueError("série trop courte pour la longueur de segment demandée")
    if np.any(series <= 0.0):
        raise ValueError("la série doit être strictement positive")
    if min_segment < 2 or max_points < 1:
        raise ValueError("min_segment ≥ 2 et max_points ≥ 1 sont requis")

    signal = np.log(series)
    count = signal.size

    if penalty is None:
        # Écart-type robuste des différences premières : la médiane des écarts absolus
        # divisée par sqrt(2) corrige le facteur introduit par la différenciation.
        deviation = float(np.median(np.abs(np.diff(signal)))) / (0.6745 * np.sqrt(2.0))
        penalty = 3.0 * max(deviation, 1e-6) ** 2 * np.log(count)

    cumulative = np.concatenate([[0.0], np.cumsum(signal)])
    squared = np.concatenate([[0.0], np.cumsum(signal**2)])

    boundaries = [0, count]
    found: list[int] = []

    while len(found) < max_points:
        best_gain, best_split = 0.0, None

        for left, right in zip(boundaries[:-1], boundaries[1:], strict=True):
            if right - left < 2 * min_segment:
                continue
            parent = _segment_cost(cumulative, squared, left, right)
            for split in range(left + min_segment, right - min_segment + 1):
                gain = parent - (
                    _segment_cost(cumulative, squared, left, split)
                    + _segment_cost(cumulative, squared, split, right)
                )
                if gain > best_gain:
                    best_gain, best_split = gain, split

        if best_split is None or best_gain <= penalty:
            break

        found.append(best_split)
        boundaries = sorted([*boundaries, best_split])

    return sorted(found)


def _saturation(excess: np.ndarray | float, scale: float, form: SaturationForm) -> np.ndarray:
    """Facteur de saturation :math:`\\sigma(W)` pour la forme demandée."""
    w = np.asarray(excess, dtype=float)
    if form == "quadratic":
        return 1.0 / (1.0 + (w / scale) ** 2)
    if form == "logistic":
        return np.clip(1.0 - w / scale, 0.0, None)

    raise ValueError(f"forme de saturation inconnue : {form}")


def _integrate(
    amplification: float,
    damping: float,
    scale: float,
    initial: float,
    times: np.ndarray,
    form: SaturationForm,
) -> np.ndarray | None:
    """Intègre :math:`\\dot W = W(\\gamma\\alpha\\,\\sigma(W) - \\lambda)`, ou renvoie None."""

    def rate(_time: float, state: np.ndarray) -> np.ndarray:
        return state * (amplification * _saturation(state, scale, form) - damping)

    try:
        with np.errstate(over="ignore", invalid="ignore"):
            solution = solve_ivp(
                rate,
                (float(times[0]), float(times[-1])),
                [initial],
                t_eval=times,
                rtol=1e-6,
                atol=1e-9,
            )
    except (ValueError, FloatingPointError):
        return None

    if not solution.success or solution.y.shape[1] != times.size:
        return None
    if not np.all(np.isfinite(solution.y[0])):
        return None

    return np.clip(solution.y[0], _FLOOR, None)


@dataclass(frozen=True)
class SaturatedFit:
    """Paramètres identifiés sur une transition vers un palier.

    Attributes:
        amplification: :math:`\\gamma\\alpha`, par jour.
        damping: :math:`\\lambda`, par jour.
        saturation: :math:`W_{\\text{sat}}`, échelle de saturation en consultations par jour.
        scatter: dispersion résiduelle en échelle logarithmique. C'est la grandeur qui
            permet d'estimer le biais vers le bas de l'ajustement.
        n_points: nombre de points de la transition.
        form: forme de saturation supposée.
        converged: vrai si l'optimisation a convergé.
    """

    amplification: float
    damping: float
    saturation: float
    scatter: float
    n_points: int
    form: SaturationForm
    converged: bool

    @property
    def ratio(self) -> float:
        """Rapport :math:`\\gamma\\alpha/\\lambda`, borne inférieure du vrai rapport."""
        if self.damping <= 0.0:
            return float("inf")

        return float(self.amplification / self.damping)

    @property
    def plateau(self) -> float:
        """Palier prédit :math:`W^*`, où la dérive s'annule.

        Pour la saturation quadratique, :math:`W^* = W_{\\text{sat}}\\sqrt{\\rho - 1}`.
        """
        if self.ratio <= 1.0:
            return 0.0
        if self.form == "quadratic":
            return float(self.saturation * np.sqrt(self.ratio - 1.0))

        return float(self.saturation * (1.0 - 1.0 / self.ratio))

    @property
    def is_usable(self) -> bool:
        """Vrai si l'ajustement est exploitable : convergé, cohérent, peu dispersé."""
        return (
            self.converged
            and self.amplification > 0.0
            and self.damping > 0.0
            and self.saturation > 0.0
            and self.ratio > 1.0
            and self.scatter <= _MAX_SCATTER
        )


def expected_precision(scatter: float) -> float:
    """Dispersion relative attendue de :math:`\\rho` estimé, à dispersion résiduelle donnée.

    Établie par récupération sur trajectoires de synthèse : on simule une transition de
    paramètres connus, on y injecte un bruit multiplicatif d'écart-type logarithmique donné,
    et on mesure l'écart interquartile du rapport estimé rapporté à sa médiane. La relation
    est proche de la proportionnalité, avec un coefficient d'environ 2.

    Le test ``test_precision_matches_synthetic_recovery`` reproduit cette mesure, de sorte que
    la valeur annoncée ici ne puisse pas dériver de la procédure qu'elle décrit.

    Args:
        scatter: dispersion résiduelle en échelle logarithmique, telle que rapportée par
            :attr:`SaturatedFit.scatter`.

    Returns:
        L'écart interquartile relatif attendu de :math:`\\rho`. Une valeur de 0,2 signifie
        que la moitié des réalisations tombent dans une fourchette de ±10 % autour de la
        médiane.

    Examples:
        >>> round(expected_precision(0.0), 2)
        0.0
        >>> round(expected_precision(0.10), 2)
        0.53
        >>> expected_precision(0.15) > expected_precision(0.05)
        True
    """
    if scatter < 0.0:
        raise ValueError("la dispersion ne peut pas être négative")

    # Points mesurés par récupération synthétique sur la **chaîne complète** — détection,
    # localisation du décollage, puis ajustement — et non sur un ajustement isolé disposant
    # déjà de sa fenêtre. L'écart est considérable : le seul ajustement atteint 0,21 à 10 %
    # de bruit, la chaîne complète 0,53. C'est cette seconde valeur qui décrit ce qu'un
    # utilisateur obtient (voir tests/test_regime.py).
    scatters = np.array([0.00, 0.05, 0.10, 0.15, 0.25])
    dispersions = np.array([0.00, 0.24, 0.53, 0.77, 1.35])

    return float(np.interp(scatter, scatters, dispersions))


def fit_saturated_growth(
    observed: np.ndarray,
    baseline: float = 0.0,
    form: SaturationForm = "quadratic",
    times: np.ndarray | None = None,
) -> SaturatedFit:
    """Identifie :math:`\\gamma\\alpha`, :math:`\\lambda` et :math:`W_{\\text{sat}}`.

    L'initialisation vient de la forme linéaire en les paramètres, appliquée à une
    log-dérivée lissée par filtre de Savitzky-Golay ; le raffinement ajuste la trajectoire
    intégrée, sans aucune dérivée, en échelle logarithmique.

    L'ajustement porte sur la série **observée** :math:`V = V_{\\text{avant}} + W`, et non sur
    l'excédent :math:`W` seul. La différence est décisive en présence de bruit : au début de
    la transition, :math:`W` est une petite différence entre deux grandeurs bruitées, donc
    d'incertitude relative énorme — or c'est précisément la phase qui contraint
    :math:`\\gamma\\alpha - \\lambda`. Ajuster :math:`V`, toujours du même ordre que le niveau
    de base, place le résidu sur une quantité bien conditionnée et rétablit le bon modèle de
    bruit.

    Args:
        observed: série observée sur la transition, strictement positive.
        baseline: ancien niveau :math:`V_{\\text{avant}}`, tenu pour connu. À zéro, la
            fonction ajuste directement l'excédent.
        form: forme de saturation supposée.
        times: instants d'observation. Par défaut, un pas quotidien.

    Returns:
        Les paramètres identifiés, avec leur dispersion résiduelle.

    Raises:
        ValueError: si la transition compte moins de dix points, ou si l'excédent au-dessus
            du niveau de base n'est pas partout strictement positif.

    Examples:
        Récupération exacte sur une trajectoire de synthèse :

        >>> import numpy as np
        >>> from ide.regime import _integrate
        >>> days = np.arange(0.0, 121.0)
        >>> clean = _integrate(1.0, 0.2, 2000.0, 20.0, days, "quadratic")
        >>> fit = fit_saturated_growth(clean)
        >>> round(fit.ratio, 2)
        5.0
        >>> round(fit.damping, 3)
        0.2

        La même trajectoire posée sur un niveau de base, qui est déclaré :

        >>> fit = fit_saturated_growth(500.0 + clean, baseline=500.0)
        >>> round(fit.ratio, 2)
        5.0
    """
    series = np.asarray(observed, dtype=float)
    if series.ndim != 1 or series.size < 10:
        raise ValueError("une transition demande au moins 10 points")
    if np.any(series <= 0.0) or not np.all(np.isfinite(series)):
        raise ValueError("la série doit être finie et strictement positive")
    if baseline < 0.0:
        raise ValueError("le niveau de base ne peut pas être négatif")

    excess = series - baseline
    if np.any(excess <= 0.0):
        raise ValueError("l'excédent au-dessus du niveau de base doit être strictement positif")

    grid = np.arange(series.size, dtype=float) if times is None else np.asarray(times, float)
    logs = np.log(series)
    reference = float(excess.max())

    # --- Initialisation : forme linéaire en les paramètres ------------------------------
    window = min(21, excess.size - (excess.size + 1) % 2)
    window = max(window if window % 2 else window - 1, 5)
    step = float(grid[1] - grid[0])
    log_excess = np.log(excess)
    smoothed = savgol_filter(log_excess, window_length=window, polyorder=2)
    derivative = savgol_filter(
        log_excess, window_length=window, polyorder=2, deriv=1, delta=step
    )

    squares = np.exp(2.0 * smoothed)
    design = np.column_stack([np.ones_like(squares), -squares * derivative, -squares])
    (linear_a, linear_b, linear_c), *_ = np.linalg.lstsq(design, derivative, rcond=None)

    if linear_b > 0.0 and linear_c > 0.0 and linear_a > 0.0:
        guess_damping = linear_c / linear_b
        guess_amplification = linear_a + guess_damping
        guess_scale = float(np.sqrt(1.0 / linear_b))
    else:
        # Repli neutre lorsque la forme linéaire produit des coefficients incohérents,
        # ce qui arrive dès que le bruit domine la dérivée.
        guess_damping, guess_amplification, guess_scale = 0.15, 0.5, reference

    guess_scale = float(np.clip(guess_scale, 0.1 * reference, 100.0 * reference))

    # --- Raffinement : ajustement de la trajectoire intégrée ----------------------------
    def residual(parameters: np.ndarray) -> np.ndarray:
        amplification, damping, scale, initial = np.exp(parameters)
        model = _integrate(amplification, damping, scale, initial, grid, form)
        if model is None:
            return np.full(series.size, 10.0)

        return np.log(baseline + model) - logs

    start = np.log(
        [
            float(np.clip(guess_amplification, 1e-3, 5.0)),
            float(np.clip(guess_damping, 1e-4, 5.0)),
            guess_scale,
            float(np.clip(excess[0], 1e-3, reference)),
        ]
    )
    # L'optimisation est **bornée**, et non libre : sans bornes, l'algorithme explore des
    # jeux de paramètres où l'intégration déborde, ce qui produit des dépassements de
    # capacité et fait échouer l'ajustement pour une raison numérique et non statistique.
    bounds = (
        np.log([1e-4, 1e-5, 1e-2 * reference, 1e-6 * reference]),
        np.log([10.0, 10.0, 1e4 * reference, 10.0 * reference]),
    )
    start = np.clip(start, bounds[0] + 1e-9, bounds[1] - 1e-9)
    outcome = least_squares(residual, start, bounds=bounds, method="trf", max_nfev=800)
    amplification, damping, scale, _ = np.exp(outcome.x)

    return SaturatedFit(
        amplification=float(amplification),
        damping=float(damping),
        saturation=float(scale),
        scatter=float(np.sqrt(2.0 * outcome.cost / series.size)),
        n_points=int(series.size),
        form=form,
        converged=bool(outcome.success),
    )


@dataclass
class RegimeCriteria:
    """Critères de détection et de validation d'un changement de régime.

    Args:
        min_lift: rapport minimal entre le nouveau niveau et l'ancien. À 2, le régime doit
            au moins doubler l'attention habituelle du sujet.
        min_level: niveau minimal du nouveau palier, en consultations par jour, pour
            contenir le bruit de comptage.
        min_prior_level: niveau minimal de l'**ancien** régime. Il faut un régime antérieur
            pour qu'il y ait changement de régime : une série passant de 2 à 280
            consultations par jour ne décrit pas un basculement d'attention mais un article
            qui vient d'être rédigé. Sans ce garde-fou, ces créations produisent des
            élévations de plusieurs centaines qui écrasent toute comparaison.
        sustain: durée sur laquelle le nouveau niveau doit se maintenir, en jours. **C'est
            le critère qui distingue un changement de régime d'un pic** : un pic retombe,
            un régime tient.
        return_tolerance: fraction de l'élévation en dessous de laquelle le niveau ne doit
            pas redescendre pendant la période de maintien.
        transition: durée de la fenêtre d'ajustement après la rupture, en jours.
        lead: nombre de jours conservés avant la rupture. La segmentation place la rupture
            vers le milieu de la montée : remonter en amont récupère la phase où l'excédent
            est petit, celle qui contraint le mieux :math:`\\gamma\\alpha - \\lambda`.
        min_segment: longueur minimale d'un segment pour la segmentation.
        max_points: nombre maximal de ruptures examinées par série.
    """

    min_lift: float = 2.0
    min_level: float = 200.0
    min_prior_level: float = 50.0
    sustain: int = 180
    return_tolerance: float = 0.35
    transition: int = 120
    lead: int = 7
    min_segment: int = 60
    max_points: int = 6

    def __post_init__(self) -> None:
        if self.min_lift <= 1.0:
            raise ValueError("l'élévation minimale doit dépasser 1")
        if self.min_level < 0.0 or self.min_prior_level < 0.0:
            raise ValueError("les niveaux minimaux ne peuvent pas être négatifs")
        if self.sustain < 2 * self.min_segment // 2:
            raise ValueError("la durée de maintien doit couvrir au moins un demi-segment")
        if not 0.0 <= self.return_tolerance < 1.0:
            raise ValueError("la tolérance de retour doit appartenir à [0, 1)")
        if self.transition < 10:
            raise ValueError("la fenêtre de transition doit couvrir au moins 10 jours")
        if self.lead < 0:
            raise ValueError("le décalage avant rupture ne peut pas être négatif")


@dataclass(frozen=True)
class RegimeShift:
    """Un changement de régime, avec ses paramètres identifiés.

    Attributes:
        label: identifiant de la série.
        index: position du **décollage** de la transition, et non de la rupture rendue par
            la segmentation : c'est cette position qui délimite la fenêtre d'ajustement.
        level_before: niveau médian avant la rupture.
        level_after: niveau médian du palier installé.
        fit: identification sous la forme de saturation du modèle.
        alternative: même identification sous une saturation logistique, pour arbitrer la
            forme par les données.
    """

    label: str
    index: int
    level_before: float
    level_after: float
    fit: SaturatedFit
    alternative: SaturatedFit | None = None

    @property
    def lift(self) -> float:
        """Élévation du palier, en multiple de l'ancien niveau."""
        if self.level_before <= 0.0:
            return float("inf")

        return float(self.level_after / self.level_before)

    @property
    def ratio(self) -> float:
        """Rapport :math:`\\gamma\\alpha/\\lambda` estimé sur la transition."""
        return self.fit.ratio

    @property
    def relative_spread(self) -> float:
        """Dispersion relative attendue du rapport, à la dispersion résiduelle observée.

        Sert de barre d'erreur : c'est l'incertitude que la récupération synthétique attribue
        à un ajustement de cette qualité, et non un écart-type calculé sur les données.
        """
        return expected_precision(self.fit.scatter)

    @property
    def has_identified_parameters(self) -> bool:
        """Vrai si les paramètres sont exploitables, et pas seulement le changement de niveau.

        La distinction est le résultat central de ce module : sur des séries de consultation
        réelles, le changement de régime est **détectable** — sa date et son ampleur sont
        mesurées — alors que :math:`\\gamma\\alpha` et :math:`\\lambda` ne sont **pas
        identifiables**, la dispersion résiduelle y étant trop élevée.
        """
        return self.fit.is_usable

    @property
    def is_form_identified(self) -> bool:
        """Vrai si les données préfèrent nettement la forme de saturation du modèle.

        L'enjeu n'est pas un biais mais une **non-identifiabilité** : sous saturation
        logistique, le rapport :math:`\\gamma\\alpha/\\lambda` ne peut pas être extrait d'une
        trajectoire, quelle que soit la précision des données. Si la forme logistique ajuste
        aussi bien — dispersions résiduelles à moins de 10 % l'une de l'autre — alors le
        rapport rapporté repose sur une hypothèse de modèle et non sur une mesure.
        """
        if self.alternative is None or not self.alternative.is_usable:
            return True

        return self.alternative.scatter - self.fit.scatter > 0.1 * self.fit.scatter


def _longest_positive_run(values: np.ndarray) -> np.ndarray:
    """Plus longue plage continue de valeurs strictement positives.

    Examples:
        >>> import numpy as np
        >>> _longest_positive_run(np.array([-1.0, 2.0, 3.0, -1.0, 4.0, 5.0, 6.0]))
        array([4., 5., 6.])
    """
    series = np.asarray(values, dtype=float)
    best_start, best_length, start = 0, 0, None

    for index, value in enumerate(series):
        if value > 0.0:
            start = index if start is None else start
            if index - start + 1 > best_length:
                best_start, best_length = start, index - start + 1
        else:
            start = None

    return series[best_start : best_start + best_length]


def _transition_onset(
    series: np.ndarray, position: int, before: float, after: float, span: int
) -> int:
    """Premier jour où l'attention décolle franchement de son ancien niveau.

    La position rendue par la segmentation n'est pas fiable pour délimiter la fenêtre
    d'ajustement : une segmentation en moyenne place la rupture vers le milieu d'une montée
    graduelle, et peut la placer jusqu'à plusieurs semaines avant le décollage réel. Ajuster
    depuis cette position ferait entrer des dizaines de jours d'ancien régime, où l'excédent
    n'est que du bruit autour de zéro.

    Le décollage est donc localisé sur un critère explicite : le premier jour, dans une
    fenêtre centrée sur la rupture, où l'attention franchit 5 % de l'élévation totale sans
    plus redescendre en dessous.
    """
    threshold = before + 0.05 * (after - before)
    start = max(0, position - span)
    stop = min(series.size, position + span)
    window = series[start:stop]

    above = window > threshold
    if not above.any():
        return position

    # On retient le début de la dernière plage qui ne redescend plus : le franchissement
    # définitif, et non un dépassement passager antérieur.
    onset = int(np.argmax(above))
    for index in range(above.size - 1, -1, -1):
        if not above[index]:
            onset = index + 1
            break

    return int(min(start + onset, series.size - 1))


#: Motifs de rejet d'une rupture candidate, dans l'ordre d'évaluation.
_REJECTIONS = ("niveau", "élévation", "maintien", "doublon", "fenêtre", "ajustement")


@dataclass(frozen=True)
class RegimeReport:
    """Compte rendu de la détection de changements de régime sur une série.

    Attributes:
        label: identifiant de la série.
        shifts: changements de régime retenus.
        candidates: nombre de ruptures détectées par la segmentation.
        rejections: nombre de rejets par motif —

            * ``niveau`` : palier en dessous du seuil de bruit de comptage ;
            * ``élévation`` : nouveau niveau trop proche de l'ancien ;
            * ``maintien`` : le niveau est redescendu — c'est un pic, non un régime ;
            * ``doublon`` : même transition déjà ajustée. Une segmentation en moyenne
              découpe une montée graduelle en escalier de ruptures ; elles décrivent un
              seul changement de régime ;
            * ``fenêtre`` : transition trop courte ou excédent non positif ;
            * ``ajustement`` : identification non convergée, incohérente ou trop dispersée.
              Ce motif **n'écarte pas** le changement de régime, qui reste rapporté sans ses
              paramètres.
    """

    label: str
    shifts: list[RegimeShift]
    candidates: int
    rejections: dict[str, int]

    @property
    def is_exploitable(self) -> bool:
        """Vrai si au moins un changement de régime a été détecté."""
        return len(self.shifts) > 0

    @property
    def identified(self) -> list[RegimeShift]:
        """Changements de régime dont les paramètres sont, en plus, exploitables."""
        return [shift for shift in self.shifts if shift.has_identified_parameters]

    @property
    def dominant_rejection(self) -> str | None:
        """Motif de rejet majoritaire, ou ``None`` si la série a livré un résultat."""
        if self.is_exploitable or not any(self.rejections.values()):
            return None

        return max(self.rejections, key=lambda motif: self.rejections[motif])


def scan_regime_shifts(
    views: np.ndarray,
    label: str = "série",
    criteria: RegimeCriteria | None = None,
    compare_forms: bool = True,
    adjust_weekly: bool = True,
) -> RegimeReport:
    """Détecte les changements de régime d'une série et identifie leurs paramètres.

    Args:
        views: consultations quotidiennes, strictement positives et sans valeur manquante.
        label: identifiant reporté sur les résultats.
        criteria: critères de détection. Par défaut, ceux du notebook 10.
        compare_forms: ajuste également une saturation logistique, pour vérifier que la
            forme est tranchée par les données.
        adjust_weekly: retire la périodicité hebdomadaire avant analyse. Recommandé : elle
            gonfle la dispersion résiduelle, dont dépend directement le biais.

    Returns:
        Le compte rendu complet, résultats retenus et rejets par motif.
    """
    series = np.asarray(views, dtype=float)
    if series.ndim != 1:
        raise ValueError("la série doit être un vecteur")

    rules = criteria or RegimeCriteria()
    minimum_length = 2 * rules.min_segment + rules.sustain
    if series.size < minimum_length:
        raise ValueError(f"la détection demande au moins {minimum_length} jours")
    if np.any(series <= 0.0):
        raise ValueError("la série doit être strictement positive")

    working = weekly_adjust(series) if adjust_weekly else series
    breaks = detect_change_points(
        working, min_segment=rules.min_segment, max_points=rules.max_points
    )

    shifts: list[RegimeShift] = []
    rejections = dict.fromkeys(_REJECTIONS, 0)
    fitted_onsets: list[int] = []

    for position in breaks:
        before = float(np.median(working[max(0, position - rules.sustain) : position]))
        window_end = min(working.size, position + rules.sustain)
        # Le palier est mesuré sur la seconde moitié de la période de maintien : la
        # première contient encore la transition, qui tirerait la médiane vers le bas.
        settled = working[position + (window_end - position) // 2 : window_end]
        if settled.size == 0:
            rejections["maintien"] += 1
            continue
        after = float(np.median(settled))

        if after < rules.min_level or before < rules.min_prior_level:
            rejections["niveau"] += 1
            continue
        if before <= 0.0 or after / before < rules.min_lift:
            rejections["élévation"] += 1
            continue

        # Critère décisif : le niveau ne doit pas redescendre. Un pic échoue ici.
        floor = before + rules.return_tolerance * (after - before)
        sustained = working[position : window_end]
        if float(np.median(sustained[len(sustained) // 2 :])) < floor:
            rejections["maintien"] += 1
            continue
        if np.mean(sustained > floor) < 0.5:
            rejections["maintien"] += 1
            continue

        onset = _transition_onset(working, position, before, after, rules.transition)
        if any(abs(onset - other) < rules.min_segment for other in fitted_onsets):
            rejections["doublon"] += 1
            continue

        start = max(0, onset - rules.lead)
        stop = min(working.size, onset + rules.transition)
        # L'excédent doit rester strictement positif — il passe au logarithme dans
        # l'initialisation — d'où la sélection de la plus longue plage continue. La fenêtre
        # ainsi retenue est ensuite ajustée sur la série observée, niveau de base compris.
        excess = _longest_positive_run(working[start:stop] - before)

        if excess.size < 10:
            rejections["fenêtre"] += 1
            continue

        fitted_onsets.append(onset)
        transition = excess + before
        fitted = fit_saturated_growth(transition, baseline=before, form="quadratic")

        # Un ajustement inexploitable **ne fait pas disparaître le changement de régime** :
        # la détection et l'identification sont deux résultats distincts, et le premier vaut
        # d'être rapporté même quand le second échoue. Confondre les deux ferait passer une
        # limite de l'estimateur pour une absence de phénomène.
        if not fitted.is_usable:
            rejections["ajustement"] += 1

        alternative = (
            fit_saturated_growth(transition, baseline=before, form="logistic")
            if compare_forms
            else None
        )

        shifts.append(
            RegimeShift(
                label=label,
                index=int(onset),
                level_before=before,
                level_after=after,
                fit=fitted,
                alternative=alternative,
            )
        )

    return RegimeReport(
        label=label,
        shifts=shifts,
        candidates=len(breaks),
        rejections=rejections,
    )
