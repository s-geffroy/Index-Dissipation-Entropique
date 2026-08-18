# Blind annotation: the protocol

!!! note "Pre-registration"
    This page describes the annotation rubric **before** a single annotation was produced. It
    is published in a commit that precedes `data/annotations.json`, and the repository history
    attests to that. Results will be appended at the end of the page, with nothing above them
    rewritten.

## The question left open

The [extended corpus](corpus-etendu.en.md) measured a null result — persistence does not
differ between emotional registers, ×3.04 versus ×2.90, $p = 0.53$ — but it also exposed the
flaw in its own protocol. Membership of a Wikipedia category is a **noisy proxy** for the
register: "Lil Tay" sits in a hoax category because of a hoax about her death, while the
attention paid to that article is a celebrity's attention.

Label noise introduces no directional bias: it **attracts any gap towards zero**. The null
result is therefore consistent with two readings the data cannot separate:

1. there is no persistence gap between registers;
2. there is one, diluted by approximate labelling.

Annotating the register by hand, subject by subject, settles it — and nothing else does. If
the gap reappears among correctly labelled subjects, dilution was the explanation; if it stays
absent, the absence of an effect was.

## What is annotated

All **440 subjects** of the `data/catalogue.json` manifest, without exception. Annotating a
chosen subset would reopen precisely the selection bias that the category-derived corpus had
closed.

Annotation does not modify the corpus: it adds a column to it. The pool remains the one the
categories produced.

## The question put to each subject

> **What would mobilise public attention on this article?**

Not what the article is about, but which emotion would carry its consultation.

| Register | Definition | Role in the model |
|---|---|---|
| `accusation` | a **wrong, a threat or a deception attributed to someone**: scandal, conspiracy, corruption, atrocity, manipulation | high emotional charge $\alpha$ |
| `discovery` | a **discovery, an exploration or an achievement**: scientific result, space mission, distinction | low $\alpha$ |
| `neither` | **neither of those**: entertainment, celebrity, ordinary institution, catalogue entry, technical concept | outside the comparison |

The third label is what does the work. It removes from the corpus those subjects a category
captured for thematic reasons without their audience belonging to the register — and the rate
at which it is used **directly measures** the label noise the extended corpus could only
diagnose.

### Five tie-breaking rules

Fixed before reading, so that borderline cases are not decided one at a time:

1. **A work of fiction about a scandal is `neither`.** Its audience is a fiction audience.
   This holds for novels, films, series and video games, whatever their subject.
2. **A person is coded by what makes them notable** according to their lede: a science
   laureate is `discovery`, a figure under accusation is `accusation`, a celebrity is
   `neither`.
3. **An atrocity, a massacre or an attack is `accusation`.** The register is that of wrong and
   threat, regardless of whether a formal accusation exists.
4. **A catalogue object or an instrument with no announcement** stays `discovery` if its
   notability rests on what it allowed to be observed, and becomes `neither` if it is merely
   one technical entry among thousands.
5. **An abstract concept naming the wrong itself** — "disinformation", "political corruption"
   — is `accusation`. Rule 1 does not apply: it is not a work.

### Two ancillary dimensions

* the **kind** of subject — event, person, organisation, work, concept, object. It allows a
  later check that the comparison does not pit events against concepts, the confound the
  choice of categories sought to avoid without being able to measure it;
* the **confidence**, binary. Uncertain subjects are not discarded — discarding on sight of
  the result is exactly what pre-registration forbids — but they support a sensitivity check,
  and each carries a written justification.

## Blindness, and what it is worth

The annotation must owe nothing to the result it serves to measure. Three provisions
contribute, and what each guarantees must be stated.

| Provision | What it guarantees |
|---|---|
| the rubric is written **before** the data | verifiable by a third party in the git history |
| the annotator's input is **frozen and fingerprinted** | `data/extracts.json`, whose SHA-256 is recorded in the annotation file: what was read is known |
| pageview series are **not loaded** during annotation | a property of the process, not a cryptographic guarantee — it is declared, not proven |

The material is the article's **lede** — its first section, plain text, truncated to 600
characters. That is what a reader sees before deciding whether to read on, hence the right
granularity for coding what would mobilise their attention.

### What blindness does not cover

**A residual contamination, named.** Six subjects were quoted with their lift on the extended
corpus page — Lil Tay, Watch Dogs, Million Dollar Extreme, The Capture, Mossack Fonseca,
Illuminati (game). The annotator knows them. They are listed in
`ide.annotation.CONTAMINATED`, they are annotated like the rest, and the analysis is repeated
without them as a sensitivity check.

