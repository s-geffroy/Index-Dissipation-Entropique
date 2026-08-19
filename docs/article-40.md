# Demande d'accès aux données au titre de l'article 40 du DSA

!!! info "Ce que ce document est, et n'est pas"
    C'est un **modèle prêt à déposer**, pas une demande déposée. L'article 40(8)(a) du DSA
    réserve la qualité de *chercheur agréé* aux personnes **affiliées à un organisme de
    recherche** au sens de l'article 2, point 1, de la directive (UE) 2019/790. Ce dépôt, tenu
    par une personne seule, n'y est **pas éligible en l'état** : la demande ci-dessous est écrite
    pour être déposée par un organisme qui en remplit les conditions, et les passages à compléter
    sont entre crochets.

!!! success "Ce que la demande a de particulier"
    Elle ne réclame **aucun journal** et **aucune donnée personnelle**. Elle demande **quatre
    tableaux agrégés**, dont le [notebook 18](notebooks/18_demande_article_40.ipynb) vérifie
    qu'ils suffisent à recalculer **à l'identique** les quatre mesures qui décident de tout — et
    qui pèsent, sur un journal réel, **95 fois moins de lignes** que le journal lui-même.

---

## Le raisonnement qui mène à cette demande

Trois jeux publics ont été mesurés, et aucun ne permet l'évaluation annoncée :

* [MIND](mind.md) porte des catégories éditoriales mais **pas le rang** — son ordre enregistré
  est indiscernable d'un mélange ($z = +0{,}12$) ;
* [Baidu-ULTR](rang-servi.md) porte le rang ($z = -206$) mais **aucune étiquette** exploitable ;
* l'[Open Bandit Dataset](rang-servi.md) porte le rang, la propension vraie et un seau
  aléatoire, mais ses attributs de contenu sont **anonymisés**.

Il reste l'article 40. Et une demande n'est recevable que si elle est **nécessaire et
proportionnée** — article 40(8)(e) du DSA, article 8(d) du règlement délégué (UE) 2025/2050,
entré en vigueur le 29 octobre 2025. « Donnez-nous vos journaux » n'est ni l'un ni l'autre :
cela réclame des données personnelles dont l'analyse n'a aucun besoin, et cela offre à la
plateforme le motif de refus le plus facile — la sécurité du service et le secret des affaires,
article 40(5).

D'où la forme retenue : **une spécification, pas un accès**.

---

## I. Identification et base juridique

| | |
|---|---|
| **Demandeur** | [ORGANISME DE RECHERCHE], au sens de l'art. 2, point 1, de la directive (UE) 2019/790 |
| **Chercheur principal** | [NOM], [FONCTION] |
| **Fournisseur de données** | [PLATEFORME], désignée VLOP le [DATE] |
| **Coordinateur pour les services numériques d'établissement** | [AUTORITÉ] — pour la plupart des VLOPs, l'autorité irlandaise |
| **Voie** | article 40(4) du règlement (UE) 2022/2065, procédure du règlement délégué (UE) 2025/2050 |
| **Dépôt** | portail d'accès aux données du DSA (art. 3 et 5 du règlement délégué) |

**Sur la voie choisie.** L'article 40(12) — accès aux **données publiquement accessibles**,
ouvert aux chercheurs affiliés à des organismes sans but lucratif — ne convient pas : les
données demandées ici ne sont pas publiquement accessibles, puisque c'est précisément l'ordre
servi et l'exposition qui manquent aux jeux publics. La voie 40(4) est donc la seule.

## II. Objet de la recherche (art. 8(f) du règlement délégué)

L'objet est la détection et la mesure d'un risque systémique visé à l'**article 34(1)(c)** du
DSA — les effets négatifs sur le discours civique — sous une forme mesurable :

> Une plateforme tenue à un plancher de diversité informationnelle portant sur la
> **composition** de ses fils peut s'y conformer en **enterrant** les contenus divergents aux
> rangs que personne ne consulte. La composition reste conforme et l'exposition réelle ne l'est
> pas.

Ce dépôt a établi ce point par énumération exhaustive : une plateforme certifiée à 0,70 par une
mesure aveugle au rang n'expose que **0,36** de diversité réelle, et fermer l'échappatoire
double le coût d'engagement ([rang adverse](rang-adverse.md)). Il a aussi établi que la
correction exige de connaître l'exposition, donc le **rang servi**, et que l'ignorer rend
l'évaluation vide par construction ([MIND](mind.md)).

La recherche demandée consiste à mesurer, sur les fils réellement servis par [PLATEFORME] :

