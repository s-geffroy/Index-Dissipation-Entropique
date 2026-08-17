# Roadmap: the limitations, and how to close them

The [critical audit](limites.en.md) lists what this work cannot do. This page proposes a
concrete path for each limitation — on the premise that a limitation without a path is an
admission, and a limitation with a path is a programme.

Entries are ordered by **value / effort**, not logically.

---

## Priority 1 — Empirical calibration

**The limitation.** The parameters $J$ (conformity), $T$ (social temperature), $\gamma$
(algorithmic gain) and $\alpha$ (emotional charge) have no estimation procedure on real
data. This is the principal weakness: without it the formalism is coherent but untethered,
and no regulatory threshold is calibratable.

### 1.1 Estimate $\lambda$ and $\gamma\alpha$ from public visibility curves

The cheapest entry point, because the observable quantity — a piece of content's
visibility over time — is exactly the model's variable.

* **Method.** Fit $V(t)$ to engagement time series: in the damped regime (exponential
  decay → $\lambda$), then in the resonant regime (growth → $\gamma\alpha - \lambda$). Two
  log-linear regressions suffice for a first order of magnitude.
* **Sources.** Reddit archives (Pushshift and successors), Wikipedia edit histories on
  contested articles — complete, timestamped and public.
* **Deliverable.** A notebook `09_calibration_visibilite.ipynb` producing a plausible range
  for $\gamma\alpha/\lambda$, and determining whether the critical threshold is crossed in
  practice. **This is the result the memorandum most lacks.**

### 1.2 Infer the Fokker-Planck coefficients directly

* **Method.** Kramers-Moyal coefficient estimation: from a time series of the macroscopic
  variable $x(t)$, the conditional moments of the increments yield $A(x)$ and $B(x)$
  **without assuming their form**. The measured drift can then be compared with
  $Jx + H - T\,\mathrm{artanh}(x)$ — that is, the model can be **tested** rather than
  fitted.
* **Sources.** Long opinion-poll series (Eurobarometer, trust barometers), which supply
  aggregated $x(t)$ over decades.
* **Difficulty.** Poll sampling frequency is low; the method needs temporal resolution only
  platform data would provide.

### 1.3 Use DSA Article 40 data access

The DSA opens vetted-researcher access to very large platform data. This is the route that
would allow genuine calibration of $T$ and of the index threshold.

* **Prerequisites.** A formal access protocol, institutional affiliation, and a processing
  plan meeting privacy constraints (see §2.3).
* **Do first.** Points 1.1 and 1.2 on public data: they constitute the case that makes an
  access request credible.

---

## Priority 2 — Robustness of the index

### 2.1 Escape arbitrary viewpoint discretisation

**The limitation.** Whoever defines the $k$ modalities defines the index.

* **Multi-scale index.** Instead of a single $k$, measure the index at several
  granularities and publish the **curve** $\mathrm{EDI}(k)$. A real bubble collapses at
  every scale; a partitioning artefact does not. This turns the choice of $k$ into a
  result rather than a hidden parameter.
* **Continuous-space entropy.** Replace the modality distribution by a distribution in a
  semantic embedding space, estimating differential entropy via $k$-nearest-neighbour
  methods (Kozachenko-Leonenko). No labels, hence no partitioning arbitrariness — at the
  cost of dependence on the embedding model, which relocates the arbitrariness rather than
  removing it.
* **Rao's quadratic entropy.** $Q = \sum_{ij} p_i p_j d_{ij}$, weighting diversity by the
  **semantic distance** between viewpoints. See §2.2: it is also the best defence against
  gaming.

### 2.2 Make the index resistant to gaming

**The limitation.** A platform required to keep the index high can serve formally divergent
but substantively empty content.

* **Explicit adversarial test.** Model a platform maximising engagement **subject to** a
  minimum index, and measure the index attainable with pure label diversity. If the
  constraint is saturable at no cost, the index is unusable as it stands — better to know
  before making it a standard. This is a constrained optimisation problem, hence entirely
  simulable: **no real data is needed to settle it.**
* **Move to Rao's quadratic entropy**, which rewards diversity only in proportion to actual
  semantic distance. Label padding yields no gain.
* **Qualitative sampling** alongside automated measurement, written into the standard.

### 2.3 Design a privacy-preserving audit protocol

* **Randomised response** on viewpoint labels: each client reports its modality with a
  known flip probability. The aggregate distribution's entropy is analytically debiased,
  and the local privacy guarantee is quantified by an $\varepsilon$.
