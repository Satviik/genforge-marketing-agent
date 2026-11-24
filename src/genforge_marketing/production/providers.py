"""Provider-neutral creative generation interfaces and a safe no-op provider."""
from typing import Protocol

from genforge_marketing.production.models import CreativeBrief, GeneratedAsset


class CreativeProviderError(RuntimeError):
    """Raised when a configured creative provider cannot produce an asset."""


class CreativeProvider(Protocol):
    """An image/video provider adapter. Implementations must not publish assets."""

    name: str

    def generate(self, brief: CreativeBrief) -> GeneratedAsset:
        """Generate one local or hosted asset from a creative brief."""


class DisabledCreativeProvider:
    """Default provider: explain that generation is not configured, never fake output."""

    name = "disabled"

    def generate(self, brief: CreativeBrief) -> GeneratedAsset:
        raise CreativeProviderError(
            "Creative generation is not configured. Select and configure an image/video "
            "provider before requesting rendered assets."
        )
