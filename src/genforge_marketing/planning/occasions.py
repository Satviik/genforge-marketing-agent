"""Festival and seasonal occasion inputs for on-demand content planning.

This module deliberately accepts researched/user-supplied occasion data rather
than guessing dates. External calendar research can be added behind this
contract later.
"""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class OccasionConfidence(StrEnum):
    VERIFIED = "verified"
    SUGGESTED = "suggested"


class MarketingOccasion(BaseModel):
    """A festival, seasonal moment, or campaign opportunity."""

    name: str = Field(min_length=2, max_length=120)
    date: date
    market: str = Field(default="India", min_length=2, max_length=80)
    confidence: OccasionConfidence = OccasionConfidence.SUGGESTED
    source_name: str = ""
    source_url: str = ""
    campaign_notes: str = ""

    @model_validator(mode="after")
    def require_evidence_for_verified_dates(self) -> "MarketingOccasion":
        if self.confidence == OccasionConfidence.VERIFIED and not (
            self.source_name.strip() or self.source_url.strip()
        ):
            raise ValueError(
                "Verified occasions require a source_name or source_url."
            )
        return self


class OccasionCalendar(BaseModel):
    """Occasions supplied for one explicit planning month."""

    year: int = Field(ge=2020, le=2100)
    month: int = Field(ge=1, le=12)
    market: str = Field(default="India", min_length=2, max_length=80)
    occasions: list[MarketingOccasion] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_month_and_market(self) -> "OccasionCalendar":
        for occasion in self.occasions:
            if occasion.date.year != self.year or occasion.date.month != self.month:
                raise ValueError(
                    f"Occasion '{occasion.name}' falls outside "
                    f"{self.year}-{self.month:02d}."
                )
            if occasion.market.casefold() != self.market.casefold():
                raise ValueError(
                    f"Occasion '{occasion.name}' market does not match "
                    f"calendar market '{self.market}'."
                )
        return self


def load_occasion_calendar(path: str) -> OccasionCalendar:
    """Load a user-researched occasion calendar from a JSON file."""
    from pathlib import Path

    return OccasionCalendar.model_validate_json(
        Path(path).read_text(encoding="utf-8")
    )
