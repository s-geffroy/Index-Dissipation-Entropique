# Index de Dissipation Entropique (IDE)

**De la décohérence quantique à la polarisation algorithmique : modélisation
thermodynamique de l'opinion publique.**

[![Licence : MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Documentation : CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey.svg)](LICENSE-DOCS)
[![Champ : sociophysique](https://img.shields.io/badge/champ-sociophysique-8a2be2.svg)](https://s-geffroy.github.io/Index-Dissipation-Entropique/)
[![Tests : 488](https://img.shields.io/badge/tests-488-brightgreen.svg)](tests/)

📖 **[Documentation complète](https://s-geffroy.github.io/Index-Dissipation-Entropique/)**
· [English](https://s-geffroy.github.io/Index-Dissipation-Entropique/en/)

---

## Résumé

Plus un système quantique est grand, plus sa décohérence est rapide. Plus une population
est grande, plus il est difficile d'y trouver un accord. Ce dépôt prend cette analogie au
sérieux : il la formalise, en teste les conséquences numériquement, et **corrige ce
qu'elle contient de faux**.

Trois résultats, chacun adossé à du code exécutable :

- **Une transition de phase, pas une dégradation continue.** Avec l'énergie libre
  $F = E - TS$ correctement écrite, la distribution des opinions passe brusquement d'un
  pic centré sur la modération à deux pics extrêmes, de part et d'autre d'une température
  sociale critique. Une société ne se polarise pas graduellement : elle bascule.
- **Un démenti ne suffit pas.** Sous cette température, couper le champ médiatique ne
  ramène pas l'opinion à la neutralité — le conformisme de groupe prend le relais. C'est
  une hystérésis, elle est mesurable, et elle explique l'échec du *debunking* passif.
- **L'amplification a un seuil net, et l'écosystème est au-dessus.** Quand le gain
  algorithmique dépasse le taux d'oubli naturel d'un contenu ($\gamma\alpha > \lambda$),
  l'amortissement effectif devient négatif : le système accumule l'énergie au lieu de la
  dissiper. La **[mesure sur données publiques](docs/calibration.md)** situe le rapport entre
  **1,5 et 12** sur 19 épisodes d'attention — et montre du même coup que vérifier le *signe*
  de ce critère n'apprend rien, ce qui a obligé à réécrire une recommandation du mémorandum.
- **Les basculements durables se datent, mais ne distinguent pas les registres.** La
  **[détection de changement de régime](docs/regimes.md)** retrouve des basculements datés —
  QAnon en mars 2020, l'affaire Benalla le 20 juillet 2018. Un écart de persistance entre
  registres émotionnels y semblait acquis (×9,2 contre ×2,9) ; la vérification sur
  **[440 sujets](docs/corpus-etendu.md)** l'a ramené à ×3,04 contre ×2,90 ($p = 0{,}53$).
  C'était un artefact de sélection manuelle, et l'**[annotation en aveugle](docs/annotation.md)**
  du registre a éliminé la dernière hypothèse de sauvetage : l'écart de taux de basculement
  passe de 8,6 % contre 2,7 % à **4,8 % contre 5,1 %** ($p = 1{,}00$) une fois l'étiquette
  corrigée. **Aucune différence entre registres ne résiste à sa vérification.**

- **Et l'index proposé n'est pas une norme tenable en l'état.** Le
  **[test adverse](docs/gaming.md)** montre qu'une plateforme capable de dissocier l'étiquette
  du contenu obtient un IDE de **1,000 pour une diversité de contenu nulle**, à coût nul. Le
  premier remplaçant proposé — l'entropie de Rao — s'est révélé pire : son optimum sous
  contrainte est **bimodal**, donc il prescrirait la polarisation. Le plancher retenu porte sur
  une entropie calculée sur les **contenus** servis, et il doit être **conscient du rang** :
  sinon la plateforme s'y conforme en enterrant les contenus divergents.
- **Et l'évaluation hors ligne de l'algorithme demandait d'abord d'être corrigée.** Sur des
  clics enregistrés, l'estimation naïve du coût d'un filtre de diversité se trompe de **201 %
  en médiane** — et rien ne garantit le sens de l'erreur.
  → **[Rang et contrefactuel](docs/evaluation.md)**

Le travail en dérive deux instruments :

| | Objet | Destinataire |
|---|---|---|
| **IDE** | *Index de Dissipation Entropique* — métrique de la diversité informationnelle d'un fil, dans $[0,1]$, mesurable **sans accès au code** de la plateforme | le régulateur |
| **ADE** | *Algorithme de Dissipation Entropique* — filtre de recommandation qui optimise cet index plutôt que l'engagement brut | la plateforme |

## À lire d'abord : ce que le travail ne prétend pas

L'**[audit critique](docs/limites.md)** recense **quinze corrections** apportées au
raisonnement d'origine — dont **cinq formules invalides**, et une découverte en tentant de
mesurer — et énumère les limites qui subsistent, y compris celles qui touchent à l'usage
réglementaire de l'index : il est manipulable, sa discrétisation en points de vue est un choix
politique, et un seuil imposé sur sa valeur est une intervention sur le débat public, non une
simple mesure technique.

Rien ici ne démontre que les opinions humaines *obéissent* à une mécanique statistique. Le
travail établit qu'un formalisme emprunté à la physique **reproduit** certains comportements
observés et en tire des quantités mesurables. **Un seul de ses paramètres est calibré sur
données réelles** — et cette calibration a montré qu'une de ses recommandations réglementaires
ne voulait rien dire. L'ancrage empirique n'est qu'entamé : c'est la faiblesse principale, et
la [feuille de route](docs/feuille-de-route.md) dit comment y remédier.

## Démarrer

Tout s'exécute en conteneur. Rien n'est installé sur la machine hôte.

```bash
git clone git@github.com:s-geffroy/Index-Dissipation-Entropique.git
cd Index-Dissipation-Entropique

docker compose run --rm test          # 488 tests, dont les exemples de docstrings
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
└── abm/            modèle à agents « compas politique »

tests/              488 tests — validation physique, numérique et statistique
notebooks/          01 à 11, un par bloc théorique, exécutables
data/pageviews/     464 séries de consultation, versionnées pour la reproductibilité
data/catalogue.json manifeste pré-enregistré du corpus étendu (440 sujets)
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

## Contenu du dépôt

- [`docs/limites.md`](docs/limites.md) — **audit critique** : les quinze corrections et les
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
