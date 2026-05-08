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
UI_PHASE_2D6_ADAPTER = "/ui-assets/v5/phase2d6_operational_status.js"
UI_V7_RUNTIME_STATUS = "/ui-assets/v7/runtime_status.js"
UI_V7_INSTRUMENT_RUNTIME = "/ui-assets/v7/instrument_runtime.js"
UI_V7_PRESET_RUNTIME = "/ui-assets/v7/preset_runtime.js"
UI_V7_OBSERVE_RUNTIME = "/ui-assets/v7/observe_runtime.js"
UI_V7_OBSERVE_GUARD = "/ui-assets/v7/observe_guard.js"

PHASE_2D6_V5_ADAPTER_ENABLED_ENV = "JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED"
PHASE_2D6_V6_ENABLED_ENV = "JUSTLS_UI_V6_ENABLED"
PHASE_2D8_V7_ENABLED_ENV = "JUSTLS_UI_V7_ENABLED"
PHASE_2D8_V7_RUNTIME_ENABLED_ENV = "JUSTLS_UI_V7_RUNTIME_ENABLED"
PHASE_2D8_V7_RUNTIME_STATUS_ENABLED_ENV = "JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED"
PHASE_2D8_V7_INSTRUMENT_RUNTIME_ENABLED_ENV = "JUSTLS_UI_V7_INSTRUMENT_RUNTIME_ENABLED"
PHASE_2D8_V7_PRESET_RUNTIME_ENABLED_ENV = "JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED"
PHASE_2D8_V7_OBSERVE_RUNTIME_ENABLED_ENV = "JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED"
PHASE_2D8_V7_OBSERVE_GUARD_ENABLED_ENV = "JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED"

if UI_DIR.exists():
    app.mount("/ui-assets", StaticFiles(directory=UI_DIR), name="ui-assets")


