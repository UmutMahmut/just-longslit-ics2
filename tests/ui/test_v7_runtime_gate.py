from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_v7_runtime_scripts_are_not_injected_by_default():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "/ui-assets/v7/runtime_status.js" not in response.text
    assert "/ui-assets/v7/instrument_runtime.js" not in response.text
    assert "/ui-assets/v7/preset_runtime.js" not in response.text
    assert "/ui-assets/v7/observe_runtime.js" not in response.text
    assert "/ui-assets/v7/observe_guard.js" not in response.text


def test_v7_runtime_master_gate_injects_status_only_by_default(monkeypatch):
    monkeypatch.setenv("JUSTLS_UI_V7_RUNTIME_ENABLED", "1")
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    switches = response.json()["ui_safety_switches"]
    assert switches["phase2d8_v7_runtime_enabled"] is True
    assert switches["phase2d8_v7_runtime_modules"] == {
        "status": True,
        "setup": False,
        "instrument": False,
        "presets": False,
        "observe": False,
        "observe_guard": False,
    }

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "/ui-assets/v7/runtime_status.js" in response.text
    assert "/ui-assets/v7/instrument_runtime.js" not in response.text
    assert "/ui-assets/v7/preset_runtime.js" not in response.text
    assert "/ui-assets/v7/observe_runtime.js" not in response.text
    assert "/ui-assets/v7/observe_guard.js" not in response.text


def test_v7_runtime_modules_are_individually_opt_in(monkeypatch):
    monkeypatch.setenv("JUSTLS_UI_V7_RUNTIME_ENABLED", "1")
    monkeypatch.setenv("JUSTLS_UI_V7_INSTRUMENT_RUNTIME_ENABLED", "1")
    monkeypatch.setenv("JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED", "1")
    monkeypatch.setenv("JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED", "1")
    monkeypatch.setenv("JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED", "1")
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    switches = response.json()["ui_safety_switches"]
    assert switches["phase2d8_v7_runtime_modules"] == {
        "status": True,
        "setup": False,
        "instrument": True,
        "presets": True,
        "observe": True,
        "observe_guard": True,
    }

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert response.text.index("/ui-assets/v7/runtime_status.js") < response.text.index("/ui-assets/v7/instrument_runtime.js")
    assert response.text.index("/ui-assets/v7/instrument_runtime.js") < response.text.index("/ui-assets/v7/preset_runtime.js")
    assert response.text.index("/ui-assets/v7/preset_runtime.js") < response.text.index("/ui-assets/v7/observe_runtime.js")
    assert response.text.index("/ui-assets/v7/observe_runtime.js") < response.text.index("/ui-assets/v7/observe_guard.js")


def test_v7_status_runtime_can_be_disabled_even_when_master_gate_is_enabled(monkeypatch):
    monkeypatch.setenv("JUSTLS_UI_V7_RUNTIME_ENABLED", "1")
    monkeypatch.setenv("JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED", "0")
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["ui_safety_switches"]["phase2d8_v7_runtime_modules"]["status"] is False
    assert response.json()["ui_safety_switches"]["phase2d8_v7_runtime_modules"]["instrument"] is False

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "/ui-assets/v7/runtime_status.js" not in response.text
    assert "/ui-assets/v7/instrument_runtime.js" not in response.text
    assert "/ui-assets/v7/preset_runtime.js" not in response.text
    assert "/ui-assets/v7/observe_runtime.js" not in response.text
    assert "/ui-assets/v7/observe_guard.js" not in response.text
