from __future__ import annotations

from datetime import datetime, timezone

from apps.api.app.domain.live_operations import (
    AgentSavingsWork,
    LiveOperationAlert,
    LiveOperationCheckItem,
    LiveOperationSummary,
    SavingsSummary,
)
from apps.api.app.infrastructure.after_sale_decision_workflow import summarize_after_sale_decision_outcomes
from apps.api.app.infrastructure.live_workflow_log_store import summarize_live_workflow_runs
from apps.api.app.infrastructure.refund_collaboration_workflow import summarize_refund_collaboration_runs


MONTHLY_LIVE_ASSISTANT_COST_YUAN = 12000
MONTHLY_AI_TEAM_REPLACEMENT_TARGET_YUAN = 70000
AI_MONTHLY_COST_YUAN = 2000
WORK_DAYS_PER_MONTH = 26
HOURLY_LABOR_COST_YUAN = 45
ZH_LIVE_ASSISTANT = "\u76f4\u64ad\u8fd0\u8425\u52a9\u7406"


def get_live_operation_summary() -> LiveOperationSummary:
    checklist = (
        LiveOperationCheckItem(
            id="pre-inventory",
            stage="pre_live",
            title="Pre-live inventory check",
            status="warning",
            owner_agent="AI Live Operation Agent",
            business_value="Avoid promoting products with unsafe stock and reduce refund risk.",
            saved_minutes=25,
            requires_approval=False,
        ),
        LiveOperationCheckItem(
            id="pre-coupon",
            stage="pre_live",
            title="Coupon and price check",
            status="done",
            owner_agent="AI Live Operation Agent",
            business_value="Detect expired coupons, price conflicts, and gift-rule conflicts before live starts.",
            saved_minutes=18,
            requires_approval=True,
        ),
        LiveOperationCheckItem(
            id="pre-script",
            stage="pre_live",
            title="Script and forbidden-words check",
            status="done",
            owner_agent="AI Live Operation Agent",
            business_value="Reduce live-room compliance risk and host mistakes.",
            saved_minutes=40,
            requires_approval=False,
        ),
        LiveOperationCheckItem(
            id="live-retention",
            stage="during_live",
            title="During-live retention warning",
            status="warning",
            owner_agent="AI Live Operation Agent",
            business_value="Prompt host to switch product, explain benefits, or interact when retention drops.",
            saved_minutes=30,
            requires_approval=False,
        ),
        LiveOperationCheckItem(
            id="post-review",
            stage="post_live",
            title="Post-live review report",
            status="pending",
            owner_agent="AI Boss",
            business_value="Turn sales, product, comment, and refund signals into tomorrow's actions.",
            saved_minutes=55,
            requires_approval=False,
        ),
    )
    alerts = (
        LiveOperationAlert(
            id="alert-stock",
            priority="high",
            title="Main product stock is below safe line",
            trigger="Main SKU stock is only enough for about 1.8 live sessions.",
            suggested_action="Move healthier-stock items higher before live starts.",
            expected_impact="Reduce refunds and traffic waste caused by stockout.",
        ),
        LiveOperationAlert(
            id="alert-retention",
            priority="medium",
            title="Retention may drop around minute 20",
            trigger="Similar sessions historically drop between minute 18 and 25.",
            suggested_action="Prepare a 30-second benefit pitch and comment interaction.",
            expected_impact="Increase watch time and conversion exposure.",
        ),
    )
    return LiveOperationSummary(
        date=_today(),
        replacement_role=ZH_LIVE_ASSISTANT,
        target_monthly_salary_yuan=MONTHLY_LIVE_ASSISTANT_COST_YUAN,
        session_title="Douyin apparel live session at 20:00",
        pre_live_ready_score=78,
        during_live_risk_score=64,
        post_live_review_status="Waiting for post-live automatic review",
        checklist=checklist,
        alerts=alerts,
        next_actions=(
            "Connect real live products, inventory, coupons, and room metrics.",
            "Put pre-live check results into CEO daily report so the boss does not read spreadsheets.",
            "Send during-live warnings to a host-assistant surface.",
        ),
    )


