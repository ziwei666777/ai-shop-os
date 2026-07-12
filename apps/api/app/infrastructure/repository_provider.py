from sqlalchemy.orm import Session

from apps.api.app.infrastructure.database import SessionFactory
from apps.api.app.infrastructure.memory_store import (
    MemoryAfterSaleRepository,
    MemoryAgentRepository,
    MemoryConnectorRepository,
    MemoryCustomerAgentRepository,
    MemoryDashboardRepository,
    MemoryFeedbackMetricRepository,
    MemoryLearningRepository,
)
from apps.api.app.infrastructure.postgres_store import (
    PostgresAfterSaleRepository,
    PostgresAgentRepository,
    PostgresConnectorRepository,
    PostgresCustomerAgentRepository,
    PostgresDashboardRepository,
    PostgresFeedbackMetricRepository,
    PostgresLearningRepository,
)


def _session() -> Session:
    if SessionFactory is None:
        raise RuntimeError("DATABASE_URL 未配置。")
    return SessionFactory()


def dashboard_repository():
    return PostgresDashboardRepository(_session) if SessionFactory else MemoryDashboardRepository()


def agent_repository():
    return PostgresAgentRepository(_session) if SessionFactory else MemoryAgentRepository()


def customer_agent_repository():
    return PostgresCustomerAgentRepository(_session) if SessionFactory else MemoryCustomerAgentRepository()


def after_sale_repository():
    return PostgresAfterSaleRepository(_session) if SessionFactory else MemoryAfterSaleRepository()


def learning_repository():
    return PostgresLearningRepository(_session) if SessionFactory else MemoryLearningRepository()


def feedback_metric_repository():
    return PostgresFeedbackMetricRepository(_session) if SessionFactory else MemoryFeedbackMetricRepository()


def connector_repository():
    return PostgresConnectorRepository(_session) if SessionFactory else MemoryConnectorRepository()
