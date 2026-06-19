import argparse
from lib.model import load_articles, save_articles
from lib.config import load_config
from lib.classify import classify, route_product

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--articles", required=True)
    args = ap.parse_args()
    cfg = load_config(args.config)
    arts = load_articles(args.articles)
    for a in arts:
        a.type = classify(a, cfg)
        if a.type in ("product", "snippet"):
            a.product, a.repo = route_product(a, cfg)
    save_articles(args.articles, arts)
    counts = {}
    for a in arts:
        counts[a.type] = counts.get(a.type, 0) + 1
    print(f"Classified {len(arts)} articles: {counts}")

if __name__ == "__main__":
    main()