def get_savings_summary() -> SavingsSummary:
    live_savings = summarize_live_workflow_runs()
    refund_savings = summarize_refund_collaboration_runs()
    decision_savings = summarize_after_sale_decision_outcomes()
    live_completed_count = int(live_savings["completed_work_count"])
    live_saved_minutes = int(live_savings["saved_minutes"] or 168)
    live_saved_yuan = int(live_savings["saved_yuan"] or _minutes_to_yuan(168))
    live_performance_score = int(live_savings["performance_score"] or 82)
    live_proof = str(live_savings["proof"] or "Completed live inventory, coupon, script, retention, and review preparation work.")

    after_sale_base_minutes = 216
    customer_base_minutes = 336
    agents = (
        AgentSavingsWork(
            agent_id="ai-live-operator",
            agent_name="AI Live Operation Agent",
            replaced_role=ZH_LIVE_ASSISTANT,
            completed_work_count=live_completed_count or 5,
            saved_minutes=live_saved_minutes,
            saved_yuan=live_saved_yuan,
            performance_score=live_performance_score,
            proof=live_proof,
        ),
        AgentSavingsWork(
            agent_id="ai-after-sale",
            agent_name="AI AfterSale",
            replaced_role="\u552e\u540e\u4e13\u5458",
            completed_work_count=18 + int(refund_savings["completed_work_count"]) + int(decision_savings["completed_work_count"]),
            saved_minutes=after_sale_base_minutes + int(refund_savings["saved_minutes"]) + int(decision_savings["saved_minutes"]),
            saved_yuan=_minutes_to_yuan(after_sale_base_minutes) + int(refund_savings["saved_yuan"]) + int(decision_savings["saved_yuan"]),
            performance_score=88 if decision_savings["completed_work_count"] else (86 if refund_savings["completed_work_count"] else 84),
            proof=str(decision_savings["proof"] or refund_savings["proof"] or "Identify high-risk refund, complaint, and compensation cases and provide approval suggestions."),
        ),
        AgentSavingsWork(
            agent_id="ai-customer",
            agent_name="AI Customer",
            replaced_role="\u5ba2\u670d\u4e13\u5458",
            completed_work_count=96,
            saved_minutes=customer_base_minutes,
            saved_yuan=_minutes_to_yuan(customer_base_minutes),
            performance_score=88,
            proof="Handle low-risk order, logistics, and FAQ drafts while escalating high-risk cases.",
        ),
    )
    today_saved_minutes = sum(agent.saved_minutes for agent in agents)
    today_saved_yuan = sum(agent.saved_yuan for agent in agents)
    projected_monthly_saving = today_saved_yuan * WORK_DAYS_PER_MONTH
    annual_saving = projected_monthly_saving * 12
    annual_cost = AI_MONTHLY_COST_YUAN * 12
    roi = round((annual_saving - annual_cost) / annual_cost * 100) if annual_cost else 0
    return SavingsSummary(
        date=_today(),
        target_monthly_replacement_yuan=MONTHLY_AI_TEAM_REPLACEMENT_TARGET_YUAN,
        today_saved_minutes=today_saved_minutes,
        today_saved_yuan=today_saved_yuan,
        projected_monthly_saving_yuan=projected_monthly_saving,
        ai_monthly_cost_yuan=AI_MONTHLY_COST_YUAN,
        annual_saving_yuan=annual_saving,
        annual_roi_percent=roi,
        agents=agents,
        next_actions=(
            "Replace live-operation estimates with workflow logs after real live data is connected.",
            "Keep boss first screen focused on saved money, operational risk, and approvals.",
            "Only expand automation privileges after monthly savings are consistently above AI cost.",
        ),
    )


def _minutes_to_yuan(minutes: int) -> int:
    return round(minutes / 60 * HOURLY_LABOR_COST_YUAN)


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()
