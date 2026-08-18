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

!!! info "To come"
    This section will be completed after annotation. The rubric above will not be modified: if
    it had to be, the rubric version would be incremented and the annotation redone.

---

*Implementation: `ide.annotation` · Script: `scripts/fetch_extracts.py` ·
[extended corpus](corpus-etendu.en.md) · [roadmap](feuille-de-route.en.md)*
