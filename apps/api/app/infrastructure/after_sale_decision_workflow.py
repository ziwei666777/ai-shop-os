from __future__ import annotations

import re
from collections.abc import Mapping
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Literal, Protocol

import httpx
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.api.app.infrastructure.approval_records import ApprovalRecord
from apps.api.app.infrastructure.config import get_settings


SessionProvider = Callable[[], Session]
AfterSaleAction = Literal["refund", "replacement", "compensation", "reject"]
ApprovalDecision = Literal["approved", "rejected"]
WarehouseNotificationStatus = Literal["queued", "sent", "failed", "cancelled"]


@dataclass(frozen=True)
class AfterSaleDecisionOutcome:
    id: str
    approval_id: str
    approval_status: ApprovalDecision
    action: AfterSaleAction
    source_workflow_id: str
    after_sale_cost_yuan: int
    saved_minutes: int
    saved_yuan: int
    warehouse_notification_id: str | None
    customer_reply: str
    proof: str
    created_at: str


@dataclass(frozen=True)
class WarehouseNotification:
    id: str
    source_outcome_id: str
    source_workflow_id: str
    action: Literal["replacement"]
    status: WarehouseNotificationStatus
    external_reference: str | None
    proof: str
    created_at: str


@dataclass(frozen=True)
class WarehouseNotificationDeliveryResult:
    id: str
    status: WarehouseNotificationStatus
    external_reference: str | None
    proof: str


class WarehouseNotificationSender(Protocol):
    def send(self, notification: WarehouseNotification) -> WarehouseNotificationDeliveryResult:
        ...


class ExportQueueWarehouseNotificationSender:
    def send(self, notification: WarehouseNotification) -> WarehouseNotificationDeliveryResult:
        settings = get_settings()
        external_reference = f"{settings.warehouse_notification_export_prefix}-{notification.id}"
        return WarehouseNotificationDeliveryResult(
            id=notification.id,
            status="sent",
            external_reference=external_reference,
            proof=(
                "Warehouse notification exported for WMS/ERP delivery; "
                f"mode={settings.warehouse_notification_delivery_mode}; reference={external_reference}."
            ),
        )

class HttpApiWarehouseNotificationSender:
    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        timeout_seconds: float | None = None,
        post_json: Callable[[str, dict[str, Any], dict[str, str], float], Mapping[str, Any]] | None = None,
    ) -> None:
        settings = get_settings()
        self.api_url = api_url if api_url is not None else settings.warehouse_notification_wms_api_url
        self.api_key = api_key if api_key is not None else settings.warehouse_notification_wms_api_key
        self.timeout_seconds = timeout_seconds if timeout_seconds is not None else settings.warehouse_notification_wms_timeout_seconds
        self.post_json = post_json

    def send(self, notification: WarehouseNotification) -> WarehouseNotificationDeliveryResult:
        if not self.api_url:
            return WarehouseNotificationDeliveryResult(
                id=notification.id,
                status="failed",
                external_reference=None,
                proof="Warehouse notification delivery failed: WMS/ERP API URL is not configured.",
            )
        payload = _warehouse_notification_payload(notification)
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            body = self._post(payload, headers)
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            return WarehouseNotificationDeliveryResult(
                id=notification.id,
                status="failed",
                external_reference=None,
                proof=f"Warehouse notification delivery failed: {exc}",
            )
        external_reference = _extract_external_reference(body) or f"wms-api-{notification.id}"
        return WarehouseNotificationDeliveryResult(
            id=notification.id,
            status="sent",
            external_reference=external_reference,
            proof=f"Warehouse notification sent to WMS/ERP API; reference={external_reference}.",
        )

    def _post(self, payload: dict[str, Any], headers: dict[str, str]) -> Mapping[str, Any]:
        if self.post_json is not None:
            return self.post_json(self.api_url, payload, headers, self.timeout_seconds)
        timeout = httpx.Timeout(self.timeout_seconds, connect=min(5.0, self.timeout_seconds))
        with httpx.Client(timeout=timeout) as client:
            response = client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            if not response.content:
                return {}
            return response.json()

