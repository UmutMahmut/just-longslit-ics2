import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("src"))

from justls.ics.app.main import app, inject_phase_2d6_ui_adapter
from justls.ics.kernel.runtime import reset_runtime


def setup_function():
    reset_runtime()


def teardown_function():
    reset_runtime()


def test_stage_2d6_ui_injection_is_idempotent():
    html = "<html><body><main>UI</main></body></html>"

    once = inject_phase_2d6_ui_adapter(html)
    twice = inject_phase_2d6_ui_adapter(once)

    assert once == twice
    assert once.count("phase2d6_operational_status.js") == 1
    assert once.index("phase2d6_operational_status.js") < once.index("</body>")


def test_stage_2d6_ui_serves_operational_adapter():
    client = TestClient(app)

    response = client.get("/ui")

    assert response.status_code == 200
    assert "phase2d6_operational_status.js" in response.text


def test_stage_2d6_ui_v6_route_available_and_structured():
    client = TestClient(app)

    response = client.get("/ui/v6")

    assert response.status_code == 200
    assert "Operational UI v6" in response.text
    assert 'data-command="observation.start"' in response.text
    assert 'data-command="observation.stop_readout"' in response.text
    assert 'data-command="observation.abort_discard"' in response.text
    assert 'data-risk="high-impact-config"' in response.text
    assert "phase2d6_operational_status.js" in response.text
    assert "phase2d6_command_runtime.js" in response.text


def test_stage_2d6_root_advertises_ui_v6():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["ui_v6"] == "/ui/v6"


def test_stage_2d6_ui_adapter_static_asset_available():
    client = TestClient(app)

    response = client.get("/ui-assets/phase2d6_operational_status.js")

    assert response.status_code == 200
    assert "operational_status" in response.text
    assert "STATUS_URL" in response.text


def test_stage_2d6_ui_adapter_has_timeout_and_inflight_guard():
    client = TestClient(app)

    response = client.get("/ui-assets/phase2d6_operational_status.js")

    assert response.status_code == 200
    assert "AbortController" in response.text
    assert "STATUS_TIMEOUT_MS" in response.text
    assert "statusRefreshInFlight" in response.text


def test_stage_2d6_ui_adapter_uses_explicit_command_gate_model():
    client = TestClient(app)

    response = client.get("/ui-assets/phase2d6_operational_status.js")

    assert response.status_code == 200
    assert "data-command" in response.text
    assert "data-risk" in response.text
    assert "phase2d6InitialDisabled" in response.text
    assert "observation.start" in response.text
    assert "observation.stop_readout" in response.text
    assert "observation.abort_discard" in response.text
    assert "config.high_impact" in response.text


def test_stage_2d6_ui_adapter_has_command_marker_catalog():
    client = TestClient(app)

    response = client.get("/ui-assets/phase2d6_operational_status.js")

    assert response.status_code == 200
    assert "COMMAND_MARKER_CATALOG" in response.text
    assert "annotateCommandMarkers" in response.text
    assert "data-phase2d6-marker-source" in response.text
    assert "Stop & Readout" in response.text
    assert "Abort & Discard" in response.text
    assert "high-impact-config" in response.text


def test_stage_2d6_command_runtime_static_asset_available():
    client = TestClient(app)

    response = client.get("/ui-assets/phase2d6_command_runtime.js")

    assert response.status_code == 200
    assert "COMMAND_TIMEOUT_MS" in response.text
    assert "commandInFlight" in response.text
    assert "X-Request-ID" in response.text
    assert "postJsonWithTimeout" in response.text
    assert "stopImmediatePropagation" in response.text
