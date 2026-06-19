import os, sys, json, subprocess

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
SCRIPTS = os.path.join(ROOT, "scripts")
WXR = os.path.join(HERE, "fixtures", "sample.wxr.xml")


def test_pipeline_on_sample_fixture(tmp_path):
    """End-to-end: parse -> classify -> analyze on the bundled sample export."""
    cfg = tmp_path / "c.yml"
    cfg.write_text(f"""
team: Demo
content_source:
  wxr_export: {WXR}
  post_types: [resources]
  taxonomies: {{category: resource_category, tag: resource_tag}}
article_types:
  default: operational
  by_category: {{product: [Sitemaps], snippet: ["Code Snippets / Filters"], training: ["Training Videos"]}}
  heuristics: {{snippet_if_code_blocks: true, training_if_video_only: true}}
products: [{{name: Core, repo: your-org/your-product, match: {{categories: ["*"]}}}}]
options: {{default_repo: your-org/your-product}}
""")
    arts = tmp_path / "articles.json"
    subprocess.run([sys.executable, f"{SCRIPTS}/parse_wxr.py", "--config", str(cfg),
                    "--out", str(arts)], check=True, cwd=SCRIPTS)
    subprocess.run([sys.executable, f"{SCRIPTS}/run_classify.py", "--config", str(cfg),
                    "--articles", str(arts)], check=True, cwd=SCRIPTS)
    data = json.load(open(arts, encoding="utf-8"))
    assert len(data) >= 1                      # sample fixture has one published resource
    types = {d["type"] for d in data}
    assert "product" in types                  # the sample article is in a 'product' category
    findings = tmp_path / "fm.json"
    subprocess.run([sys.executable, f"{SCRIPTS}/analyze_content.py", "--config", str(cfg),
                    "--articles", str(arts), "--out", str(findings)], check=True, cwd=SCRIPTS)
    fm = json.load(open(findings, encoding="utf-8"))
    assert "orphans" in fm and "duplicates" in fm
