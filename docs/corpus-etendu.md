# Corpus étendu : l'écart de persistance ne se réplique pas

!!! failure "Le résultat du corpus pilote était un artefact de sélection"
    L'écart de persistance entre registres émotionnels — **×9,2 contre ×2,9**, $p = 0{,}08$
    sur quatorze sujets choisis à la main — devient **×3,04 contre ×2,90**, $p = 0{,}53$ sur
    440 sujets dérivés de catégories. Le facteur trois a disparu.

!!! warning "Et l'écart de taux de basculement est un effet d'audience"
    Les sujets d'accusation basculent trois fois plus souvent (8,6 % contre 2,7 %,
    $p = 0{,}014$) — mais ils sont aussi **trois fois et demie plus consultés**
    ($p = 5\times10^{-14}$). À trafic comparable, le rapport de cotes tombe de 3,4 à 1,38
    ($p = 0{,}63$).

!!! info "Le nouveau protocole a son propre défaut"
    L'appartenance à une catégorie est un **indicateur bruité** du registre : « Lil Tay »
    figure dans une catégorie de canulars, mais son audience est celle d'une célébrité. Un
    bruit d'étiquetage attire tout écart vers zéro — le résultat nul est donc compatible avec
    l'absence d'effet **comme** avec un effet dilué.

!!! success "Depuis tranché — par l'annotation en aveugle"
    L'ambiguïté que cette page laisse ouverte a été levée en [annotant le registre à la
    main](annotation.md) sur les 440 sujets. Le bruit d'étiquetage est effectivement massif —
    **40 % des sujets ne relèvent d'aucun des deux registres** — et il portait la totalité de
    l'écart de taux de basculement : 8,6 % contre 2,7 % devient **4,8 % contre 5,1 %**
    ($p = 1{,}00$). **L'écart n'était pas dilué, il n'existe pas.**

---

## Pourquoi changer le protocole de sélection, et pas seulement la taille

Le [corpus pilote](regimes.md) comptait vingt-quatre sujets choisis à la main. À cette taille,
le choix se relit et se conteste. À plusieurs centaines, il ne se relit plus — et c'est
précisément là que le biais de sélection devient invisible : rien ne distingue, dans une liste
de trois cents titres, ceux qui auraient été retenus pour ce qu'ils montrent.

Le corpus étendu remplace donc le choix des **sujets** par celui des **catégories**. Dix-sept
catégories de Wikipédia sont déclarées dans `ide.catalogue.REGISTERS`, et **tout ce qu'elles
contiennent** entre dans le pool. L'appartenance d'un article à une catégorie est décidée par
les contributeurs de Wikipédia, non par l'auteur de l'analyse.

| Registre | Catégories | Disponibles | Substantiels | Retenus |
|---|---|---|---|---|
| accusation | complots, désinformation, fausses nouvelles, canulars, scandales politiques, corruption, propagande, paniques morales | 3 126 | 1 935 | 220 |
| découverte | sondes et missions spatiales, expériences de physique, relevés astronomiques, exoplanètes, lauréats Nobel | 6 322 | 2 705 | 220 |

Quatre précautions contre les confondants prévisibles :

| Précaution | Motif |
|---|---|
| des **événements** de part et d'autre | opposer des affaires à des concepts abstraits comparerait des types de sujets, non des registres |
| classes **disjointes** | un article des deux registres est écarté, non arbitré |
| échantillonnage par **empreinte de titre** | une troncature alphabétique surreprésenterait systématiquement certains sujets |
| filtre de **substance** (≥ 10 000 octets) | « Astronomical surveys » explorée à profondeur 1 ramène près de quatre mille entrées de catalogue à trafic nul, qui décimeraient un registre et pas l'autre |

Le manifeste résultant est écrit dans `data/catalogue.json` et **versionné** : c'est lui qui
constitue le pré-enregistrement, et un résultat publié se rapporte à un corpus consultable.

## Résultats

![Corpus étendu : confondant de trafic et non-réplication](figures/fig11_corpus_etendu.png)

/// caption
Le déséquilibre d'audience entre registres ; la disparition de l'écart de taux quand on
contrôle le trafic ; la non-réplication de l'écart de persistance ; et le taux de basculement
qui suit l'audience plutôt que le registre. Figure régénérée par
[le notebook 11](notebooks/11_corpus_etendu.ipynb).
///

### 1. Un écart apparaît, puis s'évanouit

| Comparaison | accusation | découverte | rapport de cotes | p |
|---|---|---|---|---|
| brut (440 sujets) | 8,6 % | 2,7 % | 3,4 | **0,014** |
| strate ≥ 47 vues/jour | 16,5 % | 12,5 % | 1,38 | 0,63 |
| apparié sur le trafic (173 paires) | 6,9 % | 3,5 % | — | 0,18 (McNemar) |

La détection exige un régime antérieur d'au moins 50 consultations par jour. Or le trafic
médian vaut 39 vues/jour côté accusation contre 11 côté découverte, et la part de sujets
au-dessus du seuil est de 47 % contre 22 %. **Le registre n'explique pas ce que l'audience
explique déjà.**

Il subsiste une direction — les sujets d'accusation basculent un peu plus souvent à trafic
égal — mais rien qui autorise une conclusion.

### 2. La persistance ne se réplique pas

