# Les lignes de base, et la frontière exacte qui les juge

!!! success "Le filtre du dépôt se tient sur la frontière"
    Manque à gagner médian de **0,0 à 1,0 %** d'engagement selon le plancher, sur 150 viviers
    tirés au sort. Diversifier est facile ; diversifier **sans laisser d'engagement sur la
    table** ne l'est pas — le tirage au sort en perd 9 à 19 % pour atteindre les mêmes niveaux.

!!! failure "Mais il n'est ni seul ni premier"
    **MMR**, publié en 1998, tient la frontière à tous les planchers — 0,0 à 0,2 % — et devance
    même le filtre en duel direct au plancher 0,80 (35 victoires contre 18). La nouveauté de ce
    dépôt n'est pas dans son algorithme.

!!! success "Il se détache là où l'exigence est haute"
    Au plancher **0,90**, MMR ne trouve aucun réglage conforme dans **47 %** des viviers — son
    paramètre sature avant — contre **12 %** pour le filtre entropique, qui l'emporte alors 72
    fois contre 14.

!!! danger "Et le prix de la norme dépend du lecteur"
    Un plancher de 0,90 coûte **3,8 %** d'engagement quand la pertinence est indépendante du
    point de vue, et **17,1 %** quand elle en découle entièrement. **La norme coûte le plus cher
    là où elle sert le plus.**

---

## La question qu'on n'avait pas posée

Le filtre proposé par ce dépôt n'a jamais été comparé qu'à un seul adversaire : le classement
par pertinence pure, dont il se distingue **par construction**. Personne ne lui a demandé s'il
faisait mieux qu'une heuristique triviale.

C'était la dette la plus ancienne du programme d'évaluation, et la seule qui ne demandait
aucune donnée nouvelle.

## Le protocole

Un fil se juge sur deux grandeurs en tension : l'**engagement** qu'il produit et la **diversité
qu'il expose**, toutes deux pondérées par l'attention de chaque rang. Un réordonnanceur n'est
donc ni bon ni mauvais : il occupe un point du plan, et la seule question qui vaille est de
combien il rate la frontière atteignable.

Cette frontière n'est pas estimée, elle est **calculée exactement** : les 151 200 arrangements
ordonnés de six contenus tirés d'un vivier de dix sont énumérés, et l'on retient à chaque niveau
de diversité l'engagement maximal. C'est une borne supérieure, pas un concurrent de plus.

| Méthode | Paramètre balayé |
|---|---|
| classement par pertinence | — (référence) |
| **tour de rôle** | nombre de positions de tête réparties entre points de vue |
| **MMR** (Carbonell & Goldstein, 1998) | compromis $\lambda$ entre pertinence et écartement |
| **Boltzmann** | température du tirage $e^{r/T}$ |
| **filtre entropique** (ce dépôt) | coefficient $\mu$ de $\text{pertinence} + \mu\,\Delta H$ |
| **tirage au sort** | la graine — la ligne de base qu'on oublie de tracer |

Comparer les méthodes là où chacune tombe serait injuste : leurs paramètres ne se correspondent
pas. On fixe donc le **plancher** et l'on demande à chacune ce qu'elle sait faire de mieux en
s'y conformant — exactement la question que pose un régulateur.

![Les lignes de base et la frontière exacte](figures/fig19_lignes_de_base.png)

/// caption
Un vivier, sa frontière exacte et ce que chaque méthode y atteint ; le manque à gagner médian
sur 150 viviers ; la part des viviers où le plancher n'est jamais atteint ; et le prix de la
norme selon l'alignement entre pertinence et point de vue. Figure régénérée par
[le notebook 19](notebooks/19_lignes_de_base.ipynb).
///

## Ce que 150 viviers donnent

**Manque à gagner médian**, parmi les viviers où la méthode atteint le plancher :

| Méthode | 0,50 | 0,60 | 0,70 | 0,80 | 0,90 |
|---|---|---|---|---|---|
| tour de rôle | 0,0 % | 0,0 % | 0,0 % | 3,8 % | 4,8 % |
| **MMR** | 0,0 % | 0,0 % | 0,0 % | **0,0 %** | **0,2 %** |
| Boltzmann | 0,0 % | 0,0 % | 0,1 % | 1,2 % | 3,7 % |
| **filtre entropique** | 0,0 % | 0,0 % | 0,0 % | **0,0 %** | **1,0 %** |
| tirage au sort | 9,3 % | 9,8 % | 11,0 % | 12,9 % | 19,1 % |

**Part des viviers où le plancher n'est jamais atteint**, alors qu'il l'est par la frontière :

