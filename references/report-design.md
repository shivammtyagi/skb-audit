# Report Design

The audit produces exactly **four deliverables** (no markdown report):

1. `report.html` — interactive, self-contained, taste-skill-designed.
2. `report.pdf` — a designed static snapshot of the HTML (rendered via Playwright HTML→PDF).
3. `skb-audit-<date>.csv` — full per-article record (one row per article).
4. `new-articles-backlog.csv` — the ranked new-article gaps.

Design principles are distilled from the taste-skill (anti-slop) + no-truncation and BAKED IN to
`build_report.py` — no runtime dependency on those skills.

## HTML (taste-skill, self-contained)

- **Self-contained:** single file, inline CSS + JS, **ZERO** external/CDN/font/network requests. Embed
  any asset as a data URI. (Article hyperlinks are content, not resource refs.)
- **Anti-slop:** no AI-purple, no decorative gradients, no gratuitous motion; **no em-dashes in the
  report chrome** (use middots / hyphens). Editorial, high-density layout (Notion/Linear feel).
- **Color:** restrained neutral base (slate/zinc) + a SEMANTIC severity palette (CRITICAL `#b91c1c`,
  HIGH `#c2410c`, MEDIUM `#a16207`, LOW `#2563eb`, NONE `#16a34a`). Accent = meaning, not decoration.
- **Typography:** system sans, clear hierarchy, tabular numerals for counts.
- **Sections:** header + scope; summary (severity stat cards + pure-SVG/CSS charts for
  criticality/type/freshness/readiness); Quick Wins; interactive Findings table; Per-Type breakdown;
  New-Article Backlog; Methodology + artifact pointers.
- **Completeness:** never truncate findings or drop rows; every article appears in the findings table.

## Interactivity (vanilla JS, no network)

- Filter chips for severity / type / freshness (toggle rows).
- Findings table: click-to-sort columns + a search box (`#finding-search`).
- Per-row collapsible detail (URL, evidence, action, known-issue, screenshot) — collapsed by default.
- Degrades gracefully: with JS off, all rows stay visible.

## PDF (Playwright HTML→PDF)

- `scripts/print_pdf.js` (Node + `playwright`) loads `report.html`, applies `@media print`, and writes
  `report.pdf` (A4, backgrounds on). `build_report._render_pdf` invokes it and auto-installs
  `playwright` + Chromium on first failure.
- The HTML's `@media print` block hides interactive controls and expands all collapsibles so the PDF is
  a complete, designed static snapshot.

## Calibration (taste-skill dials)

High DENSITY (data-dense report), low-to-moderate VARIANCE (crisp/editorial, not experimental), subtle
MOTION (none beyond hover). When authoring/redesigning the markup, the `design-taste-frontend` /
`artifact-design` skills may be used, but the shipped output must remain self-contained and match the
rules above.