class AfterSaleDecisionOutcomeRepository(Protocol):
    def record_outcome(self, outcome: AfterSaleDecisionOutcome) -> AfterSaleDecisionOutcome:
        ...

    def list_queued_warehouse_notifications(self, limit: int = 20) -> tuple[WarehouseNotification, ...]:
        ...

    def update_warehouse_notification_status(
        self,
        notification_id: str,
        status: WarehouseNotificationStatus,
        external_reference: str | None,
        proof: str,
    ) -> WarehouseNotification | None:
        ...

    def summarize(self) -> dict[str, int | str]:
        ...

    def clear_for_test(self) -> None:
        ...


class InMemoryAfterSaleDecisionOutcomeRepository:
    def __init__(self) -> None:
        self._outcomes: list[AfterSaleDecisionOutcome] = []
        self._warehouse_notifications: list[WarehouseNotification] = []
        self._lock = RLock()

    def record_outcome(self, outcome: AfterSaleDecisionOutcome) -> AfterSaleDecisionOutcome:
        with self._lock:
            self._outcomes.append(outcome)
            if outcome.warehouse_notification_id:
                self._warehouse_notifications.append(
                    WarehouseNotification(
                        id=outcome.warehouse_notification_id,
                        source_outcome_id=outcome.id,
                        source_workflow_id=outcome.source_workflow_id,
                        action="replacement",
                        status="queued",
                        external_reference=None,
                        proof=outcome.proof,
                        created_at=outcome.created_at,
                    )
                )
        return outcome

    def list_queued_warehouse_notifications(self, limit: int = 20) -> tuple[WarehouseNotification, ...]:
        with self._lock:
            queued = tuple(item for item in self._warehouse_notifications if item.status == "queued")
        return queued[:limit]

    def update_warehouse_notification_status(
        self,
        notification_id: str,
        status: WarehouseNotificationStatus,
        external_reference: str | None,
        proof: str,
    ) -> WarehouseNotification | None:
        with self._lock:
            for index, notification in enumerate(self._warehouse_notifications):
                if notification.id != notification_id:
                    continue
                updated = WarehouseNotification(
                    id=notification.id,
                    source_outcome_id=notification.source_outcome_id,
                    source_workflow_id=notification.source_workflow_id,
                    action=notification.action,
                    status=status,
                    external_reference=external_reference,
                    proof=proof,
                    created_at=notification.created_at,
                )
                self._warehouse_notifications[index] = updated
                return updated
        return None

    def summarize(self) -> dict[str, int | str]:
        with self._lock:
            return _summarize_outcomes(tuple(self._outcomes), tuple(self._warehouse_notifications))

    def clear_for_test(self) -> None:
        with self._lock:
            self._outcomes.clear()
            self._warehouse_notifications.clear()


