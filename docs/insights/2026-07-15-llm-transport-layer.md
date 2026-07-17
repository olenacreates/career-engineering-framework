# Insights — Iteration: LLM Transport Layer

**Date:** 2026-07-15
**Sprint / iteration:** Sprint 1 — MVP Career Knowledge Extraction Engine
**Scope of this iteration:** Implement `llm_client.generate_text` (Anthropic
transport) and run a pre-commit design review of it.
**Status:** Working knowledge harvest. Candidates below are labeled and NOT yet
established.

> Convention: one entry per iteration. Captures the *learning curve*, not
> decisions. Load-bearing decisions still belong in `docs/adr/` (see "Decision
> breadcrumbs" at the end).

---

## 1. Product-specific observations (not reusable)

- The MVP pipeline makes **one** LLM call per run (single Brain Dump → single
  Career Profile). This single-call shape is what makes several design choices
  below "good enough for now" — it is a property of *this* product at *this*
  stage, not a general truth.
- Model is currently pinned to `claude-opus-4-8` with `max_tokens=4096` inside
  `llm_client.py`.

## 2. Reusable engineering insights

- **Import purity.** Keeping `load_dotenv()` and client construction *inside* the
  call (not at module scope) means importing the module has no side effects and
  needs no valid API key. This keeps the module testable and importable by
  tooling, `--help`, and test collection. *What changed in our thinking:* we
  moved from "config/setup naturally goes at the top of the file" to "a module's
  import should be free of I/O and external dependencies." *Why it matters:*
  import-time failures surface far from the call site and break unrelated tooling.
- **"Move to module scope" is not automatically the cleaner refactor.** Naive
  module-scope initialization reintroduces exactly the import-time side effects we
  wanted to avoid. The genuinely better long-term shape is a **lazy, cached
  singleton** plus loading config once at the entry point — not top-of-module
  globals.
- **Config loading is an entry-point concern.** `load_dotenv()` arguably belongs
  in `main()`, with lower-level modules only *reading* `os.environ`. Deferred for
  the MVP as a low-value change, but noted.

## 3. Candidate decision frameworks (labeled — general best practice)

- **Candidate: "Import purity check."** Before placing initialization at module
  scope, ask: (1) does it do I/O or construct an external client? (2) would import
  fail if config/network/keys are absent? (3) does it make the module harder to
  test or mock? If any "yes", prefer lazy initialization (in-function or cached
  singleton) over module-scope globals. — *General best practice, not yet a
  project standard. Promote only after it proves useful on a second case.*

## 4. Candidate engineering principles (labeled)

- No new principle proposed. This iteration mostly **re-applied existing framework
  principles** rather than discovering new ones:
  - *"Build the smallest implementation that preserves the long-term architecture"*
    → per-request client is fine now; the lazy-singleton door stays open cheaply.
  - *"Invest after validation"* → we chose not to optimize connection reuse before
    there is more than one call per run.
  - *"Treat AI as a collaborator, not an oracle"* → the pre-commit design review
    (interrogating rationale before accepting AI-generated code) is the mechanism
    that surfaced these insights at all. Candidate observation: **make design
    review of AI-generated code a standing pre-commit ritual** — labeled candidate,
    validate on a further case.

## 5. Decision breadcrumbs (for retrospective ADRs)

These are load-bearing and currently only in code/chat. To be promoted to ADRs
when we return to the process work:

- **Model selection:** `claude-opus-4-8`, `max_tokens=4096`. *Context/alternatives
  not yet recorded.*
- **LLM client design:** lazy `load_dotenv()` + new `Anthropic` client per request;
  provider errors wrapped in a single `LLMError` type to decouple callers from the
  SDK. *Recommended future revisit trigger: >1 LLM call per run → lazy cached
  client + client injection for tests.*