| Méthode | 0,50 | 0,60 | 0,70 | 0,80 | 0,90 |
|---|---|---|---|---|---|
| tour de rôle | 0 % | 0 % | 0 % | 0 % | 28 % |
| MMR | 0 % | 0 % | 3 % | 0 % | **47 %** |
| Boltzmann | 1 % | 1 % | 1 % | 8 % | 36 % |
| filtre entropique | 0 % | 0 % | 1 % | 0 % | **12 %** |
| tirage au sort | 0 % | 0 % | 1 % | 0 % | 7 % |

Les deux tableaux se lisent ensemble, et c'est leur croisement qui départage. Le tirage au sort
**atteint** les planchers plus souvent que toute autre méthode — le hasard produit de la
diversité — mais il paie 9 à 19 % pour cela. MMR ne paie rien et **échoue** une fois sur deux à
l'exigence haute. Le filtre entropique est le seul à faire les deux : atteindre et ne pas payer.

L'explication tient à la règle : le filtre optimise **directement la grandeur contrainte**,
tandis que MMR optimise un écartement moyen qui n'en est qu'un substitut — et un substitut qui
sature.

## Le prix de la norme dépend du lecteur

La comparaison ci-dessus emploie des viviers où la pertinence est tirée indépendamment du point
de vue. Ce n'est pas neutre : c'est l'hypothèse la plus favorable à une norme de diversité,
puisqu'il existe alors des contenus pertinents dans chaque point de vue.

En faisant varier l'**alignement** — la part de la pertinence qui découle du point de vue du
contenu :

| Alignement | 0,60 | 0,70 | 0,80 | 0,90 |
|---|---|---|---|---|
| 0,00 — les intérêts traversent les points de vue | 0,0 % | 0,3 % | 1,1 % | 3,8 % |
| 0,50 | 0,0 % | 0,8 % | 2,6 % | 5,6 % |
| 1,00 — la préférence **est** un point de vue | 2,2 % | 6,9 % | 8,6 % | **17,1 %** |

**La norme coûte le plus cher exactement là où elle sert le plus.** C'est inconfortable et il
faut le dire : cela prédit où portera l'objection des plateformes — sur les lecteurs les plus
polarisés, ceux dont le cas motive la norme.

Cela réconcilie aussi deux chiffres du dépôt qui semblaient se contredire. Le
[rang adverse](rang-adverse.md) mesurait un coût de 10 à 21 % parce que la pertinence y était
attachée au point de vue — un alignement de 1. Ici, à alignement nul, le même plancher ne coûte
presque rien. Ce n'est pas une contradiction : c'est une **dépendance au lecteur** que ni l'un
ni l'autre n'avait isolée.

## Ce que cette comparaison règle

**La dette est payée.** Le filtre a été jugé contre quatre concurrents et contre la borne
exacte, sur 150 viviers, à cinq niveaux d'exigence.

**Le verdict est mitigé, et c'est le bon résultat.** Le filtre tient la frontière — ce n'était
pas gagné d'avance — mais il n'apporte rien qu'une heuristique de 1998 n'apporte déjà, sauf aux
planchers élevés. Ce qui distingue ce dépôt n'est donc pas son algorithme : c'est la **norme**
et les **instruments qui la vérifient**.

**Une conséquence pour le mémorandum.** Puisqu'une heuristique publiée en 1998 tient un plancher
de 0,80 sans perte mesurable d'engagement, l'argument selon lequel une norme de diversité
exigerait de refondre les moteurs de recommandation ne tient pas. Ce qu'elle exige, c'est de la
**mesurer**. → [mémorandum](memorandum.md)

## Les réserves

Ces viviers sont **synthétiques** : dix contenus, quatre points de vue, six positions. La
frontière exacte n'existe qu'à cette échelle — c'est le prix de l'exactitude, et le même que
celui du [rang adverse](rang-adverse.md). Rien n'assure que le classement relatif des méthodes
se transporte à un vivier de mille contenus.

La pertinence y est en outre **connue**, alors qu'une plateforme ne dispose que de son
estimation. Une erreur d'estimation dégraderait toutes les méthodes, mais pas nécessairement
dans le même ordre : une règle gourmande sur une grandeur bruitée peut se comporter plus mal
qu'une règle qui l'ignore.

Enfin, le tirage au sort est ici traité généreusement — dix-huit tirages par vivier, dont on
retient le meilleur conforme. Une plateforme n'aurait pas ce luxe, et sa performance réelle
serait pire que celle rapportée.

---

*Implémentation : `ide.baselines` · Notebook :
[19 — Les lignes de base](notebooks/19_lignes_de_base.ipynb) ·
[ADE — l'algorithme](ade.md) · [rang adverse et sévérité](rang-adverse.md) ·
[mémorandum](memorandum.md)*
