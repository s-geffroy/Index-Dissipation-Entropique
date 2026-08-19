# Indice de Diversité Exposée (IDE)

**Mesurer la diversité qu'un fil algorithmique expose réellement — et éprouver ce qu'on croit en savoir.**

[![Licence : MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Documentation : CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey.svg)](LICENSE-DOCS)
[![Champ : sociophysique](https://img.shields.io/badge/champ-sociophysique-8a2be2.svg)](https://s-geffroy.github.io/Index-Dissipation-Entropique/)
[![Tests : 556](https://img.shields.io/badge/tests-556-brightgreen.svg)](tests/)

📖 **[Documentation complète](https://s-geffroy.github.io/Index-Dissipation-Entropique/)**
· [English](https://s-geffroy.github.io/Index-Dissipation-Entropique/en/)

---

## Résumé

Ce dépôt construit un **instrument** — une mesure de la diversité qu'un fil d'actualité expose
réellement à son lecteur, calculable sans accès au code de la plateforme — et la **méthode
adverse** qui l'a mis à l'épreuve : chaque proposition y est attaquée, et ce qui tombe est
publié comme tel.

### Le verdict

| Objet | État |
|---|---|
| l'analogie décohérence quantique ↔ effondrement du consensus, dont le projet est parti | **réfutée**, transfert par transfert → [audit](docs/limites.md) |
| le formalisme classique qu'elle a fait emprunter | **cohérent**, un seul paramètre calibré, et sa seule prédiction propre testée quatre fois **sans effet** |
| l'index tel qu'il était proposé | **intenable** : saturable à coût nul, puis contournable par l'enterrement |
| la forme retenue de l'index | **définie et chiffrée**, jamais éprouvée sur un fil réel |
| l'algorithme (ADE) | **non évalué**, et non évaluable sur données publiques en l'état |
| l'écart de persistance entre registres émotionnels | **n'existe pas** |
| les instruments de mesure construits en chemin | **valides**, dont un confronté à une vérité terrain |

**La théorie n'a pas tenu, la métrologie oui.**

### Ce qui tient

- **Un contrôle qui dit si un journal de recommandation est corrigible.** Le test
  d'échangeabilité ne détecte rien dans MIND ($z = +0{,}12$, ordre mélangé) et rejette à
  $z = -206$ sur Baidu-ULTR, du côté que la théorie prescrit.
  → **[MIND](docs/mind.md)** · **[Journaux qui enregistrent le rang](docs/rang-servi.md)**
- **Une sévérité de biais de position estimée au lieu d'être posée.** $1{,}10 \pm 0{,}09$ sur une
  page de résultats, **dix fois moins** sur un bandeau de trois vignettes où l'allocation
  aléatoire rend la mesure causale : $\eta$ est une propriété de la surface.
  → **[Rang adverse](docs/rang-adverse.md)**
- **Des estimateurs contrefactuels vérifiés contre une vérité terrain.** +2,5 % d'écart sur la
  valeur d'une politique jamais déployée, contre +32 % pour l'estimation naïve — avec une taille
  d'échantillon **effective** de 1 513 sur 4 millions, qui interdit d'en tirer gloire.
- **Une demande d'accès aux données qui se vérifie au lieu de se plaider.** Quatre tableaux
  agrégés, sans donnée personnelle, prouvés suffisants — 95 fois moins de lignes que le journal.
  → **[Article 40](docs/article-40.md)**

### Ce qui est tombé

Six résultats négatifs, publiés avec ce qui les établit : le critère $\gamma\alpha > \lambda$
[ne veut rien dire](docs/calibration.md) ; l'écart de persistance entre registres
[n'existe pas](docs/corpus-etendu.md) et [n'était pas dilué](docs/annotation.md) par
l'étiquetage ; un plancher d'index [se sature à coût nul](docs/gaming.md) ; le premier correctif
[prescrivait la polarisation](docs/gaming.md) ; et le jeu de données de référence
[ne permet pas l'évaluation annoncée](docs/mind.md).

### Les deux instruments

| | Objet | État |
|---|---|---|
| **IDE** | *Indice de Diversité Exposée* — entropie des contenus servis sur un catalogue déclaré, **pondérée par l'attention de chaque rang**, dans $[0,1]$, mesurable sans accès au code | forme retenue **définie**, non éprouvée sur données réelles |
| **ADE** | *Algorithme de Diversité Exposée* — filtre de recommandation qui optimise cet indice plutôt que l'engagement brut | **non évalué** : le jeu de données qui le permettrait n'existe pas publiquement |

## À lire d'abord : ce que le travail ne prétend pas

L'**[audit critique](docs/limites.md)** recense **dix-sept corrections** apportées au
raisonnement d'origine — dont **cinq formules invalides**, et une découverte en tentant de
mesurer — et énumère les limites qui subsistent, y compris celles qui touchent à l'usage
réglementaire de l'index : il est manipulable, sa discrétisation en points de vue est un choix
politique, et un seuil imposé sur sa valeur est une intervention sur le débat public, non une
simple mesure technique.

Rien ici ne démontre que les opinions humaines *obéissent* à une mécanique statistique. Le
travail établit qu'un formalisme emprunté à la physique **reproduit** certains comportements
observés et en tire des quantités mesurables. **Un seul de ses paramètres est calibré sur
données réelles** — et cette calibration a montré qu'une de ses recommandations réglementaires
ne voulait rien dire.

L'ancrage empirique reste la faiblesse principale, mais son obstacle a changé de nature : ce
n'est plus une méthode qui manque, c'est une **donnée**. Mesurer l'indice sur un fil réel exige
un journal portant à la fois le rang servi et une étiquette de point de vue, et aucun jeu public
n'en porte les deux. La [feuille de route](docs/feuille-de-route.md) dit ce qui reste faisable
sans, et la [demande d'accès](docs/article-40.md) ce qu'il faudrait pour le reste.

## Démarrer

Tout s'exécute en conteneur. Rien n'est installé sur la machine hôte.

```bash
git clone git@github.com:s-geffroy/Index-Dissipation-Entropique.git
cd Index-Dissipation-Entropique

docker compose run --rm test          # 556 tests, dont les exemples de docstrings
docker compose run --rm lint          # ruff
docker compose run --rm notebooks     # régénère les 11 figures de la note
docker compose up lab                 # JupyterLab      → http://localhost:8888
docker compose up site                # documentation   → http://localhost:8000
docker compose run --rm latex         # compile paper/*.tex en PDF
```

Pour exclure les simulations Monte-Carlo longues :
`docker compose run --rm test pytest -m "not slow"`.

## Structure

```
src/ide/            noyau scientifique — modules purs, graines explicites
├── entropy.py      entropies de Shannon et von Neumann, calcul de l'IDE
├── ising.py        Metropolis 2D, cycle d'hystérésis, température critique
├── voter.py        Voter Model, dérive de désinformation, lois d'échelle
├── fokker_planck.py  énergie libre de champ moyen, solveur en volumes finis
├── resonance.py    oscillateur à amortissement négatif saturé
├── ade.py          score de recommandation entropique, recuit
├── calibration.py  identification de γα et λ sur des pics d'attention
├── regime.py       détection de changement de régime et identification associée
├── pageviews.py    accès à l'API Wikimedia, cache versionné et compressé
├── catalogue.py    corpus étendu dérivé de catégories Wikipédia
├── corpus.py       corpus pré-enregistré de calibration
├── annotation.py   grille d'annotation en aveugle, accords inter-codeurs
├── gaming.py       test adverse de l'index et mesures de diversité concurrentes
├── radio.py        divergences conscientes du rang (RADio) et métriques DART
├── offpolicy.py    estimateurs contrefactuels et sévérité du biais de position
├── ranking.py      test adverse sur fils ordonnés, énumération exhaustive
├── logs.py         journaux d'impressions : test d'échangeabilité, condensés versionnables
├── mind.py         lecture de MIND et son condensé
├── exposure.py     Baidu-ULTR et Open Bandit Dataset : le rang servi, et sa confrontation
├── aggregates.py   les quatre tableaux à demander au titre de l'article 40 du DSA
└── abm/            modèle à agents « compas politique »

tests/              556 tests — validation physique, numérique et statistique
notebooks/          01 à 18, un par bloc théorique, exécutables
data/pageviews/     464 séries de consultation, versionnées pour la reproductibilité
data/catalogue.json manifeste pré-enregistré du corpus étendu (440 sujets)
data/mind_digest.npz  condensé de MIND-small (1,5 Mo) — le jeu brut n'est pas versionné
data/exposure_digest.npz  condensé de Baidu-ULTR et de l'Open Bandit Dataset (0,7 Mo)
scripts/            collecte des données (seul point d'accès réseau du dépôt)
paper/              note de synthèse LaTeX (FR + EN) et figures générées
docs/               documentation du site, bilingue
legacy/             prototype pygame du fil d'origine, conservé tel quel
```

## Ce qui est vérifié, et comment

L'analogie physique-social n'est pas falsifiable en tant que telle. L'implémentation qui
la porte, elle, l'est — et c'est là que se joue la crédibilité du travail :

| Vérification | Pourquoi elle compte |
|---|---|
| température critique d'Onsager $T_c/J \approx 2{,}269$ retrouvée | seule prédiction théorique **exacte** du dépôt, indépendante de nos hypothèses sociologiques |
| masse de probabilité conservée à $10^{-15}$ | distingue un effondrement réel de la modération d'une fuite numérique |
| exposants du temps de consensus : $\approx 1$ en champ moyen, $\approx 2$ sur un anneau | contredit l'argument d'origine sur les réseaux « petit monde » |
| aire du cycle d'hystérésis strictement positive sous $T_c$, nulle au-dessus | validation numérique de la persistance des croyances |
| à $\mu = 0$, l'ADE est identique à un filtre d'engagement | garantit que la proposition est un ajout paramétré, pas une refonte |
| taux d'une exponentielle de synthèse retrouvés à $10^{-9}$ | condition minimale pour que la calibration empirique signifie quelque chose |
| un changement de régime synthétique n'est **pas** détecté par la méthode par pic | fige dans un test la limite qui a motivé la seconde méthode |
| deux jeux de paramètres de rapports 5,0 et 1,7 donnent la **même** trajectoire | démontre une non-identifiabilité structurelle, et non un défaut numérique |
| les deux registres du corpus étendu ont des effectifs **exactement** égaux | l'équilibre vient d'une troncature, il doit donc être exact |
| un temps d'oubli plus long que la fenêtre d'ajustement est **refusé** | sans quoi un ajustement excellent produit un rapport de 5431 |
| reproductibilité à la graine du modèle à agents | condition minimale pour qu'un chiffre du dépôt soit citable |
| le condensé de MIND rend **exactement** les chiffres du journal brut | sans quoi le dépôt publierait des mesures que personne ne pourrait refaire |
| un ordre mélangé passe le contrôle d'identifiabilité et donne cinq sévérités | fige l'erreur que ce contrôle laissait passer |
| le test d'échangeabilité **rejette** sur Baidu-ULTR, et du côté négatif | un test qui ne rejette jamais rien ne dirait rien de MIND |
| l'IPS retrouve à 2,5 % la valeur d'une politique jamais déployée | seule confrontation du dépôt à une vérité terrain mesurée |
| les mesures se recalculent **à l'identique** depuis les tableaux agrégés | c'est ce qui rend une demande d'accès proportionnée plutôt que plaidée |

## Contenu du dépôt

- [`docs/limites.md`](docs/limites.md) — **audit critique** : les dix-sept corrections et les
  limites qui subsistent.
- [`docs/calibration.md`](docs/calibration.md) — **la mesure de $\gamma\alpha/\lambda$** sur
  données publiques, ses trois enseignements et ses réserves.
- [`docs/regimes.md`](docs/regimes.md) — **les désinformations qui s'installent** : 14
  basculements datés, et pourquoi le rapport n'y est pas identifiable.
- [`docs/corpus-etendu.md`](docs/corpus-etendu.md) — **la réplication sur 440 sujets** :
  comment un corpus dérivé de catégories a infirmé le résultat du corpus pilote.
- [`docs/annotation.md`](docs/annotation.md) — **l'annotation en aveugle** : la grille
  pré-enregistrée, les 40 % de bruit d'étiquetage mesurés, la disparition du dernier écart, et
  le double recodage ($\kappa$ de Fleiss = 0,921).
- [`docs/gaming.md`](docs/gaming.md) — **le test adverse de l'index** : un plancher d'IDE se
  sature à coût nul, et le premier correctif proposé prescrivait la polarisation.
- [`docs/evaluation.md`](docs/evaluation.md) — **rang et contrefactuel** : l'enterrement de la
  diversité, et pourquoi une évaluation hors ligne naïve se trompe de 201 %.
- [`docs/rang-adverse.md`](docs/rang-adverse.md) — **rang adverse et sévérité** : les quatre
  mesures contournées par l'ordre, et l'estimation du biais de position.
- [`docs/mind.md`](docs/mind.md) — **l'exploration réelle de MIND** : un ordre indiscernable
  d'un mélange, et cinq sévérités incompatibles tirées du même jeu.
- [`docs/rang-servi.md`](docs/rang-servi.md) — **deux journaux qui enregistrent le rang** :
  la sévérité mesurée, et l'estimateur contrefactuel jugé contre une vérité terrain.
- [`docs/article-40.md`](docs/article-40.md) — **la demande d'accès aux données**, rédigée comme
  une spécification : quatre tableaux agrégés, et la preuve qu'ils suffisent.
- [`docs/feuille-de-route.md`](docs/feuille-de-route.md) — comment combler ces limites,
  classé par rapport valeur/effort.
- [`docs/memorandum.md`](docs/memorandum.md) — recommandations techniques et éthiques pour
  les régulateurs, dans l'esprit du *Digital Services Act*.
- [`docs/errata.md`](docs/errata.md) — table de correspondance avec le fil de travail
  d'origine.
- [`paper/note_de_synthese.tex`](paper/) — note académique, versions française et anglaise.

## Relecture

Ce travail est **ouvert à la relecture critique**, et il en a besoin : il croise deux
disciplines dont son auteur n'est spécialiste ni de l'une ni de l'autre.

Les retours les plus utiles portent sur la **calibration empirique** des paramètres, sur
la **viabilité de l'IDE** comme instrument réglementaire, et sur les analogies restantes
qui ne tiendraient pas. → [Appel à relecture](docs/relecture.md) ·
[CONTRIBUTING](CONTRIBUTING.md)

## Fondements théoriques

Zeh (1970) et Zurek (2003) pour la décohérence · von Neumann (1932) et Shannon (1948)
pour les entropies · Ising (1925), transposé par Galam à partir des années 1980, pour la
dynamique d'opinion · Clifford & Sudbury (1973) et Holley & Liggett (1975) pour le Voter
Model · Risken (1989) pour Fokker-Planck · Watts & Strogatz (1998) pour les réseaux
« petit monde » · Pariser (2011) pour les bulles de filtres · Reynolds (1987) pour les
*Boids*, dont le modèle à agents transpose les trois règles.

## Licences

Code (`src/`, `tests/`, `notebooks/`, `legacy/`) sous [MIT](LICENSE) · contenus
rédactionnels (`docs/`, `paper/`) sous [CC BY 4.0](LICENSE-DOCS).
