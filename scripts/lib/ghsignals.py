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
    return [{"number": i.get("number"), "title": i.get("title", ""), "comments": _comment_count(i)}
            for i in ranked]

def parse_changelog(text):
    # Versions come only from changelog entry HEADERS ("= x.y.z =", "## x.y.z",
    # "**New in Version x.y.z**") — not inline mentions like "WordPress 7.0" / "PHP 8.1".
    versions = re.findall(
        r"(?m)^\s*(?:=+\s*|#+\s*|\*\*\s*(?:New in Version\s+)?)v?(\d+\.\d+(?:\.\d+)?)", text)
    breaking = [line.strip() for line in text.splitlines()
                if re.search(r"\b(?:break(?:ing|s)?|deprecat(?:e|ed|es|ing|ion)?|remov(?:e|ed|es|al|ing))\b",
                             line, re.I)]
    # de-dupe versions preserving order
    seen, ordered = set(), []
    for v in versions:
        if v not in seen:
            seen.add(v); ordered.append(v)
    return {"versions": ordered[:50], "breaking": breaking[:100]}

def find_undocumented(symbols_in_code, article_texts):
    # Token-boundary match (treating word chars and "/" as symbol chars) so that, e.g.,
    # "user" is NOT counted as documented merely because "get_user_meta" appears.
    joined = " ".join(article_texts).lower()
    out = []
    for s in symbols_in_code:
        if not re.search(r"(?<![\w/])" + re.escape(s.lower()) + r"(?![\w/])", joined):
            out.append(s)
    return out
