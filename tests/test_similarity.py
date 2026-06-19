import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.model import Article
from lib.similarity import jaccard, shingles, find_duplicates

def mk(id, text):
    return Article(id=id, title="t", url="u", slug=id, body_text=text, body_html="")

def test_jaccard_identical():
    s = shingles("the quick brown fox jumps over the lazy dog", 3)
    assert jaccard(s, s) == 1.0

def test_find_duplicates_detects_near_dup():
    a = mk("a", "install the plugin then activate the license key in settings panel now")
    b = mk("b", "install the plugin then activate the license key in settings panel today")
    c = mk("c", "completely unrelated content about sitemaps and robots files entirely")
    dups = find_duplicates([a, b, c], threshold=0.3)
    ids = {tuple(sorted([x[0], x[1]])) for x in dups}
    assert ("a", "b") in ids
    assert ("a", "c") not in ids
