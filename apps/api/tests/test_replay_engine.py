from fastapi.testclient import TestClient

from apps.api.app.main import app


client = TestClient(app)


def test_replay_summary_returns_business_metrics() -> None:
    response = client.get("/v1/replay/summary")

    assert response.status_code == 200
    body = response.json()
    assert body["total_cases"] >= 5
    assert body["correct_cases"] > 0
    assert body["accuracy"] > 0
    assert body["saved_minutes"] > 0
    assert body["estimated_saving_yuan"] > 0


def test_replay_summary_keeps_high_risk_cases_manual() -> None:
    response = client.get("/v1/replay/summary")

    assert response.status_code == 200
    risky_results = [
        item for item in response.json()["results"]
        if "赔偿" in item["input_text"] or "投诉" in item["input_text"] or "瑕疵" in item["input_text"]
    ]
    assert risky_results
    assert all(item["requires_human"] for item in risky_results)
    assert {item["ai_decision"] for item in risky_results} <= {"human_review", "approval_required"}


def test_replay_summary_uses_business_data_sources() -> None:
    response = client.get("/v1/replay/summary")

    assert response.status_code == 200
    titles = {item["title"] for item in response.json()["results"]}
    assert any(title.startswith("客服消息") for title in titles)
    assert any(title.startswith("物流回放") for title in titles)
    assert any(title.startswith("客户运营回放") for title in titles)
