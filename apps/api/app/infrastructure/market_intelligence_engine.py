from __future__ import annotations

from statistics import median

from apps.api.app.domain.market_intelligence import MarketIntelligenceReport, PublicMarketSignal


def analyze_public_market_signals(signals: tuple[PublicMarketSignal, ...]) -> MarketIntelligenceReport:
    if not signals:
        raise ValueError("At least one public market signal is required.")
    categories = {signal.category for signal in signals}
    if len(categories) != 1:
        raise ValueError("All public market signals must describe one category.")

    prices = sorted(signal.price_yuan for signal in signals)
    sentiment_score = sum({"positive": 10, "neutral": 0, "negative": -12}[signal.review_sentiment] for signal in signals)
    engagement_score = round(sum(signal.engagement_score for signal in signals) / len(signals))
    opportunity_score = _clamp(45 + engagement_score // 2 + sentiment_score)
    risk_score = _clamp(70 - engagement_score // 2 - sentiment_score)
    category = next(iter(categories))
    median_price = round(float(median(prices)), 2)
    recommendation = _recommendation(category, opportunity_score, risk_score, median_price)
    sources = tuple(f"{signal.source_name}: {signal.source_url}" for signal in signals)

    return MarketIntelligenceReport(
        category=category,
        data_status="public_market_signal",
        data_status_reason="Public market signals guide selection and live-operation hypotheses; they do not represent a merchant's orders, inventory, profit, refunds, or ROI.",
        source_count=len(signals),
        price_floor_yuan=round(prices[0], 2),
        price_ceiling_yuan=round(prices[-1], 2),
        median_price_yuan=median_price,
        opportunity_score=opportunity_score,
        risk_score=risk_score,
        recommendation=recommendation,
        next_actions=(
            "Use the public price band to prepare a live product-positioning hypothesis.",
            "Validate demand, inventory, margin, and refund risk with merchant evidence before any price or stock action.",
        ),
        proof_points=(
            f"Analyzed {len(signals)} public signals for {category}.",
            f"Public price band: {prices[0]:.2f}-{prices[-1]:.2f} yuan; median {median_price:.2f} yuan.",
            *sources,
        ),
        merchant_roi_eligible=False,
        replaced_role="选品/竞品运营助理",
        estimated_saved_minutes=20,
    )


def _recommendation(category: str, opportunity_score: int, risk_score: int, median_price: float) -> str:
    if opportunity_score >= 70 and risk_score <= 35:
        return f"{category} has a strong public-market signal. Test a differentiated live offer near {median_price:.2f} yuan after merchant margin validation."
    if risk_score >= 60:
        return f"{category} has public demand uncertainty or negative feedback. Do not change live pricing until merchant-side quality and return evidence is available."
    return f"{category} warrants a controlled content and price-positioning test near {median_price:.2f} yuan; confirm merchant economics before execution."


def _clamp(value: int) -> int:
    return max(0, min(100, value))