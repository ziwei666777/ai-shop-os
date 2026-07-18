from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.api.app.infrastructure.config import get_settings


SessionProvider = Callable[[], Session]


@dataclass(frozen=True)
class LiveMetricSnapshot:
    id: str
    company_id: str
    platform: str
    stream_external_id: str
    observed_at: str
    online_users: int
    conversion_rate: float
    retention_rate: float
    comment_count: int
    like_count: int
    product_click_rate: float
    inventory_delta: int
    abnormal_order_count: int
    source_reference: str

    def to_workflow_payload(self) -> dict[str, int | float]:
        return {
            "online_users": self.online_users,
            "conversion_rate": self.conversion_rate,
            "retention_rate": self.retention_rate,
            "comment_count": self.comment_count,
            "like_count": self.like_count,
            "product_click_rate": self.product_click_rate,
            "inventory_delta": self.inventory_delta,
            "abnormal_order_count": self.abnormal_order_count,
        }


class InMemoryLiveMetricSnapshotRepository:
    def __init__(self) -> None:
        self._snapshots: list[LiveMetricSnapshot] = []
        self._lock = RLock()

    def record(self, company_id: str, payload: dict[str, object]) -> LiveMetricSnapshot:
        snapshot = _snapshot_from_payload(company_id, payload)
        with self._lock:
            self._snapshots.append(snapshot)
        return snapshot

    def latest(self, company_id: str) -> LiveMetricSnapshot | None:
        with self._lock:
            candidates = [item for item in self._snapshots if item.company_id == company_id]
            return max(candidates, key=lambda item: item.observed_at) if candidates else None

    def clear_for_test(self) -> None:
        with self._lock:
            self._snapshots.clear()


class PostgresLiveMetricSnapshotRepository:
    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider

    def record(self, company_id: str, payload: dict[str, object]) -> LiveMetricSnapshot:
        snapshot = _snapshot_from_payload(company_id, payload)
        with self.session_provider() as session:
            session.execute(
                text(
                    """
                    insert into live_metric_snapshots (
                      id, company_id, platform, stream_external_id, observed_at,
                      online_users, conversion_rate, retention_rate, comment_count,
                      like_count, product_click_rate, inventory_delta, abnormal_order_count,
                      source_reference, source_payload, created_at
                    ) values (
                      :id, :company_id, :platform, :stream_external_id, :observed_at,
                      :online_users, :conversion_rate, :retention_rate, :comment_count,
                      :like_count, :product_click_rate, :inventory_delta, :abnormal_order_count,
                      :source_reference, cast(:source_payload as jsonb), now()
                    )
                    on conflict (company_id, platform, stream_external_id, observed_at) do update set
                      online_users = excluded.online_users,
                      conversion_rate = excluded.conversion_rate,
                      retention_rate = excluded.retention_rate,
                      comment_count = excluded.comment_count,
                      like_count = excluded.like_count,
                      product_click_rate = excluded.product_click_rate,
                      inventory_delta = excluded.inventory_delta,
                      abnormal_order_count = excluded.abnormal_order_count,
                      source_reference = excluded.source_reference,
                      source_payload = excluded.source_payload
                    """
                ),
                {
                    **snapshot.__dict__,
                    "source_payload": json.dumps(payload, ensure_ascii=False, default=str),
                },
            )
            session.commit()
        return snapshot

    def latest(self, company_id: str) -> LiveMetricSnapshot | None:
        with self.session_provider() as session:
            row = session.execute(
                text(
                    """
                    select id::text, company_id::text, platform, stream_external_id, observed_at::text,
                           online_users, conversion_rate, retention_rate, comment_count,
                           like_count, product_click_rate, inventory_delta, abnormal_order_count,
                           source_reference
                    from live_metric_snapshots
                    where company_id = :company_id
                    order by observed_at desc
                    limit 1
                    """
                ),
                {"company_id": company_id},
            ).mappings().one_or_none()
            return _snapshot_from_row(row) if row else None

    def clear_for_test(self) -> None:
        with self.session_provider() as session:
            session.execute(text("delete from live_metric_snapshots"))
            session.commit()


_repository: InMemoryLiveMetricSnapshotRepository | PostgresLiveMetricSnapshotRepository = InMemoryLiveMetricSnapshotRepository()


def configure_live_metric_snapshot_repository(
    repository: InMemoryLiveMetricSnapshotRepository | PostgresLiveMetricSnapshotRepository,
) -> None:
    global _repository
    _repository = repository


def configure_live_metric_snapshot_repository_from_settings(
    session_provider: SessionProvider | None = None,
) -> InMemoryLiveMetricSnapshotRepository | PostgresLiveMetricSnapshotRepository:
    settings = get_settings()
    if settings.live_metric_snapshot_storage == "postgres" and settings.has_database and session_provider is not None:
        configure_live_metric_snapshot_repository(PostgresLiveMetricSnapshotRepository(session_provider))
    else:
        configure_live_metric_snapshot_repository(InMemoryLiveMetricSnapshotRepository())
    return _repository


def record_live_metric_snapshot(company_id: str, payload: dict[str, object]) -> LiveMetricSnapshot:
    return _repository.record(company_id, payload)


def latest_live_metric_payload(company_id: str) -> dict[str, int | float] | None:
    snapshot = _repository.latest(company_id)
    return snapshot.to_workflow_payload() if snapshot else None


def clear_live_metric_snapshots_for_test() -> None:
    _repository.clear_for_test()


def _snapshot_from_payload(company_id: str, payload: dict[str, object]) -> LiveMetricSnapshot:
    observed_at = payload.get("observed_at")
    observed_at_text = observed_at.isoformat() if isinstance(observed_at, datetime) else str(observed_at or datetime.now(timezone.utc).isoformat())
    return LiveMetricSnapshot(
        id=f"live-metric-{uuid4()}",
        company_id=company_id,
        platform=str(payload["platform"]),
        stream_external_id=str(payload["stream_external_id"]),
        observed_at=observed_at_text,
        online_users=int(payload["online_users"]),
        conversion_rate=float(payload["conversion_rate"]),
        retention_rate=float(payload["retention_rate"]),
        comment_count=int(payload["comment_count"]),
        like_count=int(payload["like_count"]),
        product_click_rate=float(payload["product_click_rate"]),
        inventory_delta=int(payload["inventory_delta"]),
        abnormal_order_count=int(payload["abnormal_order_count"]),
        source_reference=str(payload.get("source_reference") or ""),
    )


def _snapshot_from_row(row) -> LiveMetricSnapshot:
    return LiveMetricSnapshot(
        id=str(row["id"]),
        company_id=str(row["company_id"]),
        platform=str(row["platform"]),
        stream_external_id=str(row["stream_external_id"]),
        observed_at=str(row["observed_at"]),
        online_users=int(row["online_users"]),
        conversion_rate=float(row["conversion_rate"]),
        retention_rate=float(row["retention_rate"]),
        comment_count=int(row["comment_count"]),
        like_count=int(row["like_count"]),
        product_click_rate=float(row["product_click_rate"]),
        inventory_delta=int(row["inventory_delta"]),
        abnormal_order_count=int(row["abnormal_order_count"]),
        source_reference=str(row["source_reference"] or ""),
    )
