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

!!! success "Done — see [Calibration](calibration.en.md)"
    The ratio $\gamma\alpha/\lambda$ lies between **1.5 and 12** across 19 public attention
    episodes (Wikipedia pageviews, `user` agent, pre-registered corpus of 24 subjects), with
    a median of **2.5 to 4.2** depending on the estimator.

    Three findings, two of them negative:

    * the order of magnitude now exists — amplification is two to four times faster than
      forgetting;
    * **the sign criterion is empty**: it holds by construction for any observable episode,
      which forced recommendation 2 of the memorandum to be rewritten as a ceiling on the
      ratio;
    * **the emotional-charge prediction is not supported** ($p \geq 0.13$), and the point
      estimate goes the other way.

    Delivered: `ide.calibration`, `ide.pageviews`, `ide.corpus`,
    `scripts/fetch_pageviews.py`, a versioned cache of 24 series, 40 tests, and
    [notebook 09](notebooks/09_calibration_visibilite.ipynb).

Direct follow-ups, in order of importance:

* **Detect regime changes, not peaks.** → **[done](regimes.en.md)**, with a two-part
  result: detection works and covers the blind spot — 14 changes on the right dates, QAnon and
  health disinformation included — but parameter identification fails on real data, and a
  theoretical limitation bounds it regardless (the ratio is unidentifiable under logistic
  saturation). The **persistence** gap between emotional registers, ×9.2 versus ×2.9, is the
  project's first.
* **Move to sub-daily resolution.** The dominant rejection reason is too short a window: many
  episodes rise in one or two days. Wikimedia publishes hourly series over a limited depth,
  which would suffice to identify what cannot be identified here.
* **Fit non-exponential decay.** The tail of attention is heavier than exponential, producing
  a severe window artefact (rank correlation $-0.94$ between window length and $\lambda$),
  currently worked around with a fixed horizon. A power law or a sum of two exponentials
  would remove it.
* **Extend the corpus.** → **[done](corpus-etendu.en.md)**: 440 subjects derived from
  seventeen Wikipedia categories, replacing the choice of subjects by the choice of categories.
  The answer came, and it is negative — the pilot's persistence gap **does not replicate**
  (×3.04 versus ×2.90, $p = 0.53$), and the switching-rate gap is explained by a ×3.5 audience
  imbalance. The extension also revealed a flaw in its own protocol: category membership is a
  noisy proxy for the register.
* **Annotate the register by hand, blind.** → **[done](annotation.en.md)** across all 440
  subjects, under a pre-registered rubric. Label noise is measured at 40 % of subjects outside
  either register, and it carried the whole switching-rate gap: the odds ratio falls from 3.37
  to **0.93** ($p = 1.00$). The last rescuing hypothesis is eliminated — the gap was not
  diluted, it does not exist. The annotation also revealed a **design flaw**: correctly
  labelled, the two registers barely cover the same kinds of subject.

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
* **Entropy computed on items, not on labels.** ~~Rao's quadratic entropy~~ — discarded in
  §2.2, its constrained optimum being bimodal. What survives of the idea is simpler: project
  the items served onto the catalogue's viewpoints and compute the usual entropy there. It is
  also the best defence against gaming.

### 2.2 Make the index resistant to gaming

!!! failure "Done — and the objection holds: see [Adversarial test](gaming.en.md)"
    The saturability test was carried out by simulation. A platform able to decouple label from
    content obtains an **EDI of 1.000 for zero content diversity**, at zero engagement cost;
    and at half decoupling the constraint retains only **36 %** of its force. **A floor on
    label entropy is not a tenable standard.**

    The replacement first proposed — **Rao's quadratic entropy** — turned out to be defective
    in its turn: it is the intra-list distance, whose constrained optimum is **bimodal**. A Rao
    floor would prescribe polarisation. The retained floor is finally on **position entropy** —
    the index computed on the items served — published with a largest-gap diagnostic.
    [Memorandum recommendation 1](memorandum.en.md) has therefore been revised twice.

**The limitation.** A platform required to keep the index high can serve formally divergent
but substantively empty content.

* **Explicit adversarial test.** Model a platform maximising engagement **subject to** a
  minimum index, and measure the index attainable with pure label diversity. If the
  constraint is saturable at no cost, the index is unusable as it stands — better to know
  before making it a standard. This is a constrained optimisation problem, hence entirely
  simulable: **no real data is needed to settle it.**
* **Move to a measure bearing on the items served**, not on the labels announcing them.
  Label padding yields no gain there. Mind the choice of measure: Rao's quadratic entropy meets
  that criterion and **fails another**, its constrained optimum being bimodal.
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

