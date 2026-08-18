# Annotation en aveugle : le protocole

!!! note "Pré-enregistrement"
    Cette page décrit la grille d'annotation **avant** que la moindre annotation ait été
    produite. Elle est publiée dans un commit antérieur au fichier `data/annotations.json`,
    et l'historique du dépôt en atteste. Les résultats viendront s'ajouter en fin de page,
    sans que rien de ce qui précède soit récrit.

## La question laissée ouverte

Le [corpus étendu](corpus-etendu.md) a mesuré un résultat nul — la persistance ne diffère pas
entre registres émotionnels, ×3,04 contre ×2,90, $p = 0{,}53$ — mais il a aussi exposé le
défaut de son propre protocole. L'appartenance à une catégorie de Wikipédia est un
**indicateur bruité** du registre : « Lil Tay » figure dans une catégorie de canulars à cause
d'un canular sur sa mort, alors que l'attention portée à cet article est celle d'une
célébrité.

Or un bruit d'étiquetage n'introduit pas de biais directionnel : il **attire tout écart vers
zéro**. Le résultat nul est donc compatible avec deux lectures que les données ne séparent
pas :

1. il n'existe pas d'écart de persistance entre registres ;
2. il en existe un, dilué par l'étiquetage approximatif.

Une annotation manuelle du registre, sujet par sujet, tranche entre les deux — et c'est la
seule chose qui le fasse. Si l'écart réapparaît sur les sujets correctement étiquetés, la
dilution était l'explication ; s'il reste absent, l'absence d'effet l'était.

## Ce qui est annoté

Les **440 sujets** du manifeste `data/catalogue.json`, sans exception. Annoter un
sous-ensemble choisi rouvrirait précisément le biais de sélection que le corpus dérivé de
catégories avait fermé.

L'annotation ne modifie pas le corpus : elle lui ajoute une colonne. Le pool reste celui que
les catégories ont produit.

## La question posée à chaque sujet

> **Qu'est-ce qui mobiliserait l'attention du public sur cet article ?**

Non pas de quoi l'article parle, mais quelle émotion porterait sa consultation.

| Registre | Définition | Rôle dans le modèle |
|---|---|---|
| `accusation` | une **faute, une menace ou une tromperie attribuée à quelqu'un** : scandale, complot, corruption, atrocité, manipulation | charge émotionnelle $\alpha$ élevée |
| `discovery` | une **découverte, une exploration ou une réussite** : résultat scientifique, mission spatiale, distinction | $\alpha$ faible |
| `neither` | **ni l'un ni l'autre** : divertissement, célébrité, institution ordinaire, entrée de catalogue, concept technique | hors comparaison |

C'est la troisième étiquette qui fait le travail. Elle retire du corpus les sujets qu'une
catégorie a capturés pour des raisons thématiques, sans que leur audience relève du registre —
et le taux auquel elle est employée **mesure directement** le bruit d'étiquetage que le corpus
étendu n'avait pu que diagnostiquer.

### Cinq règles de départage

Arrêtées avant lecture, pour que les cas limites ne se décident pas au cas par cas :

1. **Une œuvre de fiction portant sur un scandale est `neither`.** Son public est un public
   de fiction. Cela vaut pour les romans, films, séries et jeux vidéo, quel que soit leur
   sujet.
2. **Une personne est codée par ce qui la rend notable** selon son chapeau : un lauréat de
   prix scientifique est `discovery`, une personnalité mise en cause est `accusation`, une
   célébrité est `neither`.
3. **Une atrocité, un massacre ou un attentat est `accusation`.** Le registre est celui de la
   faute et de la menace, indépendamment de l'existence d'une accusation formelle.
4. **Un objet de catalogue ou un instrument sans annonce** reste `discovery` si sa notabilité
   tient à ce qu'il a permis d'observer, et devient `neither` s'il n'est qu'une entrée
   technique parmi des milliers.
5. **Un concept abstrait nommant la faute elle-même** — « désinformation », « corruption
   politique » — est `accusation`. La règle 1 ne s'y applique pas : ce n'est pas une œuvre.

### Deux dimensions accessoires

* le **type** de sujet — événement, personne, organisation, œuvre, concept, objet. Il permet
  de vérifier après coup que la comparaison n'oppose pas des événements à des concepts, le
  confondant que le choix des catégories cherchait à éviter sans pouvoir le mesurer ;
