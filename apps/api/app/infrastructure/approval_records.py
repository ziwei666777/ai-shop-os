from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Literal, Protocol
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.api.app.infrastructure.config import get_settings


SessionProvider = Callable[[], Session]
ApprovalRisk = Literal["low", "medium", "high"]
ApprovalStatus = Literal["pending", "approved", "rejected"]


@dataclass(frozen=True)
class ApprovalRecord:
    id: str
    title: str
    risk_level: ApprovalRisk
    status: ApprovalStatus
    source_type: str
    source_id: str
    reason: str
    recommended_action: str
    created_at: str


class ApprovalRecordRepository(Protocol):
    def record_refund_workflow_approval(
        self,
        workflow_run_id: str,
        source_message_id: str,
        refund_amount_yuan: float,
        reason: str,
    ) -> ApprovalRecord:
        ...

    def list_pending_approvals(self) -> tuple[ApprovalRecord, ...]:
        ...

    def decide_approval(self, approval_id: str, decision: ApprovalStatus, note: str) -> ApprovalRecord | None:
        ...

    def clear_for_test(self) -> None:
        ...


_BASE_APPROVALS: tuple[ApprovalRecord, ...] = (
    ApprovalRecord(
        id="approval-1",
        title="Refund amount exceeds automatic handling threshold",
        risk_level="medium",
        status="pending",
        source_type="seed",
        source_id="seed-refund",
        reason="Demo approval used before real merchant approval records exist.",
        recommended_action="Review refund evidence before approving.",
        created_at="2026-07-09T10:00:00+08:00",
    ),
    ApprovalRecord(
        id="approval-2",
        title="Ad budget adjustment needs confirmation",
        risk_level="high",
        status="pending",
        source_type="seed",
        source_id="seed-ad-budget",
        reason="Demo approval used before real ad budget workflow exists.",
        recommended_action="Confirm budget before changing campaign spend.",
        created_at="2026-07-09T10:05:00+08:00",
    ),
)


class InMemoryApprovalRecordRepository:
    def __init__(self) -> None:
        self._records: list[ApprovalRecord] = []
        self._lock = RLock()

    def record_refund_workflow_approval(
        self,
        workflow_run_id: str,
        source_message_id: str,
        refund_amount_yuan: float,
        reason: str,
    ) -> ApprovalRecord:
        approval = _build_refund_approval(
            workflow_run_id=workflow_run_id,
            source_message_id=source_message_id,
            refund_amount_yuan=refund_amount_yuan,
            reason=reason,
        )
        with self._lock:
            self._records.append(approval)
        return approval

    def list_pending_approvals(self) -> tuple[ApprovalRecord, ...]:
        with self._lock:
            return tuple(item for item in (*self._records, *_BASE_APPROVALS) if item.status == "pending")

    def decide_approval(self, approval_id: str, decision: ApprovalStatus, note: str) -> ApprovalRecord | None:
        if decision == "pending":
            raise ValueError("approval decision must be approved or rejected")
        with self._lock:
            for index, record in enumerate(self._records):
                if record.id == approval_id:
                    updated = _copy_with_decision(record, decision, note)
                    self._records[index] = updated
                    return updated
        return None

    def clear_for_test(self) -> None:
        with self._lock:
            self._records.clear()


