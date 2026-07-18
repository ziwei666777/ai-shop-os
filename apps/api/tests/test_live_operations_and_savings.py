from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api.app.infrastructure.live_workflow_log_store import (
    InMemoryLiveWorkflowRunRepository,
    clear_live_workflow_runs_for_test,
    configure_live_workflow_repository,
    configure_live_workflow_repository_from_settings,
    live_workflow_repository,
    PostgresLiveWorkflowRunRepository,
)
from apps.api.app.main import app


@pytest.fixture(autouse=True)
def isolate_live_workflow_repository() -> None:
    repository = InMemoryLiveWorkflowRunRepository()
    configure_live_workflow_repository(repository)
    clear_live_workflow_runs_for_test()


def test_live_workflow_repository_can_be_injected_for_future_database_storage() -> None:
    repository = InMemoryLiveWorkflowRunRepository()
    configure_live_workflow_repository(repository)

    assert live_workflow_repository() is repository
    assert live_workflow_repository().summarize()["completed_work_count"] == 0


def test_live_workflow_repository_defaults_to_memory_until_database_schema_is_confirmed() -> None:
    repository = configure_live_workflow_repository_from_settings()

    assert isinstance(repository, InMemoryLiveWorkflowRunRepository)


def test_live_workflow_repository_can_switch_to_postgres_when_explicitly_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps.api.app.infrastructure import live_workflow_log_store

    class FakeSettings:
        live_workflow_log_storage = "postgres"
        has_database = True
        local_company_id = "00000000-0000-0000-0000-000000000001"

    def fake_session_provider():
        raise AssertionError("仓储配置阶段不应打开数据库连接")

    monkeypatch.setattr(live_workflow_log_store, "get_settings", lambda: FakeSettings())

    repository = configure_live_workflow_repository_from_settings(fake_session_provider)

    assert isinstance(repository, PostgresLiveWorkflowRunRepository)


def test_live_workflow_runs_migration_keeps_savings_and_proof_columns() -> None:
    migration = (
        Path(__file__).resolve().parents[3]
        / "supabase"
        / "migrations"
        / "202607150001_live_workflow_runs.sql"
    )

    sql = migration.read_text(encoding="utf-8")

    required_fragments = [
        "create table if not exists public.live_workflow_runs",
        "workflow_stage",
        "approval_required",
        "proof text not null",
        "saved_minutes",
        "saved_cost_yuan",
        "risk_score",
        "alerts jsonb",
        "recommended_actions jsonb",
        "public.is_company_member(company_id)",
    ]

    for fragment in required_fragments:
        assert fragment in sql


