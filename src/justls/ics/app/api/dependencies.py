from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from justls.ics.application.dispatcher import CommandDispatcher, validate_required_params
from justls.ics.application.services.health_service import HealthService
from justls.ics.application.services.management_service import ManagementService
from justls.ics.application.services.observation_service import ObservationService
from justls.ics.kernel.errors import InvalidStateError, UnsupportedError
from justls.ics.kernel.runtime import Runtime, get_runtime


def get_runtime_dependency() -> Runtime:
    return get_runtime()


RuntimeDep = Annotated[Runtime, Depends(get_runtime_dependency)]


def get_health_service(runtime: RuntimeDep) -> HealthService:
    return HealthService(runtime)


def get_management_service(runtime: RuntimeDep) -> ManagementService:
    return ManagementService(runtime)


def _require_slit(runtime: Runtime):
    if runtime.slit is None:
        raise UnsupportedError(
            "Slit subsystem is unavailable.",
            subsystem="slit",
        )
    return runtime.slit


def _require_lamps(runtime: Runtime):
    if runtime.lamps is None:
        raise UnsupportedError(
            "Calibration subsystem is unavailable.",
            subsystem="lamps",
        )
    return runtime.lamps


def _require_detector(runtime: Runtime):
    if runtime.detector is None:
        raise UnsupportedError(
            "Detector subsystem is unavailable.",
            subsystem="detector",
        )
    return runtime.detector


def _assert_observation_mutation_allowed(runtime: Runtime, action_name: str) -> None:
    if runtime.detector is None:
        return

    state = runtime.detector.get_snapshot().state.value
    if state in {"armed", "exposing"}:
        raise InvalidStateError(
            f"{action_name} is blocked while observation state is {state}",
            subsystem="detector",
            details={
                "observation_state": state,
                "blocked_action": action_name,
            },
        )


def _handle_slit_set_width(runtime: Runtime, request):
    _assert_observation_mutation_allowed(runtime, "set_slit_width")
    validate_required_params(request, {"width_um"})
    slit = _require_slit(runtime)
    snapshot = slit.set_width_um(float(request.params["width_um"]))
    return snapshot.to_state_fragment()


def _handle_slit_set_angle(runtime: Runtime, request):
    _assert_observation_mutation_allowed(runtime, "set_slit_angle")
    validate_required_params(request, {"angle_deg"})
    slit = _require_slit(runtime)
    snapshot = slit.set_angle_deg(float(request.params["angle_deg"]))
    return snapshot.to_state_fragment()


def _handle_lamp_legacy_set(runtime: Runtime, request):
    _assert_observation_mutation_allowed(runtime, "set_legacy_lamp")
    validate_required_params(request, {"on"})
    lamps = _require_lamps(runtime)
    snapshot = lamps.set_legacy_on(bool(request.params["on"]))
    return snapshot.to_legacy_state_fragment()


def _handle_calibration_set_mode(runtime: Runtime, request):
    _assert_observation_mutation_allowed(runtime, "set_calibration_mode")
    validate_required_params(request, {"mode"})
    lamps = _require_lamps(runtime)
    snapshot = lamps.set_mode(str(request.params["mode"]))
    return snapshot.to_dict()


def _handle_calibration_select_lamp(runtime: Runtime, request):
    _assert_observation_mutation_allowed(runtime, "select_calibration_lamp")
    validate_required_params(request, {"lamp", "enabled"})
    lamps = _require_lamps(runtime)
    snapshot = lamps.select_lamp(
        str(request.params["lamp"]),
        enable=bool(request.params["enabled"]),
    )
    return snapshot.to_dict()


def _handle_observation_arm(runtime: Runtime, request):
    validate_required_params(request, {"exp_time_s", "frame_type"})

    detector = _require_detector(runtime)

    instrument_snapshot = None
    if runtime.slit is not None:
        instrument_snapshot = runtime.slit.get_snapshot().to_state_fragment()

    calibration_snapshot = None
    if runtime.lamps is not None:
        calibration_snapshot = runtime.lamps.get_snapshot().to_dict()

    detector_config = runtime.get_detector_config_dict()

    snapshot = detector.arm(
        exp_time_s=float(request.params["exp_time_s"]),
        frame_type=str(request.params["frame_type"]),
        operator_note=request.params.get("operator_note"),
        instrument_snapshot=instrument_snapshot,
        calibration_snapshot=calibration_snapshot,
        detector_config=detector_config,
    )
    return snapshot.to_dict()


def _handle_observation_start(runtime: Runtime, request):
    detector = _require_detector(runtime)
    snapshot = detector.start()
    return snapshot.to_dict()


def _handle_observation_finish(runtime: Runtime, request):
    detector = _require_detector(runtime)
    snapshot = detector.finish_normal()
    return snapshot.to_dict()


def _handle_observation_stop_readout(runtime: Runtime, request):
    detector = _require_detector(runtime)
    snapshot = detector.stop_and_readout()
    return snapshot.to_dict()


def _handle_observation_abort_discard(runtime: Runtime, request):
    detector = _require_detector(runtime)
    snapshot = detector.abort_discard()
    return snapshot.to_dict()


def get_dispatcher(runtime: RuntimeDep) -> CommandDispatcher:
    dispatcher = CommandDispatcher(runtime)
    dispatcher.register_handler("slit", "set_width", _handle_slit_set_width)
    dispatcher.register_handler("slit", "set_angle", _handle_slit_set_angle)
    dispatcher.register_handler("lamps", "set_legacy_on", _handle_lamp_legacy_set)
    dispatcher.register_handler("lamps", "set_mode", _handle_calibration_set_mode)
    dispatcher.register_handler("lamps", "select_lamp", _handle_calibration_select_lamp)
    dispatcher.register_handler("detector", "arm_exposure", _handle_observation_arm)
    dispatcher.register_handler("detector", "start_exposure", _handle_observation_start)
    dispatcher.register_handler("detector", "finish_exposure", _handle_observation_finish)
    dispatcher.register_handler("detector", "stop_readout", _handle_observation_stop_readout)
    dispatcher.register_handler("detector", "abort_discard", _handle_observation_abort_discard)
    return dispatcher


DispatcherDep = Annotated[CommandDispatcher, Depends(get_dispatcher)]
HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]
ManagementServiceDep = Annotated[ManagementService, Depends(get_management_service)]


def get_observation_service(
    runtime: RuntimeDep,
    dispatcher: DispatcherDep,
) -> ObservationService:
    return ObservationService(runtime, dispatcher)


ObservationServiceDep = Annotated[ObservationService, Depends(get_observation_service)]
