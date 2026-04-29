from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from justls.ics.app.api.errors import build_api_error_detail
from justls.ics.app.api.routers.detector import router as detector_router
from justls.ics.app.api.routers.health import router as health_router
from justls.ics.app.api.routers.lamps import router as lamps_router
from justls.ics.app.api.routers.observation import router as observation_router
from justls.ics.app.api.routers.presets import router as presets_router
from justls.ics.app.api.routers.slit import router as slit_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="JUST Long-Slit ICS 2.0",
    version="0.0.1",
    description="Rebuilt internal control kernel for JUST long-slit spectrograph ICS.",
)


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    incoming = request.headers.get("X-Request-ID")
    request_id = incoming.strip() if incoming and incoming.strip() else uuid.uuid4().hex

    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(
    request: Request,
    exc: RequestValidationError,
):
    request_id = getattr(request.state, "request_id", None)

    response = JSONResponse(
        status_code=422,
        content={
            "detail": build_api_error_detail(
                code="validation_error",
                message="Request validation failed.",
                errors=exc.errors(),
            )
        },
    )
    if request_id:
        response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def handle_unexpected_exception(
    request: Request,
    exc: Exception,
):
    request_id = getattr(request.state, "request_id", None)

    logger.exception(
        "Unhandled exception. request_id=%s path=%s",
        request_id,
        request.url.path,
        exc_info=exc,
    )

    response = JSONResponse(
        status_code=500,
        content={
            "detail": build_api_error_detail(
                code="internal_error",
                message="Internal server error.",
                request_id=request_id,
            )
        },
    )
    if request_id:
        response.headers["X-Request-ID"] = request_id
    return response


app.include_router(health_router)
app.include_router(slit_router)
app.include_router(lamps_router)
app.include_router(observation_router)
app.include_router(detector_router)
app.include_router(presets_router)

UI_DIR = Path(__file__).resolve().parent / "ui"
UI_ENTRY = UI_DIR / "ui_alpha_skeleton_v5.html"
UI_V6_ENTRY = UI_DIR / "ui_operational_v6.html"
UI_V7_ENTRY = UI_DIR / "ui_operational_v7.html"
UI_PHASE_2D6_ADAPTER = "/ui-assets/phase2d6_operational_status.js"

PHASE_2D6_V5_ADAPTER_ENABLED_ENV = "JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED"
PHASE_2D6_V6_ENABLED_ENV = "JUSTLS_UI_V6_ENABLED"
PHASE_2D8_V7_ENABLED_ENV = "JUSTLS_UI_V7_ENABLED"

if UI_DIR.exists():
    app.mount("/ui-assets", StaticFiles(directory=UI_DIR), name="ui-assets")


def env_flag(name: str, *, default: bool = True) -> bool:
    """Read a simple boolean environment flag.

    The default remains enabled so normal local development keeps the Phase 2.6
    review UI visible. Operators can set the variable to 0/false/no/off to
    disable the feature without reverting code.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off", "disabled"}


def phase_2d6_v5_adapter_enabled() -> bool:
    return env_flag(PHASE_2D6_V5_ADAPTER_ENABLED_ENV, default=True)


def phase_2d6_v6_enabled() -> bool:
    return env_flag(PHASE_2D6_V6_ENABLED_ENV, default=True)


def phase_2d8_v7_enabled() -> bool:
    return env_flag(PHASE_2D8_V7_ENABLED_ENV, default=True)


def inject_phase_2d6_ui_adapter(html: str) -> str:
    """Attach the Phase 2.6 operational-status adapter to the static UI.

    The adapter lets the existing v5 skeleton consume the new backend
    `operational_status` block without copying or rewriting the large HTML file.
    """
    adapter_tag = f'<script src="{UI_PHASE_2D6_ADAPTER}" defer></script>'
    if adapter_tag in html:
        return html
    if "</body>" in html:
        return html.replace("</body>", f"  {adapter_tag}\n</body>")
    return f"{html}\n{adapter_tag}\n"


def serve_html(path: Path, *, inject_adapter: bool = False):
    if path.exists():
        html = path.read_text(encoding="utf-8")
        if inject_adapter:
            html = inject_phase_2d6_ui_adapter(html)
        return HTMLResponse(html)
    return {
        "message": "UI entry not found.",
        "expected": str(path),
    }


@app.get("/")
def read_root() -> dict:
    return {
        "message": "JUST Long-Slit ICS 2.0 is running.",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "ui": "/ui" if UI_ENTRY.exists() else None,
        "ui_v6": "/ui/v6" if UI_V6_ENTRY.exists() and phase_2d6_v6_enabled() else None,
        "ui_v7": "/ui/v7" if UI_V7_ENTRY.exists() and phase_2d8_v7_enabled() else None,
        "ui_safety_switches": {
            "phase2d6_v5_adapter_enabled": phase_2d6_v5_adapter_enabled(),
            "phase2d6_v6_enabled": phase_2d6_v6_enabled(),
            "phase2d8_v7_enabled": phase_2d8_v7_enabled(),
        },
    }


@app.get("/ui", include_in_schema=False)
def read_ui():
    return serve_html(UI_ENTRY, inject_adapter=phase_2d6_v5_adapter_enabled())


@app.get("/ui/v6", include_in_schema=False)
def read_ui_v6():
    if not phase_2d6_v6_enabled():
        raise HTTPException(status_code=404, detail="Operational UI v6 is disabled.")
    return serve_html(UI_V6_ENTRY)


@app.get("/ui/v7", include_in_schema=False)
def read_ui_v7():
    if not phase_2d8_v7_enabled():
        raise HTTPException(status_code=404, detail="Operational UI v7 is disabled.")
    return serve_html(UI_V7_ENTRY)
