import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.config import load_config
from parse_wxr import articles_from_wxr

HERE = os.path.dirname(__file__)
CFG = load_config(os.path.join(HERE, "fixtures", "sample-config.yml"))
XML = os.path.join(HERE, "fixtures", "sample.wxr.xml")

def test_only_published_resources():
    arts = articles_from_wxr(XML, CFG)
    assert len(arts) == 1                      # draft + page excluded
    a = arts[0]
    assert a.title == "How to configure Sitemaps"
    assert a.categories == ["Sitemaps"]
    assert a.tags == ["sitemap"]
    assert a.author == "Alice"
    assert a.modified.startswith("2026-05-01")
    assert a.has_toc is True                   # "In This Article"
    assert a.images == 1
    assert a.internal_links == 1               # team.example.com link
    assert a.external_links == 1               # google.com link
    assert a.word_count > 0
