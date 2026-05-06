from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_v7_static_shell_contains_instrument_configure_page():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    html = response.text
    assert "Instrument / Configure" in html
    assert 'data-page="instrument"' in html
    assert 'data-page-panel="instrument"' in html
    assert 'data-role="instrument-summary"' in html
    assert 'data-role="slit-configuration"' in html
    assert 'data-role="calibration-configuration"' in html
    assert 'data-role="detector-configuration"' in html
    assert 'data-role="bgr-channel-panels"' in html
    assert 'data-role="instrument-safety-boundary"' in html


def test_v7_static_shell_preserves_stable_runtime_binding_ids():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    html = response.text
    assert 'id="run-mode"' in html
    assert 'id="operational-level"' in html
    assert 'id="exposure-state"' in html
    assert 'id="local-time"' in html
    assert 'id="v7-observe-controls"' in html
    assert 'id="v7-presets-runtime"' in html


def test_v7_static_shell_models_just_as_bgr_not_mods_blue_red():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    html = response.text
    assert "B Channel" in html
    assert "G Channel" in html
    assert "R Channel" in html
    assert 'data-channel="B"' in html
    assert 'data-channel="G"' in html
    assert 'data-channel="R"' in html
    assert "Blue Channel" not in html
    assert "Red Channel" not in html


def test_v7_static_shell_keeps_unwired_hardware_honest():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    html = response.text
    assert "backend contract" in html
    assert "not wired" in html
    assert "Runtime remains opt-in" in html
    assert "quicklook / data watcher deferred" in html


def test_v7_static_shell_still_does_not_inject_runtime_by_default():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    html = response.text
    assert "/ui-assets/v7/runtime_status.js" not in html
    assert "/ui-assets/v7/preset_runtime.js" not in html
    assert "/ui-assets/v7/observe_runtime.js" not in html
    assert "/ui-assets/v7/observe_guard.js" not in html
