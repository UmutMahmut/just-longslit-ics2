# Project status

## Purpose

This is the durable project-status document for JUST Long-Slit ICS 2.0. It records current direction, phase boundaries, completed milestones, open decisions, and close criteria.

Durable hardware, P0, v5 baseline, and operator-console requirements are maintained in `docs/operator_console_requirements.md`.

The software-development strategy and phase roadmap are maintained in `docs/ics2_software_development_strategy.md`.

---

## Current snapshot

```text
Date/context: after Phase 2.9-B1 through B5 observation request/preview/readiness-gate slices, plus small maintenance cleanup.
Mainline checkpoint before this docs sync: after backend arm gate and maintenance cleanup on main.
Validation: pytest -q passed locally after B5 and maintenance cleanup; warning filter added for the known Starlette TestClient deprecation warning.
Current phase status: Phase 2.9-A closed; Phase 2.9-B in progress; B1-B5 landed; Phase 2.9-B closeout still pending.
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

Phase 2.9-B now has a working request/preview/gate chain:

```text
ObservationRequest / ExposureSpec
  -> ObservationPreviewService.preview_request()
  -> ObservationPreviewResult / ValidationIssue / ReadinessSnapshot
  -> POST /api/v1/observation/preview
  -> v7 Observe preview/readiness visibility
  -> ObservationService.arm() backend preview gate
```

The current observation preview loop is:

```text
ObservationRequest
  -> ObservationPreviewService
  -> optional SetupContextService snapshot attachment
  -> runtime detector/slit/calibration readiness checks
  -> ObservationPreviewResult
  -> API/UI preview visibility or backend arm gate
```

The current backend arm gate loop is:

```text
POST /api/v1/observation/arm
  -> ObservationService.arm()
  -> build single-exposure ObservationRequest
  -> ObservationPreviewService.preview_request()
  -> if preview.blocked or not single_exposure_compatible: raise interlock_blocked
  -> otherwise dispatch detector.arm_exposure
```

Explicitly not done yet:

```text
- no multi-exposure sequence runner;
- no FITS writer;
- no DataProduct pipeline;
- no frame-index consumption/auto-increment policy beyond current preview/snapshot behavior;
- no OCS adapter;
- no TCS control;
- no telescope pointing/rotator/guiding/dome/weather authority;
- no real TCS readiness integration;
- no per-channel B/G/R exposure readiness/control;
- no UI-enforced Arm disable based on preview result.
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
- Observe runtime is separately gated by JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED=1.
- Status runtime remains the safest first runtime module when the master gate is enabled.
- Instrument / Presets / Observe / Guard runtime modules remain individually gated.
- Backend API semantics are not changed merely by route selection.
```

---

## Architecture guardrails

Every phase, PR, and commit should pass these checks:

| Guardrail                   | Question                                                                                                | Purpose                            |
| --------------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| Contract first              | Is this stabilizing a domain/API contract, or merely piling UI/implementation detail?                   | Prevent UI-first semantic drift.   |
| Simulation parity           | Can the simulator and future real hardware keep the same contract?                                      | Prevent real-only hacks.           |
| No telescope overreach      | Does this bypass OCS/TCS authority for pointing, rotator, guiding, dome, weather, or telescope control? | Prevent ICS boundary violations.   |
| No fake capability          | Does this present a placeholder as a real capability?                                                   | Prevent operator misunderstanding. |
| Auditable command lifecycle | Do high-impact actions have request_id, latest_job, result, and error visibility?                       | Prevent untraceable operations.    |
| Layer boundary              | Are domain/application/kernel/api/ui/adapter responsibilities still separated?                          | Preserve maintainability.          |

---

## Completed milestone summary

### Phase 2.6: GUI and runtime operational maturity foundation

Closed.

Key durable outcomes:

```text
- /api/v1/status/full;
- operational-status direction;
- v6 review shell;
- v5 adapter;
- UI safety switches;
- X-Request-ID/latest-job thinking.
```

### Phase 2.7: Preset operational hardening

Closed.

Key durable outcomes:

```text
- preset category/risk/confirmation metadata;
- side-effect-free preset preview;
- guarded preset apply;
- structured apply result;
- latest-job linkage;
- observation arm attachment of latest successful preset summary.
```

### Phase 2.8-G/H/I/J and v7 UI IA cleanup

Closed.

Key durable outcomes:

```text
- v7 runtime gates;
- /ui default to v7.1 prototype;
- v5 fallback routes;
- served ui_operational_v7.html;
- compact operator-facing Instrument/Setup pages;
- HTML-owned durable structures enhanced by runtime JS.
```

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
- OpenAPI detector config schema-name test accepts current FastAPI/Pydantic naming variants.
```

