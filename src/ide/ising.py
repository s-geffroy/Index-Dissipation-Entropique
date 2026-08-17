"""Modèle d'Ising 2D : température sociale, champ médiatique et hystérésis.

Transposition du modèle de ferromagnétisme d'Ising (1925) à la dynamique
d'opinion, dans la lignée des travaux de sociophysique de Galam. Chaque individu
porte un spin :math:`s_i \\in \\{-1, +1\\}` — son opinion binaire — et la
population évolue selon la distribution de Gibbs-Boltzmann :

.. math::

    P(\\sigma) = \\frac{1}{Z}
    \\exp\\!\\left(\\frac{J \\sum_{\\langle i,j \\rangle} s_i s_j
                        + H \\sum_i s_i}{k_B T}\\right)

Les trois paramètres reçoivent une lecture sociologique :

* :math:`J` — la **force de conformisme local**, le coût psychologique d'un
  désaccord avec ses voisins immédiats ;
* :math:`T` — la **température sociale**, le niveau d'agitation, d'irrationalité
  ou d'ouverture aux fluctuations. À :math:`T \\to 0` le conformisme gèle la
  population ; à :math:`T \\to \\infty` les avis fluctuent sans écouter personne ;
* :math:`H` — le **champ médiatique externe**, l'injection asymétrique de
  désinformation qui brise la symétrie du système.

L'intérêt du modèle pour ce travail tient à deux propriétés vérifiables
numériquement, et non à l'analogie elle-même :

1. l'existence d'une température critique — en 2D, la valeur exacte d'Onsager
   :math:`T_c / J = 2 / \\ln(1 + \\sqrt{2}) \\approx 2{,}269` — qui sépare le
   régime de consensus du régime de fluctuation permanente ;
2. l'**hystérésis** : sous :math:`T_c`, couper le champ (:math:`H \\to 0`) ne
   ramène pas l'aimantation à zéro. C'est la formalisation de la persistance
   d'une croyance après démenti officiel, et la justification du contre-champ
   :math:`-H` proposé dans le mémorandum.

L'implémentation utilise une mise à jour de Metropolis en damier : les spins
d'une même couleur n'étant jamais voisins, ils peuvent être proposés en
parallèle sans violer la condition de balance détaillée, ce qui rend la
simulation vectorisable sous numpy.
"""

from __future__ import annotations

# `field` est ici le nom du champ magnétique médiatique H, paramètre central du
# modèle : l'utilitaire de dataclasses est donc importé sous un alias explicite
# plutôt que de renommer le paramètre physique.
from dataclasses import dataclass
from dataclasses import field as dataclass_field

import numpy as np

__all__ = [
    "HysteresisLoop",
    "IsingModel",
    "hysteresis_loop",
    "onsager_critical_temperature",
]


def onsager_critical_temperature(coupling: float = 1.0) -> float:
    """Température critique exacte du modèle d'Ising 2D (solution d'Onsager, 1944).

    .. math:: \\frac{T_c}{J} = \\frac{2}{\\ln(1 + \\sqrt{2})} \\approx 2{,}269

    Sert de point d'étalonnage : toute implémentation Monte-Carlo correcte doit
    retrouver cette valeur, ce qui donne au projet un test de non-régression
    indépendant de ses propres hypothèses sociologiques.

    Args:
        coupling: force de conformisme :math:`J`, strictement positive.

    Returns:
        La température critique, dans les mêmes unités que :math:`J` (avec
        :math:`k_B = 1`).

    Examples:
        >>> round(onsager_critical_temperature(), 4)
        2.2692
    """
    if coupling <= 0.0:
        raise ValueError("la force de conformisme J doit être strictement positive")

    return float(2.0 * coupling / np.log(1.0 + np.sqrt(2.0)))


