from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api.app.infrastructure.after_sale_decision_workflow import (
    HttpApiWarehouseNotificationSender,
    InMemoryAfterSaleDecisionOutcomeRepository,
    PostgresAfterSaleDecisionOutcomeRepository,
    after_sale_decision_outcome_repository,
    clear_after_sale_decision_outcomes_for_test,
    configure_after_sale_decision_outcome_repository,
    configure_after_sale_decision_outcome_repository_from_settings,
    dispatch_queued_warehouse_notifications,
    warehouse_notification_sender_from_settings,
    summarize_after_sale_decision_outcomes,
)
from apps.api.app.infrastructure.approval_records import (
    InMemoryApprovalRecordRepository,
    PostgresApprovalRecordRepository,
    approval_record_repository,
    clear_dynamic_approvals_for_test,
    configure_approval_record_repository,
    configure_approval_record_repository_from_settings,
)

from apps.api.app.infrastructure.refund_business_evidence import RefundBusinessEvidence
from apps.api.app.infrastructure.refund_collaboration_workflow import clear_refund_collaboration_runs_for_test
from apps.api.app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def isolate_approval_records():
    configure_approval_record_repository(InMemoryApprovalRecordRepository())
    configure_after_sale_decision_outcome_repository(InMemoryAfterSaleDecisionOutcomeRepository())
    clear_dynamic_approvals_for_test()
    clear_after_sale_decision_outcomes_for_test()
    yield
    configure_approval_record_repository(InMemoryApprovalRecordRepository())
    configure_after_sale_decision_outcome_repository(InMemoryAfterSaleDecisionOutcomeRepository())
    clear_dynamic_approvals_for_test()
    clear_after_sale_decision_outcomes_for_test()


