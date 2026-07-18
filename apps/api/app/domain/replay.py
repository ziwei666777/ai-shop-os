from dataclasses import dataclass
from typing import Literal


ReplayCaseType = Literal["customer_message", "after_sale_case", "operation_signal"]
ReplayDecision = Literal["auto_reply", "human_review", "approval_required", "operation_suggestion"]


@dataclass(frozen=True)
class ReplayCase:
    id: str
    case_type: ReplayCaseType
    title: str
    input_text: str
    human_result: str
    expected_decision: ReplayDecision
    expected_minutes: int


@dataclass(frozen=True)
class ReplayResult:
    id: str
    case_type: ReplayCaseType
    title: str
    input_text: str
    human_result: str
    ai_decision: ReplayDecision
    ai_result: str
    is_correct: bool
    requires_human: bool
    saved_minutes: int
    evaluation_note: str


@dataclass(frozen=True)
class ReplaySummary:
    total_cases: int
    correct_cases: int
    accuracy: float
    auto_rate: float
    manual_rate: float
    saved_minutes: int
    estimated_saving_yuan: int
    results: tuple[ReplayResult, ...]
