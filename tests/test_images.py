import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.images import extract_images

class A:
    def __init__(self, html, text=""):
        self.body_html = html
        self.body_text = text

def test_extracts_src_and_alt():
    a = A('<p>Go to Sitemaps settings</p><img src="https://k/s.png" alt="Sitemap screen">')
    imgs = extract_images(a)
    assert len(imgs) == 1
    assert imgs[0]["src"] == "https://k/s.png"
    assert imgs[0]["alt"] == "Sitemap screen"
    assert "Sitemaps" in imgs[0]["nearby_step_text"]

def test_single_quoted_attrs():
    a = A("<img src='/wp-content/x.jpg' alt='Alt here'>")
    imgs = extract_images(a)
    assert imgs[0]["src"] == "/wp-content/x.jpg"
    assert imgs[0]["alt"] == "Alt here"

def test_no_images():
    assert extract_images(A("<p>no pics here</p>")) == []

class Art:
    def __init__(self, id, html):
        self.id = id; self.title = "t" + id; self.type = "product"
        self.url = "u" + id; self.body_html = html; self.body_text = ""

def test_build_worklist_keeps_only_image_articles():
    from extract_images import build_worklist
    arts = [Art("1", '<p>step</p><img src="a.png">'), Art("2", "<p>none</p>")]
    wl = build_worklist(arts)
    assert len(wl) == 1
    assert wl[0]["article_id"] == "1"
    assert wl[0]["images"][0]["src"] == "a.png"