class PostgresAfterSaleDecisionOutcomeRepository:
    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider
        self.company_id = get_settings().local_company_id

    def record_outcome(self, outcome: AfterSaleDecisionOutcome) -> AfterSaleDecisionOutcome:
        with self.session_provider() as session:
            session.execute(
                text(
                    """
                    insert into after_sale_decision_outcomes (
                      id, company_id, approval_id, approval_status, action, source_workflow_id,
                      after_sale_cost_yuan, saved_minutes, saved_yuan, warehouse_notification_id,
                      customer_reply, proof, created_at, updated_at
                    ) values (
                      :id, :company_id, :approval_id, :approval_status, :action, :source_workflow_id,
                      :after_sale_cost_yuan, :saved_minutes, :saved_yuan, :warehouse_notification_id,
                      :customer_reply, :proof, now(), now()
                    )
                    """
                ),
                {
                    "id": outcome.id,
                    "company_id": self.company_id,
                    "approval_id": outcome.approval_id,
                    "approval_status": outcome.approval_status,
                    "action": outcome.action,
                    "source_workflow_id": outcome.source_workflow_id,
                    "after_sale_cost_yuan": outcome.after_sale_cost_yuan,
                    "saved_minutes": outcome.saved_minutes,
                    "saved_yuan": outcome.saved_yuan,
                    "warehouse_notification_id": outcome.warehouse_notification_id,
                    "customer_reply": outcome.customer_reply,
                    "proof": outcome.proof,
                },
            )
            if outcome.warehouse_notification_id:
                session.execute(
                    text(
                        """
                        insert into warehouse_notifications (
                          id, company_id, source_outcome_id, source_workflow_id, action,
                          status, proof, created_at, updated_at
                        ) values (
                          :id, :company_id, :source_outcome_id, :source_workflow_id, :action,
                          'queued', :proof, now(), now()
                        )
                        """
                    ),
                    {
                        "id": outcome.warehouse_notification_id,
                        "company_id": self.company_id,
                        "source_outcome_id": outcome.id,
                        "source_workflow_id": outcome.source_workflow_id,
                        "action": outcome.action,
                        "proof": outcome.proof,
                    },
                )
            session.commit()
        return outcome

    def list_queued_warehouse_notifications(self, limit: int = 20) -> tuple[WarehouseNotification, ...]:
        with self.session_provider() as session:
            rows = session.execute(
                text(
                    """
                    select id, source_outcome_id, source_workflow_id, action, status,
                           external_reference, proof, created_at::text
                    from warehouse_notifications
                    where company_id = :company_id and status = 'queued'
                    order by created_at asc
                    limit :limit
                    """
                ),
                {"company_id": self.company_id, "limit": limit},
            ).mappings().all()
        return tuple(_warehouse_notification_from_row(row) for row in rows)

    def update_warehouse_notification_status(
        self,
        notification_id: str,
        status: WarehouseNotificationStatus,
        external_reference: str | None,
        proof: str,
    ) -> WarehouseNotification | None:
        with self.session_provider() as session:
            row = session.execute(
                text(
                    """
                    update warehouse_notifications
                    set status = :status,
                        external_reference = :external_reference,
                        proof = :proof,
                        updated_at = now()
                    where company_id = :company_id and id = :id
                    returning id, source_outcome_id, source_workflow_id, action, status,
                              external_reference, proof, created_at::text
                    """
                ),
                {
                    "company_id": self.company_id,
                    "id": notification_id,
                    "status": status,
                    "external_reference": external_reference,
                    "proof": proof,
                },
            ).mappings().first()
            session.commit()
        return _warehouse_notification_from_row(row) if row else None

    def summarize(self) -> dict[str, int | str]:
        with self.session_provider() as session:
            outcome_rows = session.execute(
                text(
                    """
                    select id, approval_id, approval_status, action, source_workflow_id,
                           after_sale_cost_yuan, saved_minutes, saved_yuan, warehouse_notification_id,
                           customer_reply, proof, created_at::text
                    from after_sale_decision_outcomes
                    where company_id = :company_id
                    order by created_at asc
                    limit 500
                    """
                ),
                {"company_id": self.company_id},
            ).mappings().all()
            notification_rows = session.execute(
                text(
                    """
                    select id, source_outcome_id, source_workflow_id, action, status,
                           external_reference, proof, created_at::text
                    from warehouse_notifications
                    where company_id = :company_id
                    order by created_at asc
                    limit 500
                    """
                ),
                {"company_id": self.company_id},
            ).mappings().all()
        return _summarize_outcomes(
            tuple(_outcome_from_row(row) for row in outcome_rows),
            tuple(_warehouse_notification_from_row(row) for row in notification_rows),
        )

    def clear_for_test(self) -> None:
        with self.session_provider() as session:
            session.execute(text("delete from warehouse_notifications where company_id = :company_id"), {"company_id": self.company_id})
            session.execute(text("delete from after_sale_decision_outcomes where company_id = :company_id"), {"company_id": self.company_id})
            session.commit()


_repository: AfterSaleDecisionOutcomeRepository = InMemoryAfterSaleDecisionOutcomeRepository()


def configure_after_sale_decision_outcome_repository(repository: AfterSaleDecisionOutcomeRepository) -> None:
    global _repository
    _repository = repository


def configure_after_sale_decision_outcome_repository_from_settings(
    session_provider: SessionProvider | None = None,
) -> AfterSaleDecisionOutcomeRepository:
    settings = get_settings()
    if settings.after_sale_decision_storage == "postgres" and session_provider is not None and settings.has_database:
        configure_after_sale_decision_outcome_repository(PostgresAfterSaleDecisionOutcomeRepository(session_provider))
    else:
        configure_after_sale_decision_outcome_repository(InMemoryAfterSaleDecisionOutcomeRepository())
    return _repository


