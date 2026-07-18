from apps.api.app.domain.ceo_report import CeoDailyReport
from apps.api.app.domain.daily_operations import DailyOperationsRun
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
from apps.api.app.domain.replay import ReplaySummary
from apps.api.app.domain.repositories import (
    AfterSaleRepository,
    AgentRepository,
    ConnectorRepository,
    CustomerAgentRepository,
    DashboardRepository,
    FeedbackMetricRepository,
    LearningRepository,
)
from apps.api.app.domain.validation import EvaluationSummary, SimulationSummary, TrainingCenterSummary
from apps.api.app.domain.live_operations import LiveOperationSummary, SavingsSummary


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


class IngestCustomerMessage:
    def __init__(self, repository: CustomerAgentRepository) -> None:
        self.repository = repository

    async def execute(
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
        return await self.repository.ingest_message(
            company_id,
            platform,
            platform_message_id,
            customer_name,
            content,
            channel,
            customer_external_id,
            order_external_id,
        )


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


class RunReplaySummary:
    def __init__(self, runner) -> None:
        self.runner = runner

    async def execute(self) -> ReplaySummary:
        return self.runner()


class RunEvaluationSummary:
    def __init__(self, runner) -> None:
        self.runner = runner

    async def execute(self) -> EvaluationSummary:
        return self.runner()


class GetTrainingCenterSummary:
    def __init__(self, reader) -> None:
        self.reader = reader

    async def execute(self) -> TrainingCenterSummary:
        return self.reader()


class RunSimulationSummary:
    def __init__(self, runner) -> None:
        self.runner = runner

    async def execute(self) -> SimulationSummary:
        return self.runner()


class GetLiveOperationSummary:
    def __init__(self, reader) -> None:
        self.reader = reader

    async def execute(self) -> LiveOperationSummary:
        return self.reader()


class GetSavingsSummary:
    def __init__(self, reader) -> None:
        self.reader = reader

    async def execute(self) -> SavingsSummary:
        return self.reader()

class GetCeoDailyReport:
    def __init__(self, reader) -> None:
        self.reader = reader

    async def execute(self) -> CeoDailyReport:
        return self.reader()

class RunDailyOperations:
    def __init__(self, runner) -> None:
        self.runner = runner

    async def execute(self, **kwargs) -> DailyOperationsRun:
        return self.runner(**kwargs)
