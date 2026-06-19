import argparse
import os
import re
import urllib.request
from urllib.parse import urlparse
from lib.model import Article, save_articles

def extract_article_from_html(html, url):
    host = urlparse(url).netloc
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    title = re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else ""
    if not title:
        t = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
        title = (t.group(1).split("|")[0].strip() if t else "")
    body_match = re.search(r"<article[^>]*>(.*?)</article>", html, re.S | re.I)
    body_html = body_match.group(1) if body_match else html
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", body_html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    links = re.findall(r'href="([^"]+)"', body_html)
    internal = sum(1 for l in links if l.startswith("/") or (host and host in l))
    external = sum(1 for l in links if l.startswith("http") and (not host or host not in l))
    # Change 2: attribute-order-independent modified date extraction
    modified = None
    for meta_tag in re.findall(r"<meta[^>]+>", html, re.I):
        if re.search(r"modified_time|dateModified", meta_tag, re.I):
            m = re.search(r'content="([^"]+)"', meta_tag, re.I)
            if m:
                modified = m.group(1)
                break
    code_blocks = re.findall(r"<(?:pre|code)[^>]*>(.*?)</(?:pre|code)>", body_html, re.S)
    videos = re.findall(r"(youtube\.com/\S+|youtu\.be/\S+|vimeo\.com/\S+|<video)", html, re.I)
    return Article(
        id=urlparse(url).path.strip("/").replace("/", "-") or "home",
        title=title, url=url, slug=urlparse(url).path.strip("/").split("/")[-1],
        body_text=text, body_html=body_html, word_count=len(text.split()),
        modified=modified,
        has_toc=bool(re.search(r"in this article|table of contents", html, re.I)),
        images=len(re.findall(r"<img", body_html, re.I)),
        internal_links=internal, external_links=external,
        code_blocks=[c.strip() for c in code_blocks],
        # Change 3: deterministic dedup preserving order
        video_embeds=list(dict.fromkeys(videos)),
    )

def _from_saved_dir(d):
    arts = []
    for name in sorted(os.listdir(d)):
        if name.endswith((".html", ".htm")):
            html = open(os.path.join(d, name), encoding="utf-8").read()
            url = "https://" + name.rsplit(".", 1)[0].replace("__", "/")
            arts.append(extract_article_from_html(html, url))
    return arts

# Change 1: pure helper — no network, unit-testable
def _urls_from_sitemap(xml_text):
    """Extract page URLs from a sitemap XML string, skipping nested sitemap index entries."""
    urls = []
    for m in re.finditer(r"<loc>([^<]+)</loc>", xml_text):
        loc = m.group(1).strip()
        # Skip nested sitemap-index entries (any <loc> whose text contains "sitemap");
        # note: this also drops a page whose URL literally contains "sitemap".
        if "sitemap" not in loc.lower():
            urls.append(loc)
    return urls

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saved-dir", help="directory of HTML files saved via Playwright MCP")
    ap.add_argument("--sitemap", help="URL of an XML sitemap to crawl (non-JS sites)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if args.saved_dir:
        arts = _from_saved_dir(args.saved_dir)
    elif args.sitemap:
        arts = []
        req = urllib.request.Request(args.sitemap, headers={"User-Agent": "skb-audit"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                xml_text = resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            raise SystemExit(f"Failed to fetch sitemap {args.sitemap}: {exc}")
        page_urls = _urls_from_sitemap(xml_text)
        for page_url in page_urls:
            try:
                page_req = urllib.request.Request(page_url.strip(), headers={"User-Agent": "skb-audit"})
                with urllib.request.urlopen(page_req, timeout=20) as resp:
                    html = resp.read().decode("utf-8", errors="replace")
                arts.append(extract_article_from_html(html, page_url))
            except Exception as exc:
                print(f"Warning: skipping {page_url} — {exc}")
    else:
        raise SystemExit(
            "Provide --saved-dir (agent saves rendered pages via Playwright MCP first) "
            "or --sitemap URL (non-JS live sites)."
        )

    save_articles(args.out, arts)
    print(f"Extracted {len(arts)} articles -> {args.out}")

if __name__ == "__main__":
    main()
