from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DashboardMetricResponse(BaseModel):
    id: str
    label: str
    value: str
    trend: str


class DashboardSuggestionResponse(BaseModel):
    id: str
    title: str
    reason: str
    priority: Literal["high", "medium", "low"]


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: str
    status: str
    description: str
    prompt: str
    today_handled_count: int
    kpi_score: int
    future_tasks: tuple[str, ...]


class AgentLogResponse(BaseModel):
    id: str
    agent_id: str
    level: str
    message: str
    created_at: str


class DashboardSummaryResponse(BaseModel):
    date: str
    metrics: tuple[DashboardMetricResponse, ...]
    agents: tuple[AgentResponse, ...]
    suggestions: tuple[DashboardSuggestionResponse, ...]
    pending_approval_count: int


class ApprovalResponse(BaseModel):
    id: str
    title: str
    risk_level: str
    status: str



class ApprovalDecisionRequest(BaseModel):
    decision: Literal["approved", "rejected"]
    action: Literal["refund", "replacement", "compensation", "reject"] = "refund"
    note: str = Field(min_length=1, max_length=1000)


class ApprovalDecisionResponse(BaseModel):
    id: str
    approval_id: str
    approval_status: Literal["approved", "rejected"]
    action: Literal["refund", "replacement", "compensation", "reject"]
    source_workflow_id: str
    after_sale_cost_yuan: int
    saved_minutes: int
    saved_yuan: int
    warehouse_notification_id: str | None
    customer_reply: str
    proof: str
    created_at: str


class WarehouseNotificationDispatchItemResponse(BaseModel):
    id: str
    status: Literal["queued", "sent", "failed", "cancelled"]
    external_reference: str | None
    proof: str


class WarehouseNotificationDispatchResponse(BaseModel):
    total_count: int
    sent_count: int
    failed_count: int
    cancelled_count: int
    items: tuple[WarehouseNotificationDispatchItemResponse, ...]

class WorkflowResponse(BaseModel):
    id: str
    name: str
    status: str


class KnowledgeSourceResponse(BaseModel):
    id: str
    title: str
    source_type: str
    status: str


class CustomerInboxItemResponse(BaseModel):
    id: str
    platform: str
    customer_name: str
    channel: str
    content: str
    intent: str
    order_external_id: str | None
    logistics_status: str | None
    confidence: float
    automation_decision: str
    status: str
    created_at: str


class CustomerMessageIngestRequest(BaseModel):
    platform: Literal["taobao", "douyin", "xianyu", "shopify"]
    platform_message_id: str = Field(min_length=1, max_length=200)
    customer_name: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=5000)
    channel: str = Field(default="external_bridge", max_length=100)
    customer_external_id: str | None = Field(default=None, max_length=200)
    order_external_id: str | None = Field(default=None, max_length=200)


class DraftReplyResponse(BaseModel):
    message_id: str
    content: str
    confidence: float
    automation_decision: str
    reason: str
    required_human_review: bool
    knowledge_hit: str | None = None
    memory_hit: str | None = None
    saved_minutes: int = 0
    estimated_saving_yuan: int = 0


