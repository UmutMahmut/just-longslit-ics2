from __future__ import annotations

from fastapi import APIRouter

from justls.ics.app.api.dependencies import ManagementServiceDep
from justls.ics.app.api.errors import raise_api_error
from justls.ics.app.api.schemas.presets import PresetApplyReq
from justls.ics.app.api.schemas.responses import (
    ApiErrorResponse,
    PresetApplyResponse,
    PresetListResponse,
)
from justls.ics.application.usecases.presets import build_preset_plan, list_presets

router = APIRouter(prefix="/api/v1", tags=["presets"])


@router.get("/presets", response_model=PresetListResponse)
def get_presets() -> PresetListResponse:
    return PresetListResponse(items=list_presets())


@router.post(
    "/presets/apply",
    response_model=PresetApplyResponse,
    responses={404: {"model": ApiErrorResponse, "description": "Preset not found"}},
)
def apply_preset(
    req: PresetApplyReq,
    management_service: ManagementServiceDep,
) -> PresetApplyResponse:
    try:
        plan = build_preset_plan(req.name)
    except KeyError:
        raise_api_error(
            status_code=404,
            code="preset_not_found",
            message=f"Preset not found: {req.name}",
        )

    payload = management_service.apply_preset_plan(plan)
    return PresetApplyResponse.model_validate(payload)