def after_sale_decision_outcome_repository() -> AfterSaleDecisionOutcomeRepository:
    return _repository


def warehouse_notification_sender_from_settings() -> WarehouseNotificationSender:
    settings = get_settings()
    if settings.warehouse_notification_delivery_mode == "http_api":
        return HttpApiWarehouseNotificationSender()
    return ExportQueueWarehouseNotificationSender()


def dispatch_queued_warehouse_notifications(
    limit: int = 20,
    sender: WarehouseNotificationSender | None = None,
) -> dict[str, int | tuple[WarehouseNotificationDeliveryResult, ...]]:
    delivery_sender = sender or warehouse_notification_sender_from_settings()
    notifications = _repository.list_queued_warehouse_notifications(limit=limit)
    results: list[WarehouseNotificationDeliveryResult] = []
    for notification in notifications:
        try:
            result = delivery_sender.send(notification)
        except Exception as exc:  # pragma: no cover - defensive boundary for real WMS integrations.
            result = WarehouseNotificationDeliveryResult(
                id=notification.id,
                status="failed",
                external_reference=None,
                proof=f"Warehouse notification delivery failed: {exc}",
            )
        _repository.update_warehouse_notification_status(
            notification_id=notification.id,
            status=result.status,
            external_reference=result.external_reference,
            proof=result.proof,
        )
        results.append(result)
    return {
        "total_count": len(results),
        "sent_count": sum(1 for item in results if item.status == "sent"),
        "failed_count": sum(1 for item in results if item.status == "failed"),
        "cancelled_count": sum(1 for item in results if item.status == "cancelled"),
        "items": tuple(results),
    }


