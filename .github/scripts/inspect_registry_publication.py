from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

REPOSITORY = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ["GITHUB_TOKEN"]
NODE_ID = "diztraido-nodes"
VERSION = "0.1.0"


def request_json(url: str, *, github: bool = False) -> tuple[int, object]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "ComyUI-Diztraido-registry-inspector",
    }
    if github:
        headers.update(
            {
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {TOKEN}",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8", "replace")
            return response.status, json.loads(body)
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", "replace")
        try:
            payload: object = json.loads(body)
        except json.JSONDecodeError:
            payload = body
        return error.code, payload


def request_text(url: str) -> tuple[int, str]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "ComyUI-Diztraido-registry-inspector",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, error.read().decode("utf-8", "replace")


runs_url = (
    f"https://api.github.com/repos/{REPOSITORY}/actions/workflows/"
    "publish-registry.yml/runs?event=push&branch=master&per_page=10"
)
runs_http, runs_payload = request_json(runs_url, github=True)
print(f"PUBLISH_WORKFLOW_LIST_HTTP={runs_http}")
runs = runs_payload.get("workflow_runs", []) if isinstance(runs_payload, dict) else []
if not runs:
    raise SystemExit(f"No publication workflow run found: {runs_payload!r}")

run = runs[0]
run_id = run.get("id")
print(
    "PUBLISH_RUN="
    + json.dumps(
        {
            "id": run_id,
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "head_sha": run.get("head_sha"),
            "created_at": run.get("created_at"),
            "updated_at": run.get("updated_at"),
            "html_url": run.get("html_url"),
        },
        ensure_ascii=False,
    )
)

jobs_http, jobs_payload = request_json(
    f"https://api.github.com/repos/{REPOSITORY}/actions/runs/{run_id}/jobs",
    github=True,
)
print(f"PUBLISH_JOBS_HTTP={jobs_http}")
jobs = jobs_payload.get("jobs", []) if isinstance(jobs_payload, dict) else []
publish_job = next((job for job in jobs if job.get("name") == "Publish custom node"), None)
if publish_job:
    print(
        "PUBLISH_JOB="
        + json.dumps(
            {
                "id": publish_job.get("id"),
                "status": publish_job.get("status"),
                "conclusion": publish_job.get("conclusion"),
                "steps": [
                    {
                        "name": step.get("name"),
                        "status": step.get("status"),
                        "conclusion": step.get("conclusion"),
                    }
                    for step in publish_job.get("steps", [])
                ],
            },
            ensure_ascii=False,
        )
    )

    logs_http, logs_text = request_text(
        f"https://api.github.com/repos/{REPOSITORY}/actions/jobs/{publish_job['id']}/logs"
    )
    print(f"PUBLISH_JOB_LOGS_HTTP={logs_http}")
    pattern = re.compile(
        r"publish|registry|version|upload|extract|pending|flag|success|error|warn|node id|node_id",
        re.IGNORECASE,
    )
    relevant = [line for line in logs_text.splitlines() if pattern.search(line)]
    print("PUBLISH_LOGS_RELEVANT_BEGIN")
    for line in relevant[-120:]:
        print(line)
    print("PUBLISH_LOGS_RELEVANT_END")
else:
    print(f"PUBLISH_JOB_NOT_FOUND={jobs_payload!r}")

endpoints = {
    "node": f"https://api.comfy.org/nodes/{NODE_ID}",
    "version": f"https://api.comfy.org/nodes/{NODE_ID}/versions/{VERSION}",
    "install": f"https://api.comfy.org/nodes/{NODE_ID}/install?version={VERSION}",
    "versions": f"https://api.comfy.org/versions?nodeId={NODE_ID}&include_status_reason=true&pageSize=20",
}
results: dict[str, tuple[int, object]] = {}
for label, url in endpoints.items():
    http, payload = request_json(url)
    results[label] = (http, payload)
    print(f"REGISTRY_{label.upper()}_HTTP={http}")
    print(f"REGISTRY_{label.upper()}={json.dumps(payload, ensure_ascii=False)}")

version_http, version_payload = results["version"]
if version_http == 200 and isinstance(version_payload, dict):
    status = version_payload.get("status")
    if (
        version_payload.get("node_id") == NODE_ID
        and version_payload.get("version") == VERSION
        and status == "NodeVersionStatusActive"
    ):
        print(f"VERIFIED={NODE_ID}@{VERSION}")
        raise SystemExit(0)
    raise SystemExit(f"Version exists but is not active. status={status!r}")

raise SystemExit(f"Version endpoint did not return 200: {version_http} {version_payload!r}")
