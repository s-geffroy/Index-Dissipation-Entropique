# Test adverse : l'IDE se sature sans coût

!!! failure "L'index, tel qu'il était défini, n'est pas une norme tenable"
    Une plateforme capable de dissocier l'étiquette du contenu obtient un **IDE de 1,000 — la
    note maximale — pour une diversité de contenu strictement nulle**, sans céder un point
    d'engagement. Et il n'est pas besoin d'aller jusque-là : à mi-découplage, la contrainte n'a
    plus que **36 %** de sa force.

!!! success "L'entropie quadratique de Rao résiste, et se retourne contre le manipulateur"
    Au-delà d'un découplage de moitié, le plancher devient **inatteignable** : la plateforme ne
    peut plus s'y conformer, quoi qu'elle fasse. Et en deçà, il coûte **plus** cher à mesure
    qu'elle vide ses étiquettes — 16 % à découplage nul, 40 % à mi-découplage.

!!! tip "Ce que cela prescrit"
    Le résultat ne détruit pas l'index, il en **déplace la définition** : ce qu'il faut mesurer
    n'est pas la diversité des étiquettes servies, mais la distance sémantique entre les
    contenus qu'elles portent. La [recommandation 1 du mémorandum](memorandum.md) est révisée
    en conséquence.

---

## La question, et pourquoi elle précède toute norme

L'[audit critique §2.2](limites.md) relevait une objection que le reste du dépôt n'avait pas
traitée : une plateforme contrainte de maintenir un IDE élevé peut servir des contenus
**formellement divergents mais substantiellement vides** — un article étiqueté « point de vue
opposé » dont le propos reste adjacent à celui du lecteur.

C'est un problème d'optimisation sous contrainte, donc **entièrement simulable** : aucune
donnée réelle n'est nécessaire pour le trancher. Et il valait mieux le trancher avant de
proposer un seuil réglementaire, car si l'index se sature sans coût, tout ce qui s'appuie
dessus s'effondre.

## Le modèle

Un catalogue de $k$ points de vue, de positions canoniques $c_\ell$ sur un axe d'opinion. Un
lecteur en $u$. L'engagement décroît avec la distance au lecteur :

$$g(x) = \exp\left(-\frac{(x-u)^2}{2w^2}\right)$$

C'est l'hypothèse de bulle, et elle est **défavorable à la plateforme** : elle suppose que
conforter paie. Sans elle, il n'y aurait pas de conflit entre diversité et profit, donc pas de
question à poser.

Le **découplage** $\varphi \in [0,1]$ mesure la latitude de la plateforme à dissocier
l'étiquette du contenu. Le meilleur article portant l'étiquette $\ell$ se trouve en

$$x^*_\ell = c_\ell + \varphi\,(u - c_\ell)$$

À $\varphi = 0$ l'étiquette prédit le contenu ; à $\varphi = 1$, toute étiquette est disponible
en version vide, arbitrairement proche du lecteur.

### Un plancher d'entropie est une température

La plateforme maximise $\sum_\ell q_\ell\,g(x^*_\ell)$ sous $\mathrm{IDE}(q) \geq \tau$. Le
maximum d'une forme linéaire à entropie fixée est une distribution de Boltzmann :

$$q_\ell \propto \exp\big(g(x^*_\ell)/T\big)$$

où $T$ est le multiplicateur qui sature le plancher. **La contrainte réglementaire agit
exactement comme la température sociale du reste du dépôt** : à $T \to 0$ la plateforme sert son
unique meilleur contenu, à $T \to \infty$ elle sert l'uniforme.

Ce n'est pas une analogie mais la même algèbre, et elle a une conséquence pratique : la solution
est **exacte** plutôt qu'approchée. Sur un résultat négatif, où une heuristique de solveur
pourrait porter la conclusion, cela n'est pas un détail.

## Résultats

![Test adverse : l'IDE se sature sans coût, l'entropie de Rao non](figures/fig13_test_adverse.png)

/// caption
Deux fils au même IDE, l'un dispersé et l'autre réduit à un point ; l'effacement de la
contrainte avec le découplage ; les ciseaux entre diversité affichée et diversité servie ; et
le seuil au-delà duquel un plancher de Rao devient inatteignable. Figure régénérée par
[le notebook 13](notebooks/13_test_adverse_index.ipynb).
///

