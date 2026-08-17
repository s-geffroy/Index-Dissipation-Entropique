"""Équation de Fokker-Planck : paysage de l'opinion publique et transition de phase.

Plutôt que de suivre :math:`N` individus, on suit la **densité de probabilité**
:math:`P(x, t)` de l'opinion macroscopique :math:`x \\in [-1, 1]` :

.. math::

    \\frac{\\partial P}{\\partial t}
      = -\\frac{\\partial}{\\partial x}\\big[A(x) P\\big]
        + \\frac{\\partial^2}{\\partial x^2}\\big[B(x) P\\big]

deux forces antagonistes : la **dérive** :math:`A(x)` (conformisme et champ
médiatique, déterministe) contre la **diffusion** :math:`B(x)` (bruit, agitation
sociale).

Deux corrections importantes par rapport au fil de travail d'origine
-------------------------------------------------------------------

**1. La dérive n'est pas** :math:`A(x) = Jx + H`. Cette expression dérive du seul
potentiel :math:`V(x) = -\\tfrac{J}{2}x^2 - Hx`, qui est **non borné** : rien n'y
retient l'opinion dans :math:`[-1, 1]` et, surtout, il ne produit **aucune
transition de phase** — :math:`\\exp(N J x^2 / 2T)` est convexe, donc toujours
maximal aux extrêmes, quelle que soit la température. Le modèle prédirait une
société éternellement polarisée, y compris à température infinie.

La dérive correcte se lit sur l'**énergie libre de Helmholtz par individu**
:math:`f = e - Ts`, exactement la quantité que le fil invoquait sans l'écrire :

.. math::

    f(x) = -\\frac{J}{2}x^2 - Hx
           + T\\left[\\frac{1+x}{2}\\ln\\frac{1+x}{2}
                   + \\frac{1-x}{2}\\ln\\frac{1-x}{2}\\right]

Le terme entropique de mélange — le nombre de configurations microscopiques
compatibles avec une opinion moyenne :math:`x` — était le maillon manquant. Il
donne :math:`A(x) = -f'(x) = Jx + H - T\\,\\mathrm{artanh}(x)`, borne la dynamique
dans :math:`(-1, 1)`, et fait apparaître une vraie température critique de champ
moyen :math:`T_c = J`. La formulation du fil en est la linéarisation en
:math:`x \\to 0`.

**2. La diffusion en** :math:`1/N` **dit le contraire du récit**. Avec
:math:`B(x) = T(1-x^2)/N`, plus la population est grande, plus le bruit de la
variable macroscopique est **faible** : la loi des grands nombres rend la société
*plus* déterministe, pas plus désordonnée. Il n'y a pas de contradiction, mais
deux échelles distinctes qu'il faut cesser de confondre (voir ``docs/limites.md``,
point 3) : l'entropie de configuration **totale** croît avec :math:`N`, tandis que
les fluctuations de la **moyenne** :math:`x` décroissent en :math:`1/N`. La thèse
défendable est donc : *une grande population ne devient pas bruyante, elle devient
rigide* — et c'est cette rigidité qui rend le consensus organique inatteignable et
la polarisation irréversible.
"""

from __future__ import annotations

from collections.abc import Callable

# Comme dans :mod:`ide.ising`, `field` désigne le champ médiatique H : l'utilitaire
# de dataclasses est importé sous alias pour lui laisser ce nom.
from dataclasses import dataclass
from dataclasses import field as dataclass_field

import numpy as np

__all__ = [
    "FokkerPlanckSolution",
    "FokkerPlanckSolver",
    "diffusion_term",
    "drift_term",
    "mean_field_critical_temperature",
    "mean_field_free_energy",
    "stationary_distribution",
    "zero_flux_stationary",
]

# La diffusion B(x) ∝ (1 - x²) s'annule aux opinions unanimes : la grille est
# tronquée juste avant, faute de quoi le schéma numérique divise par zéro et la
# solution stationnaire exacte n'est plus intégrable.
_DOMAIN_LIMIT = 0.995


