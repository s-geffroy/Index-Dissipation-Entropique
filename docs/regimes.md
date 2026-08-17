# Changements de régime : atteindre les désinformations qui s'installent

!!! success "La détection fonctionne, et couvre l'angle mort"
    **14 changements de régime** détectés sur le corpus, aux bonnes dates — l'affaire Benalla
    le 20 juillet 2018, les révélations Pegasus en juillet 2021, l'annonce de LIGO en février
    2016. Et surtout dans les sujets que la [calibration par pic](calibration.md) manquait :
    **QAnon, désinformation Covid-19, hésitation vaccinale**.

!!! failure "L'identification échoue"
    **0 des 14** livre des paramètres exploitables. La dispersion résiduelle médiane des
    séries réelles est de **0,63**, alors que l'incertitude relative sur
    $\gamma\alpha/\lambda$ atteint déjà 77 % à 0,15. Les paramètres sont **refusés** plutôt
    que rapportés avec une barre d'erreur illusoire.

!!! failure "Résultat infirmé depuis — l'écart de persistance ne se réplique pas"
    L'écart ×9,2 contre ×2,9 rapporté plus bas a été mis à l'épreuve sur
    [440 sujets dérivés de catégories](corpus-etendu.md) : il devient ×3,04 contre ×2,90,
    $p = 0{,}53$. C'était un **artefact de la sélection manuelle** des vingt-quatre sujets de
    ce corpus pilote, qui contenait les théories du complot les plus connues. La section
    correspondante est conservée telle quelle, avec cet avertissement.

!!! danger "Et une limite théorique domine les deux"
    L'identifiabilité de $\gamma\alpha/\lambda$ sur un changement de régime **dépend de la
    forme supposée de la saturation**. Sous saturation logistique, elle n'existe pas : deux
    triplets de rapports 5,0 et 1,7 produisent exactement la même courbe. Le rapport n'est
    donc pas une grandeur que les données déterminent.

---

## Le problème que la calibration par pic laissait ouvert

Onze des vingt-quatre sujets du corpus n'avaient produit aucun épisode exploitable — et
c'étaient les cas archétypaux. Leur attention ne forme pas un pic suivi d'une décroissance :
elle **change de niveau et s'installe**. Le niveau de fond glissant suit ce palier, et le
critère de proéminence n'est jamais franchi.

Un modèle de la polarisation qui ne mesure que les flambées passagères n'atteint pas son
objet.

## Pourquoi l'estimateur par pic ne se réutilise pas

L'identification par pic reposait sur deux pentes : montée à $\gamma\alpha - \lambda$,
décroissance à $\lambda$.

Dans un régime installé, **la décroissance n'existe pas**. Le système est à son point fixe,
où par définition $\gamma\alpha\,\sigma(V^*) = \lambda$ : le niveau du palier ne dit rien à
lui seul, et il n'y a pas de seconde pente.

L'information est dans la **forme de la transition**, qui traverse tout le domaine de la
saturation et contraint les trois paramètres à la fois.

## Une identification exacte, et sa fragilité

En posant $y = \dot W/W$ et $x = W^2$, un réarrangement **exact** de l'équation donne une
forme linéaire en trois coefficients :

$$y = A - B\,xy - C\,x
  \qquad A = \gamma\alpha - \lambda, \quad B = \frac{1}{W_{\text{sat}}^2},
  \quad C = \frac{\lambda}{W_{\text{sat}}^2}$$

d'où $\lambda = C/B$ et $\gamma\alpha/\lambda = 1 + AB/C$. La régression retrouve les trois
paramètres à la précision machine, y compris pour $\rho = 40$.

Elle est pourtant inutilisable telle quelle : $y$ apparaît à la fois comme réponse et dans le
régresseur $-xy$, et il faut le calculer en dérivant des données bruitées. À 10 % de bruit
multiplicatif, l'estimation de $\rho$ passait de 5,0 à 1,7.

**L'estimateur retenu n'utilise donc aucune dérivée** : il intègre l'équation et ajuste la
trajectoire en échelle logarithmique, la forme linéaire ne servant que d'initialisation.

L'ajustement porte sur la série **observée** $V = V_{\text{avant}} + W$, et non sur l'excédent
seul. La différence est décisive : au début de la transition, $W$ est une petite différence
entre deux grandeurs bruitées — or c'est précisément la phase qui contraint
$\gamma\alpha - \lambda$.

## La limite théorique

