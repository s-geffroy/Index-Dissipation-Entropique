# Feuille de route : les limites et comment les combler

L'[audit critique](limites.md) énumère ce que ce travail ne peut pas faire. Cette page
propose, pour chaque limite, une piste concrète — avec l'idée qu'une limite sans piste
est un aveu, et qu'une limite avec piste est un programme.

Les entrées sont classées par **rapport valeur / effort**, pas par ordre logique.

---

## Priorité 1 — La calibration empirique

**La limite.** Les paramètres $J$ (conformisme), $T$ (température sociale), $\gamma$
(gain algorithmique), $\alpha$ (charge émotionnelle) n'ont aucune procédure d'estimation
sur données réelles. C'est la faiblesse principale : sans elle, le formalisme est
cohérent mais flottant, et aucun seuil réglementaire n'est calibrable.

**Pistes, du plus accessible au plus ambitieux.**

### 1.1 Estimer $\lambda$ et $\gamma\alpha$ sur des courbes de visibilité publiques

!!! success "Fait — voir [Calibration](calibration.md)"
    Le rapport $\gamma\alpha/\lambda$ vaut **1,5 à 12** sur 19 épisodes d'attention
    publics (consultations Wikipédia, agent `user`, corpus pré-enregistré de 24 sujets),
    de médiane **2,5 à 4,2** selon l'estimateur.

    Trois enseignements, dont deux négatifs :

    * l'ordre de grandeur existe — l'amplification est deux à quatre fois plus rapide que
      l'oubli ;
    * **le critère de signe est vide** : il est satisfait par construction pour tout
      épisode observable, ce qui a imposé de réécrire la recommandation 2 du mémorandum
      en plafond sur le rapport ;
    * **la prédiction sur la charge émotionnelle n'est pas vérifiée** ($p \geq 0{,}13$),
      et l'estimation ponctuelle va dans le sens contraire.

    Livré : `ide.calibration`, `ide.pageviews`, `ide.corpus`,
    `scripts/fetch_pageviews.py`, cache versionné de 24 séries, 40 tests, et le
    [notebook 09](notebooks/09_calibration_visibilite.ipynb).

Les suites directes de cette mesure, par ordre d'importance :

* **Détecter des changements de régime, pas des pics.** → **[fait](regimes.md)**, avec un
  résultat en deux temps. La détection fonctionne et couvre l'angle mort : 14 changements
  aux bonnes dates, QAnon et la désinformation sanitaire compris. Mais l'identification des
  paramètres échoue sur données réelles — la dispersion résiduelle y est quatre fois trop
  élevée — et une limite théorique la borne de toute façon : le rapport n'est pas
  identifiable sous une saturation logistique. L'écart de **persistance** entre registres
  émotionnels, ×9,2 contre ×2,9, y apparaissait comme le premier écart mesuré du projet —
  mais il **ne s'est pas répliqué** à l'échelle (voir l'entrée suivante).
* **Passer à une résolution infra-quotidienne.** Le motif de rejet dominant est la
  fenêtre trop courte : beaucoup d'épisodes montent en un ou deux jours. Wikimedia
  publie des séries horaires sur une profondeur limitée ; cela suffirait à rendre
  identifiable ce qui ne l'est pas ici.
* **Ajuster une décroissance non exponentielle.** La queue de l'attention est plus lourde
  qu'une exponentielle, ce qui produit un artefact de fenêtre sévère (corrélation de rang
  $-0{,}94$ entre durée de fenêtre et $\lambda$), aujourd'hui contourné par un horizon
  fixe. Une loi de puissance ou une somme de deux exponentielles le supprimerait.
* **Étendre le corpus.** → **[fait](corpus-etendu.md)** : 440 sujets dérivés de dix-sept
  catégories de Wikipédia, pour remplacer le choix des sujets par celui des catégories.
  La réponse est venue, et elle est négative — l'écart de persistance du corpus pilote **ne
  se réplique pas** (×3,04 contre ×2,90, $p = 0{,}53$), et l'écart de taux de basculement
  s'explique par un déséquilibre d'audience d'un facteur 3,5. L'extension a aussi révélé un
  défaut de son propre protocole : l'appartenance à une catégorie est un indicateur bruité du
  registre.
