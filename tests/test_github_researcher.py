from datetime import datetime, timezone

from genforge_marketing.research.github_client import GitHubSkillResearcher


def test_search_collects_metadata_and_assesses_candidate() -> None:
    researcher = GitHubSkillResearcher()
    calls = []

    def fake_get(path, params=None):
        calls.append((path, params))
        if path == "/search/repositories":
            return {"items": [{"full_name": "maker/instagram-mcp"}]}
        if path == "/repos/maker/instagram-mcp":
            return {
                "full_name": "maker/instagram-mcp",
                "description": "Instagram workflow tools",
                "stargazers_count": 350,
                "forks_count": 30,
                "open_issues_count": 3,
                "license": {"spdx_id": "MIT"},
                "pushed_at": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "topics": ["instagram", "mcp"],
            }
        if path == "/repos/maker/instagram-mcp/contents":
            return [{"name": "README.md"}, {"name": "tests"}, {"name": ".github"}]
        if path == "/repos/maker/instagram-mcp/contents/.github":
            return [{"name": "SECURITY.md"}]
        if path == "/repos/maker/instagram-mcp/releases":
            return [{"tag_name": "v1.0.0"}]
        raise AssertionError(f"Unexpected GitHub API path: {path}")

    researcher._get = fake_get
    try:
        results = researcher.search("instagram MCP", limit=5)
    finally:
        researcher.close()

    assert len(results) == 1
    assert results[0].full_name == "maker/instagram-mcp"
    assert results[0].recommendation == "shortlist"
    assert "Declared license: MIT" in results[0].strengths
    assert "README/documentation present" in results[0].strengths
    assert any(path.endswith("/releases") for path, _ in calls)


def test_search_rejects_empty_query() -> None:
    researcher = GitHubSkillResearcher()
    try:
        try:
            researcher.search("  ")
        except ValueError as exc:
            assert "empty" in str(exc)
        else:
            raise AssertionError("Empty query should be rejected")
    finally:
        researcher.close()
