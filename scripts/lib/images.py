import re

_IMG_RE = re.compile(r"<img\b[^>]*>", re.I)

def _attr(tag, name):
    m = (re.search(name + r'\s*=\s*"([^"]*)"', tag, re.I)
         or re.search(name + r"\s*=\s*'([^']*)'", tag, re.I))
    return m.group(1) if m else ""

def extract_images(article):
    """Return screenshot worklist entries for one article.

    Each entry: {src, alt, nearby_step_text} where nearby_step_text is the ~200
    trailing characters of de-tagged body text preceding the <img> (the step the
    screenshot illustrates). Articles without images yield an empty list.
    """
    html = getattr(article, "body_html", "") or ""
    out = []
    for m in _IMG_RE.finditer(html):
        tag = m.group(0)
        src = _attr(tag, "src")
        if not src:
            continue
        text = re.sub(r"<[^>]+>", " ", html[:m.start()])
        text = re.sub(r"\s+", " ", text).strip()
        out.append({"src": src, "alt": _attr(tag, "alt"), "nearby_step_text": text[-200:]})
    return out
