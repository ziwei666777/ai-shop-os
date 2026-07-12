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


class DraftReplyResponse(BaseModel):
    message_id: str
    content: str
    confidence: float
    automation_decision: str
    reason: str
    required_human_review: bool


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