def run_after_sale_decision_workflow(
    approval: ApprovalRecord,
    decision: ApprovalDecision,
    action: AfterSaleAction,
    note: str,
) -> AfterSaleDecisionOutcome:
    normalized_action = "reject" if decision == "rejected" else action
    refund_amount = _extract_refund_amount(approval.reason)
    after_sale_cost = _estimate_after_sale_cost(normalized_action, refund_amount)
    warehouse_notification_id = f"warehouse-notice-{uuid4()}" if normalized_action == "replacement" and decision == "approved" else None
    saved_minutes = 16 if warehouse_notification_id else 12
    saved_yuan = _minutes_to_yuan(saved_minutes)
    customer_reply = _build_customer_reply(decision, normalized_action)
    proof = (
        f"Approval {approval.id} decided as {decision}; action={normalized_action}; "
        f"after_sale_cost_yuan={after_sale_cost}; warehouse_notification_id={warehouse_notification_id}; note={note}."
    )
    outcome = AfterSaleDecisionOutcome(
        id=f"after-sale-decision-{uuid4()}",
        approval_id=approval.id,
        approval_status=decision,
        action=normalized_action,  # type: ignore[arg-type]
        source_workflow_id=approval.source_id,
        after_sale_cost_yuan=after_sale_cost,
        saved_minutes=saved_minutes,
        saved_yuan=saved_yuan,
        warehouse_notification_id=warehouse_notification_id,
        customer_reply=customer_reply,
        proof=proof,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    return _repository.record_outcome(outcome)


def summarize_after_sale_decision_outcomes() -> dict[str, int | str]:
    return _repository.summarize()


def clear_after_sale_decision_outcomes_for_test() -> None:
    _repository.clear_for_test()


def _summarize_outcomes(
    outcomes: tuple[AfterSaleDecisionOutcome, ...],
    warehouse_notifications: tuple[WarehouseNotification, ...],
) -> dict[str, int | str]:
    if not outcomes:
        return {
            "completed_work_count": 0,
            "saved_minutes": 0,
            "saved_yuan": 0,
            "after_sale_cost_yuan": 0,
            "warehouse_notification_count": 0,
            "warehouse_notification_queued_count": 0,
            "warehouse_notification_sent_count": 0,
            "warehouse_notification_failed_count": 0,
            "latest_warehouse_notification_id": "",
            "latest_warehouse_notification_status": "",
            "proof": "",
        }
    saved_minutes = sum(item.saved_minutes for item in outcomes)
    saved_yuan = sum(item.saved_yuan for item in outcomes)
    after_sale_cost_yuan = sum(item.after_sale_cost_yuan for item in outcomes)
    latest = outcomes[-1]
    latest_notification = warehouse_notifications[-1] if warehouse_notifications else None
    queued_count = sum(1 for item in warehouse_notifications if item.status == "queued")
    sent_count = sum(1 for item in warehouse_notifications if item.status == "sent")
    failed_count = sum(1 for item in warehouse_notifications if item.status == "failed")
    return {
        "completed_work_count": len(outcomes),
        "saved_minutes": saved_minutes,
        "saved_yuan": saved_yuan,
        "after_sale_cost_yuan": after_sale_cost_yuan,
        "warehouse_notification_count": len(warehouse_notifications),
        "warehouse_notification_queued_count": queued_count,
        "warehouse_notification_sent_count": sent_count,
        "warehouse_notification_failed_count": failed_count,
        "latest_warehouse_notification_id": latest_notification.id if latest_notification else "",
        "latest_warehouse_notification_status": latest_notification.status if latest_notification else "",
        "proof": f"Recorded {len(outcomes)} after-sale approval decision outcomes. Latest: {latest.proof}",
    }

def _warehouse_notification_payload(notification: WarehouseNotification) -> dict[str, Any]:
    return {
        "notification_id": notification.id,
        "source_outcome_id": notification.source_outcome_id,
        "source_workflow_id": notification.source_workflow_id,
        "action": notification.action,
        "status": notification.status,
        "proof": notification.proof,
        "created_at": notification.created_at,
    }


def _extract_external_reference(body: Mapping[str, Any]) -> str | None:
    for key in ("external_reference", "externalReference", "reference", "id", "notification_id"):
        value = body.get(key)
        if value:
            return str(value)
    return None

def _estimate_after_sale_cost(action: str, refund_amount: int) -> int:
    if action == "refund":
        return refund_amount
    if action == "compensation":
        return min(50, max(10, round(refund_amount * 0.15)))
    if action == "replacement":
        return 0
    return 0


def _extract_refund_amount(reason: str) -> int:
    match = re.search(r"refund=(\d+)", reason)
    return int(match.group(1)) if match else 0


def _build_customer_reply(decision: str, action: str) -> str:
    if decision == "rejected":
        return "Boss rejected the after-sale request. Customer service should explain the evidence and offer a low-risk follow-up path."
    if action == "replacement":
        return "Boss approved replacement. Warehouse notification has been generated and customer service can confirm the replacement plan."
    if action == "compensation":
        return "Boss approved compensation. Customer service can confirm the compensation plan and record the after-sale reason."
    return "Boss approved refund. Customer service can confirm the refund plan and record the after-sale cost."


def _minutes_to_yuan(minutes: int) -> int:
    hourly_cost_yuan = 45
    return round(minutes / 60 * hourly_cost_yuan)


def _outcome_from_row(row) -> AfterSaleDecisionOutcome:
    return AfterSaleDecisionOutcome(
        id=str(row["id"]),
        approval_id=str(row["approval_id"]),
        approval_status=str(row["approval_status"]),  # type: ignore[arg-type]
        action=str(row["action"]),  # type: ignore[arg-type]
        source_workflow_id=str(row["source_workflow_id"]),
        after_sale_cost_yuan=int(row["after_sale_cost_yuan"] or 0),
        saved_minutes=int(row["saved_minutes"] or 0),
        saved_yuan=int(row["saved_yuan"] or 0),
        warehouse_notification_id=str(row["warehouse_notification_id"]) if row["warehouse_notification_id"] else None,
        customer_reply=str(row["customer_reply"] or ""),
        proof=str(row["proof"] or ""),
        created_at=str(row["created_at"]),
    )


def _warehouse_notification_from_row(row) -> WarehouseNotification:
    return WarehouseNotification(
        id=str(row["id"]),
        source_outcome_id=str(row["source_outcome_id"]),
        source_workflow_id=str(row["source_workflow_id"]),
        action=str(row["action"]),  # type: ignore[arg-type]
        status=str(row["status"]),  # type: ignore[arg-type]
        external_reference=str(row["external_reference"]) if row["external_reference"] else None,
        proof=str(row["proof"] or ""),
        created_at=str(row["created_at"]),
    )