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


def test_normal_preset_apply_remains_backward_compatible():
    client = TestClient(app)

    response = client.post("/api/v1/presets/apply", json={"name": "science_default"})

    assert response.status_code == 200
    data = response.json()
    assert data["applied_preset"] == "science_default"
    assert data["detector_config"]["profile_name"] == "science-default"


def test_high_impact_preset_requires_confirmation():
    client = TestClient(app)

    response = client.post("/api/v1/presets/apply", json={"name": "calib_flat_default"})

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "confirmation_required"
    assert detail["message"] == "Preset calib_flat_default requires explicit confirmation before apply."
    assert detail["preset"] == "calib_flat_default"
    assert detail["category"] == "calibration"
    assert detail["risk_level"] == "high_impact"
    assert detail["requires_confirmation"] is True


def test_high_impact_preset_apply_succeeds_when_confirmed():
    client = TestClient(app)

    response = client.post(
        "/api/v1/presets/apply",
        json={"name": "calib_flat_default", "confirmed": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["applied_preset"] == "calib_flat_default"
    assert data["detector_config"]["profile_name"] == "calib-flat-default"
    assert data["calibration"]["mode"] == "calibration"
    assert data["calibration"]["active_lamp"] == "flat"
    assert data["calibration"]["lamp_enabled"] is True
    assert data["job_id"]


def test_apply_preset_records_latest_job():
    client = TestClient(app)

    response = client.post(
        "/api/v1/presets/apply",
        json={"name": "calib_flat_default", "confirmed": True},
    )
    assert response.status_code == 200
    applied = response.json()

    status = client.get("/api/v1/status/full")
    assert status.status_code == 200
    latest_job = status.json()["operational_status"]["latest_job"]

    assert latest_job["job_id"] == applied["job_id"]
    assert latest_job["status"] == "succeeded"
    assert latest_job["request"]["subsystem"] == "presets"
    assert latest_job["request"]["action"] == "apply_preset"
    assert latest_job["request"]["params"]["name"] == "calib_flat_default"
    assert latest_job["request"]["params"]["confirmed"] is True
    assert latest_job["result"]["kind"] == "preset_apply"
    assert latest_job["result"]["preset"] == "calib_flat_default"
    assert latest_job["result"]["category"] == "calibration"
    assert latest_job["result"]["risk_level"] == "high_impact"
    assert latest_job["result"]["changed_fields_count"] == len(applied["changed_fields"])
    assert latest_job["result"]["calibration_applied"] is True
    assert latest_job["result"]["slit_applied"] is False


def test_engineering_preset_requires_confirmation():
    client = TestClient(app)

    response = client.post(
        "/api/v1/presets/apply",
        json={"name": "engineering_all_channels_off"},
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "confirmation_required"
    assert detail["preset"] == "engineering_all_channels_off"
    assert detail["category"] == "engineering"
    assert detail["risk_level"] == "engineering"
    assert detail["requires_confirmation"] is True


def test_preview_still_does_not_require_confirmation():
    client = TestClient(app)

    response = client.post("/api/v1/presets/preview", json={"name": "calib_flat_default"})

    assert response.status_code == 200
    data = response.json()
    assert data["preset"] == "calib_flat_default"
    assert data["requires_confirmation"] is True
    assert data["blocked"] is False
