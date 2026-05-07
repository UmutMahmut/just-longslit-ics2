from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_v7_1_all_runtime_modules_inject_against_single_durable_skeletons(monkeypatch):
    monkeypatch.setenv("JUSTLS_UI_V7_RUNTIME_ENABLED", "1")
    monkeypatch.setenv("JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED", "1")
    monkeypatch.setenv("JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED", "1")
    monkeypatch.setenv("JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED", "1")
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    html = response.text
    assert html.count('id="v7-runtime-status"') == 1
    assert html.count('id="v7-raw-status-preview"') == 1
    assert html.count('id="v7-setup-readiness"') == 1
    assert html.count('id="v7-observe-controls"') == 1
    assert html.count('id="v7-presets-runtime"') == 1
    assert 'data-page-panel="instrument"' in html
    assert 'data-bind="v7.instrument.current_preset"' in html
    assert 'data-bind="v7.instrument.channel.B.enabled"' in html
    assert 'data-bind="v7.instrument.channel.G.enabled"' in html
    assert 'data-bind="v7.instrument.channel.R.enabled"' in html
    assert 'data-bind="v7.message.text"' in html
    assert "/ui-assets/v7/runtime_status.js" in html
    assert "/ui-assets/v7/preset_runtime.js" in html
    assert "/ui-assets/v7/observe_runtime.js" in html
    assert "/ui-assets/v7/observe_guard.js" in html


def test_v7_runtime_status_asset_targets_v7_1_instrument_and_diagnostics_skeletons():
    client = TestClient(app)

    response = client.get("/ui-assets/v7/runtime_status.js")

    assert response.status_code == 200
    js = response.text
    assert "__JUSTLS_V7_RUNTIME_STATUS__" in js
    assert "v7-runtime-status" in js
    assert "v7-setup-readiness" in js
    assert "v7-raw-status-preview" in js
    assert "v7.instrument.current_preset" in js
    assert "v7.instrument.bgr_readiness" in js
    assert "v7.instrument.channel.B.enabled" in js
    assert "v7.instrument.channel.G.enabled" in js
    assert "v7.instrument.channel.R.enabled" in js
    assert "v7.message.text" in js


def test_v7_runtime_status_asset_tracks_feedback_rail_telemetry():
    client = TestClient(app)

    response = client.get("/ui-assets/v7/runtime_status.js")

    assert response.status_code == 200
    js = response.text
    assert "lastRequestId" in js
    assert "lastRttMs" in js
    assert "lastOkAt" in js
    assert "connectionState" in js
    assert "requestIdFrom" in js
    assert "X-Request-ID" in js
    assert "x-request-id" in js
    assert "performance.now" in js
    assert "data-severity" in js
    assert "data-connection" in js
    assert "data-request-id" in js
    assert "v7.message.severity" in js
    assert "v7.connection.rtt_ms" in js
    assert "v7.connection.last_ok_at" in js
    assert "v7.request_id" in js


def test_v7_preset_runtime_asset_targets_existing_presets_skeleton():
    client = TestClient(app)

    response = client.get("/ui-assets/v7/preset_runtime.js")

    assert response.status_code == 200
    js = response.text
    assert "__JUSTLS_V7_PRESET_RUNTIME__" in js
    assert 'document.getElementById("v7-presets-runtime")' in js
    assert 'data-bind="v7.presets.catalog"' in js
    assert 'data-bind="v7.presets.preview"' in js
    assert 'data-role="v7-preset-confirmation"' in js
    assert 'data-action="apply-previewed-preset"' in js
    assert "/api/v1/presets" in js
    assert "/api/v1/presets/preview" in js
    assert "/api/v1/presets/apply" in js


def test_v7_observe_runtime_and_guard_assets_target_existing_observe_skeleton():
    client = TestClient(app)

    runtime_response = client.get("/ui-assets/v7/observe_runtime.js")
    guard_response = client.get("/ui-assets/v7/observe_guard.js")

    assert runtime_response.status_code == 200
    assert guard_response.status_code == 200
    runtime_js = runtime_response.text
    guard_js = guard_response.text
    assert "__JUSTLS_V7_OBSERVE_RUNTIME__" in runtime_js
    assert 'document.getElementById("v7-observe-controls")' in runtime_js
    assert 'data-role="obs-exp-time"' in runtime_js
    assert 'data-role="obs-frame-type"' in runtime_js
    assert 'data-role="obs-operator-note"' in runtime_js
    assert 'data-role="obs-abort-confirm"' in runtime_js
    assert 'data-action="obs-arm"' in runtime_js
    assert 'data-action="obs-start"' in runtime_js
    assert 'data-action="obs-finish"' in runtime_js
    assert 'data-action="obs-stop-readout"' in runtime_js
    assert 'data-action="obs-abort-discard"' in runtime_js
    assert "FINISH_ENDPOINT" in runtime_js
    assert "/api/v1/observation/finish" in runtime_js
    assert "v7.observe.request_id" in runtime_js
    assert "v7.observe.latest_job" in runtime_js
    assert "v7.observe.last_error" in runtime_js
    assert "requestIdFrom" in runtime_js
    assert "__JUSTLS_V7_OBSERVE_GUARD__" in guard_js
    assert 'document.getElementById("v7-observe-controls")' in guard_js
    assert 'data-role="obs-abort-confirm"' in guard_js
    assert "obs-arm" in guard_js
    assert "obs-start" in guard_js
    assert "obs-finish" in guard_js
    assert "obs-stop_readout" not in guard_js
    assert "obs-stop-readout" in guard_js
    assert "obs-abort-discard" in guard_js


def test_v7_served_observe_shell_exposes_h3_finish_and_structured_result_fields():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    html = response.text
    assert 'data-action="obs-finish"' in html
    assert 'data-bind="v7.observe.request_id"' in html
    assert 'data-bind="v7.observe.latest_job"' in html
    assert 'data-bind="v7.observe.last_error"' in html
