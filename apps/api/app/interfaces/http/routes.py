from fastapi import APIRouter, HTTPException
from fastapi import Header, Request

from apps.api.app.application.use_cases import (
    GetAgent,
    GetDashboardSummary,
    DecideAfterSaleCase,
    DraftCustomerReply,
    GetAfterSaleCase,
    ListAgentLogs,
    ListAgents,
    ListAfterSaleCases,
    ListConnectorStatuses,
    ListCustomerInbox,
    ListFeedbackMetrics,
    RecordLearningEvent,
    SendCustomerReply,
    TakeoverCustomerMessage,
)
from apps.api.app.application.agent_routing import RouteAgentEvent
from apps.api.app.domain.agent_routing import AgentRoutingInput
from apps.api.app.infrastructure.agent_runtime_provider import agent_workflow
from apps.api.app.infrastructure.commerce_connectors import ShopifyConnector
from apps.api.app.infrastructure.repository_provider import (
    after_sale_repository,
    agent_repository,
    connector_repository,
    customer_agent_repository,
    dashboard_repository,
    feedback_metric_repository,
    learning_repository,
)
from apps.api.app.interfaces.http.schemas import (
    AgentLogResponse,
    AgentRoutingRequest,
    AgentRoutingResponse,
    AgentResponse,
    AfterSaleCaseResponse,
    AfterSaleDecisionRequest,
    ApprovalResponse,
    ConnectorStatusResponse,
    CustomerInboxItemResponse,
    CustomerReplySendRequest,
    DashboardSummaryResponse,
    DraftReplyResponse,
    AgentFeedbackMetricResponse,
    KnowledgeSourceResponse,
    LearningEventRequest,
    LearningEventResponse,
    OAuthStartRequest,
    OAuthStartResponse,
    WebhookIngestResponse,
    WorkflowResponse,
)

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-shop-os-api"}


@router.post("/v1/agent-runtime/route", response_model=AgentRoutingResponse)
async def route_agent_event(payload: AgentRoutingRequest) -> AgentRoutingResponse:
    decision = RouteAgentEvent(agent_workflow()).execute(
        AgentRoutingInput(
            source_id=payload.source_id,
            event_type=payload.event_type,
            intent=payload.intent,
            confidence=payload.confidence,
        )
    )
    return AgentRoutingResponse.model_validate(decision, from_attributes=True)


@router.get("/v1/dashboard/summary", response_model=DashboardSummaryResponse)
async def dashboard_summary() -> DashboardSummaryResponse:
    summary = await GetDashboardSummary(dashboard_repository()).execute()
    return DashboardSummaryResponse.model_validate(summary, from_attributes=True)


@router.get("/v1/agents", response_model=tuple[AgentResponse, ...])
async def list_agents() -> tuple[AgentResponse, ...]:
    agents = await ListAgents(agent_repository()).execute()
    return tuple(AgentResponse.model_validate(agent, from_attributes=True) for agent in agents)


