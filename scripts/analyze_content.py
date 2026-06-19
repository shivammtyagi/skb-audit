import argparse
import json
import os
from datetime import datetime
from lib.model import load_articles
from lib.config import load_config
from lib.metrics import freshness, is_thin, support_readiness
from lib.similarity import find_duplicates
from lib.snippets import extract_symbols

def analyze(articles, signals, cfg, now=None):
    now = now or datetime.now()
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
            "orphan": a.internal_links == 0,
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