class CustomerReplySendRequest(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class AfterSaleCaseResponse(BaseModel):
    id: str
    platform: str
    case_type: str
    status: str
    customer_name: str
    order_external_id: str
    title: str
    description: str
    risk_level: str
    ai_suggestion: str
    approval_required: bool
    created_at: str


class AfterSaleDecisionRequest(BaseModel):
    decision: Literal["approved", "rejected", "needs_more_info"]
    note: str


class LearningEventRequest(BaseModel):
    source_type: Literal["message", "after_sale_case"]
    source_id: str
    agent_id: str
    action: Literal["accepted", "edited", "rejected", "manual_answered"]
    original_content: str
    final_content: str


class LearningEventResponse(BaseModel):
    id: str
    source_type: str
    source_id: str
    agent_id: str
    action: str
    original_content: str
    final_content: str
    created_at: str


class AgentFeedbackMetricResponse(BaseModel):
    id: str
    agent_id: str
    metric_name: str
    metric_value: float
    weight: float


class ConnectorStatusResponse(BaseModel):
    platform: str
    status: str
    display_name: str
    scopes: tuple[str, ...]
    next_action: str


class OAuthStartRequest(BaseModel):
    shop: str


class OAuthStartResponse(BaseModel):
    platform: str
    authorization_url: str
    state: str


class WebhookIngestResponse(BaseModel):
    accepted: bool
    platform: str
    reason: str


class AgentRoutingRequest(BaseModel):
    source_id: str = Field(min_length=1, max_length=200)
    event_type: Literal["customer_message", "after_sale_case", "operation_scan", "daily_business_review"]
    intent: str = Field(min_length=1, max_length=100)
    confidence: float = Field(ge=0, le=1)


class AgentRoutingResponse(BaseModel):
    source_id: str
    assigned_agent: Literal["ai-customer", "ai-after-sale", "ai-operator", "ai-boss"]
    requires_approval: bool
    reason: str
    trace: tuple[str, ...]


class ReplayResultResponse(BaseModel):
    id: str
    case_type: Literal["customer_message", "after_sale_case", "operation_signal"]
    title: str
    input_text: str
    human_result: str
    ai_decision: Literal["auto_reply", "human_review", "approval_required", "operation_suggestion"]
    ai_result: str
    is_correct: bool
    requires_human: bool
    saved_minutes: int
    evaluation_note: str


class ReplaySummaryResponse(BaseModel):
    total_cases: int
    correct_cases: int
    accuracy: float
    auto_rate: float
    manual_rate: float
    saved_minutes: int
    estimated_saving_yuan: int
    results: tuple[ReplayResultResponse, ...]


class EvaluationMetricResponse(BaseModel):
    id: str
    label: str
    score: float
    target: float
    status: Literal["good", "warning", "blocked"]
    explanation: str


class EvaluationSummaryResponse(BaseModel):
    overall_score: int
    readiness_level: str
    evaluated_cases: int
    estimated_monthly_saving_yuan: int
    metrics: tuple[EvaluationMetricResponse, ...]
    blockers: tuple[str, ...]
    next_actions: tuple[str, ...]


class TrainingSampleResponse(BaseModel):
    id: str
    source_type: Literal["message", "after_sale_case", "operation_signal"]
    agent_name: str
    action: Literal["accepted", "edited", "rejected", "manual_answered"]
    original_content: str
    final_content: str
    training_target: Literal["memory", "knowledge", "workflow"]
    status: Literal["ready", "needs_review"]
    created_at: str


class TrainingAssetCandidateResponse(BaseModel):
    id: str
    target: Literal["memory", "knowledge", "workflow"]
    title: str
    content: str
    source_sample_id: str
    status: Literal["candidate", "needs_review", "committed"]
    business_value: str


class TrainingCenterSummaryResponse(BaseModel):
    total_samples: int
    usable_samples: int
    memory_candidates: int
    knowledge_candidates: int
    workflow_candidates: int
    estimated_quality_gain: float
    samples: tuple[TrainingSampleResponse, ...]
    asset_candidates: tuple[TrainingAssetCandidateResponse, ...]
    next_actions: tuple[str, ...]


class SimulationScenarioResponse(BaseModel):
    id: str
    customer_type: str
    scenario_type: Literal["faq", "bargain", "refund", "complaint", "logistics", "private_domain"]
    message: str
    ai_decision: Literal["auto_reply", "human_review", "approval_required", "operation_suggestion"]
    expected_behavior: str
    risk_level: Literal["low", "medium", "high"]
    estimated_minutes: int


class SimulationSummaryResponse(BaseModel):
    total_scenarios: int
    auto_reply_count: int
    approval_required_count: int
    manual_review_count: int
    estimated_daily_capacity: int
    estimated_saved_minutes: int
    scenarios: tuple[SimulationScenarioResponse, ...]
    warnings: tuple[str, ...]


class LiveOperationCheckItemResponse(BaseModel):
    id: str
    stage: Literal["pre_live", "during_live", "post_live"]
    title: str
    status: Literal["done", "warning", "blocked", "pending"]
    owner_agent: str
    business_value: str
    saved_minutes: int
    requires_approval: bool


class LiveOperationAlertResponse(BaseModel):
    id: str
    priority: Literal["high", "medium", "low"]
    title: str
    trigger: str
    suggested_action: str
    expected_impact: str


class LiveOperationSummaryResponse(BaseModel):
    date: str
    replacement_role: str
    target_monthly_salary_yuan: int
    session_title: str
    pre_live_ready_score: int
    during_live_risk_score: int
    post_live_review_status: str
    checklist: tuple[LiveOperationCheckItemResponse, ...]
    alerts: tuple[LiveOperationAlertResponse, ...]
    next_actions: tuple[str, ...]


class AgentSavingsWorkResponse(BaseModel):
    agent_id: str
    agent_name: str
    replaced_role: str
    completed_work_count: int
    saved_minutes: int
    saved_yuan: int
    performance_score: int
    proof: str


class SavingsSummaryResponse(BaseModel):
    date: str
    target_monthly_replacement_yuan: int
    today_saved_minutes: int
    today_saved_yuan: int
    projected_monthly_saving_yuan: int
    ai_monthly_cost_yuan: int
    annual_saving_yuan: int
    annual_roi_percent: int
    agents: tuple[AgentSavingsWorkResponse, ...]
    next_actions: tuple[str, ...]


class LiveProductInput(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    inventory_count: int = Field(ge=0)
    safe_stock: int = Field(default=20, ge=0)
    regular_price: float = Field(default=0, ge=0)
    live_price: float = Field(default=0, ge=0)


class LiveCouponInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    remaining_count: int = Field(ge=0)
    expired: bool = False


class PreLiveCheckRequest(BaseModel):
    products: tuple[LiveProductInput, ...] = Field(min_length=1, max_length=200)
    coupons: tuple[LiveCouponInput, ...] = Field(default=(), max_length=100)
    script_text: str = Field(default="", max_length=20000)
    gift_ready: bool = False
    product_order_ready: bool = False


class LiveMetricScanRequest(BaseModel):
    online_users: int = Field(ge=0)
    conversion_rate: float = Field(ge=0, le=1)
    retention_rate: float = Field(ge=0, le=1)
    comment_count: int = Field(ge=0)
    like_count: int = Field(ge=0)
    product_click_rate: float = Field(ge=0, le=1)
    inventory_delta: int
    abnormal_order_count: int = Field(ge=0)


class LiveMetricSnapshotIngestRequest(LiveMetricScanRequest):
    platform: Literal["taobao", "douyin"]
    stream_external_id: str = Field(min_length=1, max_length=200)
    observed_at: datetime
    source_reference: str = Field(default="", max_length=500)


class LiveMetricSnapshotResponse(BaseModel):
    id: str
    company_id: str
    platform: Literal["taobao", "douyin"]
    stream_external_id: str
    observed_at: str
    online_users: int
    conversion_rate: float
    retention_rate: float
    comment_count: int
    like_count: int
    product_click_rate: float
    inventory_delta: int
    abnormal_order_count: int
    source_reference: str

class PostLiveReviewRequest(BaseModel):
    sales_amount_yuan: float = Field(ge=0)
    order_count: int = Field(ge=0)
    viewer_count: int = Field(ge=0)
    refund_count: int = Field(ge=0)
    top_product_title: str = Field(min_length=1, max_length=200)
    negative_comment_count: int = Field(ge=0)
    host_script_score: int = Field(ge=0, le=100)


class LiveWorkflowReportResponse(BaseModel):
    stage: Literal["pre_live", "during_live", "post_live"]
    status: Literal["done", "warning", "blocked", "pending"]
    score: int
    saved_minutes: int
    estimated_saving_yuan: int
    checks: tuple[LiveOperationCheckItemResponse, ...]
    alerts: tuple[LiveOperationAlertResponse, ...]
    next_actions: tuple[str, ...]


class LivePostReviewReportResponse(BaseModel):
    stage: Literal["pre_live", "during_live", "post_live"]
    status: Literal["done", "warning", "blocked", "pending"]
    score: int
    saved_minutes: int
    estimated_saving_yuan: int
    sales_amount_yuan: float
    conversion_rate: float
    top_product_title: str
    refund_risk_note: str
    host_performance_note: str
    next_day_actions: tuple[str, ...]


class LiveWorkflowRunResponse(BaseModel):
    id: str
    workflow_name: str
    stage: Literal["pre_live", "during_live", "post_live"]
    status: Literal["done", "warning", "blocked", "pending"]
    score: int
    saved_minutes: int
    estimated_saving_yuan: int
    alert_count: int
    approval_required: bool
    proof: str
    created_at: str

class CeoReportMetricResponse(BaseModel):
    id: str
    label: str
    value: str
    explanation: str


class CeoReportRiskResponse(BaseModel):
    id: str
    level: Literal["high", "medium", "low"]
    title: str
    reason: str
    suggested_action: str
    money_impact: str


class CeoReportActionResponse(BaseModel):
    id: str
    owner: Literal["boss", "ai-live-operator", "ai-operator", "ai-after-sale", "ai-customer"]
    title: str
    expected_result: str
    requires_approval: bool


class CeoDailyReportResponse(BaseModel):
    date: str
    headline: str
    business_health_score: int
    boss_message: str
    saved_money_today_yuan: int
    projected_monthly_saving_yuan: int
    annual_roi_percent: int
    replacement_target_yuan: int
    live_operation_status: str
    data_status: Literal["demo_estimate", "real_workflow_logs"]
    data_status_label: str
    data_status_reason: str
    metrics: tuple[CeoReportMetricResponse, ...]
    top_risks: tuple[CeoReportRiskResponse, ...]
    priority_actions: tuple[CeoReportActionResponse, ...]
    ai_employee_notes: tuple[str, ...]
    proof_points: tuple[str, ...]

class DailyOperationsRunRequest(BaseModel):
    trigger: Literal["manual", "scheduled", "webhook"] = "manual"
    pre_live: PreLiveCheckRequest | None = None
    live_metrics: LiveMetricScanRequest | None = None
    post_live: PostLiveReviewRequest | None = None


class DailyOperationsRunResponse(BaseModel):
    id: str
    date: str
    trigger: Literal["manual", "scheduled", "webhook"]
    input_mode: Literal["merchant_payload", "safe_baseline"]
    status: Literal["completed", "needs_real_data"]
    replacement_role: str
    operator_message: str
    completed_work_count: int
    saved_minutes: int
    saved_yuan: int
    workflow_runs: tuple[LiveWorkflowRunResponse, ...]
    ceo_report: CeoDailyReportResponse
    savings_summary: SavingsSummaryResponse
    next_run_hint: str


class StrategyCapabilityResponse(BaseModel):
    id: str
    priority: Literal["P0", "P1", "P2"]
    name: str
    status: Literal["done", "in_progress", "gap"]
    score: int
    proof: str
    gap: str
    next_action: str
    replaced_role: str
    daily_saved_minutes: int


class StrategyAuditResponse(BaseModel):
    positioning: str
    focus: str
    overall_score: int
    completed_count: int
    gap_count: int
    estimated_daily_saved_minutes: int
    estimated_daily_saved_yuan: int
    stop_doing: tuple[str, ...]
    capabilities: tuple[StrategyCapabilityResponse, ...]
    next_p0_actions: tuple[str, ...]



class PublicMarketSignalRequest(BaseModel):
    source_name: str = Field(min_length=1, max_length=120)
    source_url: str = Field(pattern=r"^https?://")
    observed_at: str = Field(min_length=1, max_length=80)
    signal_kind: Literal["official_ranking", "public_listing", "public_content"]
    platform: str = Field(min_length=1, max_length=40)
    category: str = Field(min_length=1, max_length=80)
    product_name: str = Field(min_length=1, max_length=160)
    price_yuan: float = Field(ge=0)
    engagement_score: int = Field(ge=0, le=100)
    review_sentiment: Literal["positive", "neutral", "negative"]


class MarketIntelligenceRequest(BaseModel):
    signals: tuple[PublicMarketSignalRequest, ...] = Field(min_length=1, max_length=50)


class MarketIntelligenceResponse(BaseModel):
    category: str
    data_status: Literal["public_market_signal"]
    data_status_reason: str
    source_count: int
    price_floor_yuan: float
    price_ceiling_yuan: float
    median_price_yuan: float
    opportunity_score: int
    risk_score: int
    recommendation: str
    next_actions: tuple[str, ...]
    proof_points: tuple[str, ...]
    merchant_roi_eligible: bool
    replaced_role: str
    estimated_saved_minutes: int
class RefundCollaborationRequest(BaseModel):
    source_message_id: str = Field(min_length=1, max_length=200)
    customer_message: str = Field(min_length=1, max_length=5000)
    order_external_id: str | None = Field(default=None, max_length=200)
    order_amount_yuan: float = Field(ge=0)
    refund_amount_yuan: float = Field(ge=0)
    delivered: bool = False
    evidence_count: int = Field(default=0, ge=0)
    inventory_available: bool = False
    complaint_risk: bool = False


class RefundWorkflowStepResponse(BaseModel):
    id: str
    agent_id: str
    title: str
    status: Literal["done", "needs_approval", "blocked"]
    evidence: str
    requires_approval: bool


class RefundCollaborationResponse(BaseModel):
    id: str
    source_message_id: str
    status: Literal["ready_to_reply", "approval_required", "blocked"]
    decision: Literal["reject_request", "refund_review", "replacement", "compensation_review", "need_more_evidence"]
    saved_minutes: int
    estimated_saving_yuan: int
    evidence_source: Literal["manual_payload", "real_order_records"]
    proof: str
    approval_id: str | None
    customer_reply: str
    next_actions: tuple[str, ...]
    steps: tuple[RefundWorkflowStepResponse, ...]
