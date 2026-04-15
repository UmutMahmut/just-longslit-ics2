from __future__ import annotations

from fastapi import APIRouter

from justls.ics.app.api.dependencies import ManagementServiceDep
from justls.ics.domain.detector.config import DetectorConfig

router = APIRouter(prefix="/api/v1", tags=["detector"])


@router.get("/detector/config", response_model=DetectorConfig)
def get_detector_config(management_service: ManagementServiceDep) -> DetectorConfig:
    return DetectorConfig.model_validate(management_service.get_detector_config_dict())


@router.post("/detector/config", response_model=DetectorConfig)
def set_detector_config(
    req: DetectorConfig,
    management_service: ManagementServiceDep,
) -> DetectorConfig:
    return DetectorConfig.model_validate(management_service.set_detector_config(req))