### 1. Sur un catalogue honnête, la contrainte mord

C'est la vérification qui rend le test non trivial : si le plancher ne coûtait rien même sans
manipulation, il n'y aurait rien à saturer.

| Plancher d'IDE | 0,50 | 0,70 | **0,80** | 0,90 | 0,95 | 1,00 |
|---|---|---|---|---|---|---|
| engagement perdu | 4,4 % | 12,0 % | **18,1 %** | 27,1 % | 34,0 % | 51,4 % |

### 2. Et elle s'efface avec le découplage

| Plancher | $\varphi = 0$ | $\varphi = 0{,}25$ | $\varphi = 0{,}5$ | $\varphi = 0{,}75$ | $\varphi = 1$ |
|---|---|---|---|---|---|
| 0,80 | 18,1 % | 12,5 % | 6,6 % | 1,8 % | **0,0 %** |
| 0,95 | 34,0 % | 25,9 % | 15,4 % | 4,8 % | **0,0 %** |
| **1,00** | 51,4 % | 41,4 % | 26,4 % | 8,7 % | **0,0 %** |

La dernière colonne est **zéro partout**, y compris pour un plancher d'IDE de 1,00.

Et ce que contient alors le fil :

| $\varphi$ | IDE | Rao | engagement | coût |
|---|---|---|---|---|
| 0,00 | 0,800 | 0,443 | 0,798 | 18,1 % |
| 0,50 | 0,800 | 0,215 | 0,928 | 6,6 % |
| **1,00** | **1,000** | **0,000** | **1,000** | **0,0 %** |

**L'index décerne son meilleur score à un fil qui ne contient qu'un seul point de vue.**

### 3. La dégradation est plus rapide que le découplage

Le découplage complet est une caricature — aucune plateforme ne peut vider *toutes* ses
étiquettes. La question qui compte pour un régulateur est la vitesse à laquelle la contrainte
perd sa force.

| $\varphi$ | 0,0 | 0,2 | 0,4 | **0,5** | 0,6 | 0,8 | 1,0 |
|---|---|---|---|---|---|---|---|
| force restante | 100 % | 76 % | 49 % | **36 %** | 25 % | 7 % | 0 % |

Un découplage de moitié — une latitude que l'on peut supposer accessible à une plateforme
disposant d'un vaste catalogue — retire déjà les deux tiers de la contrainte.

### 4. L'entropie quadratique de Rao résiste

$$Q = \frac{2}{D}\sum_{\ell m} q_\ell q_m \, |x^*_\ell - x^*_m|$$

Elle ne compte pas les étiquettes, elle compte les **écarts entre contenus servis**, rapportés
à l'étendue $D$ du catalogue de référence.

| $\varphi$ | $Q$ atteignable | conforme à $Q \geq 0{,}5$ | coût |
|---|---|---|---|
| 0,00 | 1,000 | oui | 15,6 % |
| 0,25 | 0,750 | oui | 21,1 % |
| 0,50 | 0,500 | oui | 39,5 % |
| 0,75 | 0,250 | **non — inatteignable** | — |
| 1,00 | 0,000 | **non — inatteignable** | — |

Deux propriétés, et la seconde était inattendue :

* **le plancher devient inatteignable.** Au-delà d'un découplage de moitié, aucune distribution
  d'étiquettes ne satisfait la contrainte. La plateforme qui a vidé ses étiquettes **ne peut
  plus se conformer** ;
* **le coût augmente avec le découplage** au lieu de diminuer. Vider ses étiquettes réduit la
  diversité atteignable, donc rend la conformité plus chère. **Manipuler l'étiquetage se
  retourne contre la plateforme.**

C'est cette seconde propriété, plus que la simple robustesse, qui fait de $Q$ une norme tenable :
elle inverse l'incitation.

!!! danger "Un piège de normalisation, et ce qu'il aurait coûté"
    Une première version du module normalisait $Q$ par l'étalement **effectivement servi**. La
    mesure devenait invariante d'échelle, et un fil réduit à un point y marquait $Q \approx 1$
    sur du bruit d'arrondi — cette page aurait conclu que l'entropie de Rao est manipulable elle
    aussi, c'est-à-dire l'inverse de la vérité. L'unité retenue est donc l'étendue du catalogue
    **de référence**, fixée par le régulateur, et un test verrouille le point.