* la **confiance**, binaire. Les sujets incertains ne sont pas écartés — écarter au vu du
  résultat serait exactement ce que le pré-enregistrement interdit — mais ils permettent un
  contrôle de sensibilité, et chacun porte une justification écrite.

## La cécité, et ce qu'elle vaut

L'annotation ne doit rien devoir au résultat qu'elle sert à mesurer. Trois dispositions y
concourent, et il faut dire ce que chacune garantit.

| Disposition | Ce qu'elle garantit |
|---|---|
| la grille est écrite **avant** les données | vérifiable par un tiers dans l'historique git |
| l'entrée de l'annotateur est **figée et empreintée** | `data/extracts.json`, dont le SHA-256 est inscrit dans le fichier d'annotations : on sait ce qui a été lu |
| les **séries de consultations ne sont pas chargées** pendant l'annotation | propriété du processus, non garantie cryptographique — cela se déclare, cela ne se prouve pas |

Le matériau est le **chapeau** de l'article — sa première section, en texte brut, tronquée à
600 caractères. C'est ce qu'un lecteur voit avant de décider s'il lit la suite, donc la bonne
granularité pour coder ce qui mobiliserait son attention.

### Ce que la cécité ne couvre pas

**Une contamination résiduelle, nommée.** Six sujets ont été cités avec leur élévation dans la
page du corpus étendu — Lil Tay, Watch Dogs, Million Dollar Extreme, The Capture, Mossack
Fonseca, Illuminati (game). L'annotateur les connaît. Ils sont listés dans
`ide.annotation.CONTAMINATED`, ils sont annotés comme les autres, et l'analyse est reprise
sans eux en contrôle de sensibilité.

**Un annotateur unique.** Il n'y a pas d'accord inter-juges, donc pas de mesure de la
fiabilité du codage. Ce travail corrige le bruit d'étiquetage ; il n'établit pas que la grille
serait appliquée à l'identique par quelqu'un d'autre. C'est la limite principale du
dispositif, et la grille écrite ci-dessus est ce qui la rend au moins réplicable.

!!! success "Levé en partie — voir [Réplication](#replication-deux-codeurs-independants)"
    Le corpus a depuis été recodé deux fois, en aveugle, sous la grille identique :
    $\kappa$ de Fleiss de **0,921**. La grille est donc reproductible. Ce qui subsiste — que
    trois instances d'un même modèle ne valent pas trois juges humains — est repris plus bas.

**La connaissance du résultat agrégé.** L'annotateur sait que la mesure précédente était
nulle. Aucune disposition ne neutralise cela ; la direction du biais qui en résulterait n'est
pas déterminée.

## Ce qui sera mesuré

Dans cet ordre, arrêté d'avance :

1. **la matrice de confusion** catégorie × registre annoté — le taux de bruit d'étiquetage,
   qui est un résultat en soi ;
2. **la persistance** — élévation médiane des changements de régime détectés, comparée entre
   registres annotés, par un test de Mann-Whitney. C'est le test principal ;
3. **le taux de basculement**, avec le même contrôle du trafic que sur le corpus étendu :
   stratification et appariement ;
4. **trois contrôles de sensibilité** : sans les sujets contaminés, sans les annotations
   incertaines, et à type de sujet contrôlé.

Aucun sujet ne sera retiré au vu de son résultat. Les sujets sans changement détecté seront
rapportés comme tels.

---

## Résultats

!!! success "La question est tranchée : l'écart n'était pas dilué, il n'existe pas"
    L'écart de taux de basculement **disparaît complètement** une fois l'étiquette corrigée :
    8,6 % contre 2,7 % ($p = 0{,}012$) devient **4,8 % contre 5,1 %**, rapport de cotes 0,93,
    $p = 1{,}00$. La persistance reste nulle — ×3,04 contre ×2,90, $p = 0{,}90$ — et le test
    conserve la puissance de détecter un écart de l'ampleur annoncée par le corpus pilote.

!!! warning "Le bruit d'étiquetage était massif"
    **Deux sujets sur cinq** ne relèvent d'aucun des deux registres, et l'accord entre
    catégorie et annotation n'atteint que **59,5 %**. La conjecture du corpus étendu est
    vérifiée, et son ampleur dépasse ce qu'il supposait.

!!! danger "Et l'annotation expose un défaut de conception"
    Correctement étiquetés, les deux registres **ne portent presque pas sur les mêmes types de
    sujets** : concepts et événements d'un côté, objets et personnes de l'autre. Une
    comparaison bâtie sur des catégories thématiques compare donc aussi des natures d'objets.

