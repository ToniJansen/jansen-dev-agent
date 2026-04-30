from __future__ import annotations
import base64
import os
from datetime import datetime

import requests

_BASE = "https://api.github.com"


def _headers() -> dict:
    return {
        "Authorization": f"token {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json",
    }


def _get_default_branch(repo: str) -> str:
    r = requests.get(f"{_BASE}/repos/{repo}", headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json()["default_branch"]


def _get_branch_sha(repo: str, branch: str) -> str:
    r = requests.get(f"{_BASE}/repos/{repo}/git/ref/heads/{branch}", headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json()["object"]["sha"]


def _create_branch(repo: str, branch: str, sha: str) -> None:
    requests.post(
        f"{_BASE}/repos/{repo}/git/refs",
        headers=_headers(),
        json={"ref": f"refs/heads/{branch}", "sha": sha},
        timeout=10,
    )  # ignore 422 if branch already exists


def _put_file(repo: str, path: str, content: str, message: str, branch: str) -> None:
    encoded = base64.b64encode(content.encode()).decode()
    payload: dict = {"message": message, "content": encoded, "branch": branch}
    r = requests.get(f"{_BASE}/repos/{repo}/contents/{path}?ref={branch}", headers=_headers(), timeout=10)
    if r.status_code == 200:
        payload["sha"] = r.json()["sha"]
    requests.put(
        f"{_BASE}/repos/{repo}/contents/{path}",
        headers=_headers(),
        json=payload,
        timeout=10,
    ).raise_for_status()


def _open_pr(repo: str, title: str, body: str, head: str, base: str) -> str:
    r = requests.post(
        f"{_BASE}/repos/{repo}/pulls",
        headers=_headers(),
        json={"title": title, "body": body, "head": head, "base": base},
        timeout=10,
    )
    if r.status_code == 422:
        # PR already open for this branch — return existing URL
        existing = requests.get(
            f"{_BASE}/repos/{repo}/pulls",
            headers=_headers(),
            params={"head": f"{repo.split('/')[0]}:{head}", "state": "open"},
            timeout=10,
        )
        prs = existing.json()
        return prs[0]["html_url"] if prs else f"https://github.com/{repo}/pulls"
    r.raise_for_status()
    return r.json()["html_url"]


def merge_pr(repo: str, pr_number: int) -> None:
    """Auto-merge a PR that passed all quality gates."""
    requests.put(
        f"{_BASE}/repos/{repo}/pulls/{pr_number}/merge",
        headers=_headers(),
        json={"merge_method": "squash", "commit_title": f"[Agent] Auto-merged PR #{pr_number} — no critical issues"},
        timeout=10,
    ).raise_for_status()


def _ensure_label(repo: str, name: str, color: str = "0075ca") -> None:
    requests.post(
        f"{_BASE}/repos/{repo}/labels",
        headers=_headers(),
        json={"name": name, "color": color},
        timeout=10,
    )  # 422 = already exists, safe to ignore


def _parse_assignees() -> dict[str, str]:
    """Parse MEETING_ASSIGNEES=Name:username,Name2:username2 from env."""
    result: dict[str, str] = {}
    for pair in os.environ.get("MEETING_ASSIGNEES", "").split(","):
        if ":" in pair:
            name, username = pair.split(":", 1)
            result[name.strip().lower()] = username.strip()
    return result


def _find_issue(repo: str, title: str) -> dict | None:
    """Search for an existing issue with exactly this title (open or closed)."""
    r = requests.get(
        f"{_BASE}/search/issues",
        headers=_headers(),
        params={"q": f'repo:{repo} is:issue in:title "{title}"', "per_page": 5},
        timeout=10,
    )
    if r.status_code != 200:
        return None
    for issue in r.json().get("items", []):
        if issue["title"].strip().lower() == title.strip().lower():
            return issue
    return None


def _reopen_issue(repo: str, number: int, meeting_name: str) -> None:
    """Reopen a closed issue and leave a comment."""
    requests.patch(
        f"{_BASE}/repos/{repo}/issues/{number}",
        headers=_headers(),
        json={"state": "open"},
        timeout=10,
    )
    requests.post(
        f"{_BASE}/repos/{repo}/issues/{number}/comments",
        headers=_headers(),
        json={"body": f"↩️ Reopened — mentioned again in `{meeting_name}`."},
        timeout=10,
    )


def open_meeting_issues(items: list[dict], meeting_name: str) -> list[str]:
    """Open one GitHub issue per action item with search-first + reopen logic."""
    repo = os.environ["GITHUB_REPO"]
    assignee_map = _parse_assignees()
    _ensure_label(repo, "action-item", color="0075ca")

    urls = []
    for item in items:
        title = (item.get("title") or "").strip()
        if not title:
            continue

        owner = item.get("owner") or "Unknown"
        deadline = item.get("deadline") or "No deadline"
        github_user = assignee_map.get(owner.lower())

        existing = _find_issue(repo, title)
        if existing:
            if existing["state"] == "open":
                urls.append(existing["html_url"])
                continue
            _reopen_issue(repo, existing["number"], meeting_name)
            urls.append(existing["html_url"])
            continue

        labels = ["action-item"]
        if not github_user:
            owner_label = f"owner:{owner}"
            _ensure_label(repo, owner_label, color="7057ff")
            labels.append(owner_label)

        body = (
            f"**Owner:** {owner}\n"
            f"**Deadline:** {deadline}\n"
            f"**Source:** `{meeting_name}`\n\n"
            f"> Auto-generated by `morning_agent` from meeting notes."
        )
        payload: dict = {"title": title, "body": body, "labels": labels}
        if github_user:
            payload["assignees"] = [github_user]

        r = requests.post(
            f"{_BASE}/repos/{repo}/issues",
            headers=_headers(),
            json=payload,
            timeout=10,
        )
        if r.status_code in (200, 201):
            urls.append(r.json()["html_url"])

    return urls


def open_review_pr(
    filename: str,
    review: str,
    fixed_code: str,
    test_before: str = "",
    test_after: str = "",
) -> str:
    """Create branch, commit fixed code + review report, open PR. Returns PR URL."""
    repo = os.environ["GITHUB_REPO"]
    date = datetime.now().strftime("%Y-%m-%d")
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    branch = f"agent/review-{ts}"

    default = _get_default_branch(repo)
    sha = _get_branch_sha(repo, default)
    _create_branch(repo, branch, sha)

    _put_file(
        repo,
        path=f"demo/code_auto_reviewed/{filename}",
        content=fixed_code,
        message=f"fix(agent): apply automated fixes to {filename} [{date}]",
        branch=branch,
    )

    _put_file(
        repo,
        path=f"reviews/{date}-{filename}.md",
        content=f"# Agent Code Review — {filename}\n\n_Generated by `overnight_agent` at 02:00_\n\n```\n{review}\n```\n",
        message=f"docs(agent): add code review report for {filename} [{date}]",
        branch=branch,
    )

    tests_section = ""
    if test_before or test_after:
        tests_section = (
            f"### Test Results\n\n"
            f"**Before fix** — original code:\n```\n{test_before or 'n/a'}\n```\n\n"
            f"**After fix** — patched code:\n```\n{test_after or 'n/a'}\n```\n\n"
        )

    pr_body = (
        f"## Automated Code Review — `{filename}`\n\n"
        f"> Generated by `overnight_agent` running at 02:00 via launchd/systemd.\n\n"
        f"### Findings\n\n```\n{review}\n```\n\n"
        f"{tests_section}"
        f"### Changes\n"
        f"- Fixed file committed to `demo/code_auto_reviewed/{filename}`\n"
        f"- Full report saved to `reviews/{date}-{filename}.md`\n"
    )

    return _open_pr(
        repo=repo,
        title=f"[Agent] Code review fixes — {filename} ({ts})",
        body=pr_body,
        head=branch,
        base=default,
    )
