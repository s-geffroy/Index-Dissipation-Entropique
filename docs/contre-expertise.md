# Contre-expertise : ce que la littérature reproche à ce travail

!!! failure "Une conclusion retirée : « la proximité à la cible résiste le mieux »"
    Publiée deux fois, elle est un **artefact d'échelle**. Comparer deux mesures de diversité au
    même plancher nominal n'a pas de sens — elles ne vivent pas sur la même échelle. À diversité
    **réellement exposée** égale, les deux mesures coûtent la même chose, à moins de 0,6 % de la
    borne exacte.

!!! danger "Une conclusion restreinte : « certifiée à 0,70, elle expose 0,36 »"
    Ce chiffre vaut pour une remise d'attention en $1/R$, soit $\eta = 1$. Or ce dépôt a lui-même
    mesuré que $\eta$ est une propriété de la **surface** : à $\eta = 0{,}1$ — le bandeau de trois
    vignettes — l'enterrement **disparaît** (0,747 exposé pour 0,774 affiché) ; à $\eta = 2$ il
    empire (0,157). La remise doit être **mesurée**, pas conventionnelle.

!!! warning "Une incertitude élargie : le biais de confiance"
    Le modèle de clic du dépôt est multiplicatif ; la littérature en documente un **affine**, où
    le lecteur clique par confiance sur des contenus non pertinents en tête de fil. Sous ce
    modèle, l'estimateur surestime la sévérité de **+12,8 %** — et son erreur type, 0,013, ne le
    voit pas.

!!! success "Une recommandation confirmée : l'exploration ne se remplace pas"
    L'estimateur doublement robuste fait **moins bien** que l'IPS simple sur données réelles
    (−4,9 % contre +2,5 %), et la taille d'échantillon effective ne bouge pas : elle ne dépend
    que des poids d'importance. Aucun estimateur ne fabrique de l'exploration.

---

## Pourquoi cette page

Les chapitres précédents ont attaqué l'index, la norme, les jeux de données et l'algorithme. Ils
n'avaient jamais attaqué **les instruments de mesure eux-mêmes**, ni confronté les choix du dépôt
à ce que la littérature du domaine sait déjà.

Cinq contre-épreuves, dont une invalide une conclusion publiée.

![Contre-expertise](figures/fig20_contre_expertise.png)

/// caption
L'enterrement selon la sévérité de l'attention ; le prix des deux normes selon la même
sévérité ; les deux mesures comparées à diversité exposée égale ; et la dérive de l'estimateur
sous biais de confiance. Figure régénérée par
[le notebook 20](notebooks/20_contre_expertise.ipynb).
///

## 1. La remise $1/R$ est une convention, pas une mesure

| Sévérité $\eta$ | Surface | Affiché | Exposé | Coût aveugle | Coût conscient |
|---|---|---|---|---|---|
| 0,1 | bandeau de 3 vignettes | 0,774 | **0,747** | 24,1 % | 24,1 % |
| 0,5 | intermédiaire | 0,774 | 0,620 | 17,7 % | 21,1 % |
| 1,0 | convention MRR | 0,774 | 0,443 | 10,7 % | 20,9 % |
| 1,1 | page de résultats | 0,774 | 0,408 | 9,5 % | 20,9 % |
| 2,0 | fil très top-lourd | 0,774 | **0,157** | 2,7 % | 20,8 % |

**L'enterrement n'existe que si l'attention est concentrée.** À attention presque plate, une
norme aveugle au rang suffit et la norme consciente du rang ne coûte pas un point de plus. À
attention très concentrée, enterrer devient presque gratuit — 2,7 % — donc irrésistible.

Le prix de la norme **consciente du rang**, lui, ne bouge pas : 20,8 à 24,1 % quelle que soit la
surface. C'est la seule grandeur stable du tableau.

