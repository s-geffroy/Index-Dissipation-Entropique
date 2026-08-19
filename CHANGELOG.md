# Changelog

Toutes les évolutions notables de ce projet sont consignées dans ce fichier.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le
versionnement respecte [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### Ajouté — la demande d'accès aux données, écrite comme une spécification

Seule voie restante après le constat qu'aucun jeu public ne porte à la fois le rang servi et une
étiquette de point de vue. Détail : [`docs/article-40.md`](docs/article-40.md) et le
[notebook 18](notebooks/18_demande_article_40.ipynb).

- **`ide.aggregates`** — les **quatre tableaux agrégés** dont les mesures de ce dépôt ont
  réellement besoin : profils de fils, clics par rang, cellules (contenu, rang) avec propension,
  exposition par point de vue déclaré. Le module sait les construire depuis un journal, les
  consommer, et mesurer ce que leur seuil de confidentialité coûte aux estimations.
- **`docs/article-40.md`** — la demande elle-même, rédigée article par article du règlement
  délégué (UE) 2025/2050 : objet, données, nécessité et proportionnalité, risques, publication,
  calendrier et voies de recours.
- **`notebooks/18_demande_article_40.ipynb`**, `paper/figures/fig18_demande_article_40.png` et
  11 tests supplémentaires (556 au total).

### Résultats — les quatre tableaux suffisent, et c'est vérifié

- **Le test d'échangeabilité se recalcule à $3 \times 10^{-12}$ près** depuis les seuls tableaux
  1 et 2, sur MIND comme sur Baidu-ULTR — donc le contrôle qui décide si un journal est
  corrigible n'exige **aucune donnée individuelle**.
- **La sévérité $\eta$ se recalcule exactement** — écart nul — depuis le seul tableau 3.
- **Les deux mesures de diversité** — composée et exposée — se recalculent depuis le seul
  tableau 4, qui suffit donc à constater l'**enterrement** : à composition identique, un fil
  conforme au plancher aveugle n'expose que 0,160 d'attention aux points de vue minoritaires,
  contre 0,337 pour le même fil entrelacé et 0,375 en composition.
- **Ce qui est demandé pèse 95 fois moins de lignes** que le journal brut sur Baidu-ULTR (5 543
  contre 524 164) et 101 fois moins sur MIND (57 906 contre 5 843 444).
- **Le seuil de confidentialité n'est pas neutre** : passer de 5 à 20 impressions par cellule
  déplace la sévérité estimée de 1,10 à 1,40, soit +27 %, parce que les cellules rares sont
  celles des rangs profonds. Il doit être publié avec le résultat.
- **Deux clés d'agrégation plus simples ont été écartées parce qu'elles étaient fausses** :
  indexer les fils par leur longueur plutôt que par leur profil de rangs, et omettre le nombre de
  clics du fil — qui empêche d'écarter les fils entièrement cliqués et décale l'écart réduit de
  $-205{,}7$ à $-203{,}9$. Les deux erreurs produisaient des chiffres du bon ordre de grandeur.

### Modifié

- [`docs/feuille-de-route.md`](docs/feuille-de-route.md) §3.1 — la troisième voie est désormais
  outillée, avec sa réserve : l'art. 40(8)(a) exige une affiliation à un organisme de recherche,
  que ce dépôt n'a pas. Le document est un modèle prêt à déposer.
- [`docs/memorandum.md`](docs/memorandum.md) — nouvelle disposition : **normaliser la forme de
  la demande d'accès**, et y fixer le seuil de suppression des faibles effectifs.

### Ajouté — deux journaux publics qui enregistrent le rang servi

Suite directe de l'exigence sur laquelle s'était terminée la mesure sur MIND. Détail :
[`docs/rang-servi.md`](docs/rang-servi.md) et le
[notebook 17](notebooks/17_rang_servi.ipynb).

- **`ide.logs`** — la représentation commune d'un journal d'impressions et les mesures qui s'y
  appliquent, extraites de `ide.mind` : trois jeux de données les partagent désormais. Le
  condensé versionnable y vit aussi, et **vérifie** la structure des fils au lieu de la supposer.
- **`ide.exposure`** — lecture de **Baidu-ULTR** (rang d'affichage, session, clic) et de
  l'**Open Bandit Dataset** (position, propension vraie, seau à politique aléatoire), et
  confrontation d'une estimation contrefactuelle à une vérité terrain mesurée.
- **`scripts/fetch_exposure.py`**, **`scripts/build_exposure_digest.py`** et
  **`data/exposure_digest.npz`** — 0,7 Mo versionnés pour 3,1 Go de journaux bruts, sous deux
  licences distinctes, avec vérification de taille et d'empreinte à la récupération.
- **`notebooks/17_rang_servi.ipynb`**, `paper/figures/fig17_rang_servi.png` et 14 tests
  supplémentaires (545 au total). `pyarrow` rejoint les dépendances de laboratoire.

### Résultats — la sévérité se mesure, et elle dépend de la surface

- **Le contrôle positif passe.** Sur Baidu-ULTR, le test d'échangeabilité rejette à
  $z = -205{,}7$ ($p < 10^{-12}$) et **du bon côté** : les clics se concentrent en haut. Un test
  qui ne rejetterait jamais rien ne dirait rien de MIND.
- **$\hat\eta = 1{,}10 \pm 0{,}09$** par effets fixes de document, contre 1,49 par ajustement
  agrégé : l'écart est le confondant de qualité, la plateforme plaçant les meilleurs documents
  en tête. La couverture reste mince — 55 documents portent l'estimation, sur 444 709.
- **Dix fois plus faible sur une autre surface.** Sur l'Open Bandit Dataset, à allocation
  **aléatoire** donc à effet causal, un bandeau de trois vignettes horizontales décroît en
  $R^{-0{,}04}$ (campagne « all ») à $R^{-0{,}11}$ (campagne « men »). $\eta$ est une propriété
  de la surface, pas une constante, et le transporter coûte l'ordre de grandeur que le rang
  adverse avait chiffré.
- **Première confrontation à une vérité terrain.** La valeur d'une politique jamais déployée,
  estimée sur les seules données d'une autre politique : IPS à **+2,5 %** de la valeur mesurée
  directement, contre **+31,6 %** pour l'estimation naïve, **−7,0 %** pour SNIPS et **−12,7 %**
  pour un plafond à 10.
- **Et le diagnostic qui l'accompagne** : taille d'échantillon **effective** de **1 513** pour
  4 077 727 impressions, soit 0,04 %. L'estimation est sans biais et repose sur l'équivalent de
  mille cinq cents observations.
- **Troisième résultat négatif de la série** : aucun jeu public ne porte à la fois le rang servi
  et une étiquette de point de vue interprétable. L'évaluation de l'ADE annoncée par la feuille
  de route ne peut pas être faite sur données publiques en l'état.

### Corrigé — un condensé qui supposait au lieu de vérifier

- Le condensé résumait la structure d'un fil à sa **longueur**, en supposant qu'un fil de
  longueur $L$ occupe les rangs 1 à $L$. Vrai de MIND, **faux** d'une page de résultats qui saute
  des rangs. Le défaut était indolore — $z = -200$ au lieu de $-206$ — ce qui est la façon dont
  ce genre d'erreur survit. Dix-septième entrée de l'[audit critique](docs/limites.md).

### Modifié

- [`docs/feuille-de-route.md`](docs/feuille-de-route.md) §3.1 — le critère de choix d'un jeu de
  données est réglé, la piste ne l'est pas : trois mesures restent faisables, la quatrième passe
  par une demande au titre de l'article 40 du DSA.
- [`docs/memorandum.md`](docs/memorandum.md) — l'exigence de publication du rang servi a
  désormais un **précédent industriel** ; nouvelle disposition exigeant une **fraction
  d'exploration aléatoire**, sans laquelle la taille d'échantillon effective d'un audit tombe à
  0,04 % ; cette taille devient une grandeur de contrôle à publier.
- [`docs/mind.md`](docs/mind.md) — piste ouverte 1 réglée.

### Ajouté — l'exploration réellement enregistrée dans MIND

Le préalable inscrit à la feuille de route §3.1 : mesurer l'exploration d'un jeu de données
public **avant** d'y évaluer quoi que ce soit. Détail : [`docs/mind.md`](docs/mind.md) et le
[notebook 16](notebooks/16_exploration_mind.ipynb).

- **`ide.mind`** — lecture des journaux d'impressions de MIND, **test d'échangeabilité
  intra-fil** (exact, avec étalonnage de puissance par simulation à structure de fils
  identique), taux de clic par rang à longueur de fil contrôlée, et couverture de rang.
- **`scripts/fetch_mind.py`** — récupération des journaux, avec vérification du nombre de fils
  et de l'empreinte SHA-256 : la source officielle répond désormais *409 Public access is not
  permitted*, le jeu vient d'un miroir, et un miroir se vérifie.
- **`scripts/build_mind_digest.py`** et **`data/mind_digest.npz`** — condensé de 1,5 Mo, seul
  dérivé de MIND que ce dépôt puisse porter (licence de recherche Microsoft, 135 Mo bruts). Un
  test vérifie qu'il rend **exactement** les chiffres du journal brut.
- **`notebooks/16_exploration_mind.ipynb`**, `paper/figures/fig16_exploration_mind.png` et 19
  tests supplémentaires (531 au total).

### Résultats — l'ordre enregistré dans MIND n'en est pas un

- **Indiscernable d'un mélange** : $z = +0{,}12$ ($p = 0{,}91$) sur 156 965 fils, répliqué à
  $z = +0{,}28$ ($p = 0{,}78$) sur le second découpage. Le test détecterait $\eta = 0{,}02$ à
  douze écarts-types ; la sévérité minimale détectable vaut $\eta \approx 0{,}004$.
- **La courbe de biais de position qu'on y trace est un artefact de composition.** Le taux de
  clic décroît de 0,108 à 0,038 sur vingt rangs, soit $\hat\eta = 0{,}39$ — mais à longueur de
  fil fixée la pente est nulle et **change de signe** d'une longueur à l'autre. Les positions
  élevées n'existent que dans les fils longs, où le taux de clic par contenu est plus faible.
- **Cinq sévérités incompatibles tirées du même jeu**, de $-0{,}13$ à $+0{,}25$ selon un simple
  seuil d'impressions, toutes d'erreur type inférieure à 0,007.
- **Le mélange ne débiaise pas les clics, il détruit la variable qui les corrigerait.** Sur un
  journal simulé de sévérité vraie 1,00 : $\hat\eta = 1{,}003$ avec l'ordre conservé,
  $-0{,}003$ après mélange — à clics identiques. L'évaluation qui s'ensuit estime le coût d'un
  réordonnancement à **0,00 %** contre 6,61 % de valeur vraie : sous $\eta = 0$, deux politiques
  qui ne diffèrent que par l'ordre reçoivent la même valeur, donc l'évaluation est vide par
  construction.

### Corrigé — le contrôle d'identifiabilité était nécessaire et non suffisant

- Le drapeau d'identifiabilité de `estimate_position_bias`, présenté au chantier précédent comme
  la garde à passer avant d'estimer $\eta$, **compte la variation de rang sans dire d'où elle
  vient**. Une variation artificielle le satisfait mieux que n'importe quelle exploration réelle.
  Le test d'échangeabilité est le contrôle manquant, et il doit précéder l'estimation.
  Seizième entrée de l'[audit critique](docs/limites.md).

### Modifié

- [`docs/feuille-de-route.md`](docs/feuille-de-route.md) §3.1 — la quatrième condition n'est pas
  remplie par MIND : l'estimation contrefactuelle du coût d'engagement y est impossible, les
  autres étapes restent faisables à condition de dire que le coût publié est un coût en
  pertinence **déclarée**, et le choix du jeu de données devient le premier travail.
- [`docs/memorandum.md`](docs/memorandum.md) — nouvelle section **« ce qu'un journal doit
  contenir pour être auditable »** : publication du rang servi ou de la propension d'exposition,
  et test d'échangeabilité en contrôle d'acceptation des journaux transmis au titre de
  l'article 40 du DSA.
- [`docs/rang-adverse.md`](docs/rang-adverse.md) — avertissement sur le contrôle
  d'identifiabilité, et piste ouverte 3 réglée.

### Ajouté — le test adverse sur fils ordonnés, et la sévérité du biais estimée

Règle les deux dettes explicites laissées par le chantier précédent. Détail :
[`docs/rang-adverse.md`](docs/rang-adverse.md) et le
[notebook 15](notebooks/15_rang_adverse_et_severite.ipynb).

- **`ide.ranking`** — le test adverse repris sur des fils **ordonnés** et non sur des
  compositions. L'optimisation est **exhaustive** : les 65 536 fils possibles sont énumérés,
  l'optimum est donc exact et non le résultat d'une heuristique. Au-delà d'une limite déclarée,
  le module refuse plutôt que de basculer en silence sur une approximation.
- **`ide.offpolicy.estimate_position_bias`** — estimation de $\eta$ par régression à effets
  fixes de contenu sur $\log \mathrm{CTR} = \log g(i) - \eta \log R$, avec erreur type et
  **drapeau d'identifiabilité**.
- **`notebooks/15_rang_adverse_et_severite.ipynb`** et 24 tests supplémentaires.

### Résultats — les quatre mesures se laissent contourner par l'ordre

- **Une plateforme certifiée à 0,70 n'expose que 0,36.** Sous plancher aveugle au rang,
  l'entropie de Rao certifie 0,750 pour une diversité exposée de **0,355** ; l'entropie de
  position, 0,774 pour **0,443**. Le fil optimal a toujours la même forme — six contenus du
  point de vue préféré, puis les divergents relégués aux dernières positions.
- **Un plancher conscient du rang ferme l'échappatoire, et double le coût** : de 8,2 % à
  18,9 % pour l'entropie de Rao, de 10,7 % à 20,9 % pour l'entropie de position.
- **L'écart croît avec l'exigence** : 0,262 à plancher 0,40, 0,395 à plancher 0,70 pour Rao.
  Plus la norme aveugle demande de diversité, plus il devient rentable de l'enterrer.
- **La proximité à la cible résiste le mieux** — écart nul à plancher 0,40, 0,122 à 0,70 —
  troisième point sur lequel elle se détache des trois autres mesures.
- **Cet écart-là est seuillable**, contrairement à l'excès de signature : il compare **la même
  mesure à elle-même**, une fois à l'aveugle du rang et une fois en le prenant en compte.

### Résultats — la sévérité du biais de position s'estime, et il fallait l'estimer

- **$\hat\eta = 1{,}013 \pm 0{,}019$** sur 40 000 impressions ; la sévérité vraie est
  retrouvée de 0,4 à 1,6.
- **À politique déterministe, $\eta$ n'est pas identifiable.** Aucun contenu ne change de
  rang, il n'y a donc aucune variation à exploiter, et l'estimateur **refuse de renvoyer un
  chiffre**. À exploration faible il en renvoie un, mais l'erreur type dit qu'il ne vaut rien.
- **Poser $\eta$ de travers coûte jusqu'à 179 % d'erreur** — soit l'ordre de grandeur du biais
  de 201 % que la correction contrefactuelle prétendait éliminer. Avec $\eta$ estimé, le coût
  tient entre 6,6 % et 6,9 % contre 6,6 % de valeur vraie.
- **Conséquences** : la recommandation 1 du mémorandum reçoit le **prix** de la mesure
  consciente du rang et une **grandeur de contrôle** associée ; la feuille de route §3.1 ajoute
  une quatrième exigence — estimer $\eta$, et vérifier d'abord l'exploration du jeu de données.
- **Réserve maintenue :** la forme $e(R) = R^{-\eta}$ reste posée, seule sa sévérité est
  estimée. Et l'énumération exhaustive borne les fils étudiés à huit positions sur quatre
  points de vue — rien n'assure que le comportement se transporte à plus grande échelle.

### Ajouté — rang et contrefactuel, deux corrections avant l'évaluation sur données réelles

Détail : [`docs/evaluation.md`](docs/evaluation.md) et le
[notebook 14](notebooks/14_rang_et_contrefactuel.ipynb).

- **`ide.radio`** — divergences conscientes du rang, d'après RADio (Vrijenhoek *et al.*,
  RecSys 2022) : remise de rang réciproque ou logarithmique, divergence de Jensen-Shannon en
  base 2 donc **exactement** bornée par 1, et les cinq références du cadre — calibration,
  fragmentation, activation, représentation, voix alternatives.
- **`ide.offpolicy`** — estimateurs contrefactuels : IPS, SNIPS, IPS plafonné, doublement
  robuste, taille d'échantillon effective, et l'estimateur de *replay* implémenté **pour être
  comparé, non pour être employé**. Un défaut de recouvrement y lève une erreur au lieu de
  produire un chiffre.
- **`notebooks/14_rang_et_contrefactuel.ipynb`** et 68 tests supplémentaires.

### Résultats — un quatrième adversaire, et une évaluation qui ne mesurait rien

- **L'enterrement fonctionne.** À composition **rigoureusement identique**, déplacer les
  contenus divergents vers le bas du fil rapporte **10 % d'engagement** et fait passer la
  divergence de 0,525 à 0,630. L'entropie de position — le plancher retenu la veille — vaut
  0,774 dans les deux cas : elle ne voit que la composition, jamais l'ordre.
- **La remise de rang ferme l'échappatoire.** À composition fixe, faire glisser le bloc
  divergent du haut vers le bas laisse la mesure sans remise **parfaitement plate**, tandis que
  les mesures escomptées montent de 0,29 à 0,68.
- **L'évaluation naïve d'un réordonnancement est fausse de 201 % en médiane**, jusqu'à 851 %
  sur soixante jeux de contenus. Elle surestime le coût dans 56 cas sur 60 — ce qui inviterait
  à la tenir pour prudente — mais le sous-estime dans les 4 autres, à configuration pourtant
  identique. **Un chiffre naïf n'est donc même pas une borne supérieure.**
- **IPS et SNIPS retrouvent la valeur vraie à moins d'un point** (6,6 % contre 6,6 %, là où le
  replay annonce 5,0 %).
