"""GitHub discovery and repository evidence collection.

Repositories are treated as untrusted source code. This module reads metadata
only; it never clones, installs, imports, or executes discovered projects.
"""

from datetime import datetime
from typing import Any

import httpx

from genforge_marketing.research.github_skills import (
    GitHubRepositoryEvidence,
    RepositoryAssessment,
    assess_repository,
)


class GitHubResearchError(RuntimeError):
    """Raised when GitHub discovery or metadata retrieval fails."""


class GitHubSkillResearcher:
    """Search GitHub and assess candidate skills/MCP repositories."""

    def __init__(self, token: str | None = None, timeout_seconds: float = 20.0) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.Client(
            base_url="https://api.github.com",
            headers=headers,
            timeout=timeout_seconds,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "GitHubSkillResearcher":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        try:
            response = self._client.get(path, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            if status == 403 and exc.response.headers.get("X-RateLimit-Remaining") == "0":
                raise GitHubResearchError(
                    "GitHub API rate limit reached. Configure GENFORGE_MARKETING_GITHUB_TOKEN."
                ) from exc
            raise GitHubResearchError(f"GitHub API returned HTTP {status} for {path}") from exc
        except (httpx.RequestError, ValueError) as exc:
            raise GitHubResearchError(f"GitHub API request failed for {path}: {exc}") from exc

    def search(self, query: str, limit: int = 10) -> list[RepositoryAssessment]:
        """Search public GitHub repositories and assess each result."""
        if not query.strip():
            raise ValueError("Search query cannot be empty")
        if not 1 <= limit <= 30:
            raise ValueError("Limit must be between 1 and 30")

        payload = self._get(
            "/search/repositories",
            {"q": query, "sort": "stars", "order": "desc", "per_page": limit},
        )
        assessments: list[RepositoryAssessment] = []
        for result in payload.get("items", []):
            full_name = result.get("full_name")
            if not full_name:
                continue
            details = self._get(f"/repos/{full_name}")
            root = self._get(f"/repos/{full_name}/contents")
            root_names = {
                entry.get("name", "").lower()
                for entry in root
                if isinstance(entry, dict)
            } if isinstance(root, list) else set()

            pushed_at = _parse_datetime(details.get("pushed_at"))
            created_at = _parse_datetime(details.get("created_at"))
            license_data = details.get("license") or {}
            evidence = GitHubRepositoryEvidence(
                full_name=full_name,
                description=details.get("description") or "",
                stars=details.get("stargazers_count") or 0,
                forks=details.get("forks_count") or 0,
                open_issues=details.get("open_issues_count") or 0,
                license_spdx=license_data.get("spdx_id"),
                pushed_at=pushed_at,
                created_at=created_at,
                has_readme=any(name.startswith("readme") for name in root_names),
                has_tests=any(name in {"tests", "test"} for name in root_names),
                has_release=bool(details.get("has_downloads")) and self._has_release(full_name),
                topics=details.get("topics") or [],
                security_policy="security.md" in root_names or ".github" in root_names,
            )
            assessments.append(assess_repository(evidence))
        return assessments

    def _has_release(self, full_name: str) -> bool:
        releases = self._get(f"/repos/{full_name}/releases", {"per_page": 1})
        return bool(releases)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