def mean_field_critical_temperature(coupling: float = 1.0) -> float:
    """Température critique de champ moyen (Curie-Weiss) : :math:`T_c = J`.

    À comparer à la valeur exacte en dimension 2
    (:func:`ide.ising.onsager_critical_temperature`, :math:`\\approx 2{,}269 J`).
    L'écart n'est pas une erreur : le champ moyen suppose que chacun subit
    l'opinion *moyenne* de tous, ce qui surestime la cohésion et sous-estime la
    température nécessaire pour la briser. Un réseau social globalisé est
    précisément plus proche du champ moyen qu'un voisinage géographique — la
    comparaison des deux valeurs a donc un sens sociologique.

    Examples:
        >>> mean_field_critical_temperature(1.5)
        1.5
    """
    if coupling <= 0.0:
        raise ValueError("la force de conformisme J doit être strictement positive")

    return float(coupling)


def mean_field_free_energy(
    opinion: np.ndarray | float,
    coupling: float = 1.0,
    field: float = 0.0,
    temperature: float = 1.0,
) -> np.ndarray:
    """Énergie libre de Helmholtz par individu :math:`f(x) = e(x) - T\\,s(x)`.

    Le terme d'énergie :math:`-\\tfrac{J}{2}x^2 - Hx` mesure la tension
    (frustration du désaccord, plus l'alignement sur le champ médiatique) ; le
    terme entropique de mélange mesure le nombre de façons d'obtenir une opinion
    moyenne :math:`x`. C'est le compromis entre les deux — le :math:`F = E - TS`
    du fil de travail — qui décide si une société s'accorde ou se fragmente.

    Args:
        opinion: opinion macroscopique :math:`x \\in [-1, 1]`.
        coupling: force de conformisme :math:`J`.
        field: champ médiatique :math:`H`.
        temperature: température sociale :math:`T`.

    Returns:
        L'énergie libre par individu. Ses minima sont les états stationnaires
        possibles de la société.

    Examples:
        Sans champ, l'énergie libre est symétrique :

        >>> import numpy as np
        >>> f = mean_field_free_energy(np.array([-0.6, 0.6]), temperature=0.5)
        >>> bool(np.isclose(f[0], f[1]))
        True
    """
    x = np.clip(np.asarray(opinion, dtype=float), -1.0, 1.0)
    energy = -0.5 * coupling * x**2 - field * x

    # Les limites x → ±1 donnent 0 ln 0 = 0 : on les traite explicitement plutôt
    # que de laisser numpy produire un NaN.
    half_up = np.clip((1.0 + x) / 2.0, 1e-300, 1.0)
    half_down = np.clip((1.0 - x) / 2.0, 1e-300, 1.0)
    mixing_entropy = -(half_up * np.log(half_up) + half_down * np.log(half_down))

    return energy - temperature * mixing_entropy


def drift_term(
    opinion: np.ndarray | float,
    coupling: float = 1.0,
    field: float = 0.0,
    temperature: float = 1.0,
) -> np.ndarray:
    """Dérive :math:`A(x) = -f'(x) = Jx + H - T\\,\\mathrm{artanh}(x)`.

    Trois forces s'y superposent : le conformisme :math:`Jx` qui amplifie la
    majorité existante, le champ médiatique :math:`H` qui pousse dans une
    direction imposée, et le rappel entropique :math:`-T\\,\\mathrm{artanh}(x)` qui
    ramène vers la modération et diverge aux opinions unanimes — c'est lui qui
    empêche la dynamique de sortir de l'intervalle.

    Examples:
        La modération est un point fixe en l'absence de champ :

        >>> float(drift_term(0.0))
        0.0
    """
    x = np.clip(np.asarray(opinion, dtype=float), -_DOMAIN_LIMIT, _DOMAIN_LIMIT)

    return coupling * x + field - temperature * np.arctanh(x)


def diffusion_term(
    opinion: np.ndarray | float,
    temperature: float = 1.0,
    population: int = 1_000,
) -> np.ndarray:
    """Diffusion :math:`B(x) = T(1-x^2)/N`, le bruit de la variable macroscopique.

    Le facteur :math:`(1-x^2)` éteint le bruit à l'unanimité : il n'y a plus de
    désaccord à échantillonner. Le facteur :math:`1/N` traduit la loi des grands
    nombres — c'est le point 3 de l'audit.

    Examples:
        >>> float(diffusion_term(1.0))
        0.0
    """
    if population < 1:
        raise ValueError("la population doit être strictement positive")
    if temperature <= 0.0:
        raise ValueError("la température sociale doit être strictement positive")

    x = np.clip(np.asarray(opinion, dtype=float), -1.0, 1.0)

    return temperature * (1.0 - x**2) / population


