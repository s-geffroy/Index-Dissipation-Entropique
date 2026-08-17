"""Corpus pré-enregistré pour la calibration de la cinétique de résonance.

Pourquoi un corpus figé dans le code
------------------------------------

L'analyse compare le rapport :math:`\\gamma\\alpha/\\lambda` entre deux classes de sujets.
Une telle comparaison n'a de valeur que si la liste des sujets est arrêtée **avant** de
regarder les résultats : à défaut, il suffirait d'écarter les cas gênants pour obtenir
l'effet attendu.

Ce corpus est donc versionné, et la règle est explicite : **aucun article n'est retiré au
vu de son résultat.** Les sujets pour lesquels aucun épisode exploitable n'est détecté sont
rapportés comme tels — une absence de pic net est une donnée, pas un échec à masquer.

Les deux classes
----------------

Le modèle fait dépendre l'amplification du produit :math:`\\gamma\\alpha`, où :math:`\\alpha`
est la charge émotionnelle innée du contenu. La prédiction est qu'à gain algorithmique
comparable, un contenu à forte charge émotionnelle présente un rapport plus élevé.

Le critère de classement porte sur la **nature de l'émotion mobilisée**, non sur
l'importance du sujet :

* :data:`ACCUSATION` — l'attention est mobilisée par une **accusation, une menace ou un
  scandale** : colère, indignation, peur. C'est le registre que le modèle associe à un
  :math:`\\alpha` élevé.
* :data:`DISCOVERY` — l'attention est mobilisée par une **découverte ou une réussite** :
  curiosité, admiration. Registre à :math:`\\alpha` faible.

Le confondant qu'il faut nommer
-------------------------------

Un événement soudain produit une montée plus raide qu'un événement anticipé, quelle que
soit sa charge émotionnelle. Si la classe « découverte » ne contenait que des événements
programmés — remises de prix, lancements annoncés de longue date — la prédiction serait
vérifiée pour une raison de calendrier et non d'émotion.

La classe :data:`DISCOVERY` est donc composée d'annonces **non programmées** : première
détection d'ondes gravitationnelles, première image d'un trou noir, percée algorithmique.
Le confondant n'est pas éliminé pour autant — une annonce scientifique reste plus
prévisible qu'un scandale — et cette réserve est reportée dans les conclusions.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

__all__ = [
    "ACCUSATION",
    "CORPUS",
    "CORPUS_END",
    "CORPUS_START",
    "DISCOVERY",
    "CorpusEntry",
    "by_category",
]

#: Couverture de l'API de consultations : les données quotidiennes commencent en
#: juillet 2015.
CORPUS_START = date(2015, 7, 1)
CORPUS_END = date(2026, 8, 1)


@dataclass(frozen=True)
class CorpusEntry:
    """Un sujet du corpus.

    Attributes:
        project: projet Wikimedia interrogé.
        article: titre tel qu'il doit apparaître dans l'URL de l'API, percent-encodé.
        label: intitulé lisible, employé dans les figures et les tableaux.
        category: ``"accusation"`` ou ``"discovery"``.
    """

    project: str
    article: str
    label: str
    category: str

    def __post_init__(self) -> None:
        if self.category not in ("accusation", "discovery"):
            raise ValueError("la catégorie doit valoir 'accusation' ou 'discovery'")


#: Sujets dont l'attention est mobilisée par une accusation, une menace ou un scandale.
ACCUSATION: tuple[CorpusEntry, ...] = (
    CorpusEntry("en.wikipedia", "QAnon", "QAnon", "accusation"),
    CorpusEntry(
        "en.wikipedia", "Pizzagate_conspiracy_theory", "Pizzagate", "accusation"
    ),
    CorpusEntry("en.wikipedia", "Cambridge_Analytica", "Cambridge Analytica", "accusation"),
    CorpusEntry("en.wikipedia", "Panama_Papers", "Panama Papers", "accusation"),
    CorpusEntry("en.wikipedia", "Paradise_Papers", "Paradise Papers", "accusation"),
    CorpusEntry(
        "en.wikipedia", "Chemtrail_conspiracy_theory", "Chemtrails", "accusation"
    ),
    CorpusEntry("en.wikipedia", "Great_Replacement", "Grand remplacement", "accusation"),
    CorpusEntry(
        "en.wikipedia", "COVID-19_misinformation", "Désinformation Covid-19", "accusation"
    ),
    CorpusEntry("en.wikipedia", "Vaccine_hesitancy", "Hésitation vaccinale", "accusation"),
    CorpusEntry("en.wikipedia", "Pegasus_%28spyware%29", "Pegasus (logiciel espion)", "accusation"),
    CorpusEntry("fr.wikipedia", "Affaire_Benalla", "Affaire Benalla", "accusation"),
    CorpusEntry("fr.wikipedia", "Mouvement_des_Gilets_jaunes", "Gilets jaunes", "accusation"),
)

#: Sujets dont l'attention est mobilisée par une découverte ou une réussite non programmée.
DISCOVERY: tuple[CorpusEntry, ...] = (
    CorpusEntry("en.wikipedia", "Gravitational_wave", "Ondes gravitationnelles", "discovery"),
    CorpusEntry("en.wikipedia", "LIGO", "LIGO", "discovery"),
    CorpusEntry(
        "en.wikipedia", "Event_Horizon_Telescope", "Event Horizon Telescope", "discovery"
    ),
    CorpusEntry(
        "en.wikipedia", "James_Webb_Space_Telescope", "Télescope James-Webb", "discovery"
    ),
    CorpusEntry("en.wikipedia", "CRISPR", "CRISPR", "discovery"),
    CorpusEntry("en.wikipedia", "Higgs_boson", "Boson de Higgs", "discovery"),
    CorpusEntry("en.wikipedia", "Perseverance_%28rover%29", "Perseverance", "discovery"),
    CorpusEntry("en.wikipedia", "Fast_radio_burst", "Sursauts radio rapides", "discovery"),
    CorpusEntry("en.wikipedia", "AlphaFold", "AlphaFold", "discovery"),
    CorpusEntry("en.wikipedia", "OSIRIS-REx", "OSIRIS-REx", "discovery"),
    CorpusEntry("fr.wikipedia", "Trou_noir", "Trou noir", "discovery"),
    # Le titre canonique de l'article français est « James Webb (télescope spatial) » ;
    # « Télescope spatial James Webb » n'est qu'une redirection, dont les consultations
    # sont marginales.
    CorpusEntry(
        "fr.wikipedia",
        "James_Webb_%28t%C3%A9lescope_spatial%29",
        "Télescope James-Webb (fr)",
        "discovery",
    ),
)

#: Corpus complet, dans un ordre stable.
CORPUS: tuple[CorpusEntry, ...] = ACCUSATION + DISCOVERY


def by_category(category: str) -> tuple[CorpusEntry, ...]:
    """Sujets d'une catégorie donnée.

    Examples:
        >>> len(by_category("accusation")) > 0
        True
        >>> {entry.category for entry in by_category("discovery")}
        {'discovery'}
    """
    if category not in ("accusation", "discovery"):
        raise ValueError("la catégorie doit valoir 'accusation' ou 'discovery'")

    return tuple(entry for entry in CORPUS if entry.category == category)
