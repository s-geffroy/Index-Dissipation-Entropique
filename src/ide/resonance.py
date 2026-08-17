"""Résonance algorithmique : l'effet Larsen informationnel.

Une fausse information et un algorithme de recommandation forment une boucle de
rétroaction positive, structurellement identique à l'effet Larsen en acoustique :
la rumeur est le signal initial, l'engagement qu'elle suscite est capté par la
plateforme, qui l'amplifie et le réinjecte, jusqu'à saturer l'espace cognitif.

La visibilité :math:`V(t)` d'un contenu obéit à :

.. math::

    \\ddot{V} + \\big(\\lambda - \\gamma\\alpha\\, \\sigma(V)\\big)\\dot{V}
      + \\omega_0^2 V = \\xi(t)

* :math:`\\lambda` — amortissement naturel : l'oubli, la lassitude du public ;
* :math:`\\gamma` — gain algorithmique : le multiplicateur que la plateforme
  applique à un contenu qui retient l'attention ;
* :math:`\\alpha` — charge émotionnelle innée du contenu (colère, peur, surprise) ;
* :math:`\\omega_0` — fréquence propre du cycle médiatique ;
* :math:`\\sigma(V)` — **facteur de saturation**, absent du fil d'origine ;
* :math:`\\xi(t)` — bruit blanc, les fluctuations du comportement humain.

**Critère d'instabilité.** Si :math:`\\gamma\\alpha > \\lambda`, l'amortissement
effectif devient négatif : le système n'évacue plus l'énergie qu'on lui injecte,
il l'accumule. C'est le résultat central du fil, et il fonde la recommandation
d'audit du mémorandum — interdire les configurations où le taux d'amplification
d'un contenu dépasse son taux d'amortissement naturel.

Deux corrections par rapport au fil de travail
----------------------------------------------

**Signe du rappel.** Le fil écrivait :math:`-\\omega_0^2 V`, ce qui fait du point
d'équilibre un col instable *quels que soient* les autres paramètres : le système
divergerait même avec un gain algorithmique nul, et le critère
:math:`\\gamma\\alpha > \\lambda` perdrait tout contenu. Le rappel d'un oscillateur
s'écrit :math:`+\\omega_0^2 V`.

**Saturation.** Sans :math:`\\sigma(V)`, la solution instable est
:math:`V(t) \\propto e^{(\\gamma\\alpha - \\lambda)t}`, qui diverge sans limite —
une visibilité infinie n'existe pas, l'attention disponible est finie. Le facteur
retenu, :math:`\\sigma(V) = 1/(1 + (V/V_{\\text{sat}})^2)`, éteint progressivement
l'amplification quand la visibilité approche la capacité d'attention totale. Le
système ne diverge plus : il s'installe dans un **cycle limite** de type Van der
Pol, c'est-à-dire une oscillation médiatique auto-entretenue d'amplitude finie —
ce que l'on observe effectivement, plutôt qu'une explosion.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = [
    "ResonanceParameters",
    "ResonanceSolution",
    "simulate_resonance",
]


@dataclass(frozen=True)
class ResonanceParameters:
    """Paramètres de la boucle de rétroaction algorithmique.

    Args:
        damping: amortissement naturel :math:`\\lambda` — oubli et lassitude.
        gain: gain algorithmique :math:`\\gamma` appliqué par la plateforme.
        emotion: charge émotionnelle :math:`\\alpha` du contenu.
        frequency: fréquence propre :math:`\\omega_0` du cycle médiatique.
        saturation: capacité d'attention :math:`V_{\\text{sat}}`. ``None`` désactive
            la saturation et restitue le modèle linéaire divergent du fil d'origine,
            ce qui permet de comparer les deux régimes.
        noise: écart-type du bruit blanc :math:`\\xi(t)`.

    Examples:
        >>> stable = ResonanceParameters(damping=1.0, gain=1.0, emotion=0.5)
        >>> stable.is_unstable
        False
        >>> viral = ResonanceParameters(damping=0.2, gain=3.0, emotion=0.5)
        >>> viral.is_unstable
        True
    """

    damping: float = 0.5
    gain: float = 1.0
    emotion: float = 1.0
    frequency: float = 1.0
    saturation: float | None = 1.0
    noise: float = 0.0

    def __post_init__(self) -> None:
        if self.damping < 0.0:
            raise ValueError("l'amortissement naturel ne peut pas être négatif")
        if self.gain < 0.0 or self.emotion < 0.0:
            raise ValueError("le gain et la charge émotionnelle ne peuvent pas être négatifs")
        if self.frequency <= 0.0:
            raise ValueError("la fréquence propre doit être strictement positive")
        if self.saturation is not None and self.saturation <= 0.0:
            raise ValueError("la capacité d'attention doit être strictement positive")
        if self.noise < 0.0:
            raise ValueError("l'amplitude du bruit ne peut pas être négative")

    @property
    def amplification(self) -> float:
        """Taux d'amplification effectif :math:`\\gamma\\alpha`."""
        return self.gain * self.emotion

    @property
    def is_unstable(self) -> bool:
        """Vrai si :math:`\\gamma\\alpha > \\lambda` : l'amortissement effectif est négatif.

        C'est exactement le critère que le mémorandum propose de rendre
        contrôlable par le régulateur.
        """
        return self.amplification > self.damping

    def effective_damping(self, visibility: float | np.ndarray) -> np.ndarray:
        """Amortissement effectif :math:`\\lambda - \\gamma\\alpha\\,\\sigma(V)`.

        Négatif, il traduit une accumulation d'énergie ; positif, une dissipation.
        La saturation le fait repasser positif aux fortes visibilités, ce qui borne
        le phénomène.
        """
        v = np.asarray(visibility, dtype=float)

        if self.saturation is None:
            attenuation = np.ones_like(v)
        else:
            attenuation = 1.0 / (1.0 + (v / self.saturation) ** 2)

        return self.damping - self.amplification * attenuation


