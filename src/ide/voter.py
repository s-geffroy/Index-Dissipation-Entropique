"""Voter Model : effet pur de la taille de la population sur le temps de consensus.

Le Voter Model (Clifford & Sudbury 1973 ; Holley & Liggett 1975) isole ce que le
modèle d'Ising mêle à la thermodynamique : la seule **contagion sociale**, sans
température. À chaque interaction, un individu choisi au hasard adopte l'opinion
d'un voisin choisi au hasard. Aucun paramètre libre, aucune irrationalité — juste
de l'imitation.

Sa vertu est de fournir des lois d'échelle exactes pour le temps de consensus,
mesuré ici en **balayages** (un balayage = :math:`N` interactions élémentaires,
soit une interaction par individu en moyenne) :

===================  =========================
Topologie            Temps de consensus moyen
===================  =========================
Champ moyen          :math:`\\langle \\tau \\rangle \\propto N`
Anneau 1D            :math:`\\langle \\tau \\rangle \\propto N^2`
===================  =========================

Ces lois portent un enseignement qui **corrige** le récit du fil de travail
d'origine (voir ``docs/limites.md``, point 12) : une connectivité globale de type
« petit monde » *accélère* la convergence vers un consensus au lieu de l'empêcher.
Ce n'est donc pas la connectivité qui fragmente une société, mais le **biais
directionnel** :math:`h` et l'homophilie qui déterminent *vers quoi* elle converge.
Le champ de désinformation, pas la topologie, est le coupable.

Le biais :math:`h` modélise ce champ : avec la probabilité :math:`h`, l'individu
n'écoute pas son voisin mais la source médiatique, qui pousse toujours vers
l'opinion ``+1``.

.. note::
    Le fil d'origine écrivait ces transitions
    :math:`P(x \\to x + 1/N) = x(1-x) + h(1-x)` et
    :math:`P(x \\to x - 1/N) = x(1-x) - hx`. La seconde devient **négative** dès
    que :math:`h > 1 - x`, ce qui n'est pas une probabilité. La forme retenue ici
    mélange les deux canaux d'influence au lieu de les additionner :

    .. math::

        P(x \\to x + 1/N) &= (1-h)\\,x(1-x) + h\\,(1-x) \\\\
        P(x \\to x - 1/N) &= (1-h)\\,x(1-x)

    Elle reste positive sur tout :math:`h \\in [0, 1]`, se réduit exactement au
    Voter Model classique en :math:`h = 0`, et conserve la dérive asymétrique qui
    faisait l'intérêt de la formulation initiale.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

__all__ = [
    "ConsensusScaling",
    "VoterModel",
    "consensus_time_scaling",
]

Topology = Literal["mean_field", "ring"]


@dataclass
class VoterModel:
    """Population d'opinions binaires évoluant par imitation.

    Args:
        population: nombre :math:`N` d'individus.
        topology: ``"mean_field"`` — chacun peut imiter n'importe qui (réseau
            social globalisé) ; ``"ring"`` — chacun n'imite que ses deux voisins
            immédiats (voisinage géographique).
        bias: intensité :math:`h \\in [0, 1]` du champ de désinformation, qui
            pousse vers l'opinion ``+1``. À 0, le modèle est symétrique.
        initial_fraction: fraction initiale d'individus d'opinion ``+1``.
        seed: graine du générateur.

    Examples:
        >>> model = VoterModel(population=200, topology="mean_field", seed=1)
        >>> sweeps = model.run_until_consensus(max_sweeps=5_000)
        >>> model.has_consensus
        True
    """

    population: int = 100
    topology: Topology = "mean_field"
    bias: float = 0.0
    initial_fraction: float = 0.5
    seed: int | None = None

    def __post_init__(self) -> None:
        if self.population < 2:
            raise ValueError("il faut au moins 2 individus pour qu'une imitation ait un sens")
        if not 0.0 <= self.bias <= 1.0:
            raise ValueError("le biais h doit appartenir à [0, 1]")
        if not 0.0 <= self.initial_fraction <= 1.0:
            raise ValueError("la fraction initiale doit appartenir à [0, 1]")
        if self.topology not in ("mean_field", "ring"):
            raise ValueError("la topologie doit valoir 'mean_field' ou 'ring'")

        self._rng = np.random.default_rng(self.seed)

        positives = int(round(self.initial_fraction * self.population))
        self._opinions = np.zeros(self.population, dtype=np.int8)
        self._opinions[:positives] = 1
        self._rng.shuffle(self._opinions)

        # En champ moyen, seul le nombre d'opinions « + » compte : la dynamique se
        # réduit exactement à une chaîne de naissance-mort, bien plus rapide à
        # simuler que N agents individuels.
        self._positive_count = int(self._opinions.sum())

    @property
    def fraction(self) -> float:
        """Fraction :math:`x` de la population portant l'opinion ``+1``."""
        if self.topology == "mean_field":
            return self._positive_count / self.population

        return float(self._opinions.mean())

    @property
    def has_consensus(self) -> bool:
        """Vrai si la population est unanime, dans un sens ou dans l'autre."""
        return self.fraction in (0.0, 1.0)

    def _step_mean_field(self) -> None:
        """Une interaction en champ moyen, via la chaîne de naissance-mort équivalente."""
        fraction = self._positive_count / self.population
        encounter = fraction * (1.0 - fraction)

        probability_up = (1.0 - self.bias) * encounter + self.bias * (1.0 - fraction)
        probability_down = (1.0 - self.bias) * encounter

        draw = self._rng.random()
        if draw < probability_up:
            self._positive_count = min(self.population, self._positive_count + 1)
        elif draw < probability_up + probability_down:
            self._positive_count = max(0, self._positive_count - 1)

    def _step_ring(self) -> None:
        """Une interaction sur l'anneau : imitation d'un des deux voisins immédiats."""
        listener = self._rng.integers(self.population)

        if self.bias > 0.0 and self._rng.random() < self.bias:
            self._opinions[listener] = 1
            return

        offset = 1 if self._rng.random() < 0.5 else -1
        speaker = (listener + offset) % self.population
        self._opinions[listener] = self._opinions[speaker]

    def sweep(self) -> None:
        """Un balayage : :math:`N` interactions élémentaires."""
        step = self._step_mean_field if self.topology == "mean_field" else self._step_ring

        for _ in range(self.population):
            step()

    def run_until_consensus(self, max_sweeps: int = 100_000) -> float:
        """Simule jusqu'à l'unanimité et renvoie le temps écoulé, en balayages.

        Args:
            max_sweeps: garde-fou. Avec un biais nul, le temps de consensus est
                fini mais sa queue de distribution est lourde ; sans plafond, une
                réalisation malheureuse bloquerait la suite de tests.

        Returns:
            Le nombre de balayages nécessaires. Si le plafond est atteint sans
            consensus, ``max_sweeps`` est renvoyé — la valeur est alors une borne
            inférieure, et ``has_consensus`` permet de le détecter.
        """
        if max_sweeps < 1:
            raise ValueError("max_sweeps doit être au moins 1")

        for elapsed in range(1, max_sweeps + 1):
            self.sweep()
            if self.has_consensus:
                return float(elapsed)

        return float(max_sweeps)

    def trajectory(self, sweeps: int) -> np.ndarray:
        """Enregistre la fraction :math:`x` après chaque balayage.

        Utile pour visualiser la dérive imposée par le champ de désinformation :
        à :math:`h = 0` la trajectoire est une marche aléatoire non biaisée, à
        :math:`h > 0` elle glisse systématiquement vers 1.
        """
        if sweeps < 1:
            raise ValueError("il faut au moins un balayage")

        history = np.empty(sweeps)
        for index in range(sweeps):
            self.sweep()
            history[index] = self.fraction

        return history


