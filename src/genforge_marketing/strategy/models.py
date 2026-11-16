"""Structured strategy output for a monthly content plan."""

from pydantic import BaseModel, Field


class ContentPillar(BaseModel):
    name: str
    purpose: str
    recommended_share: float = Field(ge=0, le=1)
    formats: list[str] = Field(default_factory=list)
    example_angles: list[str] = Field(default_factory=list)


class AudienceMessage(BaseModel):
    audience: str
    needs: list[str] = Field(default_factory=list)
    message: str
    proof_points: list[str] = Field(default_factory=list)


class MonthlyStrategy(BaseModel):
    business_name: str
    month: int = Field(ge=1, le=12)
    year: int
    primary_goal: str
    supporting_goals: list[str] = Field(default_factory=list)
    positioning_summary: str
    pillars: list[ContentPillar]
    audience_messages: list[AudienceMessage] = Field(default_factory=list)
    cadence_recommendation: str
    creative_direction: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
