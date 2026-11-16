"""Validated business facts used to ground content planning."""

from pydantic import BaseModel, Field


class ProductProfile(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    category: str = "3D printed product"
    price_min_inr: float | None = Field(default=None, ge=0)
    price_max_inr: float | None = Field(default=None, ge=0)
    differentiators: list[str] = Field(default_factory=list)
    available: bool = True


class BusinessProfile(BaseModel):
    business_name: str = "GenForge"
    website: str = "https://genforge.co.in"
    instagram_handle: str = "@genforge.lab"
    business_summary: str = ""
    target_audiences: list[str] = Field(default_factory=list)
    brand_voice: list[str] = Field(default_factory=lambda: ["creative", "helpful", "maker-focused"])
    content_goals: list[str] = Field(default_factory=lambda: ["awareness", "inquiries", "sales"])
    primary_cta: str = "DM GenForge for a custom order"
    posting_constraints: list[str] = Field(default_factory=list)
    products: list[ProductProfile] = Field(default_factory=list)
    facts_to_avoid_claiming: list[str] = Field(default_factory=list)
