# Calibration : la première mesure de γα/λ

!!! success "Le chiffre qui manquait"
    Sur **19 épisodes d'attention publics**, le rapport $\gamma\alpha/\lambda$ vaut entre
    **1,5 et 12**, de médiane **2,5 à 4,2** selon l'estimateur. L'amplification est deux à
    quatre fois plus rapide que l'oubli.

!!! warning "Et ce qu'il oblige à réécrire"
    Le rapport dépasse 1 dans **tous** les épisodes, sous tous les estimateurs. Ce n'est pas
    une confirmation du critère $\gamma\alpha > \lambda$ : c'est la démonstration que
    **vérifier son signe n'apprend rien.** La recommandation 2 du
    [mémorandum](memorandum.md) doit porter sur un **plafond du rapport**.

---

## Ce qui est estimé

L'[équation de résonance](theorie/resonance.md) décrit un oscillateur, mais son contenu
oscillatoire n'a de sens que dans le régime de cycle limite. Pour un **pic d'attention
isolé**, la dynamique se réduit à sa forme du premier ordre :

$$\frac{dV}{dt} = \gamma\alpha\,\sigma(V)\,V - \lambda V$$

Elle se sépare en deux régimes directement mesurables :

| Phase | Condition | Comportement | Pente |
|---|---|---|---|
| **montée** | $V \ll V_{\text{sat}}$, donc $\sigma \approx 1$ | $V \propto e^{(\gamma\alpha-\lambda)t}$ | $r_{\text{up}} = \gamma\alpha - \lambda$ |
| **décroissance** | saturation atteinte, déclencheur passé | $V \propto e^{-\lambda t}$ | $r_{\text{down}} = \lambda$ |

D'où l'identification :

$$\lambda = r_{\text{down}}, \qquad
  \gamma\alpha = r_{\text{up}} + r_{\text{down}}, \qquad
  \boxed{\frac{\gamma\alpha}{\lambda} = 1 + \frac{r_{\text{up}}}{r_{\text{down}}}}$$

Deux régressions log-linéaires sur un même épisode suffisent.

## La source, et ce qu'elle n'est pas

Les données proviennent de l'**API de consultations de Wikimedia** — la seule source qui
réunisse accès libre sans clé, granularité quotidienne, profondeur depuis juillet 2015 et
stabilité. Les archives Reddit ont fermé, l'API de X est devenue payante, Google Trends
masque l'échelle absolue.

Trois réserves bornent ce qu'on peut conclure :

1. **Wikipédia n'a pas d'algorithme de recommandation.** Le $\gamma$ estimé est le gain
   composite de l'écosystème informationnel — recherche, partage, reprise médiatique — non
   la fonction de classement d'une plateforme. C'est une borne écosystémique, pas un audit
   de plateforme.
2. **Une consultation n'est pas une exposition.** Le modèle décrit ce qui est *servi* ; ces
   séries mesurent ce qui est *consulté*.
3. **Le filtre d'agent est décisif.** Sans exclusion des robots, l'article OSIRIS-REx
   présente un pic à 17 millions de consultations en un jour. Toutes les séries sont
   filtrées sur l'agent `user`.

Le cache des 24 séries est **versionné dans le dépôt** : l'analyse est reproductible hors
ligne, et un résultat publié ne dépend pas de la disponibilité future d'un service tiers.
Un test vérifie que le corpus reste intégralement disponible.

## Le corpus est pré-enregistré

La comparaison entre classes n'aurait aucune valeur si la liste des sujets pouvait être
révisée après coup. Elle est figée dans `ide.corpus`, et la règle est explicite : **aucun
article n'est retiré au vu de son résultat.**

* **accusation** (12 sujets) — attention mobilisée par une accusation, une menace, un
  scandale : colère, indignation, peur. Registre à $\alpha$ élevé.
* **découverte** (12 sujets) — attention mobilisée par une découverte ou une réussite **non
  programmée** : curiosité, admiration. Registre à $\alpha$ faible.

La restriction aux annonces non programmées vise un confondant précis : un événement soudain
monte plus raide qu'un événement anticipé, indépendamment de sa charge émotionnelle.

## Résultats

![Calibration de γα/λ sur des séries de consultation publiques](figures/fig09_calibration.png)

/// caption
Un épisode vu de près ; la distribution du rapport par classe ; la sensibilité de la médiane
au choix d'estimateur ; et l'artefact qui a imposé le second estimateur. Figure régénérée par
[le notebook 09](notebooks/09_calibration_visibilite.ipynb).
///

| Estimateur | n | médiane | IQR | étendue | p (accusation vs découverte) |
|---|---|---|---|---|---|
| adaptatif | 19 | **4,16** | [3,44 ; 6,17] | [2,01 ; 12,01] | 0,48 |
| horizon 5 j | 19 | **2,52** | [1,92 ; 3,80] | [1,54 ; 4,89] | 0,13 |
| horizon 7 j | 9 | **3,34** | [2,97 ; 4,21] | [1,81 ; 6,28] | 0,56 |
| horizon 10 j | 4 | **3,18** | [2,78 ; 3,54] | [2,47 ; 3,78] | 0,67 |

