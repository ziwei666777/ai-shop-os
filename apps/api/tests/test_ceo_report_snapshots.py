from pathlib import Path

import pytest

from apps.api.app.infrastructure.ceo_report_engine import get_ceo_daily_report
from apps.api.app.infrastructure.ceo_report_snapshot_store import (
    InMemoryCeoDailyReportSnapshotRepository,
    PostgresCeoDailyReportSnapshotRepository,
    clear_ceo_daily_report_snapshots_for_test,
    configure_ceo_daily_report_snapshot_repository,
    configure_ceo_daily_report_snapshot_repository_from_settings,
    list_ceo_daily_report_snapshots,
)
from apps.api.app.infrastructure.daily_operations_runner import run_daily_operations
from apps.api.app.infrastructure.live_workflow_log_store import (
    InMemoryLiveWorkflowRunRepository,
    clear_live_workflow_runs_for_test,
    configure_live_workflow_repository,
)


@pytest.fixture(autouse=True)
def isolate_snapshot_repository():
    configure_live_workflow_repository(InMemoryLiveWorkflowRunRepository())
    configure_ceo_daily_report_snapshot_repository(InMemoryCeoDailyReportSnapshotRepository())
    clear_live_workflow_runs_for_test()
    clear_ceo_daily_report_snapshots_for_test()
    yield
    configure_live_workflow_repository(InMemoryLiveWorkflowRunRepository())
    configure_ceo_daily_report_snapshot_repository(InMemoryCeoDailyReportSnapshotRepository())
    clear_live_workflow_runs_for_test()
    clear_ceo_daily_report_snapshots_for_test()


def test_daily_operations_persists_ceo_report_evidence_snapshot() -> None:
    run = run_daily_operations(trigger="scheduled")

    snapshots = list_ceo_daily_report_snapshots()

    assert len(snapshots) == 1
    assert snapshots[0].date == run.ceo_report.date
    assert snapshots[0].data_status == run.ceo_report.data_status
    assert snapshots[0].saved_money_today_yuan == run.ceo_report.saved_money_today_yuan
    assert any("Savings Engine" in proof for proof in snapshots[0].proof_points)


def test_ceo_report_snapshot_repository_can_switch_to_postgres_when_explicitly_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps.api.app.infrastructure import ceo_report_snapshot_store

    class FakeSettings:
        ceo_report_snapshot_storage = "postgres"
        has_database = True
        local_company_id = "00000000-0000-0000-0000-000000000001"

    monkeypatch.setattr(ceo_report_snapshot_store, "get_settings", lambda: FakeSettings())

    repository = configure_ceo_daily_report_snapshot_repository_from_settings(lambda: None)  # type: ignore[arg-type]

    assert isinstance(repository, PostgresCeoDailyReportSnapshotRepository)


def test_ceo_report_snapshot_migration_preserves_report_and_proof_evidence() -> None:
    migration = (
        Path(__file__).resolve().parents[3]
        / "supabase"
        / "migrations"
        / "202607180001_ceo_daily_report_snapshots.sql"
    )

    sql = migration.read_text(encoding="utf-8")

    for fragment in (
        "create table if not exists public.ceo_daily_report_snapshots",
        "report jsonb not null",
        "data_status text not null",
        "proof_points jsonb not null",
        "unique (company_id, snapshot_date)",
        "public.is_company_member(company_id)",
    ):
        assert fragment in sql
