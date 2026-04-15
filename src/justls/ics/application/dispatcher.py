from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from justls.ics.kernel.errors import ICSException, InvalidParamError, UnsupportedError
from justls.ics.kernel.jobs import CommandRequest, JobRecord
from justls.ics.kernel.runtime import Runtime


Handler = Callable[[Runtime, CommandRequest], dict[str, Any] | None]


@dataclass(slots=True)
class DispatchResult:
    job: JobRecord
    payload: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "job": self.job.to_dict(),
            "payload": self.payload or {},
        }


class CommandDispatcher:
    def __init__(self, runtime: Runtime) -> None:
        self.runtime = runtime
        self._handlers: dict[tuple[str, str], Handler] = {}

    def register_handler(self, subsystem: str, action: str, handler: Handler) -> None:
        key = (subsystem, action)
        self._handlers[key] = handler

    def dispatch(self, request: CommandRequest) -> DispatchResult:
        key = (request.subsystem, request.action)
        handler = self._handlers.get(key)

        if handler is None:
            raise UnsupportedError(
                f"No handler registered for {request.subsystem}.{request.action}",
                subsystem=request.subsystem,
                details={"action": request.action},
            )

        job = self.runtime.create_job(
            request,
            subsystem_state_name=request.subsystem if request.subsystem in {"system", "slit", "lamps", "detector", "health"} else None,
        )

        try:
            self.runtime.mark_job_running(
                job.job_id,
                subsystem=request.subsystem if request.subsystem in {"system", "slit", "lamps", "detector", "health"} else None,
                message=f"Running {request.action}",
            )
            payload = handler(self.runtime, request) or {}
            job = self.runtime.mark_job_succeeded(
                job.job_id,
                subsystem=request.subsystem if request.subsystem in {"system", "slit", "lamps", "detector", "health"} else None,
                result=payload,
                message=f"Completed {request.action}",
            )
            return DispatchResult(job=job, payload=payload)

        except ICSException as exc:
            job = self.runtime.mark_job_failed(
                job.job_id,
                exc,
                subsystem=request.subsystem if request.subsystem in {"system", "slit", "lamps", "detector", "health"} else None,
                message=exc.info.message,
            )
            return DispatchResult(job=job, payload={"error": exc.to_dict()})

    def list_handlers(self) -> list[dict[str, str]]:
        return [
            {"subsystem": subsystem, "action": action}
            for subsystem, action in sorted(self._handlers.keys())
        ]


def validate_required_params(request: CommandRequest, required: set[str]) -> None:
    missing = [name for name in required if name not in request.params]
    if missing:
        raise InvalidParamError(
            f"Missing required params: {', '.join(missing)}",
            subsystem=request.subsystem,
            details={"missing": missing},
        )