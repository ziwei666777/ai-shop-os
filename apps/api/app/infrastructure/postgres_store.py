from collections.abc import Callable
from datetime import datetime, timezone
from decimal import Decimal
from typing import cast
from uuid import uuid4

from sqlalchemy import select, text
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
from apps.api.app.infrastructure.customer_reply_engine import build_customer_draft_reply


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

    async def ingest_message(
        self,
        company_id: str,
        platform: str,
        platform_message_id: str,
        customer_name: str,
        content: str,
        channel: str,
        customer_external_id: str | None = None,
        order_external_id: str | None = None,
    ) -> CustomerInboxItem:
        intent, decision, confidence = _classify_customer_message(content)
        requires_human = decision == "human_review"
        with self.session_provider() as session:
            connection_id = _ensure_bridge_connection(session, company_id, platform)
            customer_id = _ensure_bridge_customer(
                session,
                company_id,
                platform,
                connection_id,
                customer_external_id or f"bridge:{platform}:{customer_name}",
                customer_name,
            )
            order_row = None
            if order_external_id:
                order_row = session.execute(
                    text("""
                      select id::text, status
                      from orders
                      where company_id=:company_id
                        and platform_connection_id=:connection_id
                        and external_id=:external_id
                      limit 1
                    """),
                    {"company_id": company_id, "connection_id": connection_id, "external_id": order_external_id},
                ).mappings().one_or_none()
            conversation_id = str(uuid4())
            session.execute(
                text("""
                  insert into conversations (id, company_id, customer_id, agent_id, channel, status)
                  values (:id, :company_id, :customer_id, null, :channel, 'open')
                """),
                {"id": conversation_id, "company_id": company_id, "customer_id": customer_id, "channel": channel},
            )
            message_id = str(uuid4())
            row = session.execute(
                text("""
                  insert into messages (
                    id, company_id, conversation_id, sender_type, content, confidence, requires_human_review,
                    platform, platform_message_id, intent, automation_decision, merchant_edited
                  ) values (
                    :id, :company_id, :conversation_id, 'customer', :content, :confidence, :requires_human,
                    cast(:platform as connector_platform), :platform_message_id, cast(:intent as message_intent),
                    cast(:decision as automation_decision), false
                  )
                  on conflict (company_id, platform, platform_message_id)
                    where platform_message_id is not null
                  do update set
                    content=excluded.content,
                    confidence=excluded.confidence,
                    requires_human_review=excluded.requires_human_review,
                    intent=excluded.intent,
                    automation_decision=excluded.automation_decision,
                    updated_at=now()
                  returning id::text, created_at::text
                """),
                {
                    "id": message_id,
                    "company_id": company_id,
                    "conversation_id": conversation_id,
                    "content": content,
                    "confidence": confidence,
                    "requires_human": requires_human,
                    "platform": platform,
                    "platform_message_id": platform_message_id,
                    "intent": intent,
                    "decision": decision,
                },
            ).mappings().one()
            session.commit()
            return CustomerInboxItem(
                id=str(row["id"]),
                platform=_platform(platform),
                customer_name=customer_name,
                channel=channel,
                content=content,
                intent=_message_intent(intent),
                order_external_id=order_external_id,
                logistics_status=str(order_row["status"]) if order_row else None,
                confidence=confidence,
                automation_decision=_automation_decision(decision),
                status="needs_human" if requires_human else "pending",
                created_at=str(row["created_at"]),
            )

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

            conversation = session.get(ConversationRecord, message.conversation_id)
            order = None
            if conversation and conversation.customer_id:
                order = session.scalar(
                    select(OrderRecord)
                    .where(OrderRecord.customer_id == conversation.customer_id)
                    .order_by(OrderRecord.updated_at.desc())
                    .limit(1)
                )

            return build_customer_draft_reply(
                message_id=message_id,
                content=message.content,
                confidence=_num(message.confidence),
                automation_decision=message.automation_decision,
                intent=message.intent,
                order_external_id=order.external_id if order else None,
                logistics_status=order.status if order else None,
                company_id=message.company_id,
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


def _ensure_bridge_connection(session: Session, company_id: str, platform: str) -> str:
    row = session.execute(
        text("""
          select id::text
          from platform_connections
          where company_id=:company_id and platform::text=:platform and shop_identifier='external-message-bridge'
          limit 1
        """),
        {"company_id": company_id, "platform": platform},
    ).scalar_one_or_none()
    if row:
        return str(row)
    connection_id = str(uuid4())
    session.execute(
        text("""
          insert into platform_connections (id, company_id, platform, status, shop_identifier, scopes, authorization_mode)
          values (:id, :company_id, cast(:platform as connector_platform), 'connected',
                  'external-message-bridge', array['message_ingest'], 'external_bridge')
        """),
        {"id": connection_id, "company_id": company_id, "platform": platform},
    )
    return connection_id


def _ensure_bridge_customer(
    session: Session,
    company_id: str,
    platform: str,
    connection_id: str,
    external_id: str,
    name: str,
) -> str:
    row = session.execute(
        text("""
          select id::text
          from customers
          where company_id=:company_id and platform_connection_id=:connection_id and external_id=:external_id
          limit 1
        """),
        {"company_id": company_id, "connection_id": connection_id, "external_id": external_id},
    ).scalar_one_or_none()
    if row:
        session.execute(
            text("update customers set name=:name, updated_at=now() where id=:id"),
            {"id": row, "name": name},
        )
        return str(row)
    customer_id = str(uuid4())
    session.execute(
        text("""
          insert into customers (id, company_id, platform_connection_id, platform, external_id, name, source_metadata)
          values (:id, :company_id, :connection_id, cast(:platform as connector_platform), :external_id, :name,
                  '{"source":"external_message_bridge"}'::jsonb)
        """),
        {"id": customer_id, "company_id": company_id, "connection_id": connection_id, "platform": platform, "external_id": external_id, "name": name},
    )
    return customer_id


def _classify_customer_message(content: str) -> tuple[str, str, float]:
    # 真实接入先保守：有钱、有投诉、有退款风险的消息必须人工确认，避免 AI 乱承诺。
    if any(keyword in content for keyword in ("退款", "退货", "赔", "补偿", "投诉", "差评", "金额", "便宜点")):
        return "compensation", "human_review", 0.68
    if any(keyword in content for keyword in ("物流", "快递", "发货", "到哪", "单号")):
        return "logistics", "auto_reply", 0.88
    if any(keyword in content for keyword in ("订单", "下单", "付款", "拍下")):
        return "order", "auto_reply", 0.86
    if any(keyword in content for keyword in ("尺码", "颜色", "库存", "有没有", "适合")):
        return "faq", "auto_reply", 0.84
    return "unknown", "human_review", 0.55


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