def stationary_distribution(
    grid: np.ndarray,
    coupling: float = 1.0,
    field: float = 0.0,
    temperature: float = 1.0,
    population: int = 1_000,
) -> np.ndarray:
    """Distribution d'équilibre :math:`P(x) \\propto \\exp(-N f(x) / T)`.

    Forme de grandes déviations de l'équilibre statistique : la probabilité d'une
    opinion collective décroît exponentiellement avec le coût en énergie libre,
    et le facteur :math:`N` rend cette pénalité d'autant plus sévère que la
    population est grande.

    C'est l'objet qui porte la **transition de phase** annoncée dans la note :

    * :math:`T > T_c = J` — un pic unique centré sur la modération : débat fluide ;
    * :math:`T < T_c` et :math:`H = 0` — deux pics symétriques : polarisation ;
    * :math:`T < T_c` et :math:`H > 0` — deux pics asymétriques, celui du côté de
      la désinformation devenant écrasant : faux consensus.

    Args:
        grid: points d'évaluation dans :math:`[-1, 1]`.
        coupling: force de conformisme :math:`J`.
        field: champ médiatique :math:`H`.
        temperature: température sociale :math:`T`.
        population: taille :math:`N` de la population.

    Returns:
        La densité normalisée sur la grille (intégrale unitaire par la méthode des
        trapèzes).

    Examples:
        >>> import numpy as np
        >>> grid = np.linspace(-0.98, 0.98, 401)
        >>> hot = stationary_distribution(grid, temperature=2.0, population=200)
        >>> int(np.argmax(hot)) == len(grid) // 2  # T > T_c : pic sur la modération
        True
    """
    x = np.asarray(grid, dtype=float)
    if x.ndim != 1 or x.size < 3:
        raise ValueError("la grille doit être un vecteur d'au moins 3 points")

    free_energy = mean_field_free_energy(x, coupling, field, temperature)
    # Le décalage par le minimum évite un dépassement de capacité de l'exponentielle
    # pour les grandes populations, sans changer la distribution après normalisation.
    exponent = -population * (free_energy - free_energy.min()) / temperature
    density = np.exp(exponent)

    return density / np.trapezoid(density, x)


def zero_flux_stationary(
    grid: np.ndarray,
    drift: Callable[[np.ndarray], np.ndarray],
    diffusion: Callable[[np.ndarray], np.ndarray],
) -> np.ndarray:
    """État stationnaire exact à flux nul d'une équation de Fokker-Planck donnée.

    En annulant le courant de probabilité :math:`A P - \\partial_x (B P) = 0`, on
    obtient par intégration :

    .. math:: P(x) \\propto \\frac{1}{B(x)} \\exp\\!\\int^x \\frac{A(u)}{B(u)}\\,du

    Sert de référence pour valider le solveur numérique : les deux doivent
    coïncider. Cette solution diffère en général de
    :func:`stationary_distribution`, qui suppose une mobilité constante ; elles ne
    se rejoignent qu'à diffusion uniforme.

    Args:
        grid: grille régulière de points.
        drift: fonction :math:`A(x)`, vectorisée.
        diffusion: fonction :math:`B(x)`, vectorisée et strictement positive sur la
            grille.

    Returns:
        La densité normalisée sur la grille.
    """
    x = np.asarray(grid, dtype=float)
    diffusion_values = np.asarray(diffusion(x), dtype=float)

    if np.any(diffusion_values <= 0.0):
        raise ValueError("la diffusion doit être strictement positive sur toute la grille")

    integrand = np.asarray(drift(x), dtype=float) / diffusion_values
    # Primitive cumulée par trapèzes, calée à zéro sur le premier point.
    steps = np.diff(x)
    increments = 0.5 * steps * (integrand[:-1] + integrand[1:])
    potential = np.concatenate([[0.0], np.cumsum(increments)])

    log_density = potential - np.log(diffusion_values)
    density = np.exp(log_density - log_density.max())

    return density / np.trapezoid(density, x)


