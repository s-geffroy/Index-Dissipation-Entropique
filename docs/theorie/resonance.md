# Résonance algorithmique : l'effet Larsen informationnel

## Le mécanisme

Approchez un micro d'un haut-parleur : le moindre bruit est capté, amplifié, réémis,
capté de nouveau, jusqu'au sifflement. C'est l'effet Larsen — une rétroaction
positive dont le gain dépasse l'amortissement.

Une fausse information et un algorithme de recommandation forment exactement cette
boucle. La rumeur est le signal initial ; l'engagement qu'elle suscite est capté par
la plateforme, qui l'amplifie pour maximiser la rétention, ce qui produit davantage
d'engagement.

## L'équation

$$\ddot{V} + \big(\lambda - \gamma\alpha\,\sigma(V)\big)\dot{V} + \omega_0^2 V = \xi(t)$$

| Symbole | Signification |
|---|---|
| $V(t)$ | visibilité du contenu dans les flux |
| $\lambda$ | amortissement naturel : l'oubli, la lassitude du public |
| $\gamma$ | gain algorithmique appliqué par la plateforme |
| $\alpha$ | charge émotionnelle innée du contenu |
| $\omega_0$ | fréquence propre du cycle médiatique |
| $\sigma(V)$ | facteur de saturation : l'attention disponible est finie |
| $\xi(t)$ | bruit blanc : les fluctuations du comportement humain |

## Le critère d'instabilité

$$\boxed{\gamma\alpha > \lambda}$$

Au-delà de ce seuil, l'amortissement effectif devient **négatif** : le système
n'évacue plus l'énergie qu'on lui injecte, il l'accumule.

C'est le résultat le plus opérationnel de tout le travail, parce qu'il est **auditable** :
un régulateur peut, en principe, mesurer un taux d'amplification et un taux d'amortissement.
Le notebook 06 vérifie que le seuil mesuré coïncide bien avec
$\gamma^\star = \lambda/\alpha$.

!!! warning "Ce que la mesure a corrigé"
    La [calibration sur données publiques](../calibration.md) donne
    $\gamma\alpha/\lambda$ entre **1,5 et 12** sur 19 épisodes d'attention. Le rapport
    dépasse donc 1 **partout** — non par pathologie de l'écosystème, mais parce que tout
    épisode observable a connu une phase de croissance. **Vérifier le signe n'apprend
    rien** : la grandeur réglementaire est la marge, et la recommandation correspondante du
    mémorandum a été réécrite en plafond. Voir l'[audit, point 15](../limites.md).

## Le point qui compte pour la régulation

À gain algorithmique **constant**, un contenu plus émotionnel franchit le seuil qu'un
contenu factuel ne franchit pas. La conséquence est importante :

> Une plateforme n'a **pas besoin de favoriser la désinformation** pour l'amplifier
> sélectivement. Un gain uniforme appliqué à des contenus d'émotivité inégale produit
> mécaniquement ce biais.

C'est ce qui rend la mesure de $\gamma$ plus pertinente qu'un audit d'intentions : il
n'y a pas de décision malveillante à démontrer, seulement un paramètre à contraindre.

## Deux corrections au modèle d'origine

**Le signe du rappel.** Le fil écrivait $-\omega_0^2 V$, ce qui fait du point
d'équilibre un col instable *quels que soient* les autres paramètres : le système
divergerait même à gain nul, et le critère $\gamma\alpha > \lambda$ perdrait tout
contenu. → [audit, point 6](../limites.md)

**La saturation.** Sans $\sigma(V)$, la solution instable est
$V(t) \propto e^{(\gamma\alpha - \lambda)t}$, qui diverge sans limite. C'est
mathématiquement exact et physiquement vide : l'attention disponible est finie, et un
modèle qui prédit une visibilité infinie ne permet ni de comparer deux configurations
ni de calibrer un seuil.

Avec $\sigma(V) = 1/\big(1 + (V/V_{\text{sat}})^2\big)$, l'amplification s'éteint
progressivement à mesure que la visibilité approche la capacité d'attention. Le
système ne diverge plus : il s'installe dans un **cycle limite** de type Van der Pol.

C'est un gain de réalisme, pas un artifice de convergence. Ce qu'on observe d'une
fausse information installée n'est pas une explosion, c'est un **sujet qui revient
périodiquement**. → [audit, point 7](../limites.md)

## Le rôle exact des algorithmes

Le fil identifiait trois fonctions distinctes, qui restent valides :

1. **Accélérateur cinétique.** Les modèles de classement fondés sur la popularité
   mesurent la vitesse initiale de réaction. Une fausse information suscitant
   l'indignation, sa vélocité de départ est supérieure à celle d'un fait vérifié.
   L'algorithme l'interprète comme une anomalie rentable.
2. **Isolateur thermique.** Le filtrage collaboratif coupe les liens avec la
   contradiction. L'utilisateur n'est plus exposé au bruit correctif extérieur : sa
   température sociale locale chute, et son opinion se fige.
3. **Multiplicateur de portée.** L'algorithme identifie les nœuds à forte centralité
   et utilise leurs interactions pour ajuster les performances globales de
   l'écosystème.

Ces trois rôles agissent sur des paramètres différents du modèle — respectivement
$\gamma$, $T$ et la topologie — ce qui explique pourquoi un levier de régulation
unique ne suffit pas.

## Ce que la conclusion doit à l'algorithme

Le point où l'analogie physique est la plus fragile est aussi celui qui rend l'ADE
concevable. Un bain thermique ne poursuit pas d'objectif ; un algorithme de
recommandation optimise une fonction de coût. Il n'est donc pas un environnement, il
est un **acteur stratégique**.

Mais une fonction de coût, contrairement à une loi physique, **peut être changée**.
→ [ADE](../ade.md)

---

*Implémentation : `ide.resonance` · Notebook :
[06 — Résonance](../notebooks/06_resonance_larsen.ipynb)*
