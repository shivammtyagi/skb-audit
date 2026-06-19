import re

def rank_issue_demand(issues):
    ranked = sorted(issues, key=lambda i: i.get("comments", 0), reverse=True)
    return [{"number": i["number"], "title": i["title"], "comments": i.get("comments", 0)}
            for i in ranked]

def parse_changelog(text):
    versions = re.findall(r"(\d+\.\d+(?:\.\d+)?)", text)
    breaking = [line.strip() for line in text.splitlines()
                if re.search(r"break|deprecat|remov", line, re.I)]
    # de-dupe versions preserving order
    seen, ordered = set(), []
    for v in versions:
        if v not in seen:
            seen.add(v); ordered.append(v)
    return {"versions": ordered[:50], "breaking": breaking[:100]}

def find_undocumented(symbols_in_code, article_texts):
    joined = " ".join(article_texts).lower()
    return [s for s in symbols_in_code if s.lower() not in joined]
