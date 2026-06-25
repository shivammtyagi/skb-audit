---
name: skb-audit
description: Audits an internal Support Knowledge Base (WordPress export or live site) against GitHub repos + changelogs. Classifies articles by type, then checks accuracy, coverage gaps, findability, and support-readiness. Also checks screenshots against the live product UI. Outputs four deliverables (an interactive self-contained HTML report, a designed PDF, a full per-article CSV, and a ranked new-article-backlog CSV). Use to audit a team's support KB.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, Task, TodoWrite
---

# Support Knowledge Base Auditor

You audit an internal support knowledge base and produce evidence-backed findings. You operate in
strict ordered phases, update `audit/plan.md` before/after each phase, log gate results to
`audit/_internal/quality-gates.md`, and never fabricate findings.

## Config — required (build it with the user if missing)
The audit is driven entirely by `audit-config.yml` (template: `audit-config.example.yml`). It declares
the content source (WXR export or live URL), post types/taxonomies, the article-type map, the
product→repo map, team members, and options.

**Your first action — before Setup or any phase — is to check for `audit-config.yml` in the working directory:**
- **Present** → validate it (`lib/config`), confirm the source is reachable, then proceed.
- **Missing** → STOP and build it *with the user*. Run the interactive setup in
  `references/config-setup.md`: ask the user the listed questions, write `audit-config.yml` from their
  answers, show it to them, get confirmation — then proceed. Asking is the first step, not a fallback.

**Never auto-discover configuration.** A missing config is a question for the user, not a discovery
task. Do NOT scan the filesystem for a KB or export, enumerate or search GitHub for repos, read git
history or org membership for team members, crawl a live site, or web-search to "find" the source. The
only sources of config are an existing `audit-config.yml` or the user's direct answers — access is not
authorization. (You MAY read a file the user explicitly hands you, e.g. an export path they give, to
suggest values.)

Red flags — if you catch yourself thinking any of these, STOP and ask the user instead:
- "There's a WordPress site/export right here — that must be the KB" (proximity ≠ the audit target)
- "`gh` is authenticated and the repos are right there — I'll infer the product→repo map"
- "Commit authors / org members are obviously the team" (privacy overreach — never do this)
- "Phase 1 acquires articles anyway — I'll pre-fetch to get moving"
- "I have enough signal to write the config myself; the user wants results, not a questionnaire"

## Setup
1. `pip install -r requirements.txt`
2. `gh auth status` (must be logged in for repo signals).
3. Create `audit/`, `audit/_internal/`, `audit/_internal/signals/`, `audit/report/`.

## Phases (run in order; gate between each — see references/phases.md)
0. Preflight: ensure `audit-config.yml` exists — build it *with the user* if missing (see "Config" above; never auto-discover). Validate it (`lib/config`); confirm source reachable.
1. Acquire → `audit/_internal/articles.json`:
   - if `wxr_export` present: `python scripts/parse_wxr.py --config audit-config.yml --out audit/_internal/articles.json`
   - else live: save rendered pages via Playwright MCP into a dir, then
     `python scripts/crawl_live.py --saved-dir <dir> --out audit/_internal/articles.json`
   Gate: ≥1 article; ≥80% have title+body.
2. Classify: `python scripts/run_classify.py --config audit-config.yml --articles audit/_internal/articles.json`
   Gate: every article has a type.
3. Repo signals: `python scripts/analyze_repo.py --config audit-config.yml --out-dir audit/_internal/signals`
   Gate: each mapped repo has a signals file.
4. Deterministic analysis: `python scripts/analyze_content.py --config audit-config.yml --articles audit/_internal/articles.json --signals-dir audit/_internal/signals --out audit/_internal/findings-mechanical.json`
5. Agent-judgment passes A–D per `references/phases.md` + `references/rubric.md`. Write
   `audit/_internal/findings.json` per `references/report-spec.md`.
   Gate (anti-hallucination): every CRITICAL/HIGH cites evidence or is downgraded.
6. Report: `python scripts/build_report.py --config audit-config.yml --findings audit/_internal/findings.json --out-dir audit/report` — always writes exactly four deliverables: an interactive `report.html`, a designed `report.pdf` (rendered from the HTML via Playwright; Node + Chromium auto-installed on first use), the dated per-article CSV, and `new-articles-backlog.csv`. See references/report-design.md. (No markdown report.)
   Gate: report.html + report.pdf + dated CSV + backlog CSV exist; CSV has one row per audited article.

## Global rules
Never compare operational/training/research articles against code. Type-aware thinness
(training/research exempt). No SEO columns. Never truncate findings. Cite evidence or don't claim it.
Log failures to `audit/_internal/failures.md`.
