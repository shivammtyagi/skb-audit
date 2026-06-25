import argparse
import json
from lib.model import load_articles
from lib.images import extract_images

def build_worklist(articles):
    """Worklist of articles that contain >=1 image, for the Pass E screenshot check."""
    out = []
    for a in articles:
        imgs = extract_images(a)
        if imgs:
            out.append({"article_id": a.id, "title": a.title, "type": a.type,
                        "url": a.url, "images": imgs})
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--articles", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    wl = build_worklist(load_articles(args.articles))
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(wl, f, indent=2, ensure_ascii=False)
    n_imgs = sum(len(w["images"]) for w in wl)
    print(f"Image worklist: {len(wl)} articles, {n_imgs} images -> {args.out}")

if __name__ == "__main__":
    main()
