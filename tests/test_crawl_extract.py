import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from crawl_live import extract_article_from_html, _urls_from_sitemap

HTML = open(os.path.join(os.path.dirname(__file__), "fixtures", "sample-article.html"), encoding="utf-8").read()

def test_extract_from_html():
    a = extract_article_from_html(HTML, "https://team.example.com/resources/fix-license/")
    assert a.title == "Fixing the License Error"
    assert a.has_toc is True
    assert a.images == 1
    assert a.internal_links == 1
    assert a.external_links == 1
    assert a.modified.startswith("2026-04-10")
    assert a.word_count > 0
    assert len(a.code_blocks) == 1
    assert a.video_embeds == []

def test_urls_from_sitemap():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex>
  <sitemap><loc>https://example.com/sitemap-posts.xml</loc></sitemap>
  <url><loc>https://example.com/about/</loc></url>
  <url><loc>https://example.com/contact/</loc></url>
</sitemapindex>"""
    urls = _urls_from_sitemap(xml)
    assert urls == ["https://example.com/about/", "https://example.com/contact/"]
    assert all("sitemap" not in u for u in urls)
