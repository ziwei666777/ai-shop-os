from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


LiveStage = Literal["pre_live", "during_live", "post_live"]
WorkStatus = Literal["done", "warning", "blocked", "pending"]
Priority = Literal["high", "medium", "low"]


@dataclass(frozen=True)
class LiveOperationCheckItem:
    id: str
    stage: LiveStage
    title: str
    status: WorkStatus
    owner_agent: str
    business_value: str
    saved_minutes: int
    requires_approval: bool


@dataclass(frozen=True)
class LiveOperationAlert:
    id: str
    priority: Priority
    title: str
    trigger: str
    suggested_action: str
    expected_impact: str


@dataclass(frozen=True)
class LiveOperationSummary:
    date: str
    replacement_role: str
    target_monthly_salary_yuan: int
    session_title: str
    pre_live_ready_score: int
    during_live_risk_score: int
    post_live_review_status: str
    checklist: tuple[LiveOperationCheckItem, ...]
    alerts: tuple[LiveOperationAlert, ...]
    next_actions: tuple[str, ...]


@dataclass(frozen=True)
class AgentSavingsWork:
    agent_id: str
    agent_name: str
    replaced_role: str
    completed_work_count: int
    saved_minutes: int
    saved_yuan: int
    performance_score: int
    proof: str
    input_snapshot: dict


@dataclass(frozen=True)
class SavingsSummary:
    date: str
    target_monthly_replacement_yuan: int
    today_saved_minutes: int
    today_saved_yuan: int
    projected_monthly_saving_yuan: int
    ai_monthly_cost_yuan: int
    annual_saving_yuan: int
    annual_roi_percent: int
    agents: tuple[AgentSavingsWork, ...]
    next_actions: tuple[str, ...]


@dataclass(frozen=True)
class LiveWorkflowReport:
    stage: LiveStage
    status: WorkStatus
    score: int
    saved_minutes: int
    estimated_saving_yuan: int
    checks: tuple[LiveOperationCheckItem, ...]
    alerts: tuple[LiveOperationAlert, ...]
    next_actions: tuple[str, ...]


@dataclass(frozen=True)
class LivePostReviewReport:
    stage: LiveStage
    status: WorkStatus
    score: int
    saved_minutes: int
    estimated_saving_yuan: int
    sales_amount_yuan: float
    conversion_rate: float
    top_product_title: str
    refund_risk_note: str
    host_performance_note: str
    next_day_actions: tuple[str, ...]


@dataclass(frozen=True)
class LiveWorkflowRun:
    id: str
    workflow_name: str
    stage: LiveStage
    status: WorkStatus
    score: int
    saved_minutes: int
    estimated_saving_yuan: int
    alert_count: int
    approval_required: bool
    proof: str
    input_snapshot: dict
    created_at: str