**A single annotator.** There is no inter-rater agreement, hence no measure of coding
reliability. This work corrects label noise; it does not establish that the rubric would be
applied identically by someone else. That is the dispositif's principal limitation, and the
rubric written above is what makes it at least replicable.

**Knowledge of the aggregate result.** The annotator knows the previous measurement was null.
No provision neutralises that; the direction of any resulting bias is undetermined.

## What will be measured

In this order, fixed in advance:

1. **the confusion matrix** category × annotated register — the label noise rate, which is a
   result in itself;
2. **persistence** — median lift of detected regime changes, compared between annotated
   registers by a Mann-Whitney test. This is the primary test;
3. **the switching rate**, with the same traffic controls as on the extended corpus:
   stratification and matching;
4. **three sensitivity checks**: without the contaminated subjects, without the uncertain
   annotations, and with subject kind controlled.

No subject will be removed on sight of its result. Subjects with no detected change will be
reported as such.

---

## Results

!!! success "The question is settled: the gap was not diluted, it does not exist"
    The switching-rate gap **disappears entirely** once the label is corrected: 8.6 % versus
    2.7 % ($p = 0.012$) becomes **4.8 % versus 5.1 %**, odds ratio 0.93, $p = 1.00$.
    Persistence remains null — ×3.04 versus ×2.90, $p = 0.90$ — and the test retains the power
    to detect a gap of the magnitude the pilot corpus announced.

!!! warning "Label noise was massive"
    **Two subjects in five** belong to neither register, and agreement between category and
    annotation reaches only **59.5 %**. The extended corpus's conjecture is confirmed, and its
    magnitude exceeds what it supposed.

!!! danger "And the annotation exposes a design flaw"
    Correctly labelled, the two registers **barely cover the same kinds of subject**: concepts
    and events on one side, objects and people on the other. A comparison built on thematic
    categories therefore also compares kinds of object.

### 1. Label noise, measured

| Category | n | coded accusation | coded discovery | coded neither |
|---|---|---|---|---|
| accusation | 220 | **147** (66.8 %) | 3 (1.4 %) | **70** (31.8 %) |
| discovery | 220 | 0 (0.0 %) | **115** (52.3 %) | **105** (47.7 %) |

Overall agreement: **262/440 = 59.5 %**. Register outright reversed: **3 subjects**.

The noise is **asymmetric**, for a reason of construction: the discovery register drew its
numbers from catalogues of celestial objects, the vast majority of which are technical entries
with no audience. The ten-thousand-byte substance filter did not suffice there.

But outright reversal is **near zero**. The category errs by capturing subjects outside the
register, almost never by assigning the wrong register — exactly the profile of noise that
dilutes without biasing, as the extended corpus had supposed.

### 2. The switching-rate gap evaporates

![Blind annotation: label noise carried the gap](figures/fig12_annotation.png)

/// caption
Label noise; the disappearance of the rate gap once the label is corrected; persistence by
annotated register; and the design flaw the annotation reveals. Figure regenerated by
[notebook 12](notebooks/12_annotation_en_aveugle.ipynb).
///

| Label | accusation | discovery | odds ratio | p |
|---|---|---|---|---|
| category | 19/220 = 8.6 % | 6/220 = 2.7 % | 3.37 | **0.012** |
| **annotation** | 7/147 = 4.8 % | 6/118 = 5.1 % | **0.93** | **1.000** |
| *(neither)* | *12/175 = 6.9 %* | | | |

The odds ratio does not shrink: it **vanishes**, and even reverses very slightly.

The most telling detail is the last row. Discarded subjects switch at **6.9 %**, that is, **more
often than either register**. They were not inert observations: they were what carried the gap
attributed to the accusation register. Of the corpus's five largest lifts, **four** are coded
neither — Lil Tay, Watch Dogs, Million Dollar Extreme, The Capture. Exactly the cases the
extended corpus had flagged as suspect.

**The audience imbalance was itself an effect of the labelling.** Median traffic goes from 39
versus 11 views/day ($p = 5\times10^{-14}$) to 36 versus 26.5 ($p = 2.6\times10^{-3}$):
catalogue entries with no audience were inflating the discovery register. Both of the extended
corpus's controls confirm the absence of a gap — stratum ≥ 47 views/day, OR = 0.45
($p = 0.32$); 116 traffic-matched pairs, McNemar $p = 1.00$.

