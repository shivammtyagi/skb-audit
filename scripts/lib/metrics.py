import re
from datetime import datetime

THIN_THRESHOLDS = {"product": 150, "snippet": 40, "operational": 120, "training": 0, "research": 0}
_STEP_RE = re.compile(r"(?:^|\n)\s*(?:\d+\.|step\s+\d+)", re.I)
_PREREQ_RE = re.compile(r"prerequisit|before you (?:begin|start)|requirement", re.I)
_OUTCOME_RE = re.compile(r"you should (?:now )?see|expected result|once (?:done|complete)", re.I)

def freshness(modified, now, cfg):
    if not modified:
        return "Unknown"
    try:
        m = datetime.fromisoformat(str(modified)[:10])
    except ValueError:
        return "Unknown"
    months = (now - m).days / 30.0
    o = cfg.get("options", {})
    if months > o.get("freshness_stale_months", 12):
        return "Stale"
    if months > o.get("freshness_aging_months", 6):
        return "Aging"
    return "Fresh"

def is_thin(article):
    return article.word_count < THIN_THRESHOLDS.get(article.type, 150)

def has_steps(article):
    return bool(_STEP_RE.search(article.body_text)) or "<ol" in (article.body_html or "")

def has_prerequisites(article):
    return bool(_PREREQ_RE.search(article.body_text))

def has_expected_outcome(article):
    return bool(_OUTCOME_RE.search(article.body_text))

def support_readiness(article):
    if article.type in ("training", "research"):
        return "Usable"
    if is_thin(article):
        return "Thin"
    score = sum([has_steps(article), has_prerequisites(article), has_expected_outcome(article)])
    return "Resolve-ready" if score >= 2 else "Usable"
