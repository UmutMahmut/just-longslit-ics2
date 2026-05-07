# JUST Long-Slit ICS 2.0

Instrument Control System (ICS) for the JUST Telescope **Long-Slit Spectrograph**.

ICS 2.0 is intended to become the software control backbone for the JUST long-slit spectrograph. It is not only a web UI project. The repository currently contains a simulation-first, API-driven control stack and a staged operator-console frontend that are being developed toward later real-hardware integration.

---

## Current status

The project has moved beyond the early skeleton/prototype stage. The current stable baseline is a simulator-backed ICS with a usable backend/API backbone, a stable v5 default UI, and a productizing v7 operator-console prototype.

Latest reported local validation:

```text
pytest -q
144 passed
```

Current strategic UI decision:

```text
/ui      -> v5 stable default capability baseline
/ui/v6   -> v6 operational-status review shell
/ui/v7   -> future operator console prototype, static by default
```

Do **not** switch `/ui` to v7 yet.

v7 has a healthier runtime architecture than before: static shell first, versioned runtime assets, opt-in runtime gates, singleton-safe runtime modules, and consolidated durable HTML skeletons for Presets and Observe. The next mainline is a systematic **v5-to-v7 feature parity pass**, not ad-hoc runtime expansion.

---

## What this repository currently provides

- A layered Python backend organized around **domain / kernel / application / API** boundaries.
- A **FastAPI** control and status interface under `/api/v1/*`.
- A simulation-first runtime for end-to-end development before full hardware availability.
- Backend-served static frontends for zero-CORS local integration.
- A stable v5 default UI used as the current capability baseline.
- A v7 operator-console prototype with static default behavior and opt-in runtime enhancement.
- Runtime-status, preset, observe, and observe-guard prototypes for v7.
- Regression tests covering API behavior, UI route/static asset behavior, runtime gates, preset safety, and observe/status behavior.

---

## Current phase summary

```text
Phase 2.8-A: DONE
  Route stabilization. /ui remains v5; /ui/v6 and /ui/v7 keep separate roles.

Phase 2.8-B: DONE
  v7 static shell established and clickable by default without runtime JS.

Phase 2.8-C: OPT-IN PROTOTYPE DONE / VERIFIED
  v7 runtime status binding exists, is gated, and is singleton-safe.

Phase 2.8-C/D bridge: DONE / MERGED
  Earlier v5-to-v7 parity notes were consolidated into the Phase 2.8 UI migration record.

Remote hygiene guardrails: DONE / CONTINUING DISCIPLINE
  UI assets, tests, and docs have clearer durable homes.

Phase 2.8-D: STATIC DONE / RUNTIME CONTEXT OPT-IN
  v7 Setup static baseline exists; durable setup/session backend is not started.

Phase 2.8-E: STATIC SKELETON CONSOLIDATED / RUNTIME PRESET VERIFIED
  Presets skeleton and runtime are consolidated, gated, and locally verified.

Phase 2.8-F: STATIC SKELETON CONSOLIDATED / OBSERVE RUNTIME + GUARD VERIFIED
  Observe single-exposure controls and frontend guard are gated and locally verified.

Phase 2.8-G: CORE STABILIZATION DONE / CURRENT BATCH CLOSED
  v7 runtime architecture stabilization is closed enough for the next mainline.

Phase 2.8-H: PLANNED / NEXT
  v5-to-v7 feature parity pass.

Phase 2.8-I: PLANNED
  Operator workflow polish after parity decisions.

Phase 2.9: PLANNED
  New backend contracts for final frontend capabilities.
```

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

The current design has been informed by mature spectrograph-control patterns, especially:

- MODS-style separation of setup, dashboard operation, raw image display, scripting, alignment, and engineering utilities.
- BFOSC-style attention to practical observer workflow, wheel/configuration control, focusing, CCD acquisition, calibration, guiding, and data reduction constraints.
- JUST long-slit spectrograph requirements for B/G/R channel operation, calibration, slit monitoring, guiding, data storage, and future OCS/operator-console integration.

These references are design inputs, not finished implementation claims.

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

v7 currently organizes the future console around:

- Setup
- Observe
- Presets
- Diagnostics
- top-level status cards
- live image / latest exposure preview placeholders
- B/G/R channel placeholders

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
$env:JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED="1"   # status module; effectively defaults on when master gate is enabled
$env:JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED="1"   # presets module
$env:JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED="1"  # observe module
$env:JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED="1"    # frontend-only observe guard
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
│   ├── services/
│   └── usecases/
├── domain/
│   ├── detector/
│   ├── health/
│   ├── lamps/
│   ├── observation/
│   ├── slit/
│   └── system/
├── drivers/
│   ├── real/
│   └── sim/
├── infra/
└── kernel/

tests/
├── api/
├── ui/
└── test_stage_validation.py

docs/
└── phase_2_8_ui_migration.md
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
tests/      remaining staged validation coverage
```

Avoid adding new root-level `test_stage_*` files. Prefer domain-specific test locations such as `tests/api/`, `tests/ui/`, or future `tests/kernel/` as appropriate.

---

## Current limitations

ICS 2.0 is still under active development.

At the current stage:

- the project remains **simulation-first**
- many real drivers are still placeholders or early stubs
- v7 is not yet the default UI
- v7 runtime remains opt-in, not default-on
- durable setup/session metadata persistence is not started
- live image backend / quicklook / data watcher is not started
- sequence runner and durable observing plan model are deferred
- production preset UX still needs operator-facing diff tables and clearer risk presentation
- FITS/data-product pipeline and persistent observation log need future backend contracts
- role separation, authentication, and engineering/operator permission boundaries are future work

---

## Next mainline

The next mainline is **Phase 2.8-H: v5 to v7 feature parity pass**.

Recommended sequence:

1. Audit real v5 capabilities.
2. Compare v5 against current v7 Setup / Presets / Observe / Diagnostics.
3. Produce a parity checklist.
4. Classify each item as:
   - must-have
   - nice-to-have
   - engineer-only
   - deferred backend contract
5. Decide what belongs in the final operator console.
6. Identify which gaps require Phase 2.9 backend contracts.

Do not continue expanding v7 runtime ad hoc before the parity pass is complete.

---

## Historical note

This repository is intended to become the main codebase for the new ICS 2.0 effort.

Earlier historical repositories and external instrument manuals remain useful as reference material, but current implementation work is centered here.

---

## License

If a `LICENSE` file is not yet added, treat this repository as internal until a license is chosen.
