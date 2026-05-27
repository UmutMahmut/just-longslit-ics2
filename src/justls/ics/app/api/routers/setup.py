from __future__ import annotations

from fastapi import APIRouter

from justls.ics.app.api.dependencies import SetupContextServiceDep
from justls.ics.app.api.schemas.responses import SetupContextResponse

router = APIRouter(prefix="/api/v1", tags=["setup"])


@router.get("/setup/context", response_model=SetupContextResponse)
def get_setup_context(
    setup_context_service: SetupContextServiceDep,
) -> SetupContextResponse:
    payload = setup_context_service.get_context_payload()
    return SetupContextResponse.model_validate(payload)