Sous la saturation du modèle, $\sigma = 1/(1+(W/W_{\text{sat}})^2)$, les trois paramètres
façonnent la courbe de trois manières distinctes et sont séparables.

Sous une saturation **logistique**, $\sigma = 1 - W/W_{\text{sat}}$, l'équation devient

$$\dot W = (\gamma\alpha - \lambda)\,W\left(1 - \frac{W}{K}\right),
  \qquad K = W_{\text{sat}}\left(1 - \frac{\lambda}{\gamma\alpha}\right)$$

La trajectoire ne dépend plus que de **deux** combinaisons des trois paramètres. Le rapport
y est structurellement non identifiable, et aucune précision de mesure n'y changera rien.

> **L'identifiabilité de $\gamma\alpha/\lambda$ sur un changement de régime n'est pas une
> propriété des données : c'est une hypothèse sur la forme de la saturation.**

Les deux formes sont donc ajustées côte à côte, et
`RegimeShift.is_form_identified` signale les cas où les données ne tranchent pas.

## Détection : ce qui fonctionne

Segmentation binaire sur les **logarithmes** — une audience évolue multiplicativement, un
doublement doit compter autant à mille qu'à cent mille consultations par jour. La coupure qui
réduit le plus le coût quadratique est retenue si elle dépasse une pénalité, ce qui évite de
fixer à l'avance un nombre de ruptures.

Trois validations avant de parler de changement de régime :

| Critère | Rôle |
|---|---|
| **maintien** sur 180 jours | c'est ce qui sépare un régime d'un pic : un pic retombe |
| **élévation** d'au moins ×2 | un déplacement de niveau, non une fluctuation |
| **ancien régime** ≥ 50 vues/jour | il faut un régime antérieur pour qu'il y ait changement ; une série passant de 2 à 300 consultations décrit un article qui vient d'être rédigé |

Trois autres précautions se sont révélées nécessaires à l'usage :

* la **périodicité hebdomadaire** est retirée d'abord. C'est un effet systématique de 20 à
  30 % d'amplitude, et la dispersion résiduelle pilote directement l'incertitude ;
* la **position de la rupture n'est pas fiable** pour délimiter la fenêtre d'ajustement : une
  segmentation en moyenne place la rupture vers le milieu d'une montée graduelle. Le
  décollage est donc localisé séparément, au premier franchissement durable de 5 % de
  l'élévation ;
* une montée graduelle est **découpée en escalier** par la segmentation. Les ruptures d'un
  même escalier décrivent un seul changement de régime et sont dédupliquées.

## Résultats

![Détection de changement de régime sur des séries de consultation publiques](figures/fig10_regimes.png)

/// caption
QAnon et ses deux basculements datés ; la démonstration de non-identifiabilité sous
saturation logistique ; la persistance par registre émotionnel ; et la position des séries
réelles vis-à-vis de la précision atteignable. Figure régénérée par
[le notebook 10](notebooks/10_changement_de_regime.ipynb).
///

### Les dates sont les bonnes

C'est la validation la plus parlante : sans qu'aucune date ne lui soit fournie, la détection
retrouve des événements datables.

| Sujet | Date détectée | Événement | Élévation |
|---|---|---|---|
| QAnon | 31 mars 2018 | émergence du mouvement | ×44 |
| Pizzagate | 16 mars 2020 | reprise pandémique | ×18 |
| Gilets jaunes | 3 mai 2019 | — | ×14 |
| QAnon | 9 mars 2020 | bascule pandémique | ×12 |
| Pegasus | 17 juillet 2021 | révélations du *Pegasus Project* | ×4,4 |
| Affaire Benalla | 20 juillet 2018 | révélation de l'affaire | ×2,8 |
| OSIRIS-REx | 12 juin 2016 | — | ×3,3 |
| LIGO | 9 janvier 2016 | fuites précédant l'annonce | ×3,2 |
| Télescope James-Webb | 27 septembre 2021 | approche du lancement | ×2,9 |
| Ondes gravitationnelles | 1ᵉʳ février 2016 | annonce de la détection | ×2,7 |
| Event Horizon Telescope | 1ᵉʳ avril 2019 | première image d'un trou noir | ×2,4 |

Aucun faux positif sur bruit stationnaire, aucun pic accepté, aucune création d'article
retenue.

### Un écart entre registres, pour la première fois du projet

