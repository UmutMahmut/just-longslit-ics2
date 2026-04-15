from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from justls.ics.domain.detector.config import DetectorConfig


class PresetCalibrationPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mode: str
    lamp: str | None = None
    enabled: bool = False


class PresetSlitPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    width_um: float | None = None
    angle_deg: float | None = None


class PresetPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    summary: str
    detector_config: DetectorConfig
    calibration: PresetCalibrationPlan | None = None
    slit: PresetSlitPlan | None = None

    def to_dict(self) -> dict:
        return self.model_dump()