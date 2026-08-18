# L'exploration réelle de MIND : un ordre qui n'en est pas un

!!! failure "L'ordre enregistré dans MIND est indiscernable d'un mélange"
    Le test d'échangeabilité intra-fil donne $z = +0{,}12$ ($p = 0{,}91$) sur les 156 965 fils
    du découpage d'entraînement, et $z = +0{,}28$ ($p = 0{,}78$) sur les 73 152 du second. Les
    clics tombent exactement là où le hasard les mettrait — dans un jeu où le même test
    détecterait $\eta = 0{,}02$ à douze écarts-types.

!!! danger "Et la courbe qu'on trace naturellement y voit un biais de position parfait"
    Le taux de clic par position décroît de **0,108 à 0,038** sur les vingt premiers rangs, et
    l'ajustement log-log donne $\hat\eta = 0{,}39$. C'est un **artefact de composition** : la
    position 20 n'existe que dans les fils longs, où le taux de clic par contenu est
    mécaniquement plus faible. À longueur de fil fixée, la courbe est plate.

!!! failure "Correction du chantier précédent : le contrôle d'identifiabilité ne suffit pas"
    `estimate_position_bias` refuse d'estimer $\eta$ quand aucun contenu n'a changé de rang.
    Sur MIND, des milliers de contenus ont changé de rang — artificiellement. L'estimateur
    répond donc, et sa réponse est une fonction croissante d'un simple paramètre de nuisance :
    de $-0{,}13$ à $+0{,}25$ selon le seuil d'impressions, sans jamais cesser d'être
    « significative ».

---

## Ce que cette mesure devait décider

Le [rang adverse](rang-adverse.md) a établi deux choses : la sévérité $\eta$ du biais de
position **s'estime** au lieu de se poser, et la poser de travers coûte jusqu'à 179 % sur le
chiffre publié. Il a aussi établi à quelle condition cette estimation existe — que la
plateforme n'ait pas toujours classé les mêmes contenus aux mêmes places.

Cette condition est une propriété du **jeu de données**, pas de la méthode. D'où le préalable
inscrit à la [feuille de route §3.1](feuille-de-route.md) : mesurer l'exploration réelle avant
d'évaluer quoi que ce soit. [MIND](https://msnews.github.io/) (*Microsoft News Dataset*,
Wu et al., ACL 2020) est le jeu de référence de la recommandation d'actualité, celui sur lequel
l'évaluation de l'[ADE](ade.md) était prévue.

