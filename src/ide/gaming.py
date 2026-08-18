"""Test adverse de l'index : un plancher d'IDE est-il saturable sans coût ?

La question, et pourquoi elle précède toute norme
------------------------------------------------

L'[audit critique](../../docs/limites.md) relève une objection que le reste du dépôt n'avait
pas traitée : une plateforme contrainte de maintenir un IDE élevé peut servir des contenus
**formellement divergents mais substantiellement vides** — un article étiqueté « point de vue
opposé » dont le propos reste adjacent à celui du lecteur. Si l'index se sature ainsi sans
coût, il est inutilisable comme norme, et **il vaut mieux le savoir avant d'en proposer une.**

C'est un problème d'optimisation sous contrainte, donc entièrement simulable : aucune donnée
réelle n'est nécessaire pour trancher ce point.

Le modèle
---------

Un catalogue de :math:`k` points de vue, de positions canoniques :math:`c_\\ell` réparties sur
un axe d'opinion. Un lecteur en :math:`u`. L'engagement produit par un contenu situé en
:math:`x` décroît avec sa distance au lecteur,

.. math:: g(x) = \\exp\\left(-\\frac{(x-u)^2}{2w^2}\\right)

ce qui est l'hypothèse de bulle : la plateforme est payée pour conforter.

Le **découplage** :math:`\\varphi \\in [0,1]` mesure la latitude de la plateforme à dissocier
l'étiquette du contenu. Le meilleur article portant l'étiquette :math:`\\ell` se trouve en

.. math:: x^*_\\ell = c_\\ell + \\varphi\\,(u - c_\\ell)

À :math:`\\varphi = 0` l'étiquette prédit le contenu ; à :math:`\\varphi = 1` toute étiquette
est disponible en version vide, arbitrairement proche du lecteur.

Le plancher d'entropie est une température
------------------------------------------

La plateforme choisit une distribution d'étiquettes :math:`q` maximisant
:math:`\\sum_\\ell q_\\ell\\,g(x^*_\\ell)` sous :math:`\\mathrm{IDE}(q) \\geq \\tau`. Le
maximum d'une forme linéaire à entropie fixée est une distribution de Boltzmann,

.. math:: q_\\ell \\propto \\exp\\!\\big(g(x^*_\\ell)/T\\big)

où :math:`T` est le multiplicateur qui sature le plancher. **La contrainte réglementaire agit
exactement comme la température sociale du reste du dépôt** : à :math:`T \\to 0` la plateforme
sert son seul meilleur contenu, à :math:`T \\to \\infty` elle sert l'uniforme. Le lien n'est pas
une analogie mais la même algèbre, et il rend la solution exacte plutôt qu'approchée.

Ce que l'entropie de Rao change
-------------------------------

L'entropie quadratique de Rao pondère la diversité par la **distance sémantique** effective
entre les contenus servis :

.. math:: Q = \\sum_{\\ell m} q_\\ell q_m \\, |x^*_\\ell - x^*_m|

Elle ne compte pas les étiquettes, elle compte les écarts. Un remplissage par étiquettes n'y
produit aucun gain, puisque les contenus servis restent groupés autour du lecteur.

La signature de manipulation
----------------------------

Les deux indices se mesurent sur le même fil. Leur **écart** ne s'explique que d'une façon :
des étiquettes dispersées sur des contenus groupés. C'est ce que ce module propose comme
grandeur de contrôle, et c'est le seul livrable ici qui soit directement prescriptible.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from scipy import optimize

from ide.entropy import shannon_entropy

__all__ = [
    "Feed",
    "canonical_positions",
    "centre_share",
    "engagement",
    "excess_signature",
    "gaussian_ild",
    "ide_of_feed",
    "largest_gap",
    "max_achievable_rao",
    "optimal_feed_under",
    "optimal_feed_under_ide",
    "optimal_feed_under_rao",
    "position_entropy",
    "rao_entropy",
    "served_positions",
    "target_divergence",
]

@dataclass(frozen=True)
class Feed:
    """Un fil servi : une distribution d'étiquettes et les contenus qu'elles portent.

    Attributes:
        weights: fréquence de chaque étiquette dans le fil, de somme 1.
        positions: position du contenu effectivement servi sous chaque étiquette.
        user: position du lecteur.
        width: largeur de la fonction d'engagement.
        catalogue: positions canoniques du catalogue **de référence**, fixé par le
            régulateur. Il sert à la fois d'unité d'échelle et de grille de bacs. Mesurer
            contre l'étalement effectivement servi ferait marquer 1 à un fil réduit à un
            point : la diversité se juge contre une échelle imposée, non contre celle que la
            plateforme veut bien produire.
    """

    weights: np.ndarray
    positions: np.ndarray
    user: float
    width: float
    catalogue: np.ndarray

    @property
    def reference(self) -> float:
        """Écart maximal du catalogue de référence, unité de l'entropie de Rao."""
        return float(np.ptp(self.catalogue))

    @property
    def engagement(self) -> float:
        """Engagement moyen produit par le fil."""
        return float(self.weights @ engagement(self.positions, self.user, self.width))

    @property
    def ide(self) -> float:
        """Index de dissipation entropique, calculé sur les **étiquettes**."""
        return ide_of_feed(self.weights)

    @property
    def rao(self) -> float:
        """Entropie quadratique de Rao, calculée sur les **contenus**, normalisée."""
        return rao_entropy(self.weights, self.positions, self.reference)

    @property
    def reachable_rao(self) -> float:
        """Entropie de Rao maximale que ce catalogue servi permet d'atteindre."""
        return max_achievable_rao(self.positions, self.reference)

    @property
    def position_entropy(self) -> float:
        """Entropie de Shannon des **contenus** servis, sur les bacs du catalogue."""
        return position_entropy(self.weights, self.positions, self.catalogue)

    @property
    def centre_share(self) -> float:
        """Part du fil servie ailleurs qu'aux deux extrémités du catalogue.

        C'est le diagnostic qui a révélé le défaut de l'entropie de Rao : un fil peut
        satisfaire un plancher élevé en ne servant que les deux bords, et cette part tombe
        alors à zéro.
        """
        return centre_share(self.weights, self.positions, self.catalogue)

    @property
    def largest_gap(self) -> float:
        """Plus grand vide entre deux bacs consécutifs occupés, en fraction du catalogue."""
        return largest_gap(self.weights, self.positions, self.catalogue)

    @property
    def signature(self) -> float:
        """Écart entre diversité affichée et diversité réelle."""
        return self.ide - self.rao


