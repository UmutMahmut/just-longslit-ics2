from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_v7_runtime_scripts_are_not_injected_by_default():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "phase2d8_v7_status_binding.js" not in response.text
    assert "phase2d8_v7_preset_apply_guard.js" not in response.text
    assert "phase2d8_v7_observe_controls.js" not in response.text
    assert "phase2d8_v7_observe_safety_guard.js" not in response.text


def test_v7_runtime_scripts_are_injected_when_enabled(monkeypatch):
    monkeypatch.setenv("JUSTLS_UI_V7_RUNTIME_ENABLED", "1")
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["ui_safety_switches"]["phase2d8_v7_runtime_enabled"] is True

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert response.text.index("phase2d8_v7_status_binding.js") < response.text.index("phase2d8_v7_preset_apply_guard.js")
    assert response.text.index("phase2d8_v7_preset_apply_guard.js") < response.text.index("phase2d8_v7_observe_controls.js")
    assert response.text.index("phase2d8_v7_observe_controls.js") < response.text.index("phase2d8_v7_observe_safety_guard.js")
