import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.model import Article, save_articles, load_articles
import json

def test_article_roundtrip(tmp_path):
    a = Article(id="r1", title="T", url="u", slug="s", body_text="hello world",
                body_html="<p>hello world</p>", categories=["Sitemaps"], tags=["sitemap"],
                word_count=2)
    p = tmp_path / "articles.json"
    save_articles(str(p), [a])
    loaded = load_articles(str(p))
    assert len(loaded) == 1
    assert loaded[0].title == "T"
    assert loaded[0].categories == ["Sitemaps"]
    assert loaded[0].word_count == 2

def test_article_roundtrip_full_with_unknown_fields(tmp_path):
    # Build a fully-populated Article with all fields set to non-default values
    a = Article(
        id="article-123",
        title="Complete Test Article",
        url="https://example.com/article",
        slug="complete-test-article",
        body_text="This is the complete body text content.",
        body_html="<div><p>This is the complete body text content.</p></div>",
        categories=["Category1", "Category2"],
        tags=["tag1", "tag2", "tag3"],
        author="Test Author",
        published="2024-01-01",
        modified="2024-06-19",
        word_count=42,
        has_toc=True,
        images=5,
        internal_links=3,
        external_links=2,
        code_blocks=["python", "javascript"],
        video_embeds=["youtube"],
        type="tutorial",
        product="product-x",
        repo="repo-y"
    )

    # Save and load normally via save_articles/load_articles
    p = tmp_path / "articles_full.json"
    save_articles(str(p), [a])
    loaded = load_articles(str(p))
    assert len(loaded) == 1
    # Assert representative sample of fields survive the roundtrip
    assert loaded[0].id == "article-123"
    assert loaded[0].title == "Complete Test Article"
    assert loaded[0].author == "Test Author"
    assert loaded[0].published == "2024-01-01"
    assert loaded[0].word_count == 42
    assert loaded[0].has_toc is True
    assert loaded[0].categories == ["Category1", "Category2"]
    assert loaded[0].tags == ["tag1", "tag2", "tag3"]
    assert loaded[0].code_blocks == ["python", "javascript"]

    # Now test unknown field tolerance: manually write JSON with extra unknown key
    p_unknown = tmp_path / "articles_with_unknown.json"
    article_dict = {
        "id": "unknown-test",
        "title": "Unknown Field Test",
        "url": "https://test.com",
        "slug": "unknown-test",
        "body_text": "test",
        "body_html": "<p>test</p>",
        "future_field": "x"  # Unknown field that doesn't exist in Article dataclass
    }
    with open(p_unknown, "w", encoding="utf-8") as f:
        json.dump([article_dict], f)

    # load_articles should ignore the unknown "future_field" and load successfully
    loaded_with_unknown = load_articles(str(p_unknown))
    assert len(loaded_with_unknown) == 1
    assert loaded_with_unknown[0].id == "unknown-test"
    assert loaded_with_unknown[0].title == "Unknown Field Test"
