from apps.api.app.domain.agent_routing import AgentRoutingDecision, AgentRoutingInput, AgentWorkflow


class RouteAgentEvent:
    def __init__(self, workflow: AgentWorkflow) -> None:
        self.workflow = workflow

    def execute(self, routing_input: AgentRoutingInput) -> AgentRoutingDecision:
        return self.workflow.route(routing_input)
