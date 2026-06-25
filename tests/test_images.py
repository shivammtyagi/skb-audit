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
