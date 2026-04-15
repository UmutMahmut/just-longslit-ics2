from __future__ import annotations

from abc import ABC, abstractmethod

from justls.ics.drivers.sim.detector_driver import SimDetectorDriver


class BaseDetectorAdapter(ABC):
    @abstractmethod
    def acquire_exposure(
        self,
        *,
        obs_id: str,
        exp_time_s: float,
        frame_type: str,
    ) -> dict: ...


class SimDetectorAdapter(BaseDetectorAdapter):
    def __init__(self, driver: SimDetectorDriver) -> None:
        self.driver = driver

    def acquire_exposure(
        self,
        *,
        obs_id: str,
        exp_time_s: float,
        frame_type: str,
    ) -> dict:
        return self.driver.acquire_exposure(
            obs_id=obs_id,
            exp_time_s=exp_time_s,
            frame_type=frame_type,
        )