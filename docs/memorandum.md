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
([modèles](theorie/fokker-planck.md), [tests](https://github.com/s-geffroy/Index-Dissipation-Entropique/tree/main/tests)),
mais ses paramètres n'ont **aucune calibration empirique**. Il propose donc un *cadre
métrologique* et des *grandeurs à mesurer*, pas des seuils prêts à être inscrits dans
un texte.

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

### 1. Imposer un plancher d'Index de Dissipation Entropique

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

**Réserve à traiter dans le texte.** L'index est manipulable : de la diversité
d'étiquette peut satisfaire un seuil sans diversifier l'argument. Une norme technique
crédible doit prévoir un contrôle qualitatif d'échantillon en complément de la mesure.

### 2. Auditer les coefficients d'amortissement cinétique

**Mesure.** Interdire les configurations algorithmiques où le taux d'amplification d'un
contenu dépasse son taux d'amortissement naturel :

$$\gamma\alpha > \lambda \quad \text{(configuration interdite)}$$

**Fondement.** Au-delà de ce seuil, l'amortissement effectif de la boucle de
rétroaction devient négatif : le système accumule l'énergie au lieu de la dissiper.
C'est l'effet Larsen informationnel, et le seuil est net
([notebook 06](notebooks/06_resonance_larsen.ipynb)).

**Pourquoi cette recommandation est la plus solide.** Elle ne suppose aucune intention
malveillante à démontrer. À gain uniforme, un contenu plus émotionnel franchit le
seuil qu'un contenu factuel ne franchit pas : le biais est **mécanique**. Un audit de
$\gamma$ est donc plus pertinent — et plus opposable — qu'un audit d'intentions
éditoriales.

**Difficulté opérationnelle.** $\lambda$ et $\alpha$ ne sont pas directement lisibles
dans le code d'une plateforme. Leur estimation demande un protocole d'inférence à partir
de séries temporelles de visibilité, qui reste à construire.

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

### Ce qui manque pour rendre ce cadre opérationnel

Ces manques sont réels et il serait malhonnête de les taire :

| Manque | Nature |
|---|---|
| calibration de $J$, $T$, $\gamma$, $\alpha$ sur données réelles | aucune procédure proposée |
| protocole d'audit préservant la vie privée | aucune conception |
| définition normative du catalogue de points de vue $k$ | choix politique non tranché |
| résistance de l'index au *gaming* | non étudiée |
| coût en pertinence perçue d'un plancher d'IDE | non évalué |

Le mémorandum doit donc être lu comme une **proposition de cadre à durcir**, pas comme
un dispositif prêt à l'emploi. Sa contribution est de nommer des grandeurs mesurables
là où le débat réglementaire raisonne encore en volumes de contenus retirés.

---

*Voir aussi : [audit critique et limites](limites.md) ·
[feuille de route](feuille-de-route.md) · [appel à relecture](relecture.md)*