def canonical_positions(viewpoint_count: int, span: float = 1.0) -> np.ndarray:
    """Positions canoniques des :math:`k` points de vue du catalogue réglementaire."""
    if viewpoint_count < 2:
        raise ValueError("il faut au moins deux points de vue pour parler de diversité")
    return np.linspace(-span, span, viewpoint_count)


def engagement(positions: np.ndarray, user: float, width: float) -> np.ndarray:
    """Engagement produit par des contenus, décroissant avec la distance au lecteur.

    Args:
        positions: positions des contenus.
        user: position du lecteur.
        width: largeur caractéristique. Une largeur grande devant l'étendue du catalogue
            rend le lecteur indifférent, et la contrainte de diversité gratuite pour une
            raison qui n'a rien à voir avec la manipulation.

    Returns:
        Engagement dans :math:`(0, 1]`, valant 1 pour un contenu exactement au point du
        lecteur.
    """
    if width <= 0.0:
        raise ValueError("la largeur d'engagement doit être strictement positive")
    return np.exp(-((np.asarray(positions, dtype=float) - user) ** 2) / (2.0 * width**2))


def served_positions(
    canonical: np.ndarray, user: float, decoupling: float = 0.0
) -> np.ndarray:
    """Position du meilleur contenu disponible sous chaque étiquette.

    C'est ici, et nulle part ailleurs, que se joue la manipulation : le découplage mesure la
    latitude de la plateforme à faire porter une étiquette éloignée par un contenu proche.

    Args:
        canonical: positions canoniques des points de vue.
        user: position du lecteur.
        decoupling: :math:`\\varphi \\in [0, 1]`. À 0, l'étiquette prédit le contenu ; à 1,
            toute étiquette est disponible en version vide.

    Returns:
        Les positions servies.
    """
    if not 0.0 <= decoupling <= 1.0:
        raise ValueError("le découplage doit appartenir à [0, 1]")
    canonical = np.asarray(canonical, dtype=float)
    return canonical + decoupling * (user - canonical)