### 3. Persistence stays null — and the test could have concluded

| Corpus | accusation | discovery | p |
|---|---|---|---|
| pilot, 24 hand-picked subjects | ×9.20 (n = 8) | ×2.90 (n = 6) | 0.081 |
| extended, category label | ×3.04 (n = 21) | ×2.90 (n = 7) | 0.533 |
| **extended, annotated register** | **×3.04** (n = 7) | **×2.90** (n = 7) | **0.902** |
| *without contaminated subjects* | *×2.87* (n = 6) | *×2.90* (n = 7) | *0.945* |
| *without uncertain annotations* | *×3.06* (n = 6) | *×2.90* (n = 5) | *0.931* |
| *comparable traffic stratum* | *×2.69* (n = 5) | *×2.90* (n = 7) | *0.876* |

Fourteen observations, seven a side. This must be said before it is objected — but a
Mann-Whitney test at seven against seven is not blind:

| Ranks of overlap | p |
|---|---|
| 0 — complete separation | 0.0006 |
| 2 | 0.0048 |
| **4** | **0.040** |
| 5 | 0.140 |

The pilot corpus announced interquartile ranges of [4.0, 14.9] versus [2.7, 3.2], that is,
nearly disjoint. **A gap of that magnitude would have been detected here.** The null result is
therefore not a mere want of power.

> **The question the extended corpus left open is settled: the gap was not diluted by the
> labelling, it does not exist.**

### 4. What the annotation reveals about the design

This is the finding neither the pilot nor the extended corpus could make, for want of a
reliable label.

| Kind of subject | accusation | discovery | neither |
|---|---|---|---|
| event | **58** | 6 | 1 |
| concept | **63** | 15 | 21 |
| person | 13 | **39** | 12 |
| object | 0 | **58** | 109 |
| organisation | 11 | 0 | 13 |
| work | 2 | 0 | 19 |

The accusation register is made of **concepts and events**; the discovery register, of
**objects and people**. Only one kind appears on both sides in sufficient number — people,
23.1 % versus 7.7 %, $p = 0.16$ — and it yields nothing conclusive. Concepts **never** switch:
0 of 63 and 0 of 15.

The consequence goes beyond this corpus. **A register comparison built on thematic categories
also compares, and perhaps chiefly, kinds of object.** An encyclopaedic concept — "Corruption
in Mexico" — does not have the attention dynamics of a dated event, independently of any
emotional charge. The extended corpus named this confound without being able to measure it;
here it is measured, and it is severe.

This is a limitation of the **design**, not of the result: it does not resurrect the gap, it
indicates what a fourth protocol should control.

### 5. A note on identification

One fit in twenty-eight now passes every check, including the observability guard added after
the extended corpus. It concerns **"Watch Dogs (video game)"** — a subject coded neither.
Parameter identification therefore remains, in practice, out of reach on this kind of data.

## What this changes for the project

**Four measurements have been made, and none distinguishes the emotional registers**: the
amplification rate ([calibration](calibration.en.md)), persistence on the pilot then the
extended corpus ([regimes](regimes.en.md), [extended corpus](corpus-etendu.en.md)), and the
switching rate. The last rescuing hypothesis — dilution by approximate labelling — is
eliminated.

The **emotional-charge mechanism $\alpha$ remains without empirical support**, and no longer
for want of looking. If that mechanism exists, it does not show in the aggregate attention
dynamics of an encyclopaedia.

What survives is intact and never depended on the register: **dated-switch detection** works,
dates and amplitudes are robust, and they remain the instrument of observation proposed in the
[memorandum](memorandum.en.md).

## Open leads

1. **Have the same corpus annotated by a second coder**, also blind, and publish Cohen's
   $\kappa$. It is the direct and inexpensive complement to this work, and the only
   methodological caveat that remains.
2. **Match on subject kind** as well as on traffic, at corpus construction time. Comparing
   events with events and people with people is now a measured requirement, not a theoretical
   precaution.
3. **Lower the detection threshold by aggregating weekly.** Twenty-eight switches across 440
   subjects leave the primary test at seven observations per register; that is the remaining
   limiting factor.
4. **Look for the effect somewhere other than aggregate attention dynamics.** Three quantities
   have been tested without result; the fourth lead should not be a fourth measurement of the
   same object.

---

*Implementation: `ide.annotation` · Script: `scripts/fetch_extracts.py` ·
[extended corpus](corpus-etendu.en.md) · [roadmap](feuille-de-route.en.md)*