def test_refund_collaboration_routes_after_sale_work_into_savings_engine() -> None:
    clear_refund_collaboration_runs_for_test()
    clear_dynamic_approvals_for_test()

    before = client.get("/v1/savings/summary").json()
    before_after_sale = next(agent for agent in before["agents"] if agent["agent_id"] == "ai-after-sale")

    response = client.post(
        "/v1/workflows/refund-collaboration/run",
        json={
            "source_message_id": "msg-refund-1",
            "customer_message": "Customer asks for refund because the product is damaged and may complain.",
            "order_amount_yuan": 399,
            "refund_amount_yuan": 299,
            "delivered": True,
            "evidence_count": 2,
            "inventory_available": True,
            "complaint_risk": True,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approval_required"
    assert body["decision"] == "refund_review"
    assert body["saved_minutes"] > 0
    assert body["estimated_saving_yuan"] > 0
    assert body["approval_id"] is not None
    assert any(step["agent_id"] == "ai-after-sale" for step in body["steps"])
    assert any(step["agent_id"] == "ai-boss" and step["requires_approval"] for step in body["steps"])
    assert body["steps"][-1]["agent_id"] == "ai-customer"

    after = client.get("/v1/savings/summary").json()
    after_after_sale = next(agent for agent in after["agents"] if agent["agent_id"] == "ai-after-sale")
    assert after_after_sale["completed_work_count"] == before_after_sale["completed_work_count"] + 1
    assert after_after_sale["saved_minutes"] == before_after_sale["saved_minutes"] + body["saved_minutes"]
    assert after_after_sale["saved_yuan"] == before_after_sale["saved_yuan"] + body["estimated_saving_yuan"]
    assert "refund collaboration" in after_after_sale["proof"]

    pending_approvals = client.get("/v1/approvals/pending").json()
    assert any(item["id"] == body["approval_id"] for item in pending_approvals)


def test_refund_collaboration_blocks_when_evidence_is_missing() -> None:
    clear_refund_collaboration_runs_for_test()
    clear_dynamic_approvals_for_test()

    response = client.post(
        "/v1/workflows/refund-collaboration/run",
        json={
            "source_message_id": "msg-refund-no-proof",
            "customer_message": "I want a refund.",
            "order_amount_yuan": 129,
            "refund_amount_yuan": 129,
            "delivered": True,
            "evidence_count": 0,
            "inventory_available": False,
            "complaint_risk": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "blocked"
    assert body["decision"] == "need_more_evidence"
    assert body["approval_id"] is None
    assert any(step["status"] == "blocked" for step in body["steps"])
    assert "evidence" in body["proof"]


def test_approval_record_repository_can_be_injected_for_future_database_storage() -> None:
    repository = InMemoryApprovalRecordRepository()
    configure_approval_record_repository(repository)

    assert approval_record_repository() is repository
    assert len(approval_record_repository().list_pending_approvals()) == 2


def test_approval_record_repository_defaults_to_memory_until_database_schema_is_confirmed() -> None:
    repository = configure_approval_record_repository_from_settings()

    assert isinstance(repository, InMemoryApprovalRecordRepository)


def test_approval_record_repository_can_switch_to_postgres_when_explicitly_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps.api.app.infrastructure import approval_records

    class FakeSettings:
        approval_record_storage = "postgres"
        has_database = True
        local_company_id = "00000000-0000-0000-0000-000000000001"

    def fake_session_provider():
        raise AssertionError("repository configuration should not open the database connection")

    monkeypatch.setattr(approval_records, "get_settings", lambda: FakeSettings())

    repository = configure_approval_record_repository_from_settings(fake_session_provider)

    assert isinstance(repository, PostgresApprovalRecordRepository)


def test_approval_records_migration_keeps_boss_decision_and_proof_columns() -> None:
    migration = (
        Path(__file__).resolve().parents[3]
        / "supabase"
        / "migrations"
        / "202607160001_approval_records.sql"
    )

    sql = migration.read_text(encoding="utf-8")

    required_fragments = [
        "create table if not exists public.approval_records",
        "company_id uuid not null references public.companies(id)",
        "risk_level text not null check",
        "status text not null check",
        "source_type text not null",
        "source_id text not null",
        "reason text not null",
        "recommended_action text not null",
        "decision_note text",
        "metadata jsonb",
        "public.is_company_member(company_id)",
    ]

    for fragment in required_fragments:
        assert fragment in sql

def test_refund_collaboration_prefers_real_order_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps.api.app.interfaces.http import routes

    clear_refund_collaboration_runs_for_test()
    clear_dynamic_approvals_for_test()

    def fake_get_refund_business_evidence(order_external_id: str | None) -> RefundBusinessEvidence | None:
        assert order_external_id == "ORDER-REAL-1"
        return RefundBusinessEvidence(
            source="real_order_records",
            order_external_id="ORDER-REAL-1",
            order_amount_yuan=588,
            delivered=True,
            inventory_available=False,
            evidence_count=4,
            proof="real order evidence: order=ORDER-REAL-1, status=delivered, shipments=['delivered'], items=2.",
        )

    monkeypatch.setattr(routes, "get_refund_business_evidence", fake_get_refund_business_evidence)

    response = client.post(
        "/v1/workflows/refund-collaboration/run",
        json={
            "source_message_id": "msg-real-order-refund",
            "customer_message": "Customer wants refund for delivered order.",
            "order_external_id": "ORDER-REAL-1",
            "order_amount_yuan": 1,
            "refund_amount_yuan": 299,
            "delivered": False,
            "evidence_count": 0,
            "inventory_available": True,
            "complaint_risk": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["evidence_source"] == "real_order_records"
    assert body["status"] == "approval_required"
    assert body["approval_id"] is not None
    assert "ORDER-REAL-1" in body["proof"]
    assert "order_amount=588" in body["proof"]
    assert any("source=real_order_records" in step["evidence"] for step in body["steps"])

def test_approval_decision_writes_after_sale_outcome_and_warehouse_notice() -> None:
    clear_refund_collaboration_runs_for_test()
    clear_dynamic_approvals_for_test()
    clear_after_sale_decision_outcomes_for_test()

    before = client.get("/v1/savings/summary").json()
    before_after_sale = next(agent for agent in before["agents"] if agent["agent_id"] == "ai-after-sale")

    run_response = client.post(
        "/v1/workflows/refund-collaboration/run",
        json={
            "source_message_id": "msg-replacement-approval",
            "customer_message": "Customer asks for refund, but package is not delivered and replacement is possible.",
            "order_amount_yuan": 399,
            "refund_amount_yuan": 299,
            "delivered": False,
            "evidence_count": 2,
            "inventory_available": True,
            "complaint_risk": True,
        },
    )
    approval_id = run_response.json()["approval_id"]

    decision_response = client.post(
        f"/v1/approvals/{approval_id}/decision",
        json={
            "decision": "approved",
            "action": "replacement",
            "note": "Approve replacement to reduce refund loss and notify warehouse.",
        },
    )

    assert decision_response.status_code == 200
    body = decision_response.json()
    assert body["approval_id"] == approval_id
    assert body["approval_status"] == "approved"
    assert body["action"] == "replacement"
    assert body["warehouse_notification_id"] is not None
    assert body["after_sale_cost_yuan"] == 0
    assert body["saved_minutes"] > 0
    assert "warehouse_notification_id" in body["proof"]

    pending_approvals = client.get("/v1/approvals/pending").json()
    assert all(item["id"] != approval_id for item in pending_approvals)

    after = client.get("/v1/savings/summary").json()
    after_after_sale = next(agent for agent in after["agents"] if agent["agent_id"] == "ai-after-sale")
    assert after_after_sale["completed_work_count"] == before_after_sale["completed_work_count"] + 2
    assert after_after_sale["saved_minutes"] >= before_after_sale["saved_minutes"] + run_response.json()["saved_minutes"] + body["saved_minutes"]
    assert "after-sale approval decision outcomes" in after_after_sale["proof"]

def test_after_sale_decision_outcome_repository_can_be_injected_for_future_database_storage() -> None:
    repository = InMemoryAfterSaleDecisionOutcomeRepository()
    configure_after_sale_decision_outcome_repository(repository)

    assert after_sale_decision_outcome_repository() is repository
    assert after_sale_decision_outcome_repository().summarize()["completed_work_count"] == 0


def test_after_sale_decision_outcome_repository_defaults_to_memory_until_database_schema_is_confirmed() -> None:
    repository = configure_after_sale_decision_outcome_repository_from_settings()

    assert isinstance(repository, InMemoryAfterSaleDecisionOutcomeRepository)


def test_after_sale_decision_outcome_repository_can_switch_to_postgres_when_explicitly_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps.api.app.infrastructure import after_sale_decision_workflow

    class FakeSettings:
        after_sale_decision_storage = "postgres"
        has_database = True
        local_company_id = "00000000-0000-0000-0000-000000000001"

    def fake_session_provider():
        raise AssertionError("repository configuration should not open the database connection")

    monkeypatch.setattr(after_sale_decision_workflow, "get_settings", lambda: FakeSettings())

    repository = configure_after_sale_decision_outcome_repository_from_settings(fake_session_provider)

    assert isinstance(repository, PostgresAfterSaleDecisionOutcomeRepository)


def test_after_sale_decision_outcomes_migration_keeps_savings_cost_and_warehouse_columns() -> None:
    migration = (
        Path(__file__).resolve().parents[3]
        / "supabase"
        / "migrations"
        / "202607170001_after_sale_decision_outcomes.sql"
    )

    sql = migration.read_text(encoding="utf-8")

    required_fragments = [
        "create table if not exists public.after_sale_decision_outcomes",
        "create table if not exists public.warehouse_notifications",
        "approval_id text not null",
        "after_sale_cost_yuan integer not null",
        "saved_minutes integer not null",
        "saved_yuan integer not null",
        "warehouse_notification_id text",
        "customer_reply text not null",
        "proof text not null",
        "public.is_company_member(company_id)",
    ]

    for fragment in required_fragments:
        assert fragment in sql

def test_warehouse_notification_dispatch_marks_failed_when_wms_sender_fails() -> None:
    class FailingWarehouseSender:
        def send(self, notification):
            raise RuntimeError("WMS timeout")

    clear_refund_collaboration_runs_for_test()
    clear_dynamic_approvals_for_test()
    clear_after_sale_decision_outcomes_for_test()

    run_response = client.post(
        "/v1/workflows/refund-collaboration/run",
        json={
            "source_message_id": "msg-wms-fail",
            "customer_message": "Customer asks for refund, but replacement is possible.",
            "order_amount_yuan": 399,
            "refund_amount_yuan": 299,
            "delivered": False,
            "evidence_count": 2,
            "inventory_available": True,
            "complaint_risk": True,
        },
    )
    assert run_response.status_code == 200
    approval_id = run_response.json()["approval_id"]

    decision_response = client.post(
        f"/v1/approvals/{approval_id}/decision",
        json={
            "decision": "approved",
            "action": "replacement",
            "note": "Approve replacement but WMS is temporarily unavailable.",
        },
    )
    assert decision_response.status_code == 200

    dispatch_result = dispatch_queued_warehouse_notifications(sender=FailingWarehouseSender())

    assert dispatch_result["total_count"] == 1
    assert dispatch_result["failed_count"] == 1
    summary = summarize_after_sale_decision_outcomes()
    assert summary["warehouse_notification_failed_count"] == 1
    assert summary["warehouse_notification_queued_count"] == 0
    assert summary["latest_warehouse_notification_status"] == "failed"

def test_http_api_warehouse_notification_sender_posts_wms_payload() -> None:
    captured: dict[str, object] = {}

    def fake_post(url, payload, headers, timeout_seconds):
        captured["url"] = url
        captured["payload"] = payload
        captured["headers"] = headers
        captured["timeout_seconds"] = timeout_seconds
        return {"external_reference": "ERP-REPLACE-1001"}

    sender = HttpApiWarehouseNotificationSender(
        api_url="https://wms.example.test/replacement-notices",
        api_key="wms-secret",
        timeout_seconds=3.5,
        post_json=fake_post,
    )

    run_response = client.post(
        "/v1/workflows/refund-collaboration/run",
        json={
            "source_message_id": "msg-wms-api",
            "customer_message": "Customer asks for refund, but replacement is possible.",
            "order_amount_yuan": 399,
            "refund_amount_yuan": 299,
            "delivered": False,
            "evidence_count": 2,
            "inventory_available": True,
            "complaint_risk": True,
        },
    )
    approval_id = run_response.json()["approval_id"]
    client.post(
        f"/v1/approvals/{approval_id}/decision",
        json={
            "decision": "approved",
            "action": "replacement",
            "note": "Send replacement to WMS API.",
        },
    )

    dispatch_result = dispatch_queued_warehouse_notifications(sender=sender)

    assert dispatch_result["sent_count"] == 1
    assert dispatch_result["items"][0].external_reference == "ERP-REPLACE-1001"
    assert captured["url"] == "https://wms.example.test/replacement-notices"
    assert captured["headers"] == {"Content-Type": "application/json", "Authorization": "Bearer wms-secret"}
    assert captured["timeout_seconds"] == 3.5
    payload = captured["payload"]
    assert payload["notification_id"].startswith("warehouse-notice-")
    assert payload["action"] == "replacement"
    assert payload["status"] == "queued"


def test_http_api_warehouse_notification_sender_fails_without_api_url() -> None:
    sender = HttpApiWarehouseNotificationSender(api_url="", api_key="", timeout_seconds=1.0)

    run_response = client.post(
        "/v1/workflows/refund-collaboration/run",
        json={
            "source_message_id": "msg-wms-missing-url",
            "customer_message": "Customer asks for refund, but replacement is possible.",
            "order_amount_yuan": 399,
            "refund_amount_yuan": 299,
            "delivered": False,
            "evidence_count": 2,
            "inventory_available": True,
            "complaint_risk": True,
        },
    )
    approval_id = run_response.json()["approval_id"]
    client.post(
        f"/v1/approvals/{approval_id}/decision",
        json={
            "decision": "approved",
            "action": "replacement",
            "note": "Try WMS API but URL is missing.",
        },
    )

    dispatch_result = dispatch_queued_warehouse_notifications(sender=sender)

    assert dispatch_result["failed_count"] == 1
    assert "API URL is not configured" in dispatch_result["items"][0].proof
    summary = summarize_after_sale_decision_outcomes()
    assert summary["warehouse_notification_failed_count"] == 1


def test_warehouse_notification_sender_from_settings_can_use_http_api(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps.api.app.infrastructure import after_sale_decision_workflow

    class FakeSettings:
        warehouse_notification_delivery_mode = "http_api"
        warehouse_notification_wms_api_url = "https://wms.example.test/notices"
        warehouse_notification_wms_api_key = "secret"
        warehouse_notification_wms_timeout_seconds = 8.0
        warehouse_notification_export_prefix = "wms-export"

    monkeypatch.setattr(after_sale_decision_workflow, "get_settings", lambda: FakeSettings())

    sender = warehouse_notification_sender_from_settings()

    assert isinstance(sender, HttpApiWarehouseNotificationSender)