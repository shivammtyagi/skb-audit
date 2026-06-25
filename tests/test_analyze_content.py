import sys, os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.model import Article
from analyze_content import analyze

CFG = {"options": {"freshness_aging_months": 6, "freshness_stale_months": 12}}

def mk(id, t="product", wc=300, body="1. step", links=0, code=None, mod="2026-05-01",
       body_html="<ol><li>x</li></ol>"):
    return Article(id=id, title=id, url=f"https://x/{id}", slug=id, body_text=body,
                   body_html=body_html, type=t, word_count=wc,
                   internal_links=links, code_blocks=code or [], modified=mod)

def test_orphans_are_inbound():
    # Rubric: "Orphaned" = no INBOUND internal links. "hub" links to "leaf" and
    # nothing links to "hub", so hub is the orphan and leaf is not — regardless of
    # how many outbound links each has.
    hub = mk("hub", body_html='<p><a href="https://x/leaf">see leaf</a></p>')
    leaf = mk("leaf")
    result = analyze([hub, leaf], {}, CFG, now=datetime(2026, 6, 19))
    assert "hub" in result["orphans"]
    assert "leaf" not in result["orphans"]
    by_id = {p["id"]: p for p in result["per_article"]}
    assert by_id["hub"]["freshness"] == "Fresh"
    assert by_id["hub"]["support_readiness"] in ("Resolve-ready", "Usable", "Thin")

def test_orphans_resolved_by_full_path_not_slug():
    # Two articles share the last path segment "setup" at different paths; a link to
    # one must not mark the other as linked-to (no slug conflation).
    hub = mk("hub", body_html='<p><a href="https://x/redirects/setup">go</a></p>')
    rd = mk("rd"); rd.url = "https://x/redirects/setup"
    sm = mk("sm"); sm.url = "https://x/sitemaps/setup"
    result = analyze([hub, rd, sm], {}, CFG, now=datetime(2026, 6, 19))
    assert "rd" not in result["orphans"]   # hub links to /redirects/setup
    assert "sm" in result["orphans"]        # /sitemaps/setup has no inbound link

def test_orphans_external_host_not_counted_internal():
    # external host that merely contains the KB host as a substring is not internal
    hub = mk("hub", body_html='<a href="https://x.evil.com/leaf">x</a>')
    leaf = mk("leaf")  # url https://x/leaf ; host resolves to "x"
    result = analyze([hub, leaf], {}, CFG, now=datetime(2026, 6, 19))
    assert "leaf" in result["orphans"]      # the only link to it was external

def test_snippet_symbols_collected():
    arts = [mk("s1", t="snippet", code=["add_filter('myplugin_x','cb');"])]
    result = analyze(arts, {}, CFG, now=datetime(2026, 6, 19))
    by_id = {p["id"]: p for p in result["per_article"]}
    assert "myplugin_x" in by_id["s1"]["snippet_symbols"]
