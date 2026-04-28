import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("src"))

from justls.ics.app.main import app
from justls.ics.kernel.runtime import reset_runtime


def setup_function():
    reset_runtime()


def teardown_function():
    reset_runtime()


def test_stage_2d7_observation_arm_records_latest_successful_preset_apply():
    client = TestClient(app)

    applied = client.post(
        "/api/v1/presets/apply",
        json={"name": "calib_flat_default", "confirmed": True},
    )
    assert applied.status_code == 200
    apply_data = applied.json()

    armed = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 5.0, "frame_type": "flat", "operator_note": "preset-link"},
    )
    assert armed.status_code == 200
    meta = armed.json()["observation_meta"]

    assert meta["preset_apply"]["job_id"] == apply_data["job_id"]
    assert meta["preset_apply"]["preset"] == "calib_flat_default"
    assert meta["preset_apply"]["category"] == "calibration"
    assert meta["preset_apply"]["risk_level"] == "high_impact"
    assert meta["preset_apply"]["requires_confirmation"] is True
    assert meta["preset_apply"]["changed_fields_count"] == len(apply_data["changed_fields"])
    assert meta["preset_apply"]["calibration_applied"] is True
    assert meta["preset_apply"]["slit_applied"] is False


def test_stage_2d7_observation_arm_without_prior_preset_has_null_preset_reference():
    client = TestClient(app)

    armed = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 5.0, "frame_type": "science", "operator_note": "no-preset"},
    )
    assert armed.status_code == 200
    meta = armed.json()["observation_meta"]

    assert meta["preset_apply"] is None


def test_stage_2d7_status_full_observation_meta_exposes_preset_reference():
    client = TestClient(app)

    applied = client.post(
        "/api/v1/presets/apply",
        json={"name": "calib_flat_default", "confirmed": True},
    )
    assert applied.status_code == 200
    apply_data = applied.json()

    armed = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 6.0, "frame_type": "flat", "operator_note": "status-preset-link"},
    )
    assert armed.status_code == 200

    status = client.get("/api/v1/status/full")
    assert status.status_code == 200
    meta = status.json()["observation"]["observation_meta"]

    assert meta["preset_apply"]["job_id"] == apply_data["job_id"]
    assert meta["preset_apply"]["preset"] == "calib_flat_default"
    assert meta["preset_apply"]["category"] == "calibration"
    assert meta["preset_apply"]["risk_level"] == "high_impact"
