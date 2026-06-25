# Report & findings.json contract

## findings.json
{
  "articles": [ { ...Article fields..., "criticality","effort","recommendation","action",
                  "evidence","accuracy_finding","duplicate_of","known_issue_status",
                  "support_readiness","findability","has_steps","has_visuals",
                  "screenshot_status","screenshot_finding","screenshot_evidence",
                  "assigned_to","status" } ],
  "backlog": [ { "title","type","demand","source","outline","priority" } ]
}

Pass E adds `screenshot_status` (OK | Broken | Mismatch | Outdated | Not-checked),
`screenshot_finding`, and `screenshot_evidence`. An article's overall `criticality` is
max(text criticality, screenshot criticality).

## report.html / report.pdf sections
Executive summary (counts by criticality/type/freshness/readiness) → Quick Wins
(CRITICAL/HIGH + Quick Fix) → findings (interactive: filter/sort/search + collapsible detail)
→ per-type breakdown → backlog → methodology. report.pdf is the print snapshot of report.html.
No markdown report is produced.

## CSV
Columns and sort order are defined in build_report.py (CSV_COLUMNS, sort_key). No SEO columns.
