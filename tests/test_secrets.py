import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.secrets import scan_text, scan_article, redact
from lib.model import Article


def test_detects_openai_key_and_redacts():
    # synthetic, non-real key in OpenAI's sk- format (kept fake so secret-scanning
    # push protection never trips on the test suite itself)
    key = "sk-" + "FAKE0fake0FAKE0fake0FAKE0fake0FAKE0fake0"
    hits = scan_text(f"The key is {key} please use it")
    assert len(hits) == 1
    assert hits[0]["kind"] == "OpenAI API key"
    # the actual secret must NOT appear in the redacted descriptor
    assert key not in hits[0]["redacted"]
    assert "REDACTED-SECRET" in hits[0]["redacted"]


def test_detects_various_providers():
    samples = {
        "AWS access key id": "AKIAIOSFODNN7EXAMPLE",
        "GitHub token": "ghp_" + "a" * 36,
        "Google API key": "AIza" + "B" * 35,
        "Stripe secret key": "sk_live_" + "c" * 24,
    }
    for kind, val in samples.items():
        hits = scan_text(f"token: {val}")
        kinds = {h["kind"] for h in hits}
        assert kind in kinds, f"{kind} not detected in {kinds}"


def test_pem_private_key():
    hits = scan_text("-----BEGIN RSA PRIVATE KEY-----\nMIIxxx\n-----END RSA PRIVATE KEY-----")
    assert any(h["kind"] == "PEM private key" for h in hits)


def test_credential_assignment_ignores_placeholders():
    assert scan_text("password = your_password_here") == []
    assert scan_text("api_key: <YOUR_API_KEY>") == []
    assert scan_text("password=changeme") == []
    # a real-looking assigned secret is caught
    hits = scan_text("db_password = Xk9$mQ2pLz7wRt4v")
    assert any(h["kind"] == "Credential assignment" for h in hits)


def test_clean_text_has_no_findings():
    assert scan_text("This is a normal KB article about XML sitemaps and redirects.") == []
    assert scan_text("") == []


def test_dedupes_repeated_secret():
    key = "ghp_" + "z" * 36
    hits = scan_text(f"{key} and again {key}")
    assert len(hits) == 1


def test_scan_article_uses_title_and_body():
    a = Article(id="x", title="OpenAI API Key", url="u", slug="x",
                body_text="sk-" + "A" * 40, body_html="")
    hits = scan_article(a)
    assert any(h["kind"] == "OpenAI API key" for h in hits)


def test_redact_never_leaks():
    secret = "supersecretvalue12345"
    out = redact(secret, "Test")
    assert secret not in out
    assert str(len(secret)) in out
