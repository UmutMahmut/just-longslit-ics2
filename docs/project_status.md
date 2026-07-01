# Project Status

## Snapshot

```text
Project: JUST Long-Slit ICS 2.0
Status: after Phase 2.9-C code closeout
Validation: pytest -q -> 233 passed
Current emphasis: freeze command-feedback baseline before the next feature phase
```

This file is a current-state snapshot. It is not a project diary. Historical details should be recovered from git history, not accumulated here.

## Current baseline

ICS 2.0 currently provides a simulator-backed, API-driven instrument-control baseline for the JUST long-slit spectrograph.

The current working loop is:

```text
Setup/session context
  -> ObservationRequest / preview
  -> backend readiness gate
  -> observation command
  -> ObservationCommandFeedbackResponse
  -> v7 Observe summary + raw diagnostics
```

The current default UI route is:

```text
/ui    -> v7.1 operator-console prototype
/ui/v7 -> explicit v7.1 route
```

The v5 fallback remains available:

```text
/ui/v5
/ui/legacy
```

## Completed baseline

### Backend and runtime

Established:

- FastAPI application and `/api/v1/*` control/status surface.
- Request ID middleware and structured error responses.
- Runtime/subsystem state aggregation.
- Exposure state model.
- Job tracking and latest-job read model.
- Dispatcher rejection behavior for invalid state, invalid param, and unsupported command cases.
- Simulation-first assembly path.
- Real adapter boundary remains explicit and not implemented by accident.

### Setup and session context

Established:

- `SessionDataContext` domain model.
- Setup context service.
- JSON-backed setup context store.
- `GET /api/v1/setup/context`.
- `PUT /api/v1/setup/context`.
- `POST /api/v1/setup/context/reload`.
- Setup context and data preview snapshot handoff into observation metadata.

### Instrument configuration

Established:

- Slit width and slit-angle API surfaces.
- Slit unit contract: operator-facing arcsec, backend command in um.
- Fixed current conversion: `1 arcsec = 128.34 um`.
- Calibration status/mode/lamp API surfaces.
- Detector configuration visibility and guarded mutation.
- v7 Instrument / Configure static structure.
- B/G/R channel summary visibility without fake per-channel hardware telemetry.

### Presets

Established:

- Preset catalog.
- Side-effect-free preset preview.
- Guarded preset apply.
- Risk and confirmation metadata.
- Latest successful preset summary attached to later observation arm metadata.

### Observation request and preview

Established in Phase 2.9-B:

- `ObservationRequest`.
- `ExposureSpec`.
- `ObservationPreviewResult`.
- `ValidationIssue`.
- `ReadinessSnapshot`.
- `ReadinessItem`.
- Strict frame type enum for `science / flat / arc / test`.
- Multiple exposure request shape reservation.
- Single-exposure compatibility gate for current execution.
- Side-effect-free `POST /api/v1/observation/preview`.
- Preview readiness checks for detector, calibration, slit, and unavailable TCS placeholder.
- Backend `ObservationService.arm()` readiness gate.

Important boundary:

```text
Preview is advisory.
Arm is independent.
Every Arm call reruns the backend readiness gate.
The UI must not become the safety authority.
```

### Observation command feedback

Established in Phase 2.9-C:

- `ObservationCommandFeedback` domain contract.
- `ObservationCommandFeedbackResponse` API schema.
- Success, blocked, and failed command shapes.
- Request ID carried into command feedback body.
- Latest job carried into command feedback.
- Dispatch error code/message/details preserved when available.
- `interlock_blocked` arm gate failures represented as blocked command feedback.
- Observation command endpoints return command feedback:

```text
POST /api/v1/observation/arm
POST /api/v1/observation/start
POST /api/v1/observation/finish
POST /api/v1/observation/stop_readout
POST /api/v1/observation/abort_discard
```

Still separate:

```text
GET  /api/v1/observation/status  -> ObservationStatusResponse
POST /api/v1/observation/preview -> ObservationPreviewResponse
```

