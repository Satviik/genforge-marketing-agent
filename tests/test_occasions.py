"""Tests for evidence-aware festival and seasonal planning inputs."""

import pytest
from pydantic import ValidationError

from genforge_marketing.planning.occasions import (
    MarketingOccasion,
    OccasionCalendar,
    OccasionConfidence,
)


def test_verified_occasion_requires_evidence() -> None:
    with pytest.raises(ValidationError, match="require a source"):
        MarketingOccasion(
            name="Diwali",
            date="2026-11-08",
            confidence=OccasionConfidence.VERIFIED,
        )


def test_verified_occasion_accepts_source() -> None:
    occasion = MarketingOccasion(
        name="Diwali",
        date="2026-11-08",
        confidence=OccasionConfidence.VERIFIED,
        source_name="Official calendar",
    )
    assert occasion.confidence == OccasionConfidence.VERIFIED


def test_calendar_rejects_occasion_outside_requested_month() -> None:
    with pytest.raises(ValidationError, match="outside"):
        OccasionCalendar(
            year=2026,
            month=11,
            occasions=[
                MarketingOccasion(
                    name="Christmas",
                    date="2026-12-25",
                    market="India",
                )
            ],
        )


def test_calendar_rejects_mismatched_market() -> None:
    with pytest.raises(ValidationError, match="market does not match"):
        OccasionCalendar(
            year=2026,
            month=11,
            market="India",
            occasions=[
                MarketingOccasion(
                    name="Thanksgiving",
                    date="2026-11-26",
                    market="United States",
                )
            ],
        )


def test_suggested_occasion_is_allowed_without_source() -> None:
    occasion = MarketingOccasion(
        name="Winter gifting season",
        date="2026-11-20",
    )
    assert occasion.confidence == OccasionConfidence.SUGGESTED
