import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("src"))

from justls.ics.app.main import app


def test_ui_root_stays_default_v5_entry():
    client = TestClient(app)

    response = client.get("/ui")

    assert response.status_code == 200
    assert "UI Alpha Skeleton" in response.text
    assert "v7 Operator Console Prototype" not in response.text


def test_ui_v6_review_shell_stays_available():
    client = TestClient(app)

    response = client.get("/ui/v6")

    assert response.status_code == 200
    assert "v6" in response.text.lower()


def test_ui_v7_operator_console_shell_is_available():
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["ui_v7"] == "/ui/v7"
    assert response.json()["ui_safety_switches"]["phase2d8_v7_runtime_enabled"] is False

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "v7 Operator Console Prototype" in response.text
    assert "Live image region preserved" in response.text
    assert "Latest Exposure Preview" in response.text


def test_ui_v7_runtime_scripts_are_not_injected_by_default():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "phase2d8_v7_status_binding.js" not in response.text
    assert "phase2d8_v7_preset_apply_guard.js" not in response.text
    assert "phase2d8_v7_observe_controls.js" not in response.text
    assert "phase2d8_v7_observe_safety_guard.js" not in response.text


def test_ui_v7_runtime_scripts_are_injected_when_enabled(monkeypatch):
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


def test_ui_v7_runtime_static_assets_are_served():
    client = TestClient(app)

    assets = {
        "status": client.get("/ui-assets/phase2d8_v7_status_binding.js"),
        "preset_guard": client.get("/ui-assets/phase2d8_v7_preset_apply_guard.js"),
        "observe_controls": client.get("/ui-assets/phase2d8_v7_observe_controls.js"),
        "observe_guard": client.get("/ui-assets/phase2d8_v7_observe_safety_guard.js"),
    }

    for response in assets.values():
        assert response.status_code == 200

    assert "/api/v1/status/full" in assets["status"].text
    assert "/api/v1/presets" in assets["status"].text
    assert "/api/v1/presets/preview" in assets["status"].text
    assert "/api/v1/presets/apply" in assets["preset_guard"].text
    assert "/api/v1/observation/status" in assets["observe_controls"].text
    assert "/api/v1/observation/arm" in assets["observe_controls"].text
    assert "/api/v1/observation/start" in assets["observe_controls"].text
    assert "/api/v1/observation/stop_readout" in assets["observe_controls"].text


def test_ui_v7_status_binding_uses_stable_data_bind_panel():
    client = TestClient(app)

    adapter = client.get("/ui-assets/phase2d8_v7_status_binding.js")

    assert adapter.status_code == 200
    assert "v7-runtime-status" in adapter.text
    assert "data-bind" in adapter.text
    assert "v7.detector_profile" in adapter.text
    assert "v7.latest_job" in adapter.text
    assert "setInputByLabel" not in adapter.text
    assert "setDescriptionValue" not in adapter.text


def test_ui_v7_status_binding_has_runtime_panels():
    client = TestClient(app)

    adapter = client.get("/ui-assets/phase2d8_v7_status_binding.js")

    assert adapter.status_code == 200
    assert "data-connection" in adapter.text
    assert "v7.connection" in adapter.text
    assert "v7-raw-status-preview" in adapter.text
    assert "v7.raw_status_preview" in adapter.text
    assert "v7-setup-readiness" in adapter.text
    assert "Setup Readiness" in adapter.text
    assert "v7-presets-runtime" in adapter.text
    assert "Runtime Presets" in adapter.text


def test_ui_v7_setup_page_marks_local_placeholders_and_phase_boundary():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "data-role=\"setup-page\"" in response.text
    assert "data-role=\"local-session-context\"" in response.text
    assert "data-role=\"local-session-fields\"" in response.text
    assert "data-role=\"setup-phase-boundary-note\"" in response.text
    assert "data-phase=\"2.8-D\"" in response.text
    assert "data-phase=\"local-placeholder\"" in response.text
    assert "data-role=\"data-product-context\"" in response.text


def test_ui_v7_runtime_guards_have_loop_prevention_markers():
    client = TestClient(app)

    preset_guard = client.get("/ui-assets/phase2d8_v7_preset_apply_guard.js")
    observe_guard = client.get("/ui-assets/phase2d8_v7_observe_safety_guard.js")

    assert preset_guard.status_code == 200
    assert observe_guard.status_code == 200

    for script in (preset_guard.text, observe_guard.text):
        assert "refreshQueued" in script
        assert "scheduleRefresh" in script
        assert "setTextIfChanged" in script
        assert "setAttributeIfChanged" in script
        assert "MutationObserver(scheduleRefresh)" in script
        assert "window.setTimeout" in script

    assert "fetch(" not in observe_guard.text
    assert "new XMLHttpRequest" not in observe_guard.text
