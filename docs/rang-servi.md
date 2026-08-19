# Deux journaux qui enregistrent le rang servi

!!! success "Le contrôle positif passe, et du bon côté"
    Sur **Baidu-ULTR**, le test d'échangeabilité qui ne détectait rien dans MIND rejette à
    $z = -206$ ($p < 10^{-12}$). Le signe compte autant que l'ampleur : les clics se concentrent
    **en haut**, ce qu'un biais de position exige et ce qu'un mélange ne produit pas.

!!! success "La sévérité n'a plus à être posée"
    $\hat\eta = 1{,}10 \pm 0{,}09$ par effets fixes de document sur une page de résultats de
    recherche. L'ajustement agrégé donne 1,49 : l'écart est le **confondant de qualité**, la
    plateforme plaçant les meilleurs documents en tête.

!!! danger "Mais $\eta$ est une propriété de la surface, pas une constante"
    Sur l'**Open Bandit Dataset**, où l'affectation des contenus aux positions est
    **aléatoire** — donc l'effet est causal, sans modèle — un bandeau de trois vignettes
    horizontales décroît en $R^{-0{,}04}$ à $R^{-0{,}11}$. Un ordre de grandeur sépare les deux
    surfaces, et c'est exactement l'ampleur d'erreur que coûte un $\eta$ transporté.

!!! failure "Et aucun de ces jeux ne permet l'évaluation annoncée"
    Il y faudrait le rang servi **et** une étiquette de point de vue interprétable. MIND a les
    catégories sans le rang ; Baidu-ULTR a le rang sans étiquette ; l'Open Bandit Dataset a le
    rang, la propension et trois attributs catégoriels — **anonymisés**. Le jeu de données qui
    permettrait d'évaluer l'[ADE](ade.md) de bout en bout n'existe pas publiquement.

---

## Ce que cette recherche devait trouver