* **Annoter le registre à la main, en aveugle.** → **[fait](annotation.md)** sur les 440
  sujets, sous une grille pré-enregistrée. Le bruit d'étiquetage est mesuré à 40 % de sujets
  hors registre, et il portait la totalité de l'écart de taux de basculement : le rapport de
  cotes tombe de 3,37 à **0,93** ($p = 1{,}00$). La dernière hypothèse de sauvetage est
  éliminée — l'écart n'était pas dilué, il n'existe pas. L'annotation a aussi révélé un
  **défaut de plan d'expérience** : correctement étiquetés, les deux registres ne portent
  presque pas sur les mêmes types de sujets.

### 1.2 Inférer les coefficients de Fokker-Planck directement

* **Méthode.** Estimation des coefficients de Kramers-Moyal : à partir d'une série
  temporelle de la variable macroscopique $x(t)$, les moments conditionnels des
  incréments donnent $A(x)$ et $B(x)$ **sans supposer leur forme**. On peut alors
  comparer la dérive mesurée à $Jx + H - T\,\mathrm{artanh}(x)$ — et donc **tester le
  modèle** plutôt que l'ajuster.
* **Sources.** Séries longues de sondages d'opinion (Eurobaromètre, baromètres de
  confiance), qui fournissent des $x(t)$ agrégés sur des décennies.
* **Difficulté.** La fréquence d'échantillonnage des sondages est basse ; la méthode
  demande une résolution temporelle que seules les données de plateformes offriraient.

### 1.3 Utiliser l'accès aux données de l'article 40 du DSA

Le DSA ouvre aux chercheurs agréés un accès aux données des très grandes plateformes.
C'est la voie qui permettrait une vraie calibration de $T$ et du seuil d'IDE — et le
PEReN, cité dans le mémorandum, est précisément l'interlocuteur pour cela.

* **Prérequis.** Un protocole d'accès formalisé, un rattachement institutionnel, et un
  plan de traitement respectant les contraintes de vie privée (voir §2.3).
* **À faire d'abord.** Les points 1.1 et 1.2 sur données publiques : ils constituent le
  dossier qui rend une demande d'accès crédible.

---

## Priorité 2 — La robustesse de l'index

### 2.1 Sortir de la discrétisation arbitraire en points de vue

**La limite.** Qui définit les $k$ modalités définit l'index. Le découpage n'est pas un
acte technique neutre.

**Pistes.**

* **IDE multi-échelle.** Plutôt qu'un $k$ unique, mesurer l'index pour plusieurs
  granularités et publier la **courbe** $\mathrm{IDE}(k)$. Une bulle réelle s'effondre à
  toutes les échelles ; un artefact de découpage ne le fait pas. Cela transforme le
  choix de $k$ en résultat au lieu d'un paramètre caché.
* **Entropie sur espace continu.** Remplacer la distribution de modalités par une
  distribution dans un espace d'*embeddings* sémantiques, et estimer l'entropie
  différentielle par des méthodes à $k$ plus proches voisins (Kozachenko-Leonenko).
  Plus d'étiquettes, donc plus d'arbitraire de découpage — au prix d'une dépendance au
  modèle d'*embedding*, qui est un arbitraire déplacé plutôt que supprimé.
* **Entropie calculée sur les contenus, non sur les étiquettes.** ~~L'entropie quadratique
  de Rao~~ — écartée en §2.2, son optimum sous contrainte étant bimodal. Ce qui subsiste de
  l'idée est plus simple : projeter les contenus servis sur les points de vue du catalogue et
  y calculer l'entropie habituelle. C'est aussi la meilleure défense contre la manipulation.

### 2.2 Rendre l'index résistant au *gaming*