@dataclass(frozen=True)
class ConsensusScaling:
    """Loi d'échelle mesurée du temps de consensus en fonction de la taille.

    Attributes:
        populations: tailles :math:`N` testées.
        mean_times: temps de consensus moyens, en balayages.
        exponent: exposant :math:`\\alpha` de l'ajustement
            :math:`\\langle \\tau \\rangle \\propto N^{\\alpha}`, obtenu par
            régression linéaire en échelle log-log.
        topology: topologie testée.
    """

    populations: np.ndarray
    mean_times: np.ndarray
    exponent: float
    topology: Topology


def consensus_time_scaling(
    populations: tuple[int, ...] = (32, 64, 128),
    topology: Topology = "mean_field",
    repeats: int = 8,
    max_sweeps: int = 200_000,
    bias: float = 0.0,
    seed: int = 0,
) -> ConsensusScaling:
    """Mesure l'exposant de la loi d'échelle :math:`\\langle \\tau \\rangle \\propto N^{\\alpha}`.

    C'est la vérification numérique de l'argument central sur la taille : le temps
    nécessaire pour qu'une population s'accorde croît avec :math:`N`, jusqu'à
    dépasser toute échelle de temps humaine pertinente. Le résultat attendu est
    :math:`\\alpha \\approx 1` en champ moyen et :math:`\\alpha \\approx 2` sur un
    anneau.

    Args:
        populations: tailles à tester. Au moins deux valeurs, sinon aucune pente
            n'est définie.
        topology: topologie du réseau social.
        repeats: réalisations indépendantes par taille. Le temps de consensus a une
            variance élevée ; en dessous de 5 réalisations, l'exposant mesuré est
            instable.
        max_sweeps: plafond par réalisation.
        bias: intensité du champ de désinformation.
        seed: graine de base ; chaque réalisation en dérive une distincte.

    Returns:
        Les temps mesurés et l'exposant ajusté.

    Examples:
        En champ moyen, le temps de consensus est linéaire en :math:`N` :

        >>> scaling = consensus_time_scaling(populations=(32, 64, 128), repeats=6, seed=0)
        >>> 0.7 < scaling.exponent < 1.4
        True
    """
    if len(populations) < 2:
        raise ValueError("il faut au moins deux tailles pour ajuster un exposant")
    if repeats < 1:
        raise ValueError("il faut au moins une réalisation par taille")

    sizes = np.asarray(populations, dtype=float)
    mean_times = np.empty(len(populations))

    for index, size in enumerate(populations):
        times = [
            VoterModel(
                population=size,
                topology=topology,
                bias=bias,
                seed=seed + index * 1_000 + replicate,
            ).run_until_consensus(max_sweeps=max_sweeps)
            for replicate in range(repeats)
        ]
        mean_times[index] = float(np.mean(times))

    exponent, _ = np.polyfit(np.log(sizes), np.log(mean_times), deg=1)

    return ConsensusScaling(
        populations=sizes,
        mean_times=mean_times,
        exponent=float(exponent),
        topology=topology,
    )
