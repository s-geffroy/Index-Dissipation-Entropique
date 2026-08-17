"""Style et enregistrement des figures du dépôt.

Ce module est volontairement séparé du noyau scientifique : ``matplotlib`` est une
dépendance facultative (extra ``lab``), et les modèles de :mod:`ide` doivent rester
importables sans lui. Il n'est utilisé que par les notebooks.

Toutes les figures de la note sont produites ici, avec le même style et le même
chemin de sortie. Aucune illustration du dépôt n'est dessinée à la main : chacune
est régénérable par ``docker compose run --rm notebooks``, ce qui rend les figures
auditables au même titre que les chiffres.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt

__all__ = [
    "FIGURE_DIRECTORY",
    "PALETTE",
    "save_figure",
    "use_project_style",
]

# Les figures alimentent directement les sources LaTeX de la note.
FIGURE_DIRECTORY = Path(__file__).resolve().parents[2] / "paper" / "figures"

#: Palette de rôles, stable d'une figure à l'autre pour que le lecteur puisse
#: transporter sa lecture d'un graphique au suivant.
PALETTE = {
    "order": "#1f4e79",  # consensus, conformisme, régime ordonné
    "disorder": "#c1440e",  # cacophonie, agitation, régime désordonné
    "field": "#7a1f8f",  # champ médiatique, désinformation
    "remedy": "#1b7a4a",  # dissipation entropique, vérification, remède
    "neutral": "#5a5a5a",  # repères, seuils, annotations
}


def use_project_style() -> None:
    """Applique le style commun à toutes les figures du dépôt."""
    mpl.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 160,
            "savefig.bbox": "tight",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "grid.linestyle": "-",
            "legend.frameon": False,
            "lines.linewidth": 1.8,
            "figure.autolayout": True,
        }
    )


def save_figure(figure: plt.Figure, name: str) -> Path:
    """Enregistre une figure dans ``paper/figures/`` et renvoie son chemin.

    Args:
        figure: figure à enregistrer.
        name: nom de fichier, extension incluse (``"fig02_transition.png"``).

    Returns:
        Le chemin du fichier écrit.
    """
    if not name:
        raise ValueError("le nom de fichier ne peut pas être vide")

    FIGURE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    destination = FIGURE_DIRECTORY / name
    figure.savefig(destination)

    return destination
