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

Output findings.json per the schema in references/report-spec.md.
