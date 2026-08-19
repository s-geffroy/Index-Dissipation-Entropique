# Appel à relecture

Ce travail est un **document de travail ouvert**. Il croise deux disciplines, et son
auteur n'est spécialiste ni de l'une ni de l'autre : la relecture critique n'est pas une
formalité, c'est ce qui décidera s'il vaut quelque chose.

## Les retours les plus utiles

L'état du travail a changé : l'analogie de départ est [réfutée](limites.md), l'écart empirique
qui devait l'ancrer [n'existe pas](corpus-etendu.md), et ce qui tient est l'**instrumentation**.
Les retours utiles ont donc changé aussi, par ordre décroissant :

1. **La forme retenue de l'index, et son niveau.** L'IDE mesure désormais l'entropie des
   contenus servis, pondérée par l'attention de chaque rang, sur un catalogue déclaré. Est-elle
   la bonne ? Un plancher exprimé sur cette grandeur est-il applicable, et à quel niveau ? Le
   dépôt établit la forme et le prix, **pas la valeur**. → [IDE](ide.md)
2. **Les instruments de mesure.** Le test d'échangeabilité, l'estimation de la sévérité du biais
   de position, les estimateurs contrefactuels et la [spécification agrégée](article-40.md) sont
   ce qui survit à tout le reste. Une erreur méthodologique là serait la plus coûteuse.
   → [MIND](mind.md) · [journaux qui enregistrent le rang](rang-servi.md)
3. **La discrétisation en points de vue.** Peut-elle être définie sans arbitraire politique ?
   C'est la question que la mesure rend explicite au lieu de l'enfouir, et elle n'est pas
   technique.
4. **Un accès aux données.** La demande au titre de l'article 40 est écrite et vérifiée, mais
   elle exige un **organisme de recherche** déposant. C'est le seul verrou que ce dépôt ne peut
   pas lever seul. → [demande au titre de l'article 40](article-40.md)
5. **Le formalisme résiduel.** L'énergie libre de champ moyen est-elle le bon objet ? Le
   couplage entre équation de résonance et dynamique d'opinion est-il légitime ? Cette question
   compte moins qu'avant : le formalisme est cohérent, mais ce n'est plus lui qui porte les
   résultats.
6. **Des annotateurs humains.** Les trois codeurs du corpus sont des instances du même modèle de
   langue ; leur accord surestime ce que produiraient des juges indépendants.
   → [annotation en aveugle](annotation.md)

## Ce qui a déjà été corrigé

Merci de consulter l'[audit critique](limites.md) et les [errata](errata.md) avant de signaler
une erreur : **dix-sept corrections** y sont documentées, dont les cinq formules invalides du
raisonnement d'origine, deux découvertes en tentant de mesurer, et le renommage de l'index
lui-même. Six résultats négatifs y sont publiés comme tels.

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
| **Régulation du numérique** | faisabilité juridique et technique du cadre métrologique proposé, et [demande d'accès aux données](article-40.md) au titre de l'article 40 du DSA |
| **Recommandation et évaluation hors ligne** | validité du test d'échangeabilité, de l'estimation du biais de position et des estimateurs contrefactuels |

---

## Modèle de courriel de sollicitation

Le texte ci-dessous est un modèle réutilisable. Les crochets sont à compléter ; aucune
coordonnée personnelle n'est incluse dans ce dépôt.

> **Objet** — Proposition de relecture : mesurer la diversité qu'un fil algorithmique expose
> réellement (métrologie de l'audit algorithmique)
>
> Madame, Monsieur,
>
> Je me permets de solliciter votre expertise pour la relecture d'un travail ouvert portant sur
> la **mesure de la diversité réellement exposée** par un fil de recommandation, et sur les
> conditions auxquelles cette mesure est possible sur données réelles.
>
> **Résumé.** Le travail définit un *Indice de Diversité Exposée* (IDE) — l'entropie des
> contenus servis sur un catalogue de points de vue déclaré, pondérée par l'attention de chaque
> rang — et un filtre de recommandation qui l'optimise. Il est parti d'une analogie avec la
> décohérence quantique, que son propre audit a **réfutée** ; ce qui subsiste relève de la
> mécanique statistique classique, et l'essentiel des résultats est **métrologique** : un test
> exact qui dit si un journal de recommandation permet seulement une correction d'exposition,
> l'estimation de la sévérité du biais de position au lieu de sa supposition, et des estimateurs
> contrefactuels confrontés à une vérité terrain.
>
> **Ce que je sollicite en particulier.** Le dépôt publie **six résultats négatifs** et
> **dix-sept corrections** de son propre raisonnement, dont plusieurs invalidaient une formule.
> Les avis les plus utiles porteraient sur la forme retenue de l'indice et sur le niveau d'un
> éventuel plancher — que la mesure ne détermine pas —, ou sur les instruments de mesure
> eux-mêmes, où une erreur méthodologique serait la plus coûteuse. Une validation d'ensemble me
> serait bien moins utile.
>
> L'intégralité du travail est en libre accès : équations, code reproductible en conteneur,
> suite de tests, figures régénérables, et jeux de données dérivés.
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