!!! failure "Fait — et l'objection est fondée : voir [Test adverse](gaming.md)"
    Le test de saturabilité a été mené par simulation. Une plateforme capable de dissocier
    l'étiquette du contenu obtient un **IDE de 1,000 pour une diversité de contenu nulle**, à
    coût d'engagement nul ; et à mi-découplage, la contrainte n'a plus que **36 %** de sa
    force. **Un plancher d'IDE sur les étiquettes n'est pas une norme tenable.**

    Le remplacement d'abord proposé — l'**entropie quadratique de Rao** — s'est révélé
    défectueux à son tour : c'est la distance intra-liste, dont l'optimum sous contrainte est
    **bimodal**. Un plancher de Rao prescrirait la polarisation. Le plancher retenu porte
    finalement sur l'**entropie de position** — l'IDE calculé sur les contenus servis — publié
    avec un diagnostic de plus grand vide. La [recommandation 1 du mémorandum](memorandum.md)
    a donc été révisée deux fois.

**La limite.** Une plateforme contrainte de maintenir un IDE élevé peut servir des
contenus formellement divergents mais substantiellement vides.

**Pistes.**

* **Test adverse explicite.** Modéliser une plateforme qui maximise l'engagement **sous
  contrainte** d'IDE minimal, et mesurer l'IDE atteignable avec de la diversité
  d'étiquette pure. Si la contrainte est saturable sans coût, l'index est inutilisable
  en l'état — et il vaut mieux le savoir avant d'en faire une norme. C'est un problème
  d'optimisation sous contrainte, donc entièrement simulable : **aucune donnée réelle
  n'est nécessaire pour trancher ce point.**
* **Passage à une mesure portant sur les contenus servis**, et non sur les étiquettes qui
  les annoncent. Le remplissage par étiquettes n'y produit aucun gain. Attention au choix de
  la mesure : l'entropie quadratique de Rao satisfait ce critère et **échoue sur un autre**,
  son optimum sous contrainte étant bimodal.
* **Contrôle qualitatif d'échantillon** en complément de la mesure automatique, à
  inscrire dans la norme technique.

### 2.3 Concevoir un protocole d'audit préservant la vie privée

**La limite.** Mesurer l'IDE de fils individuels suppose d'observer ce qui est servi à
des personnes.

**Pistes.**

* **Réponse randomisée** sur les étiquettes de points de vue : chaque client déclare sa
  modalité avec une probabilité de brouillage connue. L'entropie de la distribution
  agrégée se dé-biaise analytiquement, et la garantie de confidentialité locale est
  quantifiée par un $\varepsilon$.
* **Estimation de la queue plutôt que de la moyenne.** La grandeur réglementaire
  proposée est la *part de population sous le seuil*. Un quantile s'estime avec moins
  d'information qu'une distribution complète — la contrainte de vie privée est donc
  moins forte qu'il n'y paraît.
* **Livrable.** Une note séparée sur le protocole, avec budget $\varepsilon$ explicite.

---

## Priorité 3 — Valider le modèle contre la réalité

### 3.1 Évaluer l'ADE hors ligne sur un jeu de données réel

**La limite.** L'ADE est validé sur son propre modèle, avec une pertinence synthétique
et quatre points de vue. Son coût en pertinence perçue n'est pas évalué.

**Piste — probablement le meilleur rapport valeur/effort du dépôt.** Les jeux de données
publics de recommandation d'actualités (type MIND, *Microsoft News Dataset*) fournissent
à la fois des historiques de consultation réels et des **catégories éditoriales**, donc
des étiquettes de points de vue déjà disponibles. On peut :

1. calculer l'IDE réel des fils observés — première mesure de l'index sur données
   authentiques ;
2. réordonner ces fils avec l'ADE ;
3. mesurer le compromis entre gain d'IDE et perte de pertinence (nDCG), et tracer la
   **frontière de Pareto**.

C'est ce qui permettrait de répondre à la seule objection sérieuse d'une plateforme :
*combien ça coûte*. Et cela ne demande aucun accès privilégié aux données.

