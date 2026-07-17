# Sprint 1 Review — Career Knowledge Extraction Engine (MVP)

**Date:** 2026-07-16
**Sprint:** Sprint 1 — MVP Foundation (branch `sprint-1-mvp-foundation`)
**Scope of this document:** PRODUCT evaluation only. How we worked is evaluated
separately in the Sprint Retrospective.

---

## Sprint Goal

> Career Brain Dump (`.docx`) → Career Profile (JSON)

Deliver the first runnable MVP of the Career Knowledge Extraction Engine:
transform an unstructured Brain Dump into a structured Career Profile that serves
as the single source of truth (ADR-001).

## What was planned

At sprint start the engineering foundation already existed — project architecture,
Python scaffold, Career Profile domain model, DOCX loader, git workflow — but the
**AI extraction pipeline did not**. Planned for Sprint 1:

- LLM transport layer (Anthropic integration)
- Extraction prompt + extraction step (Brain Dump text → `CareerProfile`)
- Pipeline orchestration + a runnable entry point (file in → JSON out)
- End-to-end verification against real input

Added within the sprint (not in the original foundation plan): a Streamlit demo UI
for workshop / conference demonstration.

**Explicitly out of scope:** Master CV generation, other future artifacts
(Skills/Achievement libraries, Hero Stories as outputs, Positioning Map), an
automated test suite, authentication, persistence.

## What was actually delivered

**Committed (`sprint-1-mvp-foundation`):**
- **LLM transport** — `llm_client.generate_text` (Anthropic Messages API),
  provider-agnostic `LLMError`, model `claude-opus-4-8`. [`4715a93`]
- **Extraction** — `career_profile_prompt.md` (evidence-only contract),
  `load_prompt()`, `extract_profile()` with defensive JSON parsing → `from_dict`.
  [`574e941`]
- **Runnable pipeline + entry point** — `pipeline.run(input_path, output_path)`,
  `main.py` (owns path conventions + user-facing messages). [`8456328`]
- **Insight evidence updates.** [`192206a`]

**Reused unchanged (pre-existing foundation):** `CareerProfile` model +
serialization, DOCX loader.

**Built and verified but NOT yet committed:** the Streamlit demo UI
(`src/streamlit_app.py`) and the `streamlit` optional extra in `pyproject.toml`.
This must be committed to count as formally delivered (see conclusion).

**Verification approach:** manual/live end-to-end runs. `tests/test_*.py` remain
empty placeholders — there is no automated test suite in this increment.

## Demonstration of the increment

- **CLI:** `python src/main.py` → reads `input/brain_dump.docx` → writes
  `output/career_profile.json` → prints `Career Profile written to
  output\career_profile.json`.
- **Demo UI:** `streamlit run src/streamlit_app.py` → upload a `.docx` → before/after
  view: raw Brain Dump text (left) vs structured Career Profile (right).

Sample run (a "Dana Kovalenko" Brain Dump) produced a valid profile: metadata
(name, location, email, target roles), 4 skills, 3 achievements, `hero_stories: []`,
`source_document: "brain_dump.docx"`.

## Evidence the Sprint Goal was achieved

- **End-to-end verified twice** on the live API: `extract_profile` directly, and the
  full `main.py` pipeline — both produced valid Career Profile JSON deserializing
  cleanly via `from_dict`.
- **Evidence-only policy held:** no hallucinated skills ("mentored two juniors" did
  not become a skill), no fabricated metrics, interpretive fields empty unless
  stated, `hero_stories` empty when unsupported.
- **Error path verified:** missing input → legible message + exit code 1.
- Evidence recorded in `docs/insights/2026-07-15-extraction-contract-design.md`
  (Evidence — Increments 1 & 2).

**Conclusion:** the goal (Brain Dump `.docx` → Career Profile JSON) is met by a
runnable application.

## Product decisions made during the sprint

Decisions that shaped the product, with where each is currently recorded:

| Decision | Recorded in |
|---|---|
| Model pinned to `claude-opus-4-8`, `max_tokens=4096` | code + insight breadcrumb — **no ADR yet** |
| LLM client design: lazy env load, per-request client, `LLMError` wrapper | code + insight breadcrumb — **no ADR yet** |
| Evidence-only extraction policy (temporary, MVP) | insight (intentionally not an ADR yet) |
| Boundary: code owns `source_document`; LLM owns the four content sections | insight / prompt contract |
| Pipeline contract `run(input_path, output_path)`; main owns "where", pipeline owns "what order" | code + planning record |
| Streamlit added as an **optional** dependency (core stays UI-independent) | `pyproject.toml` + insight |

*Factual note:* several load-bearing decisions (model pin, client design) currently
live only in code/insight breadcrumbs, not ADRs — a gap to reconcile at closure,
per "decisions belong in ADRs."

## Open architectural questions intentionally deferred

Both recorded (as Open Questions, not ADRs) in
`docs/insights/2026-07-15-extraction-contract-design.md`, each with an explicit
resolution trigger:

1. **Where should interpretation live?** — factual substrate vs interpreted
   representation. Deferred until evaluated against several real Brain Dumps. Early
   evidence: employment/work-history was dropped (no schema field) on 2 real dumps.
2. **Should `pipeline.run()` return a `CareerProfile` instead of writing files?** —
   prompted by multiple entry points (CLI, Streamlit, future REST). Early evidence:
   the Streamlit UI writes then re-reads a temp file (double-load friction).

## Overall Sprint Review conclusion

**Sprint Goal ACHIEVED.** The MVP is DONE as a product: a runnable, verified
Brain Dump → Career Profile JSON pipeline with an evidence-only extraction policy,
plus a polished demo UI. Out-of-scope items (generation, other artifacts, automated
tests) were consciously excluded and remain so.

One item stands between "built" and "formally delivered": the Streamlit UI and its
`pyproject` extra are implemented and verified but **uncommitted**; committing them
is required for the increment to be fully version-controlled per our documentation
philosophy.

**Recommendation:** accept the product increment; commit the outstanding UI work as
part of sprint closure; carry the two deferred questions (and their evidence) into
Sprint 2 planning.