class PostgresApprovalRecordRepository:
    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider
        self.company_id = get_settings().local_company_id

    def record_refund_workflow_approval(
        self,
        workflow_run_id: str,
        source_message_id: str,
        refund_amount_yuan: float,
        reason: str,
    ) -> ApprovalRecord:
        approval = _build_refund_approval(
            workflow_run_id=workflow_run_id,
            source_message_id=source_message_id,
            refund_amount_yuan=refund_amount_yuan,
            reason=reason,
        )
        with self.session_provider() as session:
            session.execute(
                text(
                    """
                    insert into approval_records (
                      id, company_id, title, risk_level, status, source_type, source_id,
                      reason, recommended_action, metadata, created_at, updated_at
                    ) values (
                      :id, :company_id, :title, :risk_level, :status, :source_type, :source_id,
                      :reason, :recommended_action, cast(:metadata as jsonb), now(), now()
                    )
                    """
                ),
                {
                    "id": approval.id,
                    "company_id": self.company_id,
                    "title": approval.title,
                    "risk_level": approval.risk_level,
                    "status": approval.status,
                    "source_type": approval.source_type,
                    "source_id": approval.source_id,
                    "reason": approval.reason,
                    "recommended_action": approval.recommended_action,
                    "metadata": _json_dumps(
                        {
                            "source_message_id": source_message_id,
                            "refund_amount_yuan": refund_amount_yuan,
                        }
                    ),
                },
            )
            session.commit()
        return approval

    def list_pending_approvals(self) -> tuple[ApprovalRecord, ...]:
        with self.session_provider() as session:
            rows = session.execute(
                text(
                    """
                    select id, title, risk_level, status, source_type, source_id,
                           reason, recommended_action, created_at::text
                    from approval_records
                    where company_id = :company_id
                      and status = 'pending'
                    order by created_at desc
                    limit 100
                    """
                ),
                {"company_id": self.company_id},
            ).mappings().all()
            return tuple(_record_from_row(row) for row in rows)

    def decide_approval(self, approval_id: str, decision: ApprovalStatus, note: str) -> ApprovalRecord | None:
        if decision == "pending":
            raise ValueError("approval decision must be approved or rejected")
        with self.session_provider() as session:
            row = session.execute(
                text(
                    """
                    update approval_records
                    set status = :decision,
                        decision_note = :note,
                        decided_at = now(),
                        updated_at = now()
                    where company_id = :company_id
                      and id = :approval_id
                    returning id, title, risk_level, status, source_type, source_id,
                              reason, recommended_action, created_at::text
                    """
                ),
                {"company_id": self.company_id, "approval_id": approval_id, "decision": decision, "note": note},
            ).mappings().one_or_none()
            session.commit()
            return _record_from_row(row) if row else None

    def clear_for_test(self) -> None:
        with self.session_provider() as session:
            session.execute(text("delete from approval_records where company_id = :company_id"), {"company_id": self.company_id})
            session.commit()


_repository: ApprovalRecordRepository = InMemoryApprovalRecordRepository()


def configure_approval_record_repository(repository: ApprovalRecordRepository) -> None:
    global _repository
    _repository = repository


def configure_approval_record_repository_from_settings(session_provider: SessionProvider | None = None) -> ApprovalRecordRepository:
    settings = get_settings()
    if settings.approval_record_storage == "postgres" and session_provider is not None and settings.has_database:
        configure_approval_record_repository(PostgresApprovalRecordRepository(session_provider))
    else:
        configure_approval_record_repository(InMemoryApprovalRecordRepository())
    return _repository


def approval_record_repository() -> ApprovalRecordRepository:
    return _repository


def record_refund_workflow_approval(
    workflow_run_id: str,
    source_message_id: str,
    refund_amount_yuan: float,
    reason: str,
) -> ApprovalRecord:
    return _repository.record_refund_workflow_approval(
        workflow_run_id=workflow_run_id,
        source_message_id=source_message_id,
        refund_amount_yuan=refund_amount_yuan,
        reason=reason,
    )


def list_pending_approvals() -> tuple[ApprovalRecord, ...]:
    return _repository.list_pending_approvals()


def decide_approval_record(approval_id: str, decision: ApprovalStatus, note: str) -> ApprovalRecord | None:
    return _repository.decide_approval(approval_id, decision, note)


def clear_dynamic_approvals_for_test() -> None:
    _repository.clear_for_test()


def _build_refund_approval(
    workflow_run_id: str,
    source_message_id: str,
    refund_amount_yuan: float,
    reason: str,
) -> ApprovalRecord:
    return ApprovalRecord(
        id=f"approval-refund-{uuid4()}",
        title=f"Refund workflow requires boss approval: {source_message_id}",
        risk_level="high" if refund_amount_yuan >= 200 else "medium",
        status="pending",
        source_type="refund_collaboration_workflow",
        source_id=workflow_run_id,
        reason=reason,
        recommended_action="Approve refund, compensation, or rejection after checking workflow evidence.",
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _copy_with_decision(record: ApprovalRecord, decision: ApprovalStatus, note: str) -> ApprovalRecord:
    return ApprovalRecord(
        id=record.id,
        title=record.title,
        risk_level=record.risk_level,
        status=decision,
        source_type=record.source_type,
        source_id=record.source_id,
        reason=record.reason,
        recommended_action=f"{record.recommended_action} Decision note: {note}",
        created_at=record.created_at,
    )


def _record_from_row(row) -> ApprovalRecord:
    return ApprovalRecord(
        id=str(row["id"]),
        title=str(row["title"]),
        risk_level=str(row["risk_level"]),  # type: ignore[arg-type]
        status=str(row["status"]),  # type: ignore[arg-type]
        source_type=str(row["source_type"]),
        source_id=str(row["source_id"]),
        reason=str(row["reason"] or ""),
        recommended_action=str(row["recommended_action"] or ""),
        created_at=str(row["created_at"]),
    )


def _json_dumps(value: object) -> str:
    import json

    return json.dumps(value, ensure_ascii=False)