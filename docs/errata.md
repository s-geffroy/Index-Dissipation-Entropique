# Errata : écarts assumés vis-à-vis du fil de travail

Ce dépôt n'est pas une transcription. Chaque écart avec le fil de travail du
14 août 2026 est listé ici, avec sa justification et l'endroit où il est vérifié.
L'[audit critique](limites.md) développe le raisonnement ; cette page sert de table de
correspondance.

## Formules modifiées

| Fil de travail | Retenu | Pourquoi | Vérifié par |
|---|---|---|---|
| $S = \mathrm{Pertinence} - \mu \Delta H$ | $S = \mathrm{Pertinence} + \mu \Delta H$, $\mu \ge 0$ | la version négative pénalise la diversité | `tests/test_ade.py::TestEntropicScore` |
| $A(x) = Jx + H$ | $A(x) = Jx + H - T\,\mathrm{artanh}(x)$ | sans terme entropique, aucune transition de phase et dynamique non bornée | `tests/test_fokker_planck.py::TestFreeEnergy` |
| $V(x) = -\frac{J}{2}x^2 - Hx$ | $f(x) = -\frac{J}{2}x^2 - Hx + T\,s_{\text{mél}}(x)$ | c'est le $F = E - TS$ que le fil invoquait sans l'écrire | idem |
| $P(x \to x-\frac{1}{N}) = x(1-x) - hx$ | $(1-h)\,x(1-x)$ | la version d'origine est négative pour $h > 1-x$ | `tests/test_voter.py::…negative_probabilities` |
| $\ddot V + (\lambda - \gamma\alpha)\dot V - \omega_0^2 V = \xi$ | $\ddot V + (\lambda - \gamma\alpha\sigma(V))\dot V + \omega_0^2 V = \xi$ | le signe négatif rendait le système instable à gain nul ; la saturation le borne | `tests/test_resonance.py::TestSimulation` |

## Affirmations reformulées

| Fil de travail | Retenu |
|---|---|
| « la taille $N$ agit comme une pompe à entropie » | l'entropie **totale** croît avec $N$, mais le bruit de la **moyenne** décroît en $1/N$ : une grande population devient **rigide**, pas bruyante |
| « le réseau small-world rend tout consensus impossible » | la connectivité globale **accélère** le consensus ; ce sont le biais directionnel et l'homophilie qui fragmentent |
| « l'entropie de von Neumann a bondi de 0 à une valeur positive » | c'est l'entropie du **sous-système réduit** qui croît ; celle du système fermé est constante |
| « effet tunnel social » | franchissement de barrière par **activation thermique** (Kramers) ; l'effet tunnel est signalé comme métaphore |
| « la probabilité d'unanimité s'effondre en $1/k^N$ » | vrai pour un **état initial** de tirages indépendants ; la question dynamique est traitée par le temps de consensus |
| $\tau_D \propto \tau_R / N$ | conservé, explicitement étiqueté **loi d'échelle heuristique** |
| « Index de Dissipation Entropique (ADE) » | **IDE** = l'index (métrique), **ADE** = l'algorithme (filtre) |
| « la régulation devient une ingénierie de la stabilité » | conservé, mais accompagné de la réserve qu'une ingénierie de la stabilité *est* une intervention sur le débat public |

## Ajouts

Ces éléments n'existent pas dans le fil de travail.

* **Température sociale dans le modèle à agents.** Le paramètre central de toute la
  théorie était absent de sa seule implémentation. Sans lui, la population s'effondre
  sur un point unique et le modèle ne peut représenter aucun des régimes décrits.
* **Facteur de saturation** dans l'équation de résonance, sans lequel la solution
  instable diverge vers l'infini.
* **Température critique de champ moyen** $T_c = J$, distincte de la valeur d'Onsager,
  et l'explication de leur écart.
* **Solution stationnaire exacte à flux nul**, comme référence de validation du solveur
  numérique.
* **Section sur les limites propres à l'index comme instrument réglementaire** —
  manipulabilité, discrétisation comme choix politique, vie privée.
* **Suite de tests** (203 tests) et **notebooks reproductibles**.

## Conservé sans modification

Ce qui n'apparaît pas ci-dessus a été conservé. En particulier, la structure d'ensemble
du raisonnement, le critère d'instabilité $\gamma\alpha > \lambda$, l'analyse de
l'hystérésis sociale, les trois rôles des algorithmes dans la propagation, et
l'architecture du mémorandum de régulation sont ceux du fil de travail. L'intuition de
départ — la taille d'un système détruit son harmonie globale — n'a pas été touchée.

## Le prototype logiciel

`legacy/simulation_thread_2026-08.py` conserve le code `pygame` du fil **tel quel**,
sans correction, y compris son indentation perdue à l'impression. Ses cinq défauts sont
documentés dans [l'audit, point 14](limites.md), et son modèle est réimplémenté dans
`ide.abm`.
