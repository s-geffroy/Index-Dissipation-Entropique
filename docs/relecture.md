# Appel à relecture

Ce travail est un **document de travail ouvert**. Il croise deux disciplines, et son
auteur n'est spécialiste ni de l'une ni de l'autre : la relecture critique n'est pas une
formalité, c'est ce qui décidera s'il vaut quelque chose.

## Les retours les plus utiles

Par ordre décroissant d'utilité :

1. **La calibration empirique.** C'est la faiblesse principale. Les paramètres $J$,
   $T$, $\gamma$, $\alpha$ n'ont aucune procédure d'estimation sur données réelles.
   Toute piste — jeu de données, protocole d'inférence, travail existant — vaut plus que
   n'importe quelle amélioration du formalisme.
2. **La viabilité de l'IDE comme instrument.** L'index est-il manipulable au point
   d'être inutile ? La discrétisation en points de vue peut-elle être définie sans
   arbitraire politique ? Un protocole d'audit préservant la vie privée est-il
   concevable ?
3. **Le formalisme.** L'énergie libre de champ moyen est-elle le bon objet ? Le
   couplage entre l'équation de résonance et la dynamique d'opinion est-il légitime, ou
   les deux échelles de temps sont-elles incompatibles ?
4. **Les analogies restantes.** L'[audit](limites.md) en a requalifié plusieurs. Il en
   reste probablement d'autres qui ne tiennent pas.

## Ce qui a déjà été corrigé

Merci de consulter l'[audit critique](limites.md) et les [errata](errata.md) avant de
signaler une erreur : quatorze corrections y sont déjà documentées, dont les cinq
formules invalides du raisonnement d'origine. Cela évitera de refaire un travail déjà
fait.

## Comment contribuer

* **Ouvrir une [issue](https://github.com/s-geffroy/Index-Dissipation-Entropique/issues)** —
  y compris pour une objection de fond, qui n'a pas besoin d'être accompagnée d'un
  correctif.
* **Proposer une *pull request*** — les corrections de formalisme sont bienvenues ;
  merci d'y joindre le test qui échouait avant et passe après.
* **Écrire directement**, si l'objection est trop large pour une issue.

Tout retour intégré est crédité dans le [CHANGELOG](https://github.com/s-geffroy/Index-Dissipation-Entropique/blob/main/CHANGELOG.md).

## Communautés visées

Le travail se situe à l'intersection de trois champs :

| Champ | Ce qui s'y joue |
|---|---|
| **Sociophysique / physique statistique** | validité des modèles d'Ising, de Fokker-Planck et du traitement de champ moyen |
| **Sciences des réseaux / sociologie computationnelle** | pertinence de l'application aux algorithmes de recommandation réels |
| **Régulation du numérique** | faisabilité juridique et technique du cadre métrologique proposé |

---

## Modèle de courriel de sollicitation

Le texte ci-dessous est un modèle réutilisable. Les crochets sont à compléter ; aucune
coordonnée personnelle n'est incluse dans ce dépôt.

> **Objet** — Proposition de relecture : modélisation thermodynamique de la
> polarisation algorithmique (Ising / Fokker-Planck)
>
> Madame, Monsieur,
>
> Je me permets de solliciter votre expertise pour la relecture d'une note de synthèse
> originale intitulée « De la décohérence quantique à la polarisation sociale :
> modélisation thermodynamique de l'opinion publique ».
>
> **Résumé.** Le travail formalise une analogie structurelle entre décohérence
> quantique et effondrement du consensus dans une population soumise à des flux
> informationnels algorithmiques. Il en dérive deux instruments : un *Index de
> Diversité Exposée* (IDE), métrique auditable de la diversité informationnelle
> d'un fil d'actualité, et un *Algorithme de Diversité Exposée* (ADE), filtre de
> recommandation qui optimise cet index plutôt que l'engagement brut. L'objectif est de
> proposer un cadre métrologique concret pour l'audit algorithmique, dans l'esprit du
> *Digital Services Act*.
>
> **Ce que je sollicite en particulier.** Le dépôt contient une section d'audit
> critique qui recense quatorze corrections apportées au raisonnement initial et les
> limites qui subsistent — notamment l'absence de calibration empirique des paramètres,
> qui est la faiblesse principale du travail. Un avis sur ce point, ou sur la viabilité
> de l'index comme instrument réglementaire, me serait bien plus précieux qu'une
> validation d'ensemble.
>
> L'intégralité du travail est en libre accès : équations, code de simulation
> reproductible en conteneur, suite de tests et figures régénérables.
>
> [lien vers le dépôt]
>
> Seriez-vous ouvert à y jeter un œil critique, ou auriez-vous un chercheur de votre
> équipe à me recommander pour cette relecture ?
>
> En vous remerciant par avance du temps accordé,
>
> [Prénom Nom] · [affiliation ou statut] · [contact]

### Conseil d'usage

Ce que le fil de travail d'origine notait à juste titre : il faut que le lecteur qui
clique sur le lien puisse comprendre l'essentiel **en moins de deux minutes**. La page
d'accueil du dépôt est écrite pour cela — un chercheur sollicité ne lira pas trois pages
d'équations avant de décider s'il répond.

Un conseil supplémentaire, issu de l'audit : mentionner explicitement les limites du
travail dans le courriel de sollicitation. Un relecteur qui découvre lui-même une
faiblesse non signalée devient méfiant sur tout le reste ; un relecteur à qui l'on
annonce la faiblesse la traite comme une question de recherche.
