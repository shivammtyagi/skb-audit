import argparse
import json
import os
import subprocess
import sys
from lib.config import load_config
from lib.ghsignals import rank_issue_demand, parse_changelog

def _gh(args, default=""):
    try:
        return subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=120).stdout
    except Exception:
        return default

def _repo_signals(repo, changelog_path):
    version = _gh(["release", "view", "--repo", repo, "--json", "tagName", "-q", ".tagName"]).strip()
    commits = _gh(["api", f"repos/{repo}/commits?per_page=50",
                   "-q", '.[] | "\\(.sha[0:7]) \\(.commit.committer.date[0:10]) \\(.commit.message | split("\\n")[0])"'])
    changelog_raw = ""
    if changelog_path:
        changelog_raw = _gh(["api", f"repos/{repo}/contents/{changelog_path}", "-q", ".content"])
        if changelog_raw:
            import base64
            try:
                changelog_raw = base64.b64decode(changelog_raw).decode("utf-8", "ignore")
            except Exception:
                changelog_raw = ""
    issues_raw = _gh(["issue", "list", "--repo", repo, "--state", "all", "--limit", "100",
                      "--search", "how do I OR how to OR docs OR missing OR cannot find",
                      "--json", "number,title,comments"], "[]")
    try:
        issues = json.loads(issues_raw or "[]")
    except json.JSONDecodeError:
        issues = []
    deprecations = _gh(["search", "code", "@deprecated", "--repo", repo, "--limit", "30"])
    errors = _gh(["search", "code", "WP_Error", "--repo", repo, "--limit", "30"])
    features = _gh(["search", "code", "register_rest_route", "--repo", repo, "--limit", "30"])
    return {
        "repo": repo,
        "version": version,
        "recent_commits": commits.splitlines(),
        "changelog": parse_changelog(changelog_raw) if changelog_raw else {"versions": [], "breaking": []},
        "deprecations": deprecations.splitlines(),
        "error_strings": errors.splitlines(),
        "feature_symbols": features.splitlines(),
        "issue_demand": rank_issue_demand(issues),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()
    cfg = load_config(args.config)
    os.makedirs(args.out_dir, exist_ok=True)
    for p in cfg["products"]:
        repo = p["repo"]
        slug = repo.replace("/", "__")
        sig = _repo_signals(repo, p.get("changelog"))
        with open(os.path.join(args.out_dir, f"{slug}.json"), "w", encoding="utf-8") as f:
            json.dump(sig, f, indent=2, ensure_ascii=False)
        print(f"Signals for {repo}: version={sig['version'] or 'n/a'}, "
              f"{len(sig['issue_demand'])} demand issues")
        if not sig["version"] and not sig["recent_commits"] and not sig["issue_demand"]:
            print(f"  WARNING: no signals returned for {repo} — check `gh auth status` and repo access.",
                  file=sys.stderr)

if __name__ == "__main__":
    main()