- **Trois grandeurs doivent accompagner tout résultat contrefactuel** : le modèle de propension
  employé, la taille d'échantillon effective — qui tombe de 60 000 à 10 026 quand le
  réordonnancement devient agressif — et le plafond, dont le seul choix déplace l'estimation de
  −6,5 % à −0,0 %.
- **Conséquences** : la recommandation 1 du mémorandum exige désormais une mesure **consciente
  du rang** ; la feuille de route §3.1 conditionne l'évaluation de l'ADE à trois exigences sans
  lesquelles « la frontière de Pareto annoncée mesurerait surtout le biais de position de la
  plateforme qui a produit les données ».
- **Réserve maintenue :** le modèle de biais de position est une hypothèse, non une mesure. Le
  problème se déplace d'un cran, de « les clics sont des étiquettes » vers « l'exposition se
  modélise par le rang ». Le second énoncé est bien meilleur, et il reste un énoncé.

### Corrigé — le remplaçant proposé pour l'IDE prescrivait la polarisation

Correction du correctif publié la veille. Détail : [`docs/gaming.md`](docs/gaming.md), section
« Le correctif », et le [notebook 13](notebooks/13_test_adverse_index.ipynb).

- **Le défaut.** L'entropie quadratique de Rao est la *distance intra-liste*, dont Ohsaka et
  Togashi (SIGIR 2023) ont montré qu'elle admet des optima dégénérés. Sur un axe d'opinion le
  dégénéré est le **fil bimodal** : elle attribue **1,000** à un fil servant les deux bords et
  rien entre eux, contre **0,750** à un fil étalé.
