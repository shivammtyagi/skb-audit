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
