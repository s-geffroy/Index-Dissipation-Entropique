# Température sociale, transition de phase et hystérésis

## Le modèle d'Ising transposé

Chaque individu porte une opinion binaire $s_i \in \{-1, +1\}$, et la population suit
la distribution de Gibbs-Boltzmann :

$$P(\sigma) = \frac{1}{Z}\exp\!\left(\frac{J \sum_{\langle i,j \rangle} s_i s_j + H \sum_i s_i}{k_B T}\right)$$

Trois paramètres, trois lectures sociologiques :

| Paramètre | Physique | Société |
|---|---|---|
| $J$ | couplage d'échange | **force de conformisme** : coût psychologique d'un désaccord avec ses voisins |
| $T$ | température thermodynamique | **température sociale** : agitation, irrationalité, ouverture aux fluctuations |
| $H$ | champ magnétique externe | **champ médiatique** : injection asymétrique d'information |

## La température critique

L'intérêt du modèle ne tient pas à l'analogie mais à une propriété **vérifiable** :
il existe une température critique qui sépare deux régimes qualitativement différents.

En dimension 2, sa valeur est connue exactement depuis Onsager (1944) :

$$\frac{T_c}{J} = \frac{2}{\ln(1 + \sqrt{2})} \approx 2{,}269$$

C'est le seul point du dépôt où une prédiction théorique exacte, **indépendante de
nos hypothèses sociologiques**, peut valider l'implémentation. Le notebook 02 la
retrouve numériquement, au décalage de taille finie près.

* $T < T_c$ — la population gèle dans un consensus, ou dans des blocs homogènes.
* $T > T_c$ — l'agitation empêche tout accord stable ; les avis fluctuent en
  permanence, même dans un petit groupe.

Le passage n'est pas graduel mais **critique** : une société peut basculer d'un régime
à l'autre sur une variation modeste d'agitation.

### Deux valeurs critiques, deux significations

Le dépôt manipule deux $T_c$ différentes, et il faut savoir laquelle sert à quoi :

| Modèle | $T_c$ | Hypothèse d'interaction |
|---|---|---|
| Ising 2D (exact) | $\approx 2{,}269\,J$ | quatre voisins géographiques |
| Champ moyen (Curie-Weiss) | $J$ | chacun subit l'opinion moyenne de tous |

Le champ moyen surestime la cohésion, donc sous-estime la température nécessaire pour
la briser. La comparaison a un sens : **un réseau social globalisé est plus proche du
champ moyen qu'un voisinage réel**, ce qui le rend plus fragile à la polarisation, pas
moins. → [audit, point 13](../limites.md)

## L'énergie libre : ce que le système optimise

$$F = E - TS$$

* $E$ est la tension interne — le coût de ne pas être d'accord avec ses voisins. Le
  système cherche à la minimiser, donc à maximiser l'accord.
* $TS$ est la force de dispersion.

Quand la population croît, l'entropie de configuration $S$ croît avec elle et le terme
$TS$ finit par dominer $E$. La nature — et la société — privilégie alors la
maximisation du désordre plutôt que la minimisation de la tension.

C'est cette énergie libre, écrite complètement, qui produit la véritable transition de
phase du modèle. Le raisonnement d'origine l'invoquait sans l'écrire, et sa version
tronquée ne pouvait produire aucune transition. → [audit, point 4](../limites.md)

## L'hystérésis : pourquoi un démenti ne suffit pas

C'est le résultat le plus directement actionnable du travail.

Si l'on aimante un morceau de fer puis qu'on coupe le champ, le fer **reste
aimanté**. Transposé : quand une fausse information est massivement diffusée puis
officiellement démentie, le champ médiatique retombe à $H = 0$, mais l'opinion ne
revient pas à la neutralité.

Le terme de conformisme $-J\sum s_i s_j$ a pris le relais du champ. Le groupe
maintient la croyance par cohésion interne, parce qu'en sortir coûterait à chacun sa
place dans le groupe.

Le cycle se lit en trois temps, qui sont ceux d'une crise médiatique :

1. **Injection** — un champ $H > 0$ massif aligne la population, même initialement
   neutre.
2. **Démenti** — $H$ retombe à zéro. L'aimantation ne suit pas : c'est
   l'**aimantation rémanente**, la fraction de la population qui continue de croire.
3. **Contre-champ** — il faut appliquer un $H < 0$ dépassant le **champ coercitif**
   du groupe pour forcer le basculement inverse.

### Deux leviers, non exclusifs

| Levier | Mécanisme | Nature |
|---|---|---|
| Réchauffer le débat | augmenter $T$ jusqu'à dissiper la mémoire | structurel, lent, préventif |
| Contre-champ ciblé | appliquer $-H$ au-delà du champ coercitif | conjoncturel, coûteux, curatif |

Le notebook 05 mesure que l'aire du cycle décroît de façon monotone avec la
température sociale : **réchauffer le débat dissipe l'hystérésis.** C'est le
fondement de la recommandation d'injection de bruit thermique du
[mémorandum](../memorandum.md).

Une réserve importante, mesurée dans le notebook 08 : le bruit n'est pas
monotoniquement bénéfique. Un bruit modéré maximise la diversité d'exposition ; un
bruit excessif la dégrade à nouveau. Le fil de travail l'avait anticipé — « si on
injecte du bruit thermique en permanence, la société devient chaotique et illisible »
— et c'est ce qui justifie le **recuit** plutôt que l'agitation permanente.

---

*Implémentation : `ide.ising` · Notebooks :
[02 — Ising](../notebooks/02_ising_temperature_sociale.ipynb),
[05 — Hystérésis](../notebooks/05_hysteresis_et_contre_champ.ipynb)*
