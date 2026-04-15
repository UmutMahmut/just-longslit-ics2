from __future__ import annotations

from fastapi import APIRouter

from justls.ics.app.api.dependencies import ObservationServiceDep
from justls.ics.app.api.errors import raise_dispatch_failure
from justls.ics.app.api.schemas.observation import ObservationArmReq
from justls.ics.app.api.schemas.responses import (
    ApiErrorResponse,
    ObservationStatusResponse,
)
from justls.ics.application.dispatcher import DispatchResult

router = APIRouter(prefix="/api/v1", tags=["observation"])


def _unwrap_observation_result(result: DispatchResult) -> ObservationStatusResponse:
    if result.job.status.value == "failed":
        raise_dispatch_failure(result, default_code="invalid_state")

    return ObservationStatusResponse.model_validate(result.payload)


@router.get("/observation/status", response_model=ObservationStatusResponse)
def get_observation_status(observation_service: ObservationServiceDep) -> ObservationStatusResponse:
    payload = observation_service.get_exposure_status()
    return ObservationStatusResponse.model_validate(payload)


@router.post(
    "/observation/arm",
    response_model=ObservationStatusResponse,
    responses={400: {"model": ApiErrorResponse, "description": "Observation request rejected"}},
)
def arm_observation(
    req: ObservationArmReq,
    observation_service: ObservationServiceDep,
) -> ObservationStatusResponse:
    result = observation_service.arm(
        exp_time_s=req.exp_time_s,
        frame_type=req.frame_type,
        operator_note=req.operator_note,
    )
    return _unwrap_observation_result(result)


@router.post(
    "/observation/start",
    response_model=ObservationStatusResponse,
    responses={400: {"model": ApiErrorResponse, "description": "Observation request rejected"}},
)
def start_observation(observation_service: ObservationServiceDep) -> ObservationStatusResponse:
    result = observation_service.start()
    return _unwrap_observation_result(result)


@router.post(
    "/observation/finish",
    response_model=ObservationStatusResponse,
    responses={400: {"model": ApiErrorResponse, "description": "Observation request rejected"}},
)
def finish_observation(observation_service: ObservationServiceDep) -> ObservationStatusResponse:
    result = observation_service.finish()
    return _unwrap_observation_result(result)


@router.post(
    "/observation/stop_readout",
    response_model=ObservationStatusResponse,
    responses={400: {"model": ApiErrorResponse, "description": "Observation request rejected"}},
)
def stop_readout_observation(observation_service: ObservationServiceDep) -> ObservationStatusResponse:
    result = observation_service.stop_readout()
    return _unwrap_observation_result(result)


@router.post(
    "/observation/abort_discard",
    response_model=ObservationStatusResponse,
    responses={400: {"model": ApiErrorResponse, "description": "Observation request rejected"}},
)
def abort_discard_observation(observation_service: ObservationServiceDep) -> ObservationStatusResponse:
    result = observation_service.abort_discard()
    return _unwrap_observation_result(result)