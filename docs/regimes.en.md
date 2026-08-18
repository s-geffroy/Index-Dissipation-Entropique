# Regime changes: reaching the disinformation that installs itself

!!! success "Detection works, and covers the blind spot"
    **14 regime changes** detected across the corpus, on the right dates — the Benalla affair
    on 20 July 2018, the Pegasus revelations in July 2021, the LIGO announcement in February
    2016. And crucially in the subjects that [peak calibration](calibration.en.md) missed:
    **QAnon, COVID-19 misinformation, vaccine hesitancy**.

!!! failure "Identification fails"
    **0 of the 14** yields usable parameters. The median residual scatter of the real series
    is **0.63**, whereas the relative uncertainty on $\gamma\alpha/\lambda$ already reaches
    77 % at 0.15. Parameters are **refused** rather than reported with an illusory error bar.

!!! failure "Since disproved — the persistence gap does not replicate"
    The ×9.2 versus ×2.9 gap reported below was tested on
    [440 category-derived subjects](corpus-etendu.en.md): it becomes ×3.04 versus ×2.90,
    $p = 0.53$. It was an **artefact of hand-selecting** the twenty-four subjects of this pilot
    corpus, which contained the best-known conspiracy theories. The section is kept as written,
    with this warning.

    [Blind annotation](annotation.en.md) of the register then eliminated the last rescuing
    hypothesis: the gap was not diluted by approximate labelling, it does not exist.

!!! danger "And a theoretical limitation dominates both"
    The identifiability of $\gamma\alpha/\lambda$ from a regime change **depends on the
    assumed saturation form**. Under logistic saturation it does not exist: two parameter
    triples with ratios of 5.0 and 1.7 produce exactly the same curve. The ratio is therefore
    not a quantity the data determine.

---

## The problem peak calibration left open

Eleven of the twenty-four corpus subjects had yielded no exploitable episode — and these were
the archetypal cases. Their attention does not form a spike followed by decay: it **shifts
level and settles**. The rolling baseline follows that plateau, so the prominence criterion is
never met.

A model of polarisation that only measures passing flare-ups does not reach its object.

## Why the peak estimator cannot be reused

Peak identification rested on two slopes: a rise at $\gamma\alpha - \lambda$, a decay at
$\lambda$.

In an installed regime **the decay does not exist**. The system sits at its fixed point, where
by definition $\gamma\alpha\,\sigma(V^*) = \lambda$: the plateau level alone says nothing, and
there is no second slope.

The information lies in the **shape of the transition**, which traverses the whole saturation
range and constrains all three parameters at once.

## An exact identification, and its fragility

Setting $y = \dot W/W$ and $x = W^2$, an **exact** rearrangement of the equation yields a form
linear in three coefficients:

$$y = A - B\,xy - C\,x
  \qquad A = \gamma\alpha - \lambda, \quad B = \frac{1}{W_{\text{sat}}^2},
  \quad C = \frac{\lambda}{W_{\text{sat}}^2}$$

hence $\lambda = C/B$ and $\gamma\alpha/\lambda = 1 + AB/C$. The regression recovers all three
parameters to machine precision, including for $\rho = 40$.

Yet it is unusable as such: $y$ appears both as the response and inside the regressor $-xy$,
and it must be obtained by differentiating noisy data. At 10 % multiplicative noise, the
estimate of $\rho$ collapsed from 5.0 to 1.7.

**The retained estimator therefore uses no derivative**: it integrates the equation and fits
the trajectory in log space, the linear form serving only as initialisation.

The fit is performed on the **observed** series $V = V_{\text{before}} + W$, not on the excess
alone. The difference is decisive: early in the transition, $W$ is a small difference between
two noisy quantities — precisely the phase that constrains $\gamma\alpha - \lambda$.

## The theoretical limitation

Under the model's saturation, $\sigma = 1/(1+(W/W_{\text{sat}})^2)$, the three parameters shape
the curve in three distinct ways and are separable.

Under **logistic** saturation, $\sigma = 1 - W/W_{\text{sat}}$, the equation becomes

$$\dot W = (\gamma\alpha - \lambda)\,W\left(1 - \frac{W}{K}\right),
  \qquad K = W_{\text{sat}}\left(1 - \frac{\lambda}{\gamma\alpha}\right)$$

The trajectory then depends on only **two** combinations of the three parameters. The ratio is
structurally unidentifiable there, and no measurement precision will change that.

> **The identifiability of $\gamma\alpha/\lambda$ from a regime change is not a property of
> the data: it is an assumption about the saturation form.**

Both forms are therefore fitted side by side, and `RegimeShift.is_form_identified` flags cases
where the data do not decide.

## Detection: what works

Binary segmentation on the **logarithms** — audience evolves multiplicatively, and a doubling
must count as much at a thousand as at a hundred thousand views a day. The split that most
reduces the quadratic cost is retained if it exceeds a penalty, which avoids fixing a number
of change points in advance.

Three validations before calling something a regime change:

| Criterion | Purpose |
|---|---|
| **sustained** over 180 days | this is what separates a regime from a peak: a peak falls back |
| **lift** of at least ×2 | a level shift, not a fluctuation |
| **prior regime** ≥ 50 views/day | there must be a prior regime for it to change; a series going from 2 to 300 views describes an article that has just been written |

Three further precautions proved necessary in practice:

* **weekly periodicity** is removed first. It is a systematic effect of 20–30 % amplitude, and
  residual scatter directly drives the uncertainty;
