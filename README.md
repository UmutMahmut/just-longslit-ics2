# JUST Long-Slit ICS 2.0

Instrument Control System (ICS) for the JUST Telescope **Long-Slit Spectrograph**.

ICS 2.0 is intended to become the software control backbone for the JUST long-slit spectrograph. It is not only a web UI project. The repository currently contains a simulation-first, API-driven backend, a staged v7.1 operator-console prototype, and durable contracts that are being hardened before real-hardware integration.

---

## Current status

The current `main` baseline is **after Phase 2.9-A closeout plus post-2.9-A maintenance fixes**.

Current checkpoint before this docs sync:

```text
a955308 ui: clarify calibration mode lamp frame coupling
```

Recent local validation reported by the user:

```text
pytest -q
202 passed in 1.40s
```

Phase 2.9-A is closed. It established the first durable backend fact source for observing setup/session metadata:

```text
Setup UI
  -> GET/PUT/reload /api/v1/setup/context
  -> JsonSetupContextStore
  -> ObservationService.arm()
  -> ObservationMeta.setup_context + data_preview
  -> GET /api/v1/observation/status
```

Post-2.9-A maintenance fixes are also closed:

```text
- Python packaging metadata restored through pyproject.toml / requirements.txt / .gitignore.
- Local install instructions now use pip install -e ".[dev]" or pip install -r requirements.txt.
- Instrument Calibration UI now preserves backend Mode/Lamp terminology and exposes frame-type advisory fields.
```

The next planned development phase remains:

```text
Phase 2.9-B: Observation request/preview contract
```

---

## Current UI route strategy

```text
/ui        -> v7.1 default operator-console prototype
/ui/v7     -> v7.1 explicit operator-console prototype
/ui/v5     -> v5 stable legacy fallback
/ui/legacy -> v5 stable legacy fallback alias
/ui/v6     -> v6 operational-status review shell
```

Important wording:

```text
v7.1 is the default operator-console prototype.
This route switch does not mean v7.1 is a final product-grade GUI.
```

---

## What this repository currently provides

- A layered Python backend organized around domain / kernel / application / API boundaries.
- A FastAPI control and status interface under `/api/v1/*`.
- Python packaging metadata for editable local development.
- A simulation-first runtime for end-to-end development before full hardware availability.
- Backend-served static frontends for zero-CORS local integration.
- A v7.1 default operator-console prototype with explicit v5 fallback routes.
- Durable setup/session context API, JSON-backed persistence, and v7 setup runtime binding.
- Observation arm metadata handoff for `setup_context` and `data_preview` snapshots.
- Instrument Calibration UI frame-type advisory for science/flat/arc Mode/Lamp compatibility.
- Runtime-status, setup, instrument, preset, observe, and observe-guard runtime modules for v7.1, all opt-in behind runtime gates.
- Regression tests covering API behavior, application/domain/kernel contracts, UI route/static asset behavior, runtime gates, preset safety, observe/status behavior, setup context persistence, and operator-console shell invariants.

---

## Design direction

ICS 2.0 is being developed as a real instrument control system for long-slit spectroscopy. The control software must support a coherent observing loop, not merely isolated buttons.

Core design priorities:

- Preserve a clear state model for setup/session context, observation, calibration, slit, detector, presets, diagnostics, and future data products.
- Keep unsafe or high-impact actions explicit, previewable, confirmed, and auditable.
- Keep operator-facing workflow separate from engineering/diagnostic detail.
- Make raw status and JSON available in Diagnostics, not in the main observing path.
- Keep simulation-first development while leaving a clean path for real hardware adapters.
- Avoid pretending that static placeholders are real telemetry or persisted backend state.
- Ensure backend capabilities are visible in the frontend when operationally relevant.
- Prefer contracts and adapters before adopting specific hardware protocols or infrastructure technologies.

The legacy ICS 1.0 repository is useful as an intent reference, especially for the minimal closed loop, SimHAL, capabilities map, slit/lamp control, SlitCam, B/G/R placeholders, and backend-served static UI. It is not the implementation source of truth for ICS 2.0.

---

## Architecture guardrails

Every phase, PR, and commit should pass these checks:

| Guardrail | Question | Purpose |
|---|---|---|
| Contract first | Is this stabilizing a domain/API contract, or merely piling UI/implementation detail? | Prevent UI-first semantic drift. |
| Simulation parity | Can the simulator and future real hardware keep the same contract? | Prevent real-only hacks. |
| No telescope overreach | Does this bypass OCS/TCS authority for pointing, rotator, guiding, dome, weather, or telescope control? | Prevent ICS boundary violations. |
| No fake capability | Does this present a placeholder as a real capability? | Prevent operator misunderstanding. |
| Auditable command lifecycle | Do high-impact actions have request_id, latest_job, result, and error visibility? | Prevent untraceable operations. |
| Layer boundary | Are domain/application/kernel/api/ui/adapter responsibilities still separated? | Preserve maintainability. |

---

## Near-term roadmap focus

Phase 2.9 is **Contract Hardening**.

```text
Phase 2.9-A  Setup/Data Context model + API + persistence + observation snapshot handoff  DONE
Post-2.9-A  Packaging metadata + calibration UI frame-type advisory                    DONE
Phase 2.9-B  Observation request/preview contract                                      NEXT
Phase 2.9-C  Shared command/status feedback contract
Phase 2.9-D  Data product and exposure-record contract
Phase 2.9-E  Read-only observatory/TCS context
Phase 2.9-F  Operator workflow polish
Phase 3.x    Simulator-backed end-to-end observing workflow
Phase 4.x    Real hardware commissioning through adapter contracts
```

The roadmap source of truth is:

```text
docs/ics2_software_development_strategy.md
```

