"""Divergences conscientes du rang, d'après RADio (Vrijenhoek *et al.*, RecSys 2022).

Ce que l'index du dépôt ignorait
--------------------------------

Le [test adverse](gaming.py) a conduit à mesurer la diversité sur les **contenus** servis
plutôt que sur les étiquettes qui les annoncent. Il restait une hypothèse implicite, et elle
est fausse : que **la position d'un contenu dans le fil ne compte pas**.

Elle compte. Un lecteur consulte le premier élément d'un fil bien plus souvent que le
huitième, et une plateforme tenue à un plancher de diversité peut s'y conformer en plaçant les
contenus divergents **en bas**. L'entropie de position ne voit pas la différence : les deux
fils contiennent les mêmes contenus. C'est un quatrième adversaire, et il n'avait pas été
éprouvé.

Ce que RADio apporte
--------------------

Vrijenhoek *et al.* ([RecSys 2022](https://arxiv.org/abs/2209.13520)) proposent deux
déplacements, et ce module les reprend l'un et l'autre.

**Le rang, d'abord.** La distribution servie est pondérée par une remise de rang :

.. math:: Q^*(x) = \\frac{\\sum_i w_{R_i}\\,\\mathbb{1}[i \\in x]}{\\sum_i w_{R_i}}

avec :math:`w_{R_i} = 1/R_i` pour la remise réciproque. Une plateforme qui enterre sa
diversité voit sa mesure chuter, alors qu'une mesure non pondérée la lui aurait comptée.

**La divergence, ensuite.** Plutôt qu'une valeur ponctuelle — une entropie, une distance
moyenne — on mesure l'**écart entre deux distributions**, celle du fil servi et une
**référence** que l'on doit nommer. C'est ce qui résout le défaut de principe relevé par le
test adverse : l'entropie suppose que l'uniforme est l'idéal, l'entropie de Rao suppose que
l'écartement l'est, et aucune ne le dit. Une divergence oblige à déclarer la référence.

Les cinq références de RADio
----------------------------

Chacune des cinq mesures est la même divergence, appliquée à une paire de distributions
différente. C'est le choix de la référence qui porte la valeur normative, non la formule :

============================ ================================= =================================
Mesure                       Distribution servie               Référence
============================ ================================= =================================
:func:`calibration`          catégories du fil                 historique de lecture du lecteur
:func:`fragmentation`        événements du fil d'un lecteur    fil d'un autre lecteur
:func:`activation`           intensité affective du fil        intensité dans l'offre disponible
:func:`representation`       points de vue du fil              points de vue dans l'offre
:func:`alternative_voices`   voix minoritaires du fil          voix minoritaires dans l'offre
============================ ================================= =================================

**Le sens souhaitable de l'écart dépend de la mesure, et n'est pas donné par les
mathématiques.** Une calibration nulle signifie un fil parfaitement conforme à l'historique du
lecteur — ce qui est l'objectif d'un recommandeur libéral et la définition d'une bulle pour un
recommandeur délibératif. La divergence mesure ; elle ne tranche pas. C'est la question que le
[mémorandum](../../docs/memorandum.md) doit poser au régulateur, et non lui cacher.

Ce que ce module implémente, et ce qu'il ne peut pas
----------------------------------------------------

La mécanique — remise de rang, divergence de Jensen-Shannon bornée, les cinq instanciations —
est ici, avec ses tests. Les **données** ne le sont pas : mesurer l'activation demande des
scores d'affect, la représentation des annotations de points de vue, les voix alternatives un
codage des minorités. Aucun de ces attributs n'existe dans ce dépôt, et le
[corpus étendu](catalogue.py) a montré ce que coûte de prendre une étiquette disponible pour
l'attribut qu'on voudrait mesurer.
"""

from __future__ import annotations

import numpy as np

from ide.entropy import shannon_entropy

__all__ = [
    "DISCOUNTS",
    "activation",
    "alternative_voices",
    "calibration",
    "fragmentation",
    "jensen_shannon",
    "radio_divergence",
    "rank_aware_distribution",
    "rank_weights",
    "representation",
]

