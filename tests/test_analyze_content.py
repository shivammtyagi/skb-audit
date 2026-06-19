import sys, os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.model import Article
from analyze_content import analyze

CFG = {"options": {"freshness_aging_months": 6, "freshness_stale_months": 12}}

def mk(id, t="product", wc=300, body="1. step", links=0, code=None, mod="2026-05-01"):
    return Article(id=id, title=id, url=f"https://x/{id}", slug=id, body_text=body,
                   body_html="<ol><li>x</li></ol>", type=t, word_count=wc,
                   internal_links=links, code_blocks=code or [], modified=mod)

def test_orphans_and_readiness():
    arts = [mk("a", links=0), mk("b", links=2)]
    result = analyze(arts, {}, CFG, now=datetime(2026, 6, 19))
    assert "a" in result["orphans"]
    assert "b" not in result["orphans"]
    by_id = {p["id"]: p for p in result["per_article"]}
    assert by_id["a"]["freshness"] == "Fresh"
    assert by_id["a"]["support_readiness"] in ("Resolve-ready", "Usable", "Thin")

def test_snippet_symbols_collected():
    arts = [mk("s1", t="snippet", code=["add_filter('myplugin_x','cb');"])]
    result = analyze(arts, {}, CFG, now=datetime(2026, 6, 19))
    by_id = {p["id"]: p for p in result["per_article"]}
    assert "myplugin_x" in by_id["s1"]["snippet_symbols"]
