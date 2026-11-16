from datetime import datetime, timedelta, timezone

from genforge_marketing.research.github_skills import (
    GitHubRepositoryEvidence,
    assess_repository,
)


def test_license_is_required_for_shortlist() -> None:
    repo = GitHubRepositoryEvidence(
        full_name="example/skill",
        stars=5000,
        pushed_at=datetime.now(timezone.utc) - timedelta(days=5),
        has_readme=True,
        has_tests=True,
        has_release=True,
        security_policy=True,
    )
    result = assess_repository(repo)
    assert result.recommendation == "do_not_install_yet"
    assert any("license" in risk.lower() for risk in result.risks)


def test_well_maintained_repo_can_be_shortlisted() -> None:
    repo = GitHubRepositoryEvidence(
        full_name="example/mcp",
        stars=500,
        forks=50,
        license_spdx="MIT",
        pushed_at=datetime.now(timezone.utc) - timedelta(days=20),
        has_readme=True,
        has_tests=True,
        has_release=True,
        security_policy=True,
    )
    result = assess_repository(repo)
    assert result.recommendation == "shortlist"
    assert result.score >= 65
