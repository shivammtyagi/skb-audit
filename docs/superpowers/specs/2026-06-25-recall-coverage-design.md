# Design: Phase 4–5 recall & coverage hardening

**Date:** 2026-06-25
**Problem:** A real audit run missed 1 CRITICAL (a leaked OpenAI API key published in the KB) and
4 HIGH accuracy findings (an AI-integration rearchitecture) that an earlier run had caught. Root
cause was in Phase 5's design, not in execution discipline:

1. **No coverage mandate.** Pass A said "compare steps/settings/version references vs signals" but
   never required *every* product/snippet article to be reviewed. A deterministic candidate filter
   (version refs + deprecation keywords) became the *only* set fed to agents; articles that drifted
   without a version cue (e.g. a feature rearchitected from direct-OpenAI to AIOSEO's own AI service)
   were never read by any agent.
2. **Only a precision gate.** "Every CRITICAL/HIGH cites evidence" guards false positives. Nothing
   guarded false negatives (recall). Two well-cited findings passed the gate and produced false
   confidence.
3. **No deterministic secrets scan.** A leaked `sk-…` credential was catchable only by reading that
   one article; it should be caught mechanically, independent of agent coverage.

## Changes

### 1. Mandatory full coverage (new `scripts/make_review_batches.py`)
Selects all `product` + `snippet` articles, splits into numbered batches
(`audit/_internal/review-batches/passA_NN.json`, ~10 articles/batch). Pass A dispatches one subagent
per batch **in parallel**; every article gets a verdict. Mechanical candidates are *prioritization
hints, not a filter*. Agents check **mechanism/architecture drift** (does the described
endpoint/flow/integration still match code?), not just version strings.

### 2. Deterministic secrets scanner (new `scripts/lib/secrets.py`, wired into `analyze_content.py`)
Regex for API keys (`sk-…`, `AKIA…`, `ghp_/gho_…`, `AIza…`), PEM private keys, bearer tokens, and
`password=`/`api_key=` assignments. Any hit → mechanical finding at **CRITICAL**,
`recommendation: Retire`. **Redaction is mandatory**: deliverables store
`[REDACTED-SECRET: <type>, <n> chars]`, never the value.

### 3. Recall gate + completeness critic (Phase 5)
- Gate: `findings.json` must carry a verdict for **every** product/snippet article; fails if
  `audited_count < (#product + #snippet)`. Logged to `quality-gates.md`.
- Completeness-critic sub-pass: one agent inspects finished findings for unexamined dimensions
  (secrets, rearchitected features, removed settings); its output seeds a targeted follow-up round.

### 4. Snippet-verification hardening (`phases.md` Pass A)
Distinguish hook **targets** (`add_filter('aioseo_x', …)`) from the user's own callback **function
names** (`function my_cb()`); only the former are verified against the repo. Verify with
**ground-truth (clone + grep)**, not `gh search code` alone (index gaps cause false "missing"
reports). This prevents the 16-false-positive class observed in review.

## Unchanged
Anti-hallucination (precision) gate stays — recall gate is additive. Phases 0–4 mechanics, Pass B–E
logic, and the four deliverables are unchanged.
