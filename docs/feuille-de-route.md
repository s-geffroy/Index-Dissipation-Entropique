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
* **Entropie quadratique de Rao.** $Q = \sum_{ij} p_i p_j d_{ij}$, qui pondère la
  diversité par la **distance sémantique** entre points de vue. Voir §2.2 : c'est aussi
  la meilleure défense contre la manipulation.

### 2.2 Rendre l'index résistant au *gaming*

**La limite.** Une plateforme contrainte de maintenir un IDE élevé peut servir des
contenus formellement divergents mais substantiellement vides.

**Pistes.**

* **Test adverse explicite.** Modéliser une plateforme qui maximise l'engagement **sous
  contrainte** d'IDE minimal, et mesurer l'IDE atteignable avec de la diversité
  d'étiquette pure. Si la contrainte est saturable sans coût, l'index est inutilisable
  en l'état — et il vaut mieux le savoir avant d'en faire une norme. C'est un problème
  d'optimisation sous contrainte, donc entièrement simulable : **aucune donnée réelle
  n'est nécessaire pour trancher ce point.**
* **Passage à l'entropie quadratique de Rao**, qui ne récompense la diversité qu'à
  proportion de la distance sémantique réelle entre les contenus servis. Le remplissage
  par étiquettes n'y produit aucun gain.
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

**Faire annoter le corpus par un second codeur, en aveugle, et publier le $\kappa$ de Cohen.**

L'annotation manuelle du registre — priorité n° 1 de la version précédente de cette page — a
été [menée sur les 440 sujets](annotation.md) et a tranché la question qu'elle devait trancher.
Le bruit d'étiquetage était massif (40 % des sujets hors registre, 59,5 % d'accord seulement)
et il portait la totalité de l'écart de taux de basculement, qui tombe de 8,6 % contre 2,7 % à
4,8 % contre 5,1 %. **L'écart n'était pas dilué, il n'existe pas.**

**Quatre mesures ont donc été menées, et aucune ne distingue les registres émotionnels** : le
taux d'amplification, la persistance sur corpus pilote puis étendu, et le taux de basculement.
Le mécanisme de la charge émotionnelle $\alpha$ reste sans appui empirique, et ce n'est plus
faute d'avoir cherché.

Ce qui subsiste est une réserve de **méthode**, et une seule : l'annotateur était unique, donc
il n'existe aucune mesure de la fiabilité du codage. La grille est écrite et publiée, elle est
donc réplicable ; un second codage à l'aveugle, sur le même corpus, coûterait quelques heures
et retirerait la dernière prise qu'un relecteur puisse avoir sur ce résultat.

**Ce qu'il ne faut probablement pas faire**, en revanche, c'est une cinquième mesure du même
objet. Trois quantités tirées de la même série d'attention agrégée ont été testées sans succès,
et l'annotation a montré au passage que le plan d'expérience lui-même est contraint : les deux
registres, correctement étiquetés, ne portent presque pas sur les mêmes types de sujets. Si le
mécanisme existe, c'est ailleurs qu'il faut le chercher — voir §3.1 et §3.2.
