import sys, os, csv
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from build_report import write_csv, CSV_COLUMNS, sort_key

def test_csv_has_no_seo_columns_and_bom(tmp_path):
    findings = {"articles": [
        {"title": "B", "url": "u2", "type": "product", "criticality": "LOW", "effort": "Medium"},
        {"title": "A", "url": "u1", "type": "product", "criticality": "CRITICAL", "effort": "Quick Fix"},
    ], "backlog": []}
    p = tmp_path / "out.csv"
    write_csv(findings, str(p))
    raw = open(p, "rb").read()
    assert raw[:3] == b"\xef\xbb\xbf"                  # UTF-8 BOM
    header = open(p, encoding="utf-8-sig").readline()
    for banned in ("Focus Keyword", "Funnel Stage", "Meta Description"):
        assert banned not in header
    assert "Support-Readiness" in header
    rows = list(csv.DictReader(open(p, encoding="utf-8-sig")))
    assert rows[0]["Title"] == "A"                     # CRITICAL sorts first

def test_sort_key_orders_criticality_then_effort():
    assert sort_key({"criticality": "CRITICAL", "effort": "Quick Fix"}) < \
           sort_key({"criticality": "CRITICAL", "effort": "Rewrite"})
    assert sort_key({"criticality": "CRITICAL", "effort": "Rewrite"}) < \
           sort_key({"criticality": "HIGH", "effort": "Quick Fix"})

def test_html_is_self_contained(tmp_path):
    from build_report import write_html
    findings = {"articles": [{"title": "A", "url": "u1", "type": "product",
                "criticality": "CRITICAL", "effort": "Quick Fix",
                "accuracy_finding": "Outdated", "evidence": "myplugin.php:42"}],
                "backlog": []}
    cfg = {"team": "TestTeam"}
    p = tmp_path / "report.html"
    write_html(findings, cfg, str(p))
    html = open(p, encoding="utf-8").read()
    assert "http://" not in html and "https://u1" not in html.replace('href="u1"', "")
    assert "cdn" not in html.lower()
    assert "<style>" in html                       # inline CSS
    assert "TestTeam" in html
    assert "CRITICAL" in html

def test_print_pdf_script_exists():
    import subprocess, os, shutil
    p = os.path.join(os.path.dirname(__file__), "..", "scripts", "print_pdf.js")
    assert os.path.exists(p)
    if shutil.which("node"):
        r = subprocess.run(["node", "--check", p], capture_output=True)
        assert r.returncode == 0, r.stderr

def test_html_interactive_and_self_contained(tmp_path):
    from build_report import write_html
    findings = {"articles": [{"title": "Crit", "url": "u1", "type": "product",
        "criticality": "CRITICAL", "effort": "Quick Fix", "freshness": "Stale",
        "support_readiness": "Misleading", "accuracy_finding": "x", "evidence": "f.php:1",
        "action": "fix", "screenshot_status": "Outdated", "screenshot_finding": "old",
        "screenshot_evidence": "s.png"}], "backlog": []}
    p = tmp_path / "report.html"
    write_html(findings, {"team": "T"}, str(p))
    h = open(p, encoding="utf-8").read()
    assert "<style>" in h and "<script>" in h
    assert "cdn" not in h.lower()
    import re
    assert not re.search(r'(href|src)\s*=\s*"https?://', h)   # no network refs in chrome
    assert "@media print" in h
    assert 'id="finding-search"' in h and "data-filter" in h and "data-sort" in h
    assert "CRITICAL" in h and "#b91c1c" in h
    assert "Outdated" in h            # screenshot finding surfaced
    assert "—" not in h          # em-dash ban in chrome

def test_csv_has_screenshot_columns(tmp_path):
    findings = {"articles": [{"title": "A", "url": "u", "type": "product",
        "criticality": "NONE", "effort": "Quick Fix", "screenshot_status": "Outdated",
        "screenshot_finding": "old menu", "screenshot_evidence": "shot.png"}], "backlog": []}
    p = tmp_path / "o.csv"
    write_csv(findings, str(p))
    import csv as _csv
    row = next(_csv.DictReader(open(p, encoding="utf-8-sig")))
    assert row["Screenshot Status"] == "Outdated"
    assert row["Screenshot Evidence"] == "shot.png"
    for banned in ("Focus Keyword", "Meta Description"):
        assert banned not in ",".join(CSV_COLUMNS)

def test_markdown_has_spec_sections(tmp_path):
    from build_report import write_markdown
    findings = {"articles": [
        {"title": "Crit One", "url": "u1", "type": "product", "repo": "o/r",
         "criticality": "CRITICAL", "effort": "Quick Fix", "freshness": "Stale",
         "support_readiness": "Misleading", "accuracy_finding": "wrong",
         "evidence": "x.php:1", "action": "fix it", "recommendation": "Update"},
        {"title": "Fine Doc", "url": "u2", "type": "operational", "criticality": "NONE",
         "effort": "Quick Fix", "freshness": "Fresh", "support_readiness": "Usable"},
    ], "backlog": [
        {"title": "New Doc", "type": "product", "demand": "many", "source": "issue #9",
         "outline": "o", "priority": "High"}]}
    p = tmp_path / "report.md"
    write_markdown(findings, {"team": "T"}, str(p))
    md = open(p, encoding="utf-8").read()
    for section in ["# SKB Audit Report — T", "## Executive Summary", "## Quick Wins",
                    "## Findings", "## Per-Type Breakdown", "## New-Article Backlog",
                    "## Methodology"]:
        assert section in md, f"missing section: {section}"
    assert "By freshness:" in md and "By support-readiness:" in md
    assert "Crit One" in md and "New Doc" in md         # finding + backlog listed
    assert "#### Fine Doc" not in md                    # NONE articles not listed individually

def test_backlog_csv(tmp_path):
    from build_report import write_backlog_csv
    findings = {"articles": [], "backlog": [
        {"title": "Doc X", "type": "product", "demand": 12, "source": "issue #1",
         "outline": "intro/steps", "priority": "HIGH"}]}
    p = tmp_path / "backlog.csv"
    write_backlog_csv(findings, str(p))
    import csv as _csv
    rows = list(_csv.DictReader(open(p, encoding="utf-8-sig")))
    assert rows[0]["Suggested Title"] == "Doc X"
