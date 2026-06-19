import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.snippets import extract_symbols

def test_extract_symbols():
    code = ["add_filter('myplugin_sitemap_urls', 'my_cb');",
            "function my_cb($urls) { return $urls; }",
            "do_action('myplugin_loaded');"]
    syms = extract_symbols(code)
    assert "myplugin_sitemap_urls" in syms
    assert "my_cb" in syms
    assert "myplugin_loaded" in syms

def test_extract_symbols_empty():
    assert extract_symbols([]) == []
