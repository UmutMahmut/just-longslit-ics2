from __future__ import annotations

from justls.ics.application.dispatcher import DispatchResult
from justls.ics.kernel.jobs import CommandRequest
from justls.ics.kernel.runtime import Runtime
from justls.ics.kernel.states import CommandSource


class ObservationService:
    def __init__(self, runtime: Runtime, dispatcher) -> None:
        self.runtime = runtime
        self.dispatcher = dispatcher

    def get_exposure_status(self) -> dict:
        if self.runtime.detector is None:
            return {
                "state": self.runtime.get_snapshot().exposure_state.value,
                "armed_exposure": None,
                "last_exposure": None,
                "observation_meta": None,
            }
        return self.runtime.detector.get_snapshot().to_dict()

    def arm(
        self,
        *,
        exp_time_s: float,
        frame_type: str = "science",
        operator_note: str | None = None,
    ) -> DispatchResult:
        request = CommandRequest.create(
            subsystem="detector",
            action="arm_exposure",
            params={
                "exp_time_s": exp_time_s,
                "frame_type": frame_type,
                "operator_note": operator_note,
            },
            source=CommandSource.API,
        )
        return self.dispatcher.dispatch(request)

    def start(self) -> DispatchResult:
        request = CommandRequest.create(
            subsystem="detector",
            action="start_exposure",
            params={},
            source=CommandSource.API,
        )
        return self.dispatcher.dispatch(request)

    def finish(self) -> DispatchResult:
        request = CommandRequest.create(
            subsystem="detector",
            action="finish_exposure",
            params={},
            source=CommandSource.API,
        )
        return self.dispatcher.dispatch(request)

    def stop_readout(self) -> DispatchResult:
        request = CommandRequest.create(
            subsystem="detector",
            action="stop_readout",
            params={},
            source=CommandSource.API,
        )
        return self.dispatcher.dispatch(request)

    def abort_discard(self) -> DispatchResult:
        request = CommandRequest.create(
            subsystem="detector",
            action="abort_discard",
            params={},
            source=CommandSource.API,
        )
        return self.dispatcher.dispatch(request)