def classify(article, cfg):
    at = cfg.get("article_types", {})
    for typ, cats in at.get("by_category", {}).items():
        if any(c in cats for c in article.categories):
            return typ
    h = at.get("heuristics", {})
    if h.get("snippet_if_code_blocks") and article.code_blocks:
        return "snippet"
    if h.get("training_if_video_only") and article.video_embeds and article.word_count < 80:
        return "training"
    return at.get("default", "operational")

def route_product(article, cfg):
    products = cfg.get("products", [])
    def is_catchall(p): return p.get("match", {}).get("categories") == ["*"]
    ordered = [p for p in products if not is_catchall(p)] + [p for p in products if is_catchall(p)]
    for p in ordered:
        m = p.get("match", {})
        if is_catchall(p):
            return p["name"], p["repo"]
        cats = m.get("categories", []) or []
        tags = m.get("tags", []) or []
        if any(c in cats for c in article.categories) or any(t in tags for t in article.tags):
            return p["name"], p["repo"]
    return "", cfg.get("options", {}).get("default_repo", "")
