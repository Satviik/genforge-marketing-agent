"""Typed models for trend opportunities received from the screening CLI."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class TrendOpportunity(BaseModel):
    """A source-backed trend that may be relevant to GenForge."""

    topic: str = Field(min_length=1, max_length=200)
    source: str = Field(min_length=1, max_length=100)
    source_url: HttpUrl | None = None
    summary: str = Field(default="", max_length=4000)
    views: int | None = Field(default=None, ge=0)
    likes: int | None = Field(default=None, ge=0)
    comments: int | None = Field(default=None, ge=0)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw: dict[str, Any] = Field(default_factory=dict)


class OpportunityBatch(BaseModel):
    """A timestamped collection of opportunities."""

    items: list[TrendOpportunity] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_agent: str = "gen-forge-screening-agent"
