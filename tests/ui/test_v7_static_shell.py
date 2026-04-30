from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_v7_static_shell_is_available_and_preserves_live_preview():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "v7 Operator Console Prototype" in response.text
    assert "Live image region preserved" in response.text
    assert "Latest Exposure Preview" in response.text


def test_v7_static_setup_page_marks_local_placeholders_and_phase_boundary():
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
