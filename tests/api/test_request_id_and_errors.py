from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from justls.ics.application.dispatcher import CommandDispatcher, validate_required_params
from justls.ics.application.services.health_service import HealthService
from justls.ics.application.services.management_service import ManagementService
from justls.ics.application.services.observation_service import ObservationService
from justls.ics.app.main import app
from justls.ics.application.usecases.presets import (
    build_preset_config,
    build_preset_plan,
    list_presets,
)
from justls.ics.domain.detector.config import DetectorConfig
from justls.ics.kernel.errors import (
    ErrorCode,
    InvalidParamError,
    InvalidStateError,
    UnsupportedError,
)
from justls.ics.kernel.jobs import CommandRequest, JobTracker
from justls.ics.kernel.runtime import RuntimeAssembler, RuntimeConfig, reset_runtime
from justls.ics.kernel.states import (
    CommandSource,
    ControlState,
    ExposureState,
    RunMode,
    build_initial_state,
)


@pytest.fixture(autouse=True)
def _reset_runtime_singleton():
    reset_runtime()
    yield
    reset_runtime()


def test_stage_2d2_api_observation_invalid_start_returns_structured_error():
    client = TestClient(app)

    response = client.post("/api/v1/observation/start")
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert data["detail"]["code"] == "invalid_state"
    assert isinstance(data["detail"]["message"], str)
    assert data["detail"]["message"]

def test_stage_2d2_api_apply_unknown_preset_returns_structured_error():
    client = TestClient(app)

    response = client.post("/api/v1/presets/apply", json={"name": "not_exists"})
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert data["detail"]["code"] == "preset_not_found"
    assert data["detail"]["message"] == "Preset not found: not_exists"

def test_stage_2d2_api_success_response_includes_request_id_header():
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]

def test_stage_2d2_api_preserves_incoming_request_id_header():
    client = TestClient(app)

    response = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": "test-req-123"},
    )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-req-123"

def test_stage_2d2_api_validation_error_includes_request_id_header():
    client = TestClient(app)

    response = client.post("/api/v1/slit", json={"width_um": 0})
    assert response.status_code == 422
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]

def test_stage_2d2_api_internal_error_includes_request_id_header_and_detail():
    route_path = "/api/v1/_test/internal-error-request-id"

    existing_paths = {route.path for route in app.router.routes}
    if route_path not in existing_paths:
        @app.get(route_path, include_in_schema=False)
        def _test_internal_error_request_id():
            raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get(route_path)
    assert response.status_code == 500

    data = response.json()
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]

    assert "detail" in data
    assert data["detail"]["code"] == "internal_error"
    assert data["detail"]["message"] == "Internal server error."
    assert data["detail"]["request_id"] == response.headers["X-Request-ID"]
