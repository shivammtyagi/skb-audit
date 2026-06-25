# Spec — Pass E: Visual / Screenshot Accuracy Audit

- **Date:** 2026-06-25
- **Status:** Design approved (brainstorm); pending spec review → implementation plan
- **Skill:** `skb-audit`
- **Author:** Shivam Tyagi (with Claude)

## Motivation

The skill currently only *counts* `<img>` tags (`images`, `has_visuals`) — it never inspects
screenshot content. Stale or wrong screenshots (steps that no longer match the UI) are a common,
high-impact KB problem. The Phase-5 agent passes already run on Claude, which reads images natively,
so screenshots can be audited with **vision (no OCR)**, and "is this current?" can be grounded against
a live reference WordPress site (via the Playwright MCP) plus the cloned code/changelog.

## Goals

For **every article that contains an image**, check:
1. **Integrity** — the image loads (no 404 / broken / unreachable).
2. **Match-to-steps** — the screenshot shows what the surrounding step text describes.
3. **Outdated UI** — the screenshot reflects the current product UI.

Ground "outdated" in evidence (live capture and/or a code/changelog citation), under the same
anti-hallucination rule as the rest of the skill. Run **always**, as part of every audit.

## Non-goals

- Pixel-diff / automated visual regression — judgment is Claude's vision + evidence, not a threshold.
- Live-comparing non-AIOSEO UIs (LowFruits SaaS, internal tools, external sites) — those get
  integrity + match-to-steps + cue/code only.
- Generating or editing replacement screenshots. The pass reports; it does not produce images.

## A. Trigger — always on

Pass E runs in every audit (after Passes A–D); there is no enable flag. Behavior adapts to config:
- `reference_site` present → live-capture comparison for AIOSEO wp-admin screenshots (Playwright).
- `reference_site` absent → the outdated-check degrades to visual-cue + code/changelog judgment.
- Integrity + match-to-steps always run (need no site).

## B. Configuration (gathered in config-setup; optional block)

```yaml
reference_site:                          # optional; enables live-UI comparison
  url: https://staging.example.com       # a WP site you grant full wp-admin access to
  admin_user: admin
  admin_pass_env: SKB_REF_WP_PASS        # password read from this env var (not stored in YAML)
```

- `references/config-setup.md` adds an optional question: *"Do you have a throwaway WordPress site I
  can fully control (log into wp-admin, install plugins, change settings) so I can compare the current
  AIOSEO UI against your screenshots? If so: URL + admin username + the name of an env var holding the
  password."* Make explicit that access is full (may install/activate plugins and change settings).
- `scripts/lib/config.py`: if `reference_site` is present, require `url`, `admin_user`, and one of
  `admin_pass` / `admin_pass_env`. Absent is valid (degraded mode).
- The pass records the reference site's installed AIOSEO version and **warns in the report if it
  differs** from the audit target (otherwise "current" is misaligned).

## C. Playwright MCP preflight — auto-setup (NOT skip)

Only when `reference_site` is configured (live capture is the only thing that needs Playwright):
1. Detect whether Playwright MCP tools (`mcp__playwright__browser_*`) are available.
2. If not available:
   - Verify Node.js + `npx` exist; if missing, stop with a clear, actionable error (installing a Node
     runtime silently is out of scope).
   - Register the server: `claude mcp add playwright -- npx -y @playwright/mcp@latest`.
   - Install browser binaries: `npx -y playwright install chromium`.
   - **Reload caveat:** Claude Code loads MCP servers at session start, so a newly added server usually
     will not hot-connect mid-session. After setup, if the tools still are not live, instruct the user
     to reload Claude Code and resume — the audit is resumable (Phases 0–4 outputs + Passes A–D findings
     persist), so only Pass E re-runs.
3. Re-check availability; proceed once connected.

Log every install/config action (transparency); all steps are idempotent (check before install).