[L'exploration réelle de MIND](mind.md) s'est terminée sur une exigence plutôt que sur un
résultat : il faut un jeu qui **enregistre le rang d'affichage**, faute de quoi l'exposition
n'est pas identifiable et l'évaluation contrefactuelle d'un réordonnancement est vide par
construction.

Deux journaux publics répondent, et pas à la même exigence.

| | MIND | Baidu-ULTR | Open Bandit Dataset |
|---|---|---|---|
| rang servi enregistré | **non** — mélangé | **oui**, 1 à 20 | **oui**, 3 positions |
| fils groupés | oui | oui, par session | non, une ligne par impression |
| propension vraie publiée | non | non | **oui** |
| seau à politique aléatoire | non | non | **oui** |
| étiquette de point de vue | oui, éditoriale | non | attributs anonymisés |
| taille employée ici | 5,8 M lignes | 0,5 M lignes | 5,9 M lignes |
| licence | recherche Microsoft | CC BY-NC 4.0 | CC BY 4.0 |

![Deux journaux qui enregistrent le rang servi](figures/fig17_rang_servi.png)

/// caption
Ce qu'un rang réellement servi fait à la courbe ; le contrôle qui distingue un ordre d'un
mélange ; l'effet de position mesuré sans modèle sur un bandeau de trois vignettes ; et
l'estimateur contrefactuel jugé contre la valeur qu'il estime. Figure régénérée par
[le notebook 17](notebooks/17_rang_servi.ipynb).
///

## 1. Baidu-ULTR : le contrôle positif

Une tranche de 524 164 documents servis, 64 200 sessions de recherche, rangs 1 à 20.

| Journal | Fils utiles | $z$ | $p$ | Lecture |
|---|---|---|---|---|
| MIND | 156 965 | **+0,12** | 0,91 | ordre indiscernable d'un mélange |
| Baidu-ULTR | 29 916 | **−205,72** | $< 10^{-12}$ | l'ordre porte le placement |

Ce contrôle-là importait autant que le verdict sur MIND : un test qui ne rejette jamais rien
serait indiscernable d'un test aveugle. Celui-ci rejette, massivement, et du côté que la théorie
prescrit.

Le taux de clic suit la décroissance attendue : 0,340 au premier rang, 0,088 au troisième,
0,010 au dixième.

## 2. La sévérité, mesurée trois fois

| Méthode | $\hat\eta$ |
|---|---|
| ajustement agrégé (rangs 1-10) | 1,494 |
| à longueur de session fixée (10 documents) | 1,144 |
| **effets fixes de document** | **1,099 ± 0,089** |

Sur MIND, l'écart entre l'ajustement agrégé et les effets fixes venait de la composition des
longueurs. Ici il vient d'autre chose, et de plus attendu : la plateforme place les **meilleurs
documents en tête**, donc une partie de la décroissance est de la qualité, pas de l'exposition.
Les effets fixes l'éliminent en ne comparant un document qu'à lui-même.

!!! warning "La couverture est mince, et le nombre de lignes ne le dit pas"
    Sur 444 709 documents distincts, **335** atteignent le seuil d'impressions et **55**
    apparaissent à plusieurs rangs. Sur une page de résultats, une même URL réapparaît rarement.
    L'estimation est identifiée — l'erreur type le dit — mais elle repose sur cinquante-cinq
    documents, pas sur un demi-million de lignes.

## 3. L'Open Bandit Dataset : la position mesurée sans modèle

Le seau **aléatoire** affecte les contenus aux positions au hasard : l'écart de taux de clic
entre positions y est un effet **causal** de la position, sans qu'aucun modèle d'examen n'ait à
être posé. C'est la mesure la plus propre possible de $\eta$ — sur une surface toute différente,
trois vignettes horizontales de gauche à droite.

| Campagne | gauche | centre | droite | $\hat\eta$ |
|---|---|---|---|---|
| all (1,37 M impressions) | 0,00354 | 0,00347 | 0,00340 | 0,037 |
| men (0,45 M impressions) | 0,00538 | 0,00524 | 0,00475 | 0,105 |

Les erreurs types valent 0,00009 (all) et 0,00019 (men) : l'effet va dans le bon sens et reste,
vignette à vignette, de l'ordre de deux erreurs types. Il est **mesurable en tendance, pas
concluant position à position** — et il est dix fois plus faible que sur une page de résultats.

Le [rang adverse](rang-adverse.md) avait chiffré ce que coûte un $\eta$ posé de travers : jusqu'à
+179 %. Transporter la valeur d'une page de résultats vers un bandeau — ou l'inverse — est
précisément une erreur de cette taille.

## 4. La confrontation : un estimateur jugé contre la vérité

L'Open Bandit Dataset contient deux seaux servis **en parallèle** par deux politiques
différentes. On peut donc faire ce qu'aucun autre jeu de ce dépôt ne permet : estimer la valeur
de la politique uniforme à partir des seules données d'une **autre** politique, puis la comparer
à sa valeur mesurée là où elle a réellement servi.

Vérité terrain : **0,005124 ± 0,000106**, mesurée sur 452 949 impressions du seau aléatoire.
Journal d'enregistrement : 4 077 727 impressions servies par Bernoulli Thompson Sampling.

| Estimateur | Valeur | Écart |
|---|---|---|
| naïf (taux de clic observé) | 0,006743 | **+31,6 %** |
| **IPS** | 0,005253 | **+2,5 %** |
| SNIPS | 0,004768 | −7,0 % |
| IPS plafonné à 10 | 0,004473 | −12,7 % |
| IPS plafonné à 100 | 0,005238 | +2,2 % |

**La correction fonctionne.** C'est la première fois dans ce dépôt qu'un estimateur
contrefactuel est jugé contre la grandeur qu'il prétend estimer, et non contre une simulation.

!!! danger "Et le diagnostic qui interdit de crier victoire"
    La **taille d'échantillon effective** vaut **1 513** pour 4 077 727 impressions, soit
    0,04 %. L'estimation sans biais repose sur l'équivalent de mille cinq cents observations :
    à un taux de clic de 0,005, cela laisse une marge de l'ordre de la moitié du chiffre. Que
    l'écart tombe à 2,5 % tient donc autant à la chance qu'à la méthode.

    C'est exactement le diagnostic que `ide.offpolicy` impose de publier à côté du chiffre, et
    voici le cas réel qui montre pourquoi : sans lui, on croirait tenir une mesure sur quatre
    millions de lignes.

**Le plafonnement n'est pas gratuit non plus.** Plafonner les poids à 10 ramène l'estimation à
−12,7 % : le biais échangé contre de la variance est du même ordre que l'erreur qu'on cherchait
à corriger. Le plafond doit être publié avec le chiffre.

## 5. Ce que cela règle, et ce que cela ne règle pas

**Réglé — le critère de choix d'un jeu de données.** Ni la taille ni la présence d'étiquettes
éditoriales : l'enregistrement du rang servi, qui se **vérifie** avant toute mesure.

**Réglé — la sévérité se mesure.** 1,10 ± 0,09 sur une page de résultats, un dixième de cela sur
un bandeau de trois vignettes. Ce qui reste interdit est de transporter l'un vers l'autre.

**Réglé — les estimateurs contrefactuels tiennent devant une vérité terrain**, avec la réserve
chiffrée que leur précision effective est bien moindre que le nombre de lignes ne le suggère.

**Non réglé — l'évaluation de l'ADE.** Elle demande le rang servi *et* une étiquette de point de
vue interprétable. Aucun des trois jeux mesurés ne porte les deux. Une diversité calculée sur
des catégories anonymisées ne dit rien : le catalogue de référence de l'[IDE](ide.md) est une
déclaration politique, et une déclaration sur des hachages n'en est pas une.

C'est le troisième résultat négatif de cette série, et il vaut d'être dit aussi nettement que les
deux autres : **le jeu de données qui permettrait l'évaluation annoncée n'existe pas
publiquement.** Ce qui reste possible tient en trois lignes, et la
[feuille de route](feuille-de-route.md) en hérite :

1. mesurer sur MIND ce qui ne dépend pas de l'exposition, en le disant ;
2. mesurer sur Baidu-ULTR et l'Open Bandit Dataset ce qui ne dépend pas des points de vue ;
3. pour le reste, **demander la donnée** — ce qui, sous l'article 40 du DSA, est une démarche
   prévue et non un vœu. → [mémorandum](memorandum.md)

## Provenance des données

**Baidu-ULTR** : tranche `part-0_split-0` (0,9 Go) redistribuée par l'université d'Amsterdam
pour l'étude de reproductibilité de Hager et al. (SIGIR 2024), sous licence CC BY-NC 4.0. Quatre
colonnes sont lues sur les vingt-neuf du fichier — session, rang, clic, identité du document ;
les embeddings, qui font tout son poids, ne le sont pas.

**Open Bandit Dataset** : trois seaux (2,2 Go) sous licence CC BY 4.0 — la campagne « all » sous
politique aléatoire, et la paire « men » aléatoire / Bernoulli TS sans laquelle la confrontation
n'aurait rien à quoi se comparer.

Aucun fichier brut n'est versionné. Le dépôt porte un **condensé** de 0,7 Mo,
`data/exposure_digest.npz`, qui rend à l'identique tous les chiffres de cette page — un test le
vérifie — et se reconstruit par `scripts/fetch_exposure.py` puis
`scripts/build_exposure_digest.py`. Taille et empreinte SHA-256 de chaque source sont inscrites
dans `ide.exposure`.

!!! failure "Un défaut du condensé, trouvé par Baidu-ULTR"
    Le condensé de MIND résumait la structure d'un fil à sa **longueur**, en supposant qu'un fil
    de longueur $L$ occupe les rangs 1 à $L$. C'est vrai de MIND et **faux** d'une page de
    résultats, qui saute des rangs. Le condensé le vérifie désormais au lieu de le supposer, et
    conserve les rangs servis un par un lorsque l'hypothèse tombe. Le défaut était indolore —
    il rendait des chiffres du bon ordre de grandeur, $z = -200$ au lieu de $-206$ — ce qui est
    la façon dont ce genre d'erreur survit.

## Les réserves

Une tranche de Baidu-ULTR n'est pas Baidu-ULTR : 0,5 million de lignes sur 1,2 milliard de
sessions. Rien n'assure que la sévérité y soit celle du jeu entier, ni celle d'un autre moteur.

L'Open Bandit Dataset mesure une **recommandation de mode sur trois vignettes**. Le transport de
ses chiffres vers un fil d'actualité est exactement l'opération que cette page déconseille.

Enfin, la confrontation de la section 4 porte sur la valeur d'une politique **uniforme**, la
seule dont ce jeu contienne un seau. Rien n'assure que l'IPS se comporte aussi bien pour une
politique cible plus éloignée de celle qui a enregistré — au contraire, la taille effective y
serait plus faible encore.

---

*Implémentation : `ide.exposure`, `ide.logs`, `scripts/fetch_exposure.py`,
`scripts/build_exposure_digest.py` · Notebook :
[17 — Deux journaux qui enregistrent le rang servi](notebooks/17_rang_servi.ipynb) ·
[exploration réelle de MIND](mind.md) · [rang adverse et sévérité](rang-adverse.md) ·
[feuille de route](feuille-de-route.md)*
