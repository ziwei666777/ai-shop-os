from dataclasses import dataclass
from typing import Literal


EvaluationStatus = Literal["good", "warning", "blocked"]
TrainingSampleStatus = Literal["ready", "needs_review"]
SimulationRiskLevel = Literal["low", "medium", "high"]
SimulationDecision = Literal["auto_reply", "human_review", "approval_required", "operation_suggestion"]


@dataclass(frozen=True)
class EvaluationMetric:
    id: str
    label: str
    score: float
    target: float
    status: EvaluationStatus
    explanation: str


@dataclass(frozen=True)
class EvaluationSummary:
    overall_score: int
    readiness_level: str
    evaluated_cases: int
    estimated_monthly_saving_yuan: int
    metrics: tuple[EvaluationMetric, ...]
    blockers: tuple[str, ...]
    next_actions: tuple[str, ...]


@dataclass(frozen=True)
class TrainingSample:
    id: str
    source_type: Literal["message", "after_sale_case", "operation_signal"]
    agent_name: str
    action: Literal["accepted", "edited", "rejected", "manual_answered"]
    original_content: str
    final_content: str
    training_target: Literal["memory", "knowledge", "workflow"]
    status: TrainingSampleStatus
    created_at: str


@dataclass(frozen=True)
class TrainingAssetCandidate:
    id: str
    target: Literal["memory", "knowledge", "workflow"]
    title: str
    content: str
    source_sample_id: str
    status: Literal["candidate", "needs_review", "committed"]
    business_value: str


@dataclass(frozen=True)
class TrainingCenterSummary:
    total_samples: int
    usable_samples: int
    memory_candidates: int
    knowledge_candidates: int
    workflow_candidates: int
    estimated_quality_gain: float
    samples: tuple[TrainingSample, ...]
    asset_candidates: tuple[TrainingAssetCandidate, ...]
    next_actions: tuple[str, ...]


@dataclass(frozen=True)
class SimulationScenario:
    id: str
    customer_type: str
    scenario_type: Literal["faq", "bargain", "refund", "complaint", "logistics", "private_domain"]
    message: str
    ai_decision: SimulationDecision
    expected_behavior: str
    risk_level: SimulationRiskLevel
    estimated_minutes: int


@dataclass(frozen=True)
class SimulationSummary:
    total_scenarios: int
    auto_reply_count: int
    approval_required_count: int
    manual_review_count: int
    estimated_daily_capacity: int
    estimated_saved_minutes: int
    scenarios: tuple[SimulationScenario, ...]
    warnings: tuple[str, ...]
