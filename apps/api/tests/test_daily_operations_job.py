import json
from pathlib import Path

from apps.api.app.infrastructure import daily_operations_job
from apps.api.app.infrastructure.live_workflow_log_store import clear_live_workflow_runs_for_test, configure_live_workflow_repository_from_settings


def test_daily_operations_job_runs_in_memory_mode(monkeypatch) -> None:
    settings = daily_operations_job.get_settings()
    monkeypatch.setattr(settings, "live_workflow_log_storage", "memory")
    monkeypatch.setattr(daily_operations_job, "SessionFactory", None)
    configure_live_workflow_repository_from_settings()
    clear_live_workflow_runs_for_test()

    result = daily_operations_job.run_daily_operations_job()

    assert result.status == "completed"
    assert result.trigger == "scheduled"
    assert result.storage == "memory"
    assert result.evidence_chain_ready is False
    assert result.completed_work_count == 1
    assert result.saved_minutes > 0
    assert result.saved_yuan > 0
    assert result.daily_run_id is not None


def test_daily_operations_job_blocks_when_postgres_required_without_database(monkeypatch) -> None:
    settings = daily_operations_job.get_settings()
    monkeypatch.setattr(settings, "live_workflow_log_storage", "postgres")
    monkeypatch.setattr(daily_operations_job, "SessionFactory", None)

    result = daily_operations_job.run_daily_operations_job()

    assert result.status == "blocked"
    assert result.storage == "postgres"
    assert result.evidence_chain_ready is False
    assert result.completed_work_count == 0
    assert any("DATABASE_URL" in item for item in result.next_actions)


def test_daily_operations_script_is_cross_platform() -> None:
    root = Path(__file__).resolve().parents[3]
    package_json = json.loads((root / "package.json").read_text(encoding="utf-8-sig"))
    script = package_json["scripts"]["api:daily-operations"]

    assert script == "node tools/run-api-module.cjs apps.api.app.infrastructure.daily_operations_job"
    assert ".venv\\Scripts" not in script


def test_render_cron_runs_daily_operations_job() -> None:
    root = Path(__file__).resolve().parents[3]
    render_yaml = (root / "render.yaml").read_text(encoding="utf-8-sig")

    assert "type: cron" in render_yaml
    assert "ai-commerce-os-daily-operations" in render_yaml
    assert "python -m apps.api.app.infrastructure.daily_operations_job" in render_yaml
    assert "LIVE_WORKFLOW_LOG_STORAGE" in render_yaml


def test_daily_operations_job_blocks_when_evidence_chain_not_ready_with_database(monkeypatch) -> None:
    settings = daily_operations_job.get_settings()
    monkeypatch.setattr(settings, "live_workflow_log_storage", "postgres")
    monkeypatch.setattr(daily_operations_job, "SessionFactory", object())

    result = daily_operations_job.run_daily_operations_job()

    assert result.status == "blocked"
    assert result.evidence_chain_ready is False
    assert result.daily_run_id is None
    assert result.completed_work_count == 0
    assert any("APPROVAL_RECORD_STORAGE=postgres" in item for item in result.evidence_chain_blockers)
    assert "生产证据链尚未 ready" in result.message

