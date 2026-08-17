# Audit critique et limites

Ce document est la pièce centrale du dépôt.

Le travail dont il est issu a été construit sous forme de fil de discussion, en une
journée, par accumulation d'analogies. Cette méthode produit des intuitions justes
et des raccourcis qui ne tiennent pas. Publier le fil tel quel exposerait
l'ensemble à être écarté sur un détail, alors que l'intuition de départ mérite mieux.

Quinze points sont documentés. Chacun suit la même structure : ce que le fil affirmait, pourquoi
c'est un problème, et la formulation retenue. Les corrections sont **traçables** :
chacune est implémentée dans `src/`, vérifiée dans `tests/`, et illustrée dans un
notebook.

La dernière section, [ce que le modèle ne peut pas faire](#ce-que-le-modele-ne-peut-pas-faire),
ne corrige rien : elle énumère les limites qui subsistent, y compris celles qui
touchent à l'usage réglementaire de l'index.

---

## A. Nomenclature

### 1. L'index et l'algorithme sont deux objets distincts

**Le fil.** Le résumé exécutif écrit « nous préconisons une régulation technique
imposant un **Index de Dissipation Entropique** (ADE) ». Le sigle et le nom
désignent deux choses différentes, et le reste du fil emploie les deux
indifféremment.

**Le problème.** Ce n'est pas une coquille. Un index est une **métrique** — quelque
chose qu'un régulateur mesure et dont il fixe un seuil. Un algorithme est un
**mécanisme** — quelque chose qu'une plateforme implémente. Les confondre rend la
proposition réglementaire inintelligible : impose-t-on une mesure ou une
implémentation ? La différence est considérable, juridiquement comme
techniquement.

**Retenu.**

| Sigle | Objet | Nature | Qui l'utilise |
|---|---|---|---|
| **IDE** | Index de Dissipation Entropique | métrique auditable, dans $[0, 1]$ | le régulateur |
| **ADE** | Algorithme de Dissipation Entropique | filtre de recommandation | la plateforme |

L'IDE se mesure sans accès au code : il suffit d'observer les contenus servis.
L'ADE est une façon parmi d'autres de le maintenir au-dessus d'un seuil. Le
mémorandum impose le premier et **ne prescrit pas** le second — imposer une
implémentation serait à la fois inapplicable et contre-productif.

Équivalents anglais : *Entropic Dissipation Index* (EDI) et *Entropic Dissipation
Algorithm* (EDA).

*Implémenté dans `ide.entropy.entropic_dissipation_index` et `ide.ade`.*

---

## B. Corrections mathématiques

### 2. Le signe du coefficient de régulation

**Le fil.** Le score de l'ADE est d'abord écrit
$S(i,c) = \mathrm{Pertinence}(i,c) - \mu \cdot \Delta H(i,c)$, puis quelques lignes
plus loin : « nous configurons l'algorithme avec un signe positif
($+\mu \cdot \Delta H$) pour récompenser les contenus qui maximisent l'entropie ».

**Le problème.** Les deux versions font l'inverse l'une de l'autre. Avec
$\Delta H > 0$ pour un contenu qui diversifie le fil, la version négative
**pénalise** la diversité : elle refermerait la bulle qu'elle prétend ouvrir. Une
plateforme de mauvaise foi pourrait implémenter la première version et se réclamer
du texte.

**Retenu.** $S(i,c) = \mathrm{Pertinence}(i,c) + \mu \cdot \Delta H(i,c)$ avec
$\mu \ge 0$ et $\Delta H = H_{\text{futur}} - H_{\text{actuelle}}$. Le code **refuse**
un $\mu$ négatif par une exception explicite, plutôt que de l'accepter
silencieusement.

*Vérifié par `tests/test_ade.py::TestEntropicScore` — dont un test s'assure qu'à
$\mu = 0$ l'ADE est indiscernable d'un filtre d'engagement pur.*

### 3. Les deux échelles de $N$ : la tension centrale du travail

**Le fil.** « L'augmentation de la taille $N$ agit comme une pompe à entropie. »
Et, quelques pages plus loin, le terme de diffusion de l'équation de
Fokker-Planck : $B(x) = k_B T (1-x^2) / N$.

**Le problème.** Ces deux affirmations disent le contraire l'une de l'autre, et
c'est la première chose qu'un relecteur de physique statistique relèvera. Le
facteur $1/N$ signifie que **plus la population est grande, moins sa variable
macroscopique est bruitée** : c'est la loi des grands nombres. Une grande
population n'est pas plus désordonnée, elle est plus prévisible.

**Retenu.** Les deux énoncés sont vrais, mais ne portent pas sur le même objet.

* L'entropie de **configuration totale** est extensive : elle croît comme $N$. Il y
  a effectivement exponentiellement plus de façons pour un million de personnes
  d'être en désaccord que pour dix.
* Les fluctuations de la **moyenne** $x$ décroissent en $1/N$. La grandeur
  observable — le taux d'adhésion à une idée — devient de plus en plus stable.

La thèse défendable n'est donc pas « une grande population devient bruyante » mais :

> **Une grande population devient rigide.** Sa taille ne l'agite pas, elle la
> prive de plasticité stochastique. Et c'est précisément cette rigidité qui rend le
> consensus organique inatteignable et la polarisation irréversible : un système
> sans bruit ne peut plus quitter le puits de potentiel où il est tombé.

Cette reformulation est plus forte que l'originale, pas plus faible : elle explique
l'irréversibilité, ce que la version « pompe à entropie » ne faisait pas.

*Mesuré dans `notebooks/04_fokker_planck_paysage.ipynb` — la densité de modérés
s'effondre exponentiellement avec $N$. Vérifié par
`tests/test_fokker_planck.py::TestDriftAndDiffusion::test_diffusion_decreases_with_population`.*

### 4. La dérive $A(x) = Jx + H$ ne peut produire aucune transition de phase

**Le fil.** Le potentiel social est posé comme $V(x) = -\frac{J}{2}x^2 - Hx$, d'où
la dérive $A(x) = -\partial_x V = Jx + H$ et la distribution stationnaire
$P_{\text{stat}}(x) \propto \exp\!\left(\frac{2N}{k_BT}\left(\frac{J}{2}x^2 + Hx\right)\right)$.

**Le problème.** Cette exponentielle est **convexe** : elle est maximale aux
extrêmes $x = \pm 1$ pour toute température. Le modèle prédit donc une société
éternellement polarisée, y compris à température infinie — l'inverse du
« scénario A » que le fil décrit deux paragraphes plus loin. Aucune transition de
phase n'existe dans cette formulation. De plus, $A(x) = Jx + H$ est non bornée :
rien n'y retient l'opinion dans $[-1, 1]$.

**Retenu.** Le terme manquant est l'**entropie de mélange** — le nombre de
configurations individuelles compatibles avec une opinion moyenne $x$. En
l'ajoutant, on obtient exactement l'énergie libre de Helmholtz que le fil invoquait
sans jamais l'écrire :

$$f(x) = \underbrace{-\frac{J}{2}x^2 - Hx}_{E} \; + \; T \underbrace{\left[\frac{1+x}{2}\ln\frac{1+x}{2} + \frac{1-x}{2}\ln\frac{1-x}{2}\right]}_{-S}$$

d'où :

$$A(x) = -f'(x) = Jx + H - T\,\mathrm{artanh}(x)$$

Le rappel entropique $-T\,\mathrm{artanh}(x)$ diverge aux opinions unanimes, ce qui
borne la dynamique, et fait apparaître une **vraie température critique** de champ
moyen $T_c = J$. La formulation du fil en est la linéarisation au voisinage de
$x = 0$ : elle n'était pas fausse, elle était incomplète — et incomplète
précisément là où se joue le phénomène qu'elle prétendait décrire.

*Implémenté dans `ide.fokker_planck.mean_field_free_energy` et `drift_term`.
Vérifié par `tests/test_fokker_planck.py::TestFreeEnergy`.*

### 5. Les probabilités de transition biaisées du Voter Model deviennent négatives

**Le fil.**
$P(x \to x + \tfrac{1}{N}) = x(1-x) + h(1-x)$ et
$P(x \to x - \tfrac{1}{N}) = x(1-x) - hx$.

**Le problème.** La seconde s'écrit $x(1 - x - h)$ : elle est **négative** dès que
$h > 1-x$. Ce n'est plus une probabilité.

**Retenu.** Les deux canaux d'influence sont **mélangés** au lieu d'être
additionnés — avec la probabilité $h$, l'individu écoute la source médiatique
plutôt que son voisin :

$$P(x \to x + \tfrac{1}{N}) = (1-h)\,x(1-x) + h\,(1-x) \qquad
  P(x \to x - \tfrac{1}{N}) = (1-h)\,x(1-x)$$

Cette forme reste positive sur tout $h \in [0,1]$, se réduit exactement au Voter
Model classique en $h = 0$, et conserve la dérive asymétrique qui faisait l'intérêt
de la formulation initiale.

*Vérifié par
`tests/test_voter.py::TestDisinformationBias::test_maximal_bias_never_produces_negative_probabilities`,
qui exécute le modèle à $h = 1$.*

### 6. Le signe du rappel dans l'équation de résonance

**Le fil.**
$\ddot{V} + (\lambda - \gamma\alpha)\dot{V} - \omega_0^2 V = \xi(t)$.

**Le problème.** Le signe négatif du terme de rappel fait du point d'équilibre un
**col instable quels que soient les autres paramètres**. Le système divergerait
même à gain algorithmique nul, et le critère $\gamma\alpha > \lambda$ — qui est le
résultat le plus intéressant de tout le fil — perdrait tout contenu.

**Retenu.** $\ddot{V} + (\lambda - \gamma\alpha\,\sigma(V))\dot{V} + \omega_0^2 V = \xi(t)$.
Avec le signe correct, l'instabilité provient bien de l'amortissement effectif
négatif, et le critère devient significatif.

### 7. Une résonance non bornée ne décrit rien d'observable

**Le fil.** « La visibilité $V(t)$ n'oscille plus, elle explose de manière
exponentielle : $V(t) \propto e^{(\gamma\alpha - \lambda)t}$. »

**Le problème.** Mathématiquement exact, physiquement vide : l'attention
disponible est finie. Un modèle qui prédit une visibilité infinie ne permet ni de
comparer deux configurations, ni de calibrer un seuil.

**Retenu.** Un facteur de saturation
$\sigma(V) = 1/\big(1 + (V/V_{\text{sat}})^2\big)$ éteint progressivement
l'amplification à mesure que la visibilité approche la capacité d'attention. Le
système ne diverge plus : il s'installe dans un **cycle limite** de type Van der
Pol — une oscillation médiatique auto-entretenue d'amplitude finie.

C'est un gain de réalisme, pas un artifice de convergence : ce que l'on observe
d'une fausse information installée n'est pas une explosion, c'est un **sujet qui
revient périodiquement**.

*Illustré dans `notebooks/06_resonance_larsen.ipynb`, où les deux régimes sont
tracés côte à côte.*

---

## C. Requalifications conceptuelles

### 8. La décohérence n'augmente pas l'entropie du système global

**Le fil.** « L'entropie de von Neumann a bondi de $0$ à une valeur positive. »

**Le problème.** L'évolution d'un système quantique **fermé** est unitaire, donc
l'entropie de von Neumann du tout est rigoureusement constante. Ce qui croît, c'est
l'entropie du **sous-système réduit** — obtenue en traçant sur les degrés de liberté
de l'environnement. L'information n'est pas détruite, elle est délocalisée dans les
corrélations système-environnement. Un physicien écarte l'analogie en une phrase si
ce point n'est pas posé.

**Retenu.** La formulation précise, et une précision associée qui renforce
l'analogie plutôt qu'elle ne l'affaiblit : **une superposition cohérente est un état
pur, d'entropie nulle**. Ce n'est donc pas la multiplicité des possibilités qui
produit du désordre, c'est la perte de cohérence entre elles.

Le pendant social est plus juste ainsi : une population où chacun garde plusieurs
opinions ouvertes n'est pas désordonnée. Le désordre naît du contact avec un
environnement qui fixe les positions.

*Vérifié par `tests/test_entropy.py::TestVonNeumannEntropy::test_superposition_is_still_pure`.*

### 9. « Effet tunnel social » : requalifié en métaphore

**Le fil.** Le basculement direct d'un extrême à l'autre sans passer par la
modération est attribué à un « effet tunnel social ».

**Le problème.** L'effet tunnel est un phénomène strictement quantique, sans
équivalent dans un système classique bruité. Le mécanisme correct porte un nom et
une théorie : le **franchissement de barrière par activation thermique**, décrit par
la formule de Kramers, dont le taux est $\propto e^{-\Delta V / k_B T}$.

**Retenu.** Kramers comme mécanisme, l'effet tunnel comme image explicitement
signalée. La différence n'est pas cosmétique : la loi de Kramers est *testable* et
donne une dépendance en température que le tunnel ne donne pas. On perd une image
séduisante, on gagne une prédiction.

### 10. $1/k^N$ décrit un état initial, pas une dynamique

**Le fil.** « La probabilité d'obtenir une unanimité spontanée s'effondre en
$1/k^N$. »

**Le problème.** Ce calcul suppose $N$ individus tirant leur opinion
**indépendamment** parmi $k$ options. C'est la probabilité d'une unanimité par
hasard à l'instant initial — or tout l'intérêt du sujet est que les individus
**interagissent**, et que c'est cette interaction qui produit (ou non) le consensus.
Le chiffre est juste et hors sujet.

**Retenu.** L'énoncé est conservé comme description de l'état initial, et la
question dynamique est traitée là où elle a un sens : le **temps de consensus** du
Voter Model, qui croît en $N$ (réseau globalisé) ou $N^2$ (voisinage local).

### 11. $\tau_D \propto \tau_R / N$ est une heuristique, pas un résultat

**Le fil.** Le temps de décohérence est donné comme inversement proportionnel au
nombre de particules de l'environnement.

**Le problème.** Le résultat de Zurek fait intervenir la séparation spatiale des
composantes de la superposition et la longueur d'onde thermique de de Broglie, pas
un $1/N$ littéral. Présenté comme une loi, l'énoncé est faux ; présenté comme un
ordre de grandeur, il est utile.

**Retenu.** L'expression est conservée, explicitement étiquetée comme **loi
d'échelle heuristique**, avec la référence au calcul exact.

---

## D. Arguments à reformuler

### 12. La connectivité globale accélère le consensus, elle ne l'empêche pas

**Le fil.** « Le réseau social passe d'un réseau classique à un réseau *small-world*
à couplage infini […] rendant tout consensus macroscopique strictement impossible. »

**Le problème.** C'est mesurablement faux. Le temps de consensus du Voter Model
croît comme $N^2$ sur un anneau, $N \ln N$ en dimension 2, et $N$ seulement en champ
moyen. Un réseau densément connecté converge donc **plus vite** qu'un voisinage
géographique. Le fil cite d'ailleurs ces lois correctement une page plus tôt, avant
d'en tirer la conclusion inverse.

**Retenu.** La connectivité n'est pas la cause de la fragmentation. Elle amplifie et
accélère — dans la direction que le champ lui donne. Les vraies causes sont :

1. le **biais directionnel** $h$ des micro-champs algorithmiques $H_i(t)$ ;
2. l'**homophilie** — le fait que les liens créés relient des individus déjà
   semblables, ce qui compartimente le réseau en sous-graphes internes.

La conséquence est importante pour le mémorandum : **le levier utile porte sur le
champ, pas sur le nombre de liens.** Brider la portée des partages reste défendable
comme mesure d'urgence, mais ce n'est pas la connectivité en soi qu'il faut viser.

*Mesuré dans `notebooks/03_voter_consensus_et_taille.ipynb`. Vérifié par
`tests/test_voter.py::TestConsensusScaling::test_global_connectivity_accelerates_consensus`.*

### 13. Deux températures critiques, deux significations

**Observation.** Le dépôt manipule deux valeurs critiques différentes, et il faut
dire laquelle sert à quoi :

| Modèle | $T_c$ | Signification |
|---|---|---|
| Ising 2D (Onsager, exact) | $2/\ln(1+\sqrt{2}) \approx 2{,}269\,J$ | voisinage géographique, 4 voisins |
| Champ moyen (Curie-Weiss) | $J$ | chacun subit l'opinion moyenne de tous |

L'écart n'est pas une erreur : le champ moyen surestime la cohésion, donc
sous-estime la température nécessaire pour la briser. La comparaison a un sens
sociologique — un réseau social globalisé est **plus proche du champ moyen** qu'un
voisinage réel, ce qui signifie qu'il est plus fragile à la polarisation, pas moins.

La valeur d'Onsager sert de **test de validation** du code : c'est le seul point du
dépôt où une prédiction théorique exacte, indépendante de nos hypothèses
sociologiques, peut confirmer que l'implémentation est correcte.

*Mesuré dans `notebooks/02_ising_temperature_sociale.ipynb`.*

---

## E. Le prototype logiciel

### 14. Cinq défauts du code du fil

Le prototype `pygame` est conservé tel quel dans
[`legacy/simulation_thread_2026-08.py`](https://github.com/s-geffroy/Index-Dissipation-Entropique/blob/main/legacy/simulation_thread_2026-08.py),
et réimplémenté proprement dans `ide.abm`.

1. **Aucune température sociale.** C'est le défaut le plus lourd, et il est
   silencieux : sans agitation individuelle, le conformisme est une force purement
   contractante. La population s'effondre sur un point unique, l'IDE tombe à zéro
   quels que soient les autres réglages, et le modèle ne peut représenter **ni** le
   débat fluide **ni** l'effet du bruit thermique que la note propose précisément
   d'injecter. Le paramètre central de toute la théorie était absent de sa seule
   implémentation.
2. **Contamination par téléportation.** `infecter()` écrivait
   `self.opinion.x = 1.0 if self.opinion.x > 0 else -1.0` : l'individu était
   instantanément placé dans un coin du compas. Toute dynamique ultérieure
   disparaissait, et la « polarisation » mesurée n'était plus qu'un décompte de
   contaminations. Remplacé par une radicalisation progressive.
3. **Vérification infaillible.** Tout individu contaminé passant à portée d'un
   fact-checker était soigné avec certitude — hypothèse que la littérature sur
   l'hystérésis des croyances, invoquée ailleurs dans le même fil, contredit
   directement. L'efficacité est devenue probabiliste et paramétrable.
4. **Bords absorbants.** Le rabattement des opinions par troncature accumulait les
   individus agités sur les bords du compas, où ils restaient piégés. L'IDE mesuré
   chutait à haute température pour une raison purement numérique. Les bords sont
   désormais réfléchissants.
5. **Indentation perdue.** Dans le fil imprimé, le corps de `main()` et le garde
   `if __name__ == "__main__"` ont perdu leur indentation : le script ne s'exécute
   pas en l'état.

---

## F. Correction issue de la mesure

Ce point n'a pas été trouvé par relecture du fil mais par **confrontation aux données**. Il
est ajouté après coup, ce qui est la façon normale dont un audit doit vivre.

### 15. Le critère $\gamma\alpha > \lambda$ n'est pas un test, c'est une définition

**Le fil, et le mémorandum qui en découlait.** « Interdire les configurations algorithmiques
où le taux d'amplification d'un contenu dépasse son taux d'amortissement naturel :
$\gamma\alpha > \lambda$. »

**Le problème, révélé par la [calibration](calibration.md).** Le rapport
$\gamma\alpha/\lambda$ dépasse 1 dans les 19 épisodes d'attention mesurés, sous les quatre
estimateurs testés. Ce n'est pas une propriété inquiétante de l'écosystème : c'est une
**tautologie de la procédure d'estimation**. Un épisode d'attention observable a
nécessairement connu une phase de croissance, donc $r_{\text{up}} > 0$, donc
$\gamma\alpha > \lambda$.

Autrement dit, la recommandation demandait à un régulateur de vérifier une condition qui est
vraie de tout contenu ayant percé. Elle était **inapplicable**, et rien dans le raisonnement
théorique ne le signalait.

**Retenu.** Un **plafond sur le rapport**, $\gamma\alpha/\lambda \leq \rho_{\max}$. La
grandeur réglementaire est la marge au-dessus du seuil, pas son franchissement. La mesure
fournit une référence descriptive — médiane de 2,5 à 4,2 selon l'estimateur — dont un
$\rho_{\max}$ normatif peut se discuter.

**Ce que cet épisode enseigne sur la méthode.** Une erreur de ce type ne se voit pas par
relecture : elle ne devient visible qu'en essayant de mesurer. C'est l'argument le plus
concret en faveur de la calibration empirique — non pour confirmer le modèle, mais pour
découvrir où ses recommandations ne veulent rien dire.

---

## Ce que le modèle ne peut pas faire

Ces limites ne sont pas des corrections en attente. Ce sont les frontières du
travail, et elles doivent être énoncées par ses auteurs plutôt que par ses
relecteurs.

### Une analogie n'est pas une explication

Rien dans ce dépôt ne démontre que les opinions humaines *obéissent* à une
mécanique statistique. Le travail établit qu'un formalisme emprunté à la physique
**reproduit** certains comportements observés — transition brusque, persistance
après démenti, amplification sélective. C'est une hypothèse structurelle, féconde
parce qu'elle produit des quantités mesurables. Ce n'est pas une loi de la nature
sociale.

Un seul de ses paramètres est aujourd'hui calibré sur données réelles : le rapport
$\gamma\alpha/\lambda$ ([calibration](calibration.md)). Et cette calibration, loin de
conforter le modèle, a montré qu'une de ses recommandations réglementaires ne voulait rien
dire (point 15) et que l'un de ses mécanismes n'était pas étayé par les données. **$J$, $T$,
$\gamma$ et $\alpha$ pris séparément restent sans procédure d'estimation** : le formalisme
est cohérent, son ancrage empirique n'est qu'entamé. C'est toujours la principale faiblesse
du travail.

### Les individus ne sont pas des spins

* **Intentionnalité.** Un individu peut adopter une posture anticonformiste, ironique
  ou stratégique. Un spin n'a pas d'intention, et un modèle de spins ne peut pas
  représenter quelqu'un qui feint d'être d'accord.
* **Multidimensionnalité.** Le modèle à agents utilise deux axes continus plutôt
  qu'un spin binaire, ce qui atténue le problème sans le résoudre : une opinion
  réelle n'est pas un point dans un espace de faible dimension.
* **Réseaux dynamiques.** Les individus coupent des liens, changent de plateforme,
  se réorganisent. La topologie est ici fixée, sauf par le seuil de bulle.
* **L'environnement n'est pas passif.** Un bain thermique ne poursuit pas d'objectif.
  Un algorithme de recommandation, si — il optimise une fonction de coût, ce qui
  fait de lui un acteur stratégique et non un environnement. C'est le point où
  l'analogie physique est la plus fragile, et c'est aussi ce qui rend l'ADE
  concevable : on peut changer une fonction de coût, pas une loi physique.

### Les limites propres à l'IDE comme instrument réglementaire

Ces réserves comptent au moins autant que les corrections mathématiques, parce
qu'elles portent sur ce que le mémorandum demande à un législateur.

* **La discrétisation en points de vue est un choix politique.** L'IDE mesure
  l'entropie d'une distribution de modalités. Qui définit les modalités définit
  l'index. Découper l'espace des opinions en 4, en 40 ou en 400 catégories change la
  valeur mesurée, et le découpage n'est pas un acte technique neutre.
* **L'index est manipulable.** Une plateforme qui doit maintenir un IDE au-dessus
  d'un seuil peut y parvenir en servant des contenus formellement divergents mais
  substantiellement vides — de la diversité d'étiquette sans diversité d'argument.
  Toute métrique imposée devient une cible ; celle-ci n'y échappe pas, et le
  mémorandum doit être lu comme une proposition à durcir, pas comme un dispositif
  prêt à l'emploi.
* **Un seuil sur l'IDE est une contrainte sur ce que les gens voient.** Elle est
  défendable — mais c'est une contrainte, et la présenter comme une simple mesure
  technique serait malhonnête. Le fil emploie la formule « la régulation cesse
  d'être une censure arbitraire pour devenir une ingénierie de la stabilité ». La
  formule est belle et il faut s'en méfier : une ingénierie de la stabilité *est*
  une intervention sur le débat public. Elle doit être justifiée comme telle, avec
  les garde-fous démocratiques correspondants, et non naturalisée par un vocabulaire
  de thermodynamique.
* **Vie privée.** Mesurer l'IDE d'un fil individuel suppose d'observer ce qui est
  servi à des individus. Un protocole d'audit crédible doit être agrégatif et
  différentiellement privé — ce dépôt ne le propose pas.

### Ce que les simulations ne montrent pas

Les notebooks explorent des régimes de paramètres choisis pour être lisibles. Aucune
étude systématique de sensibilité n'a été menée, les tailles de systèmes sont
modestes (réseaux de 24×24, populations de quelques centaines), et aucun résultat
n'est comparé à un jeu de données réel. Les conclusions sont **qualitatives** :
elles portent sur l'existence de régimes et le sens des dépendances, jamais sur des
valeurs numériques transposables.
