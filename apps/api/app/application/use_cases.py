from apps.api.app.domain.models import (
    AfterSaleCase,
    Agent,
    AgentFeedbackMetric,
    AgentLog,
    ConnectorStatusView,
    CustomerInboxItem,
    DashboardSummary,
    DraftReply,
    LearningEvent,
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


class GetDashboardSummary:
    def __init__(self, repository: DashboardRepository) -> None:
        self.repository = repository

    async def execute(self) -> DashboardSummary:
        return await self.repository.get_today_summary()


class ListAgents:
    def __init__(self, repository: AgentRepository) -> None:
        self.repository = repository

    async def execute(self) -> tuple[Agent, ...]:
        return await self.repository.list_agents()


class GetAgent:
    def __init__(self, repository: AgentRepository) -> None:
        self.repository = repository

    async def execute(self, agent_id: str) -> Agent | None:
        return await self.repository.get_agent(agent_id)


class ListAgentLogs:
    def __init__(self, repository: AgentRepository) -> None:
        self.repository = repository

    async def execute(self, agent_id: str) -> tuple[AgentLog, ...]:
        return await self.repository.list_logs(agent_id)


class ListCustomerInbox:
    def __init__(self, repository: CustomerAgentRepository) -> None:
        self.repository = repository

    async def execute(self) -> tuple[CustomerInboxItem, ...]:
        return await self.repository.list_inbox()


class DraftCustomerReply:
    def __init__(self, repository: CustomerAgentRepository) -> None:
        self.repository = repository

    async def execute(self, message_id: str) -> DraftReply | None:
        return await self.repository.draft_reply(message_id)


class SendCustomerReply:
    def __init__(self, repository: CustomerAgentRepository) -> None:
        self.repository = repository

    async def execute(self, message_id: str, final_content: str | None = None) -> CustomerInboxItem | None:
        return await self.repository.mark_sent(message_id, final_content)


class TakeoverCustomerMessage:
    def __init__(self, repository: CustomerAgentRepository) -> None:
        self.repository = repository

    async def execute(self, message_id: str) -> CustomerInboxItem | None:
        return await self.repository.mark_takeover(message_id)


class ListAfterSaleCases:
    def __init__(self, repository: AfterSaleRepository) -> None:
        self.repository = repository

    async def execute(self) -> tuple[AfterSaleCase, ...]:
        return await self.repository.list_cases()


class GetAfterSaleCase:
    def __init__(self, repository: AfterSaleRepository) -> None:
        self.repository = repository

    async def execute(self, case_id: str) -> AfterSaleCase | None:
        return await self.repository.get_case(case_id)


class DecideAfterSaleCase:
    def __init__(self, repository: AfterSaleRepository) -> None:
        self.repository = repository

    async def execute(self, case_id: str, decision: str, note: str) -> AfterSaleCase | None:
        return await self.repository.record_decision(case_id, decision, note)


class RecordLearningEvent:
    def __init__(self, repository: LearningRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        source_type: str,
        source_id: str,
        agent_id: str,
        action: str,
        original_content: str,
        final_content: str,
    ) -> LearningEvent:
        return await self.repository.record_event(
            source_type,
            source_id,
            agent_id,
            action,
            original_content,
            final_content,
        )


class ListFeedbackMetrics:
    def __init__(self, repository: FeedbackMetricRepository) -> None:
        self.repository = repository

    async def execute(self) -> tuple[AgentFeedbackMetric, ...]:
        return await self.repository.list_metrics()


class ListConnectorStatuses:
    def __init__(self, repository: ConnectorRepository) -> None:
        self.repository = repository

    async def execute(self) -> tuple[ConnectorStatusView, ...]:
        return await self.repository.list_statuses()
