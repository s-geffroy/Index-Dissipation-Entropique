# Entropie : de von Neumann à Shannon

## Ce que l'entropie mesure vraiment

L'analogie du projet repose sur une affirmation qu'il faut énoncer avec précision,
parce qu'une version approximative la ferait écarter d'emblée :

> Ce n'est pas la **multiplicité** des possibilités qui produit de l'entropie, c'est
> la **perte de cohérence** entre elles.

Un chat de Schrödinger à la fois mort et vivant est dans un état **pur**. Son
entropie de von Neumann est rigoureusement nulle. De même, une population où chacun
garde plusieurs opinions ouvertes n'est pas encore désordonnée : elle est disponible.

Le désordre naît du **contact avec un environnement** qui fixe les positions.

!!! failure "Le parallèle ci-dessous est un échafaudage, et il n'a pas tenu"
    Le rapprochement entre entropie de von Neumann et entropie de Shannon a produit l'index —
    c'est son mérite. Mais les affirmations propres de l'analogie ont été **réfutées une à
    une** : l'entropie globale ne croît pas sous décohérence (c'est celle du sous-système
    réduit), l'entropie de configuration et le bruit de la variable macroscopique varient en
    sens contraires avec $N$, et $\tau_D \propto \tau_R/N$ n'est pas le résultat de Zurek.
    Ce qui subsiste du formalisme est **classique**. → [audit critique](../limites.md)

## Les deux entropies

### Von Neumann : la pureté d'un état quantique

$$S(\rho) = -\mathrm{Tr}(\rho \ln \rho)$$

où $\rho$ est la matrice de densité. Cette quantité vaut $0$ pour un état pur, et
$\ln d$ pour le mélange maximal en dimension $d$.

Le calcul se fait par diagonalisation : les valeurs propres de $\rho$ forment une
distribution classique, à laquelle on applique l'entropie de Shannon. C'est le sens
physique de la quantité — **l'entropie de von Neumann est l'entropie de Shannon du
mélange statistique révélé par la base propre.** C'est ce qui autorise le pont entre
les deux disciplines : elles mesurent la même chose.

### Shannon : la dispersion d'une distribution d'opinions

$$H(X) = -\sum_i p_i \log_2 p_i$$

Nulle pour une opinion unanime, maximale ($\log_2 k$) pour une population
équitablement répartie sur $k$ points de vue.

### Une précision qui protège l'argument

Le fil de travail d'origine écrivait « l'entropie de von Neumann a bondi de $0$ à une
valeur positive ». L'évolution d'un système quantique **fermé** étant unitaire, son
entropie est en réalité constante. Ce qui croît est l'entropie du **sous-système
réduit**, obtenue en traçant sur les degrés de liberté de l'environnement.
L'information n'est pas détruite : elle est délocalisée dans les corrélations
système-environnement.

La correction n'est pas un détail de vocabulaire — sans elle, un physicien écarte
l'analogie en une phrase. → [audit, point 8](../limites.md)

## Le parallèle, terme à terme

| | Physique quantique | Dynamique d'opinion |
|---|---|---|
| État initial | état pur $\lvert\psi\rangle$, $S = 0$ | accord unanime, $H = 0$ |
| Ce qui détruit l'ordre | intrication avec l'environnement | confrontation aux autres |
| Grandeur qui croît | $S(\rho_{\text{réduit}})$ | $H(X)$ |
| État final | matrice diagonale, mélange statistique | distribution dispersée, polarisation |

## De l'entropie à un index

L'entropie de Shannon brute ne se compare pas d'une plateforme à l'autre : sa valeur
dépend du nombre de modalités disponibles. L'**IDE** la normalise :

$$\mathrm{IDE} = \frac{H(q)}{\log_2 k}$$

Cette normalisation est ce qui en fait un instrument réglementaire — un seuil exprimé
en pourcentage a un sens, un seuil exprimé en bits n'en a pas.

!!! danger "Mais la distribution sur laquelle porte $H$ n'est pas celle qu'on écrirait d'abord"
    Deux attaques ont réussi contre la version naïve, et chacune a imposé une correction :
    $q$ porte sur les **contenus servis** projetés sur le catalogue déclaré — non sur leurs
    étiquettes, qu'une plateforme choisit — et chaque rang y est pondéré par l'**attention**
    qu'il reçoit, faute de quoi la norme se satisfait en enterrant les contenus divergents.
    → [IDE](../ide.md) · [test adverse](../gaming.md) · [rang adverse](../rang-adverse.md)

## Un avertissement d'échelle

L'entropie mesurée par l'IDE porte sur la **distribution des opinions exposées à un
individu**, non sur l'entropie de configuration de la population entière. Ces deux
quantités évoluent en sens contraire quand la taille du système augmente, et les
confondre est l'erreur la plus lourde du raisonnement d'origine.
→ [audit, point 3](../limites.md)

---

*Implémentation : `ide.entropy` · Notebook :
[01 — Entropie et pureté](../notebooks/01_entropie_et_purete.ipynb)*
