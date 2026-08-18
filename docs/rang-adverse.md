# Rang adverse et sévérité : ce qu'une norme aveugle laisse passer

!!! failure "Une plateforme certifiée à 0,70 n'expose que 0,36"
    Jugées sur des fils **ordonnés** plutôt que sur des compositions, les quatre mesures du
    [test adverse](gaming.md) certifient toutes une diversité que le lecteur ne reçoit pas.
    L'entropie de Rao certifie 0,750 pour une diversité exposée de **0,355** ; l'entropie de
    position, 0,774 pour **0,443**.

!!! success "Un plancher conscient du rang le ferme — et il coûte"
    La diversité exposée atteint alors le plancher, les contenus divergents remontant dans le
    fil. Le prix d'engagement **double** : de 8,2 % à 18,9 % pour l'entropie de Rao, de 10,7 %
    à 20,9 % pour l'entropie de position. Une norme qui ne coûterait pas davantage ne fermerait
    rien.

!!! success "La sévérité du biais de position s'estime, et il fallait l'estimer"
    $\hat\eta = 1{,}013 \pm 0{,}019$ sur 40 000 impressions, par régression à effets fixes de
    contenu. Poser $\eta$ au jugé coûte jusqu'à **179 %** d'erreur — l'ordre de grandeur même
    du biais qu'on prétendait corriger.

---

## Deux dettes, réglées ensemble

Le [notebook 14](notebooks/14_rang_et_contrefactuel.ipynb) laissait deux dettes explicites, et
elles ont la même racine : **le rang**.

Les quatre mesures comparées au [test adverse](gaming.md) l'avaient été sur des
**compositions** — quelle part de l'attention va à quel point de vue — jamais sur des fils
ordonnés. Et les estimateurs contrefactuels reposaient sur un modèle de biais de position dont
la sévérité était **posée**, non mesurée.

![Rang adverse et sévérité](figures/fig15_rang_adverse.png)

/// caption
La diversité affichée contre celle qui est réellement exposée ; l'écart selon l'exigence de la
norme ; la sévérité retrouvée, et le seuil au-delà duquel elle cesse de l'être ; et ce que coûte
un $\eta$ posé au jugé. Figure régénérée par
[le notebook 15](notebooks/15_rang_adverse_et_severite.ipynb).
///

## 1. Le test adverse, sur des fils ordonnés

Le fil compte $n$ positions à remplir depuis un catalogue de $k$ points de vue, soit $k^n$ fils
possibles — 65 536 ici. Ils sont **tous énumérés** : l'optimum est exact, non le résultat d'une
heuristique. Il s'agit encore de résultats négatifs, et un optimum manqué par un solveur y
produirait exactement la même apparence qu'une norme qui tient.

### Sous plancher aveugle au rang

| Mesure | Coût | Affiché | **Exposé** | Fil servi |
|---|---|---|---|---|
| Rao (ILD) | 8,2 % | 0,750 | **0,355** | `00000033` |
| entropie de position | 10,7 % | 0,774 | **0,443** | `00000123` |
| Gaussian ILD | *inatteignable* | — | — | — |
| proximité à la cible | 5,9 % | 0,750 | **0,628** | `00000012` |

Le fil optimal a toujours la même forme : six contenus du point de vue préféré, puis les
divergents relégués aux dernières positions, là où l'attention ne va plus.

### Sous plancher conscient du rang

| Mesure | Coût | Affiché | Exposé | Fil servi |
|---|---|---|---|---|
| Rao (ILD) | **18,9 %** | 0,938 | **0,702** | `00033300` |
| entropie de position | **20,9 %** | 0,953 | **0,702** | `00013122` |
| proximité à la cible | **10,6 %** | 0,750 | **0,701** | `00100200` |

L'échappatoire est fermée, et le coût double. C'est le prix de la norme, et il devait être
chiffré avant d'être proposé.

### L'écart croît avec l'exigence

| Plancher aveugle | 0,40 | 0,50 | 0,60 | 0,70 | 0,80 |
|---|---|---|---|---|---|
| Rao (ILD) | 0,262 | 0,306 | 0,350 | **0,395** | 0,397 |
| entropie de position | 0,173 | 0,249 | 0,263 | 0,331 | 0,319 |
| proximité à la cible | 0,000 | 0,066 | 0,066 | 0,122 | 0,166 |

**Plus la norme aveugle exige de diversité, plus il devient rentable de l'enterrer.** Ce n'est
pas l'artefact d'un plancher particulier.

On notera que la **proximité à la cible** résiste le mieux — écart nul à plancher 0,40, 0,122 à
0,70 — là où l'entropie de Rao atteint 0,395. C'est le troisième point sur lequel elle se
détache, après avoir été la seule à rendre explicite la forme d'exposition visée.

### Un écart, cette fois, seuillable

Le [test adverse](gaming.md) avait dû renoncer à seuiller l'écart entre deux indices
*différents* : l'IDE et l'entropie de Rao ne sont pas sur la même échelle, et un fil honnête en
affichait déjà 0,36.

L'écart mesuré ici est d'une autre nature : c'est **la même mesure appliquée deux fois au même
fil**, une fois à l'aveugle du rang et une fois en le prenant en compte. Il vaut zéro pour un
fil qui ne relègue pas, et il est donc directement interprétable.