- **Ce n'est pas une faille exploitable, c'est la réponse optimale.** Sous plancher de Rao à
  0,80, la plateforme sert **4 points de vue sur 8** et laisse un vide de **0,71** — les sept
  dixièmes de l'axe. Le plancher réglementaire produit lui-même l'exposition bimodale que le
  projet cherche à mesurer.
- **La faute est de méthode** : le remplaçant avait été éprouvé contre l'attaque qu'il devait
  fermer, et contre aucune autre. L'erreur a été trouvée en lisant la littérature du domaine
  sur la mesure employée, non en relisant le code.

### Ajouté — trois mesures candidates, éprouvées contre trois adversaires

- **`position_entropy`** — l'IDE calculé sur les **contenus** servis, projetés sur les bacs du
  catalogue de référence, et non sur les étiquettes déclarées. Garde l'interprétation de
  l'index d'origine, résiste aux trois adversaires, et coûte **moins cher** que Rao (18,1 %
  contre 32,8 % à plancher 0,80).
- **`gaussian_ild`** — la proposition d'Ohsaka et Togashi. Métrique là où l'entropie est
  nominale, mais elle plafonne à 0,715 sur l'uniforme : sa borne dépend de $k$ et de la largeur
  de bande, donc un seuil chiffré n'y serait pas lisible. Bon diagnostic, mauvaise norme.
