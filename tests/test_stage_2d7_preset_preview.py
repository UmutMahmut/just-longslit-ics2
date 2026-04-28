import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("src"))

from justls.ics.application.services.management_service import ManagementService
from justls.ics.application.usecases.presets import build_preset_plan
from justls.ics.app.main import app
from justls.ics.kernel.runtime import RuntimeAssembler, reset_runtime


def setup_function():
    reset_runtime()


def teardown_function():
    reset_runtime()


def test_stage_2d7_preview_preset_plan_has_no_side_effects():
    runtime = RuntimeAssembler().build()
    service = ManagementService(runtime)
    before_detector = runtime.get_detector_config_dict()
    before_calibration = runtime.lamps.get_snapshot().to_dict()

    preview = service.preview_preset_plan(build_preset_plan("calib_flat_default"))

    assert preview["preset"] == "calib_flat_default"
    assert preview["category"] == "calibration"
    assert preview["risk_level"] == "high_impact"
    assert preview["requires_confirmation"] is True
    assert preview["blocked"] is False
    assert preview["blocked_reason"] is None
    assert preview["detector_config_changes"]
    assert preview["calibration_changes"]
    assert preview["changes"]

    assert runtime.get_detector_config_dict() == before_detector
    assert runtime.lamps.get_snapshot().to_dict() == before_calibration


def test_stage_2d7_preview_api_returns_backend_generated_diff():
    client = TestClient(app)

    response = client.post("/api/v1/presets/preview", json={"name": "calib_flat_default"})

    assert response.status_code == 200
    data = response.json()

    assert data["preset"] == "calib_flat_default"
    assert data["summary"]
    assert data["category"] == "calibration"
    assert data["risk_level"] == "high_impact"
    assert data["requires_confirmation"] is True
    assert data["blocked"] is False
    assert data["blocked_reason"] is None

    paths = {change["path"] for change in data["changes"]}
    assert "detector_config.profile_name" in paths
    assert "calibration.mode" in paths
    assert "calibration.active_lamp" in paths
    assert "calibration.lamp_enabled" in paths
    assert "calibration.mirror_inserted" in paths


def test_stage_2d7_preview_api_is_side_effect_free():
    client = TestClient(app)

    before_status = client.get("/api/v1/status/full").json()
    response = client.post("/api/v1/presets/preview", json={"name": "calib_flat_default"})
    after_status = client.get("/api/v1/status/full").json()

    assert response.status_code == 200
    assert before_status["detector_config"] == after_status["detector_config"]
    assert before_status["calibration"] == after_status["calibration"]


def test_stage_2d7_preview_api_unknown_preset_returns_404():
    client = TestClient(app)

    response = client.post("/api/v1/presets/preview", json={"name": "not_exists"})

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "preset_not_found"


def test_stage_2d7_preview_reports_blocked_when_observation_is_armed():
    client = TestClient(app)

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 10.0, "frame_type": "science", "operator_note": "preview-block"},
    )
    assert arm.status_code == 200

    response = client.post("/api/v1/presets/preview", json={"name": "science_default"})

    assert response.status_code == 200
    data = response.json()
    assert data["blocked"] is True
    assert "armed" in data["blocked_reason"]


def test_stage_2d7_preview_does_not_enforce_confirmation_yet():
    client = TestClient(app)

    response = client.post("/api/v1/presets/preview", json={"name": "engineering_all_channels_off"})

    assert response.status_code == 200
    data = response.json()
    assert data["requires_confirmation"] is True
    assert data["risk_level"] == "engineering"
    assert data["blocked"] is False
