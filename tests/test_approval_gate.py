from genforge_marketing.planning.models import ApprovalStatus, PublishingStatus
from genforge_marketing.workflow.approval import can_publish


def test_draft_cannot_be_published() -> None:
    decision = can_publish(ApprovalStatus.DRAFT, PublishingStatus.READY)
    assert not decision.allowed


def test_approved_ready_content_can_be_published() -> None:
    decision = can_publish(ApprovalStatus.APPROVED, PublishingStatus.READY)
    assert decision.allowed
