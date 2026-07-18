from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.api.app.domain.ceo_report import CeoDailyReport
from apps.api.app.infrastructure.config import get_settings


SessionProvider = Callable[[], Session]


@dataclass(frozen=True)
class CeoDailyReportSnapshot:
    id: str
    date: str
    data_status: str
    saved_money_today_yuan: int
    projected_monthly_saving_yuan: int
    annual_roi_percent: int
    proof_points: tuple[str, ...]
    created_at: str


class InMemoryCeoDailyReportSnapshotRepository:
    def __init__(self) -> None:
        self._snapshots: list[CeoDailyReportSnapshot] = []
        self._lock = RLock()

    def record(self, report: CeoDailyReport) -> CeoDailyReportSnapshot:
        snapshot = _snapshot_from_report(report)
        with self._lock:
            self._snapshots = [item for item in self._snapshots if item.date != snapshot.date]
            self._snapshots.append(snapshot)
        return snapshot

    def list_snapshots(self, limit: int = 30) -> tuple[CeoDailyReportSnapshot, ...]:
        with self._lock:
            return tuple(reversed(self._snapshots[-limit:]))

    def clear_for_test(self) -> None:
        with self._lock:
            self._snapshots.clear()


class PostgresCeoDailyReportSnapshotRepository:
    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider
        self.company_id = get_settings().local_company_id

    def record(self, report: CeoDailyReport) -> CeoDailyReportSnapshot:
        snapshot = _snapshot_from_report(report)
        with self.session_provider() as session:
            session.execute(
                text(
                    """
                    insert into ceo_daily_report_snapshots (
                      id, company_id, snapshot_date, report, data_status,
                      saved_money_today_yuan, projected_monthly_saving_yuan,
                      annual_roi_percent, proof_points, created_at, updated_at
                    ) values (
                      :id, :company_id, :snapshot_date, cast(:report as jsonb), :data_status,
                      :saved_money_today_yuan, :projected_monthly_saving_yuan,
                      :annual_roi_percent, cast(:proof_points as jsonb), now(), now()
                    )
                    on conflict (company_id, snapshot_date) do update set
                      id = excluded.id,
                      report = excluded.report,
                      data_status = excluded.data_status,
                      saved_money_today_yuan = excluded.saved_money_today_yuan,
                      projected_monthly_saving_yuan = excluded.projected_monthly_saving_yuan,
                      annual_roi_percent = excluded.annual_roi_percent,
                      proof_points = excluded.proof_points,
                      updated_at = now()
                    """
                ),
                {
                    "id": snapshot.id,
                    "company_id": self.company_id,
                    "snapshot_date": snapshot.date,
                    "report": json.dumps(_report_payload(report), ensure_ascii=False),
                    "data_status": snapshot.data_status,
                    "saved_money_today_yuan": snapshot.saved_money_today_yuan,
                    "projected_monthly_saving_yuan": snapshot.projected_monthly_saving_yuan,
                    "annual_roi_percent": snapshot.annual_roi_percent,
                    "proof_points": json.dumps(snapshot.proof_points, ensure_ascii=False),
                },
            )
            session.commit()
        return snapshot

    def list_snapshots(self, limit: int = 30) -> tuple[CeoDailyReportSnapshot, ...]:
        with self.session_provider() as session:
            rows = session.execute(
                text(
                    """
                    select id::text, snapshot_date::text, data_status,
                           saved_money_today_yuan, projected_monthly_saving_yuan,
                           annual_roi_percent, proof_points, created_at::text
                    from ceo_daily_report_snapshots
                    where company_id = :company_id
                    order by snapshot_date desc
                    limit :limit
                    """
                ),
                {"company_id": self.company_id, "limit": limit},
            ).mappings().all()
            return tuple(_snapshot_from_row(row) for row in rows)

    def clear_for_test(self) -> None:
        with self.session_provider() as session:
            session.execute(
                text("delete from ceo_daily_report_snapshots where company_id = :company_id"),
                {"company_id": self.company_id},
            )
            session.commit()