### 5. Une signature de manipulation, sans seuil inventé

L'écart brut $\mathrm{IDE} - Q$ n'est **pas** interprétable seul : les deux indices ne sont pas
sur la même échelle, et un fil parfaitement honnête en affiche déjà 0,36. Publier un seuil
là-dessus reviendrait à fabriquer un chiffre — ce que ce dépôt a déjà eu à retirer une fois.

La grandeur interprétable est l'**excès sur la contrefactuelle honnête** : ce qu'un catalogue
dont les étiquettes prédisent le contenu afficherait au même IDE.

| $\varphi$ | 0,00 | 0,25 | 0,50 | 0,75 | 1,00 |
|---|---|---|---|---|---|
| écart brut | 0,357 | 0,476 | 0,585 | 0,692 | 1,000 |
| **excès** | **0,000** | 0,119 | 0,228 | 0,335 | 0,643 |

Nul par construction pour une plateforme honnête, croissant avec la manipulation, et calculable
par le régulateur puisqu'il ne dépend que du catalogue de référence — qu'il fixe lui-même.

## Ce que cela change pour le mémorandum

La [recommandation 1](memorandum.md) imposait un plancher d'IDE. Cette formulation est
**abandonnée** : elle est saturable à coût nul par une plateforme qui découple étiquette et
contenu, et largement affaiblie bien avant.

Ce qui la remplace :

1. **le plancher porte sur l'entropie quadratique de Rao**, mesurée sur les contenus servis ;
2. **le régulateur fixe l'étendue du catalogue de référence**, qui sert d'unité — c'est la même
   question politique que le choix de $k$, déplacée d'un cran ;
3. **les deux indices sont publiés sur le même fil**, et l'excès de signature est contrôlé.

## Ce que le modèle suppose, et qui pourrait le retourner

Le résultat est un théorème sur un modèle, pas une mesure. Trois hypothèses le portent, et il
faut les nommer :

| Hypothèse | Effet si elle tombe |
|---|---|
| **la bulle paie** — l'engagement décroît avec la distance au lecteur | s'il n'en va pas ainsi, il n'y a pas de conflit à arbitrer et la question disparaît. C'est l'hypothèse la plus contestable, et elle n'est pas vérifiée empiriquement ici |
| **le découplage est gratuit** — produire un contenu vide sous une étiquette éloignée ne coûte rien | un coût de production limiterait le $\varphi$ atteignable, sans changer la forme du résultat |
| **l'axe d'opinion est unidimensionnel** | en dimension supérieure une plateforme dispose de plus de directions où se cacher : cela va dans le sens du résultat, non contre lui |

## Pistes ouvertes

1. **Reprendre le test sur des *embeddings* réels** plutôt que sur un axe synthétique. Le jeu de
   données MIND fournit des historiques de consultation et des catégories éditoriales : on
   pourrait y mesurer la distance sémantique effective entre contenus d'une même étiquette, donc
   estimer le $\varphi$ dont une plateforme dispose réellement.
2. **Chiffrer le coût de production du découplage.** Le modèle le suppose nul ; s'il ne l'est
   pas, il existe un $\varphi$ d'équilibre, et c'est lui qui détermine si la manipulation est
   rentable.
3. **Étendre au jeu de Stackelberg** de la [feuille de route §4.2](feuille-de-route.md) : ici la
   plateforme optimise sous une contrainte fixée, mais un régulateur devrait anticiper la
   réponse et choisir le plancher en conséquence.
4. **Traiter le choix du catalogue de référence.** Toute la résistance de $Q$ repose sur une
   étendue fixée par le régulateur. Qui la fixe, et comment, redevient la question politique que
   l'[audit §2.1](limites.md) posait déjà pour $k$.

---

*Implémentation : `ide.gaming` · Notebook :
[13 — Test adverse](notebooks/13_test_adverse_index.ipynb) ·
[IDE — l'index](ide.md) · [mémorandum](memorandum.md) ·
[audit critique](limites.md)*
