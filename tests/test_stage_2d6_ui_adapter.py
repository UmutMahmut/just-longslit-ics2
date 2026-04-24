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