## 2. Estimer la sévérité du biais de position

Le modèle pose $P(\text{clic}) = R^{-\eta}\,g(i)$, donc

$$\log \mathrm{CTR}(i, R) = \log g(i) - \eta \log R$$

La pertinence $g(i)$ y est un **effet fixe de contenu** : on ne cherche pas à l'estimer, on
l'élimine en centrant à l'intérieur de chaque contenu. Ce qui subsiste est la seule variation
qui identifie $\eta$ — celle d'un **même contenu vu à des rangs différents**. C'est la forme la
plus simple de la récolte d'interventions, et elle n'exige aucune expérience.

| $\eta$ vrai | 0,40 | 0,70 | 1,00 | 1,30 | 1,60 |
|---|---|---|---|---|---|
| $\hat\eta$ | 0,409 | 0,693 | 1,005 | 1,315 | 1,649 |
| erreur type | 0,0045 | 0,0064 | 0,0085 | 0,0121 | 0,0192 |

### Ce qui conditionne l'estimation

| Exploration du classement | $\hat\eta$ | Erreur type | Identifiable |
|---|---|---|---|
| **0,00** | — | — | **non** |
| 0,02 | 1,595 | 0,247 | oui, mais sans valeur |
| 0,05 | 0,800 | 0,092 | oui |
| 0,15 | 1,031 | 0,036 | oui |
| 0,50 | 1,004 | 0,011 | oui |

**À politique déterministe, $\eta$ n'est pas dans les données.** Aucun contenu ne change de
rang, il n'y a donc aucune variation à exploiter, et l'estimateur **refuse de renvoyer un
chiffre** plutôt que d'en inventer un. C'est précisément le cas où poser la valeur au lieu de
l'estimer serait indétectable dans les résultats.

À exploration faible, il en renvoie un — mais l'erreur type dit qu'il ne vaut rien.

## 3. Pourquoi il fallait l'estimer

| $\eta$ supposé | 0,5 | 0,8 | **1,0** | 1,2 | 1,5 | 2,0 |
|---|---|---|---|---|---|---|
| coût estimé | 2,7 % | 4,9 % | **6,6 %** | 8,6 % | 11,9 % | 18,4 % |
| erreur | −59 % | −26 % | **+0,6 %** | +30 % | +80 % | **+179 %** |

Le coût réel vaut 6,6 %. **Poser $\eta$ de travers coûte jusqu'à 179 % d'erreur** — c'est-à-dire
l'ordre de grandeur du biais de 201 % que la correction contrefactuelle prétendait éliminer.

Avec $\eta$ estimé sur les données — $1{,}013 \pm 0{,}019$ — le coût tient entre **6,6 % et
6,9 %** contre 6,6 % de valeur vraie.

> **Corriger ne suffit pas : il faut estimer le paramètre de la correction, et publier son
> incertitude.** Sans quoi l'on remplace un biais connu par un biais du même ordre, mais qui a
> l'air d'une correction.

## Ce que cela change pour le programme

La [recommandation 1 du mémorandum](memorandum.md) exigeait déjà une mesure consciente du rang.
Ce chantier en donne le **prix** — le coût d'engagement double — et une **grandeur de
contrôle** : l'écart entre la mesure aveugle et la mesure consciente du même fil, qui vaut zéro
pour une plateforme qui ne relègue pas.

Pour l'[évaluation contrefactuelle](evaluation.md), une quatrième exigence s'ajoute aux trois
déjà posées : **$\eta$ doit être estimé et son incertitude propagée**, et l'exploration du jeu
de données doit être vérifiée avant toute chose — c'est elle qui décide si l'estimation est
possible.

## Les hypothèses qui restent

La forme $e(R) = R^{-\eta}$ est **posée**, et seule sa sévérité est estimée. Un modèle d'examen
dépendant du contenu, ou de ce que le lecteur a déjà vu, donnerait des propensions différentes.

L'énumération exhaustive borne par ailleurs la taille des fils étudiés : huit positions sur
quatre points de vue. Rien n'assure que le comportement observé se transporte à un fil de
cinquante items, et l'affirmer demanderait une optimisation dont l'exactitude ne serait plus
garantie.

## Pistes ouvertes

1. **Vérifier que l'enterrement se transporte à grande échelle.** Au-delà de quelques dizaines
   de milliers de fils, il faudrait une optimisation approchée — dont il faudrait alors établir
   qu'elle n'invente pas le résultat.
2. **Enrichir le modèle d'examen** : les modèles à confiance ou à cascade font dépendre
   l'attention de ce que le lecteur a déjà consulté, non du seul rang.
3. **Mesurer l'exploration réelle d'un jeu de données public** avant d'en tirer quoi que ce
   soit : c'est elle qui décide si $\eta$ y est identifiable.
4. **Comparer à des lignes de base réglées** — MMR, réordonnancement aléatoire, popularité —
   qui reste la dette du programme d'évaluation.

---

*Implémentation : `ide.ranking`, `ide.offpolicy` · Notebook :
[15 — Rang adverse et sévérité](notebooks/15_rang_adverse_et_severite.ipynb) ·
[test adverse](gaming.md) · [rang et contrefactuel](evaluation.md) ·
[mémorandum](memorandum.md)*
