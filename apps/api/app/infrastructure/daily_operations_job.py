from __future__ import annotations

import json

from sqlalchemy import text
from dataclasses import asdict, dataclass
from typing import Literal

from apps.api.app.domain.daily_operations import DailyOperationsRun
from apps.api.app.infrastructure.config import get_settings
from apps.api.app.infrastructure.ceo_report_snapshot_store import configure_ceo_daily_report_snapshot_repository_from_settings
from apps.api.app.infrastructure.daily_operations_runner import run_daily_operations
from apps.api.app.infrastructure.daily_operations_data_provider import load_daily_operations_source_data
from apps.api.app.infrastructure.database import SessionFactory
from apps.api.app.infrastructure.live_workflow_log_store import configure_live_workflow_repository_from_settings
from apps.api.app.infrastructure.live_metric_snapshots import configure_live_metric_snapshot_repository_from_settings
from apps.api.app.infrastructure.production_bootstrap import assess_evidence_chain_readiness, find_missing_evidence_tables


JobStatus = Literal["completed", "blocked"]


@dataclass(frozen=True)
class DailyOperationsJobResult:
    status: JobStatus
    trigger: str
    storage: str
    evidence_chain_ready: bool
    evidence_chain_blockers: tuple[str, ...]
    daily_run_id: str | None
    input_mode: str | None
    completed_work_count: int
    saved_minutes: int
    saved_yuan: int
    message: str
    next_actions: tuple[str, ...]


# 生产定时任务入口：让 AI 像员工一样每天自动上班，而不是等待老板点击按钮。
def run_daily_operations_job() -> DailyOperationsJobResult:
    settings = get_settings()
    storage = settings.live_workflow_log_storage

    if SessionFactory is not None:
        configure_live_metric_snapshot_repository_from_settings(lambda: SessionFactory())
    else:
        configure_live_metric_snapshot_repository_from_settings()

    if storage == "postgres":
        database_ready = False
        missing_evidence_tables: tuple[str, ...] = ()
        if SessionFactory is not None:
            try:
                with SessionFactory() as session:
                    session.execute(text("select 1")).scalar_one()
                    missing_evidence_tables = find_missing_evidence_tables(session)
                database_ready = True
            except Exception:
                database_ready = False
        evidence_ready, evidence_blockers = assess_evidence_chain_readiness(database_ready, missing_evidence_tables)
        if not evidence_ready:
            return DailyOperationsJobResult(
                status="blocked",
                trigger="scheduled",
                storage=storage,
                evidence_chain_ready=False,
                evidence_chain_blockers=evidence_blockers,
                daily_run_id=None,
                input_mode=None,
                completed_work_count=0,
                saved_minutes=0,
                saved_yuan=0,
                message="每日主动工作未执行：生产证据链尚未 ready，不能写入看似真实的 AI 工作结果。",
                next_actions=(
                    "先执行 Supabase migrations，确认 live_workflow_runs、approval_records、after_sale_decision_outcomes、warehouse_notifications、ceo_daily_report_snapshots 和 live_metric_snapshots 表存在。",
                    "配置 LIVE_WORKFLOW_LOG_STORAGE=postgres、APPROVAL_RECORD_STORAGE=postgres、AFTER_SALE_DECISION_STORAGE=postgres、CEO_REPORT_SNAPSHOT_STORAGE=postgres、LIVE_METRIC_SNAPSHOT_STORAGE=postgres。",
                    "配置 WAREHOUSE_NOTIFICATION_DELIVERY_MODE=http_api 以及真实 WMS/ERP URL 和 API key。",
                    *evidence_blockers,
                ),
            )

    if storage == "postgres":
        source_data = load_daily_operations_source_data(
            lambda: SessionFactory(),
            settings.merchant_bridge_company_id or settings.local_company_id,
        )
        if source_data.source_mode != "database":
            return DailyOperationsJobResult(
                status="blocked",
                trigger="scheduled",
                storage=storage,
                evidence_chain_ready=True,
                evidence_chain_blockers=(),
                daily_run_id=None,
                input_mode=None,
                completed_work_count=0,
                saved_minutes=0,
                saved_yuan=0,
                message="每日主动工作未执行：没有可核验的商家商品、订单或售后数据，不能写入安全基线结果。",
                next_actions=source_data.warnings + (
                    "先导入真实商品和订单数据，再运行 npm run api:daily-operations。",
                ),
            )
    else:
        source_data = None

    configure_live_workflow_repository_from_settings(lambda: SessionFactory()) if SessionFactory is not None else configure_live_workflow_repository_from_settings()
    configure_ceo_daily_report_snapshot_repository_from_settings(lambda: SessionFactory()) if SessionFactory is not None else configure_ceo_daily_report_snapshot_repository_from_settings()
    run = run_daily_operations(
        trigger="scheduled",
        pre_live=source_data.pre_live if source_data else None,
        live_metrics=source_data.live_metrics if source_data else None,
        post_live=source_data.post_live if source_data else None,
    )
    return _job_result_from_run(run, storage, evidence_chain_ready=(storage == "postgres"), evidence_chain_blockers=())


def _job_result_from_run(
    run: DailyOperationsRun,
    storage: str,
    evidence_chain_ready: bool,
    evidence_chain_blockers: tuple[str, ...],
) -> DailyOperationsJobResult:
    return DailyOperationsJobResult(
        status="completed",
        trigger=run.trigger,
        storage=storage,
        evidence_chain_ready=evidence_chain_ready,
        evidence_chain_blockers=evidence_chain_blockers,
        daily_run_id=run.id,
        input_mode=run.input_mode,
        completed_work_count=run.completed_work_count,
        saved_minutes=run.saved_minutes,
        saved_yuan=run.saved_yuan,
        message=run.operator_message,
        next_actions=(run.next_run_hint,),
    )


def main() -> int:
    result = run_daily_operations_job()
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    return 0 if result.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