#: Remises de rang disponibles. ``"mrr"`` est celle qu'expose l'article ; ``"log"`` est la
#: remise logarithmique du nDCG, plus douce ; ``"none"`` retire la conscience du rang et rend
#: la mesure identique à une mesure ponctuelle sur l'ensemble servi.
DISCOUNTS: tuple[str, ...] = ("mrr", "log", "none")


def rank_weights(length: int, discount: str = "mrr") -> np.ndarray:
    """Poids d'attention accordés à chaque rang d'un fil.

    Args:
        length: nombre de positions du fil.
        discount: ``"mrr"`` pour :math:`1/R`, ``"log"`` pour :math:`1/\\log_2(R+1)`,
            ``"none"`` pour une attention uniforme.

    Returns:
        Les poids, non normalisés, du premier au dernier rang.
    """
    if length < 1:
        raise ValueError("un fil comporte au moins une position")
    if discount not in DISCOUNTS:
        raise ValueError(f"remise inconnue : {discount!r}")

    ranks = np.arange(1, length + 1, dtype=float)
    if discount == "mrr":
        return 1.0 / ranks
    if discount == "log":
        return 1.0 / np.log2(ranks + 1.0)
    return np.ones(length)


def rank_aware_distribution(
    assignments: np.ndarray,
    category_count: int,
    discount: str = "mrr",
) -> np.ndarray:
    """Distribution des catégories d'un fil, pondérée par l'attention accordée à chaque rang.

    Args:
        assignments: catégorie de l'élément servi à chaque position, dans l'ordre du fil.
        category_count: nombre de catégories du référentiel.
        discount: remise de rang, voir :func:`rank_weights`.

    Returns:
        Une distribution de probabilité sur les catégories. Sans remise, c'est la fréquence
        ordinaire ; avec remise, les premiers rangs y pèsent davantage — ce qui est le point.
    """
    assignments = np.asarray(assignments, dtype=int)
    if assignments.size == 0:
        raise ValueError("un fil vide n'a pas de distribution")
    if assignments.min() < 0 or assignments.max() >= category_count:
        raise ValueError("une catégorie servie sort du référentiel")

    weights = rank_weights(assignments.size, discount=discount)
    distribution = np.zeros(category_count)
    np.add.at(distribution, assignments, weights)

    return distribution / distribution.sum()


def jensen_shannon(first: np.ndarray, second: np.ndarray) -> float:
    """Divergence de Jensen-Shannon en base 2, donc bornée par 1.

    Le choix de la base n'est pas cosmétique : en base 2 la divergence appartient exactement
    à :math:`[0, 1]`, ce qui rend la normalisation *exacte* plutôt que conventionnelle. Un
    seuil réglementaire posé sur une grandeur normalisée par convention serait attaquable.

    Args:
        first: une distribution de probabilité.
        second: l'autre, de même longueur.

    Returns:
        0 pour deux distributions identiques, 1 pour deux supports disjoints.
    """
    first = np.asarray(first, dtype=float)
    second = np.asarray(second, dtype=float)
    if first.shape != second.shape:
        raise ValueError("les deux distributions doivent porter sur les mêmes catégories")

    first = first / first.sum()
    second = second / second.sum()
    mixture = 0.5 * (first + second)

    divergence = shannon_entropy(mixture) - 0.5 * (
        shannon_entropy(first) + shannon_entropy(second)
    )

    return float(np.clip(divergence, 0.0, 1.0))


def radio_divergence(
    served: np.ndarray,
    reference: np.ndarray,
    category_count: int,
    discount: str = "mrr",
) -> float:
    """Divergence consciente du rang entre un fil servi et une référence déclarée.

    C'est la mesure générale dont les cinq suivantes ne sont que des instanciations : ce qui
    les distingue est la **référence**, non le calcul.

    Args:
        served: catégorie de l'élément servi à chaque position du fil, **dans l'ordre**.
        reference: distribution de référence sur les catégories, déjà constituée. Les
            fonctions nommées ci-dessous la construisent chacune à leur façon ; la
            construire ici sur la foi du type des données rendrait la mesure dépendante
            d'un détail de représentation.
        category_count: taille du référentiel. Explicite à dessein : deux mesures calculées
            sur des référentiels différents ne se comparent pas, et une taille déduite des
            données observées le masquerait.
        discount: remise appliquée au fil servi, voir :func:`rank_weights`.

    Returns:
        La divergence, dans :math:`[0, 1]`.
    """
    served_distribution = rank_aware_distribution(served, category_count, discount=discount)

    reference = np.asarray(reference, dtype=float)
    if reference.size != category_count:
        raise ValueError("la distribution de référence ne couvre pas le référentiel")
    if reference.sum() <= 0.0:
        raise ValueError("une référence de masse nulle ne définit pas de distribution")

    return jensen_shannon(served_distribution, reference / reference.sum())


