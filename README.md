# skb-audit — Claude Code Skill

A Claude Code skill that runs a deep, structured audit of an internal **support knowledge base** (SKB) — the docs a support team relies on to resolve tickets — and tells you what's inaccurate, missing, hard to find, or not good enough to actually solve a problem.

It reads your KB from a **WordPress export _or_ a live site**, classifies every article by what kind of content it is, checks the technical articles against the **GitHub repo + changelog** that are their source of truth, and produces an evidence-backed report you can act on.

Built to be reusable by any team: point it at your own KB and repos via a single config file — no edits to the skill itself.

**Outputs**
- `report.md` — human-readable audit (executive summary, quick wins, findings by priority)
- `skb-audit-YYYY-MM-DD.csv` — one row per article, ready for Sheets / Excel / your tracker
- `new-articles-backlog.csv` — ranked list of articles you should write next
- `report.html` _(optional)_ — a self-contained, shareable & printable report
- `audit/_internal/` — full intermediate data, for traceability

---

## The key idea: article-type classification

An internal KB is a **mix** — product how-tos sit next to team process docs, code snippets, training videos, and research notes. Auditing a "renewals process" doc against plugin code is nonsense, and flagging a 30-word video article as "too thin" is just noise.

So skb-audit first classifies each article into a **type**, then applies a different lens to each:

| Type | What it is | How it's audited |
|------|-----------|------------------|
| **product** | Product how-tos / troubleshooting | Accuracy vs code + changelog; deprecated features; known-issue lifecycle |
| **snippet** | Code snippets / filters / hooks | Each hook/function name verified to still exist in the repo |
| **operational** | Team processes, billing, accounts | Freshness, completeness, contradictions — **never** checked against code |
| **training** | Videos / tutorials | Link & embed liveness, freshness — exempt from "thin content" checks |
| **research** | External / market research | Link liveness + freshness only |

You define the category → type mapping in your config, so it fits any team's KB.

---

## What it checks

| Priority | What it finds |
|----------|---------------|
| **Accuracy** | Steps, settings, or version references that no longer match the product; deprecated/removed features still documented as current; "known issue" articles whose issue is actually fixed |
| **Coverage gaps** | Product features, error messages, and high-demand GitHub questions with no article → a ranked backlog |
| **Findability** | Orphaned articles (nothing links to them), duplicate/overlapping articles, contradictions, weak titles & taxonomy |
| **Support-readiness** | Whether each article actually has the steps, prerequisites, expected outcomes, and visuals an agent needs to resolve a ticket |
| **Freshness** | Each article scored Fresh / Aging / Stale vs related repo activity |

Every CRITICAL/HIGH finding cites its evidence (a repo file, commit, or issue) — the skill never fabricates findings.

---

## Prerequisites

- **Claude Code** — https://claude.ai/code
- **GitHub CLI (`gh`)**, authenticated (`gh auth login`) — used to read repos, changelogs, and issues
- **Python 3.9+** with `pyyaml` + `pytest` (`pip install -r requirements.txt`)
- _(optional)_ **Playwright MCP** — only for the live-crawl path, when you don't have a WordPress export

## Install

```bash
git clone https://github.com/shivammtyagi/skb-audit ~/.claude/skills/skb-audit
cd ~/.claude/skills/skb-audit
pip install -r requirements.txt
```

## Configure

```bash
cp audit-config.example.yml audit-config.yml
# then edit audit-config.yml:
#   - your KB source (WordPress export path OR live URL)
#   - your post type(s) + taxonomies
#   - the category → type map
#   - your product → GitHub repo mapping
```

`audit-config.yml` is gitignored, so your team's details never get committed.

## Run

In Claude Code, invoke the skill:

```
/skb-audit
```

It validates the config, acquires your articles, classifies them, builds per-repo signals, runs the analysis passes, and writes the report + CSVs. Ask for an HTML report when you want one.

---

## How it works

```
config → acquire (WXR export or live crawl) → classify article types
       → build repo signals (structure · changelog · deprecations · issues)
       → analysis passes (accuracy · coverage · findability · readiness)
       → report.md + CSVs + optional report.html
```

The deterministic parts (parsing, classification, metrics, duplicate detection, snippet extraction, report building) live in tested Python under `scripts/`; the judgment parts (is this claim outdated? do these two articles contradict?) are guided by the playbooks in `references/`.

## Project layout

```
SKILL.md                  # orchestrator — the skill's entry point
audit-config.example.yml  # copy to audit-config.yml and fill in
references/               # rubric, phase playbook, report + design specs
scripts/                  # tested lib/ + CLIs (parse, classify, analyze, report)
tests/                    # pytest suite + fixtures
```

## Tests

```bash
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).