La [calibration par pic](calibration.md) ne trouvait **aucune** différence entre contenus
d'accusation et annonces scientifiques : le rapport d'amplification était indiscernable, et
l'estimation ponctuelle allait même en sens contraire à la prédiction.

La **persistance** dit autre chose :

| Registre | n | élévation médiane | IQR |
|---|---|---|---|
| accusation | 8 | **×9,2** | [4,0 ; 14,9] |
| découverte | 6 | **×2,9** | [2,7 ; 3,2] |

Mann-Whitney : $p = 0{,}081$.

Ce n'est pas concluant — quatorze observations, seuil non franchi — et une réserve
supplémentaire s'impose : les changements du registre « découverte » se situent tous juste
au-dessus du seuil de détection (×2,4 à ×3,3), ce qui suggère que certains sont des pics à
décroissance lente plutôt que de véritables régimes.

Mais la direction est celle que le modèle prédit, l'écart est net, et il porte sur une
grandeur que le projet n'avait pas encore mesurée :

> **Ce n'est pas le taux d'amplification qui distingue les registres émotionnels, c'est la
> durée pendant laquelle l'attention reste captée.**

!!! failure "Cette conclusion est infirmée"
    Sur [440 sujets](corpus-etendu.md), l'écart devient ×3,04 contre ×2,90 ($p = 0{,}53$). La
    formulation ci-dessus est conservée pour mémoire : elle illustre ce qu'une sélection
    manuelle de vingt-quatre sujets peut faire croire.

### L'identification échoue, et pourquoi

Zéro des quatorze changements ne livre de paramètres exploitables.

Ce n'est pas un défaut de l'implémentation : la récupération est **exacte** sur trajectoire
propre, y compris pour $\rho = 40$. C'est une inadéquation entre un modèle à trois paramètres
et le bruit réel des séries d'attention, qui portent des bosses médiatiques successives
superposées à la tendance.

| dispersion résiduelle | incertitude relative sur $\rho$ |
|---|---|
| 0,05 | 24 % |
| 0,10 | 53 % |
| 0,15 — *seuil d'acceptation* | 77 % |
| 0,25 | 135 % |
| **0,63 — séries réelles** | hors de portée |

Le refus est un choix explicite. Une version antérieure du module tolérait une dispersion de
0,30 et produisait des valeurs comme $\lambda = 4{,}4$ par jour — une mémoire collective de
cinq heures — ou $\rho = 139$. Ces chiffres avaient l'apparence de résultats.

## Ce que cela change pour le mémorandum

La [recommandation 2](memorandum.md) plafonnait $\gamma\alpha/\lambda$. Cette formulation
supposait le rapport mesurable. Il ne l'est ni sur les régimes installés, ni indépendamment
d'une hypothèse de forme de saturation.

En revanche, **deux grandeurs se mesurent bien** : la date du basculement et l'élévation du
palier. Un cadre réglementaire adossé à celles-ci serait opposable, là où un seuil sur $\rho$
ne l'est pas — et il porterait sur ce que le régulateur cherche réellement à constater : non la
vitesse d'un emballement, mais la **durée pendant laquelle une fausse croyance reste
installée**.

Elles **ne distinguent pas** les registres émotionnels pour autant : la vérification sur
[440 sujets](corpus-etendu.md) l'a établi. Ce sont des instruments de constat, non la preuve
d'un mécanisme.

## Pistes ouvertes

1. **Réduire le modèle plutôt que d'améliorer l'ajustement.** Deux paramètres identifiables
   sans hypothèse de forme — taux de croissance initial et niveau du palier — valent mieux
   que trois dont un n'est pas déterminé par les données.
2. **Un observable moins bruité.** La dispersion des consultations quotidiennes est
   irréductible ; des séries hebdomadaires, ou une mesure d'exposition plutôt que de
   consultation, changeraient l'ordre de grandeur.
3. **Étendre le corpus à la persistance.** L'écart ×9,2 contre ×2,9 mérite d'être testé sur
   plusieurs centaines de sujets pré-enregistrés : c'est le seul résultat du projet qui
   distingue les registres émotionnels, et il est à $p = 0{,}08$.
4. **Vérifier que les régimes « découverte » sont bien des régimes** en allongeant la durée
   de maintien exigée.

---

*Implémentation : `ide.regime` · Notebook :
[10 — Changement de régime](notebooks/10_changement_de_regime.ipynb) ·
[calibration par pic](calibration.md) · [feuille de route](feuille-de-route.md)*