### 1. Le bruit d'étiquetage, mesuré

| Catégorie | n | annoté accusation | annoté découverte | annoté ni l'un ni l'autre |
|---|---|---|---|---|
| accusation | 220 | **147** (66,8 %) | 3 (1,4 %) | **70** (31,8 %) |
| découverte | 220 | 0 (0,0 %) | **115** (52,3 %) | **105** (47,7 %) |

Accord global : **262/440 = 59,5 %**. Registre franchement inversé : **3 sujets**.

Le bruit est **asymétrique**, pour une raison de construction : le registre « découverte »
tirait ses effectifs de catalogues d'objets célestes, dont l'immense majorité sont des entrées
techniques sans public. Le filtre de substance de dix mille octets n'y suffisait pas.

Mais le registre franchement inversé est **quasi nul**. La catégorie se trompe en capturant des
sujets hors registre, presque jamais en attribuant le mauvais registre — c'est exactement le
profil d'un bruit qui dilue sans biaiser, tel que le corpus étendu l'avait supposé.

### 2. L'écart de taux de basculement s'évanouit

![Annotation en aveugle : le bruit d'étiquetage portait l'écart](figures/fig12_annotation.png)

/// caption
Le bruit d'étiquetage ; la disparition de l'écart de taux avec l'étiquette corrigée ; la
persistance par registre annoté ; et le défaut de conception que l'annotation révèle. Figure
régénérée par [le notebook 12](notebooks/12_annotation_en_aveugle.ipynb).
///

| Étiquette | accusation | découverte | rapport de cotes | p |
|---|---|---|---|---|
| catégorie | 19/220 = 8,6 % | 6/220 = 2,7 % | 3,37 | **0,012** |
| **annotation** | 7/147 = 4,8 % | 6/118 = 5,1 % | **0,93** | **1,000** |
| *(ni l'un ni l'autre)* | *12/175 = 6,9 %* | | | |

Le rapport de cotes ne s'atténue pas : il **disparaît**, et change même très légèrement de sens.

Le détail le plus parlant est la dernière ligne. Les sujets écartés basculent à **6,9 %**,
c'est-à-dire **plus souvent que les deux registres**. Ce n'étaient pas des observations
inertes : ce sont elles qui portaient l'écart attribué au registre d'accusation. Sur les cinq
plus fortes élévations du corpus, **quatre** sont codées « ni l'un ni l'autre » — Lil Tay,
Watch Dogs, Million Dollar Extreme, The Capture. Ce sont exactement les cas que le corpus
étendu avait cités comme suspects.

**Le déséquilibre d'audience était lui-même un effet de l'étiquetage.** Le trafic médian passe
de 39 contre 11 vues/jour ($p = 5\times10^{-14}$) à 36 contre 26,5 ($p = 2{,}6\times10^{-3}$) :
les entrées de catalogue sans public gonflaient le registre « découverte ». Les deux contrôles
du corpus étendu confirment l'absence d'écart — strate ≥ 47 vues/jour, RC = 0,45 ($p = 0{,}32$)
; 116 paires appariées sur le trafic, McNemar $p = 1{,}00$.

### 3. La persistance reste nulle — et le test pouvait conclure

| Corpus | accusation | découverte | p |
|---|---|---|---|
| pilote, 24 sujets choisis à la main | ×9,20 (n = 8) | ×2,90 (n = 6) | 0,081 |
| étendu, étiquette de catégorie | ×3,04 (n = 21) | ×2,90 (n = 7) | 0,533 |
| **étendu, registre annoté** | **×3,04** (n = 7) | **×2,90** (n = 7) | **0,902** |
| *sans les sujets contaminés* | *×2,87* (n = 6) | *×2,90* (n = 7) | *0,945* |
| *sans les annotations incertaines* | *×3,06* (n = 6) | *×2,90* (n = 5) | *0,931* |
| *strate de trafic comparable* | *×2,69* (n = 5) | *×2,90* (n = 7) | *0,876* |

Quatorze observations, sept de chaque côté. Il faut le dire avant qu'on ne l'objecte — mais un
test de Mann-Whitney à sept contre sept n'est pas aveugle :

| Rangs de chevauchement | p |
|---|---|
| 0 — séparation complète | 0,0006 |
| 2 | 0,0048 |
| **4** | **0,040** |
| 5 | 0,140 |

