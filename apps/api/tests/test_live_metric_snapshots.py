from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from apps.api.app.infrastructure.live_metric_snapshots import (
    InMemoryLiveMetricSnapshotRepository,
    clear_live_metric_snapshots_for_test,
    configure_live_metric_snapshot_repository,
    latest_live_metric_payload,
    record_live_metric_snapshot,
)
from apps.api.app.main import app


@pytest.fixture(autouse=True)
def isolate_live_metric_repository():
    configure_live_metric_snapshot_repository(InMemoryLiveMetricSnapshotRepository())
    clear_live_metric_snapshots_for_test()
    yield
    configure_live_metric_snapshot_repository(InMemoryLiveMetricSnapshotRepository())
    clear_live_metric_snapshots_for_test()


def _payload(observed_at: datetime) -> dict[str, object]:
    return {
        "platform": "douyin",
        "stream_external_id": "douyin-live-1001",
        "observed_at": observed_at.isoformat(),
        "online_users": 800,
        "conversion_rate": 0.12,
        "retention_rate": 0.38,
        "comment_count": 93,
        "like_count": 1800,
        "product_click_rate": 0.16,
        "inventory_delta": -32,
        "abnormal_order_count": 2,
        "source_reference": "douyin-open-platform:room-1001",
    }


def test_metric_snapshot_bridge_endpoint_records_latest_live_metrics() -> None:
    client = TestClient(app)
    observed_at = datetime(2026, 7, 18, 8, 0, tzinfo=timezone.utc)

    response = client.post("/v1/live-operations/metric-snapshots", json=_payload(observed_at))

    assert response.status_code == 201
    body = response.json()
    assert body["platform"] == "douyin"
    assert body["online_users"] == 800
    assert body["source_reference"] == "douyin-open-platform:room-1001"
    assert latest_live_metric_payload("00000000-0000-0000-0000-000000000001") == {
        "online_users": 800,
        "conversion_rate": 0.12,
        "retention_rate": 0.38,
        "comment_count": 93,
        "like_count": 1800,
        "product_click_rate": 0.16,
        "inventory_delta": -32,
        "abnormal_order_count": 2,
    }


def test_metric_snapshot_keeps_newest_observation_per_company() -> None:
    company_id = "company-live-metrics"
    older = _payload(datetime(2026, 7, 18, 8, 0, tzinfo=timezone.utc))
    newer = _payload(datetime(2026, 7, 18, 8, 5, tzinfo=timezone.utc))
    newer["online_users"] = 1200

    record_live_metric_snapshot(company_id, newer)
    record_live_metric_snapshot(company_id, older)

    latest = latest_live_metric_payload(company_id)

    assert latest is not None
    assert latest["online_users"] == 1200


def test_metric_snapshot_bridge_key_rejects_invalid_key(monkeypatch) -> None:
    from apps.api.app.infrastructure.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "merchant_bridge_api_key", "bridge-secret")
    client = TestClient(app)

    rejected = client.post(
        "/v1/live-operations/metric-snapshots",
        json=_payload(datetime(2026, 7, 18, 8, 0, tzinfo=timezone.utc)),
        headers={"X-AICOS-Bridge-Key": "wrong"},
    )
    accepted = client.post(
        "/v1/live-operations/metric-snapshots",
        json=_payload(datetime(2026, 7, 18, 8, 0, tzinfo=timezone.utc)),
        headers={"X-AICOS-Bridge-Key": "bridge-secret"},
    )

    assert rejected.status_code == 401
    assert accepted.status_code == 201


def test_live_metric_snapshot_migration_keeps_workflow_metric_evidence() -> None:
    migration = (
        Path(__file__).resolve().parents[3]
        / "supabase"
        / "migrations"
        / "202607180002_live_metric_snapshots.sql"
    )
    sql = migration.read_text(encoding="utf-8")

    for fragment in (
        "create table if not exists public.live_metric_snapshots",
        "stream_external_id text not null",
        "observed_at timestamptz not null",
        "conversion_rate numeric",
        "source_payload jsonb not null",
        "public.is_company_member(company_id)",
    ):
        assert fragment in sql