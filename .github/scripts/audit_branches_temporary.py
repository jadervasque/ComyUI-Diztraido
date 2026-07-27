from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

repository = os.environ["GH_REPOSITORY"]
token = os.environ["GH_TOKEN"]
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {token}",
    "User-Agent": "ComyUI-Diztraido-branch-auditor",
    "X-GitHub-Api-Version": "2022-11-28",
}


def get_json(url: str):
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


branches = []
page = 1
while True:
    batch = get_json(
        f"https://api.github.com/repos/{repository}/branches?per_page=100&page={page}"
    )
    branches.extend(batch)
    if len(batch) < 100:
        break
    page += 1

open_pulls = get_json(
    f"https://api.github.com/repos/{repository}/pulls?state=open&per_page=100"
)
report = {
    "repository": repository,
    "open_pull_requests": [
        {
            "number": pr.get("number"),
            "title": pr.get("title"),
            "head": pr.get("head", {}).get("ref"),
            "base": pr.get("base", {}).get("ref"),
            "draft": pr.get("draft"),
            "html_url": pr.get("html_url"),
        }
        for pr in open_pulls
    ],
    "branches": [],
}

for branch in sorted(branches, key=lambda item: item["name"].lower()):
    name = branch["name"]
    sha = branch["commit"]["sha"]
    if name == "master":
        result = {"name": name, "sha": sha, "default": True}
    else:
        encoded_name = urllib.parse.quote(name, safe="")
        compare = get_json(
            f"https://api.github.com/repos/{repository}/compare/master...{encoded_name}"
        )
        result = {
            "name": name,
            "sha": sha,
            "status": compare.get("status"),
            "ahead": compare.get("ahead_by"),
            "behind": compare.get("behind_by"),
            "files": [
                {
                    "filename": item.get("filename"),
                    "status": item.get("status"),
                    "additions": item.get("additions"),
                    "deletions": item.get("deletions"),
                }
                for item in compare.get("files", [])
            ],
            "commits": [
                {
                    "sha": item.get("sha"),
                    "message": item.get("commit", {}).get("message", "").splitlines()[0],
                }
                for item in compare.get("commits", [])
            ],
        }
    report["branches"].append(result)

Path("branch-audit.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(
    f"Audited {len(report['branches'])} branches and "
    f"{len(report['open_pull_requests'])} open pull requests."
)