Le corpus pilote annonçait des intervalles interquartiles [4,0 ; 14,9] contre [2,7 ; 3,2],
c'est-à-dire presque disjoints. **Un écart de cette ampleur aurait été détecté ici.** Le
résultat nul n'est donc pas un simple manque de puissance.

> **La question laissée ouverte par le corpus étendu est tranchée : l'écart n'était pas dilué
> par l'étiquetage, il n'existe pas.**

### 4. Ce que l'annotation révèle du plan d'expérience

C'est la découverte que ni le pilote ni le corpus étendu ne pouvaient faire, faute d'étiquette
fiable.

| Type de sujet | accusation | découverte | ni l'un ni l'autre |
|---|---|---|---|
| événement | **58** | 6 | 1 |
| concept | **63** | 15 | 21 |
| personne | 13 | **39** | 12 |
| objet | 0 | **58** | 109 |
| organisation | 11 | 0 | 13 |
| œuvre | 2 | 0 | 19 |

Le registre d'accusation est fait de **concepts et d'événements** ; celui de découverte,
d'**objets et de personnes**. Un seul type se trouve des deux côtés en nombre suffisant — les
personnes, 23,1 % contre 7,7 %, $p = 0{,}16$ — et il n'y donne rien de concluant. Les concepts,
eux, ne basculent **jamais** : 0 sur 63 et 0 sur 15.

La conséquence dépasse ce corpus. **Une comparaison entre registres bâtie sur des catégories
thématiques compare aussi, et peut-être surtout, des natures d'objets.** Un concept
encyclopédique — « Corruption au Mexique » — n'a pas la dynamique d'attention d'un événement
daté, indépendamment de toute charge émotionnelle. Le corpus étendu avait nommé ce confondant
sans pouvoir le mesurer ; il est ici mesuré, et il est sévère.

C'est une limite du **plan d'expérience**, non du résultat : elle ne ressuscite pas l'écart,
elle indique ce qu'un quatrième protocole devrait contrôler.

### 5. Une note sur l'identification

Un ajustement sur vingt-huit passe cette fois tous les contrôles, y compris celui
d'observabilité ajouté après le corpus étendu. Il porte sur **« Watch Dogs (jeu vidéo) »** —
un sujet codé « ni l'un ni l'autre ». L'identification des paramètres reste donc, en pratique,
hors de portée sur ce type de données.

## Réplication : deux codeurs indépendants

!!! success "La grille est reproductible — κ de Fleiss = 0,921"
    Le corpus a été recodé par deux lecteurs indépendants du contexte, sous la grille
    identique, à partir du même matériau présenté dans un ordre différent et **sans
    l'étiquette de catégorie**. Accords deux à deux : **0,903 · 0,917 · 0,944**. Unanimité sur
    **92,3 %** des sujets. Sur l'échelle de Landis et Koch, $\kappa > 0{,}80$ se lit « accord
    presque parfait ».

![Réplication : accords, structure du désaccord, robustesse du résultat](figures/fig12b_replication.png)

/// caption
Les accords corrigés du hasard ; la nature des trente-quatre désaccords ; et le résultat sous
les trois étiquetages. Figure régénérée par
[le notebook 12](notebooks/12_annotation_en_aveugle.ipynb).
///

### Les marges, puis les sujets

| Codeur | accusation | découverte | ni l'un ni l'autre |
|---|---|---|---|
| C1 — initial | 147 | 118 | 175 |
| C2-A | 140 | 114 | 186 |
| C2-B | 141 | 109 | 190 |

Les distributions marginales sont déjà voisines, mais cela ne suffit pas : deux codeurs peuvent
produire les mêmes effectifs sur des sujets différents. C'est l'accord corrigé du hasard qui
tranche, et il importe ici — sur un corpus dont 40 % relèvent d'une seule étiquette, l'accord
brut serait flatteur.

| Paire | accord brut | $\kappa$ de Cohen |
|---|---|---|
| C1 vs C2-A | 93,6 % | **0,903** |
| C1 vs C2-B | 94,5 % | **0,917** |
| C2-A vs C2-B | 96,4 % | **0,944** |
| les trois (Fleiss) | — | **0,921** |

### Le désaccord tombe au bon endroit

Trente-quatre sujets ne font pas l'unanimité. Leur répartition est le résultat structurel de
cette section :