!!! danger "Three conditions, without which this measurement measures nothing"
    → **[Rank and counterfactual](evaluation.en.md)** established that the protocol above,
    taken at face value, is **wrong**.

    1. diversity must be measured by a **rank-aware divergence** to a declared reference.
       Otherwise a platform complies by **burying** the divergent items: at identical
       composition that yields 10 % more engagement and no point measure sees it;
    2. the cost in relevance must be estimated by **IPS or SNIPS**, never by *replay* on logged
       clicks. Replay is off by **201 % at the median**, up to 851 %, and its sign is not
       guaranteed — so it does not even offer a bound;
    3. the **propensity model**, the **effective sample size** and the **clipping cap** must be
       published with the figure;
    4. the **position-bias severity must be estimated**, not posited — positing $\eta$ by eye
       costs up to 179 % of error — and the **dataset's exploration** must be checked first,
       since it decides whether estimation is possible at all.
       → [Adversarial rank and severity](rang-adverse.en.md)

    Without those three conditions, the announced Pareto frontier would chiefly measure the
    position bias of the platform that produced the data.

!!! failure "And MIND does not meet the fourth condition — this is measured"
    → **[MIND's real exploration](mind.en.md)**. The order recorded in `behaviors.tsv` is
    **shuffled**: the within-feed exchangeability test detects nothing ($z = +0.12$ across
    156,965 feeds, replicated at $z = +0.28$ on the second split) where it would see
    $\eta = 0.02$ at twelve standard deviations.

    Three consequences for this path:

    1. counterfactual estimation of engagement cost — step 3 of the protocol, and the point of
       the exercise — is **impossible on MIND**. Not for want of data, but for want of the
       variable that would identify exposure;
    2. steps 1 and 2 remain feasible: the index of observed feeds and the re-ranking can be
       measured without an exposure model, provided the published cost is stated as a cost in
       **declared** relevance;
    3. choosing the dataset becomes the first task, not the last. The criterion is no longer
       size or the presence of editorial labels, but whether the **served rank is recorded**.

    The check is now tooled: `ide.mind.exchangeability_test` and its power calibration, to be
    run on any public log **before** drawing a figure from it.

!!! success "Two public logs record the rank — the criterion is settled, the path is not"
    → **[Logs that record the rank](rang-servi.en.md)**. **Baidu-ULTR** records display rank: the
    test rejects at $z = -206$, on the right side, and severity is
    $\hat\eta = 1.10 \pm 0.09$. The **Open Bandit Dataset** additionally publishes true
    propensities and contains a randomly served bucket: this repository's IPS estimator recovers
    the value of a never-deployed policy to within **2.5 %**, against **+32 %** for the naive
    estimate.

    Three gains and one blocker:

    * the **criterion for choosing a dataset** is established, and checkable before any
      measurement;
    * **severity can be measured** — but it depends on the surface: ten times weaker on a
      three-thumbnail banner than on a results page. It does not transport;
    * **counterfactual estimators hold** against a ground truth, on an effective sample size of
      1,513 out of 4 million impressions — the figure to publish;
    * **no public dataset carries both the served rank and an interpretable viewpoint label.**
      MIND has categories without rank, Baidu-ULTR rank without labels, the Open Bandit Dataset
      rank with anonymised attributes.

    What remains feasible, replacing the initial protocol:

    1. measure on MIND whatever does not depend on exposure, and say so;
    2. measure on Baidu-ULTR and the Open Bandit Dataset whatever does not depend on viewpoints;
    3. for the rest, **ask for the data** under Article 40 of the DSA — the only route left, and
       a provided-for one.

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

**Have the corpus coded by human annotators.**

Hand annotation of the register — priority 1 in the previous version of this page — was
[carried out across all 440 subjects](annotation.en.md) and settled the question it was meant
to settle. Label noise was massive (40 % of subjects outside either register, only 59.5 %
agreement) and it carried the whole switching-rate gap, which falls from 8.6 % versus 2.7 % to
4.8 % versus 5.1 %. **The gap was not diluted, it does not exist.**

**Four measurements have therefore been made, and none distinguishes the emotional registers**:
the amplification rate, persistence on the pilot then the extended corpus, and the switching
rate. The emotional-charge mechanism $\alpha$ remains without empirical support, and no longer
for want of looking.

The blind double coding was carried out: Fleiss' $\kappa$ of **0.921**, unanimity on 92 % of
subjects, and an unchanged result under consensus coding. The rubric is therefore
**reproducible** — the written instructions suffice to produce a stable coding.

But the three coders are instances of the **same language model**, and agreement among them
necessarily overstates what independent judges would produce. That is the last identifiable
methodological caveat, and the only one that calculation cannot lift: it needs human
annotators.

**What probably should not be done**, by contrast, is a fifth measurement of the same object.
Three quantities drawn from the same aggregate attention series have been tested without
success, and the annotation showed along the way that the design itself is constrained: the two
registers, correctly labelled, barely cover the same kinds of subject. If the mechanism exists,
it must be sought elsewhere — see §3.1 and §3.2.
