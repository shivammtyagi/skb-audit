# Report & findings.json contract

## findings.json
{
  "articles": [ { ...Article fields..., "criticality","effort","recommendation","action",
                  "evidence","accuracy_finding","duplicate_of","known_issue_status",
                  "support_readiness","findability","has_steps","has_visuals",
                  "assigned_to","status" } ],
  "backlog": [ { "title","type","demand","source","outline","priority" } ]
}

## report.md sections
Executive summary (counts by criticality/type/freshness/readiness) → Quick Wins
(CRITICAL/HIGH + Quick Fix) → findings grouped by the four priorities → per-type breakdown
→ backlog summary → methodology + _internal pointers.

## CSV
Columns and sort order are defined in build_report.py (CSV_COLUMNS, sort_key). No SEO columns.
