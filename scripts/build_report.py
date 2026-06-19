import argparse
import csv
import json

CSV_COLUMNS = [
    "Title", "URL", "Type", "Product/Repo", "Category", "Tags", "Author",
    "Last Modified", "Freshness", "Word Count", "Support-Readiness", "Findability",
    "Accuracy Finding", "Evidence", "Duplicate-Of", "Known-Issue Status",
    "Has Steps", "Has Visuals", "Internal Links", "Criticality", "Effort",
    "Recommendation", "Action Required", "Assigned To", "Status",
]
_CRIT = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "NONE": 4}
_EFFORT = {"Quick Fix": 0, "Medium": 1, "Rewrite": 2}

def sort_key(row):
    return (_CRIT.get(row.get("criticality", "NONE"), 4),
            _EFFORT.get(row.get("effort", "Medium"), 1))

_FIELD_MAP = {
    "Title": "title", "URL": "url", "Type": "type", "Product/Repo": "repo",
    "Category": "category", "Tags": "tags", "Author": "author",
    "Last Modified": "modified", "Freshness": "freshness", "Word Count": "word_count",
    "Support-Readiness": "support_readiness", "Findability": "findability",
    "Accuracy Finding": "accuracy_finding", "Evidence": "evidence",
    "Duplicate-Of": "duplicate_of", "Known-Issue Status": "known_issue_status",
    "Has Steps": "has_steps", "Has Visuals": "has_visuals",
    "Internal Links": "internal_links", "Criticality": "criticality",
    "Effort": "effort", "Recommendation": "recommendation",
    "Action Required": "action", "Assigned To": "assigned_to", "Status": "status",
}

def write_csv(findings, path):
    rows = sorted(findings.get("articles", []), key=sort_key)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            out = {}
            for col, key in _FIELD_MAP.items():
                v = r.get(key, "")
                if isinstance(v, list):
                    v = ", ".join(str(x) for x in v)
                out[col] = str(v).replace("\n", " ").replace("\r", " ").strip()
            writer.writerow(out)
    return len(rows)

_SEVERITY_CSS = {
    "CRITICAL": "#b91c1c", "HIGH": "#c2410c", "MEDIUM": "#a16207",
    "LOW": "#2563eb", "NONE": "#16a34a",
}
# Report visual design distilled from the taste-skill (anti-slop, semantic color,
# tabular numerals) + output-skill (no truncation). Adapted for a data-dense report.
_BASE_CSS = """
:root{--bg:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;}
*{box-sizing:border-box;} body{margin:0;background:var(--bg);color:var(--fg);
font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
line-height:1.5;} .wrap{max-width:1100px;margin:0 auto;padding:40px 24px;}
h1{font-size:28px;margin:0 0 4px;} .muted{color:var(--muted);}
table{border-collapse:collapse;width:100%;margin:16px 0;font-variant-numeric:tabular-nums;}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);
font-size:14px;vertical-align:top;} th{color:var(--muted);font-weight:600;}
.badge{display:inline-block;padding:2px 8px;border-radius:999px;color:#fff;font-size:12px;}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;margin:16px 0;}
.card{border:1px solid var(--line);border-radius:10px;padding:14px;}
.card .n{font-size:24px;font-weight:700;font-variant-numeric:tabular-nums;}
.overflow{overflow-x:auto;}
"""

def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))

def _counts(findings):
    c = {}
    for a in findings.get("articles", []):
        k = a.get("criticality", "NONE")
        c[k] = c.get(k, 0) + 1
    return c

def write_markdown(findings, cfg, path):
    c = _counts(findings)
    lines = [f"# SKB Audit Report — {cfg.get('team','')}", "",
             "## Executive Summary", ""]
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE"]:
        lines.append(f"- {sev}: {c.get(sev, 0)}")
    lines += ["", "## Findings", ""]
    for a in sorted(findings.get("articles", []), key=sort_key):
        if a.get("criticality", "NONE") == "NONE":
            continue
        lines.append(f"### [{a.get('criticality')}] {a.get('title','')}")
        lines.append(f"- URL: {a.get('url','')}")
        lines.append(f"- Finding: {a.get('accuracy_finding','')}")
        lines.append(f"- Evidence: {a.get('evidence','')}")
        lines.append(f"- Action: {a.get('action','')}")
        lines.append("")
    if findings.get("backlog"):
        lines += ["## New-Article Backlog", ""]
        for b in findings["backlog"]:
            lines.append(f"- {b.get('title','')} (demand: {b.get('demand','')}, {b.get('source','')})")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def write_html(findings, cfg, path):
    c = _counts(findings)
    cards = "".join(
        f'<div class="card"><div class="n" style="color:{_SEVERITY_CSS.get(s, "#64748b")}">{c.get(s,0)}</div>'
        f'<div class="muted">{s}</div></div>' for s in ["CRITICAL","HIGH","MEDIUM","LOW","NONE"])
    rows = ""
    for a in sorted(findings.get("articles", []), key=sort_key):
        sev = a.get("criticality", "NONE")
        rows += (f'<tr><td><span class="badge" style="background:{_SEVERITY_CSS.get(sev, "#64748b")}">{sev}</span></td>'
                 f'<td>{_esc(a.get("title",""))}</td><td>{_esc(a.get("type",""))}</td>'
                 f'<td>{_esc(a.get("accuracy_finding",""))}</td>'
                 f'<td>{_esc(a.get("evidence",""))}</td>'
                 f'<td>{_esc(a.get("action",""))}</td></tr>')
    html = (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>SKB Audit — {_esc(cfg.get('team',''))}</title><style>{_BASE_CSS}</style></head>"
            f"<body><div class='wrap'><h1>SKB Audit Report</h1>"
            f"<p class='muted'>{_esc(cfg.get('team',''))}</p>"
            f"<div class='cards'>{cards}</div>"
            f"<div class='overflow'><table><thead><tr><th>Severity</th><th>Article</th>"
            f"<th>Type</th><th>Finding</th><th>Evidence</th><th>Action</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div></div></body></html>")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

def write_backlog_csv(findings, path):
    cols = ["Suggested Title", "Type", "Demand", "Source", "Suggested Outline", "Priority"]
    fmap = {"Suggested Title": "title", "Type": "type", "Demand": "demand",
            "Source": "source", "Suggested Outline": "outline", "Priority": "priority"}
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for b in findings.get("backlog", []):
            w.writerow({col: str(b.get(key, "")).replace("\n", " ") for col, key in fmap.items()})

def main():
    import datetime, os
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--findings", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--html", action="store_true")
    args = ap.parse_args()
    from lib.config import load_config
    cfg = load_config(args.config)
    findings = json.load(open(args.findings, encoding="utf-8"))
    os.makedirs(args.out_dir, exist_ok=True)
    today = os.environ.get("SKB_AUDIT_DATE", str(datetime.date.today()))
    n = write_csv(findings, os.path.join(args.out_dir, f"skb-audit-{today}.csv"))
    write_backlog_csv(findings, os.path.join(args.out_dir, "new-articles-backlog.csv"))
    write_markdown(findings, cfg, os.path.join(args.out_dir, "report.md"))
    if args.html:
        write_html(findings, cfg, os.path.join(args.out_dir, "report.html"))
    print(f"Report written: {n} article rows, html={'yes' if args.html else 'no'}")

if __name__ == "__main__":
    main()
