# Data access request under Article 40 of the DSA

!!! info "What this document is, and is not"
    It is a **template ready to file**, not a filed request. Article 40(8)(a) DSA reserves
    *vetted researcher* status to persons **affiliated to a research organisation** within the
    meaning of Article 2(1) of Directive (EU) 2019/790. This repository, kept by one person, is
    **not eligible as it stands**: the request below is written to be filed by an organisation
    that meets the conditions, and the parts to complete are in brackets.

!!! success "What makes this request unusual"
    It asks for **no logs** and **no personal data**. It asks for **four aggregate tables**,
    which [notebook 18](notebooks/18_demande_article_40.ipynb) verifies are sufficient to
    recompute **identically** the four measurements that decide everything — and which weigh, on
    a real log, **95 times fewer rows** than the log itself.

---

## The reasoning that leads to this request

Three public datasets have been measured, and none permits the announced evaluation:

* [MIND](mind.en.md) carries editorial categories but **not the rank** — its recorded order is
  indistinguishable from a shuffle ($z = +0.12$);
* [Baidu-ULTR](rang-servi.en.md) carries the rank ($z = -206$) but **no usable label**;
* the [Open Bandit Dataset](rang-servi.en.md) carries rank, true propensity and a random bucket,
  but its item attributes are **anonymised**.

Article 40 remains. And a request is admissible only if it is **necessary and proportionate** —
Article 40(8)(e) DSA, Article 8(d) of Delegated Regulation (EU) 2025/2050, in force since
29 October 2025. "Give us your logs" is neither: it demands personal data the analysis has no
need of, and it hands the platform the easiest ground for refusal — service security and trade
secrets, Article 40(5).

Hence the form adopted: **a specification, not an access**.

---

## I. Identification and legal basis

| | |
|---|---|
| **Applicant** | [RESEARCH ORGANISATION], within the meaning of Art. 2(1) of Directive (EU) 2019/790 |
| **Principal researcher** | [NAME], [POSITION] |
| **Data provider** | [PLATFORM], designated a VLOP on [DATE] |
| **Digital Services Coordinator of establishment** | [AUTHORITY] — for most VLOPs, the Irish authority |
| **Route** | Article 40(4) of Regulation (EU) 2022/2065, procedure of Delegated Regulation (EU) 2025/2050 |
| **Filing** | DSA data access portal (Arts. 3 and 5 of the Delegated Regulation) |

**On the route chosen.** Article 40(12) — access to **publicly accessible data**, open to
researchers affiliated to not-for-profit bodies — does not fit: the data requested here are not
publicly accessible, since it is precisely the served order and the exposure that public
datasets lack. Route 40(4) is therefore the only one.

## II. Subject of the research (Art. 8(f) of the Delegated Regulation)

The subject is the detection and measurement of a systemic risk under **Article 34(1)(c)** DSA —
negative effects on civic discourse — in a measurable form:

> A platform bound by a diversity floor bearing on the **composition** of its feeds can comply
> by **burying** divergent items at ranks nobody reads. The composition stays compliant and the
> actual exposure does not.

This repository established the point by exhaustive enumeration: a platform certified at 0.70 by
a rank-blind measure exposes only **0.36** of real diversity, and closing the loophole doubles
the engagement cost ([adversarial rank](rang-adverse.en.md)). It also established that the
correction requires knowing exposure, hence the **served rank**, and that ignoring it makes the
evaluation vacuous by construction ([MIND](mind.en.md)).

The research requested consists of measuring, on the feeds actually served by [PLATFORM]:

1. the gap between **composed diversity** and **exposed diversity**, by period;
2. the **position-bias severity** proper to this surface, rather than transported from another —
   the study measured 1.10 on a search results page and 0.04 to 0.11 on a three-thumbnail
   banner, an order of magnitude apart;
3. the **engagement cost** of a re-ranking that respects a rank-aware floor, estimated by
   importance weighting rather than by replay, whose measured median error reaches 201 %.

## III. Data requested (Art. 8(c) of the Delegated Regulation)

Four aggregate tables, in CSV or Parquet, for the period [PERIOD] and the market [MEMBER STATE].

**Table 1 — feed profiles**

| Column | Type | Description |
|---|---|---|
| `profile` | integer | identifier of the rank profile (see table 1 bis) |
| `feed_clicks` | integer | number of items clicked in the feed |
| `feeds` | integer | number of matching feeds |

**Table 1 bis — profile definitions**: `profile`, `rank` — the list of ranks each profile
occupies. Indexing by feed **length** alone would be shorter and **wrong** as soon as a surface
skips ranks, which a results page does.

**Table 2 — clicks by rank**

| Column | Type | Description |
|---|---|---|
| `profile` | integer | profile of the feed |
| `feed_clicks` | integer | number of items clicked in the feed |
| `rank` | integer | served rank |
| `clicks` | integer | clicks observed at that rank |

The second key is not an ornament: without it, feeds where *everything* was clicked — which
constrain nothing — cannot be excluded from the computation.

**Table 3 — (item, rank) cells**

| Column | Type | Description |
|---|---|---|
| `item` | pseudonymous identifier, stable over the period | item served |
| `rank` | integer | served rank |
| `impressions` | integer | number of displays |
| `clicks` | integer | clicks observed |
| `propensity` | real, **optional** | probability of service, if the platform knows it |

**Table 4 — exposure by viewpoint**

| Column | Type | Description |
|---|---|---|
| `rank` | integer | served rank |
| `viewpoint` | label | category of the **reference catalogue declared by the regulator** |
| `impressions` | integer | number of displays |
| `clicks` | integer | clicks observed |

