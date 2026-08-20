# Mémorandum de régulation technique et éthique

**À l'attention de** — régulateurs du numérique (ARCOM, PEReN, Commission européenne)

**Objet** — stabilisation thermodynamique de l'espace informationnel et lutte contre la
résonance algorithmique des fausses informations

**Statut** — document de travail ouvert à la relecture critique. Les valeurs numériques
citées sont des **valeurs d'illustration** issues de simulations, non des
recommandations chiffrées.

---

## Préambule : ce que ce mémorandum peut et ne peut pas prétendre

Le raisonnement qui le sous-tend est formalisé et vérifié numériquement
([modèles](theorie/fokker-planck.md), [tests](https://github.com/s-geffroy/Indice-Diversite-Exposee/tree/main/tests)).
Une seule de ses grandeurs a fait l'objet d'une mesure sur données réelles — le rapport
$\gamma\alpha/\lambda$, [estimé](calibration.md) sur des séries d'attention publiques ; les
autres paramètres ne sont pas calibrés. Ce mémorandum propose donc un *cadre métrologique* et
des *grandeurs à mesurer*, pas des seuils prêts à être inscrits dans un texte.

Cette tentative de mesure a d'ailleurs conduit à **réécrire deux fois la recommandation 2**,
puis à conclure que la grandeur qu'elle visait n'est pas celle qu'un régulateur peut
constater. C'est un argument pour mesurer avant de légiférer, non pour tenir le cadre pour
acquis.

Une seconde réserve doit être posée d'emblée. Le fil de travail d'origine concluait que
« la régulation cesse d'être une censure arbitraire pour devenir une ingénierie de la
stabilité ». La formule est séduisante et il faut s'en méfier : **une ingénierie de la
stabilité *est* une intervention sur le débat public.** Elle peut être légitime, mais
elle doit être justifiée comme telle, avec les garde-fous démocratiques
correspondants — non naturalisée par un vocabulaire emprunté à la thermodynamique.

---

## I. Recommandations techniques

Le constat commun aux trois recommandations : la vérification passive des contenus
(*fact-checking*) agit **après** que la cinétique s'est produite. Or les modèles
montrent que le phénomène est déterminé par des paramètres structurels de l'algorithme,
pas par le contenu pris un à un. Ce sont ces paramètres qu'il faut rendre observables.

### 1. Imposer un plancher d'Indice de Diversité Exposée

!!! abstract "Ce qui est recommandé aujourd'hui — après trois corrections"
    **La norme.** Un plancher sur l'entropie des **contenus servis**, projetés sur les bacs d'un
    **catalogue de référence déclaré par le régulateur**, et **pondérés par l'attention** qu'appelle
    chaque rang. Ni sur les étiquettes annoncées, ni sur la seule composition du fil.

    **Les deux grandeurs à publier avec elle** :

    * l'**écart entre la mesure aveugle au rang et la mesure consciente du rang** du même fil —
      il vaut zéro pour une plateforme qui ne relègue pas, et c'est la seule grandeur du dépôt
      qui se seuille directement ;
    * l'**excès de signature** — l'écart entre deux indices calculés sur le même fil, rapporté à
      ce qu'un catalogue honnête afficherait, qui croît avec le découplage étiquette/contenu.

    **Le prix, chiffré** : un plancher conscient du rang coûte 10,6 % à 20,9 % d'engagement
    selon la mesure, contre 5,9 % à 10,7 % pour un plancher aveugle qui ne protège de rien.

    **Ce que le régulateur fixe** : le catalogue de référence, la grandeur agrégée (la part de
    la population sous le seuil, pas la moyenne), et le niveau du seuil — qu'aucun calcul de ce
    dépôt ne détermine.

    **Ce qui reste non vérifié** : cette forme n'a jamais été mesurée sur un fil réel, faute
    d'un jeu de données portant à la fois le rang servi et une étiquette de point de vue.
    → [demande au titre de l'article 40](article-40.md)

    **Deux objections anticipées, et ce que la mesure en dit** :

    * *« il faudrait refondre nos moteurs »* — **non**. Une heuristique de diversification
      publiée en 1998 tient un plancher de 0,80 sans perte mesurable d'engagement, et le
      classement par pertinence reste le cas limite à coefficient nul. Ce que la norme exige est
      de **mesurer**, pas de reconstruire. → [lignes de base](lignes-de-base.md) ;
    * *« le coût sera prohibitif »* — **cela dépend du lecteur**, et il faut l'admettre : de
      3,8 % d'engagement pour un lecteur dont les intérêts traversent les points de vue à 17,1 %
      pour un lecteur dont la préférence *est* un point de vue, au même plancher de 0,90. La
      norme coûte le plus cher là où elle sert le plus, ce qui est précisément l'endroit où
      l'objection sera formulée.

    Le détail des trois corrections qui ont conduit là est conservé ci-dessous, dans l'ordre où
    elles sont survenues.

**Mesure.** Exiger des très grandes plateformes (VLOP au sens du DSA) qu'elles
maintiennent l'[IDE](ide.md) des fils d'actualité individuels au-dessus d'un seuil
$H_{\text{critique}}$. Sous ce seuil, la plateforme est tenue de réinjecter un « flux de
refroidissement » composé de contenus à haute diversité sémantique.

**Fondement.** Un IDE effondré est la signature d'une température sociale locale nulle,
c'est-à-dire d'un état figé au sens du modèle d'Ising. Sous cette température, la
mémoire des fausses croyances devient persistante
([notebook 05](notebooks/05_hysteresis_et_contre_champ.ipynb)).

**Ce que le régulateur doit fixer lui-même :**

* le **catalogue de référence $k$** — sans dénominateur imposé, l'index est flatteur
  pour les fils les plus fermés ;
* la **grandeur agrégée** — la part de la population sous le seuil, et non la moyenne :
  une moyenne satisfaisante peut masquer une minorité entièrement enfermée ;
* le **seuil** lui-même, qui reste à calibrer empiriquement.

**Ce que le régulateur ne devrait pas fixer** : l'implémentation. L'[ADE](ade.md) est
une façon d'atteindre l'objectif, pas la seule. Imposer un algorithme serait à la fois
inapplicable et contre-productif.

!!! failure "Recommandation révisée après le test adverse — le plancher doit porter sur Rao"
    La réserve ci-dessous, laissée en suspens, a été mise à l'épreuve par simulation
    ([test adverse](gaming.md)), et elle est **fondée au-delà de ce qui était supposé** : une
    plateforme capable de dissocier l'étiquette du contenu obtient un **IDE de 1,000 — la note
    maximale — pour une diversité de contenu strictement nulle**, sans céder un point
    d'engagement. Il n'est même pas besoin d'aller jusque-là : à mi-découplage, la contrainte
    n'a plus que **36 %** de sa force.

    **Un plancher d'IDE sur les étiquettes n'est donc pas une norme tenable.** La mesure doit
    porter sur les **contenus** servis, non sur les étiquettes qui les annoncent.

    !!! danger "Corrigé une seconde fois — pas sur l'entropie de Rao"
        Cette recommandation a d'abord désigné l'**entropie quadratique de Rao**. C'était une
        erreur, et du plus mauvais genre : l'entropie de Rao est la *distance intra-liste*,
        dont l'optimum sous contrainte est **bimodal**. Elle attribue 1,000 à un fil servant
        les deux bords et rien entre eux, contre 0,750 à un fil étalé — **un plancher de Rao
        prescrirait la polarisation.**

    **Le plancher retenu porte sur l'entropie de position** : l'entropie de Shannon des
    contenus servis, projetés sur les bacs du catalogue de référence. C'est l'IDE à une
    substitution près — les contenus au lieu des étiquettes — donc la même lecture, la même
    échelle, et un coût de conformité inférieur à celui de l'entropie de Rao.

    **Le plus grand vide est publié à côté du plancher.** L'entropie est *nominale* : elle
    compte les points de vue occupés sans voir leur écartement. Le diagnostic couvre ce
    qu'elle ne voit pas, et il est ce qui rend la bimodalité constatable.

    !!! danger "Et la mesure doit être consciente du rang"
        Une mesure portant sur la seule composition du fil se laisse satisfaire en
        **enterrant** les contenus divergents au bas du classement : à composition identique,
        cela rapporte 10 % d'engagement sans changer la mesure d'un point. Le plancher doit
        donc porter sur une distribution **pondérée par l'attention accordée à chaque rang**.
        → [Rang et contrefactuel](evaluation.md)

        **Son prix est chiffré** : le coût d'engagement double — de 8,2 % à 18,9 % pour
        l'entropie de Rao, de 10,7 % à 20,9 % pour l'entropie de position. Une plateforme
        certifiée à 0,70 par une mesure aveugle n'expose en réalité que 0,36.
        → [Rang adverse et sévérité](rang-adverse.md)

        **Grandeur de contrôle associée** : l'écart entre la mesure aveugle et la mesure
        consciente du rang du **même** fil. Contrairement à l'excès de signature, il compare
        une mesure à elle-même et se seuille donc directement — il vaut zéro pour une
        plateforme qui ne relègue pas.

    Ce que le régulateur doit alors fixer en plus : le **catalogue de référence**, qui sert à
    la fois de grille et d'unité. C'est la même question politique que le choix de $k$,
    déplacée d'un cran.

    **Disposition complémentaire.** Publier les deux indices sur le même fil et contrôler
    l'**excès de signature** — l'écart IDE − Rao rapporté à ce qu'un catalogue honnête
    afficherait au même index. Il vaut zéro pour une plateforme honnête et croît avec la
    manipulation. → [Test adverse de l'index](gaming.md)

    **Successeur à instruire.** Une *proximité à une cible déclarée* — divergence entre
    l'exposition servie et une distribution que le régulateur publie — est la seule des mesures
    éprouvées qui rende explicite la forme d'exposition visée, au lieu de la supposer. C'est
    aussi la porte d'entrée vers les métriques de diversité normative du domaine.

**Réserve d'origine, conservée pour mémoire.** L'index est manipulable : de la diversité
d'étiquette peut satisfaire un seuil sans diversifier l'argument. Une norme technique
crédible doit prévoir un contrôle qualitatif d'échantillon en complément de la mesure.

### 2. Plafonner le rapport d'amplification sur amortissement

!!! warning "Recommandation révisée après mesure"
    Cette recommandation était initialement formulée comme l'interdiction des
    configurations où $\gamma\alpha > \lambda$. La [calibration empirique](calibration.md)
    montre que cette formulation est **inapplicable** : le rapport dépasse 1 dans les
    19 épisodes mesurés, sous tous les estimateurs. C'est logique — un épisode
    d'attention observable a nécessairement connu une phase de croissance. Vérifier le
    signe n'apprend rien.

**Mesure.** Imposer un **plafond** au rapport entre le taux d'amplification d'un contenu et
son taux d'amortissement naturel :

$$\frac{\gamma\alpha}{\lambda} \leq \rho_{\max}$$

**Fondement.** Au-delà de $\gamma\alpha = \lambda$, l'amortissement effectif de la boucle de
rétroaction devient négatif : le système accumule l'énergie au lieu de la dissiper
([notebook 06](notebooks/06_resonance_larsen.ipynb)). Ce régime est la norme et non
l'exception — la mesure situe l'écosystème informationnel entre **1,5 et 12**, de médiane
**2,5 à 4,2** ([notebook 09](notebooks/09_calibration_visibilite.ipynb)). La grandeur
réglementaire pertinente est donc la **marge**, pas le franchissement.

**Pourquoi cette recommandation reste la plus solide.** Elle ne suppose aucune intention
malveillante à démontrer. À gain uniforme, un contenu plus émotionnel devrait franchir le
seuil qu'un contenu factuel ne franchit pas : le biais serait **mécanique**, et un audit de
$\gamma$ plus opposable qu'un audit d'intentions éditoriales.

**Réserve, à porter au dossier.** Ce dernier point n'est **pas étayé par les données** : la
mesure ne détecte aucun écart de rapport entre contenus d'accusation et annonces
scientifiques ($p \geq 0{,}13$). L'argument mécanique reste théoriquement solide, mais un
régulateur ne doit pas le présenter comme démontré.

**Difficultés opérationnelles, désormais chiffrées.**

* $\rho_{\max}$ n'est pas déterminé par la théorie. La mesure fournit une référence
  descriptive, pas un seuil normatif.
* La valeur estimée **dépend de la méthode** : la médiane varie d'un facteur 1,7 selon la
  fenêtre d'ajustement. Un seuil adossé à une valeur unique serait attaquable ; le protocole
  d'estimation doit être normalisé en même temps que le seuil.
* La mesure disponible porte sur un **gain d'écosystème**, non sur le $\gamma$ interne d'une
  plateforme. Y accéder demande l'article 40 du DSA.
* La méthode par pic est **aveugle aux régimes installés**. Une seconde méthode les
  [détecte bien](regimes.md), mais **n'identifie pas** le rapport sur ces cas — et une limite
  théorique s'y ajoute : sous une saturation logistique, $\gamma\alpha/\lambda$ n'est pas
  identifiable, quelle que soit la qualité des données.

!!! tip "Un indicateur de remplacement, lui, se mesure — mais ne prouve rien"
    La détection de changement de régime livre deux grandeurs robustes que le rapport
    d'amplification n'offre pas : **la date du basculement** et **l'élévation du palier**.
    Elles se mesurent sur données publiques, sans hypothèse de forme, et portent sur ce qu'un
    régulateur cherche réellement à constater : non la vitesse d'un emballement, mais la durée
    pendant laquelle une fausse croyance reste installée.

    **Elles ne discriminent pas les registres émotionnels pour autant.** Une première mesure
    sur vingt-quatre sujets suggérait un écart de ×9,2 contre ×2,9 ; la vérification sur
    [440 sujets dérivés de catégories](corpus-etendu.md) l'a réduit à ×3,04 contre ×2,90
    ($p = 0{,}53$), et a montré que l'écart de taux de basculement était un effet d'audience.
    L'[annotation en aveugle](annotation.md) du registre a clos la question : à étiquette
    corrigée, le taux de basculement passe de 8,6 % contre 2,7 % à **4,8 % contre 5,1 %**
    ($p = 1{,}00$). L'écart n'était pas dilué par un étiquetage approximatif, il n'existe pas.

    Un régulateur peut donc s'en servir pour **constater** un basculement durable, non pour
    établir qu'une catégorie de contenus en produit davantage.
    → [Changements de régime](regimes.md) · [Corpus étendu](corpus-etendu.md) ·
    [Annotation en aveugle](annotation.md)

### 3. Brider la portée des super-diffuseurs en cas d'anomalie cinétique

**Mesure.** Imposer des limites dynamiques à la portée des partages en cascade dès
qu'une anomalie de propagation est détectée.

**Fondement — et une correction importante.** Le raisonnement d'origine soutenait que
la structure « petit monde » des réseaux sociaux rend le consensus impossible. C'est
mesurablement faux : le temps de consensus croît comme $N^2$ sur un réseau local et
comme $N$ seulement en champ moyen — **la connectivité globale accélère la
convergence** ([notebook 03](notebooks/03_voter_consensus_et_taille.ipynb),
[audit, point 12](limites.md)).

Ce qui fragmente n'est pas la densité des liens mais le **biais directionnel** des
micro-champs algorithmiques et l'homophilie qui compartimente le graphe.

Cette recommandation reste donc défendable comme **mesure d'urgence** — ralentir une
cascade laisse le temps à la vérification d'agir — mais elle ne doit pas être présentée
comme le remède structurel. Les recommandations 1 et 2 sont mieux étayées.

---

## II. Recommandations éthiques et comportementales

### 1. Neutraliser la « taxe d'engagement »

Considérer la maximisation du temps de rétention par l'exploitation d'émotions
négatives comme une **nuisance sociétale**, sur le modèle des externalités
environnementales, et inciter fiscalement ou juridiquement au découplage du modèle
économique de la friction permanente.

### 2. Transparence de l'évaluation du potentiel social

Garantir le droit de chaque citoyen à connaître la forme du potentiel social auquel il
est soumis : une jauge lisible indiquant le niveau de diversité de son propre fil, et
la mesure dans laquelle son espace décisionnel a été incurvé par les micro-champs
$H_i(t)$.

**Réserve.** Ce droit suppose de mesurer des fils individuels. Le protocole doit être
agrégatif et différentiellement privé, faute de quoi la transparence se paie en
surveillance.

### 3. Droit au bruit thermique et à l'oubli algorithmique

Inscrire un principe de **déconnexion des biais** : la possibilité d'activer d'un clic
un mode « exploration fluide » qui remonte artificiellement la température sociale et
désactive le filtrage collaboratif, afin de briser l'effet d'hystérésis entretenu par
l'historique.

**Une nuance mesurée, et elle importe.** Le bruit n'est pas monotoniquement
bénéfique : au-delà d'un certain niveau, la diversité d'exposition se dégrade à nouveau
([notebook 08](notebooks/08_abm_compas_politique.ipynb)). Le fil de travail l'avait
anticipé — « injecter du bruit en permanence rend la société chaotique et illisible ».
Ce n'est donc pas la quantité de bruit qui compte mais son **dosage**, ce qui plaide
pour un mode ponctuel et un recuit cyclique plutôt qu'un bruit permanent.

---

## III. Cadre de contrôle : une métrologie de l'espace informationnel

```
[Flux de données des plateformes]
            │
            ▼
[Simulateur Fokker-Planck du régulateur]
            │
            ├──▶ distribution unimodale centrée  ─────▶ conforme
            │
            └──▶ distribution bimodale sans zone
                 de modération centrale           ─────▶ alerte, puis sanction DSA
```

### Les « scanneurs de phase »

Plutôt que de compter les signalements de fausses informations — indicateur retardé et
manipulable — le régulateur simule l'état de l'opinion à partir des distributions
fournies par les API des plateformes, et détecte les **transitions de phase**.

La grandeur pertinente n'est pas le nombre de contenus problématiques mais la **forme
de la distribution** : une bimodalité franche sans zone de modération centrale
caractérise un espace informationnel dégradé, indépendamment du contenu de chaque
message.

### Ce qu'un journal doit contenir pour être auditable

Le DSA ouvre aux chercheurs et au régulateur un accès aux données des plateformes (article 40).
Cette section dit ce que cet accès doit exiger pour ne pas être vide.

**Le rang servi, ou à défaut la propension d'exposition.** Un clic dépend de deux choses, la
pertinence du contenu et l'exposition qu'on lui a donnée. Sans le rang, les deux restent
confondues, et aucune évaluation contrefactuelle d'un réordonnancement n'est possible — ni par
le régulateur, ni par la plateforme elle-même. Publier cette colonne ne révèle rien du code de
classement : elle dit *où* un contenu a été montré, pas *pourquoi*.

**Ce que l'anonymisation ne doit pas détruire.** Mélanger l'ordre d'affichage avant publication
ne rend pas un journal non biaisé : les clics ont été produits sous l'ordre réel et en portent
le biais en entier. Le mélange retire seulement la variable qui permettrait de le corriger — il
rend le journal **non corrigible**. C'est le cas de [MIND](mind.md), le jeu de référence de la
recommandation d'actualité. → [L'exploration réelle de MIND](mind.md)

**Contrôle d'acceptation.** Avant tout audit reposant sur un journal transmis, passer le **test
d'échangeabilité intra-fil** : à fil donné, les clics sont-ils répartis indépendamment de la
position enregistrée ? Le test est exact et son étalonnage de puissance dit ce qu'il aurait su
détecter. Un journal qui le « passe » — au sens où l'ordre y est indiscernable d'un mélange —
n'est pas auditable contrefactuellement, et il vaut mieux l'établir avant l'audit qu'après.

**Pourquoi ce contrôle n'est pas facultatif.** Sans lui, l'estimation de l'exposition ne
s'interrompt pas : elle renvoie un chiffre. Sur MIND, l'estimateur de sévérité accepte le jeu,
se déclare identifiable et produit **cinq sévérités incompatibles** selon un simple paramètre de
nuisance, de $-0{,}13$ à $+0{,}25$, toutes assorties d'une erreur type inférieure à 0,007. Un
audit fondé sur l'une d'elles serait indiscernable d'un audit correct.

**L'exigence n'est pas utopique : un jeu public la satisfait déjà.** L'[Open Bandit
Dataset](rang-servi.md) publie la position servie **et** la propension vraie de chaque
affichage, et contient un seau où la politique de service est uniformément aléatoire. Sur ce
jeu, l'estimation contrefactuelle de la valeur d'une politique jamais déployée tombe à **2,5 %**
de sa valeur mesurée directement, là où l'estimation naïve se trompe de 32 %. Ce qui est demandé
ici a donc un précédent industriel, publié sous licence libre par la plateforme elle-même.

**Disposition complémentaire : exiger une fraction d'exploration.** Le même jeu montre pourquoi
publier les propensions ne suffit pas. Sur 4 077 727 impressions servies par une politique
optimisée, la **taille d'échantillon effective** de l'estimation tombe à **1 513**, soit 0,04 % :
une politique très sûre d'elle rend ses propres journaux presque inexploitables pour évaluer
autre chose qu'elle-même. Un audit sérieux suppose donc qu'une fraction du trafic soit servie de
façon **délibérément aléatoire** — c'est le prix, faible et chiffrable, de l'auditabilité.

**Grandeur de contrôle associée** : la taille d'échantillon effective, publiée avec toute
estimation contrefactuelle. Elle dit combien d'observations portent réellement le chiffre, et
elle est la seule à distinguer une mesure d'une coïncidence.

**Disposition complémentaire : normaliser la forme de la demande.** Ce que l'audit exige tient
en **quatre tableaux agrégés** — profils de fils, clics par rang, cellules (contenu, rang),
exposition par point de vue déclaré — dont il est [vérifié](article-40.md) qu'ils recalculent à
l'identique le test d'échangeabilité, la sévérité du biais de position et les deux mesures de
diversité. Aucun ne contient de donnée personnelle, et l'ensemble pèse une centaine de fois
moins de lignes que le journal correspondant.

Standardiser ce format servirait les deux parties : il retire à la plateforme le motif de refus
de l'article 40(5) — des comptages par rang ne révèlent ni le classement ni ses paramètres — et
il donne au régulateur un livrable dont la conformité se vérifie, au lieu d'un accès dont
l'étendue se négocie. Le **seuil de suppression des faibles effectifs** doit y être fixé et
publié : sur données réelles, passer de 5 à 20 impressions par cellule déplace la sévérité
estimée de 27 %.

### Ce qui manque pour rendre ce cadre opérationnel

Ces manques sont réels et il serait malhonnête de les taire :

| Manque | Nature |
|---|---|
| calibration de $\gamma\alpha/\lambda$ | **fait** — [mesuré](calibration.md) entre 1,5 et 12 sur 19 épisodes publics, avec ses réserves |
| calibration de $J$ et $T$ sur données réelles | aucune procédure proposée |
| valeur normative de $\rho_{\max}$ | la mesure décrit, elle ne prescrit pas |
| estimation du $\gamma$ **interne** d'une plateforme | demande l'accès article 40 du DSA |
| détection des régimes de désinformation **installés** | **fait** — [14 changements datés](regimes.md), QAnon et désinformation sanitaire compris |
| identification de $\rho$ sur les régimes installés | échoue : dispersion réelle quatre fois trop élevée, et non identifiable sous saturation logistique |
| calibration de l'indicateur de **persistance** | **fait, et négatif** — l'écart de ×9,2 contre ×2,9 du corpus pilote ne s'est pas répliqué sur [440 sujets](corpus-etendu.md), et l'[annotation en aveugle](annotation.md) l'a éliminé définitivement. L'indicateur constate, il ne discrimine pas |
| existence d'un effet de la **charge émotionnelle** $\alpha$ | **quatre mesures, aucun effet** : amplification, persistance sur corpus pilote puis étendu, taux de basculement |
| protocole d'audit préservant la vie privée | aucune conception |
| définition normative du catalogue de points de vue $k$ | choix politique non tranché |
| résistance de l'index au *gaming* | **fait, et négatif** — un plancher d'IDE se sature à coût nul ([test adverse](gaming.md)) ; la mesure doit porter sur l'entropie de Rao |
| calibration du plancher d'**entropie de position** | aucune procédure — le test adverse établit la forme de la norme, pas son niveau |
| choix de la **cible d'exposition** | question politique non tranchée, que la mesure par divergence rend explicite au lieu de l'enfouir |
| coût en pertinence perçue d'un plancher d'IDE | **chiffré en simulation** — 0 à 17 % selon le plancher et selon l'alignement entre pertinence et point de vue ([lignes de base](lignes-de-base.md)) ; jamais mesuré sur un fil réel |
| évaluation contrefactuelle sur un jeu de données public | **fait, et négatif** — [MIND](mind.md) ne conserve pas le rang d'affichage : l'exposition n'y est pas identifiable, et l'estimation qu'on y mène quand même renvoie cinq sévérités incompatibles |
| exigence de publication du **rang servi** dans les journaux transmis | proposée ici, non instrumentée côté régulateur — mais [un jeu public la satisfait déjà](rang-servi.md) |
| valeur de $\eta$ à retenir pour un fil d'actualité | **mesurée ailleurs, non transportable** : 1,10 sur une page de résultats, 0,04 à 0,11 sur un bandeau de trois vignettes |
| fraction d'exploration aléatoire exigible d'une plateforme | proposée ici ; sans elle la taille d'échantillon effective d'un audit tombe à 0,04 % |
| **format normalisé** d'une demande d'accès aux données | **fait** — [quatre tableaux agrégés](article-40.md), vérifiés suffisants, sans donnée personnelle |
| dépôt effectif d'une demande au titre de l'article 40 | **hors de portée de ce dépôt** : l'art. 40(8)(a) exige une affiliation à un organisme de recherche |

Le mémorandum doit donc être lu comme une **proposition de cadre à durcir**, pas comme
un dispositif prêt à l'emploi. Sa contribution est de nommer des grandeurs mesurables
là où le débat réglementaire raisonne encore en volumes de contenus retirés.

---

*Voir aussi : [audit critique et limites](limites.md) ·
[feuille de route](feuille-de-route.md) · [appel à relecture](relecture.md)*
