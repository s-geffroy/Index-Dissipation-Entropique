# Indice de Diversité Exposée

**Mesurer la diversité qu'un fil algorithmique expose réellement — et éprouver ce qu'on croit en savoir.**

---

## Ce que ce dépôt contient

Un **instrument** — une mesure de la diversité qu'un fil d'actualité expose réellement à son
lecteur, calculable sans accès au code de la plateforme — et la **méthode adverse** qui l'a
mis à l'épreuve : chaque proposition y est attaquée, et ce qui tombe est publié comme tel.

Il en reste dix-neuf notebooks exécutables, 572 tests, dix-sept corrections consignées, et un
état des lieux qui ne ressemble pas à ce que le projet annonçait.

![Une plateforme certifiée à 0,70 par une mesure aveugle au rang n'expose que 0,36 de
diversité réelle](figures/fig15_rang_adverse.png)

/// caption
Le résultat central : sous un plancher de diversité aveugle au rang, les quatre mesures
candidates se laissent contourner en **enterrant** les contenus divergents. Une plateforme
certifiée à 0,70 n'expose que 0,36. Figure régénérée par
[le notebook 15](notebooks/15_rang_adverse_et_severite.ipynb).
///

## Le verdict, en une page

| Objet | État |
|---|---|
| L'analogie décohérence quantique ↔ effondrement du consensus | **réfutée**, transfert par transfert — rien de spécifiquement quantique n'y a survécu → [audit](limites.md) |
| Le formalisme classique qu'elle a fait emprunter | **cohérent et reproduit des comportements**, mais un seul paramètre calibré, et sa seule prédiction propre — l'effet de la charge émotionnelle — **testée quatre fois sans effet** |
| L'index tel qu'il était proposé au régulateur | **intenable** : saturable à coût nul, puis contournable par l'enterrement → [test adverse](gaming.md) · [rang adverse](rang-adverse.md) |
| La forme retenue de l'index | **définie et chiffrée** — entropie des contenus servis, pondérée par le rang — mais **jamais éprouvée sur un fil réel** |
| L'algorithme (ADE) | **sur la frontière exacte, mais pas premier** : une heuristique de 1998 fait aussi bien → [lignes de base](lignes-de-base.md) ; et non évaluable sur données réelles en l'état |
| L'écart de persistance entre registres émotionnels | **n'existe pas** — c'était un artefact de sélection → [corpus étendu](corpus-etendu.md) · [annotation](annotation.md) |
| Les instruments de mesure construits en chemin | **valides**, et l'un d'eux confronté à une vérité terrain → [rang servi](rang-servi.md) |

**En une phrase : la théorie n'a pas tenu, la métrologie oui.**

## Ce qui tient

**Un contrôle qui dit si un journal de recommandation est seulement corrigible.** Le test
d'échangeabilité intra-fil ne détecte rien dans MIND ($z = +0{,}12$, ordre mélangé) et rejette
à $z = -206$ sur Baidu-ULTR, du côté que la théorie prescrit. Il est exact, étalonné en
puissance, et il doit précéder toute estimation d'exposition.
→ [Exploration de MIND](mind.md) · [Journaux qui enregistrent le rang](rang-servi.md)

**Une sévérité de biais de position qui s'estime au lieu de se poser.** $1{,}10 \pm 0{,}09$ sur
une page de résultats de recherche ; **dix fois moins** sur un bandeau de trois vignettes, où
l'allocation aléatoire rend la mesure causale. $\eta$ est une propriété de la **surface**, et la
transporter coûte jusqu'à +179 % sur le chiffre publié. → [Rang adverse](rang-adverse.md)

**Des estimateurs contrefactuels vérifiés contre une vérité terrain.** La valeur d'une politique
jamais déployée, estimée sur les seules données d'une autre : **+2,5 %** d'écart, contre
**+32 %** pour l'estimation naïve — avec le diagnostic qui interdit d'en tirer gloire, une
taille d'échantillon effective de 1 513 pour 4 millions d'impressions.
→ [Journaux qui enregistrent le rang](rang-servi.md)

**Une comparaison du filtre à la frontière exacte.** Sur 150 viviers, le filtre du dépôt laisse
**0,0 à 1,0 %** d'engagement sur la table — mais MMR, publié en 1998, fait aussi bien. Et le prix
de la norme dépend du lecteur : **3,8 %** quand ses intérêts traversent les points de vue,
**17,1 %** quand sa préférence *est* un point de vue. → [Lignes de base](lignes-de-base.md)