@dataclass
class IsingModel:
    """Population d'opinions binaires sur un réseau carré périodique.

    Args:
        size: côté :math:`L` du réseau. La population compte :math:`L^2` individus.
        temperature: température sociale :math:`T` (avec :math:`k_B = 1`).
        field: champ médiatique externe :math:`H`. Positif, il pousse vers
            l'opinion ``+1``.
        coupling: force de conformisme local :math:`J`.
        seed: graine du générateur, pour la reproductibilité.
        initial_state: ``"aligned"`` démarre d'un consensus parfait (utile pour
            les cycles d'hystérésis, qui doivent partir d'un état saturé),
            ``"random"`` d'une population sans opinion dominante.

    Examples:
        >>> model = IsingModel(size=16, temperature=1.0, seed=0)
        >>> model.run(sweeps=50)
        >>> abs(model.magnetisation) > 0.8  # T << T_c : consensus figé
        True
    """

    size: int = 32
    temperature: float = 2.0
    field: float = 0.0
    coupling: float = 1.0
    seed: int | None = None
    initial_state: str = "random"

    spins: np.ndarray = dataclass_field(init=False, repr=False)
    _rng: np.random.Generator = dataclass_field(init=False, repr=False)
    _masks: tuple[np.ndarray, np.ndarray] = dataclass_field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.size < 2:
            raise ValueError("le réseau doit compter au moins 2 sites par côté")
        if self.temperature <= 0.0:
            raise ValueError(
                "la température sociale doit être strictement positive ; "
                "T = 0 correspond à un gel total et ne se simule pas par Metropolis"
            )
        if self.coupling <= 0.0:
            raise ValueError("la force de conformisme J doit être strictement positive")

        self._rng = np.random.default_rng(self.seed)

        if self.initial_state == "aligned":
            self.spins = np.ones((self.size, self.size), dtype=np.int8)
        elif self.initial_state == "random":
            self.spins = self._rng.choice(
                np.array([-1, 1], dtype=np.int8), size=(self.size, self.size)
            )
        else:
            raise ValueError("initial_state doit valoir 'aligned' ou 'random'")

        # Damier : deux sous-réseaux dont aucun site n'est voisin d'un site de la
        # même couleur, ce qui autorise des propositions de retournement simultanées.
        rows, columns = np.indices((self.size, self.size))
        even = (rows + columns) % 2 == 0
        self._masks = (even, ~even)

    @property
    def population(self) -> int:
        """Nombre d'individus :math:`N = L^2`."""
        return self.size * self.size

    @property
    def magnetisation(self) -> float:
        """Aimantation sociale :math:`M = \\langle s \\rangle`, dans :math:`[-1, 1]`.

        Vaut :math:`\\pm 1` pour un consensus parfait, 0 pour une population
        équitablement divisée — ou pour une population dont les blocs opposés se
        compensent, ce qui est une limite connue de l'indicateur.
        """
        return float(self.spins.mean())

    @property
    def energy_per_spin(self) -> float:
        """Énergie par individu, la « frustration sociale » moyenne.

        .. math:: e = -J \\langle s_i s_j \\rangle_{\\text{voisins}} - H \\langle s \\rangle
        """
        neighbour_sum = self._neighbour_sum()
        # Chaque lien est compté deux fois par la somme sur les voisins : d'où le 1/2.
        interaction = -0.5 * self.coupling * float((self.spins * neighbour_sum).mean())

        return interaction - self.field * self.magnetisation

    def _neighbour_sum(self) -> np.ndarray:
        """Somme des quatre voisins de chaque site, avec conditions périodiques."""
        return (
            np.roll(self.spins, 1, axis=0)
            + np.roll(self.spins, -1, axis=0)
            + np.roll(self.spins, 1, axis=1)
            + np.roll(self.spins, -1, axis=1)
        ).astype(np.int8)

    def sweep(self) -> None:
        """Un balayage de Metropolis : chaque individu se voit proposer un changement d'avis."""
        for mask in self._masks:
            neighbour_sum = self._neighbour_sum()
            # Coût énergétique du retournement : ΔE = 2 s_i (J Σ_voisins + H).
            energy_change = 2.0 * self.spins * (self.coupling * neighbour_sum + self.field)

            # Un changement qui réduit la frustration est toujours accepté ; sinon il
            # l'est avec la probabilité de Boltzmann — c'est là qu'agit la température.
            acceptance = np.exp(-np.clip(energy_change, 0.0, None) / self.temperature)
            accepted = mask & (self._rng.random(self.spins.shape) < acceptance)

            self.spins = np.where(accepted, -self.spins, self.spins).astype(np.int8)

    def run(self, sweeps: int) -> None:
        """Enchaîne ``sweeps`` balayages sans rien mesurer (phase de thermalisation)."""
        if sweeps < 0:
            raise ValueError("le nombre de balayages ne peut pas être négatif")

        for _ in range(sweeps):
            self.sweep()

    def sample(self, sweeps: int = 200, burn_in: int = 200) -> dict[str, float]:
        """Thermalise puis mesure les observables moyennes de la population.

        Args:
            sweeps: nombre de balayages de mesure.
            burn_in: balayages de thermalisation écartés de la moyenne. Les ignorer
                biaiserait la mesure vers l'état initial.

        Returns:
            Un dictionnaire contenant :

            * ``magnetisation`` — moyenne signée, proche de 0 par symétrie à
              :math:`H = 0` même sous :math:`T_c`, puisque le système peut basculer ;
            * ``abs_magnetisation`` — moyenne de :math:`|M|`, l'estimateur utilisé
              pour localiser la transition sur un réseau fini ;
            * ``energy_per_spin`` — frustration moyenne ;
            * ``susceptibility`` — :math:`\\chi = N (\\langle M^2 \\rangle -
              \\langle |M| \\rangle^2) / T`, dont le maximum en fonction de
              :math:`T` localise la température critique.
        """
        if sweeps < 1:
            raise ValueError("il faut au moins un balayage de mesure")

        self.run(burn_in)

        magnetisations = np.empty(sweeps)
        energies = np.empty(sweeps)
        for index in range(sweeps):
            self.sweep()
            magnetisations[index] = self.magnetisation
            energies[index] = self.energy_per_spin

        absolute = np.abs(magnetisations)
        variance = float((magnetisations**2).mean() - absolute.mean() ** 2)

        return {
            "magnetisation": float(magnetisations.mean()),
            "abs_magnetisation": float(absolute.mean()),
            "energy_per_spin": float(energies.mean()),
            "susceptibility": self.population * max(variance, 0.0) / self.temperature,
        }


