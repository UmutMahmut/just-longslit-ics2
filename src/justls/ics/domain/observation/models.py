from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def new_obs_id() -> str:
    return f"obs-{uuid4().hex[:12]}"


def new_exp_id() -> str:
    return f"exp-{uuid4().hex[:12]}"


@dataclass(slots=True)
class FrameResult:
    frame_token: str | None
    file_uri: str | None
    kept: bool
    early_stop: bool
    discarded: bool
    checksum: str | None
    started_at_utc: str | None
    finished_at_utc: str | None
    result: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame_token": self.frame_token,
            "file_uri": self.file_uri,
            "kept": self.kept,
            "early_stop": self.early_stop,
            "discarded": self.discarded,
            "checksum": self.checksum,
            "started_at_utc": self.started_at_utc,
            "finished_at_utc": self.finished_at_utc,
            "result": self.result,
        }


@dataclass(slots=True)
class ObservationMeta:
    obs_id: str
    exp_id: str
    frame_type: str
    exp_time_s: float
    state: str
    created_at_utc: str
    started_at_utc: str | None = None
    finished_at_utc: str | None = None
    operator_note: str | None = None
    instrument_snapshot: dict[str, Any] | None = None
    calibration_snapshot: dict[str, Any] | None = None
    detector_config: dict[str, Any] | None = None
    preset_apply: dict[str, Any] | None = None
    setup_context: dict[str, Any] | None = None
    data_preview: dict[str, Any] | None = None
    frame_results: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        *,
        frame_type: str,
        exp_time_s: float,
        operator_note: str | None = None,
        instrument_snapshot: dict[str, Any] | None = None,
        calibration_snapshot: dict[str, Any] | None = None,
        detector_config: dict[str, Any] | None = None,
        preset_apply: dict[str, Any] | None = None,
        setup_context: dict[str, Any] | None = None,
        data_preview: dict[str, Any] | None = None,
    ) -> "ObservationMeta":
        return cls(
            obs_id=new_obs_id(),
            exp_id=new_exp_id(),
            frame_type=frame_type,
            exp_time_s=float(exp_time_s),
            state="armed",
            created_at_utc=utc_now_iso(),
            operator_note=operator_note,
            instrument_snapshot=instrument_snapshot,
            calibration_snapshot=calibration_snapshot,
            detector_config=detector_config,
            preset_apply=preset_apply,
            setup_context=setup_context,
            data_preview=data_preview,
        )

    def mark_exposing(self) -> None:
        self.state = "exposing"
        if self.started_at_utc is None:
            self.started_at_utc = utc_now_iso()

    def mark_completed(self, *, finished_at_utc: str | None = None) -> None:
        self.state = "completed"
        self.finished_at_utc = finished_at_utc or utc_now_iso()

    def mark_discarded(self, *, finished_at_utc: str | None = None) -> None:
        self.state = "discarded"
        self.finished_at_utc = finished_at_utc or utc_now_iso()

    def add_frame_result(self, frame_result: FrameResult) -> None:
        self.frame_results.append(frame_result.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "obs_id": self.obs_id,
            "exp_id": self.exp_id,
            "frame_type": self.frame_type,
            "exp_time_s": self.exp_time_s,
            "state": self.state,
            "created_at_utc": self.created_at_utc,
            "started_at_utc": self.started_at_utc,
            "finished_at_utc": self.finished_at_utc,
            "operator_note": self.operator_note,
            "instrument_snapshot": self.instrument_snapshot,
            "calibration_snapshot": self.calibration_snapshot,
            "detector_config": self.detector_config,
            "preset_apply": self.preset_apply,
            "setup_context": self.setup_context,
            "data_preview": self.data_preview,
            "frame_results": self.frame_results,
        }