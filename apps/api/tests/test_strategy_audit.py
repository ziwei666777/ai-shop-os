from fastapi.testclient import TestClient

from apps.api.app.main import app


client = TestClient(app)


def test_strategy_audit_tracks_v2_employee_os_gaps() -> None:
    response = client.get("/v1/strategy/audit")

    assert response.status_code == 200
    body = response.json()
    assert body["positioning"] == "AI Employee OS（企业 AI 数字员工操作系统）"
    assert "直播运营助理" in body["focus"]
    assert body["overall_score"] >= 50
    assert body["estimated_daily_saved_minutes"] > 0
    assert body["estimated_daily_saved_yuan"] > 0
    assert "不要新增 AI 客服页面" in body["stop_doing"]

    capabilities = {item["id"]: item for item in body["capabilities"]}
    assert capabilities["live-operation-agent"]["priority"] == "P0"
    assert capabilities["live-operation-agent"]["replaced_role"] == "直播运营助理"
    assert capabilities["ceo-agent"]["priority"] == "P0"
    assert capabilities["savings-roi-engine"]["priority"] == "P0"
    assert capabilities["daily-autonomous-work"]["priority"] == "P0"
    assert capabilities["daily-autonomous-work"]["status"] == "in_progress"
    assert capabilities["agent-collaboration"]["status"] == "in_progress"

    assert all("客服页面" not in action for action in body["next_p0_actions"])
    assert any("live_workflow_runs" in action for action in body["next_p0_actions"])