The viewpoint catalogue is a **decision of the regulator**, not of the platform nor of the
researcher: it is the political discretisation that the [critical audit](limites.en.md)
identifies as the chief reservation on using the index. This request concerns its application,
not its choice.

## IV. Necessity and proportionality (Art. 8(d) of the Delegated Regulation)

**What these tables allow — and nothing more.**

| Measurement | Tables needed |
|---|---|
| exchangeability test — is the log even correctable? | 1, 1 bis, 2 |
| position-bias severity $\eta$ | 3 |
| counterfactual estimation and effective sample size | 3, with propensities |
| composed and exposed diversity, burial gap | 4 |

**What is verified, not asserted.** [Notebook 18](notebooks/18_demande_article_40.ipynb)
recomputes these measurements twice — directly on a complete log, then on the tables alone — and
publishes the gap. It is $3 \times 10^{-12}$ for the exchangeability test and **exactly zero**
for severity. The code that consumes the tables is
[`ide.aggregates`](https://github.com/s-geffroy/Indice-Diversite-Exposee/blob/main/src/ide/aggregates.py),
and eleven tests lock it.

**What it weighs.** On Baidu-ULTR, 524,164 documents served yield **5,543 rows** requested, a
ratio of **95**. On MIND, 5,843,444 items served yield **57,906** rows, ratio **101**.

**What is not requested**: no reader identifier, no browsing sequence, no content, no text, no
ranking parameter, no model. A feed appears in these tables only by its **shape** and by the
number of clicks it received.

**Consequence for Article 40(5).** A platform may request amendment of a request if disclosure
would create security vulnerabilities or reveal trade secrets. Counts by rank and by declared
viewpoint reveal neither the ranking, nor its parameters, nor the items: they say **what was
exposed**, not how the platform decided to expose it.

## V. Risks, confidentiality and data protection (Art. 8(e))

**Personal data.** The tables requested contain none: the smallest unit is the cell, and no row
designates a reader. The processing therefore does not involve a communication of personal data,
which removes the request's principal risk and the platform's principal ground for objection.

**Confidentiality threshold.** The request proposes a suppression threshold of [THRESHOLD]
impressions per cell, and asks that it be **published with the data**. This threshold is not
neutral, and its effect is measured rather than assumed: on Baidu-ULTR, moving from 5 to 20
impressions shifts the estimated severity from **1.10 to 1.40**, i.e. +27 %, because rare cells
are those of deep ranks, from which the estimate draws most of its information.

**Access modalities.** A secure processing environment within the meaning of Article 9(5) of the
Delegated Regulation is accepted without reservation. Given the aggregate nature of the data, a
simple transmission nonetheless appears proportionate.

**Security.** [TECHNICAL AND ORGANISATIONAL MEASURES OF THE ORGANISATION].

**Funding** (Art. 8(b)): [FUNDING SOURCES]. **Independence** (Art. 40(8)(b)): [DECLARATION].

## VI. Publication of results (Art. 40(8) and Art. 8(a))

The publication commitment is already met in advance: all code, derived data, figures and
results — **including negative results** — are published in a public repository, under MIT for
code and CC BY 4.0 for content. The six negative results already published by this repository
are the most useful demonstration of it.

The data received will not themselves be republished; the **derived aggregates** will be, along
with the code producing them, in line with the practice already applied to the three datasets
measured.

## VII. Timetable and remedies

| Step | Deadline | Source |
|---|---|---|
| Coordinator's decision: reasoned request or rejection | **80 working days** | Art. 7(1) of the Delegated Regulation |
| Amendment request by the platform | 15 days | Art. 40(5) DSA |
| Coordinator's decision on the amendment | 15 days | Art. 40(6) DSA |
| Notification that access has been given | 3 working days | Art. 15(1) of the Delegated Regulation |
| Request for mediation | 5 working days | Art. 13(1) |
| Opening, then duration of mediation | 20, then at most 40 working days | Arts. 13(4), 13(9) |

Article 15(3) of the Delegated Regulation further forbids the provider from imposing limitations
on the use of standard analytical tools, unless the reasoned request mentions them explicitly.

## VIII. What we will do with a refusal

The refusal will be published, quoted as received, and analysed like any other result: a request
of this form cannot be set aside for disproportion without the ground bearing on something other
than its size. That is the point of the specification — **to shift the burden of proof**, and to
make refusal arguable.

---

## Reservations attaching to this request

**These tables do not permit everything.** They say nothing of a reader's trajectory, hence
nothing of individual filter bubbles, nor of the temporal dynamics of one user's feed. That is
deliberate — those are the analyses that would require personal data — but it must be said: this
request is narrow, and part of the repository's research programme falls outside it.

**An aggregate is an assumption.** Tables 1 and 2 are keyed by rank profile and by feed click
count precisely because two simpler assumptions turned out false in use, on real data, without
producing a visible error. A platform delivering these tables under a coarser key would deliver
wrong figures of the right order of magnitude — the worst case.

**And eligibility is missing.** This document is a template, not a procedure under way. Its
value is in being **ready**: a research organisation wishing to ask this question no longer has
to design the specification, only to file it.

---

*Implementation: `ide.aggregates` · Notebook:
[18 — What to ask for](notebooks/18_demande_article_40.ipynb) ·
[MIND's real exploration](mind.en.md) · [logs that record the rank](rang-servi.en.md) ·
[memorandum](memorandum.en.md)*
