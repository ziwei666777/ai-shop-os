from __future__ import annotations

from datetime import datetime, timezone

from apps.api.app.domain.ceo_report import CeoDailyReport, CeoReportAction, CeoReportMetric, CeoReportRisk
from apps.api.app.domain.live_operations import LiveOperationAlert
from apps.api.app.infrastructure.after_sale_decision_workflow import summarize_after_sale_decision_outcomes
from apps.api.app.infrastructure.live_operation_engine import get_live_operation_summary, get_savings_summary
from apps.api.app.infrastructure.live_workflow_log_store import list_live_workflow_runs


def get_ceo_daily_report() -> CeoDailyReport:
    """生成老板每天第一眼要看的经营日报。

    这不是聊天总结，而是把 AI 已完成的工作、风险、审批动作和省钱证据压缩成老板可决策的信息。
    """
    savings = get_savings_summary()
    after_sale_decisions = summarize_after_sale_decision_outcomes()
    live = get_live_operation_summary()
    runs = list_live_workflow_runs(limit=20)
    traceable_runs = tuple(run for run in runs if _has_traceable_merchant_evidence(run.input_snapshot))
    traceable_workflow_count = len(traceable_runs)
    has_real_workflow_logs = bool(traceable_runs)
    data_status = "real_workflow_logs" if has_real_workflow_logs else "demo_estimate"
    data_status_label = "真实 Workflow 数据" if has_real_workflow_logs else "演示估算数据"
    data_status_reason = (
        f"已读取 {traceable_workflow_count} 次带可追溯商家来源的直播 Workflow 运行记录，节省金额来自实际执行日志。"
        if has_real_workflow_logs
        else "当前还没有带可追溯商家来源的直播 Workflow 运行记录，页面用于试用演示和接入前校准。"
    )
    high_risk_count = sum(1 for alert in live.alerts if alert.priority == "high")
    medium_risk_count = sum(1 for alert in live.alerts if alert.priority == "medium")
    business_health_score = _clamp_score(88 - high_risk_count * 12 - medium_risk_count * 6 + min(savings.today_saved_yuan // 100, 8))
    live_status = _live_status(live.pre_live_ready_score, live.during_live_risk_score, high_risk_count)
    headline = _headline(business_health_score, savings.today_saved_yuan, high_risk_count)
    top_risks = _after_sale_decision_risks(after_sale_decisions) + tuple(_risk_from_alert(alert) for alert in live.alerts[:3])
    if not top_risks:
        top_risks = (
            CeoReportRisk(
                id="risk-no-live-data",
                level="medium",
                title="直播数据还不完整",
                reason="当前日报仍有部分内容来自默认估算，真实直播日志越多，判断越准。",
                suggested_action="优先让商家上传最近 7 场直播的商品、优惠券、直播中数据和下播复盘模板。",
                money_impact="会影响节省金额和运营建议的可信度。",
            ),
        )
    priority_actions = _build_actions(live.next_actions, savings.next_actions, has_real_workflow_logs, after_sale_decisions)
    ai_notes = tuple(
        f"{agent.agent_name}：完成 {agent.completed_work_count} 项工作，节省 {agent.saved_minutes} 分钟，约 {agent.saved_yuan} 元，绩效 {agent.performance_score} 分。"
        for agent in savings.agents
    )
    proof_points = (
        f"Savings Engine 今日记录节省 {savings.today_saved_minutes} 分钟，约 {savings.today_saved_yuan} 元。",
        f"按当前节奏，预计月节省 {savings.projected_monthly_saving_yuan} 元，年度 ROI {savings.annual_roi_percent}%。",
        f"直播 Workflow 已记录 {len(runs)} 次运行，其中 {traceable_workflow_count} 次附带可追溯商家来源。",
        data_status_reason,
        *_after_sale_decision_proof_points(after_sale_decisions),
    )
    return CeoDailyReport(
        date=datetime.now(timezone.utc).date().isoformat(),
        headline=headline,
        business_health_score=business_health_score,
        boss_message=_boss_message(business_health_score, top_risks, priority_actions),
        saved_money_today_yuan=savings.today_saved_yuan,
        projected_monthly_saving_yuan=savings.projected_monthly_saving_yuan,
        annual_roi_percent=savings.annual_roi_percent,
        replacement_target_yuan=savings.target_monthly_replacement_yuan,
        live_operation_status=live_status,
        data_status=data_status,  # type: ignore[arg-type]
        data_status_label=data_status_label,
        data_status_reason=data_status_reason,
        metrics=(
            CeoReportMetric("saved_today", "今日节省", f"{savings.today_saved_yuan} 元", "AI 员工今天替代人工完成工作的估算金额。"),
            CeoReportMetric("monthly_projection", "预计月节省", f"{savings.projected_monthly_saving_yuan} 元", "按当前工作日节奏推算的月度节省。"),
            CeoReportMetric("roi", "年度 ROI", f"{savings.annual_roi_percent}%", "用年度节省减去 AI 成本后计算。"),
            CeoReportMetric("live_status", "直播状态", live_status, "来自直播准备分、直播中风险和风险提醒。"),
        ),
        top_risks=top_risks,
        priority_actions=priority_actions,
        ai_employee_notes=ai_notes,
        proof_points=proof_points,
    )


def _has_traceable_merchant_evidence(input_snapshot: dict) -> bool:
    evidence = input_snapshot.get("evidence_source")
    if not isinstance(evidence, dict):
        return False
    if evidence.get("source_type") == "postgres":
        return bool(evidence.get("tables"))
    return bool(evidence.get("snapshot_id") and evidence.get("source_reference"))


def _after_sale_decision_risks(after_sale_decisions: dict[str, int | str]) -> tuple[CeoReportRisk, ...]:
    failed_count = int(after_sale_decisions["warehouse_notification_failed_count"])
    if not failed_count:
        return ()
    return (
        CeoReportRisk(
            id="risk-warehouse-notification-failed",
            level="high",
            title="仓库通知发送失败",
            reason=f"有 {failed_count} 条补发/换货通知没有送达 WMS/ERP。",
            suggested_action="让 AI AfterSale 重试发送，或人工通知仓库并回填外部单号。",
            money_impact="补发/换货延迟会提高退款、投诉和二次售后风险。",
        ),
    )

def _after_sale_decision_proof_points(after_sale_decisions: dict[str, int | str]) -> tuple[str, ...]:
    completed = int(after_sale_decisions["completed_work_count"])
    if not completed:
        return ()
    cost_yuan = int(after_sale_decisions["after_sale_cost_yuan"])
    notification_count = int(after_sale_decisions["warehouse_notification_count"])
    queued_count = int(after_sale_decisions["warehouse_notification_queued_count"])
    sent_count = int(after_sale_decisions["warehouse_notification_sent_count"])
    failed_count = int(after_sale_decisions["warehouse_notification_failed_count"])
    latest_notification_id = str(after_sale_decisions["latest_warehouse_notification_id"] or "none")
    latest_status = str(after_sale_decisions["latest_warehouse_notification_status"] or "none")
    proof = str(after_sale_decisions["proof"])
    return (
        f"After-sale decisions recorded {completed} approval outcomes, after-sale cost {cost_yuan} yuan, warehouse notices {notification_count}, sent {sent_count}, queued {queued_count}, failed {failed_count}, latest notice {latest_notification_id} status {latest_status}.",
        f"After-sale evidence: {proof}",
    )

def _risk_from_alert(alert: LiveOperationAlert) -> CeoReportRisk:
    return CeoReportRisk(
        id=f"ceo-{alert.id}",
        level=alert.priority,
        title=alert.title,
        reason=alert.trigger,
        suggested_action=alert.suggested_action,
        money_impact=alert.expected_impact,
    )


def _build_actions(
    live_actions: tuple[str, ...],
    saving_actions: tuple[str, ...],
    has_workflow_runs: bool,
    after_sale_decisions: dict[str, int | str],
) -> tuple[CeoReportAction, ...]:
    actions: list[CeoReportAction] = []
    for index, action in enumerate(live_actions[:2], start=1):
        actions.append(
            CeoReportAction(
                id=f"live-action-{index}",
                owner="ai-live-operator",
                title=action,
                expected_result="减少直播运营助理人工检查时间，并降低直播间临场错误。",
                requires_approval=False,
            )
        )
    if not has_workflow_runs:
        actions.append(
            CeoReportAction(
                id="boss-action-upload-live-data",
                owner="boss",
                title="今天先上传至少一场真实直播数据，让日报从估算变成真实证据。",
                expected_result="让节省金额、风险提醒和复盘建议可以被 Replay 和 Evaluation 验证。",
                requires_approval=True,
            )
        )
    failed_count = int(after_sale_decisions["warehouse_notification_failed_count"])
    if failed_count:
        actions.append(
            CeoReportAction(
                id="after-sale-warehouse-failed",
                owner="boss",
                title=f"Review {failed_count} failed warehouse notification before customers follow up.",
                expected_result="Prevent replacement delays from becoming refunds, complaints, or repeat after-sale work.",
                requires_approval=True,
            )
        )
    notification_count = int(after_sale_decisions["warehouse_notification_count"])
    if notification_count:
        actions.append(
            CeoReportAction(
                id="after-sale-warehouse-notice",
                owner="ai-after-sale",
                title=f"Check {notification_count} warehouse replacement notice before the next live session.",
                expected_result="Make replacement or reshipment work traceable instead of stopping at an approval note.",
                requires_approval=False,
            )
        )
    for index, action in enumerate(saving_actions[:1], start=1):
        actions.append(
            CeoReportAction(
                id=f"saving-action-{index}",
                owner="ai-operator",
                title=action,
                expected_result="把省钱结果变成可持续复用的运营动作。",
                requires_approval=False,
            )
        )
    return tuple(actions[:4])


def _headline(score: int, saved_yuan: int, high_risk_count: int) -> str:
    if high_risk_count:
        return f"今天 AI 已节省约 {saved_yuan} 元，但直播存在高优先级风险，需要老板先看。"
    if score >= 85:
        return f"今天经营状态稳定，AI 已节省约 {saved_yuan} 元，可以继续扩大自动化。"
    return f"今天 AI 已节省约 {saved_yuan} 元，但仍有运营风险需要处理。"


def _boss_message(score: int, risks: tuple[CeoReportRisk, ...], actions: tuple[CeoReportAction, ...]) -> str:
    first_risk = risks[0].title if risks else "暂无重大风险"
    first_action = actions[0].title if actions else "继续收集真实直播数据"
    if score < 75:
        return f"先处理：{first_risk}。建议动作：{first_action}。"
    return f"今天先看一件事：{first_risk}。如果确认无误，就执行：{first_action}。"


def _live_status(pre_score: int, risk_score: int, high_risk_count: int) -> str:
    if high_risk_count or risk_score >= 70:
        return "需要老板关注"
    if pre_score >= 80:
        return "基本可开播"
    return "准备中"


def _clamp_score(value: int) -> int:
    return max(0, min(100, value))