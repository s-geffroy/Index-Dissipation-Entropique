# IDE — Indice de Diversité Exposée

!!! info "Deux objets distincts"
    L'**IDE** est une *métrique*, destinée au régulateur. L'**[ADE](ade.md)** est un
    *algorithme*, implémenté par la plateforme. Le fil de travail d'origine employait
    les deux sigles indifféremment ; la distinction est ici délibérée.
    → [audit, point 1](limites.md)

!!! success "Renommé — le nom dit désormais ce qui est mesuré"
    L'indice s'est d'abord appelé « **Index de Dissipation Entropique** », d'après l'analogie
    avec la décohérence quantique qui a lancé ce travail. L'[audit](limites.md) a démonté cette
    analogie transfert par transfert : rien de spécifiquement quantique n'y a survécu, et ce qui
    tient — paysage d'énergie libre, hystérésis, franchissement de barrière — relève de la
    mécanique statistique classique. Un nom qui renvoie à une analogie fausse n'est pas neutre :
    il annonce autre chose que ce que l'instrument mesure.

    Le sigle reste **IDE**. Il se lit désormais **Indice de Diversité Exposée** — la répartition
    de l'attention **réellement servie** entre les points de vue du catalogue déclaré.
    « Exposée » n'est pas décoratif : c'est la correction qu'a imposée le [rang
    adverse](rang-adverse.md), une plateforme certifiée à 0,70 par une mesure aveugle au rang
    n'exposant que 0,36.

    Le nom du dépôt et l'adresse du site restent inchangés, pour ne casser aucun lien entrant —
    et la fonction historique s'appelle maintenant `label_diversity_index`, parce que c'est ce
    qu'elle calcule : la diversité des **étiquettes**, sans regarder ni les contenus ni le rang.

## Définition — la forme retenue

L'IDE est l'entropie de Shannon de la distribution des **points de vue exposés**, normalisée
par son maximum théorique :

$$\mathrm{IDE} = \frac{H(q)}{\log_2 k}, \qquad
q_i = \frac{\sum_R w_R \, \mathbb{1}[\text{le contenu servi au rang } R \text{ tombe dans le bac } i]}
{\sum_R w_R}$$

Trois choix la distinguent de l'entropie qu'on écrirait spontanément, et chacun est la
**conséquence d'une attaque qui a réussi** :

| Choix | Pourquoi | Ce qui arrive sans lui |
|---|---|---|
| $q$ porte sur les **contenus servis**, projetés sur les bacs du catalogue de référence — non sur les étiquettes qui les annoncent | une étiquette se choisit, un contenu se constate | l'index atteint **1,000 pour une diversité de contenu nulle**, à coût d'engagement nul → [test adverse](gaming.md) |
| chaque rang est pondéré par l'**attention** qu'il reçoit, $w_R$ (par défaut $1/R$) | un lecteur consulte le premier élément bien plus souvent que le dernier | la norme se satisfait en **enterrant** les contenus divergents : certifiée à 0,70, une plateforme n'expose que **0,36** → [rang adverse](rang-adverse.md) |
| le dénominateur $\log_2 k$ est fixé par le **catalogue déclaré**, non par ce que la plateforme sert | comparer deux plateformes exige la même unité | un fil parfaitement fermé ne présente qu'une modalité : le dénominateur dégénère et l'index flatte |

| Valeur | Interprétation |
|---|---|
| $\mathrm{IDE} = 1$ | l'attention servie se répartit également entre les $k$ points de vue du catalogue |
| $\mathrm{IDE} \to 0$ | bulle de filtres gelée : l'attention servie va à un seul point de vue |

**Grandeur de contrôle associée.** L'écart entre la mesure **aveugle au rang** et la mesure
**consciente du rang** du *même* fil vaut zéro pour une plateforme qui ne relègue pas, et croît
avec l'enterrement. Contrairement aux autres diagnostics du dépôt, il compare une mesure à
elle-même : il est donc directement seuillable. → [rang adverse](rang-adverse.md)

