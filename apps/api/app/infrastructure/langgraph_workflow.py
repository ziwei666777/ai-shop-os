from typing import NotRequired, TypedDict, cast

try:
    from langgraph.graph import END, START, StateGraph
except ModuleNotFoundError:
    END = START = None
    StateGraph = None

from apps.api.app.domain.agent_routing import (
    AgentRoute,
    AgentRoutingDecision,
    AgentRoutingInput,
    AgentWorkflow,
)


class AgentWorkflowState(TypedDict):
    source_id: str
    event_type: str
    intent: str
    confidence: float
    route: NotRequired[AgentRoute]
    requires_approval: NotRequired[bool]
    reason: NotRequired[str]
    trace: list[str]


HIGH_RISK_INTENTS = {"refund", "return", "complaint", "compensation", "logistics_issue"}


class LangGraphAgentWorkflow(AgentWorkflow):
    def __init__(self) -> None:
        if StateGraph is None:
            self._graph = None
            return

        builder = StateGraph(AgentWorkflowState)
        builder.add_node("识别事件", self._classify_event)
        builder.add_node("AI客服", self._assign_customer)
        builder.add_node("AI售后", self._assign_after_sale)
        builder.add_node("AI运营", self._assign_operation)
        builder.add_node("AI老板", self._assign_boss)
        builder.add_node("审批策略", self._apply_approval_policy)
        builder.add_edge(START, "识别事件")
        builder.add_conditional_edges(
            "识别事件",
            self._select_route,
            {
                "ai-customer": "AI客服",
                "ai-after-sale": "AI售后",
                "ai-operator": "AI运营",
                "ai-boss": "AI老板",
            },
        )
        for node in ("AI客服", "AI售后", "AI运营", "AI老板"):
            builder.add_edge(node, "审批策略")
        builder.add_edge("审批策略", END)
        self._graph = builder.compile()

    def route(self, routing_input: AgentRoutingInput) -> AgentRoutingDecision:
        initial_state = AgentWorkflowState(
            source_id=routing_input.source_id,
            event_type=routing_input.event_type,
            intent=routing_input.intent,
            confidence=routing_input.confidence,
            trace=[],
        )
        state = self._graph.invoke(initial_state) if self._graph is not None else self._run_local_fallback(initial_state)
        return AgentRoutingDecision(
            source_id=state["source_id"],
            assigned_agent=cast(AgentRoute, state["route"]),
            requires_approval=state["requires_approval"],
            reason=state["reason"],
            trace=tuple(state["trace"]),
        )

    def _run_local_fallback(self, initial_state: AgentWorkflowState) -> AgentWorkflowState:
        state = cast(AgentWorkflowState, {**initial_state, **self._classify_event(initial_state)})
        route = self._select_route(state)
        assignment = {
            "ai-customer": self._assign_customer,
            "ai-after-sale": self._assign_after_sale,
            "ai-operator": self._assign_operation,
            "ai-boss": self._assign_boss,
        }[route](state)
        state = cast(AgentWorkflowState, {**state, **assignment})
        return cast(AgentWorkflowState, {**state, **self._apply_approval_policy(state)})

    @staticmethod
    def _classify_event(state: AgentWorkflowState) -> dict[str, object]:
        return {"trace": [*state["trace"], "工作流程已识别事件"]}

    @staticmethod
    def _select_route(state: AgentWorkflowState) -> AgentRoute:
        if state["event_type"] == "operation_scan":
            return "ai-operator"
        if state["event_type"] == "daily_business_review":
            return "ai-boss"
        if state["event_type"] == "after_sale_case" or state["intent"] in HIGH_RISK_INTENTS:
            return "ai-after-sale"
        if state["confidence"] < 0.75 or state["intent"] == "unknown":
            return "ai-boss"
        return "ai-customer"

    @staticmethod
    def _assign_customer(state: AgentWorkflowState) -> dict[str, object]:
        return {
            "route": "ai-customer",
            "reason": "低风险售前问题由 AI 客服处理。",
            "trace": [*state["trace"], "事件已分配给 AI 客服"],
        }

    @staticmethod
    def _assign_after_sale(state: AgentWorkflowState) -> dict[str, object]:
        return {
            "route": "ai-after-sale",
            "reason": "售后或高风险问题由 AI 售后处理，并保留老板审批权。",
            "trace": [*state["trace"], "事件已分配给 AI 售后"],
        }

    @staticmethod
    def _assign_operation(state: AgentWorkflowState) -> dict[str, object]:
        return {
            "route": "ai-operator",
            "reason": "平台扫描和经营分析任务由 AI 运营处理。",
            "trace": [*state["trace"], "事件已分配给 AI 运营"],
        }

    @staticmethod
    def _assign_boss(state: AgentWorkflowState) -> dict[str, object]:
        return {
            "route": "ai-boss",
            "reason": "低置信度、未知问题或老板经营事件由 AI 老板接管。",
            "trace": [*state["trace"], "事件已升级给 AI 老板"],
        }

    @staticmethod
    def _apply_approval_policy(state: AgentWorkflowState) -> dict[str, object]:
        requires_approval = state["route"] in {"ai-after-sale", "ai-boss"}
        approval_trace = "需要老板审批" if requires_approval else "无需老板审批"
        return {
            "requires_approval": requires_approval,
            "trace": [*state["trace"], approval_trace],
        }
