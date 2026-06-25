# SKB Reports Overhaul + Screenshot Pass E — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trim the audit to 4 deliverables (interactive taste-skill HTML, designed PDF, full CSV, backlog CSV) and add a vision-based screenshot-accuracy pass (Pass E).

**Architecture:** `build_report.py` becomes the single report engine: it writes an interactive, self-contained `report.html` (vanilla JS filters/sort/search/collapse + SVG charts), prints it to `report.pdf` via a Node Playwright script, and writes the two CSVs; markdown is dropped. Pass E is a new serial, agent-orchestrated judgment pass that fetches each article's images and checks integrity + match-to-steps + outdated-UI (live-compared against a configurable reference WP site via the Playwright MCP, auto-installed), emitting `screenshot_*` fields that flow into the report.

**Tech Stack:** Python 3 (stdlib + pyyaml), Node + `playwright` (Chromium) for PDF + live capture, Playwright MCP for Pass E navigation, pytest.

## Global Constraints

- Reports are **self-contained**: single files, inline CSS/JS, **zero** external/CDN/font/network requests. Embed assets as data URIs.
- **Anti-slop / taste-skill:** no decorative gradients or motion; no em-dashes in report chrome; editorial high-density layout; system fonts; tabular numerals; semantic severity palette CRITICAL `#b91c1c`, HIGH `#c2410c`, MEDIUM `#a16207`, LOW `#2563eb`, NONE `#16a34a` on a neutral slate base. Use `design-taste-frontend` / `artifact-design` skills when authoring the HTML.
- **No truncation** of findings: long lists collapse, never "…and N more". **No SEO columns** in any CSV.
- Exactly **4 deliverables**; `report.md` is removed.
- Commit author for every commit: `Shivam Tyagi <shivammtyagi@users.noreply.github.com>`; end messages with the `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer. Prefix git with `DEVELOPER_DIR=/Library/Developer/CommandLineTools` while the Xcode-license gate is active.
- Tests must pass after every task (`python3 -m pytest tests/ -q`).

## File structure

- `scripts/build_report.py` — report engine (CSV, interactive HTML, PDF orchestration); `write_markdown` removed.
- `scripts/print_pdf.js` *(new)* — Node Playwright HTML→PDF.
- `scripts/lib/images.py` *(new)* — `extract_images(article)`.
- `scripts/extract_images.py` *(new)* — CLI building `image-worklist.json`.
- `scripts/lib/config.py` — validate optional `reference_site`.
- `audit-config.example.yml`, `references/config-setup.md` — `reference_site` block + setup question.
- `references/phases.md` — Pass E documentation.
- `references/report-design.md` — fuller taste-skill + interactivity + PDF spec.
- `SKILL.md` — Phase-6 command/gate; Pass E in the phase list; Setup note (Playwright auto-install).
- `tests/test_build_report.py`, `tests/test_images.py` *(new)*, `tests/test_config.py` — coverage.

---

## PART A — Report overhaul

### Task A1: Add screenshot_* columns to the CSV contract

**Files:** Modify `scripts/build_report.py` (CSV_COLUMNS, _FIELD_MAP); Test `tests/test_build_report.py`.

**Interfaces:** Produces CSV columns `Screenshot Status`, `Screenshot Finding`, `Screenshot Evidence` mapped to article keys `screenshot_status`, `screenshot_finding`, `screenshot_evidence`. Pass E (Part B) populates these keys; empty string when absent.

- [ ] **Step 1: Failing test** — add to `test_build_report.py`:
```python
def test_csv_has_screenshot_columns(tmp_path):
    from build_report import write_csv, CSV_COLUMNS
    assert "Screenshot Status" in CSV_COLUMNS
    findings = {"articles": [{"title": "A", "url": "u", "type": "product",
        "criticality": "NONE", "effort": "Quick Fix", "screenshot_status": "Outdated",
        "screenshot_finding": "old menu", "screenshot_evidence": "shot.png"}], "backlog": []}
    p = tmp_path / "o.csv"; write_csv(findings, str(p))
    import csv
    row = next(csv.DictReader(open(p, encoding="utf-8-sig")))
    assert row["Screenshot Status"] == "Outdated" and row["Screenshot Evidence"] == "shot.png"
    for banned in ("Focus Keyword", "Meta Description"): assert banned not in ",".join(CSV_COLUMNS)
