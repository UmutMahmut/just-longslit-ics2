from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_v7_runtime_scripts_are_not_injected_by_default():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "/ui-assets/v7/runtime_status.js" not in response.text
    assert "/ui-assets/v7/preset_runtime.js" not in response.text
    assert "/ui-assets/v7/observe_runtime.js" not in response.text
    assert "/ui-assets/v7/observe_guard.js" not in response.text


def test_v7_runtime_scripts_are_injected_when_enabled(monkeypatch):
    monkeypatch.setenv("JUSTLS_UI_V7_RUNTIME_ENABLED", "1")
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["ui_safety_switches"]["phase2d8_v7_runtime_enabled"] is True

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert response.text.index("/ui-assets/v7/runtime_status.js") < response.text.index("/ui-assets/v7/preset_runtime.js")
    assert response.text.index("/ui-assets/v7/preset_runtime.js") < response.text.index("/ui-assets/v7/observe_runtime.js")
    assert response.text.index("/ui-assets/v7/observe_runtime.js") < response.text.index("/ui-assets/v7/observe_guard.js")