def ide_of_feed(weights: np.ndarray) -> float:
    """Index de dissipation entropique d'un fil : entropie de Shannon normalisée.

    L'index ne voit que les **étiquettes**. C'est précisément l'hypothèse que ce module met
    à l'épreuve.
    """
    weights = np.asarray(weights, dtype=float)
    return float(shannon_entropy(weights) / np.log2(weights.size))


def rao_entropy(weights: np.ndarray, positions: np.ndarray, reference: float) -> float:
    """Entropie quadratique de Rao, normalisée par l'étendue du catalogue de référence.

    .. math:: Q = \\frac{2}{D}\\sum_{\\ell m} q_\\ell q_m \\, d_{\\ell m}

    La normalisation est le point délicat. Rapporter :math:`Q` à l'étalement **effectivement
    servi** rendrait la mesure invariante d'échelle, et un fil réduit à un point y marquerait
    1 : c'est exactement la manipulation qu'il s'agit de détecter. L'unité est donc l'écart
    maximal :math:`D` du catalogue de référence, fixé par le régulateur.

    Args:
        weights: fréquences des étiquettes.
        positions: positions des contenus servis.
        reference: écart maximal du catalogue de référence.

    Returns:
        Une diversité dans :math:`[0, 1]`, valant 1 pour une masse répartie à parts égales aux
        deux extrémités du catalogue de référence. Elle vaut **0** si tous les contenus servis
        coïncident, quelle que soit la diversité des étiquettes qui les portent.
    """
    if reference <= 0.0:
        raise ValueError("l'étendue de référence doit être strictement positive")

    weights = np.asarray(weights, dtype=float)
    positions = np.asarray(positions, dtype=float)
    distances = np.abs(positions[:, None] - positions[None, :])

    return float(weights @ distances @ weights) / (reference / 2.0)


def max_achievable_rao(positions: np.ndarray, reference: float) -> float:
    """Entropie de Rao maximale atteignable en distribuant librement les étiquettes.

    Le maximum d'une forme quadratique à diagonale nulle sur le simplexe est atteint en
    plaçant la moitié de la masse sur chacun des deux contenus les plus éloignés. Cette
    grandeur dit si un plancher de Rao est **atteignable du tout** : une plateforme qui a
    vidé ses étiquettes de leur contenu ne peut plus s'y conformer, quelle que soit la
    distribution qu'elle choisit.
    """
    if reference <= 0.0:
        raise ValueError("l'étendue de référence doit être strictement positive")
    positions = np.asarray(positions, dtype=float)
    return float(np.abs(positions[:, None] - positions[None, :]).max()) / reference


# ————————————————————————————————————————————————————————————————————————————————
# Diagnostics de forme, et les mesures candidates au remplacement de l'entropie de Rao
# ————————————————————————————————————————————————————————————————————————————————


