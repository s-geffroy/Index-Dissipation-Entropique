"""Estimateurs contrefactuels, pour évaluer hors ligne un filtre qu'on n'a pas déployé.

Le piège que ce module existe pour éviter
-----------------------------------------

L'étape suivante annoncée par la [feuille de route §3.1](../../docs/feuille-de-route.md) est
d'évaluer l'[ADE](ade.py) sur un jeu de données public de recommandation : réordonner des fils
enregistrés, mesurer le gain de diversité et la perte de pertinence, tracer la frontière de
compromis.

Prise au pied de la lettre, cette mesure est **fausse**, et d'une façon qui n'apparaît pas à
la lecture des résultats. Les clics enregistrés n'ont pas été produits par le filtre qu'on
évalue : ils l'ont été par celui de la plateforme. Or un clic dépend de deux choses, la
pertinence du contenu **et** l'exposition qu'on lui a donnée. Un article que la plateforme
avait enterré a peu de clics — non parce qu'il n'intéressait personne, mais parce que personne
ne l'a vu.

Un filtre de diversité fait précisément remonter ces articles-là. Évalué naïvement sur des
clics enregistrés, il est donc jugé sur des articles dont la pertinence a été mesurée à
travers l'exposition que la plateforme leur refusait.

Le biais qui en résulte est **grand**, et son sens n'est **pas garanti**. Sur soixante jeux de
contenus tirés à configuration identique, l'estimation naïve du coût d'un filtre de diversité
s'écarte de la valeur vraie de **201 % en médiane**, et jusqu'à 851 %. Elle surestime le coût
dans cinquante-six cas sur soixante — ce qui inviterait à la tenir pour prudente — mais elle le
sous-estime dans les quatre autres, à configuration pourtant identique.

On ne peut donc pas plaider la prudence : un chiffre naïf n'est pas une borne supérieure, c'est
un chiffre faux d'un montant considérable et d'un sens que rien ne garantit.

Ce que corrigent les estimateurs
--------------------------------

La correction est classique et tient en une idée : chaque observation est repondérée par
l'inverse de la probabilité qu'elle avait d'être observée.

.. math:: \\hat{V}_{\\text{IPS}} = \\frac{1}{n}\\sum_j \\frac{\\pi_1(a_j \\mid x_j)}
          {\\pi_0(a_j \\mid x_j)}\\, r_j

C'est **sans biais** dès lors que la politique d'enregistrement :math:`\\pi_0` est connue et
donne une chance à toute action que :math:`\\pi_1` pourrait choisir. Le prix est la variance :
un rapport de propensions peut être énorme, et une poignée d'observations rares peut alors
porter toute l'estimation. D'où les variantes de ce module :

* :func:`snips`, auto-normalisé — biaisé mais de variance nettement moindre, et sans
  paramètre à régler ;
* :func:`clipped_ips`, qui plafonne les poids — échange explicitement du biais contre de la
  variance ;
* :func:`doubly_robust`, qui combine un modèle de récompense et la repondération, et reste
  sans biais si **l'un des deux** est correct ;
* :func:`effective_sample_size`, qui dit combien d'observations portent réellement une
  estimation. C'est le diagnostic à publier à côté du chiffre : une estimation sans biais
  reposant sur douze observations effectives n'est pas une mesure.

La condition qui n'est pas gratuite
-----------------------------------

Tout repose sur la connaissance de :math:`\\pi_0`. Sur un jeu de données public, elle n'est
pas fournie : la plateforme n'a pas publié ses probabilités de service. Il faut donc la
**modéliser** — typiquement par un modèle de biais de position, où l'exposition d'un article
ne dépend que de son rang — et cette modélisation est une hypothèse, pas une mesure. Un
résultat obtenu ainsi doit être publié avec elle, et non sans.
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "clipped_ips",
    "doubly_robust",
    "effective_sample_size",
    "importance_weights",
    "ips",
    "naive",
    "naive_replay",
    "position_bias",
    "rank_propensities",
    "simulate_logged_feedback",
    "snips",
    "value_under_policy",
]


def position_bias(ranks: np.ndarray, severity: float = 1.0) -> np.ndarray:
    """Probabilité qu'un lecteur examine un contenu, selon son rang dans le fil.

    .. math:: e(R) = R^{-\\eta}

    C'est le modèle de biais de position le plus courant, et le plus simple qui rende compte
    du fait décisif : un contenu enterré n'est pas jugé, il est ignoré.

    Args:
        ranks: rangs, comptés à partir de 1.
        severity: exposant :math:`\\eta`. À 0, l'attention est uniforme et il n'y a pas de
            biais à corriger ; plus il croît, plus le premier rang capte l'attention.

    Returns:
        Les probabilités d'examen, dans :math:`(0, 1]`.
    """
    ranks = np.asarray(ranks, dtype=float)
    if np.any(ranks < 1):
        raise ValueError("les rangs se comptent à partir de 1")
    if severity < 0.0:
        raise ValueError("la sévérité du biais de position ne peut être négative")

    return ranks**-severity


def importance_weights(
    target_propensity: np.ndarray, logged_propensity: np.ndarray
) -> np.ndarray:
    """Rapport des propensions, :math:`\\pi_1/\\pi_0`.

    Raises:
        ValueError: si une propension d'enregistrement est nulle là où la politique évaluée
            agirait. Ce n'est pas un cas limite à contourner : c'est un **défaut de
            recouvrement**, et il rend l'estimation impossible plutôt qu'imprécise. Le taire
            reviendrait à publier un chiffre pour une quantité que les données ne contiennent
            pas.
    """
    target = np.asarray(target_propensity, dtype=float)
    logged = np.asarray(logged_propensity, dtype=float)
    if target.shape != logged.shape:
        raise ValueError("les deux jeux de propensions doivent avoir la même taille")

    unsupported = (logged <= 0.0) & (target > 0.0)
    if np.any(unsupported):
        raise ValueError(
            f"défaut de recouvrement : {int(unsupported.sum())} observations que la politique "
            "évaluée servirait n'avaient aucune chance d'être enregistrées"
        )

    return np.divide(target, logged, out=np.zeros_like(target), where=logged > 0.0)


def naive(rewards: np.ndarray) -> float:
    """Estimateur naïf : la moyenne des récompenses enregistrées, sans repondération.

    Il ne divise par rien, et c'est tout le problème : il estime la valeur de la politique
    **d'enregistrement**, celle qui a produit les clics, et non celle qu'on évalue. C'est
    l'estimateur qu'on écrit sans y penser en réordonnant des fils enregistrés.

    Implémenté ici pour être comparé, non pour être employé.
    """
    return float(np.mean(np.asarray(rewards, dtype=float)))


def ips(
    rewards: np.ndarray,
    target_propensity: np.ndarray,
    logged_propensity: np.ndarray,
) -> float:
    """Estimateur par l'inverse de la propension — sans biais, de variance élevée.

    Args:
        rewards: récompense observée pour chaque observation enregistrée.
        target_propensity: probabilité que la politique **évaluée** eût pris l'action
            enregistrée.
        logged_propensity: probabilité que la politique **d'enregistrement** l'ait prise.

    Returns:
        La valeur estimée de la politique évaluée.
    """
    weights = importance_weights(target_propensity, logged_propensity)

    return float(np.mean(weights * np.asarray(rewards, dtype=float)))


def snips(
    rewards: np.ndarray,
    target_propensity: np.ndarray,
    logged_propensity: np.ndarray,
) -> float:
    """Estimateur auto-normalisé — biaisé, mais de variance bien moindre.

    .. math:: \\hat{V}_{\\text{SNIPS}} = \\frac{\\sum_j w_j r_j}{\\sum_j w_j}

    La normalisation par la somme des poids retire l'essentiel de la variance due aux poids
    extrêmes, au prix d'un biais qui s'annule quand le nombre d'observations croît. Elle
    n'introduit **aucun paramètre à régler**, ce qui la rend préférable au plafonnement quand
    on n'a pas de raison de choisir un plafond.
    """
    weights = importance_weights(target_propensity, logged_propensity)
    total = weights.sum()
    if total <= 0.0:
        raise ValueError("aucune observation ne porte de poids : estimation impossible")

    return float((weights * np.asarray(rewards, dtype=float)).sum() / total)


def clipped_ips(
    rewards: np.ndarray,
    target_propensity: np.ndarray,
    logged_propensity: np.ndarray,
    cap: float,
) -> float:
    """Estimateur à poids plafonnés — un échange déclaré de biais contre de la variance.

    Args:
        cap: plafond des poids d'importance. Il **doit** être publié avec le résultat : sans
            lui, le chiffre n'est pas reproductible, et le choix du plafond suffit à déplacer
            l'estimation.
    """
    if cap <= 0.0:
        raise ValueError("le plafond doit être strictement positif")
    weights = np.minimum(importance_weights(target_propensity, logged_propensity), cap)

    return float(np.mean(weights * np.asarray(rewards, dtype=float)))


def doubly_robust(
    rewards: np.ndarray,
    target_propensity: np.ndarray,
    logged_propensity: np.ndarray,
    predicted_logged: np.ndarray,
    predicted_target: np.ndarray,
) -> float:
    """Estimateur doublement robuste — sans biais si le modèle **ou** les propensions le sont.

    .. math:: \\hat{V}_{\\text{DR}} = \\frac{1}{n}\\sum_j \\Big[\\hat{v}_j
              + w_j\\,\\big(r_j - \\hat{r}_j\\big)\\Big]

    Le modèle de récompense fournit une estimation directe, et la repondération ne corrige
    plus que son erreur — ce qui réduit la variance sans ajouter de biais. Sa robustesse est
    « double » en un sens précis et limité : il suffit que **l'un des deux** composants soit
    correct, pas que les deux le soient.

    Args:
        predicted_logged: récompense prédite pour l'action **enregistrée**.
        predicted_target: récompense prédite sous la politique **évaluée**, en espérance sur
            ses actions.
    """
    weights = importance_weights(target_propensity, logged_propensity)
    residual = np.asarray(rewards, dtype=float) - np.asarray(predicted_logged, dtype=float)

    return float(np.mean(np.asarray(predicted_target, dtype=float) + weights * residual))


def effective_sample_size(
    target_propensity: np.ndarray, logged_propensity: np.ndarray
) -> float:
    """Nombre d'observations qui portent réellement l'estimation.

    .. math:: n_{\\text{eff}} = \\frac{\\left(\\sum_j w_j\\right)^2}{\\sum_j w_j^2}

    Diagnostic à publier avec toute estimation contrefactuelle. Il vaut :math:`n` quand les
    deux politiques coïncident, et s'effondre à mesure qu'elles s'éloignent : une estimation
    sans biais adossée à douze observations effectives sur cinquante mille n'est pas une
    mesure, c'est un chiffre.
    """
    weights = importance_weights(target_propensity, logged_propensity)
    squared = float((weights**2).sum())
    if squared <= 0.0:
        return 0.0

    return float(weights.sum() ** 2 / squared)


def simulate_logged_feedback(
    relevance: np.ndarray,
    logging_policy: np.ndarray,
    impressions: int,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Tire des impressions enregistrées sous une politique connue.

    Le modèle est celui du biais de position, lu comme ce qu'il est : **une politique
    aléatoire**. Le lecteur examine un contenu et un seul, tiré selon la répartition de
    l'attention que le classement lui impose ; il clique ensuite selon la pertinence de ce
    contenu. Ce cadrage n'est pas un artifice de commodité — il met le problème sous la forme
    exacte où les estimateurs contrefactuels sont définis, propensions comprises.

    Args:
        relevance: pertinence intrinsèque de chaque contenu, dans :math:`[0, 1]`.
        logging_policy: probabilité que chaque contenu reçoive l'attention, sous le
            classement de la plateforme. Doit sommer à 1.
        impressions: nombre d'impressions à tirer.
        rng: générateur, pour que la simulation soit reproductible.

    Returns:
        Le contenu examiné et le clic observé, pour chaque impression.
    """
    generator = np.random.default_rng() if rng is None else rng
    relevance = np.asarray(relevance, dtype=float)
    policy = np.asarray(logging_policy, dtype=float)

    if np.any((relevance < 0.0) | (relevance > 1.0)):
        raise ValueError("une pertinence est une probabilité")
    if not np.isclose(policy.sum(), 1.0):
        raise ValueError("une politique d'enregistrement somme à 1")

    examined = generator.choice(relevance.size, size=impressions, p=policy)
    clicked = (generator.random(impressions) < relevance[examined]).astype(float)

    return examined, clicked


