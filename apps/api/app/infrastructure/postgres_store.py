from collections.abc import Callable
from datetime import datetime, timezone
from decimal import Decimal
from typing import cast
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.app.domain.models import (
    AfterSaleCase,
    Agent,
    AgentFeedbackMetric,
    AgentLog,
    AgentStatus,
    AgentType,
    ConnectorStatusView,
    ConnectorPlatform,
    ConnectorStatus,
    CustomerInboxItem,
    DashboardMetric,
    DashboardSuggestion,
    DashboardSummary,
    DraftReply,
    AfterSaleCaseType,
    AfterSaleStatus,
    AutomationDecision,
    LearningAction,
    LearningEvent,
    MessageIntent,
    Priority,
)
from apps.api.app.domain.repositories import (
    AfterSaleRepository,
    AgentRepository,
    ConnectorRepository,
    CustomerAgentRepository,
    DashboardRepository,
    FeedbackMetricRepository,
    LearningRepository,
)
from apps.api.app.infrastructure.database import (
    AfterSaleCaseRecord,
    AgentFeedbackMetricRecord,
    AgentKpiRecord,
    AgentPromptRecord,
    AgentRecord,
    CompanyRecord,
    ConversationRecord,
    CustomerRecord,
    DailyBusinessSnapshotRecord,
    MessageRecord,
    OrderRecord,
    PlatformConnectionRecord,
)


SessionProvider = Callable[[], Session]


def _num(value: Decimal | float | int | None) -> float:
    return float(value or 0)


def _agent_type(value: str) -> AgentType:
    return cast(AgentType, value)


def _agent_status(value: str) -> AgentStatus:
    return cast(AgentStatus, value)


def _platform(value: str | None) -> ConnectorPlatform:
    return cast(ConnectorPlatform, value or "shopify")


def _message_intent(value: str) -> MessageIntent:
    return cast(MessageIntent, value)


def _automation_decision(value: str) -> AutomationDecision:
    return cast(AutomationDecision, value)


def _after_sale_type(value: str) -> AfterSaleCaseType:
    return cast(AfterSaleCaseType, value)


def _after_sale_status(value: str) -> AfterSaleStatus:
    return cast(AfterSaleStatus, value)


def _priority(value: str) -> Priority:
    return cast(Priority, value)


def _connector_status(value: str) -> ConnectorStatus:
    return cast(ConnectorStatus, value)


def _agent_from_record(session: Session, record: AgentRecord) -> Agent:
    prompt = session.scalar(
        select(AgentPromptRecord)
        .where(AgentPromptRecord.agent_id == record.id)
        .where(AgentPromptRecord.is_active.is_(True))
        .limit(1)
    )
    kpi = session.scalar(select(AgentKpiRecord).where(AgentKpiRecord.agent_id == record.id).limit(1))

    return Agent(
        id=record.slug,
        name=record.name,
        type=_agent_type(record.type),
        status=_agent_status(record.status),
        description=record.description,
        prompt=prompt.content if prompt else "等待配置 Prompt。",
        today_handled_count=0,
        kpi_score=int(_num(kpi.metric_value if kpi else 0)),
        future_tasks=("接入真实平台数据", "接入工作流程引擎（Workflow Engine）", "接入学习闭环"),
    )


class PostgresDashboardRepository(DashboardRepository):
    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider

    async def get_today_summary(self) -> DashboardSummary:
        with self.session_provider() as session:
            snapshot = session.scalar(select(DailyBusinessSnapshotRecord).limit(1))
            agents = tuple(_agent_from_record(session, item) for item in session.scalars(select(AgentRecord)).all())

            metrics = (
                DashboardMetric("sales", "今日销售", f"¥{_num(snapshot.sales_amount if snapshot else 0):,.0f}", "来自 Supabase 数据库"),
                DashboardMetric("profit", "今日利润", f"¥{_num(snapshot.profit_amount if snapshot else 0):,.0f}", "来自 Supabase 数据库"),
                DashboardMetric("inventory", "库存风险", f"{snapshot.inventory_risk_count if snapshot else 0} 个 SKU", "低于安全库存需关注"),
                DashboardMetric("refunds", "退款异常", f"{snapshot.refund_count if snapshot else 0} 单", "售后任务待处理"),
            )

            return DashboardSummary(
                date=datetime.now(timezone.utc).date().isoformat(),
                pending_approval_count=snapshot.pending_approval_count if snapshot else 0,
                metrics=metrics,
                agents=agents,
                suggestions=(
                    DashboardSuggestion("db-s1", "检查 AI客服与 AI售后试用数据", "真实数据库已连接后，应优先观察商家修正和售后决策样本。", "high"),
                ),
            )


