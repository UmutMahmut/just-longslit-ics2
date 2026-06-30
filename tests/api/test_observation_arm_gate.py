from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from justls.ics.app.main import app
from justls.ics.kernel.runtime import reset_runtime


@pytest.fixture(autouse=True)
def _reset_runtime_singleton():
    reset_runtime()
    yield
    reset_runtime()


def test_api_observation_arm_rejected_when_preview_blocks_calibration_mismatch() -> None:
    client = TestClient(app)

    lamp = client.post(
        "/api/v1/calibration/lamp",
        json={"lamp": "flat", "enabled": True},
    )
    assert lamp.status_code == 200

    response = client.post(
        "/api/v1/observation/arm",
        json={"frame_type": "science", "exp_time_s": 30.0},
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "interlock_blocked"
    assert detail["subsystem"] == "detector"
    assert detail["details"]["preview"]["blocked"] is True
    assert detail["details"]["preview"]["single_exposure_compatible"] is False
    assert detail["details"]["blocked_components"] == ["calibration"]
    assert detail["details"]["validation_issue_codes"] == [
        "science_calibration_not_ready"
    ]

    status = client.get("/api/v1/observation/status").json()
    assert status["state"] == "ready_to_arm"
    assert status["armed_exposure"] is None


def test_api_observation_arm_rejected_when_detector_is_already_armed() -> None:
    client = TestClient(app)

    first = client.post(
        "/api/v1/observation/arm",
        json={"frame_type": "science", "exp_time_s": 5.0},
    )
    assert first.status_code == 200

    second = client.post(
        "/api/v1/observation/arm",
        json={"frame_type": "science", "exp_time_s": 30.0},
    )

    assert second.status_code == 400
    detail = second.json()["detail"]
    assert detail["code"] == "interlock_blocked"
    assert detail["details"]["preview"]["readiness"]["detector"]["state"] == "blocked"
    assert detail["details"]["blocked_components"] == ["detector"]
    assert detail["details"]["validation_issue_codes"] == []

    status = client.get("/api/v1/observation/status").json()
    assert status["state"] == "armed"
    assert status["armed_exposure"]["exp_time_s"] == 5.0
