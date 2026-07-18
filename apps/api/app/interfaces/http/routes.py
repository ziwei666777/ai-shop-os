from fastapi import APIRouter, Depends, HTTPException
from fastapi import Header, Request

from apps.api.app.application.use_cases import (
    GetAgent,
    GetDashboardSummary,
    DecideAfterSaleCase,
    DraftCustomerReply,
    GetAfterSaleCase,
    GetCeoDailyReport,
    IngestCustomerMessage,
    ListAgentLogs,
    ListAgents,
    ListAfterSaleCases,
    ListConnectorStatuses,
    ListCustomerInbox,
    ListFeedbackMetrics,
    RecordLearningEvent,
    GetTrainingCenterSummary,
    GetLiveOperationSummary,
    GetSavingsSummary,
    RunEvaluationSummary,
    RunReplaySummary,
    RunSimulationSummary,
    RunDailyOperations,
    SendCustomerReply,
    TakeoverCustomerMessage,
)
from apps.api.app.application.agent_routing import RouteAgentEvent
from apps.api.app.domain.agent_routing import AgentRoutingInput
from apps.api.app.infrastructure.after_sale_decision_workflow import (
    dispatch_queued_warehouse_notifications,
    run_after_sale_decision_workflow,
)
from apps.api.app.infrastructure.agent_runtime_provider import agent_workflow
from apps.api.app.infrastructure.commerce_connectors import ShopifyConnector
from apps.api.app.infrastructure.evaluation_engine import run_evaluation_summary
from apps.api.app.infrastructure.ceo_report_engine import get_ceo_daily_report
from apps.api.app.infrastructure.daily_operations_runner import run_daily_operations
from apps.api.app.infrastructure.live_operation_engine import get_live_operation_summary, get_savings_summary
from apps.api.app.infrastructure.live_metric_snapshots import record_live_metric_snapshot
from apps.api.app.infrastructure.live_operation_workflows import (
    run_live_metric_scan,
    run_post_live_review,
    run_pre_live_check,
)
from apps.api.app.infrastructure.live_workflow_log_store import (
    list_live_workflow_runs,
    record_live_workflow_report,
    record_post_live_review,
)
from apps.api.app.infrastructure.approval_records import decide_approval_record, list_pending_approvals
from apps.api.app.infrastructure.replay_engine import run_replay_summary
from apps.api.app.infrastructure.refund_business_evidence import get_refund_business_evidence
from apps.api.app.infrastructure.refund_collaboration_workflow import run_refund_collaboration_workflow
from apps.api.app.infrastructure.simulation_engine import run_simulation_summary
from apps.api.app.infrastructure.strategy_audit import get_strategy_audit
from apps.api.app.infrastructure.training_center import commit_training_asset, get_training_center_summary
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
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
    ApprovalResponse,
    ConnectorStatusResponse,
    CeoDailyReportResponse,
    CustomerMessageIngestRequest,
    CustomerInboxItemResponse,
    CustomerReplySendRequest,
    DailyOperationsRunRequest,
    DailyOperationsRunResponse,
    DashboardSummaryResponse,
    DraftReplyResponse,
    EvaluationSummaryResponse,
    AgentFeedbackMetricResponse,
    KnowledgeSourceResponse,
    LearningEventRequest,
    LearningEventResponse,
    LiveMetricScanRequest,
    LiveMetricSnapshotIngestRequest,
    LiveMetricSnapshotResponse,
    LiveOperationSummaryResponse,
    LivePostReviewReportResponse,
    LiveWorkflowReportResponse,
    LiveWorkflowRunResponse,
    OAuthStartRequest,
    OAuthStartResponse,
    PostLiveReviewRequest,
    PreLiveCheckRequest,
    RefundCollaborationRequest,
    RefundCollaborationResponse,
    ReplaySummaryResponse,
    SavingsSummaryResponse,
    SimulationSummaryResponse,
    StrategyAuditResponse,
    TrainingAssetCandidateResponse,
    TrainingCenterSummaryResponse,
    WebhookIngestResponse,
    WarehouseNotificationDispatchResponse,
    WorkflowResponse,
)
from apps.api.app.interfaces.http.auth import CompanyContext, require_company_context, require_customer_message_ingest_context, require_merchant_bridge_context

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


@router.get("/v1/ceo/daily-report", response_model=CeoDailyReportResponse)
async def ceo_daily_report() -> CeoDailyReportResponse:
    report = await GetCeoDailyReport(get_ceo_daily_report).execute()
    return CeoDailyReportResponse.model_validate(report, from_attributes=True)