Calibration UI fix boundary:

```text
- no backend calibration API change;
- no domain model change;
- no sequence runner;
- no real hardware behavior implied.
```

### Phase 2.9-B1: Observation request/preview domain contract

Landed on `main`.

Key durable outcomes:

```text
- ObservationFrameType strict enum exists for science / flat / arc / test.
- ExposureSpec exists with positive exp_time_s and frame_type.
- ObservationRequest uses exposures: list[ExposureSpec].
- Initial single-exposure compatibility is represented separately from the request shape.
- Multiple exposures are allowed as request shape reservation but blocked for current compatibility.
- ValidationIssue and ValidationSeverity exist.
- ReadinessItem, ReadinessState, and ReadinessSnapshot exist.
- ObservationPreviewResult represents side_effect_free, blocked, readiness, validation_issues, and single_exposure_compatible.
```

Boundary:

```text
- no sequence runner;
- no multi-exposure execution;
- no OCS adapter;
- no TCS control;
- no FITS/DataProduct implementation.
```

### Phase 2.9-B2: ObservationPreviewService application layer

Landed on `main`.

Key durable outcomes:

```text
- ObservationPreviewService exists in the application layer.
- ObservationPreviewService can attach current Setup/Data Context when missing from the request.
- ObservationPreviewService reads simulator runtime state for detector, slit, and calibration readiness.
- ObservationPreviewService performs minimal science/flat/arc calibration mode/lamp readiness validation.
- ObservationPreviewService is side-effect-free: it does not arm/start/finish exposure, create jobs, or write data products.
```

Boundary:

```text
- no API endpoint in B2;
- no UI binding in B2;
- no arm gate in B2;
- no sequence runner;
- no OCS/TCS integration;
- no FITS/DataProduct implementation.
```

### Phase 2.9-B3: side-effect-free observation preview API

Landed on `main`.

Key durable outcomes:

```text
- POST /api/v1/observation/preview exists.
- API request shape maps to the ObservationRequest domain contract.
- API response exposes ObservationPreviewResult shape.
- Preview endpoint is side-effect-free.
- Preview endpoint does not arm/start/finish exposure.
- Preview endpoint can return blocked, single_exposure_compatible, readiness, and validation_issues.
- OpenAPI response shape is tested.
```

Boundary:

```text
- no UI binding in B3;
- no arm gate in B3;
- no sequence runner;
- no OCS/TCS integration;
- no FITS/DataProduct implementation.
```

### Phase 2.9-B4: v7 Observe preview/readiness visibility

Landed on `main`.

Key durable outcomes:

```text
- v7 Observe page exposes a Preview button.
- v7 Observe page exposes Observation Preview - Readiness / Validation.
- Opt-in observe runtime can call POST /api/v1/observation/preview.
- Preview summary displays blocked / execution compatibility / detector / calibration / slit / TCS / setup-data / issues / summary.
- Preview raw JSON is available but collapsed by default.
- Command raw JSON is available but collapsed by default.
- Main operator flow shows summaries first; raw payloads are kept as diagnostics details.
- Runtime-enabled Observe controls are enabled when the opt-in observe runtime takes over the static fallback page.
```

