# Agent-Judgment Passes

The deterministic pipeline produces findings-mechanical.json. The agent then enriches it
into findings.json by performing these judgment passes, type-aware. NEVER compare
operational/training/research articles against code.

## Pass A — Accuracy & lifecycle (product, snippet)
- product: compare steps/settings/version references vs signals/<repo>.json (changelog,
  deprecations, recent_commits). Cite the file/commit/changelog line. Draft a correction
  for every CRITICAL.
- product known-issue lifecycle: for articles tagged "known issues", check issue_demand and
  changelog "breaking" lines; if the issue appears fixed, recommend "Resolve or retire" with citation.
- snippet: for each per_article.snippet_symbols entry, run `gh search code "<symbol>" --repo <repo>`.
  Not found → finding "Snippet references missing/renamed code — verify" (HIGH if a hook, MEDIUM otherwise).

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

Output findings.json per the schema in references/report-spec.md.
