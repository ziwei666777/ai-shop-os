from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from apps.api.app.domain.live_operations import LivePostReviewReport, LiveWorkflowReport, LiveWorkflowRun
from apps.api.app.domain.repositories import LiveWorkflowRunRepository
from apps.api.app.infrastructure.config import get_settings


SessionProvider = Callable[[], Session]


class InMemoryLiveWorkflowRunRepository(LiveWorkflowRunRepository):
    """直播 Workflow 日志的默认内存实现。

    这里故意不直接写数据库：数据库表结构需要先确认。先用仓储接口把业务边界立住，
    后续替换成 Supabase/PostgreSQL 实现时，不需要改直播 Workflow 和 Savings Engine。
    """

    def __init__(self) -> None:
        self._runs: list[LiveWorkflowRun] = []
        self._lock = RLock()

    def record_live_workflow_report(self, workflow_name: str, report: LiveWorkflowReport, input_snapshot: dict | None = None) -> LiveWorkflowRun:
        approval_required = any(check.requires_approval for check in report.checks)
        proof = f"{workflow_name} 完成 {len(report.checks)} 个检查项，产生 {len(report.alerts)} 个风险提醒。"
        return self._append_run(
            workflow_name=workflow_name,
            stage=report.stage,
            status=report.status,
            score=report.score,
            saved_minutes=report.saved_minutes,
            estimated_saving_yuan=report.estimated_saving_yuan,
            alert_count=len(report.alerts),
            approval_required=approval_required,
            proof=proof,
            input_snapshot=input_snapshot or {},
        )

    def record_post_live_review(self, workflow_name: str, report: LivePostReviewReport, input_snapshot: dict | None = None) -> LiveWorkflowRun:
        proof = f"{workflow_name} 完成成交、退款、评论和主播表现复盘，爆款商品：{report.top_product_title}。"
        return self._append_run(
            workflow_name=workflow_name,
            stage=report.stage,
            status=report.status,
            score=report.score,
            saved_minutes=report.saved_minutes,
            estimated_saving_yuan=report.estimated_saving_yuan,
            alert_count=1 if report.status != "done" else 0,
            approval_required=report.status != "done",
            proof=proof,
            input_snapshot=input_snapshot or {},
        )

    def list_runs(self, limit: int = 50) -> tuple[LiveWorkflowRun, ...]:
        with self._lock:
            return tuple(reversed(self._runs[-limit:]))

    def summarize(self) -> dict[str, int | float | str]:
        with self._lock:
            return _summarize_runs(tuple(self._runs))

    def clear_for_test(self) -> None:
        with self._lock:
            self._runs.clear()

    def _append_run(
        self,
        workflow_name: str,
        stage: str,
        status: str,
        score: int,
        saved_minutes: int,
        estimated_saving_yuan: int,
        alert_count: int,
        approval_required: bool,
        proof: str,
        input_snapshot: dict,
    ) -> LiveWorkflowRun:
        run = LiveWorkflowRun(
            id=f"live-run-{uuid4()}",
            workflow_name=workflow_name,
            stage=stage,  # type: ignore[arg-type]
            status=status,  # type: ignore[arg-type]
            score=score,
            saved_minutes=saved_minutes,
            estimated_saving_yuan=estimated_saving_yuan,
            alert_count=alert_count,
            approval_required=approval_required,
            proof=proof,
            input_snapshot=input_snapshot or {},
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._lock:
            self._runs.append(run)
        return run


class PostgresLiveWorkflowRunRepository(LiveWorkflowRunRepository):
    """直播 Workflow 日志的 PostgreSQL 实现。

    该实现只在显式配置后启用。它要求 Supabase 已存在 `live_workflow_runs` 表；
    当前代码不自动建表，避免绕过数据库设计确认流程。
    """

    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider
        self.company_id = get_settings().local_company_id

    def record_live_workflow_report(self, workflow_name: str, report: LiveWorkflowReport, input_snapshot: dict | None = None) -> LiveWorkflowRun:
        approval_required = any(check.requires_approval for check in report.checks)
        proof = f"{workflow_name} 完成 {len(report.checks)} 个检查项，产生 {len(report.alerts)} 个风险提醒。"
        return self._insert_run(
            workflow_name=workflow_name,
            stage=report.stage,
            status=report.status,
            score=report.score,
            saved_minutes=report.saved_minutes,
            estimated_saving_yuan=report.estimated_saving_yuan,
            alert_count=len(report.alerts),
            approval_required=approval_required,
            proof=proof,
            input_snapshot=input_snapshot or {},
            alerts=[alert.__dict__ for alert in report.alerts],
            recommended_actions=list(report.next_actions),
        )

    def record_post_live_review(self, workflow_name: str, report: LivePostReviewReport, input_snapshot: dict | None = None) -> LiveWorkflowRun:
        proof = f"{workflow_name} 完成成交、退款、评论和主播表现复盘，爆款商品：{report.top_product_title}。"
        return self._insert_run(
            workflow_name=workflow_name,
            stage=report.stage,
            status=report.status,
            score=report.score,
            saved_minutes=report.saved_minutes,
            estimated_saving_yuan=report.estimated_saving_yuan,
            alert_count=1 if report.status != "done" else 0,
            approval_required=report.status != "done",
            proof=proof,
            input_snapshot=input_snapshot or {},
            alerts=[{"title": report.refund_risk_note, "priority": "medium"}] if report.status != "done" else [],
            recommended_actions=list(report.next_day_actions),
        )

    def list_runs(self, limit: int = 50) -> tuple[LiveWorkflowRun, ...]:
        with self.session_provider() as session:
            rows = session.execute(
                text(
                    """
                    select
                      id::text,
                      workflow_name,
                      workflow_stage,
                      status,
                      risk_score,
                      saved_minutes,
                      saved_cost_yuan,
                      jsonb_array_length(alerts) as alert_count,
                      approval_required,
                      proof,
                      input_snapshot,
                      created_at::text
                    from live_workflow_runs
                    where company_id = :company_id
                    order by created_at desc
                    limit :limit
                    """
                ),
                {"company_id": self.company_id, "limit": limit},
            ).mappings().all()
            return tuple(_run_from_row(row) for row in rows)

    def summarize(self) -> dict[str, int | float | str]:
        runs = tuple(reversed(self.list_runs(limit=500)))
        return _summarize_runs(runs)

    def clear_for_test(self) -> None:
        with self.session_provider() as session:
            session.execute(text("delete from live_workflow_runs where company_id = :company_id"), {"company_id": self.company_id})
            session.commit()

    def _insert_run(
        self,
        workflow_name: str,
        stage: str,
        status: str,
        score: int,
        saved_minutes: int,
        estimated_saving_yuan: int,
        alert_count: int,
        approval_required: bool,
        proof: str,
        input_snapshot: dict,
        alerts: list[dict],
        recommended_actions: list[str],
    ) -> LiveWorkflowRun:
        run = LiveWorkflowRun(
            id=str(uuid4()),
            workflow_name=workflow_name,
            stage=stage,  # type: ignore[arg-type]
            status=status,  # type: ignore[arg-type]
            score=score,
            saved_minutes=saved_minutes,
            estimated_saving_yuan=estimated_saving_yuan,
            alert_count=alert_count,
            approval_required=approval_required,
            proof=proof,
            input_snapshot=input_snapshot or {},
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        with self.session_provider() as session:
            session.execute(
                text(
                    """
                    insert into live_workflow_runs (
                      id, company_id, workflow_name, workflow_stage, status,
                      input_snapshot, alerts, recommended_actions, approval_required, proof,
                      saved_minutes, saved_cost_yuan, risk_score,
                      started_at, finished_at, created_at, updated_at
                    ) values (
                      :id, :company_id, :workflow_name, :workflow_stage, :status,
                      cast(:input_snapshot as jsonb), cast(:alerts as jsonb), cast(:recommended_actions as jsonb), :approval_required, :proof,
                      :saved_minutes, :saved_cost_yuan, :risk_score,
                      now(), now(), now(), now()
                    )
                    """
                ),
                {
                    "id": run.id,
                    "company_id": self.company_id,
                    "workflow_name": run.workflow_name,
                    "workflow_stage": run.stage,
                    "status": run.status,
                    "input_snapshot": _json_dumps(input_snapshot),
                    "alerts": _json_dumps(alerts),
                    "recommended_actions": _json_dumps(recommended_actions),
                    "approval_required": run.approval_required,
                    "proof": run.proof,
                    "saved_minutes": run.saved_minutes,
                    "saved_cost_yuan": run.estimated_saving_yuan,
                    "risk_score": run.score,
                },
            )
            session.commit()
        return run


_repository: LiveWorkflowRunRepository = InMemoryLiveWorkflowRunRepository()


def configure_live_workflow_repository(repository: LiveWorkflowRunRepository) -> None:
    """替换直播日志仓储，供后续 PostgreSQL 实现和测试注入使用。"""
    global _repository
    _repository = repository


def configure_live_workflow_repository_from_settings(session_provider: SessionProvider | None = None) -> LiveWorkflowRunRepository:
    """根据配置选择直播日志仓储。

    默认永远使用内存仓储。只有显式设置 `LIVE_WORKFLOW_LOG_STORAGE=postgres` 且传入数据库会话工厂时，
    才切换到 PostgreSQL，避免在表结构未确认前误连生产库。
    """
    settings = get_settings()
    if settings.live_workflow_log_storage == "postgres" and session_provider is not None and settings.has_database:
        configure_live_workflow_repository(PostgresLiveWorkflowRunRepository(session_provider))
    else:
        configure_live_workflow_repository(InMemoryLiveWorkflowRunRepository())
    return _repository


def live_workflow_repository() -> LiveWorkflowRunRepository:
    return _repository


def record_live_workflow_report(workflow_name: str, report: LiveWorkflowReport, input_snapshot: dict | None = None) -> LiveWorkflowRun:
    return _repository.record_live_workflow_report(workflow_name, report, input_snapshot)


def record_post_live_review(workflow_name: str, report: LivePostReviewReport, input_snapshot: dict | None = None) -> LiveWorkflowRun:
    return _repository.record_post_live_review(workflow_name, report, input_snapshot)


def list_live_workflow_runs(limit: int = 50) -> tuple[LiveWorkflowRun, ...]:
    return _repository.list_runs(limit)


def summarize_live_workflow_runs() -> dict[str, int | float | str]:
    return _repository.summarize()


def clear_live_workflow_runs_for_test() -> None:
    _repository.clear_for_test()


def _summarize_runs(runs: tuple[LiveWorkflowRun, ...]) -> dict[str, int | float | str]:
    if not runs:
        return {
            "completed_work_count": 0,
            "saved_minutes": 0,
            "saved_yuan": 0,
            "performance_score": 0,
            "proof": "",
        }
    saved_minutes = sum(run.saved_minutes for run in runs)
    saved_yuan = sum(run.estimated_saving_yuan for run in runs)
    average_score = round(sum(run.score for run in runs) / len(runs))
    latest = runs[-1]
    return {
        "completed_work_count": len(runs),
        "saved_minutes": saved_minutes,
        "saved_yuan": saved_yuan,
        "performance_score": average_score,
        "proof": f"已记录 {len(runs)} 次直播 Workflow，最新：{latest.proof}",
    }


def _run_from_row(row) -> LiveWorkflowRun:
    return LiveWorkflowRun(
        id=str(row["id"]),
        workflow_name=str(row["workflow_name"]),
        stage=str(row["workflow_stage"]),  # type: ignore[arg-type]
        status=str(row["status"]),  # type: ignore[arg-type]
        score=int(row["risk_score"] or 0),
        saved_minutes=int(row["saved_minutes"] or 0),
        estimated_saving_yuan=int(row["saved_cost_yuan"] or 0),
        alert_count=int(row["alert_count"] or 0),
        approval_required=bool(row["approval_required"]),
        proof=str(row["proof"] or ""),
        input_snapshot=_json_value(row["input_snapshot"]),
        created_at=str(row["created_at"]),
    )



def _json_value(value: object) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {}
    return {}
def _json_dumps(value: object) -> str:
    return json.dumps(value, ensure_ascii=False)