Boundary:

```text
- preview visibility does not disable Arm in the UI;
- preview visibility does not change backend execution semantics by itself;
- no sequence runner;
- no OCS/TCS integration;
- no FITS/DataProduct implementation.
```

### Phase 2.9-B5: backend arm gate via preview readiness

Landed on `main`.

Key durable outcomes:

```text
- ObservationService.arm() now builds a single-exposure ObservationRequest before dispatch.
- ObservationService.arm() calls ObservationPreviewService.preview_request().
- If preview.blocked is true, arm is rejected before detector.arm_exposure dispatch.
- If preview.single_exposure_compatible is false, arm is rejected before dispatch.
- Blocked arm returns interlock_blocked through the API with preview details.
- Calibration/frame-type mismatch blocks arm.
- Detector busy/armed state blocks repeated arm.
- Blocked arm does not dispatch detector.arm_exposure.
- Existing start/finish/stop_readout/abort_discard paths remain separate.
- Setup context and data preview are still attached to arm metadata when the gate passes.
```

Boundary:

```text
- no multi-exposure sequence runner;
- no OCS adapter;
- no TCS control;
- no real TCS readiness integration;
- no FITS/DataProduct implementation;
- no UI-enforced Arm disable based on preview result.
```

### Post-B5 maintenance cleanup

Landed on `main`.

Key durable outcomes:

```text
- Known Starlette TestClient deprecation warning is filtered precisely in pytest configuration.
- .gitattributes exists to establish text/binary and LF policy for future commits.
- UTF-8 BOM was removed from touched test files.
- One touched mixed-line-ending test file was normalized.
- B4 UI tests now cover raw preview/command JSON collapsible sections.
- B4 UI tests now cover observe runtime button enabling behavior.
```

Boundary:

```text
- no full-repository line-ending renormalization was performed;
- existing CRLF-only files are not treated as blocking;
- no dependency migration to httpx2 was performed;
- no functional backend/API behavior was changed by this maintenance cleanup.
```

---

## Current capability status

| Capability                              | Current state                                                                    | Strategy judgment                                                                    |
| --------------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Layered architecture                    | Established                                                                      | Continue Domain / Kernel / Application / API / UI / Adapter separation.              |
| Request ID / Job audit                  | Established                                                                      | Future OCS, sequence, and data product work must preserve it.                        |
| Setup/Data Context                      | Durable backend + UI binding + observation snapshot handoff                      | Phase 2.9-A complete.                                                                |
| Observation single exposure             | Available with backend preview gate                                              | Keep as baseline while higher-level observation planning matures.                    |
| Observation request/preview domain      | Available                                                                        | B1 landed; this is a contract foundation, not sequence execution.                    |
| Observation preview application service | Available                                                                        | B2 landed; side-effect-free preview evaluates setup/runtime readiness in simulation. |
| Observation preview API                 | Available                                                                        | B3 landed; POST /api/v1/observation/preview is side-effect-free.                     |
| Observation preview UI                  | Available as v7 Observe visibility                                               | B4 landed; summary-first UI with collapsed raw JSON.                                 |
| Observation arm gate                    | Available in backend                                                             | B5 landed; arm checks preview readiness before dispatch.                             |
| Preset preview/apply                    | Available                                                                        | Needs later operator-facing diff polish.                                             |
| v7 default UI                           | Default prototype                                                                | Not final production GUI.                                                            |
| v7 runtime                              | Opt-in                                                                           | Keep explicit gates.                                                                 |
| Slit control                            | Basic available                                                                  | Preserve arcsec/um contract.                                                         |
| Calibration                             | Basic visible/control + Mode/Lamp frame-type advisory + preview readiness checks | Current preview/gate can check science/flat/arc compatibility in simulation.         |
| Detector config                         | Visible, partially writable                                                      | Avoid expanding routine detector write UI prematurely.                               |
| B/G/R channels                          | Honest summary only                                                              | No per-channel exposure readiness/control yet.                                       |
| OCS                                     | Not implemented                                                                  | Request/preview/gate foundation exists; actual adapter later.                        |
| TCS                                     | Not implemented                                                                  | Future read-only readiness; no telescope control.                                    |
| Data product                            | Not implemented                                                                  | Phase 2.9-D contract later.                                                          |
| Hardware protocols                      | Not selected                                                                     | Remain hardware-selection-driven and adapter-bounded.                                |