* **the change-point position is not reliable** for delimiting the fitting window: mean-shift
  segmentation places the break near the middle of a gradual rise. The onset is therefore
  located separately, at the first durable crossing of 5 % of the lift;
* a gradual rise is **cut into a staircase** by the segmentation. Breaks belonging to one
  staircase describe a single regime change and are deduplicated.

## Results

![Regime-change detection on public pageview series](figures/fig10_regimes.png)

/// caption
QAnon and its two dated switches; the demonstration of unidentifiability under logistic
saturation; persistence by emotional register; and where the real series sit relative to
attainable precision. Figure regenerated by
[notebook 10](notebooks/10_changement_de_regime.ipynb).
///

### The dates are right

The most telling validation: with no date supplied to it, detection recovers datable events.

| Subject | Detected date | Event | Lift |
|---|---|---|---|
| QAnon | 31 March 2018 | emergence of the movement | ×44 |
| Pizzagate | 16 March 2020 | pandemic-era revival | ×18 |
| Gilets jaunes | 3 May 2019 | — | ×14 |
| QAnon | 9 March 2020 | pandemic switch | ×12 |
| Pegasus | 17 July 2021 | *Pegasus Project* revelations | ×4.4 |
| Benalla affair | 20 July 2018 | the affair breaks | ×2.8 |
| OSIRIS-REx | 12 June 2016 | — | ×3.3 |
| LIGO | 9 January 2016 | leaks preceding the announcement | ×3.2 |
| James Webb telescope | 27 September 2021 | run-up to launch | ×2.9 |
| Gravitational waves | 1 February 2016 | detection announcement | ×2.7 |
| Event Horizon Telescope | 1 April 2019 | first black hole image | ×2.4 |

No false positives on stationary noise, no peak accepted, no article creation retained.

### A difference between registers, for the first time in the project

[Peak calibration](calibration.en.md) found **no** difference between accusation content and
scientific announcements: the amplification ratio was indistinguishable, and the point estimate
even went the wrong way.

**Persistence** says otherwise:

| Register | n | median lift | IQR |
|---|---|---|---|
| accusation | 8 | **×9.2** | [4.0, 14.9] |
| discovery | 6 | **×2.9** | [2.7, 3.2] |

Mann-Whitney: $p = 0.081$.

This is not conclusive — fourteen observations, threshold not crossed — and a further caveat
applies: the discovery-register changes all sit just above the detection threshold (×2.4 to
×3.3), suggesting some are slow-decaying peaks rather than genuine regimes.

But the direction is the one the model predicts, the gap is clear, and it concerns a quantity
the project had not yet measured:

> **It is not the amplification rate that distinguishes emotional registers, it is how long
> attention stays captured.**

!!! failure "This conclusion is disproved"
    Across [440 subjects](corpus-etendu.en.md) the gap becomes ×3.04 versus ×2.90
    ($p = 0.53$). The wording above is kept on record: it illustrates what a hand-picked
    selection of twenty-four subjects can suggest.

### Identification fails, and why

None of the fourteen changes yields usable parameters.

This is not an implementation defect: recovery is **exact** on a clean trajectory, including
for $\rho = 40$. It is a mismatch between a three-parameter model and the real noise of
attention series, which carry successive media bumps superimposed on the trend.

| residual scatter | relative uncertainty on $\rho$ |
|---|---|
| 0.05 | 24 % |
| 0.10 | 53 % |
| 0.15 — *acceptance threshold* | 77 % |
| 0.25 | 135 % |
| **0.63 — real series** | out of reach |

The refusal is a deliberate choice. An earlier version of the module tolerated a scatter of
0.30 and produced values such as $\lambda = 4.4$ per day — a collective memory of five hours —
or $\rho = 139$. Those figures had the appearance of results.

## What this changes for the memorandum

[Recommendation 2](memorandum.en.md) capped $\gamma\alpha/\lambda$. That formulation assumed
the ratio measurable. It is neither measurable on installed regimes, nor independent of an
assumption about the saturation form.

By contrast, **two quantities are well measured**: the date of the switch and the lift of the
plateau. A regulatory framework anchored to those would be enforceable where a threshold on
$\rho$ is not, and it would address what a regulator actually seeks to establish: not the speed
of a flare-up, but **how long a false belief stays installed**.

They do **not** distinguish emotional registers, however: verification on
[440 subjects](corpus-etendu.en.md) and then [blind annotation](annotation.en.md) established
that. They are instruments of observation, not
proof of a mechanism.

## Open leads

1. **Reduce the model rather than improve the fit.** Two parameters identifiable without a form
   assumption — initial growth rate and plateau level — are worth more than three of which one
   is not determined by the data.
2. **A less noisy observable.** Daily pageview scatter is irreducible; weekly series, or a
   measure of exposure rather than consultation, would change the order of magnitude.
3. ~~**Extend the corpus to persistence.**~~ → **done**, and the gap failed to replicate
   ([extended corpus](corpus-etendu.en.md)), then was eliminated for good by
   [blind annotation](annotation.en.md) of the register.
4. **Check that "discovery" regimes really are regimes** by lengthening the required sustain
   period.

---

*Implementation: `ide.regime` · Notebook:
[10 — Regime change](notebooks/10_changement_de_regime.ipynb) ·
[peak calibration](calibration.en.md) · [roadmap](feuille-de-route.en.md)*
