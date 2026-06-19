import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from lib.ghsignals import rank_issue_demand, parse_changelog, find_undocumented

HERE = os.path.dirname(__file__)

def test_rank_issue_demand():
    issues = json.load(open(os.path.join(HERE, "fixtures", "gh-issues.json")))
    ranked = rank_issue_demand(issues)
    assert ranked[0]["number"] == 1           # 12 comments first
    assert ranked[-1]["number"] == 2          # 3 comments last

def test_rank_issue_demand_list_shaped_comments():
    # Regression: gh >=2.x returns `comments` from `gh issue list --json` as a
    # LIST of comment objects, not an int. Sorting must not raise (comparing
    # lists element-wise compared dicts -> TypeError) and counts must rank.
    issues = [
        {"number": 10, "title": "few", "comments": [{"id": 1}]},
        {"number": 11, "title": "many", "comments": [{"id": 1}, {"id": 2}, {"id": 3}]},
        {"number": 12, "title": "none", "comments": []},
    ]
    ranked = rank_issue_demand(issues)
    assert [r["number"] for r in ranked] == [11, 10, 12]
    assert ranked[0]["comments"] == 3         # normalized to an int count
    assert ranked[-1]["comments"] == 0

def test_rank_issue_demand_object_shaped_comments():
    # GraphQL-style payloads use {"totalCount": N}.
    issues = [
        {"number": 20, "title": "a", "comments": {"totalCount": 2}},
        {"number": 21, "title": "b", "comments": {"totalCount": 9}},
    ]
    ranked = rank_issue_demand(issues)
    assert ranked[0]["number"] == 21
    assert ranked[0]["comments"] == 9

def test_parse_changelog():
    text = open(os.path.join(HERE, "fixtures", "changelog.txt")).read()
    result = parse_changelog(text)
    assert "4.7.0" in result["versions"]
    assert any("removed" in b.lower() or "deprecated" in b.lower() for b in result["breaking"])

def test_find_undocumented():
    undoc = find_undocumented(["myplugin_new_hook", "myplugin_secret"],
                              ["article mentions myplugin_new_hook somewhere"])
    assert undoc == ["myplugin_secret"]