@dataclass(frozen=True)
class HysteresisLoop:
    """Cycle d'hystérésis sociale : réponse de l'opinion à un champ médiatique cyclique.

    Attributes:
        fields: valeurs du champ :math:`H` parcourues, aller puis retour.
        magnetisations: aimantation mesurée pour chaque valeur du champ.
        temperature: température sociale du cycle.
        area: aire du cycle, mesure de la « mémoire » du système.
    """

    fields: np.ndarray
    magnetisations: np.ndarray
    temperature: float
    area: float

    @property
    def remanent_magnetisation(self) -> float:
        """Aimantation rémanente : l'opinion qui subsiste une fois le champ coupé.

        C'est la quantité centrale du mémorandum. Une valeur non nulle signifie
        qu'un démenti (:math:`H \\to 0`) ne suffit pas à dissiper la croyance :
        le conformisme de groupe a pris le relais du champ médiatique.
        """
        # Le champ le plus proche de zéro sur la branche descendante, c'est-à-dire
        # dans la seconde moitié du parcours aller-retour.
        descending = len(self.fields) // 2
        nearest_zero = descending + int(np.argmin(np.abs(self.fields[descending:])))

        return float(abs(self.magnetisations[nearest_zero]))


def hysteresis_loop(
    temperature: float,
    max_field: float = 1.0,
    steps: int = 21,
    size: int = 24,
    sweeps_per_step: int = 40,
    coupling: float = 1.0,
    seed: int | None = 0,
) -> HysteresisLoop:
    """Parcourt un cycle de champ médiatique et mesure la mémoire de l'opinion.

    Le protocole reproduit les trois phases décrites dans la note : injection d'un
    champ massif, démenti (retour à :math:`H = 0`), puis contre-champ négatif. Sous
    la température critique, la courbe de retour ne repasse pas par l'origine —
    c'est l'hystérésis. Au-dessus, l'agitation dissipe la mémoire et le cycle se
    referme sur lui-même.

    Args:
        temperature: température sociale, maintenue constante sur tout le cycle.
        max_field: amplitude maximale :math:`\\pm H` du champ médiatique.
        steps: nombre de paliers de champ sur une branche du cycle.
        size: côté du réseau.
        sweeps_per_step: balayages de relaxation à chaque palier. Trop peu, et
            l'aire mesurée traduit un simple retard de convergence plutôt qu'une
            vraie hystérésis thermodynamique.
        coupling: force de conformisme.
        seed: graine du générateur.

    Returns:
        Le cycle mesuré, avec son aire et son aimantation rémanente.

    Examples:
        Sous la température critique, le cycle enferme une aire :

        >>> loop = hysteresis_loop(temperature=1.5, steps=9, size=16, sweeps_per_step=20)
        >>> loop.area > 0.05
        True
    """
    if max_field <= 0.0:
        raise ValueError("l'amplitude du champ doit être strictement positive")
    if steps < 3:
        raise ValueError("un cycle demande au moins 3 paliers par branche")

    descending = np.linspace(max_field, -max_field, steps)
    ascending = np.linspace(-max_field, max_field, steps)
    schedule = np.concatenate([descending, ascending])

    model = IsingModel(
        size=size,
        temperature=temperature,
        field=max_field,
        coupling=coupling,
        seed=seed,
        initial_state="aligned",
    )
    # Saturation initiale : le cycle doit partir d'un état pleinement aimanté,
    # sinon la première branche mélange transitoire et réponse au champ.
    model.run(sweeps_per_step * 2)

    magnetisations = np.empty(schedule.size)
    for index, applied_field in enumerate(schedule):
        model.field = float(applied_field)
        model.run(sweeps_per_step)
        magnetisations[index] = model.magnetisation

    # Aire du cycle par la formule du lacet (Green), en refermant la courbe.
    closed_fields = np.append(schedule, schedule[0])
    closed_magnetisations = np.append(magnetisations, magnetisations[0])
    area = 0.5 * np.abs(
        np.sum(
            closed_fields[:-1] * closed_magnetisations[1:]
            - closed_fields[1:] * closed_magnetisations[:-1]
        )
    )

    return HysteresisLoop(
        fields=schedule,
        magnetisations=magnetisations,
        temperature=temperature,
        area=float(area),
    )
