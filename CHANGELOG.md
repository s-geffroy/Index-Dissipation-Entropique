# Changelog

Toutes les évolutions notables de ce projet sont consignées dans ce fichier.

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) et le
versionnement respecte [Semantic Versioning](https://semver.org/lang/fr/).

## [Non publié]

### À faire

Les pistes sont détaillées et priorisées dans
[`docs/feuille-de-route.md`](docs/feuille-de-route.md). Les trois premières :

- calibration de $\gamma\alpha/\lambda$ sur des séries temporelles de visibilité
  publiques — c'est le chiffre qui manque le plus au mémorandum ;
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