| Corpus | accusation | découverte | p |
|---|---|---|---|
| pilote, 14 sujets choisis à la main | **×9,20** (n = 8) | ×2,90 (n = 6) | 0,081 |
| étendu, 440 sujets dérivés de catégories | **×3,04** (n = 21) | ×2,90 (n = 7) | 0,533 |

Le corpus pilote contenait les théories du complot les plus connues — QAnon à ×44, Pizzagate
à ×18 — et c'est exactement ce qu'une sélection manuelle produit : les cas qui viennent à
l'esprit sont les cas extrêmes. Le corpus dérivé de catégories contient aussi des dizaines de
sujets obscurs du même registre, et sa médiane devient indiscernable de celle du registre
« découverte ».

Le protocole de sélection ne modifiait pas la précision du résultat : il en modifiait le sens.

### 3. Le registre est un indicateur bruité

Les plus fortes élévations retenues côté accusation sont instructives :

| Sujet | Date | Élévation |
|---|---|---|
| Lil Tay | 27 juin 2020 | ×7,9 |
| Watch Dogs (jeu vidéo) | 6 décembre 2020 | ×6,3 |
| Million Dollar Extreme | 6 juillet 2016 | ×5,7 |
| The Capture (série) | 30 juillet 2022 | ×5,5 |
| Mossack Fonseca | 14 octobre 2019 | ×4,8 |

« Lil Tay » figure dans une catégorie de canulars à cause d'un canular sur sa mort, mais la
dynamique d'attention de cet article est celle d'une célébrité. Il en va de même pour un jeu
vidéo ou une série télévisée classés dans des catégories thématiques sans que leur audience
soit mobilisée par un scandale.

Un bruit d'étiquetage ne biaise pas le résultat dans une direction : il **l'attire vers
zéro**. Le résultat nul est donc compatible avec deux lectures que ces données ne permettent
pas de séparer — absence d'effet, ou effet dilué.

### 4. L'identification reste hors de portée

Deux ajustements sur vingt-huit ont d'abord été déclarés exploitables, avec des rapports de
**697 et 5431** — soit des temps d'oubli de plusieurs années pour une fenêtre d'ajustement de
quatre mois. Une transition presque en marche d'escalier n'expose pas le coude qui porte
l'information sur $\lambda$ : l'ajustement épouse la courbe, la dispersion résiduelle est
excellente, et le rapport s'envole sans contrainte.

Un contrôle d'**observabilité** a donc été ajouté au module — le temps d'oubli doit tenir dans
la fenêtre ajustée. Après correction, comme sur le corpus pilote, aucun changement ne livre
de paramètres exploitables.

## Ce que cela change pour le projet

**La seule différence entre registres émotionnels que le projet avait mesurée ne survit pas à
sa vérification.** Le mécanisme de la charge émotionnelle $\alpha$ reste sans appui empirique,
ni par le taux d'amplification ([calibration](calibration.md)), ni par la persistance.

Pour le [mémorandum](memorandum.md), la conséquence est directe : l'indicateur de persistance
proposé en remplacement du plafond sur $\gamma\alpha/\lambda$ **mesure bien quelque chose** —
dates et amplitudes des basculements sont robustes — mais **ne discrimine pas** les registres
émotionnels sur ce corpus. Il reste utilisable comme instrument de constat, non comme preuve
d'un mécanisme.

## Aucun des deux protocoles ne tranche — et ce qui a tranché

Le pilote était biaisé par la sélection ; l'étendu est bruité par l'étiquetage. Ce n'est pas
une impasse mais une spécification : un troisième protocole devrait combiner un **pool dérivé
de catégories** — pour l'absence de biais de sélection — et une **validation du registre sujet
par sujet**, réalisée en aveugle, sans voir les séries. C'est un travail d'annotation, non de
calcul.

!!! success "Fait — voir [Annotation en aveugle](annotation.md)"
    Ce troisième protocole a été mené. Les 440 sujets ont été codés à la main à partir du seul
    couple titre + chapeau, sous une grille publiée avant que la moindre annotation existe.
    L'accord entre catégorie et annotation est de **59,5 %** ; l'écart de taux de basculement
    tombe à un rapport de cotes de **0,93** ($p = 1{,}00$) ; et les sujets écartés — ceux qui
    ne relèvent d'aucun registre — basculent en fait **plus souvent** que les deux autres.
    C'étaient eux qui portaient l'écart.

## Pistes ouvertes

1. ~~**Annoter le registre à la main sur le pool dérivé de catégories**, en aveugle.~~
   → **[fait](annotation.md)**, sur les 440 sujets plutôt que deux cents. La question est
   tranchée : absence d'effet, et non effet dilué.
2. **Apparier sur le trafic dès la construction du corpus** plutôt qu'en aval : tirer les
   sujets par paires de trafic comparable immuniserait la comparaison contre le confondant
   principal. L'annotation y ajoute une exigence : **apparier aussi sur le type de sujet**, les
   deux registres ne portant presque pas sur les mêmes natures d'objets.
3. **Abaisser le seuil de détection en agrégeant par semaine.** Un taux de basculement de 2 à
   8 % laisse plus de neuf sujets sur dix sans mesure.
4. **Établir un taux de basculement de référence** sur un registre témoin — sujets sans charge
   émotionnelle particulière, à trafic apparié — pour mesurer la spécificité du détecteur.

---

*Implémentation : `ide.catalogue` · Notebook :
[11 — Corpus étendu](notebooks/11_corpus_etendu.ipynb) ·
[corpus pilote](regimes.md) · [feuille de route](feuille-de-route.md)*
