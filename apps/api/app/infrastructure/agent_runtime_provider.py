from functools import lru_cache

from apps.api.app.domain.agent_routing import AgentWorkflow
from apps.api.app.infrastructure.langgraph_workflow import LangGraphAgentWorkflow


@lru_cache(maxsize=1)
def agent_workflow() -> AgentWorkflow:
    return LangGraphAgentWorkflow()