**Conséquence réglementaire.** Le régulateur ne peut pas fixer une remise unique. La remise
d'attention fait partie de ce qui doit être **mesuré sur la surface**, au même titre que le rang
servi doit être enregistré. → [demande au titre de l'article 40](article-40.md)

## 2. Comparer deux mesures au même plancher n'a pas de sens

Le [rang adverse](rang-adverse.md) a comparé quatre mesures **au même plancher de 0,70** et
conclu que la proximité à la cible résistait le mieux. La comparaison honnête fixe la diversité
**réellement exposée** et demande à chaque mesure ce qu'elle coûte pour l'obtenir.

| Mesure | Plancher | Entropie exposée | Coût | Coût optimal |
|---|---|---|---|---|
| entropie de position | 0,60 | 0,605 | 16,4 % | 16,4 % |
| proximité à la cible | 0,80 | 0,591 | 15,8 % | 15,7 % |
| entropie de position | 0,70 | 0,702 | 20,9 % | 20,8 % |
| proximité à la cible | 0,90 | 0,792 | 25,9 % | 25,5 % |

À diversité exposée comparable, les coûts le sont aussi, et les deux mesures se tiennent sur la
borne exacte. **La proximité à la cible ne résiste pas mieux : elle est moins exigeante au même
chiffre.**

Ce qui compte n'est donc pas le choix de la mesure mais le **niveau** exigé et la **conscience du
rang**. Le dépôt avait pourtant appliqué la bonne méthode ailleurs — les
[lignes de base](lignes-de-base.md) fixent le plancher précisément pour rendre les méthodes
comparables — et ne l'avait pas appliquée à ses propres mesures.

## 3. Le biais de confiance, que l'estimateur ignore

La littérature de l'apprentissage de classement non biaisé documente un modèle **affine** plutôt
que multiplicatif (Vardasbi, Oosterhuis & de Rijke, 2020) :

$$P(\text{clic} \mid k, \gamma) = \theta_k\big(\varepsilon^+_k\,\gamma
+ \varepsilon^-_k\,(1-\gamma)\big) = \alpha_k \gamma + \beta_k$$

Les mêmes auteurs démontrent qu'une pondération par l'inverse de la propension **ne peut pas**
corriger un biais affine : une transformation linéaire ne corrige pas une transformation affine.

| $\varepsilon^-$ | $\hat\eta$ | Erreur type | Erreur |
|---|---|---|---|
| 0,00 | 1,011 | 0,010 | +1,1 % |
| 0,05 | 1,045 | 0,010 | +4,5 % |
| 0,10 | 1,076 | 0,011 | +7,6 % |
| 0,20 | **1,128** | 0,013 | **+12,8 %** |

Deux nuances, dans les deux sens : c'est **beaucoup moins grave** que de poser $\eta$ au jugé,
qui coûte jusqu'à +179 % ; mais l'intervalle publié est **trop étroit**, et l'incertitude réelle
inclut une part de misspécification que l'erreur type n'estime pas.

Un détail technique explique pourquoi l'estimateur s'en tire si bien : un biais de confiance
**indépendant du rang** ne le dérange pas — la transformation reste séparable et l'effet fixe de
contenu l'absorbe entièrement. Seule la **dépendance au rang** de la confiance le biaise.

## 4. Le doublement robuste ne sauve pas la taille effective

| Estimateur | Valeur | Écart à la vérité |
|---|---|---|
| naïf | 0,006743 | +31,6 % |
| **IPS** | 0,005253 | **+2,5 %** |
| auto-normalisé | 0,004768 | −7,0 % |
| IPS plafonné à 100 | 0,005238 | +2,2 % |
| **doublement robuste** | 0,004871 | **−4,9 %** |

Le doublement robuste fait moins bien que l'IPS simple : son modèle de récompense, estimé sur le
seau d'enregistrement, hérite du biais qu'on cherchait à corriger. Et la taille d'échantillon
effective — 1 513 sur 4 077 727 — **ne change pas** : elle ne dépend que de la distribution des
poids d'importance, c'est-à-dire de la distance entre les deux politiques.

**Le problème est structurel.** La recommandation du [mémorandum](memorandum.md) tient : il faut
exiger une fraction d'exploration, pas un meilleur estimateur.

## 5. Lire l'indice en nombre effectif de points de vue

Une entropie normalisée n'est pas une diversité : elle n'est pas linéaire en ce qu'on entend par
« deux fois plus divers ». Sa conversion en **nombre effectif** l'est (Jost, 2006).

| Indice | Points de vue effectifs (sur 4) | Lecture |
|---|---|---|
| 0,774 | 2,92 | affiché par le fil enterrant |
| 0,700 | **2,64** | plancher réglementaire proposé |
| 0,443 | **1,85** | réellement exposé à $\eta = 1$ |
| 0,157 | 1,24 | réellement exposé à $\eta = 2$ |

« Certifiée à 2,6 points de vue effectifs sur 4, elle en expose 1,9 » se comprend sans
formation ; « certifiée à 0,70, elle expose 0,44 » ne se comprend pas.

## 6. Ce que la littérature ajoute, et que la mesure ne dit pas

**Corriger le biais de position n'améliore pas forcément le classement.** Hager *et al.* (2024)
reprennent Baidu-ULTR — le jeu même où ce dépôt mesure $\hat\eta = 1{,}10$ — et constatent que
les corrections standard améliorent la prédiction des clics **sans** améliorer la qualité du
classement jugée par des annotateurs experts. Ils confirment la présence du biais par quatre
méthodes concordantes, ce qui corrobore notre chiffre ; mais l'étape suivante ne suit pas
mécaniquement.

**Une norme de diversité est une norme éditoriale.** Les métriques normatives de Vrijenhoek
*et al.* (2022) découpent la diversité en cinq dimensions dérivées de théories démocratiques
explicites. L'indice de ce dépôt en occupe **une seule**, et une plateforme peut la satisfaire en
servant des contenus divergents et vides. Aucune mesure automatique ne distingue la pluralité de
la fausse balance.

**Ce que le dépôt mesure est l'exposition, pas la réception.** L'indice porte sur ce qui est
servi, pondéré par l'attention *présumée* d'un rang. Ce qui est réellement lu, compris ou retenu
n'est pas mesuré — et la remise d'attention n'en est qu'un substitut, dont la section 1 montre
qu'il est loin d'être anodin.

**Et notre conclusion sur les jeux de données n'est pas neuve.** van Drunen & Vrijenhoek (2025)
établissent, avant ce dépôt, que les jeux publics sont le goulot d'étranglement de la
recommandation diversifiée et que le droit européen est la voie d'accès à envisager. Nous
**corroborons**, nous ne découvrons pas.

→ [Bibliographie complète](bibliographie.md)

## Ce que cette contre-expertise ne fait pas

Elle n'éprouve pas le **test d'échangeabilité** lui-même contre des modèles de clic à cascade,
où l'examen d'un rang dépend de ce qui précède. Le test devrait y rejeter également — il ne teste
que l'indépendance — mais la sévérité minimale détectable, elle, n'aurait plus le même sens.

Elle ne mesure pas non plus ce qu'une **erreur d'estimation de la pertinence** ferait aux
comparaisons de méthodes : tout ce dépôt suppose la pertinence connue, ce qu'aucune plateforme
n'a.

---

*Implémentation : `ide.radio.rank_weights` (remise paramétrée), `ide.entropy.effective_viewpoints` ·
Notebook : [20 — Contre-expertise](notebooks/20_contre_expertise.ipynb) ·
[rang adverse](rang-adverse.md) · [lignes de base](lignes-de-base.md) ·
[bibliographie](bibliographie.md)*
