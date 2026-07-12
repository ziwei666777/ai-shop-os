from collections.abc import Iterator
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, Text, create_engine
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from apps.api.app.infrastructure.config import get_settings


class Base(DeclarativeBase):
    pass


agent_type_enum = Enum(
    "boss",
    "customer",
    "operator",
    "after_sale",
    "purchase",
    "logistics",
    "finance",
    "analyst",
    name="agent_type",
    native_enum=True,
    create_constraint=False,
)
agent_status_enum = Enum("online", "paused", "offline", name="agent_status", native_enum=True, create_constraint=False)
connector_platform_enum = Enum(
    "shopify", "taobao", "douyin", "xianyu", name="connector_platform", native_enum=True, create_constraint=False
)
connector_status_enum = Enum("connected", "pending", "not_connected", name="connector_status", native_enum=True, create_constraint=False)
automation_decision_enum = Enum("auto_reply", "human_review", name="automation_decision", native_enum=True, create_constraint=False)
message_intent_enum = Enum(
    "faq",
    "order",
    "logistics",
    "refund",
    "complaint",
    "compensation",
    "unknown",
    name="message_intent",
    native_enum=True,
    create_constraint=False,
)
after_sale_case_type_enum = Enum(
    "refund",
    "return",
    "logistics_issue",
    "complaint",
    "compensation",
    name="after_sale_case_type",
    native_enum=True,
    create_constraint=False,
)
after_sale_status_enum = Enum("open", "waiting_merchant", "resolved", name="after_sale_status", native_enum=True, create_constraint=False)
learning_action_enum = Enum(
    "accepted",
    "edited",
    "rejected",
    "manual_answered",
    name="learning_action",
    native_enum=True,
    create_constraint=False,
)


class CompanyRecord(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    name: Mapped[str] = mapped_column(Text)


class AgentRecord(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"))
    slug: Mapped[str] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(agent_type_enum)
    status: Mapped[str] = mapped_column(agent_status_enum)
    description: Mapped[str] = mapped_column(Text)


class AgentPromptRecord(Base):
    __tablename__ = "agent_prompts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"))
    agent_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id"))
    content: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean)


class AgentKpiRecord(Base):
    __tablename__ = "agent_kpis"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"))
    agent_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id"))
    metric_name: Mapped[str] = mapped_column(Text)
    metric_value: Mapped[float] = mapped_column(Numeric)


class CustomerRecord(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"))
    external_id: Mapped[str | None] = mapped_column(Text)
    name: Mapped[str] = mapped_column(Text)


class OrderRecord(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"))
    customer_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("customers.id"))
    external_id: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    total_amount: Mapped[float] = mapped_column(Numeric)


class ConversationRecord(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"))
    customer_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("customers.id"))
    agent_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id"))
    channel: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)


class MessageRecord(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"))
    conversation_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("conversations.id"))
    sender_type: Mapped[str] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Numeric)
    requires_human_review: Mapped[bool] = mapped_column(Boolean)
    platform: Mapped[str | None] = mapped_column(connector_platform_enum)
    platform_message_id: Mapped[str | None] = mapped_column(Text)
    intent: Mapped[str] = mapped_column(message_intent_enum)
    automation_decision: Mapped[str] = mapped_column(automation_decision_enum)
    ai_draft_content: Mapped[str | None] = mapped_column(Text)
    ai_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    merchant_edited: Mapped[bool] = mapped_column(Boolean)
    final_content: Mapped[str | None] = mapped_column(Text)


class AfterSaleCaseRecord(Base):
    __tablename__ = "after_sale_cases"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"))
    platform: Mapped[str] = mapped_column(connector_platform_enum)
    customer_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("customers.id"))
    order_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("orders.id"))
    agent_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id"))
    case_type: Mapped[str] = mapped_column(after_sale_case_type_enum)
    status: Mapped[str] = mapped_column(after_sale_status_enum)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(Text)
    ai_suggestion: Mapped[str] = mapped_column(Text)
    approval_required: Mapped[bool] = mapped_column(Boolean)
    merchant_decision: Mapped[str | None] = mapped_column(Text)
    merchant_note: Mapped[str | None] = mapped_column(Text)


class LearningEventRecord(Base):
    __tablename__ = "learning_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"))
    agent_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id"))
    source_type: Mapped[str] = mapped_column(Text)
    source_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False))
    action: Mapped[str] = mapped_column(learning_action_enum)
    original_content: Mapped[str] = mapped_column(Text)
    final_content: Mapped[str] = mapped_column(Text)


class PlatformConnectionRecord(Base):
    __tablename__ = "platform_connections"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"))
    platform: Mapped[str] = mapped_column(connector_platform_enum)
    status: Mapped[str] = mapped_column(connector_status_enum)
    shop_identifier: Mapped[str] = mapped_column(Text)
    scopes: Mapped[list[str]] = mapped_column(ARRAY(Text))
    authorization_mode: Mapped[str] = mapped_column(Text, default="service_provider")
    access_token_encrypted: Mapped[str | None] = mapped_column(Text)
    refresh_token_encrypted: Mapped[str | None] = mapped_column(Text)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    refresh_token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    connected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)


class AgentFeedbackMetricRecord(Base):
    __tablename__ = "agent_feedback_metrics"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"))
    agent_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), ForeignKey("agents.id"))
    metric_name: Mapped[str] = mapped_column(Text)
    metric_value: Mapped[float] = mapped_column(Numeric)
    weight: Mapped[float] = mapped_column(Numeric)


class DailyBusinessSnapshotRecord(Base):
    __tablename__ = "daily_business_snapshots"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    company_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("companies.id"))
    sales_amount: Mapped[float] = mapped_column(Numeric)
    profit_amount: Mapped[float] = mapped_column(Numeric)
    order_count: Mapped[int] = mapped_column(Integer)
    refund_count: Mapped[int] = mapped_column(Integer)
    pending_approval_count: Mapped[int] = mapped_column(Integer)
    inventory_risk_count: Mapped[int] = mapped_column(Integer)


def create_session_factory() -> sessionmaker[Session] | None:
    settings = get_settings()
    if not settings.has_database:
        return None

    engine = create_engine(settings.database_url, pool_pre_ping=True)
    return sessionmaker(bind=engine, expire_on_commit=False)


SessionFactory = create_session_factory()


def get_session() -> Iterator[Session]:
    if SessionFactory is None:
        raise RuntimeError("DATABASE_URL 未配置，无法使用 PostgreSQL 仓储。")

    with SessionFactory() as session:
        yield session
