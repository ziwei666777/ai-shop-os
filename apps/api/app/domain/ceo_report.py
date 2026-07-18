from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RiskLevel = Literal["high", "medium", "low"]
ActionOwner = Literal["boss", "ai-live-operator", "ai-operator", "ai-after-sale", "ai-customer"]
DataStatus = Literal["demo_estimate", "real_workflow_logs"]


@dataclass(frozen=True)
class CeoReportRisk:
    id: str
    level: RiskLevel
    title: str
    reason: str
    suggested_action: str
    money_impact: str


@dataclass(frozen=True)
class CeoReportAction:
    id: str
    owner: ActionOwner
    title: str
    expected_result: str
    requires_approval: bool


@dataclass(frozen=True)
class CeoReportMetric:
    id: str
    label: str
    value: str
    explanation: str


@dataclass(frozen=True)
class CeoDailyReport:
    date: str
    headline: str
    business_health_score: int
    boss_message: str
    saved_money_today_yuan: int
    projected_monthly_saving_yuan: int
    annual_roi_percent: int
    replacement_target_yuan: int
    live_operation_status: str
    data_status: DataStatus
    data_status_label: str
    data_status_reason: str
    metrics: tuple[CeoReportMetric, ...]
    top_risks: tuple[CeoReportRisk, ...]
    priority_actions: tuple[CeoReportAction, ...]
    ai_employee_notes: tuple[str, ...]
    proof_points: tuple[str, ...]