"""Index de Dissipation Entropique — noyau scientifique.

Deux objets distincts structurent ce paquet, et la distinction est délibérée
(voir ``docs/limites.md``, point 1) :

* **IDE** — *Index de Dissipation Entropique* : une métrique auditable de la
  diversité informationnelle d'un fil d'actualité, destinée au régulateur.
  Implémentée dans :mod:`ide.entropy`.
* **ADE** — *Algorithme de Dissipation Entropique* : un filtre de recommandation
  qui optimise cet index au lieu de l'engagement brut. Implémenté dans
  :mod:`ide.ade`.

Les autres modules fournissent les modèles de physique statistique qui fondent
l'index : :mod:`ide.ising`, :mod:`ide.voter`, :mod:`ide.fokker_planck`,
:mod:`ide.resonance`, et le modèle à agents :mod:`ide.abm`.

Tous les modules sont purs (aucune entrée-sortie) et prennent une graine
explicite lorsqu'ils sont stochastiques, afin de rester testables.
"""

from ide.ade import EntropicScorer, annealing_coefficient, entropic_score
from ide.entropy import (
    entropic_dissipation_index,
    shannon_entropy,
    shannon_entropy_from_counts,
    von_neumann_entropy,
)
from ide.fokker_planck import (
    FokkerPlanckSolver,
    diffusion_term,
    drift_term,
    stationary_distribution,
)
from ide.ising import IsingModel, hysteresis_loop, onsager_critical_temperature
from ide.resonance import ResonanceParameters, simulate_resonance
from ide.voter import VoterModel, consensus_time_scaling

__version__ = "0.1.0"

__all__ = [
    "EntropicScorer",
    "FokkerPlanckSolver",
    "IsingModel",
    "ResonanceParameters",
    "VoterModel",
    "annealing_coefficient",
    "consensus_time_scaling",
    "diffusion_term",
    "drift_term",
    "entropic_dissipation_index",
    "entropic_score",
    "hysteresis_loop",
    "onsager_critical_temperature",
    "shannon_entropy",
    "shannon_entropy_from_counts",
    "simulate_resonance",
    "stationary_distribution",
    "von_neumann_entropy",
    "__version__",
]
