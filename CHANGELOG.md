# Changelog

Toutes les évolutions notables de ce projet sont consignées dans ce fichier.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le
versionnement respecte [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

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
