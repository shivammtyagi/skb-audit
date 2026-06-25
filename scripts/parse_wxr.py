import argparse
import re
import xml.etree.ElementTree as ET
from html import unescape as _unescape
from urllib.parse import urlparse
from lib.model import Article, save_articles
from lib.config import load_config

NS = {
    "wp": "http://wordpress.org/export/1.2/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
}

def _text(el, path):
    found = el.find(path, NS)
    return found.text if found is not None and found.text else ""

def articles_from_wxr(xml_path, cfg):
    cs = cfg["content_source"]
    post_types = set(cs["post_types"])
    cat_tax = cs["taxonomies"]["category"]
    tag_tax = cs["taxonomies"]["tag"]
    root = ET.parse(xml_path).getroot()
    base_host = urlparse(_text(root.find("channel"), "wp:base_site_url") or
                         _text(root.find("channel"), "link")).netloc
    out = []
    for item in root.find("channel").findall("item"):
        if _text(item, "wp:post_type") not in post_types:
            continue
        if _text(item, "wp:status") != "publish":
            continue
        link = _text(item, "link")
        host = urlparse(link).netloc or base_host
        html = _text(item, "content:encoded")
        text = re.sub(r"<[^>]+>", " ", html)
        text = _unescape(re.sub(r"\s+", " ", text).strip())
        cats, tags = [], []
        for c in item.findall("category"):
            if not c.text:
                continue
            if c.get("domain") == cat_tax:
                cats.append(c.text)
            elif c.get("domain") == tag_tax:
                tags.append(c.text)
        links = re.findall(r'href="([^"]+)"', html)
        internal = external = 0
        for l in links:
            net = urlparse(l).netloc
            if (not net and l.startswith("/")) or (net and net == host):
                internal += 1
            elif net and net != host:
                external += 1
        code_blocks = re.findall(r"<(?:pre|code)[^>]*>(.*?)</(?:pre|code)>", html, re.S)
        videos = re.findall(r"(youtube\.com/\S+|youtu\.be/\S+|vimeo\.com/\S+|<video)", html, re.I)
        out.append(Article(
            id=f"resource-{_text(item, 'wp:post_id')}",
            title=_text(item, "title").strip(),
            url=link, slug=urlparse(link).path.strip("/").split("/")[-1],
            body_text=text, body_html=html, categories=cats, tags=tags,
            author=_text(item, "dc:creator"),
            published=(_text(item, "wp:post_date") or None),
            modified=(_text(item, "wp:post_modified") or None),
            word_count=len(text.split()),
            has_toc=bool(re.search(r"in this article|table of contents", html, re.I)),
            images=len(re.findall(r"<img", html, re.I)),
            internal_links=internal, external_links=external,
            code_blocks=[c.strip() for c in code_blocks],
            video_embeds=list(dict.fromkeys(videos)),
        ))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    cfg = load_config(args.config)
    arts = articles_from_wxr(cfg["content_source"]["wxr_export"], cfg)
    save_articles(args.out, arts)
    print(f"Parsed {len(arts)} articles -> {args.out}")

if __name__ == "__main__":
    main()
