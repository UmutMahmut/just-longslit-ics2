from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ObservationArmReq(BaseModel):
    exp_time_s: float = Field(..., gt=0)
    frame_type: Literal["science", "flat", "arc", "test"] = "science"
    operator_note: str | None = None