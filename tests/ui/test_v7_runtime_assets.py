from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_v7_runtime_static_assets_are_served():
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


def test_v7_status_binding_asset_has_runtime_panels():
    client = TestClient(app)

    adapter = client.get("/ui-assets/phase2d8_v7_status_binding.js")

    assert adapter.status_code == 200
    assert "v7-runtime-status" in adapter.text
    assert "data-bind" in adapter.text
    assert "data-connection" in adapter.text
    assert "v7.connection" in adapter.text
    assert "v7.detector_profile" in adapter.text
    assert "v7.latest_job" in adapter.text
    assert "v7-raw-status-preview" in adapter.text
    assert "v7.raw_status_preview" in adapter.text
    assert "v7-setup-readiness" in adapter.text
    assert "Setup Readiness" in adapter.text
    assert "v7-presets-runtime" in adapter.text
    assert "Runtime Presets" in adapter.text
    assert "setInputByLabel" not in adapter.text
    assert "setDescriptionValue" not in adapter.text


def test_v7_runtime_guards_have_loop_prevention_markers():
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
