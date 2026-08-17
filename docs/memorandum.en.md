# Technical and ethical regulatory memorandum

**For the attention of** — digital regulators (national authorities, European Commission)

**Subject** — thermodynamic stabilisation of the informational space and countering the
algorithmic resonance of false information

**Status** — working document, open to critical review. Numerical values quoted are
**illustrative values** from simulations, not numerical recommendations.

---

## Preamble: what this memorandum can and cannot claim

The underlying reasoning is formalised and numerically verified
([models](theorie/fokker-planck.md),
[tests](https://github.com/s-geffroy/Index-Dissipation-Entropique/tree/main/tests)), but
its parameters have **no empirical calibration**. It therefore proposes a *metrological
framework* and *quantities to measure*, not thresholds ready to be written into law.

A second reservation must be stated at the outset. The original thread concluded that
"regulation ceases to be arbitrary censorship and becomes an engineering of stability".
The phrase is appealing and should be treated with suspicion: **an engineering of
stability *is* an intervention in public debate.** It may be legitimate, but it must be
justified as such, with corresponding democratic safeguards — not naturalised by
vocabulary borrowed from thermodynamics.

---

## I. Technical recommendations

The premise common to all three: content verification acts **after** the kinetics have
played out. The models show the phenomenon is governed by structural parameters of the
algorithm, not by content taken item by item. Those parameters are what must be made
observable.

### 1. Impose a floor on the Entropic Dissipation Index

**Measure.** Require very large online platforms to keep the [index](ide.en.md) of
individual feeds above a threshold $H_{\text{critical}}$. Below it, the platform is
required to reinject a "cooling flow" of semantically diverse content.

**Rationale.** A collapsed index is the signature of a zero local social temperature, i.e.
a frozen state in the Ising sense. Below that temperature, the memory of false beliefs
becomes persistent ([notebook 05](notebooks/05_hysteresis_et_contre_champ.ipynb)).

**What the regulator must set itself:**

* the **reference catalogue $k$** — without an imposed denominator, the index flatters the
  most closed feeds;
* the **aggregate quantity** — the share of the population below the threshold, not the
  mean: a satisfactory mean can conceal a wholly enclosed minority;
* the **threshold** itself, which remains to be calibrated empirically.

**What the regulator should not set**: the implementation. The [algorithm](ade.en.md) is
one way to meet the objective, not the only one.

**Reservation to address in the text.** The index is gameable: label diversity can satisfy
a threshold without diversifying the argument. A credible standard must pair automated
measurement with qualitative sampling. → [roadmap §2.2](feuille-de-route.en.md)

### 2. Audit kinetic damping coefficients

**Measure.** Prohibit algorithmic configurations in which a piece of content's
amplification rate exceeds its natural damping rate:

$$\gamma\alpha > \lambda \quad \text{(prohibited configuration)}$$

**Rationale.** Beyond this threshold, effective damping of the feedback loop becomes
negative: the system accumulates energy instead of dissipating it. This is the
informational Larsen effect, and the threshold is sharp
([notebook 06](notebooks/06_resonance_larsen.ipynb)).

**Why this is the most solid recommendation.** It presupposes no malicious intent to be
demonstrated. At uniform gain, a more emotional item crosses the threshold where a factual
one does not: the bias is **mechanical**. Auditing $\gamma$ is therefore more relevant —
and more enforceable — than auditing editorial intent.

**Operational difficulty.** $\lambda$ and $\alpha$ are not directly legible in platform
code. Estimating them requires an inference protocol from visibility time series, which
remains to be built. → [roadmap §1.1](feuille-de-route.en.md)

### 3. Throttle super-spreader reach on kinetic anomaly

**Measure.** Impose dynamic limits on cascading share reach as soon as a propagation
anomaly is detected.

**Rationale — and an important correction.** The original reasoning held that the
small-world structure of social networks makes consensus impossible. This is measurably
false: consensus time grows as $N^2$ on a local network and only as $N$ in mean field —
**global connectivity accelerates convergence**
([notebook 03](notebooks/03_voter_consensus_et_taille.ipynb),
[audit, point 12](limites.en.md)).

What fragments is not link density but the **directional bias** of algorithmic
micro-fields, together with the homophily that compartments the graph.

This recommendation therefore stands as an **emergency measure** — slowing a cascade buys
time for verification — but should not be presented as the structural remedy.
Recommendations 1 and 2 are better supported.

---

## II. Ethical and behavioural recommendations

### 1. Neutralise the "engagement tax"

Treat the maximisation of retention time through the exploitation of negative emotions as
a **societal nuisance**, on the model of environmental externalities, and create fiscal or
legal incentives to decouple the business model from permanent friction.

### 2. Transparency of social-potential assessment

Guarantee every citizen's right to know the shape of the social potential they are subject
to: a legible gauge showing the diversity level of their own feed, and the extent to which
their decision space has been curved by algorithmic micro-fields.

**Reservation.** This right requires measuring individual feeds. The protocol must be
aggregative and differentially private, or transparency is paid for in surveillance.

### 3. A right to thermal noise and algorithmic forgetting

Establish a principle of **bias disconnection**: the ability to enable, in one click, a
"fluid exploration" mode that artificially raises social temperature and disables
collaborative filtering, breaking the hysteresis sustained by one's history.

**A measured nuance, and it matters.** Noise is not monotonically beneficial: beyond a
certain level, exposure diversity degrades again
([notebook 08](notebooks/08_abm_compas_politique.ipynb)). The original thread anticipated
this — "injecting thermal noise permanently makes society chaotic and illegible". It is
therefore not the quantity of noise that matters but its **dosage**, which argues for an
on-demand mode and cyclical annealing rather than permanent noise.

---

## III. Control framework: a metrology of the informational space

```
[Platform data feeds]
          │
          ▼
[Regulator's Fokker-Planck simulator]
          │
          ├──▶ unimodal distribution, centred  ─────▶ compliant
          │
          └──▶ bimodal distribution with no
               central moderation zone         ─────▶ alert, then DSA sanction
```

### "Phase scanners"

Rather than counting reports of false information — a lagging and gameable indicator — the
regulator simulates the state of opinion from distributions supplied via platform APIs, and
detects **phase transitions**.

The relevant quantity is not the number of problematic items but the **shape of the
distribution**: sharp bimodality with no central moderation zone characterises a degraded
informational space, independently of the content of any single message.

### What is missing to make this operational

| Gap | Nature |
|---|---|
| calibration of $J$, $T$, $\gamma$, $\alpha$ on real data | no procedure proposed |
| privacy-preserving audit protocol | not designed |
| normative definition of the viewpoint catalogue $k$ | political choice unresolved |
| resistance of the index to gaming | not studied |
| cost in perceived relevance of an index floor | not evaluated |

This memorandum should therefore be read as a **framework to harden**, not a ready-to-use
mechanism. Its contribution is to name measurable quantities where regulatory debate still
reasons in volumes of removed content. The [roadmap](feuille-de-route.en.md) sets out how
each gap could be closed.

---

*See also: [critical audit and limitations](limites.en.md) ·
[roadmap](feuille-de-route.en.md) · [call for review](relecture.md)*
