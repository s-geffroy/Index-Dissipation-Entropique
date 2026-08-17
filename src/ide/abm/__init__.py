"""Modèle à agents « compas politique ».

Refonte headless du prototype ``pygame`` du fil de travail, conservé pour mémoire
sous ``legacy/simulation_thread_2026-08.py``. Le modèle transpose les trois règles
des *Boids* de Reynolds en forces sociales — séparation/distinction, alignement/
conformisme, cohésion/appartenance — et produit l'IDE comme observable, ce qui relie
la simulation individuelle à la métrique de régulation.
"""

from ide.abm.agents import Citizen, FactChecker, MediaOutlet, quadrant_label
from ide.abm.metrics import SocietyMetrics, csv_header, measure
from ide.abm.model import SocietyModel, SocietyParameters, default_media_landscape

__all__ = [
    "Citizen",
    "FactChecker",
    "MediaOutlet",
    "SocietyMetrics",
    "SocietyModel",
    "SocietyParameters",
    "csv_header",
    "default_media_landscape",
    "measure",
    "quadrant_label",
]