def test_production_daily_job_blocks_without_merchant_source_data(monkeypatch) -> None:
    from apps.api.app.infrastructure import daily_operations_job
    from apps.api.app.infrastructure.daily_operations_data_provider import DailyOperationsSourceData

    settings = daily_operations_job.get_settings()
    monkeypatch.setattr(settings, "live_workflow_log_storage", "postgres")
    monkeypatch.setattr(settings, "approval_record_storage", "postgres")
    monkeypatch.setattr(settings, "after_sale_decision_storage", "postgres")
    monkeypatch.setattr(settings, "ceo_report_snapshot_storage", "postgres")
    monkeypatch.setattr(settings, "warehouse_notification_delivery_mode", "http_api")
    monkeypatch.setattr(settings, "warehouse_notification_wms_api_url", "https://wms.example.test/notices")
    monkeypatch.setattr(settings, "warehouse_notification_wms_api_key", "test-secret")

    class FakeResult:
        def scalar_one(self):
            return 1

        def scalars(self):
            return iter(())

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, statement, params=None):
            return FakeResult()

    monkeypatch.setattr(daily_operations_job, "SessionFactory", lambda: FakeSession())
    monkeypatch.setattr(daily_operations_job, "find_missing_evidence_tables", lambda session: ())
    monkeypatch.setattr(
        daily_operations_job,
        "load_daily_operations_source_data",
        lambda session_provider, company_id: DailyOperationsSourceData(
            source_mode="empty",
            pre_live=None,
            live_metrics=None,
            post_live=None,
            product_count=0,
            order_count=0,
            after_sale_count=0,
            warnings=("真实商品和订单数据为空。",),
        ),
    )
    monkeypatch.setattr(
        daily_operations_job,
        "run_daily_operations",
        lambda **kwargs: (_ for _ in ()).throw(AssertionError("safe baseline must not run in production")),
    )

    result = daily_operations_job.run_daily_operations_job()

    assert result.status == "blocked"
    assert result.evidence_chain_ready is True
    assert result.daily_run_id is None
    assert "真实商品和订单数据为空。" in result.next_actions


def test_production_daily_job_forwards_database_source_to_workflow(monkeypatch) -> None:
    from types import SimpleNamespace

    from apps.api.app.infrastructure import daily_operations_job
    from apps.api.app.infrastructure.daily_operations_data_provider import DailyOperationsSourceData

    settings = daily_operations_job.get_settings()
    monkeypatch.setattr(settings, "live_workflow_log_storage", "postgres")
    monkeypatch.setattr(settings, "approval_record_storage", "postgres")
    monkeypatch.setattr(settings, "after_sale_decision_storage", "postgres")
    monkeypatch.setattr(settings, "ceo_report_snapshot_storage", "postgres")
    monkeypatch.setattr(settings, "warehouse_notification_delivery_mode", "http_api")
    monkeypatch.setattr(settings, "warehouse_notification_wms_api_url", "https://wms.example.test/notices")
    monkeypatch.setattr(settings, "warehouse_notification_wms_api_key", "test-secret")

    class FakeResult:
        def scalar_one(self):
            return 1

        def scalars(self):
            return iter(())

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, statement, params=None):
            return FakeResult()

    monkeypatch.setattr(daily_operations_job, "SessionFactory", lambda: FakeSession())
    monkeypatch.setattr(daily_operations_job, "find_missing_evidence_tables", lambda session: ())
    source = DailyOperationsSourceData(
        source_mode="database",
        pre_live={"products": ({"title": "真实商品"},)},
        live_metrics=None,
        post_live={"order_count": 1},
        product_count=1,
        order_count=1,
        after_sale_count=0,
        warnings=(),
    )
    captured = {}
    monkeypatch.setattr(daily_operations_job, "load_daily_operations_source_data", lambda session_provider, company_id: source)
    monkeypatch.setattr(daily_operations_job, "configure_live_workflow_repository_from_settings", lambda *args: None)
    monkeypatch.setattr(daily_operations_job, "configure_ceo_daily_report_snapshot_repository_from_settings", lambda *args: None)
    monkeypatch.setattr(
        daily_operations_job,
        "run_daily_operations",
        lambda **kwargs: captured.update(kwargs) or SimpleNamespace(
            id="daily-1",
            trigger="scheduled",
            input_mode="merchant_payload",
            completed_work_count=2,
            saved_minutes=20,
            saved_yuan=15,
            operator_message="done",
            next_run_hint="next",
        ),
    )

    result = daily_operations_job.run_daily_operations_job()

    assert result.status == "completed"
    assert result.input_mode == "merchant_payload"
    assert captured["pre_live"] == source.pre_live
    assert captured["post_live"] == source.post_live
    assert captured["live_metrics"] is None