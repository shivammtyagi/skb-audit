import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.model import Article
from lib.classify import classify, route_product
from lib.config import load_config

CFG = load_config(os.path.join(os.path.dirname(__file__), "fixtures", "sample-config.yml"))

def mk(cats=None, tags=None, code=None, video=None, wc=300):
    return Article(id="x", title="t", url="u", slug="s", body_text="b", body_html="h",
                   categories=cats or [], tags=tags or [], code_blocks=code or [],
                   video_embeds=video or [], word_count=wc)

def test_classify_by_category():
    assert classify(mk(cats=["Sitemaps"]), CFG) == "product"
    assert classify(mk(cats=["Code Snippets / Filters"]), CFG) == "snippet"
    assert classify(mk(cats=["Training Videos"]), CFG) == "training"

def test_classify_default():
    assert classify(mk(cats=["Manager Processes"]), CFG) == "operational"

def test_classify_heuristic_snippet():
    assert classify(mk(cats=["Unknown"], code=["add_filter('x', 'y');"]), CFG) == "snippet"

def test_route_specific_before_catchall():
    name, repo = route_product(mk(cats=["Add-on Docs"]), CFG)
    assert repo == "example/dup"

def test_route_catchall():
    name, repo = route_product(mk(cats=["Sitemaps"]), CFG)
    assert repo == "example/core"

def test_run_classify_cli(tmp_path):
    import json, subprocess, sys, os
    from lib.model import Article, save_articles
    arts = [Article(id="x", title="t", url="u", slug="s", body_text="b", body_html="h",
                    categories=["Sitemaps"], tags=[])]
    p = tmp_path / "articles.json"
    save_articles(str(p), arts)
    here = os.path.join(os.path.dirname(__file__), "..", "scripts")
    cfgp = os.path.join(os.path.dirname(__file__), "fixtures", "sample-config.yml")
    subprocess.run([sys.executable, os.path.join(here, "run_classify.py"),
                    "--config", cfgp, "--articles", str(p)], check=True, cwd=here)
    data = json.load(open(p))
    assert data[0]["type"] == "product"
    assert data[0]["repo"] == "example/core"