1. l'écart entre **diversité composée** et **diversité exposée**, par période ;
2. la **sévérité du biais de position** propre à cette surface, plutôt que transportée d'une
   autre — l'étude a mesuré 1,10 sur une page de résultats et 0,04 à 0,11 sur un bandeau de
   trois vignettes, soit un ordre de grandeur d'écart ;
3. le **coût d'engagement** d'un réordonnancement respectant un plancher conscient du rang,
   estimé par pondération d'importance et non par *replay*, dont l'erreur médiane mesurée
   atteint 201 %.

## III. Données demandées (art. 8(c) du règlement délégué)

Quatre tableaux agrégés, au format CSV ou Parquet, pour la période [PÉRIODE] et le marché
[ÉTAT MEMBRE].

**Tableau 1 — profils de fils**

| Colonne | Type | Description |
|---|---|---|
| `profil` | entier | identifiant du profil de rangs (voir tableau 1 bis) |
| `clics_du_fil` | entier | nombre de contenus cliqués dans le fil |
| `fils` | entier | nombre de fils correspondants |

**Tableau 1 bis — définition des profils** : `profil`, `rang` — la liste des rangs qu'occupe
chaque profil. Indexer par la seule **longueur** du fil serait plus court et **faux** dès qu'une
surface saute des rangs, ce qu'une page de résultats fait.

**Tableau 2 — clics par rang**

| Colonne | Type | Description |
|---|---|---|
| `profil` | entier | profil du fil |
| `clics_du_fil` | entier | nombre de contenus cliqués dans le fil |
| `rang` | entier | rang servi |
| `clics` | entier | clics observés à ce rang |

Le second index n'est pas un ornement : sans lui, les fils dont *tout* a été cliqué — qui ne
contraignent rien — ne peuvent pas être écartés du calcul.

**Tableau 3 — cellules (contenu, rang)**

| Colonne | Type | Description |
|---|---|---|
| `contenu` | identifiant pseudonyme, stable sur la période | contenu servi |
| `rang` | entier | rang servi |
| `impressions` | entier | nombre d'affichages |
| `clics` | entier | clics observés |
| `propension` | réel, **facultatif** | probabilité de service, si la plateforme la connaît |

**Tableau 4 — exposition par point de vue**

| Colonne | Type | Description |
|---|---|---|
| `rang` | entier | rang servi |
| `point_de_vue` | libellé | catégorie du **catalogue de référence déclaré par le régulateur** |
| `impressions` | entier | nombre d'affichages |
| `clics` | entier | clics observés |

Le catalogue de points de vue est une **décision du régulateur**, non de la plateforme ni du
chercheur : c'est la discrétisation politique que l'[audit critique](limites.md) désigne comme
la principale réserve d'usage de l'index. La demande porte sur son application, pas sur son
choix.

## IV. Nécessité et proportionnalité (art. 8(d) du règlement délégué)

**Ce que ces tableaux permettent — et rien de plus.**

| Mesure | Tableaux nécessaires |
|---|---|
| test d'échangeabilité — le journal est-il seulement corrigible ? | 1, 1 bis, 2 |
| sévérité $\eta$ du biais de position | 3 |
| estimation contrefactuelle et taille d'échantillon effective | 3, avec propensions |
| diversité composée et diversité exposée, écart d'enterrement | 4 |

