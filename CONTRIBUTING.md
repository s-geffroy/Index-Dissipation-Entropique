# Contribuer

Ce dépôt est un **document de travail ouvert à la relecture critique**. Les objections de
fond y sont plus utiles que les correctifs de forme.

## Avant d'ouvrir une issue

Merci de consulter [`docs/limites.md`](docs/limites.md) et [`docs/errata.md`](docs/errata.md) :
quatorze corrections y sont déjà documentées, dont les cinq formules invalides du
raisonnement d'origine. Cela évite de refaire un travail déjà fait.

## Les contributions les plus utiles

Par ordre décroissant, et détaillées dans la
[feuille de route](docs/feuille-de-route.md) :

1. **Calibration empirique** des paramètres $J$, $T$, $\gamma$, $\alpha$ sur des données
   réelles. C'est ce qui manque le plus au travail : toute piste — jeu de données,
   protocole d'inférence, littérature existante — vaut plus que n'importe quelle
   amélioration du formalisme.
2. **Critique de l'IDE comme instrument** : manipulabilité, arbitraire de la
   discrétisation, protocole d'audit préservant la vie privée.
3. **Corrections de formalisme**, avec le test qui échouait avant et passe après.
4. **Analogies qui ne tiennent pas** et qui auraient échappé à l'audit.

## Environnement de développement

Aucune dépendance ne s'installe sur la machine hôte : tout passe par des conteneurs.

```bash
docker compose run --rm test          # suite complète, dont les docstrings
docker compose run --rm lint          # ruff
docker compose run --rm notebooks     # ré-exécute les notebooks et les figures
docker compose up site                # documentation en local
```

## Conventions

**Le noyau scientifique reste pur.** Les modules de `src/ide/` n'effectuent aucune
entrée-sortie et prennent une **graine explicite** dès qu'ils sont stochastiques. Un
résultat non reproductible n'est pas citable.

**Une correction s'accompagne de sa vérification.** Toute modification du formalisme doit
venir avec le test qui la contraint. Les tests portent leur justification dans leur
docstring : ils documentent *pourquoi* la valeur attendue est celle-là, pas seulement
qu'elle l'est.

**Les tolérances sont argumentées.** Plusieurs tests emploient des marges larges — par
exemple ±0,25 sur la localisation de la température critique. Ces marges sont motivées
en commentaire (ici, les effets de taille finie). Une tolérance resserrée sans justification
physique testerait le générateur aléatoire plutôt que le modèle.

**Les figures ne sont jamais dessinées à la main.** Chacune est produite par un notebook
et enregistrée dans `paper/figures/` via `ide.plotting.save_figure`. Une figure non
régénérable n'est pas auditable.

**Les nombres cités dans la documentation sont mesurés.** Toute valeur qui apparaît dans
`docs/` doit provenir d'une exécution, pas d'une estimation.

**Le CHANGELOG est mis à jour** à chaque évolution de la documentation ou du modèle, au
format [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).

## Traçabilité des corrections

Chaque écart avec le fil de travail d'origine est numéroté dans
[`docs/limites.md`](docs/limites.md), et les renvois « point N » depuis le code, les tests
et les notebooks se rapportent à cette numérotation. Ajouter une correction implique donc
d'ajouter son point à l'audit — sinon la correction devient invisible pour un relecteur.

## Crédit

Tout retour intégré est crédité dans le [CHANGELOG](CHANGELOG.md).
