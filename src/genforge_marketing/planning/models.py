"""Content calendar models for static posts and Reels."""

from datetime import date, time
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator

from genforge_marketing.planning.occasions import MarketingOccasion


class ApprovalStatus(StrEnum):
    DRAFT = "draft"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class PublishingStatus(StrEnum):
    NOT_SCHEDULED = "not_scheduled"
    READY = "ready"
    PUBLISHED = "published"
    FAILED = "failed"


class PostPlanItem(BaseModel):
    content_id: str
    planned_date: date
    planned_time: time
    platform: str = "instagram"
    post_type: str = "single_image"
    product: str
    campaign: str = ""
    objective: str = "awareness"
    audience: str = ""
    creative_brief: str = ""
    caption: str = ""
    hashtags: list[str] = Field(default_factory=list)
    cta: str = ""
    asset_path: str = ""
    approval_status: ApprovalStatus = ApprovalStatus.DRAFT
    publishing_status: PublishingStatus = PublishingStatus.NOT_SCHEDULED
    published_url: str = ""
    reach: int | None = None
    impressions: int | None = None
    likes: int | None = None
    comments: int | None = None
    saves: int | None = None
    shares: int | None = None
    profile_visits: int | None = None
    notes: str = ""


class ReelPlanItem(BaseModel):
    content_id: str
    planned_date: date
    planned_time: time
    platform: str = "instagram"
    product: str
    campaign: str = ""
    objective: str = "reach"
    audience: str = ""
    reel_format: str = "product_showcase"
    hook: str = ""
    scene_plan: str = ""
    script: str = ""
    on_screen_text: str = ""
    voiceover: str = ""
    audio_direction: str = ""
    caption: str = ""
    hashtags: list[str] = Field(default_factory=list)
    cta: str = ""
    asset_path: str = ""
    approval_status: ApprovalStatus = ApprovalStatus.DRAFT
    publishing_status: PublishingStatus = PublishingStatus.NOT_SCHEDULED
    published_url: str = ""
    views: int | None = None
    reach: int | None = None
    watch_time_seconds: float | None = None
    average_watch_time_seconds: float | None = None
    likes: int | None = None
    comments: int | None = None
    saves: int | None = None
    shares: int | None = None
    profile_visits: int | None = None
    notes: str = ""


class MonthlyContentPlan(BaseModel):
    year: int
    month: int = Field(ge=1, le=12)
    occasions: list[MarketingOccasion] = Field(default_factory=list)
    posts: list[PostPlanItem] = Field(default_factory=list)
    reels: list[ReelPlanItem] = Field(default_factory=list)

    @model_validator(mode="after")
    def occasions_match_plan_month(self) -> "MonthlyContentPlan":
        for occasion in self.occasions:
            if occasion.date.year != self.year or occasion.date.month != self.month:
                raise ValueError(
                    f"Occasion '{occasion.name}' falls outside "
                    f"{self.year}-{self.month:02d}."
                )
        return self