def env_flag(name: str, *, default: bool = True) -> bool:
    """Read a simple boolean environment flag.

    Operators can set the variable to 0/false/no/off to disable the feature, or
    1/true/yes/on to enable it.
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


def phase_2d8_v7_runtime_enabled() -> bool:
    # Keep the v7 static shell safe by default. Runtime add-ons can be enabled
    # explicitly during targeted debugging/local testing.
    return env_flag(PHASE_2D8_V7_RUNTIME_ENABLED_ENV, default=False)


def phase_2d8_v7_runtime_status_enabled() -> bool:
    # When the v7 runtime master gate is enabled, status is the first and safest
    # runtime module to restore during Phase 2.8-G.
    return env_flag(PHASE_2D8_V7_RUNTIME_STATUS_ENABLED_ENV, default=True)


def phase_2d8_v7_instrument_runtime_enabled() -> bool:
    return env_flag(PHASE_2D8_V7_INSTRUMENT_RUNTIME_ENABLED_ENV, default=False)


def phase_2d8_v7_preset_runtime_enabled() -> bool:
    return env_flag(PHASE_2D8_V7_PRESET_RUNTIME_ENABLED_ENV, default=False)


def phase_2d8_v7_observe_runtime_enabled() -> bool:
    return env_flag(PHASE_2D8_V7_OBSERVE_RUNTIME_ENABLED_ENV, default=False)


def phase_2d8_v7_observe_guard_enabled() -> bool:
    return env_flag(PHASE_2D8_V7_OBSERVE_GUARD_ENABLED_ENV, default=False)


def phase_2d8_v7_runtime_module_flags() -> dict[str, bool]:
    if not phase_2d8_v7_runtime_enabled():
        return {
            "status": False,
            "instrument": False,
            "presets": False,
            "observe": False,
            "observe_guard": False,
        }
    return {
        "status": phase_2d8_v7_runtime_status_enabled(),
        "instrument": phase_2d8_v7_instrument_runtime_enabled(),
        "presets": phase_2d8_v7_preset_runtime_enabled(),
        "observe": phase_2d8_v7_observe_runtime_enabled(),
        "observe_guard": phase_2d8_v7_observe_guard_enabled(),
    }


def phase_2d8_v7_runtime_scripts() -> tuple[str, ...]:
    flags = phase_2d8_v7_runtime_module_flags()
    scripts: list[str] = []
    if flags["status"]:
        scripts.append(UI_V7_RUNTIME_STATUS)
    if flags["instrument"]:
        scripts.append(UI_V7_INSTRUMENT_RUNTIME)
    if flags["presets"]:
        scripts.append(UI_V7_PRESET_RUNTIME)
    if flags["observe"]:
        scripts.append(UI_V7_OBSERVE_RUNTIME)
    if flags["observe_guard"]:
        scripts.append(UI_V7_OBSERVE_GUARD)
    return tuple(scripts)


def inject_script_tag(html: str, script_src: str) -> str:
    tag = f'<script src="{script_src}" defer></script>'
    if tag in html:
        return html
    if "</body>" in html:
        return html.replace("</body>", f"  {tag}\n</body>")
    return f"{html}\n{tag}\n"


def inject_phase_2d6_ui_adapter(html: str) -> str:
    """Attach the Phase 2.6 operational-status adapter to the static v5 UI."""
    return inject_script_tag(html, UI_PHASE_2D6_ADAPTER)


def expand_v7_feedback_rail(html: str) -> str:
    """Ensure /ui/v7 exposes durable H2 feedback rail binding points.

    This keeps the served v7.1 shell compatible with the H2 feedback baseline
    even when older static files still contain the compact footer rail.
    """
    if 'data-bind="v7.message.severity"' in html:
        return html

    compact_footer = """    <footer class="rail" data-role="v7-message-rail">
      <strong>Message Rail</strong>
      <span data-bind="v7.message.text">v7.1 shell ready. Instrument / Configure is static-first; runtime modules remain opt-in.</span>
      <code data-bind="v7.message.phase">Phase 2.8-H</code>
    </footer>"""
    expanded_footer = """    <footer class="rail" data-role="v7-message-rail" data-severity="info" data-connection="static">
      <strong>Operator Feedback</strong>
      <div data-role="v7-feedback-summary">
        <span data-bind="v7.message.text">v7.1 shell ready. Instrument / Configure is static-first; runtime modules remain opt-in.</span>
        <div class="badge-row" aria-label="operator feedback telemetry">
          <span class="badge demo">Severity <code data-bind="v7.message.severity">INFO</code></span>
          <span class="badge future">Connection <code data-bind="v7.message.connection">static</code></span>
          <span class="badge future">RTT <code data-bind="v7.message.rtt_ms">not measured</code></span>
          <span class="badge future">Last OK <code data-bind="v7.message.last_ok_at">not available</code></span>
          <span class="badge future">Request <code data-bind="v7.message.request_id">not available</code></span>
          <span class="badge future">Poll <code data-bind="v7.message.poll_count">0</code></span>
          <span class="badge future">Freshness <code data-bind="v7.message.freshness">not available</code></span>
        </div>
      </div>
      <code data-bind="v7.message.phase">Phase 2.8-H</code>
    </footer>"""
    return html.replace(compact_footer, expanded_footer)


def expand_v7_instrument_controls(html: str) -> str:
    """Ensure /ui/v7 exposes durable H9 Instrument API alignment bindings.

    H9 is a parity-restoration baseline: existing slit/calibration/detector
    backend capabilities become visible from Instrument / Configure, and safe
    routine slit/calibration operations get opt-in runtime controls.
    """
    if 'id="v7-instrument-controls"' in html:
        return html

    controls = """            <section class="panel" id="v7-instrument-controls" data-role="v7-instrument-controls" data-phase="runtime-enhanceable">
              <h2>Instrument API Controls · Existing Backend Capabilities</h2>
              <div class="panel-body grid">
                <div class="phase-note"><strong>H9:</strong> This panel exposes existing slit and calibration APIs in v7.1. Runtime remains opt-in; backend state-machine guards remain authoritative.</div>
                <div class="field-grid">
                  <label>Slit Width (um)<input type="number" min="0.001" step="0.001" value="100" data-role="instrument-slit-width-um" /></label>
                  <label>Slit Angle (deg)<input type="number" min="-90" max="90" step="0.001" value="0" data-role="instrument-slit-angle-deg" /></label>
                  <button class="btn" type="button" data-action="instrument-set-slit-width" disabled>Set Slit Width</button>
                  <button class="btn" type="button" data-action="instrument-set-slit-angle" disabled>Set Slit Angle</button>
                  <label>Calibration Mode<select data-role="instrument-calibration-mode"><option value="science">science</option><option value="calibration">calibration</option></select></label>
                  <label>Calibration Lamp<select data-role="instrument-calibration-lamp"><option value="flat">flat</option><option value="arc_hgar">arc_hgar</option><option value="arc_ne">arc_ne</option></select></label>
                  <button class="btn" type="button" data-action="instrument-set-calibration-mode" disabled>Set Calibration Mode</button>
                  <label><input type="checkbox" data-role="instrument-calibration-lamp-enabled" checked /> Enable selected calibration lamp</label>
                  <button class="btn" type="button" data-action="instrument-set-calibration-lamp" disabled>Set Calibration Lamp</button>
                  <button class="btn" type="button" data-action="instrument-refresh-calibration" disabled>Refresh Calibration</button>
                  <button class="btn" type="button" data-action="instrument-refresh-detector-config" disabled>Refresh Detector Config</button>
                </div>
                <dl class="kv">
                  <dt>Slit Endpoint</dt><dd><code>/api/v1/slit</code> · <code>/api/v1/slit_angle</code></dd>
                  <dt>Calibration Endpoint</dt><dd><code>/api/v1/calibration/status</code> · <code>/api/v1/calibration/mode</code> · <code>/api/v1/calibration/lamp</code></dd>
                  <dt>Detector Visibility</dt><dd><code>/api/v1/detector/config</code> read-only baseline</dd>
                  <dt>Last Command</dt><dd><code data-bind="v7.instrument.last_command">none</code></dd>
                  <dt>Request ID</dt><dd><code data-bind="v7.instrument.request_id">not available</code></dd>
                  <dt>Last Error</dt><dd><code data-bind="v7.instrument.last_error">none</code></dd>
                  <dt>Runtime State</dt><dd><code data-bind="v7.instrument.runtime_state">static fallback</code></dd>
                </dl>
                <pre data-bind="v7.instrument.result">Instrument runtime is opt-in. Existing backend capabilities are visible here; controls are disabled until runtime is enabled.</pre>
                <div class="badge-row">
                  <span class="badge live">routine slit/calibration controls</span>
                  <span class="badge future">detector config read-only</span>
                  <span class="badge future">full B/G/R hardware control deferred</span>
                </div>
              </div>
            </section>

