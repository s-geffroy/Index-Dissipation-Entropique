# ADE — Algorithme de Dissipation Entropique

!!! info "Deux objets distincts"
    L'**[IDE](ide.md)** est une *métrique*, imposée par le régulateur. L'**ADE** est
    un *algorithme*, une façon parmi d'autres de maintenir cette métrique au-dessus
    d'un seuil. Le mémorandum impose la première et **ne prescrit pas** le second.

## Le problème que l'ADE résout

Un algorithme de recommandation classique maximise l'engagement immédiat. La
[cinétique de résonance](theorie/resonance.md) montre que cette fonction de coût *est*
celle qui produit un amortissement négatif : elle récompense mécaniquement la charge
émotionnelle, donc la désinformation, et pousse le système vers la résonance
destructive.

Le problème n'est pas un défaut d'implémentation ni une intention malveillante. C'est
la fonction de coût elle-même. Et une fonction de coût, contrairement à une loi
physique, peut être changée.

## La fonction de score

$$\boxed{S(i, c) = \mathrm{Pertinence}(i, c) + \mu \cdot \Delta H(i, c)}$$

| Terme | Rôle |
|---|---|
| $\mathrm{Pertinence}(i,c)$ | le score classique de correspondance, **conservé** |
| $\Delta H(i,c) = H_{\text{futur}} - H_{\text{actuelle}}$ | l'impact entropique : ce que l'affichage ferait à l'IDE du fil |
| $\mu \ge 0$ | le coefficient de régulation thermodynamique, la « viscosité » du flux |

**Le signe est positif.** Le fil de travail hésitait entre $-\mu\Delta H$ et
$+\mu\Delta H$ ; seule la seconde version fait remonter un contenu qui diversifie. La
première refermerait la bulle qu'elle prétend ouvrir, et une plateforme de mauvaise foi
pourrait s'en réclamer. Le code **refuse** un $\mu$ négatif par une exception explicite.
→ [audit, point 2](limites.md)

**La pertinence est conservée.** Un algorithme qui servirait de la diversité sans
pertinence serait abandonné par ses utilisateurs, ce qui ne dissiperait aucune
entropie. L'ADE n'est pas un filtre de censure, c'est un rééquilibrage.

## Le recuit : $\mu$ n'est pas constant

Tant que le fil reste diversifié, l'algorithme n'a aucune raison d'intervenir. Dès que
l'IDE passe sous le seuil critique — signal d'une bulle qui se referme — $\mu$ monte et
l'algorithme entre en **mode recuit** : il sur-classe délibérément les contenus
divergents, le temps de réchauffer le fil.

C'est la transposition du **recuit simulé** de la métallurgie : un pic de température
ponctuel pour casser un état figé, suivi d'un refroidissement lent qui laisse le
système se réinstaller dans un état de moindre tension.

```python
from ide.ade import annealing_coefficient

annealing_coefficient(0.80)   # 0.5 — fil sain, régime de repos
annealing_coefficient(0.20)   # 2.25 — la bulle se referme, μ monte
annealing_coefficient(0.00)   # 4.0 — bulle gelée, recuit à pleine puissance
```

### La montée doit être progressive

Avec un déclenchement en tout ou rien, chaque intervention relèverait l'index juste
au-dessus du seuil, ce qui désactiverait l'intervention suivante, qui le laisserait
retomber : un battement permanent sans stabilisation. L'interpolation linéaire entre le
seuil et zéro évite ce cycle.

## Ce que ça donne concrètement

Un utilisateur enfermé dans une bulle, deux contenus candidats :

```python
from ide.ade import Candidate, EntropicScorer

scorer = EntropicScorer(catalogue_size=4)
feed = ["complot"] * 20

candidates = [
    Candidate("contenu-de-bulle", "complot", relevance=0.95),
    Candidate("verification",     "factuel", relevance=0.50),
]

for scored in scorer.rank(feed, candidates):
    print(f"{scored.identifier:18s} score={scored.score:.3f}  ΔH={scored.delta_entropy:.4f}")
# verification       score=1.052  ΔH=0.1381
# contenu-de-bulle   score=0.950  ΔH=0.0000
```

La vérification factuelle dépasse au classement un contenu pourtant presque deux fois
plus pertinent — non par pénalisation du second, dont le score reste sa pertinence
brute, mais par le **bonus entropique** du premier. Le fil étant gelé, $\mu$ est à sa
valeur de recuit maximale : c'est ce qui permet à un écart de pertinence de $0{,}45$
d'être renversé par un impact entropique de $0{,}14$.

Le [notebook 07](notebooks/07_ade_filtre_entropique.ipynb) montre la boucle complète :
un fil initialement gelé voit son IDE remonter au fil des cycles de service, alors
qu'un filtre d'engagement pur l'y maintient indéfiniment.

## Ce qui rend l'ADE déployable

**À $\mu = 0$, l'ADE est indiscernable d'un filtre d'engagement.** La transformation
est un ajout paramétré, pas une refonte du produit. Un régulateur peut donc exiger une
valeur minimale de $\mu$ — ou un IDE minimal, ce qui revient au même sans prescrire
l'implémentation — sans imposer de réécrire un moteur de recommandation.

**L'intervention est intermittente.** Une fois l'index rétabli, $\mu$ redescend et la
pertinence reprend la main. L'algorithme n'impose pas la diversité en permanence : il
empêche le gel. C'est aussi ce qui limite son coût en pertinence perçue.

## Les quatre remèdes du modèle, et leur portée

Le fil proposait quatre leviers. Ils restent valides, mais ils n'agissent pas sur les
mêmes paramètres et n'ont pas la même solidité :

| Levier | Action | Solidité |
|---|---|---|
| **Bruit thermique** | augmenter $T$ : injecter un quota de contenus non personnalisés | bien étayée — l'hystérésis décroît avec $T$ ([notebook 05](notebooks/05_hysteresis_et_contre_champ.ipynb)) |
| **Recuit simulé** | faire fluctuer $T(t)$ : pics ponctuels en période de crise, puis refroidissement | étayée, et **préférable au bruit permanent** : le [notebook 08](notebooks/08_abm_compas_politique.ipynb) montre qu'un bruit excessif dégrade à nouveau la diversité |
| **Contre-champ $-H$** | saturer les flux touchés par un contre-discours de puissance équivalente | conséquence directe de l'hystérésis, mais coûteuse et politiquement délicate |
| **Restructuration topologique** | limiter la portée des partages en cascade | **à reformuler** : la connectivité accélère le consensus plus qu'elle ne le bloque ([audit, point 12](limites.md)). Défendable comme mesure d'urgence, pas comme diagnostic |

## Limites

* **L'ADE n'est pas testé sur un système réel.** Il est validé sur son propre modèle,
  avec un catalogue de quatre points de vue et une notion de pertinence synthétique.
* **Le coût en engagement n'est pas évalué.** Une plateforme objectera que le
  rééquilibrage réduit la rétention ; le dépôt ne fournit aucun élément pour arbitrer.
* **La discrétisation en points de vue est héritée de l'IDE**, avec ses limites : de la
  diversité d'étiquette peut satisfaire le score sans diversifier l'argument.
* **Un algorithme qui décide de ce qu'il faut voir reste un algorithme qui décide.**
  Changer sa fonction de coût déplace le pouvoir éditorial, il ne le supprime pas.

---

*Implémentation : `ide.ade` · Notebook :
[07 — ADE](notebooks/07_ade_filtre_entropique.ipynb) ·
[Mémorandum de régulation](memorandum.md)*
