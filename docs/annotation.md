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

!!! info "À venir"
    Cette section sera complétée après l'annotation. La grille ci-dessus ne sera pas
    modifiée : si elle devait l'être, la version de grille serait incrémentée et l'annotation
    reprise.

---

*Implémentation : `ide.annotation` · Script : `scripts/fetch_extracts.py` ·
[corpus étendu](corpus-etendu.md) · [feuille de route](feuille-de-route.md)*
