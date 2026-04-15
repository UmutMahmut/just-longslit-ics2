# JUST Long-Slit ICS 2.0

Instrument Control System (ICS) for the JUST Telescope **Long-Slit Spectrograph**.

This repository contains the current **ICS 2.0** integrated codebase, including:

- A layered Python backend organized around **domain / kernel / application / API**
- A **FastAPI** control and status interface under `/api/v1/*`
- A simulation-first runtime for end-to-end development without full hardware availability
- A backend-served static frontend at `/ui/` for zero-CORS local integration
- A progressively integrated operator-facing UI for observation, slit, calibration, detector, presets, and diagnostics
- A staged regression workflow centered on `tests/test_stage_validation.py`

---

## Project status

### Current stage

This repository is now the main working codebase for **JUST Long-Slit ICS 2.0**.

The project has already moved beyond an early skeleton/prototype stage.  
At the current point, the core control backbone between backend and frontend has been connected, and the work focus has shifted toward:

- integration hardening
- state consistency
- result presentation
- regression safety
- preparation for future real hardware integration

### Completed in the current stage

- **Core backend structure established**
  - Layered codebase under `domain`, `kernel`, `application`, and `app/api`
  - Stable simulation-oriented runtime
  - Unified state and subsystem snapshot flow

- **Observation main chain integrated**
  - `arm`
  - `start`
  - `finish`
  - `stop_readout`
  - `abort_discard`

- **Slit control chain integrated**
  - slit width control
  - slit angle control

- **Calibration / lamp chain integrated**
  - calibration mode switching
  - lamp enable / disable

- **Detector configuration chain integrated**
  - `profile_name`
  - `save_enabled`
  - `trigger_mode`
  - `readout_mode`
  - per-channel `B / G / R` enable state
  - per-channel role mapping

- **Preset / apply chain integrated**
  - preset catalog
  - apply result feedback
  - preset-driven detector / calibration updates

- **System status output integrated**
  - `/api/v1/health`
  - `/api/v1/status/full`
  - `/api/v1/capabilities`
  - `/api/v1/observation/status`
  - `/api/v1/calibration/status`
  - `/api/v1/detector/config`

- **Frontend UI Alpha integrated with backend**
  - Overview page with key state visibility
  - Observation page with lifecycle controls
  - Instrument pages for slit / calibration / detector
  - Preset page with apply feedback
  - Diagnostics page with raw JSON visibility
  - day / night theme support

- **Recent consistency fixes**
  - runtime `overall_state` aggregation corrected
  - `last_exposure.operator_note` and `observation_meta.operator_note` consistency improved
  - observation re-arm behavior after completed observations aligned between backend state machine and frontend button gating

### Next

- Strengthen regression coverage for newly discovered integration bugs
- Improve **ObservationMeta / Frame Results** presentation in the frontend
- Refine diagnostics / event log / operator feedback
- Further unify API response semantics where necessary
- Continue staged preparation for future real hardware integration

---

## Design goals of ICS 2.0

Compared with earlier historical ICS work, ICS 2.0 aims to provide a more explicit, maintainable, and extensible control architecture.

Main goals include:

- separating **domain logic**, **state/kernel logic**, **application services**, and **API/UI integration**
- making observation, calibration, slit, detector, and preset workflows more explicit
- building a frontend that reflects the true control/state model rather than acting as a loose button collection
- keeping the development path simulation-first while preparing for later real-hardware connection
- making staged validation and regression testing part of normal development

---

## Important note on detector interpretation

In ICS 2.0, the detector should **not** be interpreted as a single monolithic camera abstraction.

At the current stage, the practical detector meaning is:

> **an RGB three-channel camera acquisition system**

Therefore, detector configuration is represented as:

- a detector-level config object
- per-channel `B / G / R` state
- per-channel role definitions

The current project intentionally does **not** prematurely freeze low-level hardware-specific camera parameters such as ROI, binning, gain, cooling, and similar details before real hardware requirements are finalized.

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
└── test_stage_validation.py
```

---

## Current frontend

The current operator-facing frontend is based on:

```text
src/justls/ics/app/ui/ui_alpha_skeleton_v4.html
```

This frontend is no longer only a visual mockup.  
It is already wired into the current backend backbone for the major control/status chains listed above.

The current UI emphasizes:

- overview-first monitoring
- explicit key-state visibility
- observation lifecycle control
- slit / calibration / detector operation pages
- preset application visibility
- diagnostics and raw JSON visibility
- day / night theme switching

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
python -m uvicorn justls.ics.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3) Open in browser

- Swagger UI: `http://127.0.0.1:8000/docs`
- ICS UI: `http://127.0.0.1:8000/ui/`

For local integration work, it is recommended to open the UI through the backend-served route instead of `file://`, so frontend and backend stay on the same origin.

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
- `POST /api/v1/presets/apply`

---

## Tests

The main current staged validation file is:

```text
tests/test_stage_validation.py
```

Run tests locally with:

```powershell
pytest -q
```

This file is intended to continue growing as new integration bugs are converted into regression coverage.

---

## Current limitations

ICS 2.0 is still under active development.

At the current stage:

- the project remains **simulation-first**
- many real drivers are still placeholders or early stubs
- diagnostics / event logs still need further strengthening
- ObservationMeta / Frame Results presentation is not fully formalized yet
- API envelope consistency is still a future cleanup target
- some UI regions remain future/demo slots for later capability expansion

---

## Roadmap direction

Reasonable next steps for this repository include:

1. strengthen regression coverage for newly discovered frontend/backend integration bugs
2. improve ObservationMeta / Frame Results presentation
3. refine diagnostics and operator-facing runtime feedback
4. continue tightening API semantics and response consistency
5. prepare more formally for later real hardware integration
6. later evolve toward richer detector config, preset execution safety, and management/audit capability

---

## Historical note

This repository is intended to become the main codebase for the new ICS 2.0 effort.

Earlier historical repositories remain useful as reference material, but current development is now centered here.

---

## License

If a `LICENSE` file is not yet added, treat this repository as internal until a license is chosen.