**Ce qui est vérifié, non affirmé.** Le [notebook 18](notebooks/18_demande_article_40.ipynb)
recalcule ces mesures deux fois — directement sur un journal complet, puis sur les seuls
tableaux — et publie l'écart. Il est de $3 \times 10^{-12}$ pour le test d'échangeabilité et
**exactement nul** pour la sévérité. Le code qui consomme les tableaux est
[`ide.aggregates`](https://github.com/s-geffroy/Indice-Diversite-Exposee/blob/main/src/ide/aggregates.py),
et onze tests le verrouillent.

**Ce que cela pèse.** Sur Baidu-ULTR, 524 164 documents servis donnent **5 543 lignes**
demandées, soit un rapport de **95**. Sur MIND, 5 843 444 contenus servis donnent **57 906**
lignes, rapport **101**.

**Ce qui n'est pas demandé** : aucun identifiant de lecteur, aucune séquence de navigation,
aucun contenu, aucun texte, aucun paramètre de classement, aucun modèle. Un fil ne figure dans
ces tableaux que par sa **forme** et par le nombre de clics qu'il a reçus.

**Conséquence sur l'article 40(5).** Une plateforme peut demander l'amendement d'une requête si
la divulgation créerait des vulnérabilités de sécurité ou révélerait des secrets d'affaires. Des
comptages par rang et par point de vue déclaré ne révèlent ni le classement, ni ses paramètres,
ni les contenus : ils disent **ce qui a été exposé**, pas comment la plateforme a décidé de
l'exposer.

## V. Risques, confidentialité et protection des données (art. 8(e))

**Données personnelles.** Les tableaux demandés n'en contiennent pas : la plus petite unité est
la cellule, et aucune ligne ne désigne un lecteur. Le traitement ne relève donc pas d'une
communication de données à caractère personnel, ce qui retire à la demande son principal risque
et à la plateforme son principal motif d'opposition.

**Seuil de confidentialité.** La demande propose un seuil de suppression de [SEUIL] impressions
par cellule, et demande qu'il soit **publié avec les données**. Ce seuil n'est pas neutre, et
son effet est mesuré plutôt que supposé : sur Baidu-ULTR, passer de 5 à 20 impressions déplace
la sévérité estimée de **1,10 à 1,40**, soit +27 %, parce que les cellules rares sont celles des
rangs profonds, dont l'estimation tire l'essentiel de son information.

**Modalités d'accès.** Un environnement de traitement sécurisé au sens de l'article 9(5) du
règlement délégué est accepté sans réserve. Compte tenu de la nature agrégée des données, une
transmission simple paraît toutefois proportionnée.

**Sécurité.** [MESURES TECHNIQUES ET ORGANISATIONNELLES DE L'ORGANISME].

**Financement** (art. 8(b)) : [SOURCES DE FINANCEMENT]. **Indépendance** (art. 40(8)(b)) :
[DÉCLARATION].

## VI. Publication des résultats (art. 40(8) et art. 8(a))

L'engagement de publication est déjà tenu par avance : l'intégralité du code, des données
dérivées, des figures et des résultats — **y compris les résultats négatifs** — est publiée
dans un dépôt public, sous licence MIT pour le code et CC BY 4.0 pour les contenus. Les six
résultats négatifs déjà publiés par ce dépôt en sont la démonstration la plus utile.

Les données reçues elles-mêmes ne seront pas republiées ; les **agrégats dérivés** le seront,
ainsi que le code qui les produit, conformément à la pratique déjà appliquée aux trois jeux
mesurés.

## VII. Calendrier et voies de recours

| Étape | Délai | Source |
|---|---|---|
| Décision du coordinateur : requête motivée ou rejet | **80 jours ouvrables** | art. 7(1) du règlement délégué |
| Demande d'amendement par la plateforme | 15 jours | art. 40(5) du DSA |
| Décision du coordinateur sur l'amendement | 15 jours | art. 40(6) du DSA |
| Notification de la mise à disposition | 3 jours ouvrables | art. 15(1) du règlement délégué |
| Demande de médiation | 5 jours ouvrables | art. 13(1) |
| Ouverture, puis durée de la médiation | 20, puis 40 jours ouvrables au plus | art. 13(4), 13(9) |

L'article 15(3) du règlement délégué interdit par ailleurs au fournisseur d'imposer des
limitations à l'usage d'outils d'analyse standard, sauf si la requête motivée les mentionne
explicitement.

## VIII. Ce que nous ferons d'un refus

Le refus sera publié, motivé tel qu'il aura été reçu, et analysé au même titre qu'un résultat :
une demande de cette forme ne peut être écartée pour disproportion sans que le motif porte sur
autre chose que sa taille. C'est la raison d'être de la spécification — **déplacer la charge de
la preuve**, et rendre le refus argumentable.

---

## Les réserves de cette demande

**Ces tableaux ne permettent pas tout.** Ils ne disent rien de la trajectoire d'un lecteur, donc
rien des bulles de filtres individuelles, ni de la dynamique temporelle d'un fil pour un même
usager. C'est délibéré — ce sont les analyses qui exigeraient des données personnelles — mais
il faut le dire : cette demande est étroite, et une partie du programme de recherche du dépôt
n'y entre pas.

**L'agrégat est une hypothèse.** Les tableaux 1 et 2 sont indexés par le profil de rangs et par
le nombre de clics du fil précisément parce que deux hypothèses plus simples se sont révélées
fausses à l'usage, sur données réelles, sans produire d'erreur visible. Une plateforme qui
livrerait ces tableaux sous une clé plus grossière livrerait des chiffres faux du bon ordre de
grandeur — le pire cas.

**Et l'éligibilité manque.** Ce document est un modèle, non une démarche engagée. Sa valeur est
d'être **prêt** : un organisme de recherche qui voudrait poser cette question n'a plus à
concevoir la spécification, seulement à la déposer.

---

*Implémentation : `ide.aggregates` · Notebook :
[18 — Ce qu'il faut demander](notebooks/18_demande_article_40.ipynb) ·
[exploration réelle de MIND](mind.md) · [journaux qui enregistrent le rang](rang-servi.md) ·
[mémorandum](memorandum.md)*