!!! warning "Cette forme n'a jamais été mesurée sur un fil réel"
    Son coût d'engagement est chiffré **en simulation** — de 8,2 % à 18,9 % selon la mesure,
    par énumération exhaustive de tous les fils possibles — et son niveau de plancher reste à
    décider politiquement. Aucun jeu de données public ne permet de la calculer : il y faudrait
    le rang servi **et** une étiquette de point de vue interprétable, et aucun ne porte les
    deux. → [journaux qui enregistrent le rang](rang-servi.md) ·
    [demande au titre de l'article 40](article-40.md)

## La forme d'origine, et ce qu'elle mesurait

Le fil de travail définissait l'index sur les **étiquettes** d'un fil, sans regarder le rang :

$$H_{\text{norm}} = \frac{H(X)}{\log_2 k}$$

C'est ce que calcule `ide.entropy.label_diversity_index`, dont le nom dit désormais la portée.
Cette forme reste utile là où le rang n'existe pas — le [modèle à agents](notebooks/08_abm_compas_politique.ipynb)
décrit ainsi l'exposition d'un individu — mais elle **ne peut pas servir de norme** : c'est elle
que le test adverse met en défaut.

## Pourquoi la normalisation est le point essentiel

L'entropie brute se mesure en bits, et sa valeur dépend du nombre de modalités
disponibles. Deux plateformes aux catalogues différents produiraient des chiffres
incomparables.

La normalisation par $\log_2 k$ rend l'index **sans dimension et borné**. C'est ce qui
en fait un instrument juridique utilisable : un seuil exprimé en pourcentage se
transpose d'une plateforme à l'autre, un seuil exprimé en bits ne se transpose à rien.

## Le dénominateur doit être imposé

Une plateforme laissée libre de choisir $k$ choisirait le nombre de modalités
qu'elle sert *effectivement*. Un fil parfaitement fermé ne présentant qu'une seule
modalité, le dénominateur deviendrait dégénéré et l'index flatteur.

L'implémentation rend cette dépendance explicite :

```python
from ide.entropy import label_diversity_index

feed = ["complot"] * 10 + ["factuel"] * 10

label_diversity_index(feed)                    # 1.0  — deux modalités observées
label_diversity_index(feed, catalogue_size=4)  # 0.5  — quatre points de vue disponibles
```

**Un régulateur doit donc imposer un $k$ de référence.** C'est le premier paramètre
sur lequel une norme technique doit se prononcer, et c'est aussi l'endroit où l'index
devient un objet politique — voir les [limites](#limites).

## Ce que l'index détecte

Le lien avec la théorie est direct : un IDE effondré est la signature d'une
température sociale locale nulle, c'est-à-dire d'un état figé au sens du modèle
d'Ising. Le [notebook 01](notebooks/01_entropie_et_purete.ipynb) montre que l'index
franchit le seuil critique **bien avant** la fermeture complète du fil : un régulateur
peut donc constater un gel *en cours*, et pas seulement une fois établi.

Le [notebook 08](notebooks/08_abm_compas_politique.ipynb) mesure sa réponse au
paramètre que l'algorithme contrôle réellement — le seuil de bulle :

| Seuil de bulle | IDE moyen | Population en bulle gelée |
|---|---|---|
| étroit (0,10) | ≈ 0,27 | ≈ 60 % |
| large (0,80) | ≈ 0,93 | ≈ 0 % |

## Protocole de mesure proposé

1. **Fenêtre** — 24 heures glissantes de contenus servis.
2. **Unité** — le contenu servi, non le contenu consulté : c'est la plateforme qui est
   auditée, pas l'utilisateur.
3. **Catalogue de référence** — $k$ fixé par le régulateur, identique pour toutes les
   plateformes d'une même catégorie de service.
4. **Agrégation** — l'index est calculé par utilisateur puis agrégé ; la grandeur
   réglementaire est la **part de la population sous le seuil critique**, pas la
   moyenne. Une moyenne satisfaisante peut masquer une minorité entièrement enfermée.
5. **Seuil** — $H_{\text{critique}}$, à calibrer empiriquement. La valeur de $0{,}4$
   employée dans ce dépôt est une **valeur d'illustration**, pas une recommandation
   chiffrée.

## Deux métriques qu'il ne faut pas confondre

Le modèle à agents suit à la fois la **polarisation** — distance moyenne à la
modération — et l'**IDE**. Leur écart est instructif :

* une société peut être fortement polarisée avec un IDE élevé : quatre blocs qui
  s'affrontent en se voyant ;
* elle peut être faiblement polarisée avec un IDE effondré : tout le monde d'accord.

C'est la seconde qu'un régulateur doit mesurer, parce que c'est celle qui décrit
l'autonomie cognitive réelle — et celle que l'algorithme détermine.

## Limites

Ces réserves comptent autant que la définition, et elles sont développées dans
l'[audit critique](limites.md).

* **La discrétisation en points de vue est un choix politique.** Qui définit les
  modalités définit l'index. Découper l'espace des opinions en 4, 40 ou 400 catégories
  change la valeur mesurée, et ce découpage n'est pas un acte technique neutre.
* **L'index est manipulable, et cela a été mesuré.** Sur la forme d'origine, l'attaque est
  totale : 1,000 pour une diversité de contenu nulle, sans céder un point d'engagement. La
  forme retenue ferme cette voie et l'enterrement avec, mais **toute métrique imposée reste une
  cible** : une plateforme peut encore servir des contenus formellement divergents et
  substantiellement vides — de la diversité de bac sans diversité d'argument. Aucune mesure
  automatique ne distingue les deux. → [test adverse](gaming.md)
* **Le niveau du plancher n'est pas déductible de la mesure.** Le dépôt établit la *forme* de
  la norme et son *prix*, pas sa valeur. Fixer 0,60 plutôt que 0,40 est une décision politique
  qu'aucun calcul de ce dépôt ne tranche.
* **Un seuil sur l'IDE est une contrainte sur ce que les gens voient.** C'est
  défendable, mais c'est une intervention sur le débat public, et la présenter comme
  une simple mesure technique serait malhonnête.
* **Vie privée.** Mesurer l'IDE de fils individuels suppose d'observer ce qui est
  servi à des personnes. Un protocole crédible doit être agrégatif et
  différentiellement privé — ce dépôt ne le propose pas encore.

---

*Implémentation : `ide.entropy.label_diversity_index` ·
[Mémorandum de régulation](memorandum.md)*
