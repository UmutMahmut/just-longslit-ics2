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

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "v7 Operator Console Prototype" in response.text
    assert "Live image region preserved" in response.text
    assert "Latest Exposure Preview" in response.text


def test_ui_v7_status_binding_adapter_is_injected_and_served():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "/ui-assets/phase2d8_v7_status_binding.js" in response.text

    adapter = client.get("/ui-assets/phase2d8_v7_status_binding.js")

    assert adapter.status_code == 200
    assert "/api/v1/status/full" in adapter.text
    assert "Latest Exposure Preview" not in adapter.text


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


def test_ui_v7_status_binding_has_connection_state_markers():
    client = TestClient(app)

    adapter = client.get("/ui-assets/phase2d8_v7_status_binding.js")

    assert adapter.status_code == 200
    assert "data-connection" in adapter.text
    assert "connectionStatus" in adapter.text
    assert "v7.connection" in adapter.text
    assert "STALE" in adapter.text
    assert "CONNECTED" in adapter.text
    assert "ERROR" in adapter.text
    assert "data-level" in adapter.text


def test_ui_v7_status_binding_has_bounded_raw_status_preview():
    client = TestClient(app)

    adapter = client.get("/ui-assets/phase2d8_v7_status_binding.js")

    assert adapter.status_code == 200
    assert "RAW_STATUS_MAX_CHARS" in adapter.text
    assert "v7-raw-status-preview" in adapter.text
    assert "v7.raw_status_preview" in adapter.text
    assert "ensureRawStatusPreview" in adapter.text
    assert "updateRawStatusPreview" in adapter.text
    assert "updateRawStatusError" in adapter.text
    assert "data-page-panel=\"diagnostics\"" in adapter.text
    assert "truncated at" in adapter.text


def test_ui_v7_status_binding_has_setup_readiness_panel():
    client = TestClient(app)

    adapter = client.get("/ui-assets/phase2d8_v7_status_binding.js")

    assert adapter.status_code == 200
    assert "v7-setup-readiness" in adapter.text
    assert "Setup Readiness" in adapter.text
    assert "ensureSetupReadinessPanel" in adapter.text
    assert "updateSetupReadiness" in adapter.text
    assert "v7.setup.detector_profile" in adapter.text
    assert "v7.setup.calibration" in adapter.text
    assert "v7.setup.preset_context" in adapter.text
    assert "v7.setup.save_enabled" in adapter.text
    assert "Session form fields remain local placeholders" in adapter.text


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
    assert "data-phase=\"not-wired\"" in response.text
    assert "data-role=\"data-product-context\"" in response.text
    assert "data-phase=\"future-binding\"" in response.text
    assert "Runtime instrument context is shown in the Setup Readiness panel" in response.text
