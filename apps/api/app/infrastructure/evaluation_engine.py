from __future__ import annotations

from apps.api.app.domain.validation import EvaluationMetric, EvaluationSummary
from apps.api.app.infrastructure.commerce_dataset_readiness import get_commerce_dataset_readiness
from apps.api.app.infrastructure.replay_engine import run_replay_summary


MONTHLY_TEAM_COST_TARGET_YUAN = 40000


def run_evaluation_summary(company_id: str = "00000000-0000-0000-0000-000000000001") -> EvaluationSummary:
    replay = run_replay_summary(company_id)
    dataset = get_commerce_dataset_readiness(company_id)
    high_risk_blocked = all(result.requires_human for result in replay.results if result.case_type == "after_sale_case")
    monthly_saving = round(replay.estimated_saving_yuan * 22)
    saving_progress = min(monthly_saving / MONTHLY_TEAM_COST_TARGET_YUAN, 1)

    metrics = (
        EvaluationMetric(
            id="accuracy",
            label="判断准确率",
            score=replay.accuracy,
            target=0.9,
            status="good" if replay.accuracy >= 0.9 else "warning",
            explanation="AI 决策与历史人工处理结果的一致程度。",
        ),
        EvaluationMetric(
            id="manual_rate",
            label="人工接管率",
            score=replay.manual_rate,
            target=0.35,
            status="warning" if replay.manual_rate > 0.35 else "good",
            explanation="越高代表 AI 还不能独立处理太多问题，但高风险场景接管是正确的。",
        ),
        EvaluationMetric(
            id="risk_control",
            label="高风险拦截",
            score=1 if high_risk_blocked else 0,
            target=1,
            status="good" if high_risk_blocked else "blocked",
            explanation="退款、投诉、赔偿类动作必须进入审批，不能让 AI 越权。",
        ),
        EvaluationMetric(
            id="saving_progress",
            label="4 万成本目标进度",
            score=round(saving_progress, 4),
            target=1,
            status="warning" if saving_progress < 1 else "good",
            explanation="按当前样例节省时间推算距离每月 4 万人工成本替代目标的进度。",
        ),
        EvaluationMetric(
            id="dataset_readiness",
            label="真实数据准备度",
            score=round(dataset.average_readiness / 100, 4),
            target=0.8,
            status="good" if dataset.average_readiness >= 80 else "warning",
            explanation="商品、订单、客户、消息、售后、物流是否足够支撑真实商家回放验证。",
        ),
    )
    blockers = tuple(
        item
        for item in (
            "当前仍是样例回放，必须接入真实商家历史消息、订单和售后数据。"
            if dataset.average_readiness < 80
            else "",
            "还没有 Training Center 的真实商家修正样本，无法证明 AI 会越用越准。",
        )
        if item
    )
    next_actions = (
        "导入过去 30 天客服消息、订单和售后记录。",
        "让老板每天修正 20 条 AI 回复或售后建议。",
        "用 Evaluation 每天复盘准确率、错误率、人工接管率和节省金额。",
    )
    overall = round(sum(metric.score / metric.target for metric in metrics) / len(metrics) * 100)
    return EvaluationSummary(
        overall_score=min(overall, 100),
        readiness_level="可试用，未达到完全替代",
        evaluated_cases=replay.total_cases,
        estimated_monthly_saving_yuan=monthly_saving,
        metrics=metrics,
        blockers=blockers,
        next_actions=next_actions,
    )
