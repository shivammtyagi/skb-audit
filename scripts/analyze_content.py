import argparse
import json
import os
import re
from datetime import datetime
from urllib.parse import urlparse
from lib.model import load_articles
from lib.config import load_config
from lib.metrics import freshness, is_thin, support_readiness
from lib.similarity import find_duplicates
from lib.snippets import extract_symbols

def _inbound_orphans(articles):
    """IDs with no INBOUND internal link from another article.

    Matches the rubric's "Orphaned" definition (no inbound internal links).
    Builds a link graph from each article's body_html hrefs, resolving same-host
    or root-relative links to a target article by the last URL-path segment (slug).
    Note: this is distinct from outbound dead-ends (article.internal_links == 0).
    """
    slug_to_id = {}
    for a in articles:
        if a.slug:
            slug_to_id.setdefault(a.slug, a.id)
    hosts = [urlparse(a.url).netloc for a in articles if a.url]
    host = max(set(hosts), key=hosts.count) if hosts else ""
    linked_to = set()
    for a in articles:
        for href in re.findall(r'href="([^"]+)"', a.body_html or ""):
            if href.startswith("#"):
                continue
            if (host and host in href) or href.startswith("/"):
                segs = [s for s in urlparse(href).path.split("/") if s]
                tid = slug_to_id.get(segs[-1]) if segs else None
                if tid and tid != a.id:
                    linked_to.add(tid)
    return {a.id for a in articles if a.id not in linked_to}

def analyze(articles, signals, cfg, now=None):
    now = now or datetime.now()
    orphan_ids = _inbound_orphans(articles)
    per_article = []
    for a in articles:
        per_article.append({
            "id": a.id,
            "title": a.title,
            "type": a.type,
            "repo": a.repo,
            "freshness": freshness(a.modified, now, cfg),
            "support_readiness": support_readiness(a),
            "is_thin": is_thin(a),
            "orphan": a.id in orphan_ids,
            "snippet_symbols": extract_symbols(a.code_blocks) if a.type == "snippet" else [],
        })
    orphans = [p["id"] for p in per_article if p["orphan"]]
    duplicates = find_duplicates(articles, threshold=cfg.get("options", {}).get("dup_threshold", 0.4))
    return {"per_article": per_article, "orphans": orphans, "duplicates": duplicates}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--articles", required=True)
    ap.add_argument("--signals-dir", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    cfg = load_config(args.config)
    articles = load_articles(args.articles)
    signals = {}
    if args.signals_dir and os.path.isdir(args.signals_dir):
        for name in os.listdir(args.signals_dir):
            if name.endswith(".json"):
                signals[name[:-5]] = json.load(open(os.path.join(args.signals_dir, name)))
    result = analyze(articles, signals, cfg)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Mechanical findings: {len(result['orphans'])} orphans, "
          f"{len(result['duplicates'])} duplicate pairs")

if __name__ == "__main__":
    main()
