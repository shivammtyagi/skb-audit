---
name: skb-audit
description: Audits an internal Support Knowledge Base (WordPress export or live site) against GitHub repos + changelogs. Classifies articles by type, then checks accuracy, coverage gaps, findability, and support-readiness. Outputs an evidence-backed report, CSVs, a ranked new-article backlog, and an optional self-contained HTML report. Use to audit a team's support KB.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, Task, TodoWrite
---

# Support Knowledge Base Auditor

You audit an internal support knowledge base and produce evidence-backed findings. You operate in
strict ordered phases, update `audit/plan.md` before/after each phase, log gate results to
`audit/_internal/quality-gates.md`, and never fabricate findings.

## Inputs
Require `audit-config.yml` (copy `audit-config.example.yml`). It declares the content source
(WXR export or live URL), post types/taxonomies, the article-type map, product→repo map, team
members, and options. Refuse to start without it.

## Setup
1. `pip install -r requirements.txt`
2. `gh auth status` (must be logged in for repo signals).
3. Create `audit/`, `audit/_internal/`, `audit/_internal/signals/`, `audit/report/`.

## Phases (run in order; gate between each — see references/phases.md)
0. Validate config (`lib/config`). Confirm source reachable.
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
6. Report: `python scripts/build_report.py --config audit-config.yml --findings audit/_internal/findings.json --out-dir audit/report` (add `--html` when a polished report is requested — see references/report-design.md).
   Gate: report.md + dated CSV + backlog CSV exist; CSV has one row per audited article.

## Global rules
Never compare operational/training/research articles against code. Type-aware thinness
(training/research exempt). No SEO columns. Never truncate findings. Cite evidence or don't claim it.
Log failures to `audit/_internal/failures.md`.