def _binned(weights: np.ndarray, positions: np.ndarray, catalogue: np.ndarray) -> np.ndarray:
    """Répartit les contenus servis sur les bacs du catalogue de référence.

    Chaque contenu est affecté au point de vue canonique le plus proche. C'est ce passage
    par les **contenus** — et non par les étiquettes déclarées — qui rend les mesures
    suivantes insensibles au bourrage d'étiquettes.
    """
    weights = np.asarray(weights, dtype=float)
    positions = np.asarray(positions, dtype=float)
    catalogue = np.asarray(catalogue, dtype=float)

    nearest = np.argmin(np.abs(positions[:, None] - catalogue[None, :]), axis=1)
    binned = np.zeros(catalogue.size)
    np.add.at(binned, nearest, weights)
    return binned


def position_entropy(
    weights: np.ndarray, positions: np.ndarray, catalogue: np.ndarray
) -> float:
    """Entropie de Shannon des **contenus** servis, normalisée.

    C'est l'IDE, à une substitution près : la distribution mesurée n'est plus celle des
    étiquettes déclarées mais celle des positions effectivement servies, projetées sur les
    bacs du catalogue de référence.

    La substitution est mineure en apparence et décisive en pratique. Elle conserve
    l'interprétation de l'index d'origine — une entropie normalisée dans :math:`[0,1]`, nulle
    pour un fil gelé — tout en refusant les deux échappatoires : un fil dont toutes les
    étiquettes portent le même contenu tombe dans un seul bac, et un fil réduit aux deux
    bords n'en occupe que deux.
    """
    return float(shannon_entropy(_binned(weights, positions, catalogue)) / np.log2(len(catalogue)))


def gaussian_ild(
    weights: np.ndarray,
    positions: np.ndarray,
    bandwidth: float,
) -> float:
    """Diversité de type *Gaussian ILD*, d'après Ohsaka et Togashi (SIGIR 2023).

    .. math::

        G = 1 - \\sum_{\\ell m} q_\\ell q_m
            \\exp\\!\\left(-\\frac{d_{\\ell m}^2}{2h^2}\\right)

    L'entropie de Rao — qui est la distance intra-liste moyenne — récompense un écart quel
    qu'en soit le prix, et se maximise donc en empilant la masse aux deux bords. Le noyau
    gaussien sature : au-delà de quelques largeurs de bande, éloigner davantage ne rapporte
    plus rien, et la seule façon de gagner encore est d'**occuper des endroits différents**.

    Args:
        weights: fréquences des étiquettes.
        positions: positions des contenus servis.
        bandwidth: largeur de bande :math:`h`. Grande devant le catalogue, la mesure tend
            vers l'entropie de Rao et en retrouve le défaut ; petite, elle tend vers un
            simple comptage de contenus distincts. L'écart entre points de vue voisins du
            catalogue est le choix naturel, et c'est l'analogue continu de la largeur de bac.

    Returns:
        Une diversité dans :math:`[0, 1)`, nulle si tous les contenus servis coïncident.
    """
    if bandwidth <= 0.0:
        raise ValueError("la largeur de bande doit être strictement positive")

    weights = np.asarray(weights, dtype=float)
    positions = np.asarray(positions, dtype=float)
    distances = positions[:, None] - positions[None, :]
    similarity = np.exp(-(distances**2) / (2.0 * bandwidth**2))

    return 1.0 - float(weights @ similarity @ weights)


