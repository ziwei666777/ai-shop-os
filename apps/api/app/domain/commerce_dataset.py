from dataclasses import dataclass
from typing import Literal


DatasetKind = Literal["products", "orders", "customers", "messages", "after_sales", "shipments"]


@dataclass(frozen=True)
class DatasetReadinessItem:
    kind: DatasetKind
    label: str
    record_count: int
    readiness: int
    replay_ready: bool
    owner: str
    missing_reason: str | None


@dataclass(frozen=True)
class CommerceDatasetReadiness:
    average_readiness: int
    replay_ready_count: int
    total_kinds: int
    estimated_replay_cases: int
    items: tuple[DatasetReadinessItem, ...]
    next_actions: tuple[str, ...]