* **Estimate the tail, not the mean.** The proposed regulatory quantity is the *share of
  population below threshold*. A quantile requires less information than a full
  distribution — the privacy constraint is therefore weaker than it appears.
* **Deliverable.** A separate note on the protocol, with an explicit $\varepsilon$ budget.

---

## Priority 3 — Validate the model against reality

### 3.1 Evaluate the algorithm offline on a real dataset

**The limitation.** The algorithm is validated against its own model, with synthetic
relevance and four viewpoints. Its cost in perceived relevance is not evaluated.

**Path — probably the best value/effort in the repository.** Public news-recommendation
datasets (such as MIND, the Microsoft News Dataset) provide both real reading histories and
**editorial categories**, hence viewpoint labels that already exist. One can:

1. compute the real index of observed feeds — the first measurement of the index on
   authentic data;
2. re-rank those feeds with the algorithm;
3. measure the trade-off between index gain and relevance loss (nDCG), and plot the
   **Pareto frontier**.

This would answer the only serious objection a platform can raise: *what does it cost*.
And it requires no privileged data access.

### 3.2 Formulate a falsifiable prediction

**The limitation.** Nothing shows opinion *obeys* this mechanics; the work shows it
*reproduces* observed behaviours.

**Path.** Kramers' law yields a quantitative prediction that the tunnelling analogy did
not: the rate of switching from one extreme to the other varies as
$e^{-\Delta V / k_B T}$. This is **testable** on longitudinal panel data (the same
individuals followed over time): the frequency of extreme-to-extreme switches should depend
exponentially on the inverse of exposure diversity.

A failed prediction would be a result; this is what the edifice most lacks in order to stop
being an analogy.

### 3.3 Systematic sensitivity study

* systematic **parameter sweeps** with confidence intervals;
* **finite-size scaling** for $T_c$ — Binder cumulant rather than susceptibility peak,
  which would give a clean extrapolation to the thermodynamic limit instead of the ±0.25
  tolerance currently required;
* a compute budget in continuous integration, with long simulations moved to a nightly job.

---

## Priority 4 — Extend the model

### 4.1 Co-evolving networks

**The limitation.** Topology is fixed, except through the bubble threshold. Yet people cut
ties and reorganise.

**Path.** Add a homophilic rewiring rule to the agent model: an individual in persistent
disagreement cuts the link and reconnects to a like-minded peer. The question is precise
and worth testing: **is the fragmentation the original reasoning wrongly attributed to
connectivity entirely explained by homophily?** The [audit, point 12](limites.en.md)
asserts this without demonstrating it.

### 4.2 The platform as a strategic actor

**The limitation.** A thermal bath pursues no objective; an algorithm optimises a cost
function. This is where the physical analogy is weakest.

**Path.** Formulate the problem as a **Stackelberg game**: the regulator sets an index
constraint, the platform maximises engagement under it, users respond. The mean-field-game
formalism is the natural continuation of the Fokker-Planck equation already written — the
transition is technical, not conceptual. This is the route that would make the memorandum
genuinely prescriptive: one would know which threshold produces which behaviour from a
rational platform.

### 4.3 Multidimensional, continuous opinions

The agent model already uses two continuous axes. Extend towards bounded-confidence models
(Deffuant, Hegselmann-Krause), whose tolerance parameter is the exact analogue of the bubble
threshold — connecting the work to an established literature rather than an ad hoc model.

---

## Priority 5 — Repository debt

| Item | State | To do |
|---|---|---|
| Theory pages in English | French only, automatic fallback | translate `theorie/*.md`; the English paper already covers the science |
| LaTeX paper | compiled, FR + EN | arXiv submission (`physics.soc-ph`) |
| Figure calibration | regimes chosen by hand | add confidence intervals from §3.3 |
| Agent model | static bubble threshold | make the threshold dynamic, driven by a simulated algorithm, closing the theory on itself |
| Long tests | marked `slow`, run locally | nightly CI job |

---

## If only one thing were done

**§1.1 — estimate $\gamma\alpha/\lambda$ on public data.**

It is the only result that would turn the instability criterion, today a formal inequality,
into an empirical finding. The memorandum recommends prohibiting configurations where
$\gamma\alpha > \lambda$; nobody yet knows whether real platforms sit there. Until that
number exists, the work's most solid recommendation remains a hypothesis.
