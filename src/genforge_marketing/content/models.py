"""Structured creative assets for Instagram posts and Reels."""

from pydantic import BaseModel, Field


class CarouselSlide(BaseModel):
    slide_number: int = Field(ge=1)
    purpose: str
    headline: str
    body_copy: str = ""
    visual_direction: str = ""


class InstagramPostContent(BaseModel):
    content_id: str
    product: str
    concept: str
    caption: str
    hashtags: list[str] = Field(default_factory=list)
    call_to_action: str
    carousel_slides: list[CarouselSlide] = Field(default_factory=list)
    visual_prompt: str = ""
    alt_text: str = ""
    fact_check_notes: list[str] = Field(default_factory=list)


class ReelScene(BaseModel):
    scene_number: int = Field(ge=1)
    duration_seconds: int = Field(ge=1, le=60)
    shot_description: str
    camera_direction: str = ""
    on_screen_text: str = ""
    voiceover: str = ""


class InstagramReelContent(BaseModel):
    content_id: str
    product: str
    concept: str
    hook: str
    duration_seconds: int = Field(ge=5, le=90)
    scenes: list[ReelScene]
    caption: str
    hashtags: list[str] = Field(default_factory=list)
    call_to_action: str
    audio_direction: str = ""
    cover_visual_prompt: str = ""
    fact_check_notes: list[str] = Field(default_factory=list)