## D. Architecture — Pass E (serial agent loop)

Runs after the parallel Passes A–D. Because the Playwright MCP drives a single browser session, the
live-capture loop is **serial** (a single agent).

**Prep (deterministic):** `scripts/extract_images.py --articles <articles.json> --out
image-worklist.json` extracts, per article with images, a list of `{src, alt, nearby_step_text}` from
`body_html` (new helper `scripts/lib/images.py:extract_images`). Articles without images are skipped.

**Per article (serial loop):**
1. **Integrity** — HTTP-fetch each `src`; non-200 / unfetchable → finding (broken/missing). No vision.
2. **Match-to-steps** — Claude reads the image + its `nearby_step_text`; if the screenshot shows a
   different screen/control than the step describes → finding.
3. **Outdated** — for AIOSEO wp-admin screenshots, when `reference_site` is set:
   - Infer the target admin screen from the step text (e.g., "All in One SEO → Sitemaps").
   - **Within-run screen cache:** reuse a prior capture of the same screen; on miss, drive Playwright
     (login session reused) → navigate → screenshot → cache to `audit/_internal/screenshots/`.
   - Compare the article image against the live capture, **grounded in code/changelog** (e.g., changelog
     says the screen was renamed/removed). Material UI drift / missing screen → finding.
   - Non-AIOSEO images (operational tools, LowFruits, external) or unreachable screens → fall back to
     visual-cue + code/changelog judgment (no live capture).
4. Aggregate per-image results into one per-article screenshot finding.

**Resilience:** per-article fallback — a navigation/capture failure drops that image to cue+code and
never aborts the pass; progress logging; resumable.

## E. Findings output

New per-article fields (in `findings.json` and as CSV columns — additive, no SEO columns):
- `screenshot_status`: `OK | Broken | Mismatch | Outdated | Not-checked`
- `screenshot_finding`: short description
- `screenshot_evidence`: saved live-capture path and/or code/changelog citation

The row's overall `criticality` becomes `max(text_criticality, screenshot_criticality)`. Severity
guidance: broken image in a resolve-critical flow → HIGH; outdated screen that misleads the steps →
MEDIUM; cosmetic drift → LOW. `report.md` gains a "Screenshot issues" subsection; the HTML report shows
a screenshot column/section. The anti-hallucination gate applies: a HIGH outdated/mismatch finding must
cite the live capture and/or a code line, else it is downgraded.

## F. Files touched

- `scripts/lib/images.py` — `extract_images(article)`.
- `scripts/extract_images.py` — build the image worklist.
- `references/phases.md` — document **Pass E** (serial, agent-orchestrated, Playwright preflight).
- `references/config-setup.md` + `audit-config.example.yml` — optional `reference_site` question/block.
- `scripts/lib/config.py` — validate optional `reference_site`.
- `scripts/build_report.py` — new columns + "Screenshot issues" section.
- `SKILL.md` — document Pass E (always-on), the config, and the Playwright auto-setup.
- `tests/` — `test_images.py` (extraction), `test_config.py` (reference_site validation),
  `test_build_report.py` (new columns).

## G. Cost / runtime / limits (honest)

- Serial live navigation at "every article with an image" scope is a long, token-heavy pass; the screen
  cache reduces distinct-screen captures but it remains the slowest part of the audit. (Accepted:
  Approach 2 + full scope + always-on were chosen deliberately.)
- Integrity + match-to-steps are cheaper and site-free.
- Live-compare only covers AIOSEO wp-admin screens; everything else is cue+code.
- Requires Node/`npx` for Playwright auto-setup; a freshly added MCP server may need a session reload
  before it connects (resume at Pass E).

## H. Open questions / future

- If serial runtime becomes painful, revisit the "reference library" optimization (pre-capture each
  AIOSEO screen once, then parallelize the vision comparison) — same checks, faster.
- Optional later: auto-draft replacement screenshots from the live captures.