- **`target_divergence`** — proximité à une distribution d'exposition **déclarée** par le
  régulateur. Seule à rendre explicite la forme visée, là où les autres la supposent : l'entropie
  suppose l'uniforme, l'entropie de Rao suppose l'écartement.
- **`centre_share` et `largest_gap`** — diagnostics de forme. Ce sont eux qui ont rendu le
  défaut visible, alors qu'aucune grandeur contrainte ne s'en émouvait.
- **`optimal_feed_under`** — optimiseur générique : toutes les mesures passent désormais par le
  même solveur, une comparaison entre normes ne valant que si l'optimisation est identique de
  part et d'autre.
- **`Feed`** porte le catalogue de référence complet et non son seul écart maximal, ce qui lui
  donne aussi la grille de bacs.
- 25 tests supplémentaires, dont le défaut de Rao énoncé comme test — il est reproductible,
  donc il est réel.

### Résultats — ce que le correctif retient

| Rôle | Mesure |
|---|---|
| plancher | entropie de position |
| publié à côté | plus grand vide, l'entropie étant nominale |
| successeur à instruire | proximité à une cible déclarée |

- **Recommandation 1 du mémorandum révisée une seconde fois.** Le plancher ne porte ni sur
  l'IDE des étiquettes, ni sur l'entropie de Rao des contenus, mais sur l'**entropie de
  position**, publiée avec le plus grand vide.
- **Pages corrigées en place** : `gaming`, `memorandum`, `feuille-de-route` (§2.1 et §2.2),
  `index` et README, qui présentaient tous l'entropie de Rao comme le remplacement retenu.

### Ajouté — test adverse de l'index, et réplication de l'annotation

Deux vérifications indépendantes, l'une sur le livrable réglementaire, l'autre sur la méthode
d'annotation. Détail : [`docs/gaming.md`](docs/gaming.md) et
[`docs/annotation.md`](docs/annotation.md).

- **`ide.gaming`** — test de saturabilité de l'index sous contrainte. Une plateforme maximise
  l'engagement sous plancher d'IDE ou d'entropie de Rao, avec une latitude paramétrée de
  découplage entre étiquette et contenu. La solution sous contrainte d'entropie est **exacte**
  (distribution de Boltzmann : le plancher agit comme une température), ce qui importe pour un
  résultat négatif.
- **`ide.annotation`** — $\kappa$ de Cohen, $\kappa$ de Fleiss, registre consensuel, et
  chargement des recodages indépendants.
- **`data/annotations_replication.json`** — deux recodages complets du corpus, sous la grille
  identique, à partir du même matériau présenté dans un ordre différent et sans l'étiquette de
  catégorie.
- **`notebooks/13_test_adverse_index.ipynb`**, section 8 à 10 du notebook 12, et 48 tests
  supplémentaires.

### Résultats — l'index n'est pas une norme tenable en l'état

