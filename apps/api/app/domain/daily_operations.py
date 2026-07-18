from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from apps.api.app.domain.ceo_report import CeoDailyReport
from apps.api.app.domain.live_operations import LiveWorkflowRun, SavingsSummary


DailyOperationTrigger = Literal["manual", "scheduled", "webhook"]
DailyOperationInputMode = Literal["merchant_payload", "safe_baseline"]
DailyOperationStatus = Literal["completed", "needs_real_data"]


@dataclass(frozen=True)
class DailyOperationsRun:
    id: str
    date: str
    trigger: DailyOperationTrigger
    input_mode: DailyOperationInputMode
    status: DailyOperationStatus
    replacement_role: str
    operator_message: str
    completed_work_count: int
    saved_minutes: int
    saved_yuan: int
    workflow_runs: tuple[LiveWorkflowRun, ...]
    ceo_report: CeoDailyReport
    savings_summary: SavingsSummary
    next_run_hint: str
