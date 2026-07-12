from apps.api.app.domain.models import (
    AfterSaleCase,
    AgentFeedbackMetric,
    Agent,
    AgentLog,
    ConnectorStatusView,
    CustomerInboxItem,
    DashboardMetric,
    DashboardSuggestion,
    DashboardSummary,
    DraftReply,
    LearningEvent,
    LearningAction,
)
from typing import cast

from apps.api.app.domain.repositories import (
    AfterSaleRepository,
    AgentRepository,
    ConnectorRepository,
    CustomerAgentRepository,
    DashboardRepository,
    FeedbackMetricRepository,
    LearningRepository,
)


AGENTS: tuple[Agent, ...] = (
    Agent(
        id="ai-boss",
        name="AI 老板",
        type="boss",
        status="online",
        description="每天生成老板经营汇报、识别异常、汇总审批并分配 AI 员工任务。",
        prompt="你是 AI Shop OS 的 AI 老板，只给出可追踪、可审批、可执行的经营建议。",
        today_handled_count=12,
        kpi_score=86,
        future_tasks=("接入日报生成", "接入审批策略", "接入利润分析"),
    ),
    Agent(
        id="ai-customer",
        name="AI 客服",
        type="customer",
        status="online",
        description="负责商品咨询、订单查询、物流查询、退款说明和未知问题升级。",
        prompt="你是 AI 客服，禁止编造答案；不确定时必须暂停并升级给老板。",
        today_handled_count=96,
        kpi_score=91,
        future_tasks=("接入对话记忆（Memory）", "接入检索增强知识库（RAG）", "接入人工接管"),
    ),
    Agent(
        id="ai-operator",
        name="AI 运营",
        type="operator",
        status="paused",
        description="后续负责商品标题、详情页、广告、竞品和 SEO 分析。",
        prompt="等待 Sprint 2 之后启用。",
        today_handled_count=0,
        kpi_score=0,
        future_tasks=("商品优化", "竞品分析", "广告建议"),
    ),
    Agent(
        id="ai-after-sale",
        name="AI 售后",
        type="after_sale",
        status="online",
        description="负责退款、退货、物流异常、投诉和赔偿的风险判断与审批建议。",
        prompt="你是 AI 售后，涉及退款、赔偿、投诉和金额变化时必须要求商家确认。",
        today_handled_count=18,
        kpi_score=82,
        future_tasks=("接入退款规则", "接入物流异常识别", "接入售后审批流"),
    ),
)

INBOX_ITEMS: dict[str, CustomerInboxItem] = {
    "msg-1": CustomerInboxItem(
        id="msg-1",
        platform="shopify",
        customer_name="Lily Chen",
        channel="shopify_inbox",
        content="这件衬衫还有 M 码吗？今天下单什么时候发货？",
        intent="faq",
        order_external_id=None,
        logistics_status=None,
        confidence=0.92,
        automation_decision="auto_reply",
        status="pending",
        created_at="2026-07-09T10:12:00+08:00",
    ),
    "msg-2": CustomerInboxItem(
        id="msg-2",
        platform="shopify",
        customer_name="Alex Wong",
        channel="shopify_inbox",
        content="订单 #1007 到哪里了？",
        intent="logistics",
        order_external_id="#1007",
        logistics_status="运输中，预计 2 天内送达",
        confidence=0.88,
        automation_decision="auto_reply",
        status="pending",
        created_at="2026-07-09T10:18:00+08:00",
    ),
    "msg-3": CustomerInboxItem(
        id="msg-3",
        platform="taobao",
        customer_name="王女士",
        channel="taobao_message",
        content="收到货有瑕疵，可以赔偿吗？",
        intent="compensation",
        order_external_id="TB20260709003",
        logistics_status="已签收",
        confidence=0.67,
        automation_decision="human_review",
        status="needs_human",
        created_at="2026-07-09T10:25:00+08:00",
    ),
}

