# JUST Long-Slit ICS 2.0

Instrument Control System (ICS) for the JUST Telescope **Long-Slit Spectrograph**.

ICS 2.0 is intended to become the software control backbone for the JUST long-slit spectrograph. It is not only a web UI project. The repository currently contains a simulation-first, API-driven control stack and a staged operator-console frontend being developed toward later real-hardware integration.

---

## Current status

The current stable baseline is a simulator-backed ICS with a usable backend/API backbone, a stable v5 default UI, and a productizing v7.1 operator-console prototype.

Current strategic UI decision:

```text
/ui      -> v5 stable default capability baseline
/ui/v6   -> v6 operational-status review shell
/ui/v7   -> v7.1 operator-console prototype, static by default
```

Do **not** switch `/ui` to v7 yet.

Current mainline:

```text
Phase 2.8-H: v5 to v7 feature parity pass
```

Recent local validation reported by the user:

```text
pytest -q
156 passed in 0.97s
```

For the durable current-status record, see:

```text
docs/project_status.md
```

For operator-console requirements and backend-capability visibility rules, see:

```text
docs/operator_console_requirements.md
```

---

## What this repository currently provides

- A layered Python backend organized around domain / kernel / application / API boundaries.
- A FastAPI control and status interface under `/api/v1/*`.
- A simulation-first runtime for end-to-end development before full hardware availability.
- Backend-served static frontends for zero-CORS local integration.
- A stable v5 default UI used as the current capability baseline.
- A v7.1 operator-console prototype with static default behavior and opt-in runtime enhancement.
- Runtime-status, preset, observe, and observe-guard prototypes for v7.1.
- Regression tests covering API behavior, UI route/static asset behavior, runtime gates, preset safety, observe/status behavior, and operator-console shell invariants.

---

## Design direction

ICS 2.0 is being developed as a real instrument control system for long-slit spectroscopy. The control software must eventually support a coherent observing loop, not merely isolated buttons.

Core design priorities:

- Preserve a clear state model for observation, calibration, slit, detector, presets, and diagnostics.
- Keep unsafe or high-impact actions explicit, previewable, confirmed, and auditable.
- Keep operator-facing workflow separate from engineering/diagnostic detail.
- Make raw status and JSON available in Diagnostics, not in the main observing path.
- Keep simulation-first development while leaving a clean path for real hardware adapters.
- Avoid pretending that static placeholders are real telemetry or persisted backend state.
- Ensure backend capabilities are at least visible in the frontend, even when not directly controllable.

The current design has been informed by mature spectrograph-control patterns and by earlier JUST ICS experience. The legacy ICS 1.0 repository is useful as an intent reference, especially for the minimal closed loop, SimHAL, capabilities map, slit/lamp control, SlitCam, B/G/R placeholders, and backend-served static UI. It is not the implementation source of truth for ICS 2.0.

---

## Current frontend routes

### `/ui`

Default stable UI.

Backed by:

```text
src/justls/ics/app/ui/ui_alpha_skeleton_v5.html
```

Treat this as the current operator-facing capability baseline until v7 parity is explicitly approved.

### `/ui/v6`

Operational-status review shell.

Backed by:

```text
src/justls/ics/app/ui/ui_operational_v6.html
```

Keep available for review and continuity with Phase 2.6/2.7 work.

### `/ui/v7`

Future operator-console prototype.

Backed by:

```text
src/justls/ics/app/ui/ui_operational_v7.html
```

Default behavior must remain static and clickable without runtime JS.

v7.1 currently organizes the future console around:

```text
Setup
Instrument / Configure
Observe
Presets
Diagnostics
Housekeeping
Engineer
```

---

## v7 runtime gates

The v7 runtime architecture is opt-in.

Recommended cleanup before starting a local server:

```powershell
Remove-Item Env:JUSTLS_UI_V7_RUNTIME_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED -ErrorAction SilentlyContinue
```

Master gate:

```powershell
$env:JUSTLS_UI_V7_RUNTIME_ENABLED="1"
```

Module gates:

```powershell
$env:JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED="1"
$env:JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED="1"
$env:JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED="1"
$env:JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED="1"
```

Runtime assets:

