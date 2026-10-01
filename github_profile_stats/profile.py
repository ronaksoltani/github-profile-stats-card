"""Fetch public GitHub account and repository metadata and aggregate it."""

from __future__ import annotations

import os
import re
from collections import Counter
from typing import Any

import requests

API_ROOT = "https://api.github.com"


class GitHubApi:
    def __init__(self, token: str | None = None, timeout: float = 15) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "GitHubProfileStatsCard/1.0",
            }
        )
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def get_json(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        response = self.session.get(f"{API_ROOT}{endpoint}", params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def fetch_profile(self, username: str, include_forks: bool = False) -> dict[str, Any]:
        if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", username):
            raise ValueError("Username must contain only letters, numbers, or hyphens.")
        user = self.get_json(f"/users/{username}")
        repos = []
        page = 1
        while True:
            batch = self.get_json(
                f"/users/{username}/repos",
                params={"per_page": 100, "page": page, "sort": "updated"},
            )
            if not isinstance(batch, list):
                raise ValueError("GitHub returned an unexpected repository response.")
            repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1

        selected = [repo for repo in repos if include_forks or not repo.get("fork", False)]
        languages = Counter(repo["language"] for repo in selected if repo.get("language"))
        language_total = sum(languages.values())
        language_rows = [
            {
                "name": name,
                "count": count,
                "percent": round(count / language_total * 100, 1) if language_total else 0,
                "bar": "█" * max(1, round(count / language_total * 20)) if language_total else "",
            }
            for name, count in languages.most_common(8)
        ]
        return {
            "username": user["login"],
            "name": user.get("name") or user["login"],
            "bio": user.get("bio") or "",
            "profile_url": user["html_url"],
            "followers": user.get("followers", 0),
            "public_repos": user.get("public_repos", len(repos)),
            "selected_repos": len(selected),
            "stars": sum(int(repo.get("stargazers_count", 0)) for repo in selected),
            "forks": sum(int(repo.get("forks_count", 0)) for repo in selected),
            "languages": language_rows,
            "include_forks": include_forks,
        }


def build_stats(username: str, include_forks: bool = False) -> dict[str, Any]:
    token = os.getenv("GITHUB_TOKEN")
    return GitHubApi(token=token).fetch_profile(username, include_forks=include_forks)