- **Un plancher d'IDE se sature à coût nul.** Une plateforme capable de dissocier l'étiquette
  du contenu obtient un **IDE de 1,000 — la note maximale — pour une diversité de contenu
  strictement nulle**, sans céder un point d'engagement. Sur un catalogue honnête, le même
  plancher à 0,80 coûte 18 % d'engagement : la contrainte mord, et c'est bien la manipulation
  qui l'annule.
- **La dégradation devance largement le découplage.** À mi-découplage, la contrainte n'a plus
  que **36 %** de sa force ; à 80 %, il en reste 7 %.
- **L'entropie quadratique de Rao résiste, et inverse l'incitation.** Au-delà d'un découplage
  de moitié le plancher devient **inatteignable** ; en deçà, il coûte *plus* cher à mesure que
  la plateforme vide ses étiquettes — 16 % à découplage nul, 40 % à mi-découplage.
- **Une signature de manipulation**, définie comme excès sur la contrefactuelle honnête et non
  comme écart brut : nulle par construction pour une plateforme honnête, croissante avec le
  découplage. L'écart brut, lui, vaut déjà 0,36 sur un fil honnête et ne se prête donc à aucun
  seuil.
- **Recommandation 1 du mémorandum révisée** : le plancher ne porte plus sur l'IDE des
  étiquettes mais sur l'entropie de Rao des contenus, le régulateur fixant l'étendue du
  catalogue de référence.
- **Défaut corrigé en cours de route.** Une première version normalisait l'entropie de Rao par
  l'étalement effectivement servi. La mesure devenait invariante d'échelle et un fil réduit à
  un point y marquait $Q \approx 1$ sur du bruit d'arrondi — la conclusion publiée aurait été
  l'inverse de la vérité. Un test verrouille désormais le point.

### Résultats — la grille d'annotation est reproductible

- **$\kappa$ de Fleiss = 0,921** sur trois codages du même corpus ; accords deux à deux de
  0,903, 0,917 et 0,944 ; unanimité sur **92,3 %** des sujets.
- **Le désaccord tombe au bon endroit.** Sur 34 sujets non unanimes, **33** portent sur
  l'appartenance à un registre et **1** seul inverse `accusation` et `discovery` :
  l'imprécision résiduelle fait varier les effectifs de la comparaison, pas son sens.
- **Le résultat est inchangé sous le codage consensuel** : taux de basculement 4,3 % contre
  5,4 % ($p = 0{,}77$), persistance ×3,06 contre ×2,90 ($p = 0{,}84$).
- **Réserve maintenue :** les trois codeurs sont des instances du même modèle de langue.
  L'accord mesure la reproductibilité de la **grille**, non l'accord entre juges humains
  indépendants, et il le surestime nécessairement. La feuille de route en fait sa priorité n° 1.

### Résultats — l'annotation en aveugle tranche : l'écart n'existe pas

Détail : [`docs/annotation.md`](docs/annotation.md) et le
[notebook 12](notebooks/12_annotation_en_aveugle.ipynb).

- **Le bruit d'étiquetage est massif et mesuré.** 175 sujets sur 440 — **40 %** — ne relèvent
  d'aucun des deux registres, et l'accord entre catégorie et annotation n'atteint que
  **59,5 %**. Le bruit est asymétrique (31,8 % côté accusation, 47,7 % côté découverte) mais
  le registre franchement inversé est quasi nul : 3 sujets. C'est le profil d'un bruit qui
  dilue sans biaiser, tel que le corpus étendu l'avait supposé.
- **L'écart de taux de basculement disparaît.** 8,6 % contre 2,7 % (rapport de cotes 3,37,
  $p = 0{,}012$) devient **4,8 % contre 5,1 %** (rapport de cotes **0,93**, $p = 1{,}00$). Les
  sujets écartés basculent à 6,9 %, soit **plus souvent que les deux registres** : ce sont eux
  qui portaient l'écart. Quatre des cinq plus fortes élévations du corpus sont codées « ni
  l'un ni l'autre ».
- **Le déséquilibre d'audience était lui-même un effet de l'étiquetage.** Le trafic médian
  passe de 39 contre 11 vues/jour à 36 contre 26,5.
- **La persistance reste nulle, avec la puissance de conclure.** ×3,04 contre ×2,90
  ($p = 0{,}90$), robuste au retrait des sujets contaminés, des annotations incertaines et des
  sujets à faible trafic. À $n = 7$ contre 7, un écart aussi séparé que celui qu'annonçait le
  corpus pilote aurait été détecté ($p = 0{,}04$ avec quatre rangs de chevauchement).
- **Un défaut de plan d'expérience est révélé.** Correctement étiquetés, les deux registres ne
  portent presque pas sur les mêmes types de sujets — 58 événements et 63 concepts côté
  accusation, 58 objets et 39 personnes côté découverte. Les concepts ne basculent jamais
  (0/63 et 0/15). Une comparaison bâtie sur des catégories thématiques compare donc aussi des
  natures d'objets.
- **Bilan :** quatre mesures, aucun effet du registre émotionnel. La dernière hypothèse de
  sauvetage — la dilution par l'étiquetage — est éliminée. Le mécanisme de la charge
  émotionnelle $\alpha$ reste sans appui empirique.
- **Pages corrigées en place** : `corpus-etendu`, `regimes`, `memorandum` (dont la ligne
  « persistance » du tableau des points non mesurés, restée en ×9,2 contre ×2,9), `index`,
  README et feuille de route, dont la priorité n° 1 devient le double codage.

### Ajouté — pré-enregistrement de l'annotation en aveugle

Fixe la grille d'annotation manuelle du registre **avant** toute annotation, pour trancher
entre absence d'effet et effet dilué par le bruit d'étiquetage. Protocole :
[`docs/annotation.md`](docs/annotation.md).

- **`ide.annotation`** — grille à trois registres (`accusation`, `discovery`, `neither`),
  cinq règles de départage arrêtées d'avance, type de sujet et confiance en dimensions
  accessoires ; chargement d'annotations refusé si la version de grille diffère.
