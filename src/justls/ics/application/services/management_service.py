from __future__ import annotations

from justls.ics.application.usecases.preset_plan import PresetPlan
from justls.ics.domain.detector.config import DetectorConfig
from justls.ics.kernel.runtime import Runtime
from justls.ics.kernel.states import ControlState


class ManagementService:
    def __init__(self, runtime: Runtime) -> None:
        self.runtime = runtime

    def set_connected(self, subsystem: str, connected: bool, *, message: str = "") -> dict:
        state = self.runtime.set_subsystem_connected(subsystem, connected, message=message)
        return state.to_dict()

    def set_state(self, subsystem: str, state: ControlState, *, message: str = "") -> dict:
        updated = self.runtime.set_subsystem_state(subsystem, state, message=message)
        return updated.to_dict()

    def get_detector_config(self) -> DetectorConfig:
        return self.runtime.get_detector_config()

    def get_detector_config_dict(self) -> dict:
        return self.runtime.get_detector_config_dict()

    def set_detector_config(self, config: DetectorConfig | dict) -> dict:
        updated = self.runtime.set_detector_config(config)
        return updated.to_dict()

    def apply_preset_plan(self, plan: PresetPlan) -> dict:
        detector_config = self.runtime.set_detector_config(plan.detector_config).to_dict()

        calibration_result = None
        calibration_applied = False

        if plan.calibration is not None and self.runtime.lamps is not None:
            if plan.calibration.mode == "science":
                snapshot = self.runtime.lamps.set_mode("science")
                calibration_result = snapshot.to_dict()
                calibration_applied = True
            elif plan.calibration.mode == "calibration":
                self.runtime.lamps.set_mode("calibration")
                if plan.calibration.lamp is not None:
                    snapshot = self.runtime.lamps.select_lamp(
                        plan.calibration.lamp,
                        enable=plan.calibration.enabled,
                    )
                else:
                    snapshot = self.runtime.lamps.get_snapshot()
                calibration_result = snapshot.to_dict()
                calibration_applied = True

        return {
            "applied_preset": plan.name,
            "summary": plan.summary,
            "detector_config": detector_config,
            "calibration": calibration_result,
            "calibration_applied": calibration_applied,
            "slit_plan": plan.slit.to_dict() if plan.slit is not None else None,
            "slit_applied": False,
        }