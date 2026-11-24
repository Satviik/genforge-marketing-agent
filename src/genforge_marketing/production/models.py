"""Contracts for generated creative assets; providers must preserve supplied products."""
from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel, Field, HttpUrl


class AssetKind(StrEnum):
    IMAGE = "image"
    VIDEO = "video"


class CreativeBrief(BaseModel):
    content_id: str
    prompt: str = Field(min_length=1)
    kind: AssetKind
    aspect_ratio: str = "4:5"
    reference_images: list[Path] = Field(default_factory=list)
    duration_seconds: int | None = Field(default=None, ge=1, le=90)
    preserve_reference_geometry: bool = True
    overlay_text: bool = False


class GeneratedAsset(BaseModel):
    content_id: str
    kind: AssetKind
    provider: str
    local_path: Path | None = None
    remote_url: HttpUrl | None = None
    prompt_used: str
    reference_images_used: list[Path] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
