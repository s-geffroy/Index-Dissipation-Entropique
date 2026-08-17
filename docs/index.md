# Index de Dissipation Entropique

**De la décohérence quantique à la polarisation algorithmique : modélisation
thermodynamique de l'opinion publique.**

---

## L'intuition de départ

Plus un système quantique est grand, plus sa décohérence est rapide : au contact d'un
environnement massif, la superposition d'états s'effondre presque instantanément vers
un état classique unique.

Plus une population est grande, plus il est difficile d'y trouver un accord.

Cette analogie tient-elle mathématiquement ? Ce dépôt la prend au sérieux, la
formalise, en teste les conséquences numériquement — et corrige au passage ce qu'elle
contient de faux.

![Les trois régimes de l'opinion publique : paysage d'énergie libre, distributions
stationnaires, et scission d'une société initialement modérée](figures/fig04_paysage.png)

/// caption
Les trois régimes de l'opinion publique, obtenus en changeant deux paramètres du même
paysage d'énergie libre. Figure régénérée par
[le notebook 04](notebooks/04_fokker_planck_paysage.ipynb).
///

## Ce que le travail établit

Trois résultats, chacun vérifié par du code exécutable :

**Une transition de phase, pas une dégradation continue.** Avec l'énergie libre
$F = E - TS$ correctement écrite, la distribution des opinions passe brusquement d'un
pic unique centré sur la modération à deux pics extrêmes, de part et d'autre d'une
**température sociale critique**. Une société ne se polarise pas graduellement : elle
bascule. → [Fokker-Planck](theorie/fokker-planck.md)

**Un démenti ne suffit pas.** Sous la température critique, couper le champ
médiatique ne ramène pas l'opinion à la neutralité : le conformisme de groupe prend
le relais et maintient la croyance. C'est une **hystérésis**, mesurable, et elle
explique pourquoi le *debunking* passif échoue. → [Température sociale](theorie/temperature.md)

**L'amplification a un seuil net — et l'écosystème est au-dessus.** Quand le gain
algorithmique dépasse le taux d'oubli naturel d'un contenu ($\gamma\alpha > \lambda$),
l'amortissement effectif devient négatif : le système accumule l'énergie qu'on lui injecte au
lieu de la dissiper. La [mesure sur données publiques](calibration.md) situe le rapport entre
**1,5 et 12** sur 19 épisodes d'attention — et montre du même coup que vérifier le *signe* de
ce critère n'apprend rien, ce qui a obligé à réécrire une recommandation du mémorandum.
→ [Résonance](theorie/resonance.md) · [Calibration](calibration.md)

**Les basculements durables se datent, mais ne distinguent pas les registres.** La détection
de [changement de régime](regimes.md) retrouve des basculements datés — QAnon en mars 2020,
l'affaire Benalla le 20 juillet 2018. Un écart de persistance entre contenus d'accusation et
annonces de découverte y semblait acquis, ×9,2 contre ×2,9 ; la vérification sur
[440 sujets](corpus-etendu.md) l'a ramené à ×3,04 contre ×2,90 ($p = 0{,}53$). C'était un
artefact de sélection manuelle. → [Corpus étendu](corpus-etendu.md)

## Ce que le travail propose

| | Objet | Destinataire |
|---|---|---|
| **[IDE](ide.md)** | *Index de Dissipation Entropique* — une métrique de la diversité informationnelle d'un fil, dans $[0, 1]$, mesurable sans accès au code de la plateforme | le régulateur |
| **[ADE](ade.md)** | *Algorithme de Dissipation Entropique* — un filtre de recommandation qui optimise cet index au lieu de l'engagement brut | la plateforme |

Un seul paramètre du modèle est aujourd'hui **calibré sur données réelles** :
→ [Calibration empirique](calibration.md).

Le [mémorandum de régulation](memorandum.md) traduit ces deux objets en
recommandations pour l'ARCOM et la Commission européenne, dans le cadre du *Digital
Services Act*.

## Ce que le travail ne prétend pas

L'[**audit critique**](limites.md) est la page qu'il faut lire avant les autres. Il
recense **quinze corrections** apportées au raisonnement d'origine — dont cinq qui
invalidaient une formule, et une découverte en tentant de mesurer — et énumère les limites
qui subsistent, y compris celles qui touchent à l'usage réglementaire de l'index : l'IDE est
manipulable, sa discrétisation en points de vue est un choix politique, et un seuil imposé sur
sa valeur est une intervention sur le débat public, non une simple mesure technique.

Rien ici ne démontre que les opinions humaines *obéissent* à une mécanique statistique. Le
travail établit qu'un formalisme emprunté à la physique **reproduit** certains comportements
observés, et en tire des quantités mesurables. Un seul de ses paramètres est aujourd'hui
calibré sur données réelles — et cette calibration a montré qu'une de ses recommandations
réglementaires ne voulait rien dire. L'ancrage empirique n'est qu'entamé : c'est la principale
faiblesse du travail, et la [feuille de route](feuille-de-route.md) dit comment y remédier.

## Explorer

Les onze notebooks sont exécutables et produisent l'intégralité des figures de la
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

## Reproduire

Tout s'exécute en conteneur. Aucune dépendance n'est installée sur la machine hôte.

```bash
git clone git@github.com:s-geffroy/Index-Dissipation-Entropique.git
cd Index-Dissipation-Entropique

docker compose run --rm test          # 266 tests
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
[Dépôt GitHub](https://github.com/s-geffroy/Index-Dissipation-Entropique)*
