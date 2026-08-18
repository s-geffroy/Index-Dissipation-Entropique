# Rang et contrefactuel : deux corrections avant toute évaluation

!!! failure "Un quatrième adversaire : se conformer en enterrant"
    À composition **rigoureusement identique**, déplacer les contenus divergents vers le bas du
    fil rapporte **10 % d'engagement** et fait passer la divergence de 0,525 à 0,630. Aucune
    des mesures retenues jusqu'ici ne le voyait : elles ne regardent que la composition, jamais
    l'ordre.

!!! failure "L'évaluation naïve d'un réordonnancement se trompe de 201 % en médiane"
    Sur soixante jeux de contenus, l'estimation naïve du coût d'un filtre de diversité s'écarte
    de la valeur vraie de **201 % en médiane** et jusqu'à **851 %**. Elle surestime le coût dans
    56 cas sur 60 — mais le sous-estime dans les 4 autres. **Un chiffre naïf n'est pas une borne
    supérieure.**

!!! success "Les deux corrections existent, et elles sont peu coûteuses"
    La **remise de rang** de [RADio](https://arxiv.org/abs/2209.13520) ferme l'échappatoire de
    l'enterrement. Les **estimateurs contrefactuels** retrouvent la valeur vraie à moins d'un
    point. Ce ne sont pas des raffinements à apporter après l'évaluation sur données réelles :
    ce sont eux qui décident si cette évaluation mesurera quoi que ce soit.

---

## Pourquoi ces deux corrections viennent maintenant

Le [test adverse](gaming.md) a corrigé deux fois la définition de l'index : mesurer les
**contenus** et non les étiquettes, puis ne pas mesurer par l'entropie de Rao, qui prescrivait
la polarisation. Le mouvement suivant annoncé par la [feuille de route](feuille-de-route.md)
est l'évaluation de l'[ADE](ade.md) sur un jeu de données public de recommandation.

Deux hypothèses portaient encore ce programme, implicites l'une et l'autre :

1. **que la position d'un contenu dans le fil ne compte pas** ;
2. **qu'un fil enregistré puisse servir à évaluer un filtre qui ne l'a pas produit**.

Elles sont fausses toutes les deux, et la seconde invaliderait le résultat principal du
chantier suivant.

## 1. L'enterrement

Un lecteur consulte le premier élément d'un fil bien plus souvent que le huitième. Une
plateforme tenue à un plancher de diversité peut donc s'y conformer en plaçant les contenus
divergents **en bas** — sans rien changer à la composition de son fil.

| Fil de huit positions | Composition | Entropie de position | Divergence consciente du rang | Engagement |
|---|---|---|---|---|
| diversité remontée | [5, 1, 1, 1] | 0,774 | **0,525** | 1,934 |
| diversité enterrée | [5, 1, 1, 1] | 0,774 | **0,630** | **2,118** |

Même multiensemble, même entropie de position — et **10 % d'engagement en plus**. Une norme
aveugle au rang offre ce gain gratuitement.

![Rang et contrefactuel](figures/fig14_rang_et_contrefactuel.png)

/// caption
L'enterrement à composition constante ; l'effet de la remise de rang selon sa forme, la courbe
sans remise étant plate par construction ; les estimateurs contre la valeur vraie ; et la
distribution des erreurs du replay sur soixante jeux de contenus. Figure régénérée par
[le notebook 14](notebooks/14_rang_et_contrefactuel.ipynb).
///

### La remise de rang

RADio pondère chaque position par l'attention qu'elle reçoit :

$$Q^*(x) = \frac{\sum_i w_{R_i}\,\mathbb{1}[i \in x]}{\sum_i w_{R_i}}
  \qquad w_{R_i} = \frac{1}{R_i}$$

Le second panneau de la figure le montre au plus court : à composition fixe, faire glisser le
bloc divergent du haut vers le bas du fil laisse la mesure **sans remise parfaitement plate**,
tandis que les mesures escomptées montent de 0,29 à 0,68. **La conscience du rang est
exactement ce qui ferme cette échappatoire.**

Le choix de la remise — réciproque $1/R$ ou logarithmique $1/\log_2(R+1)$ — déplace le
résultat, et doit donc être publié avec lui.

## 2. La référence déclarée

Le second apport de RADio importe autant que le premier, et il répond au défaut de principe
relevé par le [test adverse](gaming.md) : l'entropie suppose que l'uniforme est l'idéal,
l'entropie de Rao suppose que l'écartement l'est, et aucune ne le dit.

Les cinq mesures de RADio sont **la même divergence** appliquée à des paires de distributions
différentes. Ce qui les distingue est le choix de la **référence**, et c'est lui qui porte la
valeur normative :

| Mesure | Distribution servie | Référence |
|---|---|---|
| calibration | catégories du fil | historique de lecture du lecteur |
| fragmentation | fil d'un lecteur | fil d'un autre lecteur |
| activation | intensité affective du fil | intensité dans l'offre |
| représentation | points de vue du fil | points de vue dans l'offre |
| voix alternatives | voix minoritaires du fil | voix minoritaires dans l'offre |

**Le sens souhaitable de l'écart n'est pas donné par les mathématiques.** Une calibration de
0,013 décrit un fil parfaitement conforme à ce que le lecteur lisait déjà : c'est l'objectif
d'un recommandeur libéral et la définition d'une bulle pour un recommandeur délibératif. La
divergence mesure ; elle ne tranche pas — et c'est ce qu'elle a de mieux à offrir à un
régulateur, qui doit alors déclarer ce qu'il vise au lieu de le cacher dans le choix d'une
formule.

## 3. Le piège de l'évaluation hors ligne

Réordonner des fils enregistrés et mesurer la perte de pertinence : c'est ce que le programme
annonçait, et cette mesure est fausse.

Les clics enregistrés n'ont pas été produits par le filtre qu'on évalue. Un clic dépend de la
pertinence du contenu **et** de l'exposition qu'on lui a donnée. Un article que la plateforme
avait enterré a peu de clics — non parce qu'il n'intéressait personne, mais parce que personne
ne l'a vu. Et un filtre de diversité fait précisément remonter ces articles-là.

### Ce que mesure chaque estimateur

| Estimateur | Coût estimé | Écart à la vérité |
|---|---|---|
| **coût réel** (connu ici, jamais sur données réelles) | **6,6 %** | — |
| replay naïf | 5,0 % | −24 % |
| IPS | 6,6 % | −0,0 % |
| SNIPS | 6,6 % | −0,1 % |
| IPS plafonné à 5 | 6,6 % | −0,0 % |

Le **replay** est l'estimateur réellement employé : on réordonne les candidats, puis on somme
les clics observés pondérés par l'exposition que le nouveau classement leur donnerait. Son
biais est structurel — le taux de clic observé porte déjà l'exposition accordée par la
plateforme, si bien que l'estimateur **l'applique deux fois**.

### L'ampleur, et le sens

Sur soixante jeux de contenus tirés à configuration identique :

| | |
|---|---|
| erreur relative médiane du replay | **201 %** |
| pire cas | **+851 %** |
| surestime le coût | 56/60 |
| le sous-estime | 4/60 |

On aimerait pouvoir dire que le biais est conservateur — qu'il surestime toujours le coût, et
qu'un résultat favorable obtenu naïvement resterait donc défendable. **Il ne l'est pas.** Le
sens dépend du jeu de contenus, c'est-à-dire de données qu'on ne choisit pas.

> **Un chiffre naïf n'est pas une borne supérieure. C'est un chiffre faux d'un montant
> considérable et d'un sens que rien ne garantit.**

## 4. Ce qu'il faut publier à côté du chiffre

Un estimateur sans biais ne suffit pas. Trois grandeurs doivent accompagner tout résultat
contrefactuel, faute de quoi il n'est ni interprétable ni reproductible.

**Le modèle de propension.** Tout repose sur la connaissance de la politique qui a produit les
données. Sur un jeu public, elle n'est pas fournie : il faut la **modéliser**, typiquement par
un biais de position $e(R) = R^{-\eta}$. C'est une hypothèse, pas une mesure.

**La taille d'échantillon effective.** Plus la politique évaluée s'éloigne de celle qui a
produit les données, moins il reste d'observations pour l'estimer :

| Agressivité du réordonnancement | Taille effective (sur 60 000) |
|---|---|
| nulle | 60 000 |
| modérée | 47 660 |
| forte | **10 026** |

Une estimation sans biais adossée à quelques centaines d'observations effectives n'est pas une
mesure, c'est un chiffre.

**Le plafond, s'il y en a un.** Son choix suffit à déplacer l'estimation — de −6,5 % à
plafond 1,2, à −0,0 % sans plafond — et sans lui le résultat n'est pas reproductible.

## Ce que cela change pour le programme

L'évaluation de l'ADE sur données réelles n'est pas abandonnée : elle est **conditionnée**.

1. la diversité s'y mesure **par une divergence consciente du rang** à une référence déclarée,
   non par une valeur ponctuelle sur la composition du fil ;
2. le coût en pertinence s'y estime **par IPS ou SNIPS**, jamais par replay ;
3. le modèle de propension, la taille effective et le plafond sont **publiés avec le chiffre**.

Sans ces trois conditions, la frontière de compromis annoncée mesurerait surtout le biais de
position de la plateforme qui a produit les données.

## Les hypothèses qui restent

Le modèle de biais de position — l'exposition ne dépend que du rang — est une **hypothèse**.
Tout ce qui précède déplace donc le problème d'un cran, de « les clics sont des étiquettes »
vers « l'exposition se modélise par le rang ». Le second énoncé est bien meilleur que le
premier, et il reste un énoncé.

Trois des cinq références de RADio demandent en outre des attributs que ce dépôt n'a pas —
scores d'affect, annotations de points de vue, codage des minorités. Le
[corpus étendu](corpus-etendu.md) a montré ce qu'il en coûte de prendre une étiquette
disponible pour l'attribut qu'on voudrait mesurer.

## Pistes ouvertes

1. **Estimer la sévérité du biais de position** plutôt que la poser. Les méthodes
   d'*intervention harvesting* et les modèles de position par maximum de vraisemblance
   l'estiment à partir des données enregistrées elles-mêmes.
2. **Reprendre le test adverse sous mesure consciente du rang.** Les quatre mesures comparées
   au [notebook 13](notebooks/13_test_adverse_index.ipynb) l'ont été sans rang ; l'enterrement
   les concerne toutes.
3. **Comparer à des lignes de base réglées** — MMR, réordonnancement aléatoire, popularité — et
   non au seul filtre d'engagement pur, qui est un homme de paille.
4. **Instancier les cinq références sur données réelles**, ce qui suppose de résoudre d'abord le
   problème d'étiquetage que le corpus étendu a documenté.

---

*Implémentation : `ide.radio`, `ide.offpolicy` · Notebook :
[14 — Rang et contrefactuel](notebooks/14_rang_et_contrefactuel.ipynb) ·
[test adverse](gaming.md) · [ADE](ade.md) · [feuille de route](feuille-de-route.md)*