![L'exploration réelle de MIND](figures/fig16_exploration_mind.png)

/// caption
La courbe agrégée et son démenti à longueur fixée ; ce que le test aurait su détecter ; les cinq
sévérités tirées du même jeu ; et ce que coûte la variable détruite. Figure régénérée par
[le notebook 16](notebooks/16_exploration_mind.ipynb).
///

## 1. La condition d'identifiabilité est satisfaite — abondamment

| Grandeur | Valeur |
|---|---|
| fils | 156 965 |
| contenus servis | 5 843 444 |
| contenus distincts | 20 288 |
| contenus vus à plusieurs rangs (seuil 5) | 2 655 |
| rangs distincts par contenu (médiane) | **16** |
| rang maximal observé | 299 |

Un contenu médian retenu a été servi à seize positions différentes. Aucun jeu de données réel ne
saurait offrir mieux : à ce compte, l'exploration paraît **idéale**.

## 2. La courbe qu'on trace naturellement

| Rang | 1 | 2 | 3 | 5 | 10 | 15 | 20 |
|---|---|---|---|---|---|---|---|
| taux de clic | 0,108 | 0,108 | 0,081 | 0,066 | 0,050 | 0,043 | 0,038 |

Décroissance régulière sur 5,8 millions de contenus servis, ajustement $\hat\eta = 0{,}39$.
C'est le premier graphique que produit quiconque cherche un biais de position, et il a
exactement l'allure attendue.

## 3. Le confondant

Les fils de MIND n'ont pas tous la même longueur — médiane 24, moyenne 37, maximum 299. Or **la
position 20 n'existe que dans les fils d'au moins 20 contenus**, et le taux de clic *par contenu
servi* y est mécaniquement plus faible : un lecteur qui clique une fois dans un fil de 100
contenus produit un taux de 0,01, le même clic dans un fil de 4 contenus en produit 0,25.

Il suffit de tenir la longueur fixée pour séparer les deux effets.

| Longueur du fil | 6 | 10 | 15 | 20 | 30 | 50 |
|---|---|---|---|---|---|---|
| $\eta$ apparent | −0,022 | +0,025 | −0,025 | −0,033 | −0,002 | +0,037 |

La pente est nulle, et son **signe change** d'une longueur à l'autre. Les 0,39 de la courbe
agrégée ne mesuraient que le mélange des longueurs.

## 4. Le test exact, et ce qu'il aurait su détecter

Le contrôle par longueur fixée est parlant mais partiel : il jette la plupart des fils et laisse
jouer la qualité moyenne des contenus d'un fil comme l'appétit de clic de son lecteur. Le test
exact conditionne au fil.

Pour un fil de longueur $L$ portant $k$ clics, on somme les rangs normalisés
$u_R = (R - 1/2)/L$ des contenus cliqués. Sous l'hypothèse que les clics sont **indifférents à
la position**, ces $k$ positions sont un tirage sans remise parmi les $L$ positions du fil,
d'espérance et de variance connues exactement :

$$\mathbb{E} = k\,\bar{u}, \qquad \mathbb{V} = \frac{k(L-k)}{L-1}\,\sigma^2_u.$$

Un biais de position concentre les clics en haut : il rend l'écart réduit **négatif**.

| Découpage | Fils | Somme observée | Attendue | $z$ | $p$ |
|---|---|---|---|---|---|
| train | 156 965 | 118 187,9 | 118 172,0 | **+0,116** | 0,908 |
| dev | 73 152 | 55 717,7 | 55 691,5 | **+0,278** | 0,781 |

Un test qui ne rejette rien ne dit rien tant qu'on ignore ce qu'il rejetterait. L'étalonnage se
fait sur des journaux simulés de **même structure de fils** que MIND, sous un biais de position
de sévérité connue.

| $\eta$ simulé | 0,00 | 0,02 | 0,05 | 0,10 | 0,25 | 0,50 | 1,00 |
|---|---|---|---|---|---|---|---|
| $z$ | +0,9 | **−9,0** | −27,0 | −49,2 | −104,4 | −161,2 | −199,3 |

La sévérité minimale détectable vaut $\eta \approx 0{,}004$. L'ordre enregistré dans MIND ne
porte donc aucune information de placement au-delà de ce seuil.

La documentation du jeu le disait d'ailleurs, en une ligne : *« the orders of news in a
impressions have been shuffled »*. Une ligne de documentation ne dit toutefois ni ce qu'il en
reste, ni ce que la mesure donne quand on l'ignore.

## 5. Cinq estimations du même jeu, quatre de trop

| Méthode | $\hat\eta$ | Erreur type |
|---|---|---|
| ajustement naïf agrégé | +0,388 | — |
| effets fixes, seuil 5 | **−0,131** | 0,002 |
| effets fixes, seuil 10 | −0,047 | 0,002 |
| effets fixes, seuil 20 | +0,053 | 0,003 |
| effets fixes, seuil 50 | +0,194 | 0,004 |
| effets fixes, seuil 100 | +0,255 | 0,007 |
| **test d'échangeabilité** | **0,000** | ±0,004 |

Une sévérité négative voudrait dire que les positions basses reçoivent *plus* de clics. Toutes
ces estimations sont assorties d'une erreur type inférieure à 0,007, donc toutes
« significatives », et toutes incompatibles entre elles.

C'est la démonstration que le contrôle d'identifiabilité du [rang adverse](rang-adverse.md) est
**nécessaire et non suffisant** : il compte la variation de rang sans dire d'où elle vient, et
une variation artificielle le satisfait mieux que n'importe quelle exploration réelle.

## 6. Le mélange ne débiaise pas les clics

Une lecture répandue veut que mélanger l'ordre enregistré *protège* du biais de position. Elle
confond deux choses.

Les clics de MIND ont été produits par des lecteurs qui voyaient un fil **ordonné** — l'ordre
réel de Microsoft News, celui que le jeu n'a pas conservé. Ils portent donc le biais de position
en entier. Ce que le mélange a retiré, c'est le **rang**, seul régresseur qui aurait permis d'en
tenir compte.

Sur un journal simulé dont on connaît la vérité ($\eta = 1{,}00$) :

| Journal | $\hat\eta$ |
|---|---|
| ordre conservé | 1,003 ± 0,008 |
| ordre mélangé à l'intérieur de chaque fil | **−0,003 ± 0,006** |

Les clics sont **les mêmes** dans les deux lignes. Seule la variable qui permettait de les
corriger a disparu.

### Ce que cette perte coûte à l'évaluation

| Estimation du coût d'un filtre de diversité | Valeur |
|---|---|
| coût réel | 6,61 % |
| avec $\eta$ lu sur l'ordre conservé | 6,68 % |
| avec $\eta$ lu sur l'ordre mélangé | **0,00 %** |

Le zéro n'est pas une coïncidence numérique. Sous $\eta = 0$, toutes les positions sont réputées
également vues : deux politiques qui ne diffèrent que par l'ordre reçoivent alors la même valeur
estimée, quoi qu'elles fassent. L'évaluation ne se trompe pas de peu — dans ce cadre, elle est
**vide par construction**, et son résultat est que le réordonnancement ne coûte rien.

## 7. Ce que cette mesure décide

**MIND ne peut pas calibrer $\eta$.** Ce n'est pas un défaut de la méthode ni un manque de
données — 5,8 millions de contenus servis — mais l'absence de la seule variable qui identifierait
la sévérité. Aucun raffinement de l'estimateur n'y changera rien.

*Pour ce dépôt.* L'évaluation de l'ADE sur MIND reste possible pour ce qui ne dépend pas de
l'exposition : composition des fils, diversité servie, coût en pertinence déclarée. Elle est
**impossible** pour ce qui en dépend — l'estimation contrefactuelle du coût d'engagement, qui
était l'objet même de l'exercice. Il faut soit un jeu qui enregistre le rang d'affichage, soit
assumer un $\eta$ importé, dont le [rang adverse](rang-adverse.md) a chiffré le prix.

*Pour quiconque évalue un réordonnancement sur données publiques.* Le contrôle à faire n'est pas
« ai-je assez de variation de rang ? » mais « cette variation vient-elle de la plateforme ou de
l'anonymisation ? ». Les deux se ressemblent parfaitement du point de vue de l'estimateur, et
seule la seconde produit des chiffres confiants et faux.

*Pour ceux qui publient des journaux — et pour le régulateur qui en exige.* Mélanger l'ordre
d'affichage ne rend pas un jeu de données non biaisé : il le rend **non corrigible**. Publier le
rang servi, ou à défaut la propension d'exposition, coûte une colonne et décide de ce qui reste
mesurable. → [mémorandum](memorandum.md)

## Provenance des données

Le lien officiel de MIND-small
(`mind201910small.blob.core.windows.net`) répond aujourd'hui *409 Public access is not permitted
on this storage account* : le jeu n'est plus téléchargeable à sa source. Les journaux employés
ici viennent d'un miroir, et un miroir se vérifie : nombre de fils conforme aux statistiques
publiées avec MIND-small (156 965 et 73 152), empreintes SHA-256 inscrites dans `ide.mind`.

Le jeu brut n'est pas versionné — licence de recherche Microsoft, 135 Mo. Le dépôt porte un
**condensé** de 1,5 Mo, `data/mind_digest.npz`, qui retient la structure d'ordre des fils et les
cellules (contenu, rang) suffisamment observées. Il rend **à l'identique** tous les chiffres de
cette page, ce qu'un test vérifie, et se reconstruit par `scripts/fetch_mind.py` puis
`scripts/build_mind_digest.py`.

## Les réserves

Le test d'échangeabilité porte sur le **rang enregistré**. Il établit que ce rang ne prédit pas
le clic ; il ne dit rien de l'ordre réellement affiché, qui n'est pas dans le jeu et ne peut pas
en être déduit. C'est bien la limite du résultat : le biais de position de Microsoft News reste
inconnu, et inconnaissable depuis MIND.

L'étalonnage de puissance suppose par ailleurs le modèle $e(R) = R^{-\eta}$. Un examen à
cascade, ou dépendant du contenu, produirait une autre forme de dépendance au rang — que le test
détecterait tout aussi bien, puisqu'il ne teste que l'indépendance, mais que la sévérité
minimale détectable ne résumerait plus.

## Pistes ouvertes

1. **Trouver un jeu public qui enregistre le rang servi.** Baidu-ULTR publie la position
   d'affichage et l'entourage de page ; c'est un jeu de recherche, non de recommandation
   d'actualité, et la transposition n'est pas gratuite.
2. **Évaluer sur MIND ce qui ne dépend pas de l'exposition**, en le disant : composition,
   diversité servie, frontière de compromis en pertinence déclarée.
3. **Faire du test d'échangeabilité un contrôle d'acceptation** des journaux transmis au titre
   de l'article 40 du DSA : un journal dont l'ordre est indiscernable d'un mélange n'est pas
   auditable contrefactuellement, et il vaut mieux le savoir avant l'audit qu'après.
4. **Comparer à des lignes de base réglées** — MMR, réordonnancement aléatoire, popularité —
   qui reste la dette la plus ancienne du programme d'évaluation.

---

*Implémentation : `ide.mind`, `scripts/fetch_mind.py`, `scripts/build_mind_digest.py` ·
Notebook : [16 — L'exploration réelle de MIND](notebooks/16_exploration_mind.ipynb) ·
[rang adverse et sévérité](rang-adverse.md) · [rang et contrefactuel](evaluation.md) ·
[feuille de route](feuille-de-route.md)*