**Une demande d'accès aux données qui se vérifie au lieu de se plaider.** Quatre tableaux
agrégés, sans aucune donnée personnelle, dont il est prouvé qu'ils recalculent les mesures **à
l'identique** — pour 95 fois moins de lignes que le journal brut.
→ [Demande au titre de l'article 40](article-40.md)

## Ce qui est tombé

Six résultats négatifs, chacun publié avec ce qui l'a établi :

* **le critère $\gamma\alpha > \lambda$ ne veut rien dire** — il est satisfait par construction
  pour tout contenu ayant percé, ce que seule la mesure a révélé → [calibration](calibration.md) ;
* **l'écart de persistance entre registres n'existe pas** — ×9,2 contre ×2,9 sur le corpus
  pilote, ×3,04 contre ×2,90 ($p = 0{,}53$) sur 440 sujets → [corpus étendu](corpus-etendu.md) ;
* **il n'était pas dilué par l'étiquetage** — 40 % de bruit mesuré, et l'écart disparaît quand
  même → [annotation en aveugle](annotation.md) ;
* **un plancher d'index se sature à coût nul** — 1,000 pour une diversité de contenu nulle
  → [test adverse](gaming.md) ;
* **le premier correctif prescrivait la polarisation** — l'optimum sous contrainte de l'entropie
  de Rao est bimodal → [test adverse](gaming.md) ;
* **le jeu de données de référence ne permet pas l'évaluation annoncée** — MIND ne conserve pas
  l'ordre servi, et aucun jeu public ne porte à la fois le rang et une étiquette de point de vue
  → [MIND](mind.md) · [rang servi](rang-servi.md).

## Ce qui n'est pas tranché

* **La forme retenue de l'index n'a jamais été mesurée sur un fil réel.** Elle est définie,
  son coût d'engagement est chiffré en simulation, et c'est tout.
* **Le niveau du plancher est une décision politique**, comme le catalogue de points de vue qui
  lui sert de grille. La mesure décrit, elle ne prescrit pas.
* **Les trois codeurs de l'annotation sont des instances du même modèle de langue.** L'accord
  entre elles surestime ce que produiraient des juges indépendants.
* **Rien ne démontre que les opinions humaines *obéissent* à une mécanique statistique.** Le
  travail établit qu'un formalisme emprunté à la physique en **reproduit** des comportements.

## Les deux instruments

| | Objet | État |
|---|---|---|
| **[IDE](ide.md)** | *Indice de Diversité Exposée* — entropie des contenus servis sur le catalogue de référence déclaré, **pondérée par l'attention de chaque rang**, dans $[0, 1]$ | forme retenue **définie**, non éprouvée sur données réelles |
| **[ADE](ade.md)** | *Algorithme de Diversité Exposée* — filtre de recommandation qui optimise cet indice au lieu de l'engagement brut | **non évalué** : le jeu de données qui le permettrait n'existe pas publiquement |

Le [mémorandum de régulation](memorandum.md) traduit l'indice en recommandations pour l'ARCOM
et la Commission européenne, dans le cadre du *Digital Services Act* — avec, à chaque
recommandation, la mesure qui l'a corrigée.

## D'où cela vient

Le projet est parti d'une analogie : plus un système quantique est grand, plus vite il
décohère ; plus une population est grande, plus l'accord y est difficile. Cette analogie a
produit des quantités mesurables, et **aucune de ses affirmations propres n'a résisté à la
vérification**. C'est l'objet de l'[audit critique](limites.md), qui recense **dix-sept
corrections** — dont cinq invalidaient une formule, et deux ont été découvertes en tentant de
mesurer.

Ce qui subsiste du formalisme est classique : paysage d'énergie libre, transition de phase,
hystérésis, franchissement de barrière.

![Les trois régimes de l'opinion publique : paysage d'énergie libre, distributions
stationnaires, et scission d'une société initialement modérée](figures/fig04_paysage.png)

/// caption
Les trois régimes de l'opinion publique, obtenus en changeant deux paramètres du même paysage
d'énergie libre. Figure régénérée par
[le notebook 04](notebooks/04_fokker_planck_paysage.ipynb).
///

## Explorer

Les dix-neuf notebooks sont exécutables et produisent l'intégralité des figures de la
note. Chacun se lit indépendamment.

| Notebook | Ce qu'il montre |
|---|---|
| [01 — Entropie et pureté](notebooks/01_entropie_et_purete.ipynb) | une superposition cohérente a une entropie nulle ; l'IDE et sa normalisation |
| [02 — Ising](notebooks/02_ising_temperature_sociale.ipynb) | la température critique d'Onsager, retrouvée numériquement |
| [03 — Voter Model](notebooks/03_voter_consensus_et_taille.ipynb) | les lois d'échelle du consensus, et pourquoi la connectivité n'est pas la coupable |
| [04 — Fokker-Planck](notebooks/04_fokker_planck_paysage.ipynb) | les trois régimes de l'opinion publique dans un même paysage d'énergie libre |
| [05 — Hystérésis](notebooks/05_hysteresis_et_contre_champ.ipynb) | la mémoire d'une fausse croyance, et les deux façons de l'effacer |
| [06 — Résonance](notebooks/06_resonance_larsen.ipynb) | le seuil $\gamma\alpha > \lambda$ et le cycle limite de l'attention |
| [07 — ADE](notebooks/07_ade_filtre_entropique.ipynb) | un fil gelé qui se réouvre sous l'effet du recuit |
| [08 — Modèle à agents](notebooks/08_abm_compas_politique.ipynb) | la bulle de filtres vue depuis l'individu |
| [09 — Calibration](notebooks/09_calibration_visibilite.ipynb) | $\gamma\alpha/\lambda$ mesuré sur 19 épisodes d'attention publics |
| [10 — Changement de régime](notebooks/10_changement_de_regime.ipynb) | 14 basculements datés, et pourquoi le rapport n'y est pas identifiable |
| [11 — Corpus étendu](notebooks/11_corpus_etendu.ipynb) | 440 sujets dérivés de catégories : l'écart de persistance ne se réplique pas |
| [12 — Annotation en aveugle](notebooks/12_annotation_en_aveugle.ipynb) | 40 % de bruit d'étiquetage mesuré, et le double recodage à $\kappa = 0{,}92$ |
| [13 — Test adverse](notebooks/13_test_adverse_index.ipynb) | un plancher d'IDE saturé à coût nul, et le correctif qui prescrivait la polarisation |
| [14 — Rang et contrefactuel](notebooks/14_rang_et_contrefactuel.ipynb) | l'enterrement de la diversité, et l'évaluation hors ligne fausse de 201 % |
| [15 — Rang adverse](notebooks/15_rang_adverse_et_severite.ipynb) | les quatre mesures contournées par l'ordre, et la sévérité du biais estimée |
| [16 — Exploration de MIND](notebooks/16_exploration_mind.ipynb) | un ordre indiscernable d'un mélange, et cinq sévérités tirées du même jeu |
| [17 — Rang servi](notebooks/17_rang_servi.ipynb) | deux journaux qui enregistrent le rang, et un estimateur jugé contre la vérité |
| [18 — Demande article 40](notebooks/18_demande_article_40.ipynb) | quatre tableaux agrégés qui suffisent, et la preuve qu'ils suffisent |
| [19 — Lignes de base](notebooks/19_lignes_de_base.ipynb) | le filtre jugé contre quatre concurrents et contre la frontière exacte |

## Reproduire

Tout s'exécute en conteneur. Aucune dépendance n'est installée sur la machine hôte.

```bash
git clone git@github.com:s-geffroy/Indice-Diversite-Exposee.git
cd Indice-Diversite-Exposee

docker compose run --rm test          # 572 tests
docker compose run --rm notebooks     # régénère les figures
docker compose up lab                 # JupyterLab sur :8888
docker compose up site                # cette documentation sur :8000
docker compose run --rm latex         # compile la note en PDF
```

## Relecture

Ce travail est **ouvert à la relecture critique**. Les retours sur le formalisme, sur
la viabilité de l'index ou sur les limites énumérées dans l'audit sont les plus
utiles. → [Appel à relecture](relecture.md)

---

*Code sous licence MIT · Contenus rédactionnels sous licence CC BY 4.0 ·
[Dépôt GitHub](https://github.com/s-geffroy/Indice-Diversite-Exposee)*