The current-status source of truth is:

```text
docs/project_status.md
```

Operator-console requirements and capability visibility rules are maintained in:

```text
docs/operator_console_requirements.md
```

---

## Phase 2.9-B locked decisions

The first Phase 2.9-B implementation slice must stay small and domain-first:

```text
- ObservationRequest uses exposures: list[ExposureSpec].
- Initial preview/arm compatibility allows exactly one ExposureSpec only.
- Multiple exposures are a shape reservation, not sequence-runner support.
- frame_type is strict and initially execution-compatible with science / flat / arc / test.
- TCS readiness may have a placeholder slot, but detailed TCS fields remain unavailable/unknown until a real interface exists.
- ExposureRecord/DataProduct contract comes before sequence runner.
- No database is introduced yet; keep protocol + JSON/JSONL style persistence until real operational needs appear.
```

---

## Technology adoption rule

New infrastructure, protocol, database, event-streaming, hardware-bus, or observatory-integration technology must not be promoted into the main roadmap merely because it is powerful or familiar.

Before adoption, it must pass this gate:

```text
1. What current project problem does it solve?
2. Is that problem present in the current phase?
3. Is there real hardware, real operations, or a real interface contract behind it?
4. Can a simpler schema, simulator, file contract, or adapter boundary solve it for now?
5. Does it preserve Domain / Kernel / Application / Adapter boundaries?
6. Does it avoid exposing low-level engineering complexity in routine operator UI?
7. Can it be tested through pytest or integration tests?
8. If we do not adopt it now, can the current phase still move forward cleanly?
```

If these questions are not answerable, the item should remain `TBD`, `candidate`, or `adapter-bounded`, not a named implementation route.

---

## v7 runtime gates

The v7 runtime architecture is opt-in.

Recommended cleanup before starting a local server:

```powershell
Remove-Item Env:JUSTLS_UI_V7_RUNTIME_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_SETUP_RUNTIME_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_INSTRUMENT_RUNTIME_ENABLED -ErrorAction SilentlyContinue
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
$env:JUSTLS_UI_V7_SETUP_RUNTIME_ENABLED="1"
$env:JUSTLS_UI_V7_INSTRUMENT_RUNTIME_ENABLED="1"
$env:JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED="1"
$env:JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED="1"
$env:JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED="1"
```

Important rule:

```text
HTML owns durable structure.
Runtime JS enhances durable HTML skeletons.
Runtime JS should not create competing duplicate UI panels unless it is a fallback for a missing skeleton.
```

---

## API overview

Representative current endpoints include:

- `GET /api/v1/health`
- `GET /api/v1/status`
- `GET /api/v1/status/full`
- `GET /api/v1/capabilities`
- `GET /api/v1/setup/context`
- `PUT /api/v1/setup/context`
- `POST /api/v1/setup/context/reload`
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

Use your existing local Python environment for development and testing.

```powershell
python -m pip install -U pip
pip install -e ".[dev]"
```

Equivalent convenience entry:

```powershell
pip install -r requirements.txt
```

Run backend:

```powershell
python -m uvicorn justls.ics.app.main:app --app-dir src --reload
```

Open in browser:

- Swagger UI: `http://127.0.0.1:8000/docs`
- Default v7.1 prototype: `http://127.0.0.1:8000/ui/`
- v7 explicit prototype: `http://127.0.0.1:8000/ui/v7`
- v5 fallback: `http://127.0.0.1:8000/ui/v5`
- v5 legacy alias: `http://127.0.0.1:8000/ui/legacy`
- v6 review shell: `http://127.0.0.1:8000/ui/v6`

For local integration work, open the UI through the backend-served route instead of `file://`, so frontend and backend stay on the same origin.

---

## Tests

Run tests locally with:

```powershell
pytest -q
```

Current baseline reported after post-2.9-A maintenance fixes:

```text
202 passed in 1.40s
```

Current test homes:

```text
tests/api/          API behavior and response contracts
tests/application/  application services and use-case contracts
tests/domain/       domain models and validation
tests/kernel/       runtime, job, state, and guard behavior
tests/ui/           UI routes, static shells, static assets, runtime injection gates
```

Avoid adding new root-level `test_stage_*` files. Prefer boundary-specific test locations such as `tests/api/`, `tests/application/`, `tests/domain/`, `tests/kernel/`, or `tests/ui/`.

---

## Current limitations

ICS 2.0 is still under active development.

At the current stage:

- the project remains simulation-first;
- many real drivers are still placeholders or early stubs;
- v7 is now the default operator-console prototype, not a final product-grade GUI;
- v7 runtime remains opt-in, not default-on;
- setup/session metadata now has durable JSON-backed persistence and observation arm snapshot handoff;
- calibration UI now has frame-type advisory, but blocking validation still belongs to the future Observation preview contract;
- Phase 2.9-B has not yet defined the ObservationRequest / Preview contract;
- live image backend / quicklook / data watcher is not started;
- sequence runner and durable observing plan execution remain deferred;
- FITS/data-product pipeline and persistent observation log need future backend contracts;
- role separation, authentication, and engineering/operator permission boundaries are future work;
- real hardware communication protocols remain hardware-selection-driven and adapter-bounded, not preselected in the software roadmap.

---

## Documentation policy

Keep repository docs few and durable. Current source of truth:

```text
docs/ics2_software_development_strategy.md
docs/project_status.md
docs/operator_console_requirements.md
```

Avoid adding one-off phase notes. Update durable docs when the decision remains useful.

---

## Historical note

Earlier historical repositories and external instrument manuals remain useful as reference material, but current implementation work is centered here.

---

## License

If a `LICENSE` file is not yet added, treat this repository as internal until a license is chosen.
