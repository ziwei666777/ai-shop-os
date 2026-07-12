from fastapi.testclient import TestClient

from apps.api.app.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard_summary_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/v1/dashboard/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["pending_approval_count"] == 3
    assert body["agents"][0]["id"] == "ai-boss"


def test_agent_detail_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/v1/agents/ai-customer")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "customer"
    assert "禁止编造答案" in body["prompt"]


def test_shopify_webhook_requires_valid_signature() -> None:
    client = TestClient(app)

    rejected = client.post("/v1/webhooks/shopify", content=b"{}", headers={"x-shopify-hmac-sha256": "bad"})
    accepted = client.post("/v1/webhooks/shopify", content=b"{}", headers={"x-shopify-hmac-sha256": "dev-valid-signature"})

    assert rejected.status_code == 401
    assert accepted.status_code == 200
    assert accepted.json()["accepted"] is True


def test_customer_agent_low_risk_draft_and_high_risk_block() -> None:
    client = TestClient(app)

    low_risk = client.post("/v1/customer-agent/messages/msg-2/draft-reply")
    low_risk_send = client.post(
        "/v1/customer-agent/messages/msg-2/send",
        json={"content": "您好，物流状态已更新，我会继续为您跟进。"},
    )
    high_risk_send = client.post("/v1/customer-agent/messages/msg-3/send")

    assert low_risk.status_code == 200
    assert low_risk.json()["automation_decision"] == "auto_reply"
    assert low_risk_send.status_code == 200
    assert low_risk_send.json()["status"] == "sent"
    assert high_risk_send.status_code == 409


def test_after_sale_case_requires_approval_and_learning_event_records() -> None:
    client = TestClient(app)

    case_response = client.get("/v1/after-sale/cases/case-2")
    learning_response = client.post(
        "/v1/learning-events",
        json={
            "source_type": "message",
            "source_id": "msg-3",
            "agent_id": "ai-customer",
            "action": "edited",
            "original_content": "需要赔偿",
            "final_content": "已收到反馈，我们会先核实图片和订单信息。",
        },
    )

    assert case_response.status_code == 200
    assert case_response.json()["approval_required"] is True
    assert learning_response.status_code == 200
    assert learning_response.json()["action"] == "edited"


def test_agent_runtime_routes_low_risk_message_to_customer_agent() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/agent-runtime/route",
        json={"source_id": "msg-routing-1", "event_type": "customer_message", "intent": "faq", "confidence": 0.92},
    )

    assert response.status_code == 200
    assert response.json()["assigned_agent"] == "ai-customer"
    assert response.json()["requires_approval"] is False


def test_agent_runtime_routes_high_risk_and_unknown_events_safely() -> None:
    client = TestClient(app)

    after_sale = client.post(
        "/v1/agent-runtime/route",
        json={"source_id": "case-routing-1", "event_type": "customer_message", "intent": "refund", "confidence": 0.9},
    )
    unknown = client.post(
        "/v1/agent-runtime/route",
        json={"source_id": "msg-routing-2", "event_type": "customer_message", "intent": "unknown", "confidence": 0.3},
    )

    assert after_sale.json()["assigned_agent"] == "ai-after-sale"
    assert after_sale.json()["requires_approval"] is True
    assert unknown.json()["assigned_agent"] == "ai-boss"
    assert unknown.json()["requires_approval"] is True


def test_connector_priorities_match_current_merchant_channels() -> None:
    client = TestClient(app)

    response = client.get("/v1/connectors/status")

    assert response.status_code == 200
    platforms = [item["platform"] for item in response.json()]
    assert platforms[:3] == ["taobao", "douyin", "xianyu"]
    xianyu = next(item for item in response.json() if item["platform"] == "xianyu")
    assert xianyu["status"] == "not_connected"
