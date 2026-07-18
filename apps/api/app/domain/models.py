from dataclasses import dataclass
from typing import Literal


AgentStatus = Literal["online", "paused", "offline"]
AgentType = Literal[
    "boss",
    "customer",
    "operator",
    "after_sale",
    "purchase",
    "logistics",
    "finance",
    "analyst",
]
Priority = Literal["high", "medium", "low"]
MessageIntent = Literal["faq", "order", "logistics", "refund", "complaint", "compensation", "unknown"]
AutomationDecision = Literal["auto_reply", "human_review"]
AfterSaleCaseType = Literal["refund", "return", "logistics_issue", "complaint", "compensation"]
AfterSaleStatus = Literal["open", "waiting_merchant", "resolved"]
LearningAction = Literal["accepted", "edited", "rejected", "manual_answered"]
ConnectorPlatform = Literal["taobao", "douyin", "xianyu", "shopify"]
ConnectorStatus = Literal["connected", "pending", "not_connected"]


@dataclass(frozen=True)
class DashboardMetric:
    id: str
    label: str
    value: str
    trend: str


@dataclass(frozen=True)
class DashboardSuggestion:
    id: str
    title: str
    reason: str
    priority: Priority


@dataclass(frozen=True)
class Agent:
    id: str
    name: str
    type: AgentType
    status: AgentStatus
    description: str
    prompt: str
    today_handled_count: int
    kpi_score: int
    future_tasks: tuple[str, ...]


@dataclass(frozen=True)
class AgentLog:
    id: str
    agent_id: str
    level: str
    message: str
    created_at: str


@dataclass(frozen=True)
class DashboardSummary:
    date: str
    metrics: tuple[DashboardMetric, ...]
    agents: tuple[Agent, ...]
    suggestions: tuple[DashboardSuggestion, ...]
    pending_approval_count: int


@dataclass(frozen=True)
class CustomerInboxItem:
    id: str
    platform: ConnectorPlatform
    customer_name: str
    channel: str
    content: str
    intent: MessageIntent
    order_external_id: str | None
    logistics_status: str | None
    confidence: float
    automation_decision: AutomationDecision
    status: str
    created_at: str


@dataclass(frozen=True)
class DraftReply:
    message_id: str
    content: str
    confidence: float
    automation_decision: AutomationDecision
    reason: str
    required_human_review: bool
    knowledge_hit: str | None = None
    memory_hit: str | None = None
    saved_minutes: int = 0
    estimated_saving_yuan: int = 0


@dataclass(frozen=True)
class AfterSaleCase:
    id: str
    platform: ConnectorPlatform
    case_type: AfterSaleCaseType
    status: AfterSaleStatus
    customer_name: str
    order_external_id: str
    title: str
    description: str
    risk_level: Priority
    ai_suggestion: str
    approval_required: bool
    created_at: str


@dataclass(frozen=True)
class LearningEvent:
    id: str
    source_type: str
    source_id: str
    agent_id: str
    action: LearningAction
    original_content: str
    final_content: str
    created_at: str


@dataclass(frozen=True)
class AgentFeedbackMetric:
    id: str
    agent_id: str
    metric_name: str
    metric_value: float
    weight: float


@dataclass(frozen=True)
class ConnectorStatusView:
    platform: ConnectorPlatform
    status: ConnectorStatus
    display_name: str
    scopes: tuple[str, ...]
    next_action: str