AFTER_SALE_CASES: dict[str, AfterSaleCase] = {
    "case-1": AfterSaleCase(
        id="case-1",
        platform="shopify",
        case_type="refund",
        status="waiting_merchant",
        customer_name="Alex Wong",
        order_external_id="#1007",
        title="客户申请退款",
        description="客户表示物流超过预期，希望退款。",
        risk_level="medium",
        ai_suggestion="先核查物流轨迹，如果 48 小时内无更新，再建议部分补偿或退款审批。",
        approval_required=True,
        created_at="2026-07-09T10:28:00+08:00",
    ),
    "case-2": AfterSaleCase(
        id="case-2",
        platform="taobao",
        case_type="complaint",
        status="waiting_merchant",
        customer_name="王女士",
        order_external_id="TB20260709003",
        title="商品瑕疵投诉",
        description="客户反馈商品有瑕疵并提出赔偿。",
        risk_level="high",
        ai_suggestion="需要人工查看图片证据；未确认前不得承诺赔偿金额。",
        approval_required=True,
        created_at="2026-07-09T10:31:00+08:00",
    ),
}

LEARNING_EVENTS: list[LearningEvent] = []


class MemoryDashboardRepository(DashboardRepository):
    async def get_today_summary(self) -> DashboardSummary:
        return DashboardSummary(
            date="2026-07-09",
            pending_approval_count=3,
            metrics=(
                DashboardMetric("sales", "今日销售", "¥12,860", "较昨日 +8.2%"),
                DashboardMetric("profit", "今日利润", "¥3,420", "毛利率 26.6%"),
                DashboardMetric("inventory", "库存风险", "5 个 SKU", "2 个低于安全库存"),
                DashboardMetric("refunds", "退款异常", "7 单", "2 单需要审批"),
            ),
            agents=AGENTS,
            suggestions=(
                DashboardSuggestion("s1", "优先审批 2 个退款申请", "等待时间超过 6 小时，可能影响店铺体验分。", "high"),
                DashboardSuggestion("s2", "检查热销 SKU 库存", "订单增长明显，当前库存可售天数低于 5 天。", "medium"),
                DashboardSuggestion("s3", "沉淀 AI 客服未知问题", "把老板回答转成知识，后续相同问题由 AI 自动处理。", "low"),
            ),
        )


class MemoryAgentRepository(AgentRepository):
    async def list_agents(self) -> tuple[Agent, ...]:
        return AGENTS

    async def get_agent(self, agent_id: str) -> Agent | None:
        return next((agent for agent in AGENTS if agent.id == agent_id), None)

    async def list_logs(self, agent_id: str) -> tuple[AgentLog, ...]:
        if not any(agent.id == agent_id for agent in AGENTS):
            return ()

        return (
            AgentLog("log-1", agent_id, "info", "读取今日任务状态。", "2026-07-09T09:00:00+08:00"),
            AgentLog("log-2", agent_id, "info", "等待工作流程引擎（Workflow Engine）接入。", "2026-07-09T09:05:00+08:00"),
        )


class MemoryCustomerAgentRepository(CustomerAgentRepository):
    async def list_inbox(self) -> tuple[CustomerInboxItem, ...]:
        return tuple(INBOX_ITEMS.values())

    async def draft_reply(self, message_id: str) -> DraftReply | None:
        message = INBOX_ITEMS.get(message_id)
        if message is None:
            return None

        if message.automation_decision == "human_review":
            return DraftReply(
                message_id=message_id,
                content="这个问题涉及退款、赔偿或投诉，需要商家确认后再回复。",
                confidence=message.confidence,
                automation_decision="human_review",
                reason="命中高风险售后规则，禁止自动承诺金额或结果。",
                required_human_review=True,
            )

        if message.intent == "logistics":
            content = f"您好，您的订单 {message.order_external_id} 当前状态是：{message.logistics_status}。我会继续帮您关注物流更新。"
        elif message.intent == "order":
            content = f"您好，您的订单 {message.order_external_id} 已查询到，我们会按订单状态继续为您跟进。"
        else:
            content = "您好，这款商品当前可以正常咨询和下单。具体尺码库存我会按页面实时库存为您确认。"

        return DraftReply(
            message_id=message_id,
            content=content,
            confidence=message.confidence,
            automation_decision="auto_reply",
            reason="属于 FAQ、订单或物流低风险范围，可自动回复。",
            required_human_review=False,
        )

    async def mark_sent(self, message_id: str, final_content: str | None = None) -> CustomerInboxItem | None:
        message = INBOX_ITEMS.get(message_id)
        if message is None or message.automation_decision == "human_review":
            return None
        updated = CustomerInboxItem(**{**message.__dict__, "status": "sent"})
        INBOX_ITEMS[message_id] = updated
        return updated

    async def mark_takeover(self, message_id: str) -> CustomerInboxItem | None:
        message = INBOX_ITEMS.get(message_id)
        if message is None:
            return None
        updated = CustomerInboxItem(**{**message.__dict__, "status": "human_takeover", "automation_decision": "human_review"})
        INBOX_ITEMS[message_id] = updated
        return updated


