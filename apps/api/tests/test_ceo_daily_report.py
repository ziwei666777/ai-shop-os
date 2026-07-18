import pytest
from fastapi.testclient import TestClient

from apps.api.app.infrastructure.after_sale_decision_workflow import (
    InMemoryAfterSaleDecisionOutcomeRepository,
    dispatch_queued_warehouse_notifications,
    clear_after_sale_decision_outcomes_for_test,
    configure_after_sale_decision_outcome_repository,
)
from apps.api.app.infrastructure.approval_records import (
    InMemoryApprovalRecordRepository,
    clear_dynamic_approvals_for_test,
    configure_approval_record_repository,
)
from apps.api.app.infrastructure.live_workflow_log_store import (
    InMemoryLiveWorkflowRunRepository,
    clear_live_workflow_runs_for_test,
    configure_live_workflow_repository,
)
from apps.api.app.main import app


@pytest.fixture(autouse=True)
def isolate_live_workflow_repository():
    repository = InMemoryLiveWorkflowRunRepository()
    configure_live_workflow_repository(repository)
    configure_approval_record_repository(InMemoryApprovalRecordRepository())
    configure_after_sale_decision_outcome_repository(InMemoryAfterSaleDecisionOutcomeRepository())
    clear_live_workflow_runs_for_test()
    clear_dynamic_approvals_for_test()
    clear_after_sale_decision_outcomes_for_test()
    yield
    configure_live_workflow_repository(InMemoryLiveWorkflowRunRepository())
    configure_approval_record_repository(InMemoryApprovalRecordRepository())
    configure_after_sale_decision_outcome_repository(InMemoryAfterSaleDecisionOutcomeRepository())
    clear_live_workflow_runs_for_test()
    clear_dynamic_approvals_for_test()
    clear_after_sale_decision_outcomes_for_test()


def test_ceo_daily_report_gives_boss_money_risk_and_actions() -> None:
    client = TestClient(app)

    response = client.get("/v1/ceo/daily-report")

    assert response.status_code == 200
    body = response.json()
    assert body["headline"]
    assert body["boss_message"]
    assert body["business_health_score"] > 0
    assert body["saved_money_today_yuan"] > 0
    assert body["projected_monthly_saving_yuan"] >= body["saved_money_today_yuan"]
    assert body["annual_roi_percent"] > 0
    assert body["replacement_target_yuan"] == 70000
    assert body["live_operation_status"]
    assert body["top_risks"]
    assert body["priority_actions"]
    assert any("Savings Engine" in item for item in body["proof_points"])


def test_ceo_daily_report_keeps_untraceable_live_workflow_as_demo() -> None:
    client = TestClient(app)

    client.post(
        "/v1/live-operations/pre-live-check",
        json={
            "products": [
                {"title": "featured product", "inventory_count": 70, "safe_stock": 20, "regular_price": 199, "live_price": 129}
            ],
            "coupons": [{"name": "live coupon", "remaining_count": 120, "expired": False}],
            "script_text": "No exaggerated claims.",
            "gift_ready": True,
            "product_order_ready": True,
        },
    )

    response = client.get("/v1/ceo/daily-report")

    assert response.status_code == 200
    body = response.json()
    assert body["data_status"] == "demo_estimate"
    assert body["saved_money_today_yuan"] > 0


def test_ceo_daily_report_keeps_unproven_database_rows_as_demo() -> None:
    from apps.api.app.infrastructure.daily_operations_runner import run_daily_operations

    run_daily_operations(
        pre_live={
            "products": ({"title": "Imported product", "inventory_count": 70, "safe_stock": 20, "regular_price": 199, "live_price": 129},),
            "evidence_source": {"source_type": "postgres", "tables": ("products",)},
        }
    )

    response = TestClient(app).get("/v1/ceo/daily-report")

    assert response.status_code == 200
    assert response.json()["data_status"] == "demo_estimate"


