from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


StrategyStatus = Literal["done", "in_progress", "gap"]
StrategyPriority = Literal["P0", "P1", "P2"]


@dataclass(frozen=True)
class StrategyCapability:
    id: str
    priority: StrategyPriority
    name: str
    status: StrategyStatus
    score: int
    proof: str
    gap: str
    next_action: str
    replaced_role: str
    daily_saved_minutes: int


@dataclass(frozen=True)
class StrategyAudit:
    positioning: str
    focus: str
    overall_score: int
    completed_count: int
    gap_count: int
    estimated_daily_saved_minutes: int
    estimated_daily_saved_yuan: int
    stop_doing: tuple[str, ...]
    capabilities: tuple[StrategyCapability, ...]
    next_p0_actions: tuple[str, ...]
