import re

def _comment_count(issue):
    """Normalize the gh `comments` field to an int count.

    gh ≥2.x (`gh issue list --json comments`) returns a list of comment objects;
    GraphQL-style payloads use {"totalCount": N}; older gh returned a bare int.
    """
    c = issue.get("comments", 0)
    if isinstance(c, list):
        return len(c)
    if isinstance(c, dict):
        return c.get("totalCount", 0) or 0
    return c or 0

def rank_issue_demand(issues):
    ranked = sorted(issues, key=_comment_count, reverse=True)
    return [{"number": i["number"], "title": i["title"], "comments": _comment_count(i)}
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
