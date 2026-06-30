from __future__ import annotations

from justls.ics.application.dispatcher import DispatchResult
from justls.ics.application.services.observation_preview_service import (
    ObservationPreviewService,
)
from justls.ics.application.services.setup_context_service import SetupContextService
from justls.ics.domain.observation.models import (
    ExposureSpec,
    ObservationPreviewResult,
    ObservationRequest,
)
from justls.ics.kernel.errors import InterlockBlockedError
from justls.ics.kernel.jobs import CommandRequest
from justls.ics.kernel.runtime import Runtime
from justls.ics.kernel.states import CommandSource


class ObservationService:
    def __init__(
        self,
        runtime: Runtime,
        dispatcher,
        setup_context_service: SetupContextService | None = None,
        preview_service: ObservationPreviewService | None = None,
    ) -> None:
        self.runtime = runtime
        self.dispatcher = dispatcher
        self.setup_context_service = setup_context_service
        self.preview_service = preview_service or ObservationPreviewService(
            runtime,
            setup_context_service,
        )

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

    def _arm_preview_request(
        self,
        *,
        exp_time_s: float,
        frame_type: str,
        operator_note: str | None,
        setup_context: dict | None,
    ) -> ObservationRequest:
        return ObservationRequest(
            exposures=[
                ExposureSpec(
                    frame_type=frame_type,
                    exp_time_s=exp_time_s,
                )
            ],
            operator_note=operator_note,
            setup_context=setup_context,
        )

    def _arm_gate_message(self, preview: ObservationPreviewResult) -> str:
        issue_codes = [issue.code for issue in preview.validation_issues]
        blocked_components = preview.readiness.blocked_components()

        if issue_codes and blocked_components:
            return (
                "Observation arm blocked by preview readiness gate: "
                f"issues={issue_codes}, blocked_components={blocked_components}."
            )
        if issue_codes:
            return (
                "Observation arm blocked by preview validation issues: "
                f"{issue_codes}."
            )
        if blocked_components:
            return (
                "Observation arm blocked by preview readiness components: "
                f"{blocked_components}."
            )
        return "Observation arm blocked by preview readiness gate."

    def _enforce_arm_preview_gate(
        self,
        *,
        exp_time_s: float,
        frame_type: str,
        operator_note: str | None,
        setup_context: dict | None,
    ) -> ObservationPreviewResult:
        request = self._arm_preview_request(
            exp_time_s=exp_time_s,
            frame_type=frame_type,
            operator_note=operator_note,
            setup_context=setup_context,
        )
        preview = self.preview_service.preview_request(request)

        if preview.blocked or not preview.single_exposure_compatible:
            raise InterlockBlockedError(
                self._arm_gate_message(preview),
                subsystem="detector",
                details={
                    "preview": preview.model_dump(mode="json"),
                    "blocked_components": preview.readiness.blocked_components(),
                    "validation_issue_codes": [
                        issue.code for issue in preview.validation_issues
                    ],
                },
            )

        return preview

    def arm(
        self,
        *,
        exp_time_s: float,
        frame_type: str = "science",
        operator_note: str | None = None,
    ) -> DispatchResult:
        setup_context, data_preview = self._setup_context_payloads()

        self._enforce_arm_preview_gate(
            exp_time_s=exp_time_s,
            frame_type=frame_type,
            operator_note=operator_note,
            setup_context=setup_context,
        )

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