def target_divergence(
    weights: np.ndarray,
    positions: np.ndarray,
    catalogue: np.ndarray,
    target: np.ndarray | None = None,
) -> float:
    """Proximité à une distribution d'exposition **déclarée** par le régulateur.

    .. math:: D = 1 - \\mathrm{JS}(p_{\\text{servi}} \\,\\|\\, p_{\\text{cible}})

    Les trois autres mesures partagent un défaut de principe : elles supposent qu'une forme
    d'exposition est bonne sans jamais le dire. L'entropie suppose que l'uniforme est
    l'idéal ; l'entropie de Rao suppose que l'écartement l'est — et c'est ce non-dit qui la
    conduit à prescrire la bimodalité.

    Une divergence rend l'hypothèse explicite : le régulateur **déclare** la distribution
    d'exposition visée, et la mesure dit à quelle distance on s'en trouve. Le choix de la
    cible redevient alors ce qu'il est, un choix politique, au lieu d'être enfoui dans le
    choix d'une formule.

    Args:
        target: distribution visée sur les bacs du catalogue. À défaut, l'uniforme — qui
            n'est pas neutre non plus, seulement explicite.

    Returns:
        Une valeur dans :math:`[0, 1]`, valant 1 quand l'exposition servie coïncide avec la
        cible. La divergence de Jensen-Shannon en base 2 est bornée par 1, ce qui rend la
        normalisation exacte plutôt que conventionnelle.
    """
    served = _binned(weights, positions, catalogue)
    if target is None:
        target = np.full(len(catalogue), 1.0 / len(catalogue))
    target = np.asarray(target, dtype=float)
    target = target / target.sum()

    mixture = 0.5 * (served + target)
    divergence = shannon_entropy(mixture) - 0.5 * (
        shannon_entropy(served) + shannon_entropy(target)
    )

    return 1.0 - float(np.clip(divergence, 0.0, 1.0))


def centre_share(
    weights: np.ndarray, weights_positions: np.ndarray, catalogue: np.ndarray
) -> float:
    """Part du fil servie ailleurs qu'aux deux extrémités du catalogue.

    Diagnostic, non contrainte : c'est lui qui a rendu visible le défaut de l'entropie de
    Rao. Un fil qui satisfait un plancher de Rao élevé en ne servant que les deux bords y
    tombe à zéro, alors qu'aucune des grandeurs contraintes ne s'en émeut.
    """
    binned = _binned(weights, weights_positions, catalogue)
    return float(binned[1:-1].sum())


def largest_gap(
    weights: np.ndarray, positions: np.ndarray, catalogue: np.ndarray, floor: float = 0.01
) -> float:
    """Plus grand vide entre deux bacs occupés, en fraction de l'étendue du catalogue.

    Args:
        floor: masse en deçà de laquelle un bac est tenu pour vide. Sans ce seuil, servir
            une miette dans chaque bac suffirait à effacer le diagnostic.
    """
    binned = _binned(weights, positions, catalogue)
    occupied = np.asarray(catalogue, dtype=float)[binned > floor]
    if occupied.size < 2:
        return 1.0
    return float(np.max(np.diff(np.sort(occupied))) / np.ptp(catalogue))


def _boltzmann(payoff: np.ndarray, temperature: float) -> np.ndarray:
    """Distribution maximisant l'engagement à entropie fixée."""
    scaled = payoff / temperature
    scaled -= scaled.max()
    weights = np.exp(scaled)
    return weights / weights.sum()