@router.get("/v1/replay/summary", response_model=ReplaySummaryResponse)
async def replay_summary(
    x_company_id: str = Header(default="00000000-0000-0000-0000-000000000001", alias="X-Company-ID")
) -> ReplaySummaryResponse:
    summary = await RunReplaySummary(lambda: run_replay_summary(x_company_id)).execute()
    return ReplaySummaryResponse.model_validate(summary, from_attributes=True)


@router.get("/v1/evaluation/summary", response_model=EvaluationSummaryResponse)
async def evaluation_summary(x_company_id: str = Header(default="00000000-0000-0000-0000-000000000001", alias="X-Company-ID")) -> EvaluationSummaryResponse:
    summary = await RunEvaluationSummary(lambda: run_evaluation_summary(x_company_id)).execute()
    return EvaluationSummaryResponse.model_validate(summary, from_attributes=True)


@router.get("/v1/training-center/summary", response_model=TrainingCenterSummaryResponse)
async def training_center_summary(
    x_company_id: str = Header(default="00000000-0000-0000-0000-000000000001", alias="X-Company-ID")
) -> TrainingCenterSummaryResponse:
    summary = await GetTrainingCenterSummary(lambda: get_training_center_summary(x_company_id)).execute()
    return TrainingCenterSummaryResponse.model_validate(summary, from_attributes=True)


@router.post("/v1/training-center/assets/{candidate_id}/commit", response_model=TrainingAssetCandidateResponse)
async def commit_training_center_asset(
    candidate_id: str,
    x_company_id: str = Header(default="00000000-0000-0000-0000-000000000001", alias="X-Company-ID"),
) -> TrainingAssetCandidateResponse:
    candidate = commit_training_asset(x_company_id, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="训练候选资产不存在，或当前仍需复核。")
    return TrainingAssetCandidateResponse.model_validate(candidate, from_attributes=True)


@router.get("/v1/simulation/summary", response_model=SimulationSummaryResponse)
async def simulation_summary() -> SimulationSummaryResponse:
    summary = await RunSimulationSummary(run_simulation_summary).execute()
    return SimulationSummaryResponse.model_validate(summary, from_attributes=True)


@router.get("/v1/strategy/audit", response_model=StrategyAuditResponse)
async def strategy_audit() -> StrategyAuditResponse:
    audit = get_strategy_audit()
    return StrategyAuditResponse.model_validate(audit, from_attributes=True)


@router.post("/v1/workflows/refund-collaboration/run", response_model=RefundCollaborationResponse)
async def refund_collaboration_run(payload: RefundCollaborationRequest) -> RefundCollaborationResponse:
    run = run_refund_collaboration_workflow(
        source_message_id=payload.source_message_id,
        customer_message=payload.customer_message,
        order_amount_yuan=payload.order_amount_yuan,
        refund_amount_yuan=payload.refund_amount_yuan,
        delivered=payload.delivered,
        evidence_count=payload.evidence_count,
        inventory_available=payload.inventory_available,
        complaint_risk=payload.complaint_risk,
        business_evidence=get_refund_business_evidence(payload.order_external_id),
    )
    return RefundCollaborationResponse.model_validate(run, from_attributes=True)


@router.get("/v1/live-operations/summary", response_model=LiveOperationSummaryResponse)
async def live_operation_summary() -> LiveOperationSummaryResponse:
    summary = await GetLiveOperationSummary(get_live_operation_summary).execute()
    return LiveOperationSummaryResponse.model_validate(summary, from_attributes=True)


@router.get("/v1/savings/summary", response_model=SavingsSummaryResponse)
async def savings_summary() -> SavingsSummaryResponse:
    summary = await GetSavingsSummary(get_savings_summary).execute()
    return SavingsSummaryResponse.model_validate(summary, from_attributes=True)




@router.post("/v1/daily-operations/run", response_model=DailyOperationsRunResponse)
async def run_daily_operations_route(payload: DailyOperationsRunRequest) -> DailyOperationsRunResponse:
    run = await RunDailyOperations(run_daily_operations).execute(
        trigger=payload.trigger,
        pre_live=payload.pre_live.model_dump() if payload.pre_live else None,
        live_metrics=payload.live_metrics.model_dump() if payload.live_metrics else None,
        post_live=payload.post_live.model_dump() if payload.post_live else None,
    )
    return DailyOperationsRunResponse.model_validate(run, from_attributes=True)

@router.get("/v1/live-operations/runs", response_model=tuple[LiveWorkflowRunResponse, ...])
async def live_workflow_runs() -> tuple[LiveWorkflowRunResponse, ...]:
    runs = list_live_workflow_runs()
    return tuple(LiveWorkflowRunResponse.model_validate(run, from_attributes=True) for run in runs)