- **`scripts/fetch_extracts.py`** — fige le chapeau des 440 articles dans
  `data/extracts.json`, seule entrée de l'annotateur, dont l'empreinte SHA-256 est inscrite
  dans le fichier d'annotations.
- **Contamination déclarée** — les six sujets cités avec leur élévation dans la page du
  corpus étendu sont listés dans `ide.annotation.CONTAMINATED`, annotés comme les autres, et
  l'analyse est reprise sans eux.
- **`data/extracts.json` et `data/annotations.json`** — les chapeaux figés des 440 articles et
  leur codage manuel, avec l'empreinte SHA-256 des premiers inscrite dans le second.
- **`notebooks/12_annotation_en_aveugle.ipynb`** et 22 tests supplémentaires.

### Ajouté — corpus étendu et réplication

Met à l'épreuve, sur 440 sujets, le seul écart entre registres émotionnels que le projet
avait mesuré. Détail : [`docs/corpus-etendu.md`](docs/corpus-etendu.md).

- **`ide.catalogue`** — construction d'un corpus depuis dix-sept catégories de Wikipédia
  déclarées à l'avance, avec classes disjointes, filtre de substance et échantillonnage
  déterministe par empreinte de titre. Remplace le choix des *sujets* par celui des
  *catégories* : à trois cents titres, une sélection manuelle ne se relit plus.
- **`scripts/build_catalogue.py`** et le manifeste versionné `data/catalogue.json`.
- **Cache compressé** — `ide.pageviews` écrit désormais des fichiers `.json.gz`, ce qui
  ramène 440 séries quotidiennes sur onze ans de dix mégaoctets à trois.
- **`notebooks/11_corpus_etendu.ipynb`** et 40 tests supplémentaires.

### Résultats — le résultat du corpus pilote est infirmé

- **L'écart de persistance ne se réplique pas.** ×9,2 contre ×2,9 ($p = 0{,}08$) sur
  quatorze sujets choisis à la main devient **×3,04 contre ×2,90** ($p = 0{,}53$) sur 440
  sujets dérivés de catégories. Le corpus pilote contenait les théories du complot les plus
  connues — c'est précisément ce qu'une sélection manuelle produit.
- **L'écart de taux de basculement est un effet d'audience.** Les sujets d'accusation
  basculent trois fois plus souvent (8,6 % contre 2,7 %, $p = 0{,}014$), mais ils sont aussi
  trois fois et demie plus consultés ($p = 5\times10^{-14}$). À trafic comparable, le rapport
  de cotes tombe de 3,4 à 1,38 ($p = 0{,}63$) ; sur 173 paires appariées, McNemar donne
  $p = 0{,}18$.
- **Le nouveau protocole a son propre défaut.** L'appartenance à une catégorie est un
  indicateur bruité du registre — « Lil Tay » est dans une catégorie de canulars, mais son
  audience est celle d'une célébrité. Un bruit d'étiquetage attire tout écart vers zéro : le
  résultat nul est compatible avec l'absence d'effet **comme** avec un effet dilué.
- **Bilan :** aucune différence entre registres émotionnels ne résiste à sa vérification, ni
  par le taux d'amplification, ni par la persistance. Le mécanisme de la charge émotionnelle
  reste sans appui empirique.

### Modifié

- **Contrôle d'observabilité ajouté à `ide.regime`.** Le temps d'oubli doit tenir dans la
  fenêtre ajustée. Sans lui, deux transitions presque en marche d'escalier du corpus étendu
  produisaient des rapports de 697 et 5431 — soit des mémoires collectives de plusieurs
  années — avec une dispersion résiduelle excellente.
- **Affirmations corrigées** dans `docs/regimes.md`, le mémorandum et les pages d'accueil :
  l'écart de persistance y était présenté comme le premier écart mesuré du projet. Les
  sections concernées sont conservées, avec l'avertissement qui les infirme.

### Ajouté — détection de changement de régime

Traite l'angle mort de la calibration par pic : les désinformations qui ne flambent pas mais
s'installent. Détail et réserves : [`docs/regimes.md`](docs/regimes.md).

- **`ide.regime`** — segmentation binaire sur les logarithmes pour détecter les ruptures de
  niveau, localisation séparée du décollage de la transition, déduplication des escaliers de
  ruptures, correction de la périodicité hebdomadaire, et identification de
  $\gamma\alpha$, $\lambda$, $W_{\text{sat}}$ par ajustement de trajectoire.
- **`notebooks/10_changement_de_regime.ipynb`** et 58 tests supplémentaires (324 au total).

### Résultats — deux réussites à ne pas confondre

- **La détection fonctionne, et couvre l'angle mort.** 14 changements de régime sur le
  corpus, aux bonnes dates sans qu'aucune date ne lui soit fournie : affaire Benalla le
  20 juillet 2018, révélations Pegasus en juillet 2021, annonce de LIGO en février 2016,
  bascule QAnon en mars 2020. Et surtout dans les sujets que la méthode par pic manquait —
  QAnon, désinformation Covid-19, hésitation vaccinale.
- **L'identification échoue sur données réelles.** Zéro des 14 livre des paramètres
  exploitables : la dispersion résiduelle médiane est de 0,63, alors que l'incertitude
  relative sur le rapport atteint déjà 77 % à 0,15. La récupération est pourtant exacte sur
  trajectoire de synthèse, y compris pour $\rho = 40$ — c'est une inadéquation entre un
  modèle à trois paramètres et le bruit réel, non un défaut d'implémentation.
- **Une limite théorique domine les deux.** Sous saturation logistique, l'équation se réduit
  à une logistique à deux paramètres de forme : $\gamma\alpha/\lambda$ y est **structurellement
  non identifiable**, et deux triplets de rapports 5,0 et 1,7 produisent la même courbe.
  L'identifiabilité du rapport n'est donc pas une propriété des données mais une hypothèse
  sur la forme de la saturation.
- **Premier écart mesuré entre registres émotionnels.** L'élévation durable du palier vaut
  ×9,2 pour les contenus d'accusation contre ×2,9 pour les annonces de découverte
  ($p = 0{,}08$, n = 14). Ce n'est pas le taux d'amplification qui sépare les registres,
  c'est la durée pendant laquelle l'attention reste captée.

