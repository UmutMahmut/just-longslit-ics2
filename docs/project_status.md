# Project status

## Purpose

This is the durable project-status document for JUST Long-Slit ICS 2.0. It records current direction, phase boundaries, completed milestones, open decisions, and close criteria.

Durable hardware, P0, v5 baseline, and operator-console requirements are maintained in `docs/operator_console_requirements.md`.

The software-development strategy and phase roadmap are maintained in `docs/ics2_software_development_strategy.md`.

---

## Current snapshot

```text
Date/context: after Phase 2.9-A closeout, packaging metadata recovery, README install sync, and calibration Mode/Lamp frame-type advisory fix
Mainline checkpoint before this docs sync: a955308 ui: clarify calibration mode lamp frame coupling
Validation: pytest -q -> 202 passed in 1.40s
Current phase status: Phase 2.9-A closed; post-2.9-A maintenance fixes closed; Phase 2.9-B1 next
```

Phase 2.9-A is merged into `main` and closed.

Durable Setup/Data Context is no longer a frontend-only placeholder. It now has:

```text
- SessionDataContext domain model;
- GET /api/v1/setup/context;
- PUT /api/v1/setup/context;
- POST /api/v1/setup/context/reload;
- SetupContextService;
- SetupContextStore protocol;
- JsonSetupContextStore;
- v7 setup_runtime.js behind opt-in runtime gates;
- Observation arm snapshot handoff into ObservationMeta.setup_context and ObservationMeta.data_preview.
```

The current Setup/Data Context loop is:

```text
Setup UI
  -> GET/PUT/reload /api/v1/setup/context
  -> JsonSetupContextStore
  -> ObservationService.arm()
  -> ObservationMeta.setup_context + data_preview
  -> GET /api/v1/observation/status
```

Explicitly not done in Phase 2.9-A:

```text
- no proposal database;
- no scheduler;
- no sequence runner;
- no FITS writer;
- no DataProduct pipeline;
- no frame-index consumption/auto-increment policy;
- no TCS/OCS control;
- no telescope pointing/rotator/guiding/dome/weather authority;
- no per-channel B/G/R exposure readiness/control.
```

---

## Project goal

JUST Long-Slit ICS 2.0 is the control-system backbone for the JUST Telescope long-slit spectrograph. It is not merely a web UI project.

The system is being developed around:

```text
- simulation-first backend development;
- clear API/domain/kernel/application boundaries;
- operator-safe control surfaces;
- explicit diagnostics and request tracing;
- staged migration from the v5 capability baseline to the v7.1 operator console;
- later real-hardware integration through adapter/gateway boundaries.
```

Long-term target loop:

```text
OCS / Operator / Future Script
  -> ObservationRequest / ObservationPlan
  -> ICS validation and readiness
  -> SequenceStep execution
  -> Slit / calibration / detector / TCS-readiness coordination
  -> ExposureRecord / DataProduct / Quicklook
  -> Lifecycle event stream
  -> Result callback / audit log
  -> Safe abort and recovery
```

This target loop is directional. It must be reached through stable contracts and small reversible increments, not through a large speculative implementation.

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

Runtime policy:

```text
- v7 runtime remains opt-in through JUSTLS_UI_V7_RUNTIME_ENABLED=1.
- Setup runtime is separately gated by JUSTLS_UI_V7_SETUP_RUNTIME_ENABLED=1.
- Status runtime remains the safest first runtime module when the master gate is enabled.
- Instrument / Presets / Observe / Guard runtime modules remain individually gated.
- Backend API semantics are not changed merely by route selection.
```

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

## Completed milestone summary

### Phase 2.6: GUI and runtime operational maturity foundation

Closed. Key durable outcomes: `/api/v1/status/full`, operational-status direction, v6 review shell, v5 adapter, UI safety switches, and X-Request-ID/latest-job thinking.

### Phase 2.7: Preset operational hardening

Closed. Key durable outcomes: preset category/risk/confirmation metadata, side-effect-free preview, guarded apply, structured apply result, latest-job linkage, and observation arm attachment of latest successful preset summary.

### Phase 2.8-G/H/I/J and v7 UI IA cleanup

Closed. Key durable outcomes: v7 runtime gates, `/ui` default to v7.1 prototype, v5 fallback routes, served `ui_operational_v7.html`, compact operator-facing Instrument/Setup pages, and HTML-owned durable structures enhanced by runtime JS.

### Phase 2.9-A: durable Setup/Data Context

Closed and merged into `main`.

Key durable outcomes:

```text
- SessionDataContext domain model exists.
- Setup context has GET/PUT/reload API endpoints.
- Setup context has a service layer and JSON store abstraction.
- v7 Setup page has persisted-context hooks and opt-in setup_runtime.js binding.
- Observation arm attaches setup_context and data_preview snapshots into observation metadata.
- Tests are placed by boundary under tests/domain, tests/application, tests/api, and tests/ui.
```

A1-A6 closeout:

```text
A1  SessionDataContext domain model + domain tests       done
A2  read-only GET API + service default                  done
A3  persistence port + JSON store                        done
A4  PUT/reload API + JSON-backed dependency              done
A5  Setup UI runtime binding                             done
A6  observation metadata handoff                         done
```

