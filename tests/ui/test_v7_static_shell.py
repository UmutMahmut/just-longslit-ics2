from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_v7_static_shell_is_available_and_preserves_live_preview():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "v7.1 Operator Console Prototype" in response.text
    assert "Latest Exposure Preview" in response.text
    assert "Instrument / Configure" in response.text


def test_v7_static_setup_page_marks_local_placeholders_and_phase_boundary():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "data-role=\"setup-page\"" in response.text
    assert "data-role=\"local-session-context\"" in response.text
    assert "data-role=\"session-input\"" in response.text
    assert "data-phase=\"2.8-H-static\"" in response.text
    assert "data-phase=\"local-placeholder\"" in response.text
    assert "Routine instrument configuration now lives under Instrument / Configure" in response.text
    assert "id=\"v7-setup-readiness\"" in response.text


def test_v7_static_presets_page_has_single_runtime_enhanceable_skeleton():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert response.text.count('id="v7-presets-runtime"') == 1
    assert 'data-role="v7-presets-panel"' in response.text
    assert 'data-phase="static-fallback"' in response.text
    assert 'data-bind="v7.presets.status"' in response.text
    assert 'data-bind="v7.presets.catalog"' in response.text
    assert 'data-bind="v7.presets.preview"' in response.text
    assert 'data-role="v7-preset-confirmation"' in response.text
    assert 'data-action="apply-previewed-preset"' in response.text
    assert "Presets · Catalog / Preview / Guarded Apply" in response.text
    assert "<h2>Preset List</h2>" not in response.text
    assert "<h2>Preview / Apply</h2>" not in response.text


def test_v7_static_observe_page_has_single_runtime_enhanceable_skeleton():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert response.text.count('id="v7-observe-controls"') == 1
    assert 'data-role="v7-observe-panel"' in response.text
    assert 'data-bind="v7.observe.state"' in response.text
    assert 'data-bind="v7.observe.armed"' in response.text
    assert 'data-bind="v7.observe.last_command"' in response.text
    assert 'data-bind="v7.observe.runtime_state"' in response.text
    assert 'data-bind="v7.observe.result"' in response.text
    assert 'data-role="obs-exp-time"' in response.text
    assert 'data-role="obs-frame-type"' in response.text
    assert 'data-role="obs-operator-note"' in response.text
    assert 'data-role="obs-abort-confirm"' in response.text
    assert 'data-action="obs-arm"' in response.text
    assert 'data-action="obs-start"' in response.text
    assert 'data-action="obs-stop-readout"' in response.text
    assert 'data-action="obs-abort-discard"' in response.text
    assert "Observe · Single Exposure Control · Single Exposure Only" in response.text
    assert "Buttons are static until Phase 2.8-F binding" not in response.text

def test_v7_default_shell_exposes_unified_command_feedback_static_bindings():
    client = TestClient(app)

    response = client.get("/ui")

    assert response.status_code == 200
    assert "v7.1 Operator Console Prototype" in response.text
    assert 'data-role="diagnostics-command-feedback"' in response.text
    assert "last_command / request_id / latest_job / last_error / result_summary / raw_json" in response.text

    for prefix in ("instrument", "observe", "presets"):
        assert f'data-bind="v7.{prefix}.last_command"' in response.text
        assert f'data-bind="v7.{prefix}.request_id"' in response.text
        assert f'data-bind="v7.{prefix}.latest_job"' in response.text
        assert f'data-bind="v7.{prefix}.last_error"' in response.text
        assert f'data-bind="v7.{prefix}.result_summary"' in response.text