def test_ceo_daily_report_marks_hashed_file_import_as_real_data() -> None:
    from apps.api.app.infrastructure.daily_operations_runner import run_daily_operations

    run_daily_operations(
        pre_live={
            "products": ({"title": "Imported product", "inventory_count": 70, "safe_stock": 20, "regular_price": 199, "live_price": 129},),
            "evidence_source": {
                "source_type": "postgres",
                "tables": ("products",),
                "ingestion_evidence": (
                    {
                        "import_job_id": "import-products-1",
                        "platform": "taobao",
                        "import_mode": "file",
                        "file_name": "products-2026-07-18.csv",
                        "file_sha256": "a" * 64,
                    },
                ),
            },
        }
    )

    response = TestClient(app).get("/v1/ceo/daily-report")

    assert response.status_code == 200
    assert response.json()["data_status"] == "real_workflow_logs"

def test_ceo_daily_report_marks_traceable_live_snapshot_as_real_data() -> None:
    from apps.api.app.infrastructure.daily_operations_runner import run_daily_operations

    run_daily_operations(
        live_metrics={
            "online_users": 800,
            "conversion_rate": 0.12,
            "retention_rate": 0.38,
            "comment_count": 93,
            "like_count": 1800,
            "product_click_rate": 0.16,
            "inventory_delta": -32,
            "abnormal_order_count": 2,
            "evidence_source": {
                "snapshot_id": "live-metric-1001",
                "platform": "douyin",
                "stream_external_id": "douyin-live-1001",
                "observed_at": "2026-07-18T08:00:00+00:00",
                "source_reference": "douyin-open-platform:room-1001",
            },
        }
    )

    response = TestClient(app).get("/v1/ceo/daily-report")

    assert response.status_code == 200
    assert response.json()["data_status"] == "real_workflow_logs"


def test_ceo_daily_report_shows_after_sale_decision_cost_and_warehouse_notice() -> None:
    client = TestClient(app)

    run_response = client.post(
        "/v1/workflows/refund-collaboration/run",
        json={
            "source_message_id": "msg-ceo-replacement-proof",
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
            "note": "Approve replacement so warehouse can execute the after-sale work.",
        },
    )
    assert decision_response.status_code == 200

    dispatch_response = client.post("/v1/warehouse-notifications/dispatch")
    assert dispatch_response.status_code == 200
    dispatch_body = dispatch_response.json()
    assert dispatch_body["total_count"] == 1
    assert dispatch_body["sent_count"] == 1
    assert dispatch_body["items"][0]["external_reference"].startswith("wms-export-")

    response = client.get("/v1/ceo/daily-report")

    assert response.status_code == 200
    body = response.json()
    assert any("After-sale decisions recorded 1 approval outcomes" in item for item in body["proof_points"])
    assert any("after-sale cost 0 yuan" in item for item in body["proof_points"])
    assert any("warehouse notices 1" in item for item in body["proof_points"])
    assert any("sent 1" in item and "queued 0" in item for item in body["proof_points"])
    assert any(action["id"] == "after-sale-warehouse-notice" for action in body["priority_actions"])

def test_ceo_daily_report_flags_failed_warehouse_notifications_as_boss_risk() -> None:
    class FailingWarehouseSender:
        def send(self, notification):
            raise RuntimeError("WMS timeout")

    client = TestClient(app)

    run_response = client.post(
        "/v1/workflows/refund-collaboration/run",
        json={
            "source_message_id": "msg-ceo-wms-failed",
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
            "note": "Approve replacement but WMS is unavailable.",
        },
    )
    dispatch_queued_warehouse_notifications(sender=FailingWarehouseSender())

    response = client.get("/v1/ceo/daily-report")

    assert response.status_code == 200
    body = response.json()
    assert any(risk["id"] == "risk-warehouse-notification-failed" for risk in body["top_risks"])
    assert any(action["id"] == "after-sale-warehouse-failed" for action in body["priority_actions"])
    assert any("failed 1" in item for item in body["proof_points"])