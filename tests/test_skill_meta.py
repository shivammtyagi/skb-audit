import os, re
import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..")

def test_skill_frontmatter():
    text = open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    assert m, "SKILL.md must start with YAML frontmatter"
    fm = yaml.safe_load(m.group(1))
    assert fm.get("name") == "skb-audit"
    assert fm.get("description")

def test_example_config_is_valid():
    import sys
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from lib.config import load_config
    cfg = load_config(os.path.join(ROOT, "audit-config.example.yml"))
    assert cfg["products"]