_repository: InMemoryCeoDailyReportSnapshotRepository | PostgresCeoDailyReportSnapshotRepository = (
    InMemoryCeoDailyReportSnapshotRepository()
)


def configure_ceo_daily_report_snapshot_repository(
    repository: InMemoryCeoDailyReportSnapshotRepository | PostgresCeoDailyReportSnapshotRepository,
) -> None:
    global _repository
    _repository = repository


def configure_ceo_daily_report_snapshot_repository_from_settings(
    session_provider: SessionProvider | None = None,
) -> InMemoryCeoDailyReportSnapshotRepository | PostgresCeoDailyReportSnapshotRepository:
    settings = get_settings()
    if settings.ceo_report_snapshot_storage == "postgres" and session_provider is not None and settings.has_database:
        configure_ceo_daily_report_snapshot_repository(PostgresCeoDailyReportSnapshotRepository(session_provider))
    else:
        configure_ceo_daily_report_snapshot_repository(InMemoryCeoDailyReportSnapshotRepository())
    return _repository


def ceo_daily_report_snapshot_repository() -> InMemoryCeoDailyReportSnapshotRepository | PostgresCeoDailyReportSnapshotRepository:
    return _repository


def record_ceo_daily_report_snapshot(report: CeoDailyReport) -> CeoDailyReportSnapshot:
    return _repository.record(report)


def list_ceo_daily_report_snapshots(limit: int = 30) -> tuple[CeoDailyReportSnapshot, ...]:
    return _repository.list_snapshots(limit)


def clear_ceo_daily_report_snapshots_for_test() -> None:
    _repository.clear_for_test()


def _snapshot_from_report(report: CeoDailyReport) -> CeoDailyReportSnapshot:
    return CeoDailyReportSnapshot(
        id=f"ceo-report-snapshot-{uuid4()}",
        date=report.date,
        data_status=report.data_status,
        saved_money_today_yuan=report.saved_money_today_yuan,
        projected_monthly_saving_yuan=report.projected_monthly_saving_yuan,
        annual_roi_percent=report.annual_roi_percent,
        proof_points=report.proof_points,
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _report_payload(report: CeoDailyReport) -> dict[str, object]:
    return {
        "date": report.date,
        "headline": report.headline,
        "business_health_score": report.business_health_score,
        "boss_message": report.boss_message,
        "saved_money_today_yuan": report.saved_money_today_yuan,
        "projected_monthly_saving_yuan": report.projected_monthly_saving_yuan,
        "annual_roi_percent": report.annual_roi_percent,
        "replacement_target_yuan": report.replacement_target_yuan,
        "live_operation_status": report.live_operation_status,
        "data_status": report.data_status,
        "data_status_label": report.data_status_label,
        "data_status_reason": report.data_status_reason,
        "metrics": [metric.__dict__ for metric in report.metrics],
        "top_risks": [risk.__dict__ for risk in report.top_risks],
        "priority_actions": [action.__dict__ for action in report.priority_actions],
        "ai_employee_notes": list(report.ai_employee_notes),
        "proof_points": list(report.proof_points),
    }


def _snapshot_from_row(row) -> CeoDailyReportSnapshot:
    proof_points = row["proof_points"] or []
    if isinstance(proof_points, str):
        proof_points = json.loads(proof_points)
    return CeoDailyReportSnapshot(
        id=str(row["id"]),
        date=str(row["snapshot_date"]),
        data_status=str(row["data_status"]),
        saved_money_today_yuan=int(row["saved_money_today_yuan"] or 0),
        projected_monthly_saving_yuan=int(row["projected_monthly_saving_yuan"] or 0),
        annual_roi_percent=int(row["annual_roi_percent"] or 0),
        proof_points=tuple(str(item) for item in proof_points),
        created_at=str(row["created_at"]),
    )