def test_live_operation_summary_focuses_on_live_assistant_workflow() -> None:
    client = TestClient(app)

    response = client.get("/v1/live-operations/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["replacement_role"] == "直播运营助理"
    assert body["target_monthly_salary_yuan"] > 0
    assert body["pre_live_ready_score"] > 0
    assert any(item["stage"] == "pre_live" for item in body["checklist"])
    assert any(item["stage"] == "during_live" for item in body["checklist"])
    assert any(item["stage"] == "post_live" for item in body["checklist"])
    assert body["alerts"][0]["suggested_action"]


def test_savings_summary_calculates_money_and_roi() -> None:
    client = TestClient(app)

    response = client.get("/v1/savings/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["target_monthly_replacement_yuan"] == 70000
    assert body["today_saved_minutes"] > 0
    assert body["today_saved_yuan"] > 0
    assert body["projected_monthly_saving_yuan"] > body["today_saved_yuan"]
    assert body["annual_roi_percent"] > 0
    assert any(agent["agent_id"] == "ai-live-operator" for agent in body["agents"])
    assert all(agent["replaced_role"] for agent in body["agents"])


def test_pre_live_check_blocks_risky_live_setup() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/live-operations/pre-live-check",
        json={
            "products": [
                {"title": "主推连衣裙", "inventory_count": 8, "safe_stock": 20, "regular_price": 99, "live_price": 109}
            ],
            "coupons": [{"name": "直播间 10 元券", "remaining_count": 0, "expired": False}],
            "script_text": "今晚全网第一，优惠永久有效。",
            "gift_ready": False,
            "product_order_ready": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stage"] == "pre_live"
    assert body["status"] == "blocked"
    assert body["estimated_saving_yuan"] > 0
    assert any(alert["id"] == "pre-alert-script" for alert in body["alerts"])
    assert any(check["requires_approval"] for check in body["checks"])


def test_live_metric_scan_creates_active_stream_alerts() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/live-operations/live-metric-scan",
        json={
            "online_users": 88,
            "conversion_rate": 0.012,
            "retention_rate": 0.22,
            "comment_count": 12,
            "like_count": 300,
            "product_click_rate": 0.04,
            "inventory_delta": -80,
            "abnormal_order_count": 2,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stage"] == "during_live"
    assert body["status"] == "blocked"
    assert any(alert["id"] == "live-alert-retention" for alert in body["alerts"])
    assert any(alert["id"] == "live-alert-order" for alert in body["alerts"])
    assert body["next_actions"]


def test_post_live_review_outputs_next_day_actions_and_savings() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/live-operations/post-live-review",
        json={
            "sales_amount_yuan": 38600,
            "order_count": 120,
            "viewer_count": 4200,
            "refund_count": 13,
            "top_product_title": "主推连衣裙",
            "negative_comment_count": 24,
            "host_script_score": 72,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["stage"] == "post_live"
    assert body["status"] == "warning"
    assert body["estimated_saving_yuan"] > 0
    assert body["conversion_rate"] > 0
    assert "退款风险" in body["refund_risk_note"]
    assert body["next_day_actions"]


def test_live_workflow_runs_are_recorded_and_used_by_savings_engine() -> None:
    client = TestClient(app)

    client.post(
        "/v1/live-operations/pre-live-check",
        json={
            "products": [
                {"title": "主推连衣裙", "inventory_count": 80, "safe_stock": 20, "regular_price": 129, "live_price": 99}
            ],
            "coupons": [{"name": "直播间券", "remaining_count": 100, "expired": False}],
            "script_text": "今晚福利讲清楚，不承诺绝对效果。",
            "gift_ready": True,
            "product_order_ready": True,
        },
    )

    runs = client.get("/v1/live-operations/runs")
    savings = client.get("/v1/savings/summary")

    assert runs.status_code == 200
    assert len(runs.json()) == 1
    assert runs.json()[0]["workflow_name"] == "开播前检查"
    assert runs.json()[0]["saved_minutes"] > 0
    live_operator = next(agent for agent in savings.json()["agents"] if agent["agent_id"] == "ai-live-operator")
    assert live_operator["completed_work_count"] == 1
    assert live_operator["saved_minutes"] == runs.json()[0]["saved_minutes"]



def test_daily_operations_run_without_payload_marks_safe_baseline() -> None:
    client = TestClient(app)

    response = client.post("/v1/daily-operations/run", json={})

    assert response.status_code == 200
    body = response.json()
    assert body["replacement_role"] == "直播运营助理"
    assert body["input_mode"] == "safe_baseline"
    assert body["status"] == "needs_real_data"
    assert body["completed_work_count"] == 1
    assert body["saved_minutes"] > 0
    assert body["saved_yuan"] > 0
    assert "真实数据" in body["operator_message"]
    assert body["workflow_runs"][0]["workflow_name"] == "每日开播前自动巡检"


def test_daily_operations_run_with_merchant_payload_records_three_workflows() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/daily-operations/run",
        json={
            "trigger": "scheduled",
            "pre_live": {
                "products": [
                    {"title": "抖店主推套装", "inventory_count": 120, "safe_stock": 30, "regular_price": 169, "live_price": 129}
                ],
                "coupons": [{"name": "直播间 20 元券", "remaining_count": 300, "expired": False}],
                "script_text": "今晚福利讲清楚，不承诺绝对效果。",
                "gift_ready": True,
                "product_order_ready": True,
            },
            "live_metrics": {
                "online_users": 800,
                "conversion_rate": 0.045,
                "retention_rate": 0.42,
                "comment_count": 180,
                "like_count": 6000,
                "product_click_rate": 0.18,
                "inventory_delta": -35,
                "abnormal_order_count": 0,
            },
            "post_live": {
                "sales_amount_yuan": 58600,
                "order_count": 260,
                "viewer_count": 9000,
                "refund_count": 8,
                "top_product_title": "抖店主推套装",
                "negative_comment_count": 6,
                "host_script_score": 86,
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["trigger"] == "scheduled"
    assert body["input_mode"] == "merchant_payload"
    assert body["status"] == "completed"
    assert body["completed_work_count"] == 3
    assert body["saved_minutes"] == sum(run["saved_minutes"] for run in body["workflow_runs"])
    assert body["saved_yuan"] == sum(run["estimated_saving_yuan"] for run in body["workflow_runs"])
    assert body["savings_summary"]["agents"][0]["completed_work_count"] == 3
    assert body["ceo_report"]["saved_money_today_yuan"] >= body["saved_yuan"]


def test_api_startup_configures_live_workflow_repository_for_http_workflows(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps.api.app import main as main_module

    configured_sessions: list[str | None] = []

    def fake_session_factory() -> str:
        return "postgres-session"

    def fake_configure(session_provider=None):
        configured_sessions.append(session_provider() if session_provider else None)
        return InMemoryLiveWorkflowRunRepository()

    monkeypatch.setattr(main_module, "SessionFactory", fake_session_factory)
    monkeypatch.setattr(main_module, "configure_live_workflow_repository_from_settings", fake_configure)

    main_module.create_app()

    assert configured_sessions == ["postgres-session"]
