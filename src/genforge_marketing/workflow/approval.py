"""Explicit approval gate used by future scheduled publishing triggers."""

from dataclasses import dataclass
from datetime import datetime, timezone

from genforge_marketing.planning.models import ApprovalStatus, PublishingStatus


@dataclass(frozen=True)
class PublishDecision:
    allowed: bool
    reason: str


def can_publish(
    approval_status: ApprovalStatus,
    publishing_status: PublishingStatus,
    now: datetime | None = None,
    scheduled_at: datetime | None = None,
) -> PublishDecision:
    """Publishing requires explicit approval and a due, ready item."""
    if approval_status is not ApprovalStatus.APPROVED:
        return PublishDecision(False, "Human approval is required.")
    if publishing_status is not PublishingStatus.READY:
        return PublishDecision(False, "Content is not marked ready for publishing.")
    if scheduled_at is not None:
        current = now or datetime.now(timezone.utc)
        if current < scheduled_at:
            return PublishDecision(False, "Scheduled publishing time has not arrived.")
    return PublishDecision(True, "Approved and ready.")
