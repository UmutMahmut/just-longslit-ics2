from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SimDetectorDriver:
    def acquire_exposure(
        self,
        *,
        obs_id: str,
        exp_time_s: float,
        frame_type: str,
    ) -> dict:
        return {
            "obs_id": obs_id,
            "frame_type": frame_type,
            "exp_time_s": exp_time_s,
            "frame_token": f"frame-{uuid4().hex[:12]}",
            "started_at": utc_now_iso(),
            "finished_at": utc_now_iso(),
            "result": "completed",
        }