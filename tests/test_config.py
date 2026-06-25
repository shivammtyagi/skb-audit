import sys, os, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.config import load_config, ConfigError

FIX = os.path.join(os.path.dirname(__file__), "fixtures", "sample-config.yml")

def test_load_valid_config():
    cfg = load_config(FIX)
    assert cfg["content_source"]["post_types"] == ["resources"]
    assert len(cfg["products"]) == 2

def test_missing_content_source(tmp_path):
    p = tmp_path / "c.yml"
    p.write_text("products: [{name: X, repo: y, match: {categories: ['*']}}]\n")
    with pytest.raises(ConfigError):
        load_config(str(p))

def test_no_source_url_or_export(tmp_path):
    p = tmp_path / "c.yml"
    p.write_text("content_source: {post_types: [resources]}\nproducts: [{name: X, repo: y}]\n")
    with pytest.raises(ConfigError):
        load_config(str(p))

def test_missing_taxonomies(tmp_path):
    p = tmp_path / "c.yml"
    p.write_text("content_source: {wxr_export: ./test.xml, post_types: [resources]}\nproducts: [{name: X, repo: y}]\n")
    with pytest.raises(ConfigError):
        load_config(str(p))

_VALID_BASE = ("content_source: {wxr_export: ./x.xml, post_types: [resources], "
               "taxonomies: {category: c, tag: t}}\n"
               "products: [{name: X, repo: y, match: {categories: ['*']}}]\n")

def test_reference_site_valid(tmp_path):
    p = tmp_path / "c.yml"
    p.write_text(_VALID_BASE + "reference_site: {url: 'https://x', admin_user: admin, admin_pass_env: PW}\n")
    cfg = load_config(str(p))
    assert cfg["reference_site"]["admin_user"] == "admin"

def test_reference_site_missing_fields(tmp_path):
    p = tmp_path / "c.yml"
    p.write_text(_VALID_BASE + "reference_site: {url: 'https://x'}\n")
    with pytest.raises(ConfigError):
        load_config(str(p))

def test_reference_site_absent_is_ok(tmp_path):
    p = tmp_path / "c.yml"
    p.write_text(_VALID_BASE)
    load_config(str(p))  # no reference_site -> valid
