"""
Discovers every GitHub Pages site owned by GITHUB_REPOSITORY_OWNER and writes
its metadata (title, description, language, last-updated, etc.) to
library.json. No uptime checking — this is a catalog, not a monitor.
index.html reads library.json to render the bookshelf.
"""

import json
import os
import sys
from datetime import datetime, timezone

import requests

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER")
HEADERS = {"Accept": "application/vnd.github+json"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

OUTPUT_FILE = "library.json"
REQUEST_TIMEOUT = 15


def get_all_repos(owner):
    """List every public repo owned by `owner` (paginated)."""
    repos = []
    page = 1
    while True:
        resp = requests.get(
            f"https://api.github.com/users/{owner}/repos",
            params={"per_page": 100, "page": page, "type": "owner", "sort": "updated"},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos


def get_pages_url(owner, repo_name):
    """Return the live Pages URL for a repo, or None if Pages isn't enabled."""
    resp = requests.get(
        f"https://api.github.com/repos/{owner}/{repo_name}/pages",
        headers=HEADERS,
        timeout=REQUEST_TIMEOUT,
    )
    if resp.status_code == 200:
        return resp.json().get("html_url")
    return None


def main():
    if not OWNER:
        print("GITHUB_REPOSITORY_OWNER is not set", file=sys.stderr)
        sys.exit(1)

    repos = get_all_repos(OWNER)
    books = []

    for repo in repos:
        if repo.get("archived") or not repo.get("has_pages"):
            continue

        name = repo["name"]
        url = get_pages_url(OWNER, name)
        if not url:
            continue

        books.append(
            {
                "repo": name,
                "description": repo.get("description") or "",
                "url": url,
                "language": repo.get("language"),
                "topics": repo.get("topics", []),
                "stars": repo.get("stargazers_count", 0),
                "updated_at": repo.get("pushed_at"),
            }
        )

    # Most recently updated first
    books.sort(key=lambda b: (b["updated_at"] or ""), reverse=True)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "owner": OWNER,
        "books": books,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Found {len(books)} site(s).")


if __name__ == "__main__":
    main()