### v7 Observe runtime

Established in Phase 2.9-C:

- v7 Observe runtime consumes `ObservationCommandFeedbackResponse`.
- Command summary shows success, blocked, and failed outcomes.
- Blocked arm can show readiness-gate reason, blocked components, and validation issues.
- Failed command can show preserved backend error code/message.
- Raw command JSON remains available in collapsible diagnostics.
- Refreshing status does not overwrite the last command summary.
- v7 status runtime, Observe runtime, and Observe guard are default-on.
- Setup, Instrument, and Presets runtimes remain default-off.

## Current test baseline

Current reported validation:

```text
pytest -q
233 passed
```

UI tests also pass after default runtime update:

```text
tests/ui -> 53 passed
```

This means code and tests are aligned with the current runtime/default route behavior.

## Explicitly not implemented

The following are intentionally not part of the current baseline:

- multi-exposure sequence runner;
- observation plan executor;
- FITS writer;
- durable DataProduct pipeline;
- ExposureRecord persistence beyond current observation metadata;
- OCS adapter;
- TCS telescope control;
- real TCS readiness integration;
- telescope pointing, rotator, guiding, dome, or weather authority;
- real hardware communication protocols;
- real B/G/R camera exposure control;
- per-channel B/G/R readiness/control;
- slit monitor image backend;
- quicklook/data watcher;
- role-based authentication or operator/engineer permission enforcement.

## Current phase status

### Phase 2.9-A

Closed.

Durable setup/session context and observation metadata snapshot handoff are complete.

### Phase 2.9-B

Closed at the code-contract level.

Observation request, preview, readiness snapshot, validation issue, preview endpoint, v7 preview visibility, and backend arm gate are implemented and tested.

### Phase 2.9-C

Code closed.

Observation command feedback contract, API response migration, request ID/error preservation, v7 Observe runtime feedback rendering, and default Observe runtime injection are implemented and tested.

Documentation closeout is in progress through README/docs rewrite.

## Recommended next feature phase

Do not extend Phase 2.9-C with new features.

The next phase should be selected from one of these focused options:

### Option A: Phase 2.9-D Data Product / Exposure Record Contract

Best if the next priority is to make “exposure completed” and “data product exists” distinct.

Candidate outputs:

```text
ExposureRecord
FrameRecord
DataProductRef
QuicklookRef
FitsHeaderSummary
QualityFlag
```

### Option B: Phase 2.9-E Read-only Observatory/TCS Context

Best if the next priority is observatory integration without telescope control.

Candidate outputs:

```text
ObservatoryContext
TcsReadinessSnapshot
Weather/Dome/Telescope read-only placeholders
stale/unavailable semantics
```

### Option C: Phase 2.9-F Operator Workflow Polish

Best if the next priority is operator clarity before deeper backend expansion.

Candidate outputs:

```text
Preset diff polish
Diagnostics command/error polish
Observe blocked/failed wording polish
Housekeeping/Engineer boundaries
```

Avoid starting a sequence runner until DataProduct/ExposureRecord semantics are clearer.

## Engineering cautions

- Do not let frontend preview state become safety authority.
- Do not present placeholder telemetry as real.
- Do not add telescope write-control inside ICS without an OCS/TCS contract.
- Do not introduce a database just because persistence will eventually matter.
- Do not turn B/G/R summary into fake per-channel readiness/control.
- Do not bury command feedback inside raw JSON only.
- Do not keep appending history to this document. Rewrite the snapshot when the phase changes.

## Documentation state

This document should be rewritten at phase boundaries.

Other durable documents:

```text
README.md
docs/ics2_software_development_strategy.md
docs/operator_console_requirements.md
```

Rules:

- README states current facts.
- Project status states current snapshot.
- Software strategy changes only when strategy changes.
- Operator-console requirements change only when UI responsibility boundaries or hardware facts change.
