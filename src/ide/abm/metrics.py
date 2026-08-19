"""Observables du modèle à agents.

Trois mesures sont suivies à chaque pas de temps, et leur écart est instructif :

* la **polarisation**, moyenne des distances à la modération, décrit l'état
  *macroscopique* de la société ;
* l'**IDE moyen**, moyenne des index individuels, décrit ce que chaque individu
  *voit* ;
* la **fraction contaminée** décrit la diffusion de la fausse information.

Une société peut être fortement polarisée tout en offrant un IDE élevé — quatre
blocs qui s'affrontent en se voyant — ou faiblement polarisée avec un IDE
effondré, si tout le monde partage la même opinion modérée. C'est exactement la
distinction d'échelle du point 3 de l'audit : l'entropie de la population n'est pas
l'entropie de l'exposition individuelle, et le régulateur doit mesurer la seconde.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, fields

import numpy as np

from ide.abm.agents import Citizen
from ide.entropy import label_diversity_index

__all__ = [
    "SocietyMetrics",
    "csv_header",
    "measure",
]

# Distance maximale à la modération dans un compas carré : le coin, à √2.
_MAXIMAL_RADICALISM = float(np.sqrt(2.0))


@dataclass(frozen=True)
class SocietyMetrics:
    """Instantané de l'état d'une société simulée.

    Attributes:
        step: pas de temps.
        polarisation: distance moyenne à la modération, en pourcentage du maximum.
        exposure_index: IDE moyen sur la population, dans :math:`[0, 1]`.
        infected_fraction: proportion d'individus porteurs d'une fausse croyance.
        frozen_fraction: proportion d'individus dont l'IDE individuel est tombé
            sous le seuil critique — la part de la population en bulle gelée, celle
            que le mémorandum rend juridiquement constatable.
    """

    step: int
    polarisation: float
    exposure_index: float
    infected_fraction: float
    frozen_fraction: float

    def as_row(self) -> list[float]:
        """Ligne CSV, dans l'ordre de :func:`csv_header`."""
        return [getattr(self, column.name) for column in fields(self)]


def csv_header() -> list[str]:
    """En-tête CSV correspondant à :meth:`SocietyMetrics.as_row`."""
    return [column.name for column in fields(SocietyMetrics)]


def measure(
    citizens: Sequence[Citizen],
    step: int,
    catalogue_size: int = 4,
    critical_index: float = 0.4,
) -> SocietyMetrics:
    """Calcule les observables d'une population à un instant donné.

    Args:
        citizens: population mesurée.
        step: pas de temps courant.
        catalogue_size: nombre de points de vue de référence — les quatre quadrants
            du compas, sauf modèle étendu.
        critical_index: seuil sous lequel un individu est réputé en bulle gelée.

    Returns:
        L'instantané mesuré. Une population vide renvoie des valeurs nulles plutôt
        que de lever une exception : cela évite d'interrompre une simulation dont la
        population aurait été vidée par un scénario extrême.
    """
    if not citizens:
        return SocietyMetrics(step=step, polarisation=0.0, exposure_index=0.0,
                              infected_fraction=0.0, frozen_fraction=0.0)

    radicalism = np.array([citizen.radicalism for citizen in citizens])
    individual_indices = np.array(
        [
            label_diversity_index(list(citizen.exposure), catalogue_size=catalogue_size)
            for citizen in citizens
        ]
    )
    infected = np.array([citizen.infected for citizen in citizens])

    return SocietyMetrics(
        step=step,
        polarisation=float(radicalism.mean() / _MAXIMAL_RADICALISM * 100.0),
        exposure_index=float(individual_indices.mean()),
        infected_fraction=float(infected.mean()),
        frozen_fraction=float((individual_indices < critical_index).mean()),
    )
