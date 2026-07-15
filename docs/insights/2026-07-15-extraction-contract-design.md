# Insights — Iteration: Extraction Contract Design & Implementation

**Date:** 2026-07-15
**Sprint / iteration:** Sprint 1 — extraction contract design, then implementation
of `load_prompt()` + `extract_profile()` + the extraction prompt.
**Status:** Working knowledge harvest. Contains one Open Architectural Question
(intentionally NOT an ADR), one temporary MVP implementation decision (now
validated end-to-end), and first-run evidence.

---

## Context

We needed to define the contract between an unstructured Brain Dump and the
structured `CareerProfile` before writing extraction code, because ADR-001 makes
the Career Profile the source of truth for all downstream artifacts. We designed
the contract, deferred a deeper architectural question, adopted a temporary
evidence-only MVP policy, wrote `career_profile_prompt.md`, and implemented the
extraction path.

## Observation

- **The `CareerProfile` model is already a hybrid.** ~half its fields are factual
  (`name`, `email`, `location`, `skill.name`, `achievement.title`/`.context`) and
  ~half are interpretive (`headline`, `summary`, `target_roles`, `skill.category`,
  `hero_stories`). So "extract vs interpret" is not a future choice — it is already
  latent in the schema.
- **The real tension** is not evidence-only vs conservative inference, but
  *extracting what was said* vs *interpreting what the experience means*.
- **A source of truth should be the most stable, least opinionated layer.**
  Interpretation is a projection of facts through an intent (substrate vs
  projection / event-log vs read-model). *General best practice.*
- **New, from real usage:** the current schema does not capture **employment
  history or work history**.

## Evidence (first successful end-to-end extraction — 2026-07-15)

A small sample Brain Dump was run through `extract_profile()` against the live
Anthropic API. Observed:

- **Career Profile successfully generated** — full end-to-end flow worked
  (`load_prompt` → `{{BRAIN_DUMP}}` substitution → `generate_text` → JSON parse →
  `from_dict`).
- **JSON contract respected** — valid JSON, exact snake_case keys, list items as
  objects; deserialized cleanly via `from_dict`.
- **No hallucinated skills** — "mentored two junior engineers" did NOT become a
  "Leadership"/"Mentoring" skill; no capability was inferred.
- **No fabricated achievements or metrics** — "cut checkout errors roughly in half"
  was preserved as stated (light wording normalization only); nothing invented.
- **Hero Stories remained empty** (`[]`) when unsupported by a narrated story.
- **Target Roles extracted only when explicitly stated** (the dump stated the
  goal).
- **Interpretive fields remained empty unless explicitly supported** — `headline`,
  `summary`, and every `skill.category` came back `""`.
- **`source_document` intentionally remains outside the prompt contract** — the
  LLM never emits it; the code/pipeline owns that provenance.
- **Employment/work history was dropped** — "backend developer for 5 years" had no
  home in the schema. Evidence from a real extraction, not yet a decision.

### Increment 2 — first runnable MVP (pipeline + entry point)

- **End-to-end application runs:** `python src/main.py` reads
  `input/brain_dump.docx`, produces `output/career_profile.json`, and reports
  success — the Sprint Goal (Brain Dump → Career Profile JSON) is met by a
  runnable app, not just a library call.
- **Error path is clean:** a missing input yields a legible message and exit
  code 1 (the pipeline raises; the entry point presents).
- **`source_document` provenance validated in the running app** — set by the
  pipeline to the filename only (`brain_dump.docx`), confirming the code-owns-
  provenance boundary in practice.
- **Schema gap reproduced (2nd data point):** on a richer dump, employment
  history / tenure was dropped again — reinforcing the Open Question evidence.
- **Ops observation (reusable):** a declared dependency (`python-docx`) was not
  installed in the active interpreter; the earlier tests passed only because they
  didn't exercise the DOCX loader. Verify declared deps are actually importable in
  the target interpreter before claiming a flow is "runnable."

## Why it matters

- The evidence-only MVP policy is now **validated in practice**: the extractor
  captures facts without inventing capabilities, protecting the source of truth
  from hallucination that (per ADR-001) would propagate into every downstream
  artifact.
- The employment-history gap is the **first real-usage signal** that the schema
  may be incomplete for real Brain Dumps — direct input to the Open Question below.

## Decision or Open Question

### Open Architectural Question — Where should interpretation live?

**Question.** Should the Career Profile remain a *factual knowledge layer*, or also
contain *interpreted capabilities* (positioning, inferred skills, narrative
framing)?

**Why open.** The distinction between factual extraction, capability
interpretation, and the long-term role of the Career Profile is larger than
Sprint 1; we don't yet have enough evidence to answer it correctly.

**Decision.** Intentionally **postponed** until the MVP is evaluated against
several real Brain Dumps. Recorded as an Open Question, not an ADR, by explicit
Product Owner decision.

**Resolution trigger (how we exit this question).**
- If evidence-only profiles are consistently *too sparse* to produce a useful
  Master CV → evidence FOR an interpretation layer / richer schema.
- If profiles are *sufficient* → the factual substrate model holds.
- Guard against the confound: a sparse profile → weak CV could indict the *product*
  when the cause is the *strict policy*. Hold the policy as a known variable.
- The **employment-history gap** is now logged as a first data point feeding this.

**When resolved:** promote to an ADR (likely a clarification/amendment of ADR-001).

### Temporary MVP implementation decision (validated this increment)

For Sprint 1 only: extract only what the Brain Dump explicitly supports; never
invent facts/achievements/metrics; do not infer capabilities; keep interpretive
fields but populate them only when explicitly stated; allow light wording
normalization (no new facts); strict schema-locked JSON output. Explicitly
temporary; may be promoted to an ADR if it survives evaluation.

## Candidate Principle (only if justified)

- **Candidate:** *Every deferred architectural decision must carry an explicit
  resolution trigger* — the condition/evidence that will later resolve it —
  otherwise it becomes a floating decision. Emerged this session and affirmed by
  the Product Owner. Keep as a labeled candidate until it proves useful on a
  further real deferral.
- **Toward established:** the *optionality three-question test* was applied to a
  second real case here (interpretation-in-source-of-truth is expensive-to-reverse,
  keeping the profile factual is cheap-to-keep-open). Evidence toward promoting it
  from candidate to established.

## Decision breadcrumbs

- `source_document` owned by code/pipeline, not the LLM.
- `temperature` not pinned in `llm_client` → residual output variance (evidence-only
  narrows it; does not eliminate it).
- Employment/work-history schema gap logged as evidence for the Open Question.
