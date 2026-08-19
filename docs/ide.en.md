# EDI — Exposed Diversity Index

!!! info "Two distinct objects"
    The **index** (IDE in French, EDI in English) is a *metric*, for the regulator. The
    **[algorithm](ade.en.md)** is a *mechanism*, for the platform. The original thread
    used both acronyms interchangeably; the distinction here is deliberate.
    → [audit, point 1](limites.en.md)

!!! success "Renamed — the name now says what is measured"
    The index was first called the "**Entropic Dissipation Index**", after the quantum
    decoherence analogy that started this work. The [audit](limites.en.md) dismantled that
    analogy transfer by transfer: nothing specifically quantum survived it, and what holds —
    free-energy landscape, hysteresis, barrier crossing — belongs to classical statistical
    mechanics. A name pointing at a false analogy is not neutral: it announces something other
    than what the instrument measures.

    The acronym stays **EDI / IDE**. It now reads **Exposed Diversity Index** — the spread of
    the attention **actually served** across the viewpoints of the declared catalogue.
    "Exposed" is not decoration: it is the correction imposed by [adversarial
    rank](rang-adverse.en.md), where a platform certified at 0.70 by a rank-blind measure
    exposes only 0.36.

The historical function is now called `label_diversity_index`, because that is what it
    computes: the diversity of **labels**, looking at neither the items nor the rank.

    **The repository and the site address followed**, in a second step: they were called
    `Index-Dissipation-Entropique`. GitHub redirects `git` operations from the old name to the
    new one, but **not** published page addresses: old
    `s-geffroy.github.io/Index-Dissipation-Entropique/…` links no longer work. That was the
    price of a coherent name, and it was paid knowingly.

## Definition — the retained form

The index is the Shannon entropy of the distribution of **exposed viewpoints**, normalised by
its theoretical maximum:

$$\mathrm{EDI} = \frac{H(q)}{\log_2 k}, \qquad
q_i = \frac{\sum_R w_R \, \mathbb{1}[\text{the item served at rank } R \text{ falls in bin } i]}
{\sum_R w_R}$$

Three choices distinguish it from the entropy one would write spontaneously, and each is the
**consequence of an attack that succeeded**:

| Choice | Why | What happens without it |
|---|---|---|
| $q$ bears on the **items served**, projected onto the bins of the reference catalogue — not on the labels announcing them | a label is chosen, an item is observed | the index reaches **1.000 for zero content diversity**, at zero engagement cost → [adversarial test](gaming.en.md) |
| each rank is weighted by the **attention** it receives, $w_R$ (default $1/R$) | a reader consults the first item far more often than the last | the standard is satisfied by **burying** divergent items: certified at 0.70, a platform exposes only **0.36** → [adversarial rank](rang-adverse.en.md) |
| the denominator $\log_2 k$ is fixed by the **declared catalogue**, not by what the platform serves | comparing two platforms requires the same unit | a perfectly closed feed shows one modality: the denominator degenerates and the index flatters |

| Value | Reading |
|---|---|
| $\mathrm{EDI} = 1$ | served attention is spread evenly across the catalogue's $k$ viewpoints |
| $\mathrm{EDI} \to 0$ | frozen filter bubble: served attention goes to a single viewpoint |

**Associated control quantity.** The gap between the **rank-blind** and the **rank-aware**
measure of the *same* feed is zero for a platform that does not relegate, and grows with burial.
Unlike the repository's other diagnostics, it compares a measure with itself: it is therefore
directly thresholdable. → [adversarial rank](rang-adverse.en.md)

!!! warning "This form has never been measured on a real feed"
    Its engagement cost is quantified **in simulation** — 8.2 % to 18.9 % depending on the
    measure, by exhaustive enumeration of every possible feed — and its floor level remains a
    political decision. No public dataset allows it to be computed: that would require the
    served rank **and** an interpretable viewpoint label, and none carries both.
    → [logs that record the rank](rang-servi.en.md) · [Article 40 request](article-40.en.md)

## The original form, and what it measured

The working thread defined the index on a feed's **labels**, without looking at rank:

$$H_{\text{norm}} = \frac{H(X)}{\log_2 k}$$