```
- [ ] **Step 2: Run, verify fail** — `python3 -m pytest tests/test_build_report.py::test_csv_has_screenshot_columns -v` → FAIL (KeyError / column missing).
- [ ] **Step 3: Implement** — insert after `"Has Visuals"` group in `CSV_COLUMNS`: `"Screenshot Status", "Screenshot Finding", "Screenshot Evidence",` and in `_FIELD_MAP`: `"Screenshot Status": "screenshot_status", "Screenshot Finding": "screenshot_finding", "Screenshot Evidence": "screenshot_evidence",`.
- [ ] **Step 4: Run, verify pass.**
- [ ] **Step 5: Commit** — `feat(report): add screenshot_* CSV columns`.

### Task A2: Interactive, taste-skill HTML report

**Files:** Modify `scripts/build_report.py` (`write_html`); Test `tests/test_build_report.py`.

**Interfaces:** Consumes `findings = {articles:[...], backlog:[...]}` (article keys incl. `screenshot_status/finding/evidence`). Produces a single self-contained `report.html`.

**Authoring note:** invoke `anthropic-skills:design-taste-frontend` (or `artifact-design`) while writing the markup/CSS so the visual design is taste-skill-grade. Calibration: high DENSITY, low-moderate VARIANCE, subtle MOTION.

Required HTML capabilities (the test asserts the hooks; the design skill decides the look):
- Summary dashboard: stat cards + **pure SVG/CSS** charts for criticality/type/freshness/readiness (no chart lib).
- Findings **table** with: filter chips (`data-filter` for severity/type/freshness), a search `<input id="finding-search">`, sortable headers (`<th data-sort=...>` + JS), and per-row collapsible detail (evidence/action/screenshot).
- Quick Wins, Per-Type breakdown, Backlog, Methodology sections. All findings rendered (no truncation).
- One `<style>` (incl. `@media print { ... }` hiding `.controls`, expanding `details`) and one `<script>` (vanilla JS). No `http`/`https` resource refs, no `cdn`.

- [ ] **Step 1: Failing test**:
```python
def test_html_interactive_and_self_contained(tmp_path):
    from build_report import write_html
    findings = {"articles": [{"title": "Crit", "url": "u1", "type": "product",
        "criticality": "CRITICAL", "effort": "Quick Fix", "freshness": "Stale",
        "support_readiness": "Misleading", "accuracy_finding": "x", "evidence": "f.php:1",
        "action": "fix", "screenshot_status": "Outdated", "screenshot_finding": "old",
        "screenshot_evidence": "s.png"}], "backlog": []}
    p = tmp_path / "report.html"; write_html(findings, {"team": "T"}, str(p))
    h = open(p, encoding="utf-8").read()
    assert "<style>" in h and "<script>" in h
    assert "cdn" not in h.lower()
    import re
    assert not re.search(r'(href|src)\s*=\s*"https?://', h)   # no network refs
    assert "@media print" in h
    assert 'id="finding-search"' in h and "data-filter" in h and "data-sort" in h
    assert "CRITICAL" in h and "#b91c1c" in h
    assert "Outdated" in h            # screenshot finding surfaced
    assert "—" not in h          # em-dash ban in chrome
```
- [ ] **Step 2: Run, verify fail.**
- [ ] **Step 3: Implement** `write_html` per the capabilities above (use the design skill). Keep `_SEVERITY_CSS`; build cards, SVG charts, the interactive table, sections, `@media print`, and the JS (filter/search/sort/collapse). Ensure no em-dash characters in any template literal.
- [ ] **Step 4: Run, verify pass** (+ full suite).
- [ ] **Step 5: Commit** — `feat(report): interactive, taste-skill HTML report`.

### Task A3: Node Playwright print script

**Files:** Create `scripts/print_pdf.js`; Test `tests/test_build_report.py`.

**Interfaces:** CLI `node scripts/print_pdf.js <input.html> <output.pdf>`; exit 0 on success.

```javascript
// scripts/print_pdf.js
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const [, , inFile, outFile] = process.argv;
  if (!inFile || !outFile) { console.error('usage: print_pdf.js <html> <pdf>'); process.exit(2); }
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(inFile), { waitUntil: 'networkidle' });
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: outFile, format: 'A4', printBackground: true,
    margin: { top: '14mm', bottom: '14mm', left: '12mm', right: '12mm' } });
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
```

- [ ] **Step 1: Write the file** (above).
- [ ] **Step 2: Syntax check** — `node --check scripts/print_pdf.js` → no output, exit 0.
- [ ] **Step 3: Test (presence + valid JS)**:
```python
def test_print_pdf_script_exists():
    import subprocess, os
    p = os.path.join(os.path.dirname(__file__), "..", "scripts", "print_pdf.js")
    assert os.path.exists(p)
    r = subprocess.run(["node", "--check", p], capture_output=True)
    assert r.returncode == 0, r.stderr