class PostgresAgentRepository(AgentRepository):
    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider

    async def list_agents(self) -> tuple[Agent, ...]:
        with self.session_provider() as session:
            return tuple(_agent_from_record(session, item) for item in session.scalars(select(AgentRecord)).all())

    async def get_agent(self, agent_id: str) -> Agent | None:
        with self.session_provider() as session:
            record = session.scalar(select(AgentRecord).where(AgentRecord.slug == agent_id).limit(1))
            return _agent_from_record(session, record) if record else None

    async def list_logs(self, agent_id: str) -> tuple[AgentLog, ...]:
        return (
            AgentLog("pg-log-1", agent_id, "info", "已连接 PostgreSQL 仓储。", datetime.now(timezone.utc).isoformat()),
        )


class PostgresCustomerAgentRepository(CustomerAgentRepository):
    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider

    async def list_inbox(self) -> tuple[CustomerInboxItem, ...]:
        with self.session_provider() as session:
            rows = (
                session.query(MessageRecord, ConversationRecord, CustomerRecord, OrderRecord)
                .join(ConversationRecord, MessageRecord.conversation_id == ConversationRecord.id)
                .outerjoin(CustomerRecord, ConversationRecord.customer_id == CustomerRecord.id)
                .outerjoin(OrderRecord, OrderRecord.customer_id == CustomerRecord.id)
                .order_by(MessageRecord.id)
                .limit(50)
                .all()
            )
            return tuple(
                CustomerInboxItem(
                    id=message.id,
                    platform=_platform(message.platform),
                    customer_name=customer.name if customer else "未知客户",
                    channel=conversation.channel,
                    content=message.content,
                    intent=_message_intent(message.intent),
                    order_external_id=order.external_id if order else None,
                    logistics_status=order.status if order else None,
                    confidence=_num(message.confidence),
                    automation_decision=_automation_decision(message.automation_decision),
                    status="needs_human" if message.requires_human_review else "pending",
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
                for message, conversation, customer, order in rows
            )

    async def draft_reply(self, message_id: str) -> DraftReply | None:
        with self.session_provider() as session:
            message = session.get(MessageRecord, message_id)
            if message is None:
                return None

            if message.automation_decision == "human_review":
                return DraftReply(message_id, "这个问题需要商家确认后再回复。", _num(message.confidence), "human_review", "命中人工确认规则。", True)

            return DraftReply(
                message_id,
                message.ai_draft_content or "您好，已收到您的消息，我们会根据订单和物流信息继续为您跟进。",
                _num(message.confidence),
                "auto_reply",
                "属于低风险自动回复范围。",
                False,
            )

    async def mark_sent(self, message_id: str, final_content: str | None = None) -> CustomerInboxItem | None:
        with self.session_provider() as session:
            message = session.get(MessageRecord, message_id)
            if message is None or message.automation_decision == "human_review":
                return None
            message.ai_sent_at = datetime.now(timezone.utc)
            resolved_content = final_content or message.ai_draft_content or message.content
            message.merchant_edited = bool(final_content and final_content != message.ai_draft_content)
            message.final_content = resolved_content
            session.commit()
        inbox = await self.list_inbox()
        return next((item for item in inbox if item.id == message_id), None)

    async def mark_takeover(self, message_id: str) -> CustomerInboxItem | None:
        with self.session_provider() as session:
            message = session.get(MessageRecord, message_id)
            if message is None:
                return None
            message.automation_decision = "human_review"
            message.requires_human_review = True
            session.commit()
        inbox = await self.list_inbox()
        return next((item for item in inbox if item.id == message_id), None)


class PostgresAfterSaleRepository(AfterSaleRepository):
    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider

    async def list_cases(self) -> tuple[AfterSaleCase, ...]:
        with self.session_provider() as session:
            rows = session.scalars(select(AfterSaleCaseRecord).order_by(AfterSaleCaseRecord.id)).all()
            return tuple(self._to_domain(row, session) for row in rows)

    async def get_case(self, case_id: str) -> AfterSaleCase | None:
        with self.session_provider() as session:
            row = session.get(AfterSaleCaseRecord, case_id)
            return self._to_domain(row, session) if row else None

    async def record_decision(self, case_id: str, decision: str, note: str) -> AfterSaleCase | None:
        with self.session_provider() as session:
            row = session.get(AfterSaleCaseRecord, case_id)
            if row is None:
                return None
            row.merchant_decision = decision
            row.merchant_note = note
            row.status = "resolved" if decision in {"approved", "rejected"} else row.status
            session.commit()
            return self._to_domain(row, session)

    def _to_domain(self, row: AfterSaleCaseRecord, session: Session) -> AfterSaleCase:
        customer = session.get(CustomerRecord, row.customer_id) if row.customer_id else None
        order = session.get(OrderRecord, row.order_id) if row.order_id else None
        return AfterSaleCase(
            id=row.id,
            platform=_platform(row.platform),
            case_type=_after_sale_type(row.case_type),
            status=_after_sale_status(row.status),
            customer_name=customer.name if customer else "未知客户",
            order_external_id=order.external_id if order else "未知订单",
            title=row.title,
            description=row.description,
            risk_level=_priority(row.risk_level),
            ai_suggestion=row.ai_suggestion,
            approval_required=row.approval_required,
            created_at=datetime.now(timezone.utc).isoformat(),
        )


class PostgresLearningRepository(LearningRepository):
    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider

    async def record_event(
        self,
        source_type: str,
        source_id: str,
        agent_id: str,
        action: str,
        original_content: str,
        final_content: str,
    ) -> LearningEvent:
        with self.session_provider() as session:
            agent = session.scalar(select(AgentRecord).where(AgentRecord.slug == agent_id).limit(1))
            company_id = agent.company_id if agent else session.scalar(select(CompanyRecord.id).limit(1))
            record = LearningEventRecord(
                id=str(uuid4()),
                company_id=company_id,
                agent_id=agent.id if agent else None,
                source_type=source_type,
                source_id=None,
                action=action,
                original_content=original_content,
                final_content=final_content,
            )
            session.add(record)
            session.commit()
            return LearningEvent(
                record.id,
                source_type,
                source_id,
                agent_id,
                cast(LearningAction, action),
                original_content,
                final_content,
                datetime.now(timezone.utc).isoformat(),
            )


class PostgresFeedbackMetricRepository(FeedbackMetricRepository):
    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider

    async def list_metrics(self) -> tuple[AgentFeedbackMetric, ...]:
        with self.session_provider() as session:
            rows = session.scalars(select(AgentFeedbackMetricRecord)).all()
            return tuple(AgentFeedbackMetric(row.id, row.agent_id or "", row.metric_name, _num(row.metric_value), _num(row.weight)) for row in rows)


class PostgresConnectorRepository(ConnectorRepository):
    def __init__(self, session_provider: SessionProvider) -> None:
        self.session_provider = session_provider

    async def list_statuses(self) -> tuple[ConnectorStatusView, ...]:
        with self.session_provider() as session:
            rows = session.scalars(select(PlatformConnectionRecord)).all()
            return tuple(
                ConnectorStatusView(
                    platform=_platform(row.platform),
                    status=_connector_status(row.status),
                    display_name="Shopify" if row.platform == "shopify" else "淘宝开放平台",
                    scopes=tuple(row.scopes or ()),
                    next_action="已连接，可继续接入 Webhook。" if row.status == "connected" else "继续配置官方授权。",
                )
                for row in rows
            )