!!! danger "Trois conditions, sans lesquelles cette mesure ne mesure rien"
    → **[Rang et contrefactuel](evaluation.md)** a établi que le protocole ci-dessus, pris au
    pied de la lettre, est **faux**.

    1. la diversité doit se mesurer par une **divergence consciente du rang** à une référence
       déclarée. Sans quoi une plateforme s'y conforme en **enterrant** les contenus
       divergents : à composition identique, cela rapporte 10 % d'engagement et aucune mesure
       ponctuelle ne le voit ;
    2. le coût en pertinence doit s'estimer par **IPS ou SNIPS**, jamais par *replay* sur les
       clics enregistrés. Le replay se trompe de **201 % en médiane**, jusqu'à 851 %, et son
       sens n'est pas garanti — il n'offre donc même pas une borne ;
    3. le **modèle de propension**, la **taille d'échantillon effective** et le **plafond**
       doivent être publiés avec le chiffre ;
    4. la **sévérité du biais de position doit être estimée**, non posée — poser $\eta$ au
       jugé coûte jusqu'à 179 % d'erreur — et l'**exploration du jeu de données** doit être
       vérifiée d'abord, car c'est elle qui décide si l'estimation est seulement possible.
       → [Rang adverse et sévérité](rang-adverse.md)

    Sans ces trois conditions, la frontière de Pareto annoncée mesurerait surtout le biais de
    position de la plateforme qui a produit les données.