@dataclass(frozen=True)
class FokkerPlanckSolution:
    """Résultat d'une intégration temporelle de l'équation de Fokker-Planck.

    Attributes:
        grid: grille d'opinions.
        density: densité de probabilité finale.
        times: instants enregistrés.
        history: densité à chaque instant enregistré, de forme ``(len(times), len(grid))``.
        mass_drift: écart maximal de la masse totale à 1 au cours de l'intégration.
            Le schéma étant conservatif par construction, cette valeur doit rester
            au niveau de la précision machine ; toute dérive signale un bug.
    """

    grid: np.ndarray
    density: np.ndarray
    times: np.ndarray
    history: np.ndarray
    mass_drift: float

    @property
    def modes(self) -> np.ndarray:
        """Positions des maxima locaux de la densité finale.

        Un mode unique proche de zéro décrit une société modérée ; deux modes
        décrivent une polarisation ; deux modes d'amplitudes très inégales
        décrivent un faux consensus imposé par le champ médiatique.
        """
        interior = self.density[1:-1]
        is_peak = (interior > self.density[:-2]) & (interior > self.density[2:])

        return self.grid[1:-1][is_peak]

    @property
    def is_bimodal(self) -> bool:
        """Vrai si la densité finale présente au moins deux maxima locaux."""
        return len(self.modes) >= 2

    def mean_opinion(self) -> float:
        """Opinion moyenne :math:`\\langle x \\rangle` de la distribution finale."""
        return float(np.trapezoid(self.grid * self.density, self.grid))