def optimal_feed_under_ide(
    viewpoint_count: int,
    user: float = 0.6,
    floor: float = 0.0,
    decoupling: float = 0.0,
    width: float = 0.5,
    span: float = 1.0,
) -> Feed:
    """Fil maximisant l'engagement sous un plancher d'**IDE**.

    La solution est exacte : maximiser une forme linéaire à entropie fixée donne une
    distribution de Boltzmann, et le plancher se sature en ajustant la température. Aucune
    heuristique n'intervient, ce qui rend la conclusion du test adverse imputable au modèle et
    non au solveur.

    Args:
        viewpoint_count: nombre :math:`k` de points de vue du catalogue.
        user: position du lecteur.
        floor: plancher d'IDE imposé, dans :math:`[0, 1]`.
        decoupling: latitude de manipulation, voir :func:`served_positions`.
        width: largeur de la fonction d'engagement.
        span: étendue du catalogue de points de vue.

    Returns:
        Le fil retenu par la plateforme.
    """
    if not 0.0 <= floor <= 1.0:
        raise ValueError("le plancher doit appartenir à [0, 1]")

    canonical = canonical_positions(viewpoint_count, span=span)
    positions = served_positions(canonical, user, decoupling=decoupling)
    payoff = engagement(positions, user, width)

    def build(temperature: float) -> np.ndarray:
        return _boltzmann(payoff, temperature)

    # Sans plancher, la plateforme sert son unique meilleur contenu.
    if floor <= 0.0:
        weights = np.zeros(viewpoint_count)
        weights[int(np.argmax(payoff))] = 1.0
        return Feed(weights, positions, user, width, canonical)

    # Le découplage complet égalise les gains : toute distribution est optimale, et la
    # plateforme choisit celle qui satisfait le plancher au moindre effort — l'uniforme.
    if float(payoff.max() - payoff.min()) < 1e-12:
        uniform = np.full(viewpoint_count, 1.0 / viewpoint_count)
        return Feed(uniform, positions, user, width, canonical)

    # L'entropie de la distribution de Boltzmann croît avec la température, de 0 à log k.
    def gap(log_temperature: float) -> float:
        return ide_of_feed(build(float(np.exp(log_temperature)))) - floor

    low, high = -12.0, 12.0
    if gap(high) < 0.0:
        # Le plancher est hors d'atteinte : la plateforme sert l'uniforme, qui le maximise.
        uniform = np.full(viewpoint_count, 1.0 / viewpoint_count)
        return Feed(uniform, positions, user, width, canonical)
    if gap(low) > 0.0:
        return Feed(build(float(np.exp(low))), positions, user, width, canonical)

    root = optimize.brentq(gap, low, high, xtol=1e-10)

    return Feed(build(float(np.exp(root))), positions, user, width, canonical)



def optimal_feed_under(
    measure: Callable[[np.ndarray, np.ndarray], float],
    viewpoint_count: int,
    user: float = 0.6,
    floor: float = 0.0,
    decoupling: float = 0.0,
    width: float = 0.5,
    span: float = 1.0,
    restarts: int = 12,
    seed: int = 0,
) -> Feed:
    """Fil maximisant l'engagement sous un plancher portant sur une mesure quelconque.

    Toutes les mesures candidates passent par ce solveur, et non par un chemin propre à
    chacune : une comparaison entre normes ne vaut que si l'optimisation est la même de part
    et d'autre. Seul le plancher d'IDE dispose en outre d'une solution fermée
    (:func:`optimal_feed_under_ide`), utilisée là où elle s'applique.

    L'ensemble réalisable n'est pas convexe en général, et il n'existe pas de solution
    fermée. L'optimisation est donc numérique, à départs multiples ; le meilleur résultat est
    retenu. Le risque d'optimum local **sous-estime** l'engagement atteignable sous
    contrainte, donc surestime le coût de la norme : il joue contre la mesure évaluée, non en
    sa faveur.

    Args:
        measure: fonction ``(poids, positions) -> [0, 1]`` à contraindre.
        restarts: nombre de départs aléatoires.
        seed: graine, pour que le résultat soit reproductible.

    Returns:
        Le meilleur fil trouvé. Si aucun ne satisfait le plancher, le fil le plus divers
        possible est rapporté — sa mesure dira qu'elle reste sous le plancher.
    """
    if not 0.0 <= floor <= 1.0:
        raise ValueError("le plancher doit appartenir à [0, 1]")

    canonical = canonical_positions(viewpoint_count, span=span)
    positions = served_positions(canonical, user, decoupling=decoupling)
    payoff = engagement(positions, user, width)

    if floor <= 0.0:
        weights = np.zeros(viewpoint_count)
        weights[int(np.argmax(payoff))] = 1.0
        return Feed(weights, positions, user, width, canonical)

    constraints = (
        {"type": "eq", "fun": lambda q: q.sum() - 1.0},
        {"type": "ineq", "fun": lambda q: measure(q, positions) - floor},
    )
    bounds = [(0.0, 1.0)] * viewpoint_count

    generator = np.random.default_rng(seed)
    starts = [np.full(viewpoint_count, 1.0 / viewpoint_count)]
    starts += [generator.dirichlet(np.ones(viewpoint_count)) for _ in range(restarts - 1)]

    best_weights, best_value = None, -np.inf
    for start in starts:
        result = optimize.minimize(
            lambda q: -float(q @ payoff),
            start,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 400, "ftol": 1e-12},
        )
        if not result.success:
            continue
        weights = np.clip(result.x, 0.0, None)
        weights = weights / weights.sum()
        # Une contrainte satisfaite à la tolérance près reste une contrainte satisfaite.
        if measure(weights, positions) < floor - 1e-6:
            continue
        value = float(weights @ payoff)
        if value > best_value:
            best_weights, best_value = weights, value

    if best_weights is None:
        # Aucun fil ne satisfait le plancher. On rapporte le plus divers atteignable, dont
        # la mesure signalera qu'elle reste sous le plancher.
        best_weights = np.zeros(viewpoint_count)
        distances = np.abs(positions[:, None] - positions[None, :])
        far = np.unravel_index(int(np.argmax(distances)), distances.shape)
        best_weights[far[0]] += 0.5
        best_weights[far[1]] += 0.5

    return Feed(best_weights, positions, user, width, canonical)


