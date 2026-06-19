import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.ghsignals import rank_issue_demand, parse_changelog, find_undocumented

HERE = os.path.dirname(__file__)

def test_rank_issue_demand():
    issues = json.load(open(os.path.join(HERE, "fixtures", "gh-issues.json")))
    ranked = rank_issue_demand(issues)
    assert ranked[0]["number"] == 1           # 12 comments first
    assert ranked[-1]["number"] == 2          # 3 comments last

def test_parse_changelog():
    text = open(os.path.join(HERE, "fixtures", "changelog.txt")).read()
    result = parse_changelog(text)
    assert "4.7.0" in result["versions"]
    assert any("removed" in b.lower() or "deprecated" in b.lower() for b in result["breaking"])

def test_find_undocumented():
    undoc = find_undocumented(["myplugin_new_hook", "myplugin_secret"],
                              ["article mentions myplugin_new_hook somewhere"])
    assert undoc == ["myplugin_secret"]