@router.get("/v1/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str) -> AgentResponse:
    agent = await GetAgent(agent_repository()).execute(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="AI 员工不存在")
    return AgentResponse.model_validate(agent, from_attributes=True)


@router.get("/v1/agents/{agent_id}/logs", response_model=tuple[AgentLogResponse, ...])
async def list_agent_logs(agent_id: str) -> tuple[AgentLogResponse, ...]:
    logs = await ListAgentLogs(agent_repository()).execute(agent_id)
    return tuple(AgentLogResponse.model_validate(log, from_attributes=True) for log in logs)


@router.get("/v1/approvals/pending", response_model=tuple[ApprovalResponse, ...])
async def pending_approvals() -> tuple[ApprovalResponse, ...]:
    return (
        ApprovalResponse(id="approval-1", title="退款金额超过自动处理阈值", risk_level="medium", status="pending"),
        ApprovalResponse(id="approval-2", title="广告预算调整需要确认", risk_level="high", status="pending"),
    )


@router.get("/v1/workflows", response_model=tuple[WorkflowResponse, ...])
async def workflows() -> tuple[WorkflowResponse, ...]:
    return (
        WorkflowResponse(id="wf-customer-message", name="客户消息处理流程", status="draft"),
        WorkflowResponse(id="wf-refund-review", name="退款审批流程", status="draft"),
    )


@router.get("/v1/knowledge/sources", response_model=tuple[KnowledgeSourceResponse, ...])
async def knowledge_sources() -> tuple[KnowledgeSourceResponse, ...]:
    return (
        KnowledgeSourceResponse(id="ks-policy", title="售后政策", source_type="manual", status="pending_embedding"),
    )


@router.post("/v1/connectors/shopify/oauth/start", response_model=OAuthStartResponse)
async def shopify_oauth_start(payload: OAuthStartRequest) -> OAuthStartResponse:
    result = ShopifyConnector().start_oauth(payload.shop)
    return OAuthStartResponse(**result.__dict__)


@router.get("/v1/connectors/shopify/oauth/callback")
async def shopify_oauth_callback(code: str | None = None, shop: str | None = None, state: str | None = None) -> dict[str, str]:
    if not code or not shop or not state:
        raise HTTPException(status_code=400, detail="缺少 Shopify OAuth 参数")
    return {"status": "pending_token_exchange", "platform": "shopify", "shop": shop}


@router.get("/v1/connectors/status", response_model=tuple[ConnectorStatusResponse, ...])
async def connector_statuses() -> tuple[ConnectorStatusResponse, ...]:
    statuses = await ListConnectorStatuses(connector_repository()).execute()
    return tuple(ConnectorStatusResponse.model_validate(status, from_attributes=True) for status in statuses)


@router.post("/v1/webhooks/shopify", response_model=WebhookIngestResponse)
async def shopify_webhook(
    request: Request,
    x_shopify_hmac_sha256: str = Header(default=""),
) -> WebhookIngestResponse:
    raw_body = await request.body()
    if not ShopifyConnector().verify_webhook(raw_body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Shopify webhook 签名校验失败")
    return WebhookIngestResponse(accepted=True, platform="shopify", reason="Webhook 已通过签名校验并进入试用版接入边界")


@router.get("/v1/customer-agent/inbox", response_model=tuple[CustomerInboxItemResponse, ...])
async def customer_inbox() -> tuple[CustomerInboxItemResponse, ...]:
    items = await ListCustomerInbox(customer_agent_repository()).execute()
    return tuple(CustomerInboxItemResponse.model_validate(item, from_attributes=True) for item in items)


@router.post("/v1/customer-agent/messages/{message_id}/draft-reply", response_model=DraftReplyResponse)
async def draft_customer_reply(message_id: str) -> DraftReplyResponse:
    draft = await DraftCustomerReply(customer_agent_repository()).execute(message_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="客户消息不存在")
    return DraftReplyResponse.model_validate(draft, from_attributes=True)


@router.post("/v1/customer-agent/messages/{message_id}/send", response_model=CustomerInboxItemResponse)
async def send_customer_reply(
    message_id: str, payload: CustomerReplySendRequest | None = None
) -> CustomerInboxItemResponse:
    item = await SendCustomerReply(customer_agent_repository()).execute(message_id, payload.content if payload else None)
    if item is None:
        raise HTTPException(status_code=409, detail="该消息需要人工确认，不能自动发送")
    return CustomerInboxItemResponse.model_validate(item, from_attributes=True)


@router.post("/v1/customer-agent/messages/{message_id}/takeover", response_model=CustomerInboxItemResponse)
async def takeover_customer_message(message_id: str) -> CustomerInboxItemResponse:
    item = await TakeoverCustomerMessage(customer_agent_repository()).execute(message_id)
    if item is None:
        raise HTTPException(status_code=404, detail="客户消息不存在")
    return CustomerInboxItemResponse.model_validate(item, from_attributes=True)


@router.get("/v1/after-sale/cases", response_model=tuple[AfterSaleCaseResponse, ...])
async def after_sale_cases() -> tuple[AfterSaleCaseResponse, ...]:
    cases = await ListAfterSaleCases(after_sale_repository()).execute()
    return tuple(AfterSaleCaseResponse.model_validate(case, from_attributes=True) for case in cases)


@router.get("/v1/after-sale/cases/{case_id}", response_model=AfterSaleCaseResponse)
async def after_sale_case_detail(case_id: str) -> AfterSaleCaseResponse:
    case = await GetAfterSaleCase(after_sale_repository()).execute(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="售后任务不存在")
    return AfterSaleCaseResponse.model_validate(case, from_attributes=True)


@router.post("/v1/after-sale/cases/{case_id}/decision", response_model=AfterSaleCaseResponse)
async def decide_after_sale_case(case_id: str, payload: AfterSaleDecisionRequest) -> AfterSaleCaseResponse:
    case = await DecideAfterSaleCase(after_sale_repository()).execute(case_id, payload.decision, payload.note)
    if case is None:
        raise HTTPException(status_code=404, detail="售后任务不存在")
    return AfterSaleCaseResponse.model_validate(case, from_attributes=True)


@router.post("/v1/learning-events", response_model=LearningEventResponse)
async def learning_event(payload: LearningEventRequest) -> LearningEventResponse:
    event = await RecordLearningEvent(learning_repository()).execute(
        payload.source_type,
        payload.source_id,
        payload.agent_id,
        payload.action,
        payload.original_content,
        payload.final_content,
    )
    return LearningEventResponse.model_validate(event, from_attributes=True)


@router.get("/v1/feedback-metrics", response_model=tuple[AgentFeedbackMetricResponse, ...])
async def feedback_metrics() -> tuple[AgentFeedbackMetricResponse, ...]:
    metrics = await ListFeedbackMetrics(feedback_metric_repository()).execute()
    return tuple(AgentFeedbackMetricResponse.model_validate(metric, from_attributes=True) for metric in metrics)
