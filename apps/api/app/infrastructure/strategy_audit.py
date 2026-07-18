from __future__ import annotations

from apps.api.app.domain.strategy import StrategyAudit, StrategyCapability, StrategyStatus
from apps.api.app.infrastructure.ceo_report_engine import get_ceo_daily_report
from apps.api.app.infrastructure.live_operation_engine import get_live_operation_summary, get_savings_summary
from apps.api.app.infrastructure.live_workflow_log_store import list_live_workflow_runs


ZH_POSITIONING = "AI Employee OS\uff08\u4f01\u4e1a AI \u6570\u5b57\u5458\u5de5\u64cd\u4f5c\u7cfb\u7edf\uff09"
ZH_FOCUS = "\u672a\u6765\u4e09\u4e2a\u6708\u53ea\u56f4\u7ed5\u76f4\u64ad\u8fd0\u8425\u52a9\u7406\u3001\u8001\u677f\u65e5\u62a5\u3001Savings Engine\u3001ROI Engine \u63a8\u8fdb\u3002"


def get_strategy_audit() -> StrategyAudit:
    """Audit whether the product is moving toward AI Employee OS instead of AI customer service SaaS."""

    live = get_live_operation_summary()
    savings = get_savings_summary()
    ceo_report = get_ceo_daily_report()
    runs = list_live_workflow_runs(limit=50)

    has_workflow_runs = bool(runs)
    has_real_data_status = ceo_report.data_status == "real_workflow_logs"
    has_daily_work = True

    capabilities = (
        _capability(
            id="live-operation-agent",
            priority="P0",
            name="AI Live Operation Agent",
            status="in_progress" if live.checklist else "gap",
            score=82 if live.checklist else 35,
            proof=f"Already has {len(live.checklist)} live operation checks covering pre-live, during-live, and post-live workflows.",
            gap="Database-backed product, order, and after-sale inputs are wired; direct Douyin/Taobao live metrics, coupons, and scripts still need platform integration.",
            next_action="Connect Douyin/Taobao live feeds and pass real inventory, coupons, live metrics, and post-live data into the scheduled job.",
            replaced_role="\u76f4\u64ad\u8fd0\u8425\u52a9\u7406",
            daily_saved_minutes=sum(item.saved_minutes for item in live.checklist),
        ),
        _capability(
            id="ceo-agent",
            priority="P0",
            name="CEO Agent",
            status="done" if ceo_report.proof_points else "gap",
            score=86 if ceo_report.proof_points else 40,
            proof=f"CEO report outputs {len(ceo_report.proof_points)} proof points and {len(ceo_report.priority_actions)} priority actions.",
            gap="Snapshot persistence is wired; automatic push and cross-day trend comparison still need production scheduling and history reads.",
            next_action="Add cross-day snapshot comparison and an approved CEO notification channel after production data is live.",
            replaced_role="\u8fd0\u8425\u8d1f\u8d23\u4eba\u6bcf\u65e5\u6c47\u62a5",
            daily_saved_minutes=25,
        ),
        _capability(
            id="savings-roi-engine",
            priority="P0",
            name="Savings Engine / ROI Engine",
            status="in_progress" if savings.today_saved_yuan > 0 else "gap",
            score=78 if savings.today_saved_yuan > 0 else 30,
            proof=f"Can calculate today's saving as {savings.today_saved_yuan} yuan and annual ROI as {savings.annual_roi_percent}%.",
            gap="Needs more real workflow logs to replace demo estimates with merchant-trustworthy evidence.",
            next_action="Every P0 workflow must write saved minutes, saved yuan, proof, and approval status.",
            replaced_role="\u8d22\u52a1/\u8fd0\u8425\u7ee9\u6548\u590d\u76d8",
            daily_saved_minutes=20,
        ),
        _capability(
            id="daily-autonomous-work",
            priority="P0",
            name="AI daily autonomous work",
            status="in_progress" if has_daily_work else "gap",
            score=74 if has_daily_work else 35,
            proof="/v1/daily-operations/run and production Cron config exist; Postgres mode now loads database-backed merchant inputs and blocks when source data is empty.",
            gap="Production still needs Cron deployment, DATABASE_URL, and direct Douyin/Taobao live data sources.",
            next_action="Deploy the scheduled job, then verify merchant_payload runs write to live_workflow_runs and CEO snapshots in PostgreSQL.",
            replaced_role="\u76f4\u64ad\u8fd0\u8425\u65e9\u665a\u5de1\u68c0",
            daily_saved_minutes=35,
        ),
        _capability(
            id="agent-collaboration",
            priority="P1",
            name="Agent collaboration workflow",
            status="in_progress",
            score=90,
            proof="Refund collaboration executes customer -> after-sale -> operation -> boss -> customer, can prefer real order/logistics/inventory evidence, creates approval records, boss decisions write after-sale outcomes plus warehouse notices, those outcomes have a PostgreSQL persistence boundary, and warehouse notices now support queued/sent/failed/cancelled delivery status flow plus a configurable WMS/ERP HTTP API sender boundary.",
            gap="Refund collaboration has decision writeback, warehouse notice generation, persistence boundary, export delivery status, and configurable WMS/ERP HTTP delivery; next gap is production credentials plus real merchant endpoint enablement.",
            next_action="Enable after_sale_decision_outcomes storage in production, configure WMS/ERP endpoint credentials, and monitor failed notices in CEO report.",
            replaced_role="\u5ba2\u670d\u4e3b\u7ba1/\u552e\u540e\u4e3b\u7ba1\u534f\u8c03",
            daily_saved_minutes=15,
        ),
        _capability(
            id="real-data-proof-chain",
            priority="P0",
            name="Real data proof chain",
            status="done" if has_real_data_status else ("in_progress" if has_workflow_runs else "gap"),
            score=88 if has_real_data_status else (66 if has_workflow_runs else 50),
            proof=f"Recorded {len(runs)} live workflow runs." if has_workflow_runs else "Production readiness now checks database, postgres storage modes, evidence tables, warehouse dispatch, and WMS/ERP credentials; scheduled daily work is blocked when this evidence chain is not ready, so it cannot write fake production work logs.",
            gap="Production readiness gate and scheduled-job guard exist, but Supabase migrations, postgres storage modes, warehouse dispatch, and WMS/ERP endpoint credentials still need to be enabled online.",
            next_action="Run the production readiness gate until evidence_chain_ready=true, then make Dashboard, CEO report, and Savings read persistent logs online.",
            replaced_role="\u8fd0\u8425\u6570\u636e\u590d\u76d8",
            daily_saved_minutes=25 if has_workflow_runs else 0,
        ),
    )

    overall_score = round(sum(item.score for item in capabilities) / len(capabilities))
    completed_count = sum(1 for item in capabilities if item.status == "done")
    gap_count = sum(1 for item in capabilities if item.status == "gap")
    daily_minutes = sum(item.daily_saved_minutes for item in capabilities if item.status != "gap")
    daily_yuan = _minutes_to_yuan(daily_minutes)

    return StrategyAudit(
        positioning=ZH_POSITIONING,
        focus=ZH_FOCUS,
        overall_score=overall_score,
        completed_count=completed_count,
        gap_count=gap_count,
        estimated_daily_saved_minutes=daily_minutes,
        estimated_daily_saved_yuan=daily_yuan,
        stop_doing=(
            "\u4e0d\u8981\u65b0\u589e AI \u5ba2\u670d\u9875\u9762",
            "\u4e0d\u8981\u65b0\u589e\u804a\u5929\u529f\u80fd",
            "\u4e0d\u8981\u65b0\u589e Prompt \u9875\u9762",
            "\u4e0d\u8981\u65b0\u589e\u666e\u901a\u77e5\u8bc6\u5e93\u9875\u9762",
            "\u4e0d\u8981\u4e3a\u4e86\u5c55\u793a\u65b0\u589e Dashboard \u9875\u9762",
        ),
        capabilities=capabilities,
        next_p0_actions=tuple(
            item.next_action for item in capabilities if item.priority == "P0" and item.status != "done"
        ),
    )


def _capability(
    id: str,
    priority: str,
    name: str,
    status: StrategyStatus,
    score: int,
    proof: str,
    gap: str,
    next_action: str,
    replaced_role: str,
    daily_saved_minutes: int,
) -> StrategyCapability:
    return StrategyCapability(
        id=id,
        priority=priority,  # type: ignore[arg-type]
        name=name,
        status=status,
        score=score,
        proof=proof,
        gap=gap,
        next_action=next_action,
        replaced_role=replaced_role,
        daily_saved_minutes=daily_saved_minutes,
    )


def _minutes_to_yuan(minutes: int) -> int:
    hourly_cost_yuan = 35
    return round(minutes / 60 * hourly_cost_yuan)
