import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("src"))

from justls.ics.application.usecases.presets import build_preset_plan, list_presets
from justls.ics.app.main import app
from justls.ics.kernel.runtime import reset_runtime


def setup_function():
    reset_runtime()


def teardown_function():
    reset_runtime()


def test_stage_2d7_builtin_preset_plans_include_operational_metadata():
    science = build_preset_plan("science_default")
    rgb_safe = build_preset_plan("rgb_safe_default")
    engineering = build_preset_plan("engineering_all_channels_off")
    flat = build_preset_plan("calib_flat_default")

    assert science.category == "science"
    assert science.risk_level == "normal"
    assert science.requires_confirmation is False

    assert rgb_safe.category == "science"
    assert rgb_safe.risk_level == "normal"
    assert rgb_safe.requires_confirmation is False

    assert engineering.category == "engineering"
    assert engineering.risk_level == "engineering"
    assert engineering.requires_confirmation is True

    assert flat.category == "calibration"
    assert flat.risk_level == "high_impact"
    assert flat.requires_confirmation is True


def test_stage_2d7_list_presets_exposes_metadata_without_full_payloads():
    items = list_presets()
    by_name = {item["name"]: item for item in items}

    assert by_name["science_default"]["category"] == "science"
    assert by_name["science_default"]["risk_level"] == "normal"
    assert by_name["science_default"]["requires_confirmation"] is False

    assert by_name["calib_flat_default"]["category"] == "calibration"
    assert by_name["calib_flat_default"]["risk_level"] == "high_impact"
    assert by_name["calib_flat_default"]["requires_confirmation"] is True

    assert by_name["engineering_all_channels_off"]["category"] == "engineering"
    assert by_name["engineering_all_channels_off"]["risk_level"] == "engineering"
    assert by_name["engineering_all_channels_off"]["requires_confirmation"] is True

    assert "detector_config" not in by_name["science_default"]
    assert "calibration" not in by_name["science_default"]


def test_stage_2d7_presets_api_exposes_operational_metadata():
    client = TestClient(app)

    response = client.get("/api/v1/presets")

    assert response.status_code == 200
    data = response.json()
    by_name = {item["name"]: item for item in data["items"]}

    assert by_name["science_default"]["category"] == "science"
    assert by_name["science_default"]["risk_level"] == "normal"
    assert by_name["science_default"]["requires_confirmation"] is False

    assert by_name["calib_flat_default"]["category"] == "calibration"
    assert by_name["calib_flat_default"]["risk_level"] == "high_impact"
    assert by_name["calib_flat_default"]["requires_confirmation"] is True

    assert by_name["engineering_all_channels_off"]["category"] == "engineering"
    assert by_name["engineering_all_channels_off"]["risk_level"] == "engineering"
    assert by_name["engineering_all_channels_off"]["requires_confirmation"] is True


def test_stage_2d7_apply_preset_returns_structured_metadata_and_diff():
    client = TestClient(app)

    response = client.post("/api/v1/presets/apply", json={"name": "science_default"})

    assert response.status_code == 200
    data = response.json()
    assert data["applied_preset"] == "science_default"
    assert data["category"] == "science"
    assert data["risk_level"] == "normal"
    assert data["requires_confirmation"] is False
    assert data["detector_config"]["profile_name"] == "science-default"
    assert data["detector_config_changes"]
    assert data["changed_fields"]
    assert data["skipped_fields"] == []
    assert data["blocked_fields"] == []
