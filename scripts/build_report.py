import argparse
import csv
import json
import os

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_COLUMNS = [
    "Title", "URL", "Type", "Product/Repo", "Category", "Tags", "Author",
    "Last Modified", "Freshness", "Word Count", "Support-Readiness", "Findability",
    "Accuracy Finding", "Evidence", "Duplicate-Of", "Known-Issue Status",
    "Has Steps", "Has Visuals", "Screenshot Status", "Screenshot Finding",
    "Screenshot Evidence", "Internal Links", "Criticality", "Effort",
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
    "Screenshot Status": "screenshot_status", "Screenshot Finding": "screenshot_finding",
    "Screenshot Evidence": "screenshot_evidence",
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
# Report visual design: anti-slop / taste-skill (semantic severity color, restrained
# neutral base, system fonts, tabular numerals, high density, no decorative gradients
# or motion, no em-dashes in chrome) + no-truncation. Self-contained: inline CSS/JS,
# zero network. CSS/JS are plain (non-f-string) constants so braces stay literal.
_REPORT_CSS = """
:root{--bg:#fff;--fg:#0f172a;--muted:#64748b;--line:#e2e8f0;--soft:#f8fafc;--accent:#0f172a;}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.5;font-variant-numeric:tabular-nums;}
.wrap{max-width:1180px;margin:0 auto;padding:36px 24px 80px;}
h1{font-size:30px;margin:0 0 2px;letter-spacing:-.01em;}
h2{font-size:19px;margin:36px 0 12px;padding-bottom:6px;border-bottom:2px solid var(--line);}
h3{font-size:14px;margin:18px 0 8px;color:#334155;text-transform:uppercase;letter-spacing:.05em;}
.muted{color:var(--muted);} .small{font-size:12px;} a{color:#0369a1;text-decoration:none;} a:hover{text-decoration:underline;}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px;}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(108px,1fr));gap:10px;margin:14px 0;}
.card{border:1px solid var(--line);border-radius:10px;padding:14px 12px;text-align:center;background:var(--soft);}
.card .n{font-size:30px;font-weight:750;line-height:1;} .card .cl{font-size:11px;letter-spacing:.06em;color:var(--muted);margin-top:6px;text-transform:uppercase;}
.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px;margin:14px 0;}
.chart .ct{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px;}
.row-bar{display:flex;align-items:center;gap:8px;margin:4px 0;font-size:13px;}
.row-bar .lbl{width:104px;color:#475569;flex:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.row-bar .track{flex:1;background:var(--soft);border-radius:4px;height:14px;overflow:hidden;}
.row-bar .fill{height:100%;border-radius:4px;}
.row-bar .v{width:34px;text-align:right;flex:none;color:#475569;}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:14px 0;padding:12px;background:var(--soft);border:1px solid var(--line);border-radius:10px;}
.controls .grp{display:flex;flex-wrap:wrap;gap:6px;align-items:center;}
.controls .glabel{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin-right:2px;}
.chip{cursor:pointer;user-select:none;border:1px solid var(--line);background:#fff;border-radius:999px;padding:3px 10px;font-size:12.5px;color:#334155;}
.chip[aria-pressed="true"]{background:var(--accent);color:#fff;border-color:var(--accent);}
#finding-search{flex:1;min-width:180px;padding:7px 10px;border:1px solid var(--line);border-radius:8px;font-size:13px;}
.overflow{overflow-x:auto;border:1px solid var(--line);border-radius:10px;margin:12px 0;}
table{border-collapse:collapse;width:100%;font-size:13px;}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top;}
th{background:var(--soft);color:var(--muted);font-weight:600;font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;position:sticky;top:0;}
th[data-sort]{cursor:pointer;} th[data-sort]::after{content:"\\2195";opacity:.35;margin-left:5px;font-size:10px;}
tr:last-child td{border-bottom:none;}
.frow{cursor:pointer;} .frow:hover{background:var(--soft);} .frow .twist{display:inline-block;width:12px;color:var(--muted);transition:transform .12s;}
.frow.open .twist{transform:rotate(90deg);}
.badge{display:inline-block;padding:2px 9px;border-radius:999px;color:#fff;font-size:11.5px;font-weight:650;}
.tag{display:inline-block;padding:1px 8px;border:1px solid var(--line);border-radius:999px;font-size:11px;color:#475569;}
.detail{display:none;} .detail.show{display:table-row;} .detail td{background:#fcfcfd;}
.detail .kv{display:grid;grid-template-columns:120px 1fr;gap:8px;margin:4px 0;font-size:13px;}
.detail .k{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.04em;}
.pill{display:inline-block;background:var(--soft);border:1px solid var(--line);border-radius:6px;padding:2px 8px;margin:2px 4px 2px 0;font-size:12.5px;}
.foot{margin-top:40px;padding-top:16px;border-top:1px solid var(--line);font-size:12.5px;color:var(--muted);}
.hidden{display:none!important;}
@media print{
  .controls{display:none!important;} th[data-sort]::after{content:"";}
  .detail{display:table-row!important;} .frow .twist{display:none;}
  .wrap{max-width:none;padding:0;} a{color:inherit;text-decoration:none;}
  h2{break-after:avoid;} tr{break-inside:avoid;}
}
"""

_REPORT_JS = """
(function(){
  var active={severity:new Set(),type:new Set(),freshness:new Set()};
  var search=document.getElementById('finding-search');
  var rows=[].slice.call(document.querySelectorAll('tr.frow'));
  function detailOf(r){var d=r.nextElementSibling;return (d&&d.classList.contains('detail'))?d:null;}
  function matches(r){
    for(var dim in active){ if(active[dim].size && !active[dim].has(r.getAttribute('data-'+dim))) return false; }
    var q=(search&&search.value||'').trim().toLowerCase();
    if(q && (r.getAttribute('data-text')||'').indexOf(q)===-1) return false;
    return true;
  }
  function apply(){
    rows.forEach(function(r){
      var ok=matches(r); r.classList.toggle('hidden',!ok);
      var d=detailOf(r); if(d){ d.classList.toggle('hidden',!ok); if(!ok) d.classList.remove('show'); }
    });
  }
  document.querySelectorAll('.chip').forEach(function(ch){
    ch.addEventListener('click',function(){
      var f=ch.getAttribute('data-filter'); if(!f) return; var p=f.split(':'),dim=p[0],val=p[1];
      var on=ch.getAttribute('aria-pressed')==='true'; ch.setAttribute('aria-pressed',on?'false':'true');
      if(on) active[dim].delete(val); else active[dim].add(val); apply();
    });
  });
  if(search) search.addEventListener('input',apply);
  // row expand/collapse
  rows.forEach(function(r){ r.addEventListener('click',function(e){
    if(e.target.tagName==='A') return; var d=detailOf(r); if(!d) return;
    var open=d.classList.toggle('show'); r.classList.toggle('open',open);
  });});
  // sortable columns (keeps each detail row paired with its frow)
  document.querySelectorAll('th[data-sort]').forEach(function(th){
    th.addEventListener('click',function(){
      var idx=parseInt(th.getAttribute('data-sort'),10);
      var tbody=th.closest('table').querySelector('tbody');
      var asc=th.getAttribute('data-dir')!=='asc'; th.setAttribute('data-dir',asc?'asc':'desc');
      var pairs=rows.map(function(r){return [r,detailOf(r)];});
      pairs.sort(function(a,b){
        var ka=a[0].children[idx]?a[0].children[idx].getAttribute('data-key')||a[0].children[idx].textContent:'';
        var kb=b[0].children[idx]?b[0].children[idx].getAttribute('data-key')||b[0].children[idx].textContent:'';
        var na=parseFloat(ka),nb=parseFloat(kb);
        if(!isNaN(na)&&!isNaN(nb)){return asc?na-nb:nb-na;}
        return asc?String(ka).localeCompare(String(kb)):String(kb).localeCompare(String(ka));
      });
      pairs.forEach(function(p){tbody.appendChild(p[0]); if(p[1]) tbody.appendChild(p[1]);});
    });
  });
})();
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

def _count_by(findings, key):
    c = {}
    for a in findings.get("articles", []):
        k = a.get(key) or "Unknown"
        c[k] = c.get(k, 0) + 1
    return c

def _inline(s):
    # collapse newlines/whitespace so dynamic text stays on one markdown line
    return " ".join(str(s or "").split())

_TYPE_CSS = {"product": "#0369a1", "snippet": "#7c3aed", "operational": "#0f766e",
             "training": "#a16207", "research": "#475569"}
_SEV_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NONE"]
_FRESH_CSS = {"Fresh": "#16a34a", "Aging": "#a16207", "Stale": "#b91c1c"}
_READY_CSS = {"Resolve-ready": "#16a34a", "Usable": "#0369a1", "Thin": "#a16207", "Misleading": "#b91c1c"}

def _bar_chart(title, counts, color_for, order):
    keys = [k for k in order if k in counts] + [k for k in counts if k not in order]
    mx = max(counts.values()) if counts else 1
    bars = "".join(
        f'<div class="row-bar"><span class="lbl">{_esc(k)}</span>'
        f'<span class="track"><span class="fill" style="width:{(100.0*counts[k]/mx) if mx else 0:.1f}%;background:{color_for(k)}"></span></span>'
        f'<span class="v">{counts[k]}</span></div>' for k in keys)
    return f'<div class="chart"><div class="ct">{_esc(title)}</div>{bars}</div>'

def write_html(findings, cfg, path):
    arts = findings.get("articles", [])
    team = _esc(cfg.get("team", ""))
    crit = _counts(findings)
    types = _count_by(findings, "type")
    fresh = _count_by(findings, "freshness")
    ready = _count_by(findings, "support_readiness")
    sevc = lambda k: _SEVERITY_CSS.get(k, "#64748b")
    typc = lambda k: _TYPE_CSS.get(k, "#64748b")

    cards = "".join(
        f'<div class="card"><div class="n" style="color:{sevc(s)}">{crit.get(s,0)}</div>'
        f'<div class="cl">{s}</div></div>' for s in _SEV_ORDER)
    charts = "".join([
        _bar_chart("By criticality", crit, sevc, _SEV_ORDER),
        _bar_chart("By type", types, typc, ["product","snippet","operational","training","research"]),
        _bar_chart("By freshness", fresh, lambda k: _FRESH_CSS.get(k, "#64748b"), ["Fresh","Aging","Stale","Unknown"]),
        _bar_chart("By support-readiness", ready, lambda k: _READY_CSS.get(k, "#64748b"), ["Resolve-ready","Usable","Thin","Misleading"]),
    ])

    sev_chips = "".join(f'<span class="chip" data-filter="severity:{s}" aria-pressed="false">{s}</span>' for s in _SEV_ORDER if crit.get(s))
    type_chips = "".join(f'<span class="chip" data-filter="type:{_esc(t)}" aria-pressed="false">{_esc(t)}</span>' for t in ["product","snippet","operational","training","research"] if t in types)
    fresh_chips = "".join(f'<span class="chip" data-filter="freshness:{_esc(fr)}" aria-pressed="false">{_esc(fr)}</span>' for fr in ["Fresh","Aging","Stale","Unknown"] if fr in fresh)

    body_rows = []
    for a in sorted(arts, key=sort_key):
        sev = a.get("criticality", "NONE")
        t = a.get("type", ""); fr = a.get("freshness", ""); rd = a.get("support_readiness", "")
        st = " ".join(str(a.get(k, "")) for k in ("title","accuracy_finding","evidence","action","screenshot_finding","category")).lower()
        short = _esc(_inline(a.get("accuracy_finding") or a.get("screenshot_finding") or ""))
        body_rows.append(
            f'<tr class="frow" data-severity="{_esc(sev)}" data-type="{_esc(t)}" data-freshness="{_esc(fr)}" data-text="{_esc(st)}">'
            f'<td data-key="{_CRIT.get(sev,4)}"><span class="twist">&#9656;</span> <span class="badge" style="background:{sevc(sev)}">{_esc(sev)}</span></td>'
            f'<td>{_esc(a.get("title",""))}</td>'
            f'<td><span class="tag" style="color:{typc(t)};border-color:{typc(t)}">{_esc(t)}</span></td>'
            f'<td>{_esc(fr)}</td><td>{_esc(rd)}</td><td>{short}</td></tr>')
        kv = []
        if a.get("url"): kv.append(f'<div class="kv"><span class="k">URL</span><span><a href="{_esc(a.get("url"))}">{_esc(a.get("url"))}</a></span></div>')
        kv.append(f'<div class="kv"><span class="k">Meta</span><span>{_esc(t)} · {_esc(a.get("repo","") or "no repo")} · effort {_esc(a.get("effort",""))} · rec {_esc(a.get("recommendation",""))}</span></div>')
        if a.get("accuracy_finding"): kv.append(f'<div class="kv"><span class="k">Finding</span><span>{_esc(_inline(a.get("accuracy_finding")))}</span></div>')
        if a.get("evidence"): kv.append(f'<div class="kv"><span class="k">Evidence</span><span class="mono">{_esc(_inline(a.get("evidence")))}</span></div>')
        if a.get("action"): kv.append(f'<div class="kv"><span class="k">Action</span><span>{_esc(_inline(a.get("action")))}</span></div>')
        if a.get("known_issue_status"): kv.append(f'<div class="kv"><span class="k">Known-issue</span><span>{_esc(_inline(a.get("known_issue_status")))}</span></div>')
        if a.get("screenshot_status"): kv.append(f'<div class="kv"><span class="k">Screenshot</span><span>{_esc(a.get("screenshot_status"))}: {_esc(_inline(a.get("screenshot_finding","")))} <span class="mono">{_esc(_inline(a.get("screenshot_evidence","")))}</span></span></div>')
        body_rows.append(f'<tr class="detail"><td colspan="6">{"".join(kv)}</td></tr>')

    qw = sorted([a for a in arts if a.get("criticality") in ("CRITICAL","HIGH") and a.get("effort") == "Quick Fix"], key=sort_key)
    qw_html = "".join(
        f'<li><span class="badge" style="background:{sevc(a.get("criticality"))}">{_esc(a.get("criticality") or "")}</span> '
        f'{_esc(a.get("title",""))} <span class="muted">{_esc(_inline(a.get("action") or a.get("accuracy_finding") or ""))}</span></li>' for a in qw) or '<li class="muted">None.</li>'

    pt_rows = ""
    for t in sorted(types, key=lambda x: -types[x]):
        g = [a for a in arts if a.get("type") == t]
        cc = lambda s: sum(1 for a in g if a.get("criticality") == s)
        stale = sum(1 for a in g if a.get("freshness") == "Stale")
        thin = sum(1 for a in g if a.get("support_readiness") == "Thin")
        pt_rows += (f'<tr><td><span class="tag" style="color:{typc(t)};border-color:{typc(t)}">{_esc(t)}</span></td>'
                    f'<td>{len(g)}</td><td>{cc("CRITICAL")}</td><td>{cc("HIGH")}</td><td>{cc("MEDIUM")}</td>'
                    f'<td>{cc("LOW")}</td><td>{stale}</td><td>{thin}</td></tr>')

    bl = findings.get("backlog", [])
    pric = {"High": "#b91c1c", "Medium": "#a16207", "Low": "#2563eb"}
    prio = lambda b: str(b.get("priority", "")).capitalize()
    bl_rows = "".join(
        f'<tr><td><span class="badge" style="background:{pric.get(prio(b),"#64748b")}">{_esc(prio(b) or "-")}</span></td>'
        f'<td><span class="tag">{_esc(b.get("type",""))}</span></td>'
        f'<td><b>{_esc(b.get("title",""))}</b><div class="muted small">{_esc(_inline(b.get("demand","")))}</div></td>'
        f'<td class="mono small">{_esc(_inline(b.get("source","")))}</td></tr>'
        for b in sorted(bl, key=lambda x: {"High":0,"Medium":1,"Low":2}.get(prio(x), 3)))
    backlog_section = (f'<h2>New-Article Backlog ({len(bl)})</h2>'
        f'<div class="overflow"><table><thead><tr><th>Priority</th><th>Type</th><th>Suggested article</th><th>Source</th></tr></thead>'
        f'<tbody>{bl_rows}</tbody></table></div>') if bl else ""

    html = "".join([
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
        f"<title>SKB Audit Report · {team}</title>",
        "<style>", _REPORT_CSS, "</style></head><body><div class=\"wrap\">",
        "<h1>Support Knowledge Base Audit</h1>",
        f"<p class=\"muted\">{team} · {len(arts)} articles audited</p>",
        "<h2>Summary</h2>", f"<div class=\"cards\">{cards}</div>", f"<div class=\"charts\">{charts}</div>",
        "<h2>Quick Wins</h2>",
        f"<p class=\"muted small\">High-impact and fast: CRITICAL or HIGH findings that are a Quick Fix.</p><ul>{qw_html}</ul>",
        "<h2>Findings</h2>",
        "<div class=\"controls\">",
        f"<span class=\"grp\"><span class=\"glabel\">Severity</span>{sev_chips}</span>",
        f"<span class=\"grp\"><span class=\"glabel\">Type</span>{type_chips}</span>",
        f"<span class=\"grp\"><span class=\"glabel\">Freshness</span>{fresh_chips}</span>",
        "<input id=\"finding-search\" type=\"search\" placeholder=\"Search findings...\">",
        "</div>",
        "<div class=\"overflow\"><table id=\"findings\"><thead><tr>",
        "<th data-sort=\"0\">Severity</th><th data-sort=\"1\">Article</th><th data-sort=\"2\">Type</th>",
        "<th data-sort=\"3\">Freshness</th><th data-sort=\"4\">Readiness</th><th>Finding</th>",
        "</tr></thead><tbody>", "".join(body_rows), "</tbody></table></div>",
        "<p class=\"muted small\">Click a row for evidence and the recommended action. Filter with the chips and search box; click a column header to sort.</p>",
        "<h2>Per-Type Breakdown</h2>",
        "<div class=\"overflow\"><table><thead><tr><th>Type</th><th>Articles</th><th>CRIT</th><th>HIGH</th><th>MED</th><th>LOW</th><th>Stale</th><th>Thin</th></tr></thead><tbody>",
        pt_rows, "</tbody></table></div>",
        backlog_section,
        "<h2>Methodology</h2>",
        "<p class=\"small\">Articles are classified by type; only product and snippet articles are checked against code (operational, training, and research are exempt, judged on quality and freshness). Accuracy findings cite repo evidence or are flagged for manual review; any CRITICAL or HIGH without evidence is downgraded. Screenshot checks, when run, cover image integrity, match-to-steps, and outdated UI.</p>",
        "<div class=\"foot\">Full data accompanies this report: the dated per-article CSV (one row per article) and new-articles-backlog.csv; machine-readable findings live in _internal/findings.json.</div>",
        "</div><script>", _REPORT_JS, "</script></body></html>",
    ])
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

def _ensure_playwright():
    """Best-effort: ensure Node + the `playwright` package + Chromium are available."""
    import shutil, subprocess
    if not shutil.which("node"):
        raise RuntimeError("Node.js is required to render the PDF (node not found). Install Node and re-run.")
    has_pkg = subprocess.run(["node", "-e", "require.resolve('playwright')"], capture_output=True, cwd=_SCRIPT_DIR).returncode == 0
    if not has_pkg:
        subprocess.run(["npm", "install", "--no-save", "playwright"], cwd=_SCRIPT_DIR, check=False)
    subprocess.run(["npx", "-y", "playwright", "install", "chromium"], check=False)

def _render_pdf(html_path, pdf_path):
    """Render report.html -> report.pdf via the Node Playwright print script (auto-installs if needed)."""
    import subprocess
    script = os.path.join(_SCRIPT_DIR, "print_pdf.js")
    def _run():
        return subprocess.run(["node", script, html_path, pdf_path], capture_output=True, text=True)
    try:
        r = _run()
    except FileNotFoundError:
        r = None  # `node` not on PATH
    if r is None or r.returncode != 0 or not os.path.exists(pdf_path):
        _ensure_playwright()   # raises a clear error if Node is missing, else installs playwright + chromium
        r = _run()
    if r.returncode != 0 or not os.path.exists(pdf_path):
        raise RuntimeError("PDF generation failed. Ensure Node + Playwright Chromium are installed "
                           "(npx playwright install chromium).\n" + (r.stderr or ""))

def main_with_args(config, findings_path, out_dir, date=None):
    import datetime
    from lib.config import load_config
    cfg = load_config(config)
    findings = json.load(open(findings_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    today = date or os.environ.get("SKB_AUDIT_DATE", str(datetime.date.today()))
    n = write_csv(findings, os.path.join(out_dir, f"skb-audit-{today}.csv"))
    write_backlog_csv(findings, os.path.join(out_dir, "new-articles-backlog.csv"))
    html_path = os.path.join(out_dir, "report.html")
    write_html(findings, cfg, html_path)
    _render_pdf(html_path, os.path.join(out_dir, "report.pdf"))
    print(f"Report written: {n} article rows -> report.html, report.pdf, "
          f"skb-audit-{today}.csv, new-articles-backlog.csv")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--findings", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    main_with_args(args.config, args.findings, args.out_dir)

if __name__ == "__main__":
    main()
