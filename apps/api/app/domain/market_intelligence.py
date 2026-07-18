from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


PublicSignalKind = Literal["official_ranking", "public_listing", "public_content"]


@dataclass(frozen=True)
class PublicMarketSignal:
    source_name: str
    source_url: str
    observed_at: str
    signal_kind: PublicSignalKind
    platform: str
    category: str
    product_name: str
    price_yuan: float
    engagement_score: int
    review_sentiment: Literal["positive", "neutral", "negative"]


@dataclass(frozen=True)
class MarketIntelligenceReport:
    category: str
    data_status: Literal["public_market_signal"]
    data_status_reason: str
    source_count: int
    price_floor_yuan: float
    price_ceiling_yuan: float
    median_price_yuan: float
    opportunity_score: int
    risk_score: int
    recommendation: str
    next_actions: tuple[str, ...]
    proof_points: tuple[str, ...]
    merchant_roi_eligible: bool
    replaced_role: str
    estimated_saved_minutes: int