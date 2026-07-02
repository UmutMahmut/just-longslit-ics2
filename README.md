# JUST Long-Slit ICS 2.0

Instrument Control System for the JUST Telescope long-slit spectrograph.

This repository is not only a web UI prototype. It contains the current ICS 2.0 software backbone: a simulation-first backend, a FastAPI control/status surface, an operator-console prototype, and the domain/API contracts being hardened before real-hardware integration.

## Current baseline

Current code baseline: after Phase 2.9-E exposure-record and read-only observatory-context closeout.

Validation baseline:

```text
pytest -q
244 passed
```

Current default UI behavior:

```text
/ui        -> v7.1 operator-console prototype
/ui/v7     -> v7.1 explicit operator-console prototype
/ui/v5     -> v5 fallback shell
/ui/legacy -> v5 fallback alias
/ui/v6     -> v6 review shell
```

`/ui` and `/ui/v7` now load v7 runtime status plus Observe runtime by default. Setup, Instrument, and Presets runtime modules remain off unless explicitly enabled.

## What works now

The current repository supports a simulator-backed single-exposure control loop with auditable command feedback:

```text
Setup / Instrument context
  -> Observation preview
  -> backend readiness gate
  -> command feedback
  -> ExposureRecord / simulated DataProductRef
  -> read-only observatory context visibility
  -> v7 Observe command summary
  -> raw JSON diagnostics when needed
```

Implemented capabilities include:

- FastAPI backend under `/api/v1/*`.
- Request ID middleware and structured API error responses.
- Runtime, subsystem state, exposure state, job tracking, and latest-job visibility.
- Setup/session context domain model, service, JSON store, and API.
- Setup context snapshot handoff into observation metadata.
- Slit width and slit-angle API surfaces.
- Calibration mode/lamp API surfaces and simulator state.
- Detector configuration visibility and guarded mutation.
- Preset catalog, preview, guarded apply, risk/confirmation metadata, and observation metadata linkage.
- Observation single-exposure lifecycle: arm, start, finish, stop/readout, abort/discard.
- Side-effect-free observation preview contract.
- Backend arm gate based on current readiness preview.
- Observation command feedback contract for success, blocked, and failed command results.
- ExposureRecord, FrameRecord, DataProductRef, QuicklookRef-style references, FITS header summary placeholders, and quality flags.
- Simulator-backed data-product references that explicitly do not claim real FITS files exist.
- Read-only `/api/v1/observatory/context` for OCS/TCS/telescope/dome/weather/guider visibility with unavailable/stale-ready semantics reserved.
- `/api/v1/status/full` includes observatory context and latest exposure-record visibility.
- Simulator adapter contract tests for detector, slit, and calibration behavior.
- v7 Observe runtime consumption of command feedback.
- v7 route/runtime tests and API contract tests.

## What is not implemented yet

The repository intentionally does not yet implement:

- multi-exposure sequence runner;
- FITS writer or real file persistence;
- durable DataProduct pipeline beyond current runtime/read-model contracts;
- OCS adapter;
- TCS telescope control;
- real TCS readiness integration;
- telescope pointing, rotator, guider, dome, weather, or safety authority;
- real B/G/R camera hardware control;
- per-channel B/G/R exposure readiness/control;
- slit monitor image backend beyond visible placeholders;
- role-based authentication and operator/engineer permission separation;
- real hardware communication protocols.

These are future phases. They should enter through contracts and adapters, not direct UI shortcuts.

## Quick start

Install for local development:

```powershell
python -m pip install -U pip
pip install -e ".[dev]"
```

Run tests:

```powershell
pytest -q
```

Run backend:

```powershell
python -m uvicorn justls.ics.app.main:app --app-dir src --reload
```

Open:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/ui
http://127.0.0.1:8000/ui/v7
```

Use backend-served UI routes rather than opening HTML files directly. This keeps API calls, runtime scripts, and static assets on the same origin.

## Runtime defaults

Default v7 behavior:

```text
JUSTLS_UI_V7_RUNTIME_ENABLED         default: on
JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED  default: on
JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED default: on
JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED   default: on
```

Still default off:

```text
JUSTLS_UI_V7_SETUP_RUNTIME_ENABLED
JUSTLS_UI_V7_INSTRUMENT_RUNTIME_ENABLED
JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED
```

To force the v7 static shell:

```powershell
$env:JUSTLS_UI_V7_RUNTIME_ENABLED="0"
```

To explicitly enable additional modules:

```powershell
$env:JUSTLS_UI_V7_INSTRUMENT_RUNTIME_ENABLED="1"
$env:JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED="1"
$env:JUSTLS_UI_V7_SETUP_RUNTIME_ENABLED="1"
```

## API overview

Representative current endpoints:

```text
GET  /api/v1/health
GET  /api/v1/status
GET  /api/v1/status/full
GET  /api/v1/capabilities
GET  /api/v1/observatory/context

GET  /api/v1/setup/context
PUT  /api/v1/setup/context
POST /api/v1/setup/context/reload

POST /api/v1/slit
POST /api/v1/slit_angle

GET  /api/v1/calibration/status
POST /api/v1/calibration/mode
POST /api/v1/calibration/lamp

GET  /api/v1/detector/config
POST /api/v1/detector/config

GET  /api/v1/observation/status
POST /api/v1/observation/preview
POST /api/v1/observation/arm
POST /api/v1/observation/start
POST /api/v1/observation/finish
POST /api/v1/observation/stop_readout
POST /api/v1/observation/abort_discard

GET  /api/v1/presets
POST /api/v1/presets/preview
POST /api/v1/presets/apply
```

Important contract split:

```text
GET  /observation/status  -> current observation state
POST /observation/preview -> side-effect-free readiness/validation preview
POST observation commands -> ObservationCommandFeedbackResponse
latest_exposure_record -> exposure lifecycle + data-product reference contract
```

Preview is advisory. Arm is an independent command. Every Arm call reruns the backend readiness gate.

## Documentation map

Current durable docs:

```text
docs/project_status.md
docs/ics2_software_development_strategy.md
docs/operator_console_requirements.md
```

Use them as follows:

- `README.md`: current repository entry point.
- `docs/project_status.md`: current status snapshot and next-step boundary.
- `docs/ics2_software_development_strategy.md`: software strategy, architecture, roadmap, and documentation policy.
- `docs/operator_console_requirements.md`: operator-console requirements, hardware facts, capability visibility, and UI responsibility boundaries.

Avoid adding one-off phase notes. If a decision remains useful, fold it into one of the durable documents.

## Test layout

```text
tests/api/          API behavior and response contracts
tests/application/  application services and use-case contracts
tests/adapters/     simulator adapter parity contracts
tests/domain/       domain models and validation
tests/kernel/       runtime, job, state, and guard behavior
tests/ui/           UI routes, static shells, static assets, runtime gates
```

Prefer boundary-specific tests. Do not add new root-level temporary test files for phase work.

## Development guardrails

Every meaningful change should preserve:

- contract-first development;
- simulation parity with future real hardware;
- backend safety authority over frontend assumptions;
- request ID / latest job / error visibility;
- clear Domain / Kernel / Application / API / UI / Adapter boundaries;
- honest labeling of simulated, unavailable, placeholder, and real capabilities;
- no telescope/OCS/TCS authority overreach.

## License

If no `LICENSE` file is present, treat this repository as internal until a license is chosen.
