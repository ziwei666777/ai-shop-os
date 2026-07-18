from fastapi.testclient import TestClient

from apps.api.app.infrastructure.memory_store import LEARNING_EVENTS
from apps.api.app.infrastructure.training_center import COMMITTED_TRAINING_ASSETS
from apps.api.app.main import app


client = TestClient(app)


def test_evaluation_summary_uses_replay_metrics() -> None:
    response = client.get("/v1/evaluation/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["overall_score"] > 0
    assert body["evaluated_cases"] >= 5
    assert body["estimated_monthly_saving_yuan"] > 0
    assert any(metric["id"] == "risk_control" for metric in body["metrics"])
    assert any(metric["id"] == "dataset_readiness" for metric in body["metrics"])


def test_training_center_summary_groups_learning_targets() -> None:
    LEARNING_EVENTS.clear()
    COMMITTED_TRAINING_ASSETS.clear()
    response = client.get("/v1/training-center/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total_samples"] == 3
    assert body["usable_samples"] == 2
    assert body["memory_candidates"] == 1
    assert body["workflow_candidates"] == 1
    assert len(body["asset_candidates"]) == 3
    assert {item["target"] for item in body["asset_candidates"]} == {"knowledge", "memory", "workflow"}


def test_training_center_uses_real_learning_events_when_available() -> None:
    LEARNING_EVENTS.clear()
    COMMITTED_TRAINING_ASSETS.clear()
    learning_response = client.post(
        "/v1/learning-events",
        json={
            "source_type": "message",
            "source_id": "msg-real-1",
            "agent_id": "ai-customer",
            "action": "edited",
            "original_content": "亲，可以催一下。",
            "final_content": "您好，我已经查询订单，今天会发货；如果 24 小时没有物流更新，我会继续跟进。",
        },
    )
    assert learning_response.status_code == 200

    response = client.get("/v1/training-center/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total_samples"] == 1
    assert body["usable_samples"] == 1
    assert body["samples"][0]["id"] == learning_response.json()["id"]
    assert body["samples"][0]["training_target"] in {"memory", "knowledge"}
    assert body["asset_candidates"][0]["source_sample_id"] == learning_response.json()["id"]
    assert body["asset_candidates"][0]["status"] == "candidate"


def test_training_asset_can_be_committed_after_learning_event() -> None:
    LEARNING_EVENTS.clear()
    COMMITTED_TRAINING_ASSETS.clear()
    learning_response = client.post(
        "/v1/learning-events",
        json={
            "source_type": "after_sale_case",
            "source_id": "case-real-1",
            "agent_id": "ai-after-sale",
            "action": "manual_answered",
            "original_content": "可以直接退款。",
            "final_content": "退款前必须先核实订单、物流和图片证据，确认后进入老板审批。",
        },
    )
    assert learning_response.status_code == 200

    summary = client.get("/v1/training-center/summary").json()
    candidate_id = summary["asset_candidates"][0]["id"]
    commit_response = client.post(f"/v1/training-center/assets/{candidate_id}/commit")

    assert commit_response.status_code == 200
    assert commit_response.json()["status"] == "committed"
    assert commit_response.json()["target"] == "workflow"

    refreshed = client.get("/v1/training-center/summary").json()
    assert refreshed["asset_candidates"][0]["status"] == "committed"


def test_simulation_summary_keeps_risky_actions_approval_only() -> None:
    response = client.get("/v1/simulation/summary")
    assert response.status_code == 200
    body = response.json()
    risky = [item for item in body["scenarios"] if item["risk_level"] == "high"]
    assert risky
    assert all(item["ai_decision"] == "approval_required" for item in risky)
    assert body["estimated_daily_capacity"] == 10000