---

## Phase 2.9-B status and closeout path

Phase 2.9-B defines the **Observation request/preview/readiness gate contract**.

Locked decisions for the current implementation:

```text
- ObservationRequest uses exposures: list[ExposureSpec].
- Phase 2.9-B initial compatibility allows exactly one ExposureSpec only.
- Multiple exposures are a shape reservation, not sequence-runner support.
- frame_type is a strict enum.
- The execution-compatible initial frame types remain science / flat / arc / test unless explicitly extended.
- TCS readiness slot may exist in the contract, but detailed TCS fields remain unavailable/unknown for now.
- ExposureRecord/DataProduct contract should come before sequence runner.
- Do not introduce a database yet; keep protocol + JSON/JSONL style stores until real query/operations needs appear.
```

Completed slices:

```text
2.9-B1: domain model for ObservationRequest / ExposureSpec / ObservationPreviewResult / ValidationIssue / ReadinessSnapshot + domain tests         DONE
2.9-B2: application-level ObservationPreviewService + setup/runtime/calibration readiness checks + application tests                            DONE
2.9-B3: POST /api/v1/observation/preview side-effect-free API endpoint + API tests                                                           DONE
2.9-B4: v7 Observe preview/readiness visibility + compact raw JSON diagnostics + UI tests                                                     DONE
2.9-B5: backend ObservationService.arm() preview readiness gate + API/application tests                                                       DONE
```

Phase 2.9-B is not formally closed yet. Before closeout, do a short final review around:

```text
- whether backend arm gate behavior and error payload are acceptable as the stable contract;
- whether UI should add a non-blocking advisory around backend gate failures;
- whether any B5 details should be summarized in README or operator docs;
- whether docs/project_status.md and docs/ics2_software_development_strategy.md agree on the next phase;
- whether the old reference branch should be retained as reference, archived, or deleted after closeout.
```

Expected next discussion after B5:

```text
- whether to add UI advisory around backend gate errors;
- whether Phase 2.9-B can be closed after documentation review;
- whether Phase 2.9-C should focus on sequence/plan skeleton, ExposureRecord, or DataProduct contract;
- no actual multi-exposure sequence runner until the contract boundary is explicitly chosen;
- no OCS adapter yet;
- no real TCS control;
- no FITS/DataProduct implementation yet.
```

---

## Known follow-up items

### Reference branch

There is a reference branch with more aggressive Phase 2.9-B work. It can be used for selective design comparison, especially around API/UI/test ideas, but it should not be merged directly.

Current decision:

```text
- keep the branch for reference for now;
- do not merge it into main;
- revisit after Phase 2.9-B closeout;
- delete or archive only after confirming no useful design/test material remains.
```

### Line endings and encoding

Current decision:

```text
- .gitattributes establishes future LF and binary policy.
- Do not run full-repository git add --renormalize . as part of ordinary feature work.
- Existing CRLF-only files are not blocking.
- Mixed line endings in touched files should be fixed when encountered.
- UTF-8 BOM should be removed from touched source/test/doc files.
```

### TestClient deprecation warning

Current decision:

```text
- The known Starlette TestClient deprecation warning is filtered precisely for now.
- Do not migrate to httpx2 or rewrite the test client stack during observation preview/gate work.
- Revisit dependency/test-client strategy as a dedicated maintenance task later.
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
- raw JSON belongs in collapsible page detail areas and Diagnostics, not as the dominant main flow.
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