```text
src/justls/ics/app/ui/v7/runtime_status.js
src/justls/ics/app/ui/v7/preset_runtime.js
src/justls/ics/app/ui/v7/observe_runtime.js
src/justls/ics/app/ui/v7/observe_guard.js
```

Important rule:

```text
HTML owns durable structure.
Runtime JS enhances durable HTML skeletons.
Runtime JS should not create competing duplicate UI panels unless it is a fallback for a missing skeleton.
```

---

## Repository layout

A simplified view of the current repository:

```text
src/justls/ics/
├── adapters/
├── app/
│   ├── api/
│   ├── desktop/
│   ├── ui/
│   │   ├── ui_alpha_skeleton_v5.html
│   │   ├── ui_operational_v6.html
│   │   ├── ui_operational_v7.html
│   │   ├── v5/
│   │   ├── v6/
│   │   └── v7/
│   └── main.py
├── application/
├── domain/
├── drivers/
├── infra/
└── kernel/

tests/
├── api/
└── ui/

docs/
├── project_status.md
└── operator_console_requirements.md
```

---

## API overview

Current backend work is centered around the `/api/v1/*` namespace.

Representative endpoints include:

- `GET /api/v1/health`
- `GET /api/v1/status`
- `GET /api/v1/status/full`
- `GET /api/v1/capabilities`
- `GET /api/v1/observation/status`
- `POST /api/v1/observation/arm`
- `POST /api/v1/observation/start`
- `POST /api/v1/observation/finish`
- `POST /api/v1/observation/stop_readout`
- `POST /api/v1/observation/abort_discard`
- `POST /api/v1/slit`
- `POST /api/v1/slit_angle`
- `GET /api/v1/calibration/status`
- `POST /api/v1/calibration/mode`
- `POST /api/v1/calibration/lamp`
- `GET /api/v1/detector/config`
- `POST /api/v1/detector/config`
- `GET /api/v1/presets`
- `POST /api/v1/presets/preview`
- `POST /api/v1/presets/apply`

---

## Running locally

### 0) Recommended environment

Use your existing local Python environment for development and testing.

If you use conda, activate your environment first:

```powershell
conda activate <your-env>
```

### 1) Install dependencies

From repository root:

```powershell
python -m pip install -U pip
pip install -e .
pip install -U pytest httpx uvicorn fastapi
```

### 2) Run backend

A typical local startup command is:

```powershell
python -m uvicorn justls.ics.app.main:app --app-dir src --reload
```

Alternative explicit host/port form:

```powershell
python -m uvicorn justls.ics.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3) Open in browser

- Swagger UI: `http://127.0.0.1:8000/docs`
- Default stable UI: `http://127.0.0.1:8000/ui/`
- v6 review shell: `http://127.0.0.1:8000/ui/v6`
- v7 static prototype: `http://127.0.0.1:8000/ui/v7`

For local integration work, open the UI through the backend-served route instead of `file://`, so frontend and backend stay on the same origin.

---

## Tests

Run tests locally with:

```powershell
pytest -q
```

Current test homes:

```text
tests/api/  API behavior and response contracts
tests/ui/   UI routes, static shells, static assets, runtime injection gates
```

Avoid adding new root-level `test_stage_*` files. Prefer domain-specific test locations such as `tests/api/`, `tests/ui/`, or future `tests/kernel/` as appropriate.

---

## Current limitations

ICS 2.0 is still under active development.

At the current stage:

- the project remains simulation-first;
- many real drivers are still placeholders or early stubs;
- v7 is not yet the default UI;
- v7 runtime remains opt-in, not default-on;
- durable setup/session metadata persistence is not started;
- live image backend / quicklook / data watcher is not started;
- sequence runner and durable observing plan model are deferred;
- production preset UX still needs operator-facing diff tables and clearer risk presentation;
- FITS/data-product pipeline and persistent observation log need future backend contracts;
- role separation, authentication, and engineering/operator permission boundaries are future work.

---

## Documentation policy

Keep repository docs few and durable. Current source of truth:

```text
docs/project_status.md
docs/operator_console_requirements.md
```

Avoid adding one-off phase notes. Update the two durable docs when the decision remains useful.

---

## Historical note

Earlier historical repositories and external instrument manuals remain useful as reference material, but current implementation work is centered here.

---

## License

If a `LICENSE` file is not yet added, treat this repository as internal until a license is chosen.