class MemoryAfterSaleRepository(AfterSaleRepository):
    async def list_cases(self) -> tuple[AfterSaleCase, ...]:
        return tuple(AFTER_SALE_CASES.values())

    async def get_case(self, case_id: str) -> AfterSaleCase | None:
        return AFTER_SALE_CASES.get(case_id)

    async def record_decision(self, case_id: str, decision: str, note: str) -> AfterSaleCase | None:
        case = AFTER_SALE_CASES.get(case_id)
        if case is None:
            return None
        status = "resolved" if decision in {"approved", "rejected"} else case.status
        updated = AfterSaleCase(**{**case.__dict__, "status": status})
        AFTER_SALE_CASES[case_id] = updated
        return updated


class MemoryLearningRepository(LearningRepository):
    async def record_event(
        self,
        source_type: str,
        source_id: str,
        agent_id: str,
        action: str,
        original_content: str,
        final_content: str,
    ) -> LearningEvent:
        event = LearningEvent(
            id=f"learn-{len(LEARNING_EVENTS) + 1}",
            source_type=source_type,
            source_id=source_id,
            agent_id=agent_id,
            action=cast(LearningAction, action),
            original_content=original_content,
            final_content=final_content,
            created_at="2026-07-09T11:00:00+08:00",
        )
        LEARNING_EVENTS.append(event)
        return event


class MemoryFeedbackMetricRepository(FeedbackMetricRepository):
    async def list_metrics(self) -> tuple[AgentFeedbackMetric, ...]:
        return (
            AgentFeedbackMetric("metric-1", "ai-customer", "客服问答修正样本", 60, 0.6),
            AgentFeedbackMetric("metric-2", "ai-after-sale", "售后决策样本", 30, 0.3),
            AgentFeedbackMetric("metric-3", "ai-customer", "采纳率与接管率", 10, 0.1),
        )


class MemoryConnectorRepository(ConnectorRepository):
    async def list_statuses(self) -> tuple[ConnectorStatusView, ...]:
        return (
            ConnectorStatusView(
                platform="taobao",
                status="pending",
                display_name="淘宝开放平台",
                scopes=("订单查询", "商品查询", "物流查询", "消息接入"),
                next_action="申请淘宝开放平台应用权限，并配置 App Key、密钥和回调地址。",
            ),
            ConnectorStatusView(
                platform="douyin",
                status="pending",
                display_name="抖音商店",
                scopes=("商家授权", "订单查询", "商品查询", "售后查询"),
                next_action="申请抖店开放平台应用和对应电商权限，再接入官方 OpenAPI。",
            ),
            ConnectorStatusView(
                platform="xianyu",
                status="not_connected",
                display_name="闲鱼",
                scopes=("官方能力待确认",),
                next_action="等待确认可商用的官方开放能力；不使用 Cookie、扫码登录或抓包方案。",
            ),
            ConnectorStatusView(
                platform="shopify",
                status="pending",
                display_name="Shopify",
                scopes=("读取订单", "读取商品", "读取客户"),
                next_action="海外平台后续接入，当前优先级低于淘宝、抖音和闲鱼。",
            ),
        )