def rank_propensities(
    ranks: np.ndarray, severity: float = 1.0, normalise: bool = True
) -> np.ndarray:
    """Propensions d'exposition induites par un classement.

    C'est le pont entre un problème de classement et le formalisme de ce module : la
    « propension » d'un contenu y est la probabilité qu'il soit examiné, laquelle ne dépend
    que du rang qu'on lui a donné.

    Args:
        normalise: si vrai, les propensions somment à 1 et se lisent comme une répartition
            de l'attention. La normalisation ne change aucun rapport de propensions, donc
            aucun estimateur — elle rend seulement les valeurs comparables d'un fil à l'autre.
    """
    exposure = position_bias(ranks, severity=severity)

    return exposure / exposure.sum() if normalise else exposure


def value_under_policy(relevance: np.ndarray, policy: np.ndarray) -> float:
    """Valeur vraie d'une politique — accessible en simulation, jamais sur données réelles.

    Elle sert de référence pour vérifier qu'un estimateur est sans biais. Sur des données
    enregistrées, c'est exactement la quantité que l'on cherche et que l'on n'a pas.
    """
    return float(np.asarray(policy, dtype=float) @ np.asarray(relevance, dtype=float))

def naive_replay(
    click_rates: np.ndarray, target_propensity: np.ndarray
) -> float:
    """Estimateur de *replay* : les taux de clic enregistrés pris pour des étiquettes.

    C'est celui qu'on emploie réellement pour évaluer un réordonnancement hors ligne — on
    réordonne les candidats, puis on somme les clics observés pondérés par l'exposition que
    le nouveau classement leur donnerait :

    .. math:: \\hat{V}_{\\text{replay}} = \\sum_i \\pi_1(i)\\,\\hat{c}_i

    Son biais est structurel. Le taux de clic observé vaut :math:`\\pi_0(i)\\,g(i)` : il porte
    déjà l'exposition que la plateforme avait accordée. L'estimateur **applique donc
    l'exposition deux fois**, et pénalise exactement les contenus que la plateforme avait
    enterrés — c'est-à-dire ceux qu'un filtre de diversité fait remonter.

    Args:
        click_rates: taux de clic observé pour chaque contenu.
        target_propensity: exposition que la politique évaluée accorderait à chaque contenu.

    Returns:
        La valeur estimée, biaisée.
    """
    return float(np.asarray(target_propensity, dtype=float)
                 @ np.asarray(click_rates, dtype=float))