def _unordered_distribution(items: np.ndarray, category_count: int) -> np.ndarray:
    """Distribution d'un ensemble sans ordre de présentation — offre, historique de lecture.

    Une remise de rang n'y aurait pas de sens : ce qu'un lecteur a déjà lu n'est pas classé
    par la plateforme, et l'offre disponible ne l'est pas davantage.
    """
    return rank_aware_distribution(items, category_count, discount="none")


def calibration(
    served: np.ndarray,
    history: np.ndarray,
    category_count: int,
    discount: str = "mrr",
) -> float:
    """Écart entre le fil servi et l'**historique de lecture** du lecteur.

    Une valeur nulle signifie un fil parfaitement conforme à ce que le lecteur consultait
    déjà. **C'est l'objectif d'un recommandeur libéral et la définition d'une bulle pour un
    recommandeur délibératif** : la mesure ne dit pas lequel a raison, elle oblige à choisir.

    Args:
        served: le fil servi, dans l'ordre.
        history: catégories des articles lus par le lecteur, sans ordre.
    """
    return radio_divergence(
        served, _unordered_distribution(history, category_count), category_count, discount
    )


def fragmentation(
    served: np.ndarray,
    other_reader: np.ndarray,
    category_count: int,
    discount: str = "mrr",
) -> float:
    """Écart entre les fils servis à **deux lecteurs différents**.

    Seule des cinq mesures à ne pas comparer un fil à une référence globale : elle demande si
    deux lecteurs partagent encore un espace commun. Une valeur élevée décrit une population
    dont les membres ne lisent plus les mêmes choses — ce que le reste du dépôt appelle un
    régime figé.

    Args:
        served: le fil du premier lecteur, dans l'ordre.
        other_reader: le fil du second, dans l'ordre lui aussi — c'est la seule des cinq
            références qui soit un classement, donc la seule à être elle-même escomptée.
    """
    other = rank_aware_distribution(other_reader, category_count, discount=discount)

    return radio_divergence(served, other, category_count, discount)


def activation(
    served: np.ndarray,
    supply: np.ndarray,
    category_count: int,
    discount: str = "mrr",
) -> float:
    """Écart d'**intensité affective** entre le fil servi et l'offre disponible.

    C'est la mesure qui toucherait au plus près la charge émotionnelle :math:`\\alpha` du
    modèle — et c'est aussi celle que ce dépôt ne peut pas instancier, faute de scores
    d'affect. Elle est implémentée pour être appliquée, non pour être appliquée ici.
    """
    return radio_divergence(served, supply, category_count, discount=discount)


def representation(
    served: np.ndarray,
    supply: np.ndarray,
    category_count: int,
    discount: str = "mrr",
) -> float:
    """Écart des **points de vue** entre le fil servi et l'offre disponible.

    C'est la mesure la plus proche de l'IDE d'origine, à trois différences près : elle est
    consciente du rang, elle se rapporte à une référence déclarée plutôt qu'à l'uniforme
    supposé, et elle porte sur une divergence plutôt que sur une valeur ponctuelle.
    """
    return radio_divergence(served, supply, category_count, discount=discount)


def alternative_voices(
    served: np.ndarray,
    supply: np.ndarray,
    category_count: int,
    discount: str = "mrr",
) -> float:
    """Écart de présence des **voix minoritaires** entre le fil servi et l'offre.

    Demande un codage des minorités que ce dépôt n'a pas, et que le
    [corpus étendu](catalogue.py) a montré coûteux à obtenir : une étiquette disponible n'est
    pas l'attribut qu'on voudrait mesurer.

    Args:
        served: le fil servi, dans l'ordre.
        supply: catégories des articles disponibles, sans ordre.
    """
    return radio_divergence(
        served, _unordered_distribution(supply, category_count), category_count, discount
    )