```
(If `node` is unavailable in CI, mark `@pytest.mark.skipif(shutil.which('node') is None)`.)
- [ ] **Step 4: Run, verify pass/skip.**
- [ ] **Step 5: Commit** — `feat(report): add Node Playwright HTML->PDF print script`.

### Task A4: Wire PDF + drop markdown in main()

**Files:** Modify `scripts/build_report.py` (`main`, add `_ensure_playwright`, `_render_pdf`); Test `tests/test_build_report.py`.

**Interfaces:** `main()` writes `report.html`, `report.pdf`, `skb-audit-<date>.csv`, `new-articles-backlog.csv`; never `report.md`. `_render_pdf(html_path, pdf_path)` runs `node print_pdf.js`; on missing node/playwright runs `npx -y playwright install chromium` (and warns to `npm i playwright` if the package is absent); raises if it still cannot produce the PDF.

- [ ] **Step 1: Failing test** (markdown gone; html+csvs always; pdf attempted):
```python
def test_main_outputs_no_markdown(tmp_path, monkeypatch):
    import build_report, json, os
    monkeypatch.setattr(build_report, "_render_pdf", lambda h, p: open(p, "w").write("%PDF-1.4 stub"))
    findings = {"articles": [{"title":"A","url":"u","type":"product","criticality":"NONE","effort":"Quick Fix"}], "backlog": []}
    fp = tmp_path/"f.json"; json.dump(findings, open(fp,"w"))
    cfgp = tmp_path/"c.yml"; open(cfgp,"w").write("team: T\ncontent_source:\n  wxr_export: x\n  post_types: [r]\n  taxonomies: {category: c, tag: t}\nproducts:\n  - {name: P, repo: o/r, match: {categories: ['*']}}\n")
    out = tmp_path/"report"
    build_report.main_with_args(str(cfgp), str(fp), str(out), date="2026-06-25")  # see Step 3
    files = set(os.listdir(out))
    assert "report.html" in files and "report.pdf" in files
    assert "skb-audit-2026-06-25.csv" in files and "new-articles-backlog.csv" in files
    assert "report.md" not in files
```
- [ ] **Step 2: Run, verify fail.**
- [ ] **Step 3: Implement** — refactor `main()` to call a testable `main_with_args(config, findings, out_dir, date=None)`: load cfg, write CSV, backlog CSV, `write_html`, then `_render_pdf(html, pdf)`. Remove the `write_markdown` call and the `--html` flag (HTML always on). Add `_ensure_playwright()` and `_render_pdf()` (subprocess to `node scripts/print_pdf.js`; on failure attempt `npx -y playwright install chromium`; raise `RuntimeError` if still failing). Keep `write_markdown` deletion (remove the function).
- [ ] **Step 4: Run, verify pass** (+ full suite).
- [ ] **Step 5: Commit** — `feat(report): produce html+pdf+csvs, drop markdown report`.

### Task A5: Docs — gate, command, report-design

**Files:** Modify `SKILL.md`, `references/report-design.md`.

- [ ] **Step 1:** In `SKILL.md` Phase 6: change the command to drop `--html` (HTML always produced) and update the gate to: "report.html + report.pdf + dated CSV + backlog CSV exist; CSV one row per article." Remove `report.md` mentions.
- [ ] **Step 2:** Rewrite `references/report-design.md` to document: the 4 deliverables, the interactivity (filters/sort/search/collapse/charts), the `@media print` → PDF flow, the self-contained/no-CDN rule, the em-dash ban, and the taste-skill calibration (density/variance/motion).
- [ ] **Step 3: Commit** — `docs: update report gate + report-design for 4-output interactive reports`.

---

## PART B — Screenshot Pass E

### Task B1: Image extraction helper

**Files:** Create `scripts/lib/images.py`; Test `tests/test_images.py`.

**Interfaces:** Produces `extract_images(article) -> list[dict]` with keys `src`, `alt`, `nearby_step_text` (the ~200 chars of body_text/HTML text preceding the img). Consumes an `Article` (has `body_html`, `body_text`).

- [ ] **Step 1: Failing test** (`tests/test_images.py`):
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.images import extract_images

class A:
    def __init__(self, html, text=""): self.body_html = html; self.body_text = text

def test_extracts_src_and_alt():
    a = A('<p>Go to Sitemaps</p><img src="https://k/s.png" alt="Sitemap screen">')
    imgs = extract_images(a)
    assert imgs[0]["src"] == "https://k/s.png"
    assert imgs[0]["alt"] == "Sitemap screen"
    assert "Sitemaps" in imgs[0]["nearby_step_text"]

def test_no_images():
    assert extract_images(A("<p>no pics</p>")) == []
```
- [ ] **Step 2: Run, verify fail.**
- [ ] **Step 3: Implement** — regex out `<img ...>` tags, capture `src` and `alt`; for `nearby_step_text`, strip tags from the HTML before each img and take the trailing ~200 chars.
- [ ] **Step 4: Run, verify pass.**
- [ ] **Step 5: Commit** — `feat(images): extract_images() for screenshot worklist`.