### 1. Le critère de signe est vide

Le rapport dépasse 1 partout — et c'est logique : par construction, un épisode d'attention
observable a connu une phase de croissance, donc $r_{\text{up}} > 0$, donc
$\gamma\alpha > \lambda$.

> **Conséquence pour le mémorandum.** « Interdire les configurations où
> $\gamma\alpha > \lambda$ » est **inapplicable tel quel** : la condition est satisfaite par
> tout contenu qui a percé. Ce qu'un régulateur peut contraindre, c'est un **plafond sur le
> rapport** — et cette mesure fournit la référence à partir de laquelle un tel plafond se
> discute.

C'est un résultat négatif sur la formulation, et positif sur la démarche : sans la mesure,
l'erreur serait passée dans un texte réglementaire.

### 2. La valeur est sensible à la méthode, le signe ne l'est pas

La médiane varie d'un facteur 1,7 entre estimateurs. Toute valeur citée doit l'être avec son
estimateur, et un seuil réglementaire adossé à une valeur unique serait attaquable.

### 3. L'artefact de fenêtre, et sa correction

Avec des fenêtres délimitées par le retour au niveau de fond, leur durée varie de 6 à 46
jours. L'attention ne décroissant pas exactement comme une exponentielle — sa queue est plus
lourde — un ajustement sur une fenêtre longue capte cette queue et produit un $\lambda$ plus
faible. La corrélation de rang mesurée est de **−0,94** : $\lambda$ était pour l'essentiel
déterminé par la longueur de la fenêtre, non par le sujet.

L'estimateur à **horizon fixe** force les deux fenêtres à la même durée. $\lambda$ devient
« le taux d'oubli moyen sur les $H$ premiers jours après le pic », comparable entre
épisodes. Le prix est le rejet des épisodes trop brefs — d'où la chute d'effectif quand $H$
augmente.

### 4. Le mécanisme de la charge émotionnelle n'est pas étayé

Aucun estimateur ne produit d'écart détectable entre les deux classes ($p \geq 0{,}13$), et
l'estimation ponctuelle va **dans le sens contraire** à la prédiction : la classe
« découverte » présente une médiane légèrement supérieure.

Il serait malhonnête d'en tirer une réfutation : les effectifs sont minuscules, le biais de
sélection décrit ci-dessous écarte les cas les plus chargés émotionnellement, et Wikipédia
n'est pas le terrain où le mécanisme est censé opérer. Mais il serait tout aussi malhonnête
de présenter le mécanisme comme soutenu par les données. **Il ne l'est pas.**

## La limite la plus lourde : la méthode est aveugle aux régimes installés

Onze sujets sur vingt-quatre n'ont livré aucun épisode exploitable — et ce sont, pour la
classe « accusation », les cas archétypaux : **QAnon, désinformation Covid-19, hésitation
vaccinale, grand remplacement, Pegasus**.

La raison est structurelle. Ces sujets ne produisent pas un pic suivi d'une décroissance :
leur attention **change de régime et s'installe** sur un palier durable. Le niveau de fond
glissant suit ce palier, et le critère de proéminence n'est alors jamais franchi. La méthode
ne les rejette pas — elle **ne les voit pas**.

C'est une limite de premier ordre : la procédure sélectionne contre le phénomène même que la
théorie cherche à décrire. Un [test](https://github.com/s-geffroy/Indice-Diversite-Exposee/blob/main/tests/test_calibration.py)
le vérifie explicitement sur un changement de régime synthétique, pour que cette limite ne
puisse pas être oubliée.

Le second motif de rejet dominant est la **fenêtre trop courte** : beaucoup d'épisodes
montent en un ou deux jours, ce qui n'est pas ajustable en données quotidiennes.

## Ce que cela ouvre

1. **Détection de changement de régime** plutôt que de pic, pour atteindre les dynamiques
   d'installation durable — le cas qui compte le plus et qui échappe entièrement à cette
   analyse.
2. **Résolution infra-quotidienne**, pour rendre identifiables les épisodes brefs.
3. **Décroissance non exponentielle** — ajuster une loi de puissance ou une somme de deux
   exponentielles supprimerait l'artefact de fenêtre au lieu de le contourner.
4. **Une source dotée d'un algorithme de recommandation**, seule voie pour estimer un
   $\gamma$ de plateforme plutôt qu'un gain d'écosystème : c'est l'objet de l'accès aux
   données de l'article 40 du DSA. La présente mesure est le dossier qui rend une telle
   demande crédible.

---

## Reproduire

```bash
# Le cache est versionné : cette étape n'est nécessaire que pour le rafraîchir.
docker compose run --rm lab python scripts/fetch_pageviews.py

docker compose run --rm notebooks jupyter nbconvert --to notebook --execute --inplace \
  notebooks/09_calibration_visibilite.ipynb
```

*Implémentation : `ide.calibration`, `ide.pageviews`, `ide.corpus` · Notebook :
[09 — Calibration](notebooks/09_calibration_visibilite.ipynb) ·
[feuille de route](feuille-de-route.md)*
