from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_v7_runtime_static_assets_are_served_from_v7_directory():
    client = TestClient(app)

    assets = {
        "status": client.get("/ui-assets/v7/runtime_status.js"),
        "presets": client.get("/ui-assets/v7/preset_runtime.js"),
        "observe": client.get("/ui-assets/v7/observe_runtime.js"),
        "guard": client.get("/ui-assets/v7/observe_guard.js"),
    }

    for response in assets.values():
        assert response.status_code == 200

    assert "/api/v1/status/full" in assets["status"].text
    assert "/api/v1/presets" in assets["presets"].text
    assert "/api/v1/presets/preview" in assets["presets"].text
    assert "/api/v1/presets/apply" in assets["presets"].text
    assert "/api/v1/observation/status" in assets["observe"].text
    assert "/api/v1/observation/arm" in assets["observe"].text
    assert "/api/v1/observation/start" in assets["observe"].text
    assert "/api/v1/observation/stop_readout" in assets["observe"].text


def test_v5_operational_adapter_is_served_from_v5_directory():
    client = TestClient(app)

    adapter = client.get("/ui-assets/v5/phase2d6_operational_status.js")

    assert adapter.status_code == 200
    assert "/api/v1/status/full" in adapter.text
    assert "Phase 2.6 operational status adapter" in adapter.text


def test_v7_runtime_assets_have_expected_panel_markers():
    client = TestClient(app)

    status = client.get("/ui-assets/v7/runtime_status.js")
    presets = client.get("/ui-assets/v7/preset_runtime.js")
    observe = client.get("/ui-assets/v7/observe_runtime.js")
    guard = client.get("/ui-assets/v7/observe_guard.js")

    assert status.status_code == 200
    assert presets.status_code == 200
    assert observe.status_code == 200
    assert guard.status_code == 200

    assert "v7-runtime-status" in status.text
    assert "v7-setup-readiness" in status.text
    assert "v7-raw-status-preview" in status.text
    assert "v7-presets-runtime" in presets.text
    assert "Guarded Apply" in presets.text
    assert "v7-observe-controls" in observe.text
    assert "Single Exposure Only" in observe.text
    assert "data-guard-available" in guard.text
    assert "fetch(" not in guard.text
    assert "new XMLHttpRequest" not in guard.text


def test_v7_status_runtime_is_singleton_safe():
    client = TestClient(app)

    status = client.get("/ui-assets/v7/runtime_status.js")

    assert status.status_code == 200
    assert "__JUSTLS_V7_RUNTIME_STATUS__" in status.text
    assert "runtime.started" in status.text
    assert "runtime.intervalId" in status.text
    assert "runtime.refreshInFlight" in status.text
    assert "window.setInterval(refresh, POLL_MS)" in status.text
    assert "v7.runtime_status.refresh_count" in status.text
