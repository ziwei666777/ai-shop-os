from fastapi.testclient import TestClient

from apps.api.app.main import app


def test_market_intelligence_analyzes_public_sources_without_claiming_merchant_roi() -> None:
    response = TestClient(app).post(
        "/v1/market-intelligence/analyze",
        json={
            "signals": [
                {
                    "source_name": "Public product listing A",
                    "source_url": "https://example.com/listing-a",
                    "observed_at": "2026-07-18T08:00:00+00:00",
                    "signal_kind": "public_listing",
                    "platform": "public-web",
                    "category": "wireless earbuds",
                    "product_name": "Earbuds A",
                    "price_yuan": 129,
                    "engagement_score": 78,
                    "review_sentiment": "positive",
                },
                {
                    "source_name": "Public product listing B",
                    "source_url": "https://example.com/listing-b",
                    "observed_at": "2026-07-18T08:10:00+00:00",
                    "signal_kind": "public_listing",
                    "platform": "public-web",
                    "category": "wireless earbuds",
                    "product_name": "Earbuds B",
                    "price_yuan": 159,
                    "engagement_score": 66,
                    "review_sentiment": "neutral",
                },
            ]
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["data_status"] == "public_market_signal"
    assert body["merchant_roi_eligible"] is False
    assert body["source_count"] == 2
    assert body["median_price_yuan"] == 144
    assert body["replaced_role"] == "选品/竞品运营助理"
    assert any("https://example.com/listing-a" in item for item in body["proof_points"])


def test_market_intelligence_rejects_mixed_categories() -> None:
    response = TestClient(app).post(
        "/v1/market-intelligence/analyze",
        json={
            "signals": [
                {
                    "source_name": "Source A",
                    "source_url": "https://example.com/a",
                    "observed_at": "2026-07-18T08:00:00+00:00",
                    "signal_kind": "public_listing",
                    "platform": "public-web",
                    "category": "wireless earbuds",
                    "product_name": "Earbuds A",
                    "price_yuan": 129,
                    "engagement_score": 50,
                    "review_sentiment": "neutral",
                },
                {
                    "source_name": "Source B",
                    "source_url": "https://example.com/b",
                    "observed_at": "2026-07-18T08:10:00+00:00",
                    "signal_kind": "public_listing",
                    "platform": "public-web",
                    "category": "portable fans",
                    "product_name": "Fan B",
                    "price_yuan": 79,
                    "engagement_score": 50,
                    "review_sentiment": "neutral",
                },
            ]
        },
    )

    assert response.status_code == 400
    assert "one category" in response.json()["detail"]