!!! failure "Et la quatrième condition n'est pas remplie par MIND — c'est mesuré"
    → **[L'exploration réelle de MIND](mind.md)**. L'ordre enregistré dans `behaviors.tsv` est
    **mélangé** : le test d'échangeabilité intra-fil n'y détecte rien ($z = +0{,}12$ sur 156 965
    fils, répliqué à $z = +0{,}28$ sur le second découpage) là où il verrait $\eta = 0{,}02$ à
    douze écarts-types.

    Trois conséquences pour cette piste :

    1. l'estimation contrefactuelle du coût d'engagement — le point 3 du protocole, et l'objet
       même de l'exercice — est **impossible sur MIND**. Non par manque de données, mais par
       absence de la variable qui identifierait l'exposition ;
    2. les points 1 et 2 restent faisables : l'IDE des fils observés et le réordonnancement se
       mesurent sans modèle d'exposition, à condition de dire que le coût publié est un coût en
       pertinence **déclarée** ;
    3. le choix du jeu de données devient le premier travail, pas le dernier. Le critère n'est
       plus la taille ni la présence d'étiquettes éditoriales, mais l'**enregistrement du rang
       servi**.

    Le contrôle est désormais outillé : `ide.mind.exchangeability_test` et son étalonnage de
    puissance, à passer sur tout journal public **avant** d'en tirer un chiffre.

!!! success "Deux journaux publics enregistrent le rang — le critère est réglé, la piste ne l'est pas"
    → **[Journaux qui enregistrent le rang](rang-servi.md)**. **Baidu-ULTR** enregistre le rang
    d'affichage : le test y rejette à $z = -206$, du bon côté, et la sévérité vaut
    $\hat\eta = 1{,}10 \pm 0{,}09$. L'**Open Bandit Dataset** publie en outre la propension
    vraie et contient un seau à politique aléatoire : l'estimateur IPS de ce dépôt y retrouve à
    **2,5 %** la valeur d'une politique jamais déployée, contre **+32 %** pour l'estimation naïve.

    Trois acquis et un blocage :

    * le **critère de choix** d'un jeu de données est établi, et vérifiable avant toute mesure ;
    * la **sévérité se mesure** — mais elle dépend de la surface : dix fois plus faible sur un
      bandeau de trois vignettes que sur une page de résultats. Elle ne se transporte pas ;
    * les **estimateurs contrefactuels tiennent** devant une vérité terrain, avec une taille
      d'échantillon effective de 1 513 pour 4 millions d'impressions — le chiffre à publier ;
    * **aucun jeu public ne porte à la fois le rang servi et une étiquette de point de vue
      interprétable.** MIND a les catégories sans le rang, Baidu-ULTR le rang sans étiquette,
      l'Open Bandit Dataset le rang avec des attributs anonymisés.

    Ce qui reste faisable, et qui remplace le protocole initial :

    1. mesurer sur MIND ce qui ne dépend pas de l'exposition, en le disant ;
    2. mesurer sur Baidu-ULTR et l'Open Bandit Dataset ce qui ne dépend pas des points de vue ;
    3. pour le reste, **demander la donnée** au titre de l'article 40 du DSA — la seule voie qui
       reste, et une voie prévue.

!!! success "Et la demande est écrite, spécifiée et vérifiée"
    → **[Demande au titre de l'article 40](article-40.md)**. Elle ne réclame ni journal ni
    donnée personnelle, mais **quatre tableaux agrégés** dont le
    [notebook 18](notebooks/18_demande_article_40.ipynb) vérifie qu'ils recalculent **à
    l'identique** le test d'échangeabilité, la sévérité $\eta$ et les deux mesures de diversité
    — écart de $3 \times 10^{-12}$ pour l'un, exactement nul pour l'autre.

    Ce qui est demandé pèse **95 fois moins de lignes** que le journal brut sur Baidu-ULTR, 101
    fois moins sur MIND. Une demande de cette forme ne peut être écartée pour disproportion sans
    que le motif porte sur autre chose que sa taille.

    Reste l'obstacle qui n'est pas technique : l'article 40(8)(a) exige une **affiliation à un
    organisme de recherche**, que ce dépôt n'a pas. Le document est donc un modèle prêt à
    déposer, et c'est la forme la plus utile qu'il pouvait prendre.

### 3.2 Formuler une prédiction falsifiable

**La limite.** Rien ne démontre que les opinions *obéissent* à cette mécanique ; le
travail montre qu'elle *reproduit* des comportements observés.

**Piste.** La loi de Kramers donne une prédiction quantitative que l'analogie de l'effet
tunnel ne donnait pas : le taux de basculement d'un extrême à l'autre varie comme
$e^{-\Delta V / k_B T}$. C'est **testable** sur des données de panel longitudinales
(mêmes individus suivis dans le temps) : la fréquence des basculements extrême-à-extrême
doit dépendre exponentiellement de l'inverse de la diversité d'exposition.

Une prédiction fausse serait un résultat ; c'est ce qui manque le plus à l'édifice pour
cesser d'être une analogie.

### 3.3 Étude systématique de sensibilité

Les notebooks explorent des régimes choisis pour être lisibles. À compléter par :

* des **balayages de paramètres** systématiques avec intervalles de confiance ;
* une **analyse d'échelle en taille finie** pour $T_c$ — cumulant de Binder plutôt que
  pic de susceptibilité, ce qui donnerait une extrapolation propre à la limite
  thermodynamique au lieu de la tolérance de ±0,25 actuellement nécessaire ;
* un budget de calcul en intégration continue, avec les simulations longues déportées
  dans un *job* nocturne.

---

## Priorité 4 — Étendre le modèle

### 4.1 Réseaux co-évolutifs

**La limite.** La topologie est fixée, sauf par le seuil de bulle. Or les individus
coupent des liens et se réorganisent.

**Piste.** Ajouter une règle de *rewiring* homophile au modèle à agents : un individu en
désaccord persistant coupe le lien et se reconnecte à un semblable. L'enjeu est précis
et vaut d'être testé : **la fragmentation que le raisonnement d'origine attribuait à tort
à la connectivité s'explique-t-elle entièrement par l'homophilie ?**
L'[audit, point 12](limites.md) l'affirme sans le démontrer.

### 4.2 La plateforme comme acteur stratégique

**La limite.** Un bain thermique ne poursuit pas d'objectif ; un algorithme optimise une
fonction de coût. C'est le point où l'analogie physique est la plus fragile.

**Piste.** Formuler le problème comme un **jeu de Stackelberg** : le régulateur fixe une
contrainte d'IDE, la plateforme maximise l'engagement sous cette contrainte, les
utilisateurs réagissent. Le formalisme des jeux à champ moyen est le prolongement naturel
de l'équation de Fokker-Planck déjà écrite — la transition est technique, pas
conceptuelle. C'est la voie qui rendrait le mémorandum réellement prescriptif : on
saurait quel seuil produit quel comportement d'une plateforme rationnelle.

### 4.3 Opinions multidimensionnelles et continues

Le modèle à agents utilise déjà deux axes continus. À prolonger vers les modèles de
confiance bornée (Deffuant, Hegselmann-Krause), dont le paramètre de tolérance est
l'exact analogue du seuil de bulle — ce qui permettrait de raccrocher le travail à une
littérature établie plutôt qu'à un modèle ad hoc.

---

## Priorité 5 — Dette du dépôt

Ces points n'ont pas d'enjeu scientifique, mais ils conditionnent la relecture.

| Élément | État | À faire |
|---|---|---|
| Pages théoriques en anglais | FR uniquement, repli automatique | traduire `theorie/*.md` ; la note LaTeX anglaise couvre déjà la science |
| Note LaTeX | compilée, FR + EN | soumission arXiv (catégorie `physics.soc-ph`) |
| Calibration des figures | régimes choisis à la main | ajouter les intervalles de confiance issus de §3.3 |
| Modèle à agents | seuil de bulle statique | rendre le seuil dynamique, piloté par un ADE simulé, pour boucler la théorie sur elle-même |
| Tests longs | marqués `slow`, exécutés localement | *job* d'intégration continue nocturne |

---

## Si une seule chose devait être faite

**Faire déposer la demande d'accès aux données par un organisme de recherche.**

C'est le seul verrou que ce dépôt ne peut pas lever seul, et c'est celui qui commande tous les
autres. La [demande](article-40.md) est écrite, spécifiée article par article du règlement
délégué (UE) 2025/2050, et **vérifiée** : les quatre tableaux agrégés qu'elle réclame
recalculent à l'identique le test d'échangeabilité, la sévérité du biais de position et les deux
mesures de diversité, pour 95 fois moins de lignes que le journal brut et sans aucune donnée
personnelle. Il ne lui manque qu'un déposant éligible au sens de l'article 40(8)(a).

Sans elle, trois choses restent hors de portée, et le resteront quels que soient les progrès de
méthode :

* **mesurer l'IDE sur un fil réel** — la forme retenue n'a jamais été calculée ailleurs qu'en
  simulation ;
* **évaluer le coût d'engagement de l'ADE** autrement que sur son propre modèle ;
* **vérifier que l'enterrement se produit vraiment** sur une plateforme, plutôt que sur des fils
  de huit positions énumérés exhaustivement.

### Ce qui vient juste après

**Des annotateurs humains.** Les trois codeurs du corpus sont des instances du même modèle de
langue : leur accord — $\kappa$ de Fleiss de **0,921**, unanimité sur 92 % des sujets —
surestime nécessairement ce que produiraient des juges indépendants. C'est la dernière réserve
de méthode qui ne se lève pas par le calcul. Elle ne changerait toutefois pas la conclusion :
l'annotation en aveugle a **éliminé** l'écart de registre, et quatre mesures indépendantes n'en
retrouvent aucune trace.

~~**Des lignes de base réglées** — MMR, réordonnancement aléatoire, popularité.~~ →
**[fait](lignes-de-base.md)**, et le verdict est mitigé : le filtre du dépôt tient la frontière
exacte, mais MMR — publié en 1998 — la tient aussi, et le devance au plancher 0,80. Le filtre ne
se détache qu'à l'exigence haute, où il atteint la contrainte quatre fois plus souvent. La
mesure a aussi isolé une dépendance que personne n'avait vue : **le prix de la norme dépend du
lecteur**, de 3,8 % à 17,1 % selon que ses intérêts traversent les points de vue ou s'y
confondent.
