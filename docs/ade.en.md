# EDA — Exposed Diversity Algorithm

!!! info "Two distinct objects"
    The **[index](ide.en.md)** is a *metric*, mandated by the regulator. The **algorithm**
    is one way among others of keeping that metric above a threshold. The memorandum
    mandates the former and **does not prescribe** the latter.

## The problem it addresses

A conventional recommender maximises immediate engagement. The
[resonance kinetics](theorie/resonance.md) shows that this cost function *is* the one
producing negative damping: it mechanically rewards emotional charge, hence
disinformation, and drives the system towards destructive resonance.

The problem is neither an implementation flaw nor malicious intent. It is the cost
function itself. And a cost function, unlike a physical law, can be changed.

## The scoring function

$$\boxed{S(i, c) = \mathrm{Relevance}(i, c) + \mu \cdot \Delta H(i, c)}$$

| Term | Role |
|---|---|
| $\mathrm{Relevance}(i,c)$ | the conventional matching score, **retained** |
| $\Delta H(i,c) = H_{\text{future}} - H_{\text{current}}$ | entropic impact: what serving the item would do to the feed's index |
| $\mu \ge 0$ | the thermodynamic regulation coefficient — the "viscosity" of the flow |

**The sign is positive.** The original thread wavered between $-\mu\Delta H$ and
$+\mu\Delta H$; only the latter promotes diversifying content. The former would close the
bubble it claims to open, and a bad-faith platform could invoke it. The code **refuses** a
negative $\mu$ with an explicit exception. → [audit, point 2](limites.en.md)

**Relevance is retained.** An algorithm serving diversity without relevance would be
abandoned by its users, dissipating no entropy at all. This is not a censorship filter, it
is a rebalancing.

## Annealing: $\mu$ is not constant

While the feed stays diverse, the algorithm has no reason to intervene. Once the index
drops below the critical threshold — the signal of a closing bubble — $\mu$ rises and the
algorithm enters **annealing mode**: it deliberately over-ranks divergent content long
enough to reheat the feed.

This transposes **simulated annealing** from metallurgy: a temperature spike to break a
frozen state, followed by slow cooling that lets the system resettle at lower tension.

```python
from ide.ade import annealing_coefficient

annealing_coefficient(0.80)   # 0.5  — healthy feed, resting regime
annealing_coefficient(0.20)   # 2.25 — the bubble is closing, μ rises
annealing_coefficient(0.00)   # 4.0  — frozen bubble, full annealing
```

### The ramp must be progressive

With all-or-nothing triggering, each intervention would lift the index just above the
threshold, disabling the next intervention, which would let it fall back: permanent
chattering without stabilisation. Linear interpolation between the threshold and zero
avoids that cycle.

## What it does in practice

A user enclosed in a bubble, two candidate items:

```python
from ide.ade import Candidate, EntropicScorer

scorer = EntropicScorer(catalogue_size=4)
feed = ["conspiracy"] * 20

candidates = [
    Candidate("bubble-item",  "conspiracy", relevance=0.95),
    Candidate("fact-check",   "factual",    relevance=0.50),
]

for scored in scorer.rank(feed, candidates):
    print(f"{scored.identifier:14s} score={scored.score:.3f}  ΔH={scored.delta_entropy:.4f}")
# fact-check     score=1.052  ΔH=0.1381
# bubble-item    score=0.950  ΔH=0.0000
```

The fact-check outranks an item almost twice as relevant — not by penalising the latter,
whose score remains its raw relevance, but through the **entropic bonus** of the former.
The feed being frozen, $\mu$ sits at its maximum annealing value: that is what lets a
relevance gap of $0.45$ be overturned by an entropic impact of $0.14$.

[Notebook 07](notebooks/07_ade_filtre_entropique.ipynb) shows the full loop: an initially
frozen feed sees its index recover over successive serving cycles, whereas a pure
engagement filter holds it there indefinitely.

## What makes it deployable

**At $\mu = 0$, the algorithm is indistinguishable from an engagement filter.** The
transformation is a parameterised addition, not a product rewrite. A regulator can
therefore require a minimum $\mu$ — or a minimum index, which amounts to the same without
prescribing the implementation — without mandating that a recommender engine be rewritten.

**The intervention is intermittent.** Once the index recovers, $\mu$ falls back and
relevance takes over. The algorithm does not impose permanent diversity: it prevents
freezing. That is also what limits its cost in perceived relevance.

## The four remedies, and how solid each is

| Lever | Action | Solidity |
|---|---|---|
| **Thermal noise** | raise $T$: inject a quota of non-personalised content | well supported — hysteresis decreases with $T$ ([notebook 05](notebooks/05_hysteresis_et_contre_champ.ipynb)) |
| **Simulated annealing** | modulate $T(t)$: spikes during crises, then cooling | supported, and **preferable to permanent noise**: [notebook 08](notebooks/08_abm_compas_politique.ipynb) shows excessive noise degrades diversity again |
| **Counter-field $-H$** | saturate affected feeds with equally forceful counter-speech | direct consequence of hysteresis, but costly and politically delicate |
| **Topological restructuring** | limit cascading share reach | **to reformulate**: connectivity accelerates consensus more than it blocks it ([audit, point 12](limites.en.md)). Defensible as an emergency measure, not as a diagnosis |

## Limitations

* **Not tested on a real system.** Validated against its own model, with a four-viewpoint
  catalogue and synthetic relevance. → [roadmap §3.1](feuille-de-route.en.md)
* **The engagement cost is not evaluated.** A platform will object that rebalancing
  reduces retention; the repository offers nothing to settle that.
* **Viewpoint discretisation is inherited from the index**, with its limitations: label
  diversity can satisfy the score without diversifying the argument.
* **An algorithm that decides what should be seen is still an algorithm that decides.**
  Changing its cost function relocates editorial power; it does not remove it.

---

*Implementation: `ide.ade` · Notebook:
[07](notebooks/07_ade_filtre_entropique.ipynb) ·
[Regulatory memorandum](memorandum.en.md)*