@dataclass
class FokkerPlanckSolver:
    """Intégrateur en volumes finis de l'équation de Fokker-Planck.

    Le schéma est écrit sous **forme de flux** : la densité de chaque cellule
    n'évolue que par échange avec ses voisines, et les flux aux deux bords du
    domaine sont imposés nuls. La masse totale de probabilité est donc conservée
    exactement, à la précision machine près — propriété qu'un schéma en
    différences finies naïf ne garantit pas, et que la suite de tests vérifie.

    Args:
        points: nombre de cellules de la grille.
        coupling: force de conformisme :math:`J`.
        field: champ médiatique :math:`H`.
        temperature: température sociale :math:`T`.
        population: taille :math:`N`, qui fixe l'amplitude de la diffusion.
        domain_limit: troncature du domaine, nécessaire parce que :math:`B(x)`
            s'annule à l'unanimité.

    Examples:
        >>> solver = FokkerPlanckSolver(points=401, temperature=0.8, population=400)
        >>> solution = solver.solve(total_time=60.0)
        >>> solution.mass_drift < 1e-9
        True
        >>> solution.is_bimodal  # T < T_c = J : polarisation
        True
        >>> [round(float(mode), 2) for mode in solution.modes]
        [-0.72, 0.72]
    """

    points: int = 401
    coupling: float = 1.0
    field: float = 0.0
    temperature: float = 1.0
    population: int = 1_000
    domain_limit: float = _DOMAIN_LIMIT

    grid: np.ndarray = dataclass_field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.points < 11:
            raise ValueError("la grille doit compter au moins 11 points")
        if not 0.0 < self.domain_limit < 1.0:
            raise ValueError("la troncature du domaine doit appartenir à (0, 1)")

        self.grid = np.linspace(-self.domain_limit, self.domain_limit, self.points)
        self._spacing = float(self.grid[1] - self.grid[0])

        # Les flux vivent sur les faces entre cellules, d'où l'évaluation de la
        # dérive à mi-chemin entre deux points de grille.
        faces = 0.5 * (self.grid[:-1] + self.grid[1:])
        self._face_drift = self.drift(faces)
        self._cell_diffusion = self.diffusion(self.grid)

    def drift(self, opinion: np.ndarray) -> np.ndarray:
        """Dérive :math:`A(x)` du modèle, avec ses paramètres courants."""
        return drift_term(opinion, self.coupling, self.field, self.temperature)

    def diffusion(self, opinion: np.ndarray) -> np.ndarray:
        """Diffusion :math:`B(x)` du modèle, avec ses paramètres courants."""
        return diffusion_term(opinion, self.temperature, self.population)

    def mass(self, density: np.ndarray) -> float:
        """Masse totale de probabilité, au sens exact du schéma en volumes finis.

        La règle du rectangle — et non celle des trapèzes — est employée à dessein :
        c'est cette somme que le schéma en flux conserve **exactement**, puisque
        chaque cellule n'échange qu'avec ses voisines et que les flux aux bords sont
        nuls. La règle des trapèzes, en pondérant à demi les cellules extrêmes,
        afficherait une fausse dérive de masse dès que la densité s'accumule aux
        bords du domaine.
        """
        return float(self._spacing * np.sum(density))

    def initial_condition(self, centre: float = 0.0, width: float = 0.15) -> np.ndarray:
        """Densité initiale gaussienne, normalisée — une société initialement modérée."""
        density = np.exp(-0.5 * ((self.grid - centre) / width) ** 2)

        return density / self.mass(density)

    def stable_time_step(self, safety: float = 0.4) -> float:
        """Pas de temps respectant les conditions de stabilité advection-diffusion.

        Le minimum des deux contraintes (CFL pour la dérive, condition parabolique
        pour la diffusion) est retenu, puis pondéré par un facteur de sécurité.
        """
        max_drift = float(np.max(np.abs(self._face_drift)))
        max_diffusion = float(np.max(self._cell_diffusion))

        advective = self._spacing / max_drift if max_drift > 0.0 else np.inf
        diffusive = self._spacing**2 / (2.0 * max_diffusion) if max_diffusion > 0.0 else np.inf

        return safety * min(advective, diffusive)

    def solve(
        self,
        total_time: float,
        density: np.ndarray | None = None,
        time_step: float | None = None,
        snapshots: int = 25,
    ) -> FokkerPlanckSolution:
        """Intègre l'équation jusqu'à ``total_time``.

        Args:
            total_time: durée d'intégration, en unités de temps du modèle.
            density: condition initiale. Par défaut, une société modérée centrée
                sur :math:`x = 0`.
            time_step: pas de temps. Par défaut, la valeur stable calculée par
                :meth:`stable_time_step`.
            snapshots: nombre d'instants enregistrés dans l'historique.

        Returns:
            La solution, son historique et la dérive de masse observée.
        """
        if total_time <= 0.0:
            raise ValueError("la durée d'intégration doit être strictement positive")
        if snapshots < 2:
            raise ValueError("il faut au moins deux instantanés (début et fin)")

        current = self.initial_condition() if density is None else np.array(density, dtype=float)
        if current.shape != self.grid.shape:
            raise ValueError("la condition initiale doit avoir la forme de la grille")

        step = self.stable_time_step() if time_step is None else float(time_step)
        iterations = max(1, int(np.ceil(total_time / step)))
        step = total_time / iterations

        # Les instants d'enregistrement sont calculés d'avance et dédupliqués : un
        # simple test de modulo enregistrerait deux fois le dernier pas dès que le
        # nombre d'itérations n'est pas un multiple exact de l'intervalle, et
        # l'historique porterait deux instantanés au même instant.
        recorded_iterations = set(
            np.linspace(1, iterations, snapshots - 1).round().astype(int).tolist()
        )
        initial_mass = self.mass(current)

        times = [0.0]
        history = [current.copy()]
        mass_drift = 0.0

        for iteration in range(1, iterations + 1):
            current = self._advance(current, step)

            mass_drift = max(mass_drift, abs(self.mass(current) - initial_mass))

            if iteration in recorded_iterations:
                times.append(iteration * step)
                history.append(current.copy())

        return FokkerPlanckSolution(
            grid=self.grid,
            density=current,
            times=np.asarray(times),
            history=np.asarray(history),
            mass_drift=mass_drift,
        )

    def _advance(self, density: np.ndarray, time_step: float) -> np.ndarray:
        """Un pas de temps explicite, en forme de flux conservative.

        L'advection est décentrée **amont** : la densité transportée à travers une
        face est prélevée du côté d'où vient le courant. Une interpolation centrée
        serait plus précise sur le papier, mais elle est inconditionnellement
        instable dès que le nombre de Péclet de maille :math:`|A|\\Delta x / B`
        dépasse 2 — ce qui est le régime normal de ce modèle, puisque la diffusion
        est en :math:`1/N` et devient minuscule pour une grande population. Le
        décentrement amont est monotone : il ne peut pas produire de densité
        négative ni d'oscillation de maille.
        """
        # Flux advectif sur les faces intérieures, décentré selon le signe de la dérive.
        upstream = np.where(self._face_drift >= 0.0, density[:-1], density[1:])
        advective_flux = self._face_drift * upstream

        # Flux diffusif : dérivée de (B·P) évaluée sur les mêmes faces.
        scaled = self._cell_diffusion * density
        diffusive_flux = (scaled[1:] - scaled[:-1]) / self._spacing

        interior_flux = advective_flux - diffusive_flux
        # Flux nul aux deux bords : aucune probabilité ne quitte le domaine.
        flux = np.concatenate([[0.0], interior_flux, [0.0]])

        return density - time_step * np.diff(flux) / self._spacing
