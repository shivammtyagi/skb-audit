# Agent-Judgment Passes

The deterministic pipeline produces findings-mechanical.json. The agent then enriches it
into findings.json by performing these judgment passes, type-aware. NEVER compare
operational/training/research articles against code.

## Pass A — Accuracy & lifecycle (product, snippet)

**COVERAGE IS MANDATORY. Review EVERY product and snippet article — not a subset.** The mechanical
candidate cues (version references, deprecation keywords) are **prioritization hints, NOT a filter**.
The most damaging misses are articles that drifted WITHOUT a version cue — e.g. a feature
rearchitected behind the scenes (an integration that moved from a third party to a first-party
service, an endpoint/flow that was renamed). Those never appear in a keyword filter, so a
filter-only Pass A will silently miss them. Do not let that happen.

Mechanism for full coverage:
1. Run `python scripts/make_review_batches.py --articles audit/_internal/articles.json --out-dir audit/_internal/review-batches`.
   It writes one batch file per ~10 product/snippet articles plus a `manifest.json`.
2. **Dispatch ONE subagent per batch, IN PARALLEL** (send all the Task calls together). Each agent
   reviews every article in its batch against `signals/<owner>__<repo>.json`.
3. Each agent returns a verdict for EVERY article in its batch:
   `{id, criticality, accuracy_finding, evidence | "reviewed: no issue found", correction, recommendation}`.
   "reviewed: no issue found" is a valid, required verdict — silence is not.

What each agent checks per article:
- **Steps/settings/version drift** vs changelog, deprecations, recent_commits. Cite the
  file/commit/changelog line. Draft a correction for every CRITICAL/HIGH.
- **Mechanism / architecture drift** (REQUIRED, not optional): does the described integration,
  endpoint, data flow, model, or service still match the current code? Verify the named mechanism
  exists (e.g. grep the endpoint/class/URL constant in the repo). A confidently-worded article about
  a mechanism the code no longer uses is HIGH even with no version number in sight.
- **Known-issue lifecycle**: for articles tagged "known issues", check issue_demand and changelog
  "breaking" lines; if the issue appears fixed, recommend "Resolve or retire" with citation.
- **Leaked secrets**: `findings-mechanical.json` flags any article with `secrets` (deterministic
  scan). Confirm and surface as CRITICAL, `recommendation: Retire`. NEVER reproduce the secret value
  in any output — cite the redacted descriptor only.

### snippet symbol verification — do it right
For each `per_article.snippet_symbols` entry, decide whether it is a HOOK the article tells users to
hook into, or the article's OWN callback function name:
- A **hook target** appears as the quoted first arg of `add_filter('x', …)` / `add_action('x', …)` /
  `apply_filters('x', …)`. Only hook targets are product hooks to verify.
- A **callback function name** appears as `function x(` (the user's own code) or as the 2nd arg of
  `add_filter(<hook>, 'x')`. These are NOT product symbols — do NOT flag them as "missing". (A snippet
  that defines `function aioseo_truncate_title()` and hooks it onto the real `aioseo_title` filter is
  correct; flagging `aioseo_truncate_title` as a missing hook is a false positive.)
- Verify hook targets with **ground truth**, not `gh search code` alone — GitHub code search has
  index gaps and returns false "no results". Prefer a shallow clone + `grep -r` across the repo (all
  file types, including .js/.vue), or confirm a "missing" verdict a second way before asserting it.
  Genuinely absent hook → "Snippet references missing/renamed code — verify" (HIGH if a hook, MEDIUM
  otherwise), citing the grep that found nothing.

## Pass B — Coverage gaps (→ backlog)
- Undocumented feature_symbols / error_strings (use lib.ghsignals.find_undocumented over article texts).
- Top issue_demand items with no matching article. Rank by demand. Each backlog item cites its source.

## Pass C — Findability & structure (all types)
- Use mechanical orphans + duplicates. For each duplicate pair, decide Merge vs Keep-canonical.
- Read duplicate/near-duplicate pairs for CONTRADICTIONS; flag with both article URLs cited.

## Pass D — Quality & support-readiness (type-aware)
- Confirm/adjust mechanical support_readiness; flag thin (non-exempt) and stale articles;
  for product, note missing visuals when steps imply a UI.

## Pass E — Visual / screenshot accuracy (always on; SERIAL)
Checks the screenshots in every article that has an image. Runs AFTER A–D, as a single serial
agent loop (the Playwright MCP drives one browser session, so it cannot be parallelized).

Inputs: build the worklist with `python scripts/extract_images.py --articles audit/_internal/articles.json --out audit/_internal/image-worklist.json` (each entry has src, alt, nearby_step_text).

Preflight (only when `reference_site` is configured): ensure the Playwright MCP is available; if it is
NOT, INSTALL it (do not skip) — register the server (`claude mcp add playwright -- npx -y @playwright/mcp@latest`) and install browsers (`npx -y playwright install chromium`). Claude Code loads MCP servers at
startup, so if the tools do not hot-connect, tell the user to reload Claude Code and resume — the audit
is resumable (Phases 0–4 + Passes A–D persist), so only Pass E re-runs. Then log into `reference_site`
(password from `admin_pass_env`) and record the live AIOSEO version (warn if it differs from the audit target).

For each image, three checks:
- **Integrity** — fetch the src; a 404 / unreachable image is a finding (no vision needed).
- **Match-to-steps** — read the image; if it shows a different screen/control than nearby_step_text
  describes, that is a finding.
- **Outdated** — for AIOSEO wp-admin screenshots only: infer the target admin screen, navigate the
  reference site to it (reuse a within-run screen cache to avoid re-navigating), screenshot it, and
  compare; ground the verdict in the code/changelog (e.g. the screen was renamed/removed). Non-AIOSEO
  images (operational tools, LowFruits SaaS, external) or unreachable screens fall back to visual-cue +
  code/changelog judgment. Save live captures under `audit/_internal/screenshots/`.

Resilience: a navigation/capture failure drops that image to cue+code (never aborts the pass).
Emit per article: `screenshot_status` (OK | Broken | Mismatch | Outdated | Not-checked),
`screenshot_finding`, `screenshot_evidence`. The article's overall `criticality` = max(text, screenshot).
EVIDENCE RULE applies: a HIGH outdated/mismatch must cite the saved live capture and/or a code line, else downgrade.

## Completeness critic (after A–E, before the gate)
Dispatch one subagent over the assembled findings to attack RECALL — not "are the findings right?"
but "what was NOT examined?". It must answer:
- Does every product/snippet article have a verdict? (cross-check against
  `review-batches/manifest.json` ids — list any missing.)
- Any article flagged with `secrets` that is not CRITICAL/Retire in findings?
- Any class of drift likely unexamined — a rearchitected feature, a removed/renamed setting, an
  endpoint no longer present — that a version-keyword pass would miss?
Anything it surfaces becomes a targeted follow-up review round (re-run the relevant batch) before the
gate. Log what it checked and found to `audit/_internal/quality-gates.md`.

## Gates for Phase 5 (both must pass)
- **Precision (anti-hallucination):** every CRITICAL/HIGH cites evidence or is downgraded.
- **Recall (coverage):** every product + snippet article has a verdict in findings.json; the audited
  count must equal `#product + #snippet`. Every `secret_findings` article is CRITICAL. Fail → go back
  and review the missing articles; do not proceed to the report on a recall failure.

Output findings.json per the schema in references/report-spec.md.
