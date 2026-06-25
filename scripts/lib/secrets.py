"""Deterministic secret / credential detection.

Catches leaked credentials published in KB articles regardless of whether an
agent-judgment pass happens to read that article. Matches are NEVER reproduced in
output — `redact()` returns a type + length descriptor only, so the audit deliverables
do not re-leak the secret.
"""
import re

# (name, compiled pattern). Patterns are intentionally specific to keep false positives low.
_PATTERNS = [
    ("OpenAI API key",        re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b")),
    ("AWS access key id",     re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("GitHub token",          re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b")),
    ("Google API key",        re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Slack token",           re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("Stripe secret key",     re.compile(r"\b(?:sk|rk)_(?:live|test)_[A-Za-z0-9]{20,}\b")),
    ("PEM private key",       re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
    ("JWT",                   re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("Bearer token",          re.compile(r"\b[Bb]earer\s+[A-Za-z0-9._-]{20,}\b")),
    ("Credential assignment", re.compile(
        r"(?i)(?:password|passwd|api[_-]?key|secret|access[_-]?token|client[_-]?secret)"
        r"\s*[:=]\s*['\"]?([^\s'\"]{8,})")),
]

# Obvious non-secrets that the broad "Credential assignment" rule would otherwise catch.
_PLACEHOLDER = re.compile(
    r"(?i)\b(?:your[_-]?\w+|example|placeholder|xx+|<[^>]+>|\*{3,}|redacted|none|null|true|false|"
    r"changeme|password123|s3cret|yourpassword)\b")


def redact(value, kind):
    """Return a safe descriptor for a matched secret — never the value itself."""
    return f"[REDACTED-SECRET: {kind}, {len(value)} chars]"


def scan_text(text):
    """Return a list of {kind, redacted} for secrets found in `text`. De-duplicated by (kind, value)."""
    if not text:
        return []
    found, seen = [], set()
    for kind, pat in _PATTERNS:
        for m in pat.finditer(text):
            value = m.group(1) if (m.groups() and m.group(1)) else m.group(0)
            if kind == "Credential assignment" and _PLACEHOLDER.search(value):
                continue
            key = (kind, value)
            if key in seen:
                continue
            seen.add(key)
            found.append({"kind": kind, "redacted": redact(value, kind)})
    return found


def scan_article(article):
    """Scan an article's title + body_text. Returns the secrets list (possibly empty)."""
    text = " ".join(filter(None, [getattr(article, "title", ""), getattr(article, "body_text", "")]))
    return scan_text(text)
