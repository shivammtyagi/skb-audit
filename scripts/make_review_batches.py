"""Build Pass A review batches covering EVERY product/snippet article.

Phase 5 Pass A must review every product and snippet article — not just a mechanical
candidate subset. This splits them into numbered batches so the skill can dispatch one
subagent per batch in parallel, then verify (via the recall gate) that every article got
a verdict. Mechanical candidates remain prioritization hints, never a filter.
"""
import argparse
import json
import os
import math

REVIEW_TYPES = ("product", "snippet")


def make_batches(articles, batch_size=10):
    targets = [a for a in articles if a.get("type") in REVIEW_TYPES]
    batches = [targets[i:i + batch_size] for i in range(0, len(targets), batch_size)]
    return targets, batches


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--articles", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--batch-size", type=int, default=10)
    args = ap.parse_args()

    articles = json.load(open(args.articles, encoding="utf-8"))
    targets, batches = make_batches(articles, args.batch_size)
    os.makedirs(args.out_dir, exist_ok=True)

    # carry only the fields a reviewing agent needs (keeps batch files small)
    keep = ("id", "title", "type", "url", "repo", "product", "modified",
            "word_count", "categories", "tags", "body_text", "code_blocks")
    width = max(2, len(str(len(batches))))
    manifest = {"total_articles_to_review": len(targets), "batch_count": len(batches),
                "batch_size": args.batch_size, "batches": []}
    for i, batch in enumerate(batches, 1):
        name = f"passA_{str(i).zfill(width)}.json"
        path = os.path.join(args.out_dir, name)
        payload = [{k: a.get(k) for k in keep} for a in batch]
        json.dump(payload, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        manifest["batches"].append({"file": name, "ids": [a["id"] for a in batch]})

    json.dump(manifest, open(os.path.join(args.out_dir, "manifest.json"), "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print(f"Review coverage: {len(targets)} product/snippet articles -> "
          f"{len(batches)} batches (size {args.batch_size}) in {args.out_dir}")
    print("Dispatch ONE subagent per batch IN PARALLEL. Every article must get a verdict.")


if __name__ == "__main__":
    main()