### Modifié

- **Recommandation 2 du mémorandum, à nouveau amendée.** Le plafond sur
  $\gamma\alpha/\lambda$ supposait le rapport mesurable ; il ne l'est ni sur les régimes
  installés, ni indépendamment d'une hypothèse de forme. Un indicateur de remplacement est
  proposé — date du basculement et élévation du palier — qui se mesure, distingue les
  registres, et porte sur ce qu'un régulateur cherche réellement à constater.
- **Table de correction de biais supprimée.** Une première version du module publiait une
  sous-estimation de 20 % à 10 % de bruit. Cette table était fausse : elle venait d'un
  prototype dont l'initialisation, un lissage aux bords corrompus, dégradait l'ajustement
  bien plus que le bruit. Corriger l'initialisation a supprimé le biais qu'il fallait
  soi-disant corriger. Elle est remplacée par une table de **précision**, mesurée sur la
  chaîne complète et non sur un ajustement isolé.

### Ajouté — calibration empirique de γα/λ

Première mesure d'un paramètre du modèle sur des données réelles. Détail et réserves :
[`docs/calibration.md`](docs/calibration.md).

- **`ide.calibration`** — identification de $\gamma\alpha$ et $\lambda$ par réduction de
  l'équation de résonance au premier ordre, avec deux estimateurs : fenêtres adaptatives, et
  fenêtres à horizon fixe. Détection d'épisodes par proéminence sur niveau de fond glissant,
  avec compte rendu des rejets par motif.
- **`ide.pageviews`** — accès à l'API de consultations de Wikimedia et cache sur disque.
  Filtre d'agent `user` par défaut, pour exclure les robots.
- **`ide.corpus`** — corpus pré-enregistré de 24 sujets, réparti en deux registres
  émotionnels. Figé dans le code afin qu'aucun sujet ne puisse être écarté au vu de son
  résultat.
- **`scripts/fetch_pageviews.py`** — seul point d'accès réseau du dépôt, exécuté une fois.
- **`data/pageviews/`** — les 24 séries, versionnées : l'analyse est reproductible hors
  ligne et un test vérifie que le corpus reste intégralement disponible.
- **`notebooks/09_calibration_visibilite.ipynb`** et 63 tests supplémentaires (266 au total).

### Résultats

- $\gamma\alpha/\lambda$ vaut **1,5 à 12** sur 19 épisodes, de médiane **2,5 à 4,2** selon
  l'estimateur. L'amplification est deux à quatre fois plus rapide que l'oubli.
- **Le critère de signe est vide** — nouveau point 15 de l'audit. Le rapport dépasse 1 dans
  tous les épisodes, par construction de la procédure d'estimation : un épisode observable a
  nécessairement connu une phase de croissance.
- **La prédiction sur la charge émotionnelle n'est pas étayée** : aucun écart détectable
  entre registres ($p \geq 0{,}13$), et l'estimation ponctuelle va dans le sens contraire.

### Modifié

- **Recommandation 2 du mémorandum réécrite** — d'une interdiction des configurations où
  $\gamma\alpha > \lambda$, inapplicable puisque toujours vraie, vers un **plafond sur le
  rapport** $\gamma\alpha/\lambda \leq \rho_{\max}$.
- `docs/limites.md` : ajout du point 15 et révision de la section sur la calibration, qui
  n'est plus absente mais seulement entamée.
- `ide.calibration.fit_exponential_rate` exige des valeurs strictement positives au lieu de
  les rabattre sur un plancher — un rabattement aplatissait silencieusement les
  décroissances et produisait un taux nul.

### À faire

Priorisé dans [`docs/feuille-de-route.md`](docs/feuille-de-route.md). En tête désormais :

- **détecter des changements de régime, et non des pics** — la calibration actuelle ne voit
  pas les désinformations qui s'installent, soit précisément les cas archétypaux ;
- résolution infra-quotidienne, et décroissance non exponentielle ;
- test adverse de manipulabilité de l'IDE, entièrement simulable ;
- évaluation hors ligne de l'ADE sur un jeu de données de recommandation réel.

## [0.1.0] — 2026-08-17

Première mise en forme du travail : passage d'un fil de discussion à un dépôt
scientifique reproductible, bilingue et publié.

### Ajouté

- **Noyau scientifique** `src/ide/` — modules purs, sans entrée-sortie, à graine
  explicite : entropies de Shannon et de von Neumann, calcul de l'IDE, modèle d'Ising 2D
  par Metropolis en damier avec champ externe et cycle d'hystérésis, Voter Model avec
  dérive de désinformation, énergie libre de champ moyen et solveur de Fokker-Planck en
  volumes finis, cinétique de résonance saturée, score de recommandation de l'ADE avec
  recuit, et modèle à agents « compas politique ».
- **Module de tracé** `ide.plotting` — style et palette communs à toutes les figures,
  isolé du noyau parce que `matplotlib` est une dépendance facultative.
- **Suite de 203 tests** — température critique d'Onsager retrouvée à ±0,25 sur un réseau
  24×24, conservation de la masse de probabilité à 10⁻¹⁵, bimodalité sous $T_c$ et
  unimodalité au-dessus, exposants des lois d'échelle du temps de consensus, aire du
  cycle d'hystérésis strictement positive sous $T_c$ et nulle au-dessus, équivalence de
  l'ADE avec un filtre d'engagement à $\mu = 0$, reproductibilité à la graine du modèle à
  agents. Les exemples des docstrings sont exécutés avec la suite.
- **Notebooks** `01` à `08` — un par bloc théorique, exécutables en conteneur, produisant
  l'intégralité des figures de la note.
- **Documentation bilingue** publiée sur GitHub Pages — théorie, index IDE, algorithme
  ADE, mémorandum de régulation ARCOM/DSA. Les pages de théorie sont en français, avec
  repli automatique depuis l'anglais ; la note scientifique anglaise couvre la science.