def optimal_feed_under_rao(
    viewpoint_count: int,
    user: float = 0.6,
    floor: float = 0.0,
    decoupling: float = 0.0,
    width: float = 0.5,
    span: float = 1.0,
    restarts: int = 12,
    seed: int = 0,
) -> Feed:
    """Fil maximisant l'engagement sous un plancher d'**entropie de Rao**.

    Conservé pour ce qu'il démontre, et non pour ce qu'il prescrit : l'entropie de Rao
    résiste au bourrage d'étiquettes, mais son optimum sous contrainte **vide le centre** du
    catalogue. Voir :func:`optimal_feed_under` pour les mesures qui ne le font pas.
    """
    reference = float(np.ptp(canonical_positions(viewpoint_count, span=span)))

    return optimal_feed_under(
        lambda q, x: rao_entropy(q, x, reference),
        viewpoint_count,
        user=user,
        floor=floor,
        decoupling=decoupling,
        width=width,
        span=span,
        restarts=restarts,
        seed=seed,
    )


def excess_signature(
    viewpoint_count: int,
    user: float = 0.6,
    floor: float = 0.8,
    decoupling: float = 0.0,
    width: float = 0.5,
    span: float = 1.0,
) -> float:
    """Écart de signature au-delà de ce qu'un catalogue honnête produirait au même IDE.

    L'écart brut :math:`\\mathrm{IDE} - Q` n'est **pas** interprétable seul : les deux indices
    ne sont pas sur la même échelle, et un fil parfaitement honnête en affiche déjà un
    substantiel — 0,36 dans la configuration de référence. Publier un seuil sur l'écart brut
    reviendrait à inventer un chiffre, ce que ce dépôt s'est déjà fait reprocher une fois.

    La grandeur interprétable est la **différence à la contrefactuelle honnête** : ce qu'un
    catalogue dont les étiquettes prédisent le contenu afficherait à index égal. Elle vaut 0
    par construction pour une plateforme honnête et croît avec le découplage.

    Args:
        viewpoint_count: nombre de points de vue du catalogue.
        user: position du lecteur.
        floor: plancher d'IDE sous lequel la plateforme optimise.
        decoupling: latitude de manipulation à évaluer.
        width: largeur de la fonction d'engagement.
        span: étendue du catalogue.

    Returns:
        L'excès de signature, nul pour une plateforme honnête.
    """
    observed = optimal_feed_under_ide(viewpoint_count, user, floor, decoupling, width, span)
    honest = optimal_feed_under_ide(viewpoint_count, user, floor, 0.0, width, span)
    return observed.signature - honest.signature
