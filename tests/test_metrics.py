import sys, os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.model import Article
from lib.metrics import freshness, is_thin, has_steps, support_readiness

CFG = {"options": {"freshness_aging_months": 6, "freshness_stale_months": 12}}
NOW = datetime(2026, 6, 19)

def mk(t="product", wc=300, body="1. do this\n2. then that", html="<ol><li>x</li></ol>"):
    return Article(id="x", title="t", url="u", slug="s", body_text=body, body_html=html,
                   type=t, word_count=wc)

def test_freshness():
    assert freshness("2026-05-01", NOW, CFG) == "Fresh"
    assert freshness("2025-10-01", NOW, CFG) == "Aging"
    assert freshness("2024-01-01", NOW, CFG) == "Stale"
    assert freshness(None, NOW, CFG) == "Unknown"

def test_thinness_is_type_aware():
    assert is_thin(mk(t="product", wc=100)) is True
    assert is_thin(mk(t="training", wc=20)) is False   # training exempt
    assert is_thin(mk(t="research", wc=20)) is False

def test_has_steps():
    assert has_steps(mk()) is True
    assert has_steps(mk(body="no steps here", html="<p>x</p>")) is False

def test_support_readiness():
    assert support_readiness(mk(t="product", wc=100)) == "Thin"
    assert support_readiness(mk(t="training", wc=10)) == "Usable"