### Task B2: Worklist CLI

**Files:** Create `scripts/extract_images.py`; Test `tests/test_images.py`.

**Interfaces:** CLI `python3 scripts/extract_images.py --articles <articles.json> --out <worklist.json>`; writes `[{article_id, title, type, url, images:[{src,alt,nearby_step_text}]}]` for articles that have ≥1 image.

- [ ] **Step 1: Failing test** — call `build_worklist(articles)` (importable) and assert only image-bearing articles appear with their images.
- [ ] **Step 2: Run, verify fail.**
- [ ] **Step 3: Implement** — `load_articles`, map each via `extract_images`, keep non-empty, `argparse` main writing JSON. Run from working dir with the skill `scripts/` dir on `sys.path` (same convention as other scripts).
- [ ] **Step 4: Run, verify pass.**
- [ ] **Step 5: Commit** — `feat(images): extract_images.py worklist CLI`.

### Task B3: Validate optional reference_site in config

**Files:** Modify `scripts/lib/config.py`; Test `tests/test_config.py`.

**Interfaces:** `load_config` accepts an optional `reference_site` dict; if present it must have `url`, `admin_user`, and one of `admin_pass`/`admin_pass_env`, else `ConfigError`. Absent is valid.

- [ ] **Step 1: Failing tests**:
```python
def test_reference_site_optional(tmp_path):  # absent is fine
    cfg = _base(tmp_path); cfg_path = _write(tmp_path, cfg)
    load_config(cfg_path)  # no raise

def test_reference_site_requires_fields(tmp_path):
    cfg = _base(tmp_path); cfg["reference_site"] = {"url": "https://x"}
    import pytest
    with pytest.raises(Exception):
        load_config(_write(tmp_path, cfg))
```
(`_base`/`_write` helpers build a minimal valid config dict + write YAML.)
- [ ] **Step 2: Run, verify fail.**
- [ ] **Step 3: Implement** — in `_validate`, if `cfg.get("reference_site")`: require `url`, `admin_user`, and (`admin_pass` or `admin_pass_env`).
- [ ] **Step 4: Run, verify pass.**
- [ ] **Step 5: Commit** — `feat(config): validate optional reference_site block`.

### Task B4: Config example + setup question

**Files:** Modify `audit-config.example.yml`, `references/config-setup.md`.

- [ ] **Step 1:** Add to `audit-config.example.yml` a commented `reference_site` block (url, admin_user, admin_pass_env) with a note: optional; full wp-admin access; password via env var.
- [ ] **Step 2:** Add an optional question to `references/config-setup.md` (the throwaway-WP-site question; make full-access explicit; env var for the password).
- [ ] **Step 3: Commit** — `docs(config): document optional reference_site for screenshot checks`.

### Task B5: Pass E documentation (phases + SKILL)

**Files:** Modify `references/phases.md`, `SKILL.md`.

- [ ] **Step 1:** In `references/phases.md`, add **Pass E — Visual / screenshot accuracy** (serial, agent-orchestrated): inputs (image worklist), the three checks (integrity / match-to-steps / outdated), the Playwright MCP preflight + auto-install (with the session-reload/resume caveat), the within-run screen cache, per-article fallback, the AIOSEO-only live-compare scope, and the evidence rule (HIGH must cite a live capture and/or code line). Emits `screenshot_status/finding/evidence`; row criticality = max(text, screenshot).
- [ ] **Step 2:** In `SKILL.md`: add Pass E to the Phase-5 pass list (always-on); add a Setup note that when `reference_site` is set, Pass E auto-installs the Playwright MCP + Chromium; note the reference site should match the audited AIOSEO version.
- [ ] **Step 3: Commit** — `docs: document always-on Pass E (visual/screenshot accuracy)`.

---

## Self-review checklist (run after writing)

- Spec coverage: report spec → A1–A5 (4 outputs, interactive, PDF, drop md, gate); Pass E spec → B1–B5 (config, images, docs/preflight, screenshot fields). Live-navigation runtime is agent-orchestrated (documented, not unit-tested) — flagged.
- Placeholder scan: none.
- Type consistency: `screenshot_status/finding/evidence` keys consistent across A1, A2, B5; `extract_images` shape consistent across B1/B2; `_render_pdf`/`main_with_args` names consistent across A4 + tests.