That is what `ide.entropy.label_diversity_index` computes, and its name now states its scope.
The form remains useful where rank does not exist — the [agent model](notebooks/08_abm_compas_politique.ipynb)
describes an individual's exposure this way — but it **cannot serve as a standard**: it is the
one the adversarial test defeats.

## Why normalisation is the essential point

Raw entropy is measured in bits, and its value depends on the number of available
modalities. Two platforms with different catalogues would produce incomparable figures.

Normalising by $\log_2 k$ makes the index **dimensionless and bounded**. That is what
makes it usable as a legal instrument: a threshold expressed as a percentage transposes
across platforms; a threshold in bits transposes to nothing.

## The denominator must be imposed

A platform free to choose $k$ would choose the number of modalities it *actually* serves.
Since a perfectly closed feed presents only one modality, the denominator would degenerate
and the index would flatter.

```python
from ide.entropy import label_diversity_index

feed = ["conspiracy"] * 10 + ["factual"] * 10

label_diversity_index(feed)                    # 1.0  — two modalities observed
label_diversity_index(feed, catalogue_size=4)  # 0.5  — four viewpoints available
```

**A regulator must therefore impose a reference $k$.** It is the first parameter a
technical standard has to settle, and also the point where the index becomes a political
object — see [limitations](#limitations).

## What the index detects

The link to the theory is direct: a collapsed index is the signature of a zero local
social temperature, i.e. a frozen state in the Ising sense.
[Notebook 01](notebooks/01_entropie_et_purete.ipynb) shows that the index crosses the
critical threshold **well before** the feed closes completely: a regulator can therefore
observe a freeze *in progress*, not merely once established.

[Notebook 08](notebooks/08_abm_compas_politique.ipynb) measures its response to the
parameter the algorithm actually controls — the bubble threshold:

| Bubble threshold | Mean index | Population in a frozen bubble |
|---|---|---|
| narrow (0.10) | ≈ 0.27 | ≈ 60 % |
| wide (0.80) | ≈ 0.93 | ≈ 0 % |

## Proposed measurement protocol

1. **Window** — a rolling 24 hours of served content.
2. **Unit** — content *served*, not content consulted: the platform is being audited, not
   the user.
3. **Reference catalogue** — $k$ set by the regulator, identical across platforms in the
   same service category.
4. **Aggregation** — computed per user, then aggregated; the regulatory quantity is the
   **share of the population below the critical threshold**, not the mean. A satisfactory
   mean can conceal a wholly enclosed minority.
5. **Threshold** — $H_{\text{critical}}$, to be calibrated empirically. The value of
   $0.4$ used throughout this repository is an **illustrative value**, not a numerical
   recommendation.

## Two metrics not to be confused

The agent model tracks both **polarisation** — mean distance from moderation — and the
**index**. Their divergence is instructive:

* a society can be strongly polarised with a high index: four blocs confronting each
  other while seeing each other;
* it can be weakly polarised with a collapsed index: everyone in agreement.

A regulator should measure the second, because it describes actual cognitive autonomy —
and it is the one the algorithm determines.

## Limitations

Developed further in the [critical audit](limites.en.md).

* **Discretisation into viewpoints is a political choice.** Whoever defines the modalities
  defines the index.
* **The index is gameable, and that was measured.** On the original form the attack is total:
  1.000 for zero content diversity, without giving up a point of engagement. The retained form
  closes that route and burial with it, but **any mandated metric remains a target**: a platform
  can still serve formally divergent, substantively empty items — bin diversity without argument
  diversity. No automatic measure separates the two. → [adversarial test](gaming.en.md)
* **The floor level cannot be deduced from the measurement.** The repository establishes the
  *form* of the standard and its *price*, not its value. Setting 0.60 rather than 0.40 is a
  political decision no computation here settles.
* **A floor on the index is a constraint on what people see.** Defensible, but an
  intervention in public debate — not a neutral technical measure.
* **Privacy.** Measuring individual feeds requires observing what is served to people. A
  credible protocol must be aggregative and differentially private; this repository does
  not yet propose one. → [roadmap §2.3](feuille-de-route.en.md)

---

*Implementation: `ide.entropy.label_diversity_index` ·
[Regulatory memorandum](memorandum.en.md)*
