from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


AgentEventType = Literal["customer_message", "after_sale_case", "operation_scan", "daily_business_review"]
AgentRoute = Literal["ai-customer", "ai-after-sale", "ai-operator", "ai-boss"]


@dataclass(frozen=True)
class AgentRoutingInput:
    source_id: str
    event_type: AgentEventType
    intent: str
    confidence: float


@dataclass(frozen=True)
class AgentRoutingDecision:
    source_id: str
    assigned_agent: AgentRoute
    requires_approval: bool
    reason: str
    trace: tuple[str, ...]


class AgentWorkflow(ABC):
    @abstractmethod
    def route(self, routing_input: AgentRoutingInput) -> AgentRoutingDecision:
        """通过工作流程路由事件，AI 员工之间不得直接互相调用。"""
