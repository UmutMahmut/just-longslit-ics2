from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from justls.ics.app.api.dependencies import (
    ObservationPreviewServiceDep,
    ObservationServiceDep,
)
from justls.ics.app.api.schemas.observation import (
    ObservationArmReq,
    ObservationCommandFeedbackResponse,
)
from justls.ics.app.api.schemas.observation_preview import (
    ObservationPreviewReq,
    ObservationPreviewResponse,
)
from justls.ics.app.api.schemas.responses import ObservationStatusResponse
from justls.ics.application.dispatcher import DispatchResult
from justls.ics.domain.observation.models import (
    ObservationCommandFeedback,
    ObservationCommandName,
)
from justls.ics.kernel.errors import ICSException

router = APIRouter(prefix="/api/v1", tags=["observation"])


def _feedback_response(
    feedback: ObservationCommandFeedback,
) -> ObservationCommandFeedbackResponse:
    return ObservationCommandFeedbackResponse.from_domain(feedback)


def _feedback_error_response(
    feedback: ObservationCommandFeedback,
    *,
    status_code: int = 400,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=_feedback_response(feedback).model_dump(mode="json"),
    )


def _observation_command_response(
    *,
    command: ObservationCommandName,
    result: DispatchResult,
    observation_service: ObservationServiceDep,
) -> ObservationCommandFeedbackResponse | JSONResponse:
    feedback = observation_service.feedback_from_dispatch_result(command, result)
    if feedback.ok:
        return _feedback_response(feedback)
    return _feedback_error_response(feedback, status_code=400)


def _observation_exception_response(
    *,
    command: ObservationCommandName,
    exc: ICSException,
    observation_service: ObservationServiceDep,
) -> JSONResponse:
    feedback = observation_service.feedback_from_exception(command, exc)
    return _feedback_error_response(feedback, status_code=400)


@router.get("/observation/status", response_model=ObservationStatusResponse)
def get_observation_status(observation_service: ObservationServiceDep) -> ObservationStatusResponse:
    payload = observation_service.get_exposure_status()
    return ObservationStatusResponse.model_validate(payload)


@router.post(
    "/observation/preview",
    response_model=ObservationPreviewResponse,
)
def preview_observation(
    req: ObservationPreviewReq,
    observation_preview_service: ObservationPreviewServiceDep,
) -> ObservationPreviewResponse:
    preview = observation_preview_service.preview_request(req.to_domain())
    return ObservationPreviewResponse.model_validate(preview.model_dump(mode="json"))


@router.post(
    "/observation/arm",
    response_model=ObservationCommandFeedbackResponse,
    responses={
        400: {
            "model": ObservationCommandFeedbackResponse,
            "description": "Observation command rejected",
        }
    },
)
def arm_observation(
    req: ObservationArmReq,
    observation_service: ObservationServiceDep,
) -> ObservationCommandFeedbackResponse | JSONResponse:
    try:
        result = observation_service.arm(
            exp_time_s=req.exp_time_s,
            frame_type=req.frame_type,
            operator_note=req.operator_note,
        )
    except ICSException as exc:
        return _observation_exception_response(
            command=ObservationCommandName.ARM,
            exc=exc,
            observation_service=observation_service,
        )

    return _observation_command_response(
        command=ObservationCommandName.ARM,
        result=result,
        observation_service=observation_service,
    )


@router.post(
    "/observation/start",
    response_model=ObservationCommandFeedbackResponse,
    responses={
        400: {
            "model": ObservationCommandFeedbackResponse,
            "description": "Observation command rejected",
        }
    },
)
def start_observation(
    observation_service: ObservationServiceDep,
) -> ObservationCommandFeedbackResponse | JSONResponse:
    try:
        result = observation_service.start()
    except ICSException as exc:
        return _observation_exception_response(
            command=ObservationCommandName.START,
            exc=exc,
            observation_service=observation_service,
        )

    return _observation_command_response(
        command=ObservationCommandName.START,
        result=result,
        observation_service=observation_service,
    )


@router.post(
    "/observation/finish",
    response_model=ObservationCommandFeedbackResponse,
    responses={
        400: {
            "model": ObservationCommandFeedbackResponse,
            "description": "Observation command rejected",
        }
    },
)
def finish_observation(
    observation_service: ObservationServiceDep,
) -> ObservationCommandFeedbackResponse | JSONResponse:
    try:
        result = observation_service.finish()
    except ICSException as exc:
        return _observation_exception_response(
            command=ObservationCommandName.FINISH,
            exc=exc,
            observation_service=observation_service,
        )

    return _observation_command_response(
        command=ObservationCommandName.FINISH,
        result=result,
        observation_service=observation_service,
    )


@router.post(
    "/observation/stop_readout",
    response_model=ObservationCommandFeedbackResponse,
    responses={
        400: {
            "model": ObservationCommandFeedbackResponse,
            "description": "Observation command rejected",
        }
    },
)
def stop_readout_observation(
    observation_service: ObservationServiceDep,
) -> ObservationCommandFeedbackResponse | JSONResponse:
    try:
        result = observation_service.stop_readout()
    except ICSException as exc:
        return _observation_exception_response(
            command=ObservationCommandName.STOP_READOUT,
            exc=exc,
            observation_service=observation_service,
        )

    return _observation_command_response(
        command=ObservationCommandName.STOP_READOUT,
        result=result,
        observation_service=observation_service,
    )


@router.post(
    "/observation/abort_discard",
    response_model=ObservationCommandFeedbackResponse,
    responses={
        400: {
            "model": ObservationCommandFeedbackResponse,
            "description": "Observation command rejected",
        }
    },
)
def abort_discard_observation(
    observation_service: ObservationServiceDep,
) -> ObservationCommandFeedbackResponse | JSONResponse:
    try:
        result = observation_service.abort_discard()
    except ICSException as exc:
        return _observation_exception_response(
            command=ObservationCommandName.ABORT_DISCARD,
            exc=exc,
            observation_service=observation_service,
        )

    return _observation_command_response(
        command=ObservationCommandName.ABORT_DISCARD,
        result=result,
        observation_service=observation_service,
    )
