# Fokker-Planck : le paysage de l'opinion publique

## Passer de l'individu à la distribution

Suivre un million d'individus est impossible ; suivre la **densité de probabilité** de
l'opinion collective ne l'est pas. C'est ce que fait l'équation de Fokker-Planck,
appliquée à la variable macroscopique $x \in [-1, 1]$ — le taux d'adhésion à une idée :

$$\frac{\partial P(x,t)}{\partial t} = -\frac{\partial}{\partial x}\big[A(x)P(x,t)\big] + \frac{\partial^2}{\partial x^2}\big[B(x)P(x,t)\big]$$

Deux forces antagonistes :

* la **dérive** $A(x)$ — déterministe : conformisme et champ médiatique ;
* la **diffusion** $B(x)$ — stochastique : bruit, agitation, hasard individuel.

Le parallèle avec l'équation de Schrödinger est structurel : dans les deux cas, la
forme du **potentiel** dicte la forme de la fonction de probabilité stationnaire. Un
potentiel à double puits produit, en physique quantique, des états stationnaires
localisés au fond de chaque puits ; en dynamique d'opinion, deux blocs polarisés.

## La dérive : ce que le raisonnement d'origine avait omis

Le fil posait $V(x) = -\frac{J}{2}x^2 - Hx$, d'où $A(x) = Jx + H$.

Cette formulation ne peut produire **aucune transition de phase** :
$\exp(NJx^2/2T)$ est convexe, donc maximale aux extrêmes à *toute* température. Le
modèle prédirait une société éternellement polarisée, y compris à température infinie.

Le terme manquant est l'**entropie de mélange** — le nombre de configurations
individuelles compatibles avec une opinion moyenne $x$. En l'ajoutant, on retrouve
exactement l'énergie libre de Helmholtz $F = E - TS$ que le fil invoquait par
ailleurs :

$$f(x) = \underbrace{-\frac{J}{2}x^2 - Hx}_{\text{énergie } E} + T\underbrace{\left[\frac{1+x}{2}\ln\frac{1+x}{2} + \frac{1-x}{2}\ln\frac{1-x}{2}\right]}_{-\,\text{entropie } S}$$

$$\boxed{A(x) = -f'(x) = Jx + H - T\,\mathrm{artanh}(x)}$$

Trois forces s'y superposent :

* $Jx$ — le conformisme, qui amplifie la majorité existante ;
* $H$ — le champ médiatique, qui pousse dans une direction imposée ;
* $-T\,\mathrm{artanh}(x)$ — le rappel entropique, qui ramène vers la modération et
  diverge aux opinions unanimes.

Ce dernier terme borne la dynamique dans $(-1,1)$ et fait apparaître une vraie
température critique de champ moyen $T_c = J$. La formulation du fil en est la
linéarisation au voisinage de $x = 0$ — incomplète précisément là où se joue le
phénomène. → [audit, point 4](../limites.md)

## La diffusion : ce qu'une grande population fait réellement

$$B(x) = \frac{k_B T (1 - x^2)}{N}$$

Le facteur $(1-x^2)$ éteint le bruit à l'unanimité : il n'y a plus de désaccord à
échantillonner.

Le facteur $1/N$ dit quelque chose de **contraire au récit initial** : plus la
population est grande, plus le bruit de sa variable macroscopique est faible. C'est la
loi des grands nombres.

Il n'y a pas de contradiction, mais deux échelles qu'il faut cesser de confondre :

| Grandeur | Comportement en $N$ | Ce qu'elle décrit |
|---|---|---|
| entropie de configuration totale | croît (extensive) | le nombre de façons d'être en désaccord |
| fluctuations de la moyenne $x$ | décroît en $1/N$ | la stabilité du taux d'adhésion observé |

D'où la reformulation retenue :

> **Une grande population ne devient pas bruyante, elle devient rigide.** Sa taille ne
> l'agite pas, elle la prive de plasticité stochastique — et c'est cette rigidité qui
> rend la polarisation irréversible : un système sans bruit ne peut plus quitter le
> puits où il est tombé.

Cette version est plus forte que l'originale : elle explique l'irréversibilité.
→ [audit, point 3](../limites.md)

## Les trois régimes de l'opinion publique

La distribution d'équilibre s'écrit sous forme de grandes déviations :

$$P_{\text{stat}}(x) \propto \exp\!\left(-\frac{N f(x)}{T}\right)$$

Le facteur $N$ rend la pénalité d'autant plus sévère que la population est grande.
Trois formes, obtenues en changeant deux paramètres :

| Régime | Conditions | Paysage | Société |
|---|---|---|---|
| **Fluide** | $T > T_c$ | un puits centré | débat vivant, modération majoritaire |
| **Polarisé** | $T < T_c$, $H = 0$ | deux puits symétriques | deux blocs d'égale force |
| **Manipulé** | $T < T_c$, $H > 0$ | deux puits inclinés | faux consensus imposé par le champ |

Le « faux consensus » n'est pas une hypothèse ajoutée : c'est le puits incliné. Et la
densité de modérés s'effondre **exponentiellement** avec $N$ — dans une grande
population sous $T_c$, la modération n'est pas minoritaire, elle est
*statistiquement inaccessible*.

## Franchir la barrière

Comment une opinion passe-t-elle d'un bloc à l'autre sans traverser la modération ?

Le fil parlait d'un « effet tunnel social ». L'effet tunnel étant strictement
quantique, le mécanisme correct est le **franchissement de barrière par activation
thermique**, décrit par la formule de Kramers, dont le taux varie comme
$e^{-\Delta V / k_B T}$.

On perd une image séduisante, on gagne une prédiction : la loi de Kramers donne une
dépendance en température que l'effet tunnel ne donne pas.
→ [audit, point 9](../limites.md)

## Note numérique

Le solveur est écrit en **volumes finis à flux nul aux bords** : chaque cellule
n'échange qu'avec ses voisines, et la masse de probabilité est conservée exactement, à
la précision machine près. Cela permet de distinguer un vrai effondrement de la
modération d'une fuite numérique.

L'advection est **décentrée amont**. Une interpolation centrée serait plus précise sur
le papier, mais elle est inconditionnellement instable dès que le nombre de Péclet de
maille dépasse 2 — ce qui est le régime normal ici, la diffusion étant en $1/N$.

---

*Implémentation : `ide.fokker_planck` · Notebook :
[04 — Fokker-Planck](../notebooks/04_fokker_planck_paysage.ipynb)*
