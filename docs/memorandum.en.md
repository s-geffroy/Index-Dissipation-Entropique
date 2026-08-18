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
[tests](https://github.com/s-geffroy/Index-Dissipation-Entropique/tree/main/tests)). Exactly
one of its quantities has been measured on real data — the ratio $\gamma\alpha/\lambda$,
[estimated](calibration.en.md) on public attention series; the other parameters are not
calibrated. It therefore proposes a *metrological framework* and *quantities to measure*, not
thresholds ready to be written into law.

That attempt at measurement in fact forced **recommendation 2 to be rewritten twice**, and then
to conclude that the quantity it targeted is not one a regulator can establish. An argument for
measuring before legislating, not for taking the framework as settled.

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

!!! failure "Recommendation revised after the adversarial test — the floor must be on Rao"
    The reservation below, left open, was put to the test by simulation
    ([adversarial test](gaming.en.md)), and it holds **beyond what was supposed**: a platform
    able to decouple label from content obtains an **EDI of 1.000 — full marks — for strictly
    zero content diversity**, without giving up a point of engagement. It need not even go
    that far: at half decoupling, the constraint retains only **36 %** of its force.

    **A floor on label entropy is therefore not a tenable standard.** The measurement must be
    made on the **items** served, not on the labels announcing them.

    !!! danger "Corrected a second time — not on Rao's entropy"
        This recommendation first named **Rao's quadratic entropy**. That was an error, and of
        the worst kind: Rao's entropy is the *intra-list distance*, whose constrained optimum
        is **bimodal**. It awards 1.000 to a feed serving the two edges and nothing between,
        against 0.750 to a spread feed — **a Rao floor would prescribe polarisation.**

    **The retained floor is on position entropy**: the Shannon entropy of the items served,
    projected onto the bins of the reference catalogue. It is the index with one substitution
    — items instead of labels — hence the same reading, the same scale, and a lower compliance
    cost than Rao's entropy.

    **The largest gap is published beside the floor.** Entropy is *nominal*: it counts
    occupied viewpoints without seeing their spacing. The diagnostic covers what it misses,
    and it is what makes bimodality observable.

    !!! danger "And the measure must be rank-aware"
        A measure bearing on a feed's composition alone is satisfied by **burying** the
        divergent items at the bottom of the ranking: at identical composition that yields
        10 % more engagement without moving the measure by a point. The floor must therefore
        bear on a distribution **weighted by the attention each rank receives**.
        → [Rank and counterfactual](evaluation.en.md)

        **Its price is quantified**: the engagement cost doubles — from 8.2 % to 18.9 % for
        Rao's entropy, from 10.7 % to 20.9 % for position entropy. A platform certified at
        0.70 by a blind measure in fact exposes only 0.36.
        → [Adversarial rank and severity](rang-adverse.en.md)

        **Associated control quantity**: the gap between the blind and the rank-aware measure
        of the **same** feed. Unlike the excess signature, it compares a measure with itself
        and is therefore directly thresholdable — it is zero for a platform that does not
        relegate.

    What the regulator must then fix in addition: the **reference catalogue**, which serves as
    both grid and unit. It is the same political question as the choice of $k$, moved one step
    along.

    **Complementary provision.** Publish both indices on the same feed and monitor the
    **excess signature** — the EDI − Rao gap relative to what an honest catalogue would show
    at the same index. It is zero for an honest platform and grows with gaming.
    → [Adversarial test of the index](gaming.en.md)

    **Successor to be worked out.** A *target proximity* — divergence between the exposure
    served and a distribution the regulator publishes — is the only measure tested that makes
    the intended shape of exposure explicit rather than assumed. It is also the entry point to
    the field's normative-diversity metrics.

**Original reservation, kept on record.** The index is gameable: label diversity can satisfy
a threshold without diversifying the argument. A credible standard must pair automated
measurement with qualitative sampling.

### 2. Cap the amplification-to-damping ratio

!!! warning "Recommendation revised after measurement"
    This recommendation was originally written as a prohibition on configurations where
    $\gamma\alpha > \lambda$. The [empirical calibration](calibration.en.md) shows that
    formulation to be **inapplicable**: the ratio exceeds 1 in all 19 measured episodes,
    under every estimator. This follows logically — an observable attention episode
    necessarily went through a growth phase. Checking the sign tells you nothing.

**Measure.** Impose a **ceiling** on the ratio between a piece of content's amplification
rate and its natural damping rate:

$$\frac{\gamma\alpha}{\lambda} \leq \rho_{\max}$$

**Rationale.** Beyond $\gamma\alpha = \lambda$, effective damping of the feedback loop
becomes negative: the system accumulates energy instead of dissipating it
([notebook 06](notebooks/06_resonance_larsen.ipynb)). That regime is the norm, not the
exception — measurement places the information ecosystem between **1.5 and 12**, median
**2.5 to 4.2** ([notebook 09](notebooks/09_calibration_visibilite.ipynb)). The relevant
regulatory quantity is therefore the **margin**, not the crossing.

**Why this remains the most solid recommendation.** It presupposes no malicious intent to be
demonstrated. At uniform gain, a more emotional item should cross the threshold where a
factual one does not: the bias would be **mechanical**, and auditing $\gamma$ more
enforceable than auditing editorial intent.

**A caveat for the record.** That last point is **not supported by the data**: the
measurement detects no difference in ratio between accusation content and scientific
announcements ($p \geq 0.13$). The mechanical argument remains theoretically sound, but a
regulator must not present it as demonstrated.

**Operational difficulties, now quantified.**

* $\rho_{\max}$ is not determined by theory. The measurement provides a descriptive
  reference, not a normative threshold.
* The estimated value is **method-dependent**: the median varies by a factor of 1.7 with the
  fitting window. A threshold anchored to a single value would be contestable; the estimation
  protocol must be standardised alongside the threshold.
* The available measurement concerns an **ecosystem gain**, not a platform's internal
  $\gamma$. Reaching the latter requires DSA Article 40 access.
* The peak method is **blind to installed regimes**. A second method
  [detects them well](regimes.en.md) but **does not identify** the ratio on those cases — and a
  theoretical limitation compounds this: under logistic saturation, $\gamma\alpha/\lambda$ is
  unidentifiable regardless of data quality.

!!! tip "A replacement indicator does measure — but proves nothing"
    Regime-change detection yields two robust quantities the amplification ratio does not:
    **the date of the switch** and **the lift of the plateau**. They are measurable on public
    data, without a form assumption, and they address what a regulator actually seeks to
    establish: not the speed of a flare-up, but how long a false belief stays installed.

    **They do not discriminate between emotional registers, however.** A first measurement on
    twenty-four subjects suggested a ×9.2 versus ×2.9 gap; verification on
    [440 category-derived subjects](corpus-etendu.en.md) reduced it to ×3.04 versus ×2.90
    ($p = 0.53$), and showed the switching-rate gap to be an audience effect.
    [Blind annotation](annotation.en.md) of the register closed the question: with the label
    corrected, the switching rate goes from 8.6 % versus 2.7 % to **4.8 % versus 5.1 %**
    ($p = 1.00$). The gap was not diluted by approximate labelling, it does not exist.

    A regulator can therefore use it to **observe** a durable switch, not to establish that a
    category of content produces more of them.
    → [Regime changes](regimes.en.md) · [Extended corpus](corpus-etendu.en.md) ·
    [Blind annotation](annotation.en.md)

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

### What a log must contain to be auditable

The DSA opens platform data to researchers and regulators (Article 40). This section states what
that access must require if it is not to be empty.

**The served rank, or failing that the exposure propensity.** A click depends on two things: the
item's relevance and the exposure it was given. Without the rank the two stay conflated, and no
counterfactual evaluation of a re-ranking is possible — not by the regulator, nor by the platform
itself. Publishing that column reveals nothing of the ranking code: it says *where* an item was
shown, not *why*.

**What anonymisation must not destroy.** Shuffling the display order before publication does not
make a log unbiased: the clicks were produced under the real order and carry its bias in full.
The shuffle removes only the variable that would allow correction — it makes the log
**uncorrectable**. That is the case of [MIND](mind.en.md), the reference dataset for news
recommendation. → [MIND's real exploration](mind.en.md)

**Acceptance check.** Before any audit resting on a supplied log, run the **within-feed
exchangeability test**: given the feed, are clicks distributed independently of the recorded
position? The test is exact, and its power calibration states what it would have detected. A log
that "passes" it — in the sense that its order is indistinguishable from a shuffle — is not
auditable counterfactually, and it is better to establish that before the audit than after.

**Why this check is not optional.** Without it, exposure estimation does not halt: it returns a
figure. On MIND the severity estimator accepts the dataset, declares itself identifiable and
produces **five incompatible severities** depending on a mere nuisance parameter, from $-0.13$ to
$+0.25$, each with a standard error below 0.007. An audit resting on any one of them would be
indistinguishable from a correct one.

### What is missing to make this operational

| Gap | Nature |
|---|---|
| calibration of $\gamma\alpha/\lambda$ | **done** — [measured](calibration.en.md) between 1.5 and 12 across 19 public episodes, with its caveats |
| calibration of $J$ and $T$ on real data | no procedure proposed |
| normative value of $\rho_{\max}$ | the measurement describes, it does not prescribe |
| estimating a platform's **internal** $\gamma$ | requires DSA Article 40 access |
| detection of **installed** disinformation regimes | **done** — [14 dated changes](regimes.en.md), QAnon and health disinformation included |
| identification of $\rho$ on installed regimes | fails: real scatter four times too high, and unidentifiable under logistic saturation |
| calibration of the **persistence** indicator | **done, and negative** — the pilot corpus's ×9.2 versus ×2.9 gap failed to replicate across [440 subjects](corpus-etendu.en.md), and [blind annotation](annotation.en.md) eliminated it for good. The indicator observes; it does not discriminate |
| existence of an **emotional-charge** effect $\alpha$ | **four measurements, no effect**: amplification, persistence on the pilot then the extended corpus, switching rate |
| privacy-preserving audit protocol | not designed |
| normative definition of the viewpoint catalogue $k$ | political choice unresolved |
| resistance of the index to gaming | **done, and negative** — an EDI floor saturates at zero cost ([adversarial test](gaming.en.md)); the measurement must be made on Rao's entropy |
| calibration of the **position-entropy** floor | no procedure — the adversarial test establishes the form of the standard, not its level |
| choice of the **exposure target** | an unsettled political question, which a divergence measure makes explicit instead of burying |
| cost in perceived relevance of an index floor | not evaluated |
| counterfactual evaluation on a public dataset | **done, and negative** — [MIND](mind.en.md) does not retain display rank: exposure is not identifiable there, and estimating it anyway returns five incompatible severities |
| requiring the **served rank** in supplied logs | proposed here, not instrumented on the regulator's side |

This memorandum should therefore be read as a **framework to harden**, not a ready-to-use
mechanism. Its contribution is to name measurable quantities where regulatory debate still
reasons in volumes of removed content. The [roadmap](feuille-de-route.en.md) sets out how
each gap could be closed.

---

*See also: [critical audit and limitations](limites.en.md) ·
[roadmap](feuille-de-route.en.md) · [call for review](relecture.md)*