| Nature du désaccord | sujets |
|---|---|
| appartenance à un registre (`accusation` ou `discovery` contre `neither`) | **33** |
| inversion des deux registres comparés | **1** |

**Un seul sujet sur 440** voit un codeur dire « accusation » là où un autre dit « découverte ».
L'ambiguïté résiduelle de la grille fait donc varier les **effectifs** de la comparaison, pas
son **sens** — c'est la forme d'imprécision la moins dommageable qu'on pouvait espérer.

Les cas litigieux sont interprétables : des étoiles dont le chapeau ne dit pas si leur
notabilité tient à une découverte, des dispositifs de physique sans annonce associée, quelques
affaires dont le chapeau ne rapporte pas la mise en cause. La **règle 4** — l'objet de
catalogue — est celle qui laisse le plus de latitude, et c'est là qu'une version 1.1 de la
grille devrait porter.

### Le résultat sous le codage consensuel

| Étiquette | accusation | découverte | rapport de cotes | p |
|---|---|---|---|---|
| catégorie | 8,6 % | 2,7 % | 3,37 | 0,012 |
| annotation C1 | 4,8 % | 5,1 % | 0,93 | 1,000 |
| **consensus des trois** | **4,3 %** | **5,4 %** | **0,78** | **0,769** |

Et la persistance : ×3,06 (n = 6) contre ×2,90 (n = 7), $p = 0{,}836$.

**Les deux résultats sont inchangés.** Le codage initial n'était pas un cas particulier.

!!! danger "Ce que cet accord ne mesure pas"
    Les trois codeurs sont des instances du **même modèle de langue**. L'accord mesure donc la
    reproductibilité de la **grille** — le fait qu'une lecture fraîche des mêmes consignes,
    sans accès au premier codage ni aux résultats, redonne les mêmes étiquettes. Il ne mesure
    **pas** l'accord entre juges humains indépendants, et il le surestime nécessairement, des
    instances d'un même modèle partageant leurs a priori.

    La réserve d'un codage humain multiple subsiste donc entière. Ce qui a changé : on sait
    désormais que les consignes écrites suffisent à produire un codage stable, ce qui rend le
    travail **réplicable** par un tiers plutôt que seulement consultable.

## Ce que cela change pour le projet

**Quatre mesures ont été menées, et aucune ne distingue les registres émotionnels** : le taux
d'amplification ([calibration](calibration.md)), la persistance sur corpus pilote puis étendu
([régimes](regimes.md), [corpus étendu](corpus-etendu.md)), et le taux de basculement. La
dernière hypothèse de sauvetage — la dilution par un étiquetage approximatif — est éliminée.

Le mécanisme de la **charge émotionnelle $\alpha$ reste sans appui empirique**, et ce n'est
plus faute d'avoir cherché. Si ce mécanisme existe, il ne se lit pas dans la dynamique
d'attention agrégée d'une encyclopédie.

Ce qui subsiste est intact et n'a jamais dépendu du registre : la **détection de basculements
datés** fonctionne, les dates et les amplitudes sont robustes, et elles restent l'instrument de
constat proposé au [mémorandum](memorandum.md).

## Pistes ouvertes

1. ~~**Faire annoter le même corpus par un second codeur**, à l'aveugle également, et publier
   le $\kappa$ de Cohen.~~ → **fait**, avec deux codeurs plutôt qu'un : $\kappa$ de Fleiss de
   0,921, et un résultat inchangé sous le codage consensuel. Ce qui reste à faire est un
   codage par des **annotateurs humains** : trois instances d'un même modèle partagent leurs
   a priori, et surestiment donc l'accord.
2. **Apparier sur le type de sujet** autant que sur le trafic, dès la construction du corpus.
   Comparer des événements à des événements et des personnes à des personnes est désormais une
   exigence mesurée, non une précaution théorique.
3. **Abaisser le seuil de détection en agrégeant par semaine.** Vingt-huit basculements sur
   440 sujets laissent le test principal à sept observations par registre ; c'est le facteur
   limitant qui reste.
4. **Chercher l'effet ailleurs que dans la dynamique d'attention agrégée.** Trois quantités ont
   été testées sans résultat ; la quatrième piste ne devrait pas être une quatrième mesure du
   même objet.

---

*Implémentation : `ide.annotation` · Script : `scripts/fetch_extracts.py` ·
[corpus étendu](corpus-etendu.md) · [feuille de route](feuille-de-route.md)*
