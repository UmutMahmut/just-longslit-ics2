# Project Status

## Snapshot

```text
Project: JUST Long-Slit ICS 2.0
Status: after Phase 2.9-E code closeout
Validation: pytest -q -> 244 passed
Current emphasis: stabilize exposure-record and read-only observatory context before workflow polish
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
  -> ExposureRecord / simulated DataProductRef
  -> read-only ObservatoryContext
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

## Completed Baseline

Established:

- FastAPI application and `/api/v1/*` control/status surface.
- Request ID middleware and structured error responses.
- Runtime/subsystem state aggregation.
- Exposure state model.
- Job tracking and latest-job read model.
- Simulation-first assembly path.
- Setup/session context model, service, JSON store, and API.
- Slit width and slit-angle API surfaces with arcsec/um unit boundary.
- Calibration status/mode/lamp API surfaces and simulator state.
- Detector configuration visibility and guarded mutation.
- Preset catalog, preview, guarded apply, risk/confirmation metadata, and observation metadata linkage.
- Observation request, side-effect-free preview, readiness snapshot, validation issues, and backend arm gate.
- Observation command feedback for success, blocked, and failed command results.
- v7 status runtime, Observe runtime, and Observe guard default-on.

## Exposure Records

Established in Phase 2.9-D:

- `ExposureRecord`, `FrameRecord`, `DataProductRef`, `FitsHeaderSummary`, and `QualityFlag`.
- Latest exposure record attached to detector snapshots and observation metadata.
- Completed simulator exposures produce simulated data-product and quicklook references.
- Discarded exposures explicitly report `not_created` data-product state.
- Current references do not claim that real FITS or quicklook files exist.

Important boundary:

```text
Exposure completed does not mean a FITS file exists.
Simulator data products are references only.
Real file persistence remains a future writer/pipeline concern.
```

## Observatory Context

Established in Phase 2.9-E:

- `ObservatoryContext` and `ObservatoryComponentContext`.
- `GET /api/v1/observatory/context`.
- `/api/v1/status/full` includes observatory context.
- OCS, TCS, telescope, dome, weather, and guider are visible as unavailable by default.
- The context is explicitly read-only and exposes no telescope/dome/weather write route.

Important boundary:

```text
ICS can expose observatory context.
ICS still has no telescope, dome, weather, or OCS write authority.
```

## Current Test Baseline

Current reported validation:

```text
pytest -q
244 passed
```

This means code and tests are aligned with the current runtime/default route behavior.

## Explicitly Not Implemented

The following are intentionally not part of the current baseline:

- multi-exposure sequence runner;
- observation plan executor;
- FITS writer or real file persistence;
- durable DataProduct pipeline beyond current runtime/read-model contracts;
- durable ExposureRecord persistence beyond current runtime state;
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

## Current Phase Status

```text
Phase 2.9-A  Setup/Data Context                         closed
Phase 2.9-B  Observation Request / Preview / Arm Gate    closed
Phase 2.9-C  Observation Command Feedback + v7 Observe   closed
Phase 2.9-D  ExposureRecord / DataProductRef Contract    closed
Phase 2.9-E  Read-only Observatory Context               closed
```

## Recommended Next Feature Phase

Do not extend Phase 2.9-D/E with sequence or real-hardware scope.

Focused options:

- Phase 2.9-F Operator Workflow Polish: preset diff polish, diagnostics command/error polish, Observe exposure-record/data-product wording, and Housekeeping/Engineer boundaries.
- Phase 3.0 Observation Plan / Sequence Contract: observation plan, sequence preview, execution state, pause/abort/recover semantics.
- Phase 4.0 Real Hardware Adapter Hardening: detector/slit/calibration adapter parity expansion, timeout/disconnect/recovery contracts, and hardware-in-loop tests.

Avoid starting a sequence runner until the current ExposureRecord/DataProductRef contract is accepted as the baseline.

## Engineering Cautions

- Do not let frontend preview state become safety authority.
- Do not present placeholder telemetry as real.
- Do not add telescope write-control inside ICS without an OCS/TCS contract.
- Do not introduce a database just because persistence will eventually matter.
- Do not turn B/G/R summary into fake per-channel readiness/control.
- Do not imply simulator data-product references are real FITS files.
- Do not keep appending history to this document. Rewrite the snapshot when the phase changes.

## Documentation State

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