@dataclass(frozen=True)
class ResonanceSolution:
    """Trajectoire de visibilité d'un contenu soumis à la boucle algorithmique.

    Attributes:
        times: instants d'échantillonnage.
        visibility: visibilité :math:`V(t)`.
        velocity: vitesse :math:`\\dot{V}(t)`, la vélocité de propagation.
        parameters: paramètres utilisés.
        diverged: vrai si l'intégration a dépassé le seuil numérique de divergence.
    """

    times: np.ndarray
    visibility: np.ndarray
    velocity: np.ndarray
    parameters: ResonanceParameters
    diverged: bool

    @property
    def peak_visibility(self) -> float:
        """Visibilité maximale atteinte, en valeur absolue."""
        return float(np.max(np.abs(self.visibility)))

    def late_amplitude(self, fraction: float = 0.25) -> float:
        """Amplitude sur la dernière fraction de la trajectoire.

        Distingue un régime borné (cycle limite : amplitude stable) d'un régime
        divergent (amplitude qui continue de croître).
        """
        if not 0.0 < fraction <= 1.0:
            raise ValueError("la fraction doit appartenir à (0, 1]")

        tail = self.visibility[-max(1, int(len(self.visibility) * fraction)) :]

        return float(np.max(np.abs(tail)))


# Au-delà de ce seuil, la trajectoire est considérée comme divergente et
# l'intégration s'arrête : poursuivre ne produirait que des infinis et des NaN.
_DIVERGENCE_THRESHOLD = 1e12


def simulate_resonance(
    parameters: ResonanceParameters,
    total_time: float = 60.0,
    time_step: float = 1e-3,
    initial_visibility: float = 0.05,
    initial_velocity: float = 0.0,
    seed: int | None = None,
) -> ResonanceSolution:
    """Intègre la dynamique de résonance par schéma d'Euler-Maruyama.

    Le schéma est choisi pour rester correct en présence de bruit blanc :
    l'incrément stochastique y est en :math:`\\sqrt{\\Delta t}`, ce qu'un
    intégrateur déterministe d'ordre supérieur traiterait à tort comme un terme
    régulier.

    Args:
        parameters: paramètres de la boucle.
        total_time: durée simulée.
        time_step: pas de temps.
        initial_visibility: visibilité initiale du contenu — l'étincelle de départ.
        initial_velocity: vélocité initiale.
        seed: graine du bruit.

    Returns:
        La trajectoire complète, tronquée à l'instant de divergence le cas échéant.

    Examples:
        Gain modéré : le contenu s'éteint.

        >>> calm = simulate_resonance(
        ...     ResonanceParameters(damping=1.0, gain=0.5, emotion=0.5),
        ...     total_time=40.0,
        ... )
        >>> calm.late_amplitude() < 0.01
        True

        Gain excessif avec attention finie : cycle limite, borné mais permanent.

        >>> viral = simulate_resonance(
        ...     ResonanceParameters(damping=0.2, gain=3.0, emotion=0.5, saturation=1.0),
        ...     total_time=120.0,
        ... )
        >>> viral.diverged
        False
        >>> viral.late_amplitude() > 0.5
        True
    """
    if total_time <= 0.0:
        raise ValueError("la durée simulée doit être strictement positive")
    if time_step <= 0.0 or time_step > total_time:
        raise ValueError("le pas de temps doit être positif et inférieur à la durée")

    steps = int(np.ceil(total_time / time_step))
    rng = np.random.default_rng(seed)

    times = np.linspace(0.0, steps * time_step, steps + 1)
    visibility = np.empty(steps + 1)
    velocity = np.empty(steps + 1)
    visibility[0] = initial_visibility
    velocity[0] = initial_velocity

    squared_frequency = parameters.frequency**2
    noise_scale = parameters.noise * np.sqrt(time_step)
    diverged = False

    for index in range(steps):
        current_visibility = visibility[index]
        current_velocity = velocity[index]

        damping = float(parameters.effective_damping(current_visibility))
        acceleration = -damping * current_velocity - squared_frequency * current_visibility

        velocity[index + 1] = (
            current_velocity
            + time_step * acceleration
            + (noise_scale * rng.standard_normal() if noise_scale > 0.0 else 0.0)
        )
        visibility[index + 1] = current_visibility + time_step * velocity[index + 1]

        if not np.isfinite(visibility[index + 1]) or abs(visibility[index + 1]) > (
            _DIVERGENCE_THRESHOLD
        ):
            diverged = True
            times = times[: index + 2]
            visibility = visibility[: index + 2]
            velocity = velocity[: index + 2]
            break

    return ResonanceSolution(
        times=times,
        visibility=visibility,
        velocity=velocity,
        parameters=parameters,
        diverged=diverged,
    )
