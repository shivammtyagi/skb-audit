# Spec — Report Overhaul: 4 deliverables, interactive HTML, designed PDF

- **Date:** 2026-06-25
- **Status:** Design approved (Q&A); pending implementation plan
- **Skill:** `skb-audit`
- **Author:** Shivam Tyagi (with Claude)

## Motivation

`build_report.py` currently emits `report.md` + dated CSV + backlog CSV + a basic optional HTML. The
HTML/PDF are not fully taste-skill-aligned, there is no PDF, and the markdown report is redundant. Trim
to four high-quality deliverables, make the HTML interactive and properly designed (anti-slop /
taste-skill), and add a designed PDF.

## Deliverables — exactly four

1. `report.html` — interactive, taste-skill-designed (always produced; no `--html` flag).
2. `report.pdf` — taste-skill-designed; a complete static print snapshot of the HTML (all findings
   expanded, interactive controls hidden).
3. `skb-audit-<date>.csv` — full per-article CSV (one row per article; existing columns + the new
   `screenshot_*` columns from Pass E).
4. `new-articles-backlog.csv` — unchanged.

**Dropped:** `report.md` (remove `write_markdown` from the pipeline).

## Phase-6 gate update

Was: `report.md` + dated CSV + backlog CSV exist. **Now:** `report.html` + `report.pdf` + dated CSV +
backlog CSV exist; CSV has one row per audited article.

## HTML design (taste-skill)

- **Anti-slop:** no AI-purple/decorative gradients, no gratuitous motion, no em-dashes in the report
  chrome. Editorial, high-density (Notion/Linear feel). System font stack, tabular numerals. Restrained
  neutral (slate/zinc) base carrying the **semantic severity palette** (CRITICAL `#b91c1c`, HIGH
  `#c2410c`, MEDIUM `#a16207`, LOW `#2563eb`, NONE `#16a34a`). Built via the `design-taste-frontend` /
  `artifact-design` skills at implementation time.
- **Self-contained:** single file, inline CSS + JS, **zero** external/CDN/font/network requests
  (CSP-safe). Any assets embedded as data URIs.
- **Sections:** header + scope; summary dashboard (stat cards + charts for criticality / type /
  freshness / readiness); Quick Wins; Findings (interactive table + expandable detail); Per-Type
  breakdown; New-Article Backlog; Methodology + artifacts. **No truncation** — long lists collapse,
  never "…and N more".

## Interactivity (self-contained vanilla JS, no network)

- **Filter chips:** severity, type, freshness (toggle rows on/off).
- **Findings table:** click-to-sort columns; a text search box filters rows.
- **Collapsible finding details:** evidence/action expand on click; collapsed by default.
- **Summary charts:** pure SVG/CSS (no chart-library), reflecting the counts.
- Degrades gracefully: with JS disabled, all rows remain visible (static).

## PDF generation (Playwright HTML→PDF)

- New `scripts/print_pdf.js` (Node, uses the `playwright` package): `node print_pdf.js <html> <pdf>`
  launches headless Chromium, loads the file, and calls `page.pdf({ format: 'A4', printBackground: true })`.
- `build_report.py` invokes it after writing `report.html`. If Node + Playwright are missing it runs the
  **same auto-setup routine as Pass E** (`npx playwright install chromium`); if it still cannot run, it
  errors clearly (PDF is a required deliverable, not optional).
- The HTML carries an `@media print` stylesheet that hides interactive controls (filter chips, search,
  sort affordances) and expands all collapsibles, so the PDF is a complete, designed static snapshot.

## Files touched

- `scripts/build_report.py` — rewrite `write_html` (interactive + taste); add the PDF step; remove
  `write_markdown` from `main()`; keep `write_csv` / `write_backlog_csv`; add `screenshot_*` columns
  (coordinated with the Pass E spec).
- `scripts/print_pdf.js` — new Node print script.
- `references/report-design.md` — update to the fuller taste-skill spec + interactivity + PDF.
- `SKILL.md` — Phase-6 command + gate updated (html + pdf + csvs; html always produced; md dropped).
- `tests/test_build_report.py` — assert the four outputs, interactive-HTML markers (filter/search/sort
  hooks; no CDN/network), the print stylesheet, and that no `report.md` is produced; guard/mokc the PDF step.

## Dependencies

- Node + Playwright (Chromium) for the PDF step — shared with Pass E's auto-setup.

## Non-goals

- No server/runtime; the HTML is a static file with embedded JS.
- No external analytics/telemetry/fonts.

## Open questions / future

- If Node/Playwright is unavailable in some environment, a future fallback could ship HTML-only and note
  that the PDF requires the print step.
