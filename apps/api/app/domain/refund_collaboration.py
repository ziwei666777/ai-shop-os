from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RefundWorkflowStatus = Literal["ready_to_reply", "approval_required", "blocked"]
RefundDecision = Literal["reject_request", "refund_review", "replacement", "compensation_review", "need_more_evidence"]


@dataclass(frozen=True)
class RefundWorkflowStep:
    id: str
    agent_id: str
    title: str
    status: Literal["done", "needs_approval", "blocked"]
    evidence: str
    requires_approval: bool


@dataclass(frozen=True)
class RefundCollaborationRun:
    id: str
    source_message_id: str
    status: RefundWorkflowStatus
    decision: RefundDecision
    saved_minutes: int
    estimated_saving_yuan: int
    evidence_source: str
    proof: str
    approval_id: str | None
    customer_reply: str
    next_actions: tuple[str, ...]
    steps: tuple[RefundWorkflowStep, ...]