- **Note scientifique** `paper/` en LaTeX, versions française (9 pages) et anglaise
  (8 pages), compilées en conteneur texlive avec bibliographie BibTeX.
- **Audit critique** [`docs/limites.md`](docs/limites.md) — quatorze corrections
  documentées et traçables, plus les limites qui subsistent, y compris celles qui portent
  sur l'usage réglementaire de l'index : manipulabilité, arbitraire de la discrétisation
  en points de vue, vie privée, et le fait qu'un plancher d'IDE est une intervention sur
  le débat public et non une simple mesure technique.
- **Feuille de route** [`docs/feuille-de-route.md`](docs/feuille-de-route.md) — une piste
  concrète par limite, classée par rapport valeur/effort.
- **Errata** [`docs/errata.md`](docs/errata.md) — table de correspondance ligne à ligne
  avec le fil de travail d'origine.
- **Environnement conteneurisé** — services `lab`, `test`, `lint`, `notebooks`, `site`,
  `site-build` et `latex` ; aucune dépendance installée sur la machine hôte.
- **Intégration continue** — tests, lint, exécution des notebooks et build du site à
  chaque push ; déploiement automatique de la documentation.

### Modifié par rapport au fil de travail d'origine (14 août 2026)

Les cinq premières entrées corrigent des **formules invalides**.

- **Signe du coefficient de régulation** — le score de l'ADE est fixé à
  `S = Pertinence + μ·ΔH` avec `μ ≥ 0`. Le fil hésitait entre `-μ·ΔH` et `+μ·ΔH` ; la
  version négative refermait la bulle qu'elle prétendait ouvrir. Le code refuse désormais
  un `μ` négatif par une exception explicite.
- **Dérive de l'équation de Fokker-Planck** — `A(x) = Jx + H` est remplacée par
  `A(x) = Jx + H - T·artanh(x)`. Sans le terme entropique de mélange, la distribution
  stationnaire est convexe : le modèle ne pouvait produire **aucune transition de phase**,
  et la dynamique n'était pas bornée. La correction fait apparaître l'énergie libre
  `F = E - TS` que le fil invoquait sans l'écrire, et une température critique de champ
  moyen `T_c = J`.
- **Probabilités de transition du Voter Model biaisé** — la forme du fil,
  `P(x → x-1/N) = x(1-x) - hx`, devient négative dès que `h > 1-x`. Les deux canaux
  d'influence sont désormais mélangés plutôt qu'additionnés.
- **Signe du rappel dans l'équation de résonance** — `-ω₀²V` est corrigé en `+ω₀²V`. Le
  signe d'origine rendait le système instable même à gain algorithmique nul, ce qui privait
  de tout contenu le critère `γα > λ`.
- **Cinétique de résonance bornée** — ajout d'un facteur de saturation traduisant la
  finitude de l'attention. La version d'origine divergeait exponentiellement sans limite,
  ce qui rendait impossible toute comparaison entre configurations.
- **Effet de la taille du système reformulé** — l'entropie de configuration totale croît
  avec `N`, mais le bruit de la variable macroscopique décroît en `1/N`. La thèse retenue
  est qu'une grande population devient **rigide**, non bruyante — ce qui explique
  l'irréversibilité de la polarisation, contrairement à la métaphore de la « pompe à
  entropie ».
- **Argument sur la connectivité corrigé** — le temps de consensus croît en `N` en champ
  moyen contre `N²` sur un anneau : un réseau globalisé converge **plus vite**. Ce ne sont
  donc pas les liens qui fragmentent, mais le biais directionnel et l'homophilie.
- **Statut des analogies requalifié** — l'entropie qui croît sous décohérence est celle du
  sous-système réduit, non du système fermé ; l'effet tunnel social devient une métaphore,
  le mécanisme correct étant le franchissement de barrière par activation thermique
  (Kramers) ; `1/k^N` décrit un état initial et non une dynamique ; `τ_D ∝ τ_R/N` est
  étiqueté loi d'échelle heuristique.
- **Nomenclature dissociée** — l'**IDE** désigne l'*index* métrologique, l'**ADE**
  l'*algorithme* de filtrage. Le fil employait les deux sigles indifféremment, ce qui
  rendait la proposition réglementaire ambiguë : impose-t-on une mesure ou une
  implémentation ?
- **Conclusion du mémorandum nuancée** — la formule « la régulation devient une ingénierie
  de la stabilité » est conservée, accompagnée de la réserve qu'une ingénierie de la
  stabilité *est* une intervention sur le débat public.

### Ajouté au modèle à agents

- **Température sociale** — le paramètre central de toute la théorie était absent de sa
  seule implémentation. Sans agitation individuelle, le conformisme fait converger la
  population vers un point unique : l'IDE tombe à zéro quels que soient les autres
  réglages, et le modèle ne pouvait représenter ni le débat fluide ni l'effet du bruit
  thermique qu'il recommandait d'injecter.
- **Radicalisation progressive** à la contamination, en remplacement de la téléportation
  dans un coin du compas, qui supprimait toute dynamique ultérieure.
- **Vérification probabiliste** — l'efficacité des fact-checkers est paramétrable, là où le
  prototype soignait avec certitude tout individu à portée.
- **Bords réfléchissants** — la troncature des opinions accumulait les individus agités sur
  les bords, ce qui faisait chuter l'IDE à haute température pour une raison purement
  numérique.

### Archivé

- [`legacy/simulation_thread_2026-08.py`](legacy/) — la simulation `pygame` du fil
  d'origine, conservée **sans correction**, y compris son indentation perdue à
  l'impression. Ses cinq défauts et ses trois bons choix sont documentés dans
  [`legacy/README.md`](legacy/README.md).

### Note sur la source

Le fil de travail source est une impression Gmail rasterisée, sans couche de texte. Il n'a
pas été commité : il contient des adresses électroniques personnelles et
professionnelles. Son contenu a été réécrit, non copié.

[Non publié]: https://github.com/s-geffroy/Index-Dissipation-Entropique/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/s-geffroy/Index-Dissipation-Entropique/releases/tag/v0.1.0
