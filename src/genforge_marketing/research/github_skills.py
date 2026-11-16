"""Evaluate supplied GitHub metadata; never execute repository code."""

from datetime import datetime, timezone
from pydantic import BaseModel, Field


class GitHubRepositoryEvidence(BaseModel):
    full_name: str
    description: str = ""
    stars: int = Field(default=0, ge=0)
    forks: int = Field(default=0, ge=0)
    open_issues: int = Field(default=0, ge=0)
    license_spdx: str | None = None
    pushed_at: datetime | None = None
    created_at: datetime | None = None
    has_readme: bool = False
    has_tests: bool = False
    has_release: bool = False
    topics: list[str] = Field(default_factory=list)
    security_policy: bool = False


class RepositoryAssessment(BaseModel):
    full_name: str
    score: float
    recommendation: str
    strengths: list[str]
    risks: list[str]
    evidence_checked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def assess_repository(repo: GitHubRepositoryEvidence) -> RepositoryAssessment:
    """Score a repository transparently; stars are only one small signal."""
    score = 0.0
    strengths: list[str] = []
    risks: list[str] = []

    if repo.stars >= 1000:
        score += 10
        strengths.append("Established star history (1,000+ stars)")
    elif repo.stars >= 100:
        score += 6
        strengths.append("Some community adoption")
    elif repo.stars >= 20:
        score += 3
    else:
        risks.append("Limited star-based adoption signal")

    if repo.license_spdx:
        score += 15
        strengths.append(f"Declared license: {repo.license_spdx}")
    else:
        risks.append("No SPDX license detected; usage rights need manual review")

    if repo.pushed_at:
        age_days = max((datetime.now(timezone.utc) - repo.pushed_at).days, 0)
        if age_days <= 90:
            score += 20
            strengths.append("Updated in the last 90 days")
        elif age_days <= 365:
            score += 12
            strengths.append("Updated in the last year")
        else:
            risks.append("No recent commit activity (over one year)")
    else:
        risks.append("Last push date unavailable")

    for enabled, points, label in (
        (repo.has_readme, 10, "README/documentation present"),
        (repo.has_tests, 10, "Tests present"),
        (repo.has_release, 10, "At least one release published"),
        (repo.security_policy, 10, "Security policy present"),
    ):
        if enabled:
            score += points
            strengths.append(label)
        else:
            risks.append(f"Missing signal: {label.lower()}")

    if repo.forks >= 20:
        score += 5
        strengths.append("Community forks indicate reuse")
    if repo.open_issues > max(repo.stars // 10, 50):
        risks.append("High open-issue count relative to popularity")

    score = min(score, 100.0)
    recommendation = "shortlist" if score >= 65 and repo.license_spdx else "manual_review"
    if not repo.license_spdx:
        recommendation = "do_not_install_yet"

    return RepositoryAssessment(
        full_name=repo.full_name,
        score=round(score, 1),
        recommendation=recommendation,
        strengths=strengths,
        risks=risks,
    )