"""
    marker = '            <section class="panel" data-role="instrument-safety-boundary">'
    if marker in html:
        return html.replace(marker, controls + marker)
    return html


def expand_v7_observe_command_panel(html: str) -> str:
    """Ensure /ui/v7 exposes durable H3 Observe command-result bindings.

    H3 keeps Observe focused on the existing single-exposure backend contract
    while making the Finish command and structured command-result fields visible
    in the served v7.1 shell.
    """
    if 'data-action="obs-finish"' not in html:
        html = html.replace(
            '                  <button class="btn primary" type="button" data-action="obs-start" disabled>Start</button>\n'
            '                  <button class="btn" type="button" data-action="obs-stop-readout" disabled>Stop & Readout</button>',
            '                  <button class="btn primary" type="button" data-action="obs-start" disabled>Start</button>\n'
            '                  <button class="btn" type="button" data-action="obs-finish" disabled>Finish</button>\n'
            '                  <button class="btn" type="button" data-action="obs-stop-readout" disabled>Stop & Readout</button>',
        )

    if 'data-bind="v7.observe.request_id"' not in html:
        html = html.replace(
            '                  <dt>Last Command</dt><dd><code data-bind="v7.observe.last_command">none</code></dd>\n'
            '                  <dt>Runtime State</dt><dd><code data-bind="v7.observe.runtime_state">static fallback</code></dd>',
            '                  <dt>Last Command</dt><dd><code data-bind="v7.observe.last_command">none</code></dd>\n'
            '                  <dt>Request ID</dt><dd><code data-bind="v7.observe.request_id">not available</code></dd>\n'
            '                  <dt>Latest Job</dt><dd><code data-bind="v7.observe.latest_job">not available</code></dd>\n'
            '                  <dt>Last Error</dt><dd><code data-bind="v7.observe.last_error">none</code></dd>\n'
            '                  <dt>Runtime State</dt><dd><code data-bind="v7.observe.runtime_state">static fallback</code></dd>',
        )
    return html


def serve_html(
    path: Path,
    *,
    inject_adapter: bool = False,
    extra_scripts: tuple[str, ...] = (),
    expand_v7_feedback: bool = False,
    expand_v7_instrument: bool = False,
    expand_v7_observe: bool = False,
):
    if path.exists():
        html = path.read_text(encoding="utf-8")
        if inject_adapter:
            html = inject_phase_2d6_ui_adapter(html)
        if expand_v7_feedback:
            html = expand_v7_feedback_rail(html)
        if expand_v7_instrument:
            html = expand_v7_instrument_controls(html)
        if expand_v7_observe:
            html = expand_v7_observe_command_panel(html)
        for script_src in extra_scripts:
            html = inject_script_tag(html, script_src)
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
            "phase2d8_v7_runtime_enabled": phase_2d8_v7_runtime_enabled(),
            "phase2d8_v7_runtime_modules": phase_2d8_v7_runtime_module_flags(),
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
    return serve_html(
        UI_V7_ENTRY,
        extra_scripts=phase_2d8_v7_runtime_scripts(),
        expand_v7_feedback=True,
        expand_v7_instrument=True,
        expand_v7_observe=True,
    )
