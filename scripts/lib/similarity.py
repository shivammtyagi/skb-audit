import re

def shingles(text, k=5):
    words = re.findall(r"\w+", (text or "").lower())
    if len(words) < k:
        return {tuple(words)} if words else set()
    return {tuple(words[i:i + k]) for i in range(len(words) - k + 1)}

def jaccard(a, b):
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0

def find_duplicates(articles, threshold=0.4):
    sh = {a.id: shingles(a.body_text, 3) for a in articles}
    ids = [a.id for a in articles]
    out = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            score = jaccard(sh[ids[i]], sh[ids[j]])
            if score >= threshold:
                out.append((ids[i], ids[j], round(score, 3)))
    return out