@router.post("/v1/live-operations/pre-live-check", response_model=LiveWorkflowReportResponse)
async def pre_live_check(payload: PreLiveCheckRequest) -> LiveWorkflowReportResponse:
    report = run_pre_live_check(
        products=tuple(item.model_dump() for item in payload.products),
        coupons=tuple(item.model_dump() for item in payload.coupons),
        script_text=payload.script_text,
        gift_ready=payload.gift_ready,
        product_order_ready=payload.product_order_ready,
    )
    record_live_workflow_report("开播前检查", report, input_snapshot=payload.model_dump())
    return LiveWorkflowReportResponse.model_validate(report, from_attributes=True)


@router.post("/v1/live-operations/metric-snapshots", response_model=LiveMetricSnapshotResponse, status_code=201)
async def ingest_live_metric_snapshot(
    payload: LiveMetricSnapshotIngestRequest,
    context: CompanyContext = Depends(require_merchant_bridge_context),
) -> LiveMetricSnapshotResponse:
    snapshot = record_live_metric_snapshot(context.company_id, payload.model_dump())
    return LiveMetricSnapshotResponse.model_validate(snapshot, from_attributes=True)

@router.post("/v1/live-operations/live-metric-scan", response_model=LiveWorkflowReportResponse)
async def live_metric_scan(payload: LiveMetricScanRequest) -> LiveWorkflowReportResponse:
    report = run_live_metric_scan(
        online_users=payload.online_users,
        conversion_rate=payload.conversion_rate,
        retention_rate=payload.retention_rate,
        comment_count=payload.comment_count,
        like_count=payload.like_count,
        product_click_rate=payload.product_click_rate,
        inventory_delta=payload.inventory_delta,
        abnormal_order_count=payload.abnormal_order_count,
    )
    record_live_workflow_report("直播中扫描", report, input_snapshot=payload.model_dump())
    return LiveWorkflowReportResponse.model_validate(report, from_attributes=True)


@router.post("/v1/live-operations/post-live-review", response_model=LivePostReviewReportResponse)
async def post_live_review(payload: PostLiveReviewRequest) -> LivePostReviewReportResponse:
    report = run_post_live_review(
        sales_amount_yuan=payload.sales_amount_yuan,
        order_count=payload.order_count,
        viewer_count=payload.viewer_count,
        refund_count=payload.refund_count,
        top_product_title=payload.top_product_title,
        negative_comment_count=payload.negative_comment_count,
        host_script_score=payload.host_script_score,
    )
    record_post_live_review("下播复盘", report, input_snapshot=payload.model_dump())
    return LivePostReviewReportResponse.model_validate(report, from_attributes=True)


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
    approvals = list_pending_approvals()
    return tuple(
        ApprovalResponse(
            id=approval.id,
            title=approval.title,
            risk_level=approval.risk_level,
            status=approval.status,
        )
        for approval in approvals
    )



@router.post("/v1/approvals/{approval_id}/decision", response_model=ApprovalDecisionResponse)
async def decide_approval(approval_id: str, payload: ApprovalDecisionRequest) -> ApprovalDecisionResponse:
    approval = decide_approval_record(approval_id, payload.decision, payload.note)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval record not found")
    outcome = run_after_sale_decision_workflow(
        approval=approval,
        decision=payload.decision,
        action=payload.action,
        note=payload.note,
    )
    return ApprovalDecisionResponse.model_validate(outcome, from_attributes=True)

@router.post("/v1/warehouse-notifications/dispatch", response_model=WarehouseNotificationDispatchResponse)
async def dispatch_warehouse_notifications(limit: int = 20) -> WarehouseNotificationDispatchResponse:
    result = dispatch_queued_warehouse_notifications(limit=limit)
    return WarehouseNotificationDispatchResponse.model_validate(result, from_attributes=True)

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


@router.post("/v1/customer-agent/external-messages", response_model=CustomerInboxItemResponse, status_code=201)
async def ingest_external_customer_message(
    payload: CustomerMessageIngestRequest,
    context: CompanyContext = Depends(require_customer_message_ingest_context),
) -> CustomerInboxItemResponse:
    item = await IngestCustomerMessage(customer_agent_repository()).execute(
        context.company_id,
        payload.platform,
        payload.platform_message_id,
        payload.customer_name,
        payload.content,
        payload.channel,
        payload.customer_external_id,
        payload.order_external_id,
    )
    return CustomerInboxItemResponse.model_validate(item, from_attributes=True)


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