### Post-2.9-A maintenance closeout

Closed.

Key durable outcomes:

```text
- Python packaging metadata restored through pyproject.toml.
- requirements.txt delegates to -e .[dev].
- .gitignore excludes packaging/build artifacts such as *.egg-info/, build/, and dist/.
- README local install instructions match the packaging contract.
- Instrument Calibration UI preserves backend Mode/Lamp terminology.
- Calibration UI exposes Observe Frame, Expected for Frame, and Compatibility advisory fields.
- Use Frame-Type Defaults is UI-only and does not dispatch hardware/API commands by itself.
```

Calibration UI fix boundary:

```text
- no backend calibration API change;
- no domain model change;
- no observation preview implementation yet;
- no sequence runner;
- no real hardware behavior implied.
```

---

## Current capability status

| Capability | Current state | Strategy judgment |
|---|---|---|
| Layered architecture | Established | Continue Domain / Kernel / Application / API / UI / Adapter separation. |
| Request ID / Job audit | Established | Future OCS, sequence, and data product work must preserve it. |
| Setup/Data Context | Durable backend + UI binding + observation snapshot handoff | Phase 2.9-A complete. |
| Observation single exposure | Available | Keep as baseline while defining ObservationRequest/Preview in 2.9-B. |
| Preset preview/apply | Available | Needs later operator-facing diff polish. |
| v7 default UI | Default prototype | Not final production GUI. |
| v7 runtime | Opt-in | Keep explicit gates. |
| Slit control | Basic available | Preserve arcsec/um contract. |
| Calibration | Basic visible/control + Mode/Lamp frame-type advisory | Current UI shows science/flat/arc compatibility; future preview contract should enforce readiness. |
| Detector config | Visible, partially writable | Avoid expanding routine detector write UI prematurely. |
| B/G/R channels | Honest summary only | No per-channel exposure readiness/control yet. |
| OCS | Not implemented | Phase 2.9-B starts request/preview contract; actual adapter later. |
| TCS | Not implemented | Future read-only readiness; no telescope control. |
| Data product | Not implemented | Phase 2.9-D contract later. |
| Hardware protocols | Not selected | Remain hardware-selection-driven and adapter-bounded. |

---

## Phase 2.9-B next

Phase 2.9-B should define the **Observation request/preview contract**.

Locked decisions for the first implementation slice:

```text
- ObservationRequest should use exposures: list[ExposureSpec].
- Phase 2.9-B initial compatibility allows exactly one ExposureSpec only.
- Multiple exposures are a shape reservation, not sequence-runner support.
- frame_type should be a strict enum.
- The execution-compatible initial frame types remain science / flat / arc / test unless explicitly extended.
- TCS readiness slot may exist in the contract, but detailed TCS fields remain unavailable/unknown for now.
- ExposureRecord/DataProduct contract should come before sequence runner.
- Do not introduce a database yet; keep protocol + JSON/JSONL style stores until real query/operations needs appear.
```

Expected first discussion:

```text
- ObservationRequest fields and minimal schema;
- ExposureSpec boundaries;
- ObservationPreviewResult shape;
- ValidationIssue and ReadinessSnapshot semantics;
- relationship to current single-exposure arm/start/finish lifecycle;
- side-effect-free preview guarantees;
- calibration Mode/Lamp/frame-type readiness checks;
- setup context snapshot use;
- no actual sequence runner yet;
- no OCS adapter yet;
- no TCS control;
- no FITS/DataProduct implementation.
```

First slice:

```text
2.9-B1: domain model for ObservationRequest / ExposureSpec / ObservationPreviewResult / ValidationIssue / ReadinessSnapshot + domain tests only
```

---

## Technology adoption gate

New infrastructure, protocol, database, event-streaming, hardware-bus, external platform, or observatory-integration technology must not be promoted into the main roadmap merely because it is powerful or familiar.

Before adoption, it must answer:

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

If these questions are not answerable, the item remains `TBD`, `candidate`, or `adapter-bounded`, not a named implementation route.

---

## Route and runtime invariants

These must remain true unless explicitly changed by a major decision:

```text
- /ui is the v7.1 default operator-console prototype.
- /ui/v5 and /ui/legacy remain v5 fallback routes.
- /ui/v7 remains static and clickable by default.
- v7 runtime is opt-in through JUSTLS_UI_V7_RUNTIME_ENABLED=1.
- v7 module-level runtime gates remain opt-in or master-gated.
- runtime JS must enhance durable skeletons and avoid duplicate competing panels.
- routine pages show command summaries first.
- raw JSON belongs in page detail areas and Diagnostics, not as the dominant main flow.
- unsafe engineering actions belong in Engineer/Housekeeping/Diagnostics, not routine operator flow.
- bottom-layer hardware protocols remain hardware-selection-driven and adapter-bounded.
```

---

## Documentation policy

`docs/` should remain small and durable.

Current durable docs:

```text
docs/ics2_software_development_strategy.md
docs/project_status.md
docs/operator_console_requirements.md
```

Avoid reintroducing one-off phase notes. If a decision remains useful, fold it into one of these files.
