from __future__ import annotations

from datetime import datetime, timezone

from justls.ics.kernel.runtime import Runtime


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class HealthService:
    def __init__(self, runtime: Runtime) -> None:
        self.runtime = runtime

    def get_state_dto(self) -> dict:
        slit_snapshot = self.runtime.slit.get_snapshot() if self.runtime.slit is not None else None
        lamp_snapshot = self.runtime.lamps.get_snapshot() if self.runtime.lamps is not None else None

        return {
            "slit_width_um": slit_snapshot.width_um if slit_snapshot is not None else None,
            "slit_angle_deg": slit_snapshot.angle_deg if slit_snapshot is not None else None,
            "lamp_on": lamp_snapshot.lamp_enabled if lamp_snapshot is not None else False,
            "temperature_c": None,
        }

    def get_capabilities(self) -> dict:
        return self.runtime.get_capabilities_dict()

    def get_calibration_status(self) -> dict | None:
        if self.runtime.lamps is None:
            return None
        return self.runtime.lamps.get_snapshot().to_dict()

    def get_observation_status(self) -> dict | None:
        if self.runtime.detector is None:
            return None
        return self.runtime.detector.get_snapshot().to_dict()

    def get_status_full(self) -> dict:
        return {
            "state": self.get_state_dto(),
            "capabilities": self.get_capabilities(),
            "calibration": self.get_calibration_status(),
            "observation": self.get_observation_status(),
            "detector_config": self.runtime.get_detector_config_dict(),
            "hal": self.runtime.config.run_mode.value,
            "run_mode": self.runtime.config.run_mode.value,
            "timestamp_utc": utc_now_iso(),
        }

    def get_health(self) -> dict:
        return {
            "ok": True,
            "service": "just-longslit-ics-2.0",
            "runtime": self.runtime.status_dict(),
        }

    def get_status(self) -> dict:
        return self.get_status_full()