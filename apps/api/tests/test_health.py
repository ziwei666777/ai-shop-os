from fastapi.testclient import TestClient

from apps.api.app.infrastructure.config import get_settings
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
    assert low_risk.json()["knowledge_hit"] == "物流查询"
    assert low_risk.json()["memory_hit"] == "店铺语气"
    assert low_risk.json()["saved_minutes"] > 0
    assert low_risk.json()["estimated_saving_yuan"] > 0
    assert low_risk_send.status_code == 200
    assert low_risk_send.json()["status"] == "sent"
    assert high_risk_send.status_code == 409

    high_risk = client.post("/v1/customer-agent/messages/msg-3/draft-reply")
    assert high_risk.status_code == 200
    assert high_risk.json()["automation_decision"] == "human_review"
    assert high_risk.json()["required_human_review"] is True
    assert high_risk.json()["saved_minutes"] == 0


def test_external_customer_message_ingest_creates_real_inbox_item() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/customer-agent/external-messages",
        json={
            "platform": "taobao",
            "platform_message_id": "tb-live-msg-1",
            "customer_name": "真实客户A",
            "content": "订单什么时候发货？",
            "channel": "taobao_bridge",
            "customer_external_id": "tb-customer-a",
            "order_external_id": "TB10001",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["platform"] == "taobao"
    assert body["intent"] == "logistics"
    assert body["automation_decision"] == "auto_reply"

    draft = client.post(f"/v1/customer-agent/messages/{body['id']}/draft-reply")
    assert draft.status_code == 200
    assert draft.json()["required_human_review"] is False


def test_external_customer_message_ingest_blocks_high_risk_auto_reply() -> None:
    client = TestClient(app)

    response = client.post(
        "/v1/customer-agent/external-messages",
        json={
            "platform": "douyin",
            "platform_message_id": "dy-live-msg-1",
            "customer_name": "真实客户B",
            "content": "我要投诉，商品有问题你们要赔偿",
            "channel": "douyin_bridge",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["automation_decision"] == "human_review"
    assert body["status"] == "needs_human"

    send = client.post(f"/v1/customer-agent/messages/{body['id']}/send", json={"content": "好的，马上赔偿。"})
    assert send.status_code == 409


def test_external_customer_message_ingest_accepts_bridge_key(monkeypatch) -> None:
    client = TestClient(app)
    settings = get_settings()
    monkeypatch.setattr(settings, "auth_required", True)
    monkeypatch.setattr(settings, "merchant_bridge_api_key", "bridge-secret")
    monkeypatch.setattr(settings, "merchant_bridge_company_id", "00000000-0000-0000-0000-000000000001")

    rejected = client.post(
        "/v1/customer-agent/external-messages",
        json={
            "platform": "taobao",
            "platform_message_id": "tb-bridge-rejected",
            "customer_name": "桥接客户",
            "content": "订单什么时候发货？",
        },
        headers={"X-AICOS-Bridge-Key": "bad"},
    )
    accepted = client.post(
        "/v1/customer-agent/external-messages",
        json={
            "platform": "taobao",
            "platform_message_id": "tb-bridge-accepted",
            "customer_name": "桥接客户",
            "content": "订单什么时候发货？",
        },
        headers={"X-AICOS-Bridge-Key": "bridge-secret"},
    )

    assert rejected.status_code == 401
    assert accepted.status_code == 201
    assert accepted.json()["automation_decision"] == "auto_reply"


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


def test_readiness_endpoint_reports_evidence_chain_status() -> None:
    client = TestClient(app)

    response = client.get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert "evidence_chain_ready" in body
    assert "evidence_chain_blockers" in body
def test_readiness_endpoint_blocks_when_evidence_table_is_missing(monkeypatch) -> None:
    from apps.api.app import main

    class FakeResult:
        def scalar_one(self):
            return 1

    class FakeSession:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, statement):
            return FakeResult()

    monkeypatch.setattr(main, "SessionFactory", lambda: FakeSession())
    monkeypatch.setattr(main, "find_missing_evidence_tables", lambda session: ("ceo_daily_report_snapshots",))

    response = TestClient(app).get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["database"] is True
    assert body["evidence_chain_ready"] is False
    assert "Missing evidence table: ceo_daily_report_snapshots." in body["evidence_chain_blockers"]