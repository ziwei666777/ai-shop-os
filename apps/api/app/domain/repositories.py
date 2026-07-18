from abc import ABC, abstractmethod

from apps.api.app.domain.live_operations import LivePostReviewReport, LiveWorkflowReport, LiveWorkflowRun
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


class DashboardRepository(ABC):
    @abstractmethod
    async def get_today_summary(self) -> DashboardSummary:
        """读取老板首页摘要，具体数据源由基础设施层决定。"""


class AgentRepository(ABC):
    @abstractmethod
    async def list_agents(self) -> tuple[Agent, ...]:
        """读取 AI 员工列表。"""

    @abstractmethod
    async def get_agent(self, agent_id: str) -> Agent | None:
        """按标识读取单个 AI 员工。"""

    @abstractmethod
    async def list_logs(self, agent_id: str) -> tuple[AgentLog, ...]:
        """读取 AI 员工日志。"""


class CustomerAgentRepository(ABC):
    @abstractmethod
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
        """接收真实平台或桥接工具推送的客户消息，统一进入 AI 客服收件箱。"""

    @abstractmethod
    async def list_inbox(self) -> tuple[CustomerInboxItem, ...]:
        """读取平台消息收件箱。"""

    @abstractmethod
    async def draft_reply(self, message_id: str) -> DraftReply | None:
        """生成可审计的 AI 回复草稿。"""

    @abstractmethod
    async def mark_sent(self, message_id: str, final_content: str | None = None) -> CustomerInboxItem | None:
        """记录消息已发送，真实平台发送由 Connector 负责。"""

    @abstractmethod
    async def mark_takeover(self, message_id: str) -> CustomerInboxItem | None:
        """记录人工接管，避免 AI 继续自动处理。"""


class AfterSaleRepository(ABC):
    @abstractmethod
    async def list_cases(self) -> tuple[AfterSaleCase, ...]:
        """读取售后任务列表。"""

    @abstractmethod
    async def get_case(self, case_id: str) -> AfterSaleCase | None:
        """读取售后任务详情。"""

    @abstractmethod
    async def record_decision(self, case_id: str, decision: str, note: str) -> AfterSaleCase | None:
        """记录商家对 AI 售后建议的处理结果。"""


class LearningRepository(ABC):
    @abstractmethod
    async def record_event(
        self,
        source_type: str,
        source_id: str,
        agent_id: str,
        action: str,
        original_content: str,
        final_content: str,
    ) -> LearningEvent:
        """记录商家修正、采纳或拒绝，用于后续学习。"""


class FeedbackMetricRepository(ABC):
    @abstractmethod
    async def list_metrics(self) -> tuple[AgentFeedbackMetric, ...]:
        """读取商家试用阶段的核心反馈指标。"""


class ConnectorRepository(ABC):
    @abstractmethod
    async def list_statuses(self) -> tuple[ConnectorStatusView, ...]:
        """读取平台连接状态。"""

class LiveWorkflowRunRepository(ABC):
    @abstractmethod
    def record_live_workflow_report(self, workflow_name: str, report: LiveWorkflowReport, input_snapshot: dict | None = None) -> LiveWorkflowRun:
        """记录直播 Workflow 执行结果，用于证明 AI 做了哪些工作、节省了多少钱。"""

    @abstractmethod
    def record_post_live_review(self, workflow_name: str, report: LivePostReviewReport, input_snapshot: dict | None = None) -> LiveWorkflowRun:
        """记录下播复盘结果，让复盘也进入 Savings Engine 统计。"""

    @abstractmethod
    def list_runs(self, limit: int = 50) -> tuple[LiveWorkflowRun, ...]:
        """按最新在前读取直播 Workflow 日志。"""

    @abstractmethod
    def summarize(self) -> dict[str, int | float | str]:
        """给 Savings Engine 提供聚合后的节省时间和金额。"""

    @abstractmethod
    def clear_for_test(self) -> None:
        """测试时清空日志，生产实现不得暴露给普通业务入口。"""