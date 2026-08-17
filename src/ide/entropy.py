"""Mesures d'entropie et définition de l'Index de Dissipation Entropique (IDE).

Le pont conceptuel du projet repose sur deux entropies qui mesurent la même chose
— la perte de pureté d'un état — dans deux mondes différents :

* l'entropie de von Neumann :math:`S(\\rho) = -\\mathrm{Tr}(\\rho \\ln \\rho)`,
  nulle pour un état quantique pur, strictement positive dès que le système
  s'intrique avec son environnement ;
* l'entropie de Shannon :math:`H(X) = -\\sum_i p_i \\log_2 p_i`, nulle pour une
  opinion unanime, maximale pour une population totalement fragmentée.

L'**IDE** est l'entropie de Shannon d'un fil d'actualité individuel, normalisée
par son maximum théorique pour vivre dans :math:`[0, 1]` et rester comparable
entre plateformes de tailles de catalogue différentes. C'est cette normalisation
qui en fait une métrique auditable : un seuil réglementaire exprimé en pourcentage
a un sens, un seuil exprimé en bits n'en a pas.

Avertissement d'échelle (voir ``docs/limites.md``, point 3) : l'entropie mesurée
ici porte sur la **distribution des opinions exposées à un individu**, pas sur
l'entropie de configuration de la population entière. La première décroît quand la
bulle se referme ; la seconde croît avec la taille du système. Les confondre est
l'erreur que l'audit du projet corrige.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np

__all__ = [
    "entropic_dissipation_index",
    "shannon_entropy",
    "shannon_entropy_from_counts",
    "von_neumann_entropy",
]

# En deçà de cette masse de probabilité, une modalité est traitée comme absente :
# la limite p·log(p) → 0 est prise explicitement plutôt que laissée à numpy.
_PROBABILITY_FLOOR = 1e-15


def _as_probability_vector(distribution: Iterable[float]) -> np.ndarray:
    """Valide une distribution discrète et la renvoie sous forme de tableau normalisé."""
    probabilities = np.asarray(list(distribution), dtype=float)

    if probabilities.ndim != 1 or probabilities.size == 0:
        raise ValueError("une distribution doit être un vecteur non vide")
    if np.any(probabilities < -_PROBABILITY_FLOOR):
        raise ValueError("une distribution ne peut pas contenir de probabilité négative")

    total_mass = probabilities.sum()
    if total_mass <= _PROBABILITY_FLOOR:
        raise ValueError("la masse totale de la distribution est nulle")

    return np.clip(probabilities, 0.0, None) / total_mass


def shannon_entropy(distribution: Iterable[float], base: float = 2.0) -> float:
    """Entropie de Shannon d'une distribution discrète d'opinions.

    La distribution est normalisée si sa somme diffère de 1, ce qui permet de
    passer indifféremment des probabilités ou des effectifs.

    Args:
        distribution: masses de probabilité (ou effectifs) des modalités d'opinion.
        base: base du logarithme. 2 donne des bits, ``numpy.e`` des nats.

    Returns:
        L'entropie en bits (ou en nats), dans :math:`[0, \\log_b k]`.

    Examples:
        Un accord unanime ne porte aucune incertitude :

        >>> round(shannon_entropy([1.0, 0.0, 0.0]), 12)
        0.0

        Quatre opinions équiprobables valent exactement deux bits :

        >>> round(shannon_entropy([1, 1, 1, 1]), 12)
        2.0
    """
    if base <= 1.0:
        raise ValueError("la base du logarithme doit être strictement supérieure à 1")

    probabilities = _as_probability_vector(distribution)
    support = probabilities[probabilities > _PROBABILITY_FLOOR]
    entropy = -np.sum(support * np.log(support)) / np.log(base)

    # Le rabattement sur zéro n'est pas seulement défensif : sur une distribution
    # dégénérée, la somme vide produit -0.0, un zéro négatif qui se propagerait
    # jusque dans l'IDE et les fichiers de résultats.
    return float(max(0.0, entropy))


def shannon_entropy_from_counts(labels: Sequence[object], base: float = 2.0) -> float:
    """Entropie de Shannon d'un échantillon d'étiquettes d'opinion.

    Raccourci pour le cas concret d'un fil d'actualité : on dispose d'une liste de
    contenus étiquetés (``["complot", "factuel", "complot", ...]``) plutôt que
    d'une distribution déjà agrégée.

    Args:
        labels: étiquettes observées, de n'importe quel type hachable.
        base: base du logarithme.

    Returns:
        L'entropie empirique de l'échantillon. Un échantillon vide vaut ``0.0``,
        par convention : un fil sans contenu ne porte aucune diversité.

    Examples:
        >>> shannon_entropy_from_counts(["a", "a", "b", "b"])
        1.0
    """
    if len(labels) == 0:
        return 0.0

    _, counts = np.unique(np.asarray(labels, dtype=object), return_counts=True)

    return shannon_entropy(counts, base=base)


def von_neumann_entropy(density_matrix: np.ndarray, base: float = np.e) -> float:
    """Entropie de von Neumann :math:`S(\\rho) = -\\mathrm{Tr}(\\rho \\ln \\rho)`.

    Calculée par diagonalisation : les valeurs propres de la matrice de densité
    forment une distribution classique, à laquelle on applique l'entropie de
    Shannon. C'est exactement le sens physique de la quantité — l'entropie de
    von Neumann est l'entropie de Shannon du mélange statistique révélé par la
    base propre.

    Args:
        density_matrix: matrice de densité hermitienne, de trace 1.
        base: base du logarithme. ``numpy.e`` (défaut) donne la convention
            physique en nats, 2 permet de comparer directement à l'IDE en bits.

    Returns:
        ``0.0`` pour un état pur, :math:`\\ln d` pour le mélange maximal en
        dimension :math:`d`.

    Raises:
        ValueError: si la matrice n'est pas carrée, hermitienne ou de trace 1.

    Examples:
        Un état pur — ici :math:`|0\\rangle` — a une entropie nulle :

        >>> import numpy as np
        >>> round(von_neumann_entropy(np.array([[1.0, 0.0], [0.0, 0.0]])), 12)
        0.0

        Le mélange maximal à deux niveaux vaut :math:`\\ln 2` :

        >>> round(von_neumann_entropy(np.eye(2) / 2), 12)
        0.69314718056
    """
    matrix = np.asarray(density_matrix)

    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("une matrice de densité doit être carrée")
    if not np.allclose(matrix, matrix.conj().T, atol=1e-10):
        raise ValueError("une matrice de densité doit être hermitienne")

    trace = np.trace(matrix).real
    if not np.isclose(trace, 1.0, atol=1e-8):
        raise ValueError(f"une matrice de densité doit avoir une trace de 1 (trace = {trace:.6f})")

    eigenvalues = np.linalg.eigvalsh(matrix).real
    # La diagonalisation numérique produit des valeurs propres légèrement négatives
    # pour un état pur ; on les rabat sur zéro avant de prendre le logarithme.
    populations = np.clip(eigenvalues, 0.0, None)

    return shannon_entropy(populations, base=base)


def entropic_dissipation_index(
    labels: Sequence[object],
    catalogue_size: int | None = None,
) -> float:
    """Index de Dissipation Entropique d'un fil d'actualité individuel.

    C'est la métrique proposée au régulateur : l'entropie de Shannon des opinions
    exposées à un utilisateur, rapportée à l'entropie maximale atteignable pour le
    même nombre de modalités.

    .. math::

        \\mathrm{IDE} = \\frac{H(X)}{\\log_2 k}

    Interprétation :

    * :math:`\\mathrm{IDE} = 1` — exposition parfaitement équilibrée entre les
      :math:`k` points de vue disponibles ;
    * :math:`\\mathrm{IDE} \\to 0` — bulle de filtres gelée, un seul point de vue
      occupe le fil. C'est l'état :math:`T \\to 0` du modèle d'Ising, celui que le
      mémorandum de régulation cherche à rendre juridiquement constatable.

    Args:
        labels: étiquettes des contenus servis à l'utilisateur sur la fenêtre
            d'observation (24 h dans le mémorandum).
        catalogue_size: nombre :math:`k` de points de vue que la plateforme
            *pourrait* servir. À défaut, le nombre de modalités effectivement
            observées est utilisé — mais ce défaut est optimiste : une bulle
            parfaitement fermée ne présente qu'une modalité, donc un dénominateur
            dégénéré. Un régulateur doit imposer un :math:`k` de référence.

    Returns:
        Un indice dans :math:`[0, 1]`.

    Raises:
        ValueError: si ``catalogue_size`` est plus petit que le nombre de
            modalités réellement observées.

    Examples:
        Fil équilibré sur quatre points de vue :

        >>> entropic_dissipation_index(["a", "b", "c", "d"], catalogue_size=4)
        1.0

        Bulle fermée, alors que la plateforme disposait de quatre points de vue :

        >>> entropic_dissipation_index(["a", "a", "a", "a"], catalogue_size=4)
        0.0
    """
    if len(labels) == 0:
        return 0.0

    observed_modalities = len(set(labels))
    reference_modalities = catalogue_size if catalogue_size is not None else observed_modalities

    if reference_modalities < observed_modalities:
        raise ValueError(
            f"catalogue_size={reference_modalities} est inférieur aux "
            f"{observed_modalities} modalités observées"
        )
    if reference_modalities <= 1:
        # Une seule modalité de référence : l'entropie maximale est nulle, le
        # rapport n'est pas défini. Le fil est par construction sans diversité.
        return 0.0

    maximal_entropy = np.log2(reference_modalities)

    return float(shannon_entropy_from_counts(labels) / maximal_entropy)
