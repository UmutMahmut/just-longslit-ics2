from __future__ import annotations

from justls.ics.application.dispatcher import DispatchResult
from justls.ics.application.services.setup_context_service import SetupContextService
from justls.ics.kernel.jobs import CommandRequest
from justls.ics.kernel.runtime import Runtime
from justls.ics.kernel.states import CommandSource


class ObservationService:
    def __init__(
        self,
        runtime: Runtime,
        dispatcher,
        setup_context_service: SetupContextService | None = None,
    ) -> None:
        self.runtime = runtime
        self.dispatcher = dispatcher
        self.setup_context_service = setup_context_service

    def get_exposure_status(self) -> dict:
        if self.runtime.detector is None:
            return {
                "state": self.runtime.get_snapshot().exposure_state.value,
                "armed_exposure": None,
                "last_exposure": None,
                "observation_meta": None,
            }
        return self.runtime.detector.get_snapshot().to_dict()

    def _setup_context_payloads(self) -> tuple[dict | None, dict | None]:
        if self.setup_context_service is None:
            return None, None

        context = self.setup_context_service.get_context()
        return context.to_persisted_dict(), context.data_preview()

    def arm(
        self,
        *,
        exp_time_s: float,
        frame_type: str = "science",
        operator_note: str | None = None,
    ) -> DispatchResult:
        setup_context, data_preview = self._setup_context_payloads()

        params = {
            "exp_time_s": exp_time_s,
            "frame_type": frame_type,
            "operator_note": operator_note,
        }
        if setup_context is not None:
            params["setup_context"] = setup_context
        if data_preview is not None:
            params["data_preview"] = data_preview

        request = CommandRequest.create(
            subsystem="detector",
            action="arm_exposure",
            params=params,
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