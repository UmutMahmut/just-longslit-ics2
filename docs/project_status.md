# JUST Long-Slit ICS 2.0 project status

This is the durable project-status document for the ICS 2.0 repository. It intentionally replaces the former collection of phase-specific audit notes. Keep this file focused on decisions that still guide current work.

## Project goal

ICS 2.0 is intended to become the software control backbone for the JUST Telescope long-slit spectrograph. It is not merely a web UI project. The system must evolve into a simulation-first, API-driven, test-protected instrument control stack that can later connect to real hardware safely.

Core long-term responsibilities:

```text
- observation lifecycle control;
- slit control;
- calibration mode and lamp control;
- detector and B/G/R channel status/configuration;
- preset preview/apply/audit;
- diagnostics, request-id, latest-job, and error visibility;
- future quicklook/data watcher integration;
- future OCS/operator workflow integration;
- future real hardware adapter integration.
```

## Current route policy

```text
/ui      -> v5 stable default capability baseline
/ui/v6   -> v6 operational-status review shell
/ui/v7   -> v7.1 operator-console prototype, static by default
```

Do not switch `/ui` to v7 until Phase 2.8-H parity and the following workflow-polish phase are accepted.

## Current phase

```text
Current phase:
  Phase 2.8-H: v5 to v7 feature parity pass

Completed in H:
  H7 v7.1 Instrument / Configure static shell
  H8 v7.1 runtime compatibility check
  H2 v7 operator feedback rail baseline
  H3 Observe Finish + structured-result baseline, locally validated by user

Immediate H work:
  H-reconcile: backend/API capability -> v7.1 visibility/control alignment
  H9 decision: whether minimal Instrument runtime belongs in Phase 2.8-H

Not doing in the current version:
  N1 night/day theme strategy
  further H3 polish
  Presets diff polish
  workflow-level unification

After H:
  Phase 2.8-I operator workflow polish
```

Latest user-reported validation after H3 baseline:

```text
pytest -q
156 passed in 0.97s
```

## Phase summary

```text
Phase 2.6 GUI/runtime operational maturity
  Closed. Established operational-status concepts, UI safety switches, request-id visibility direction, and v6 review shell.
  Important decision: do not promote v6 to default /ui.

Phase 2.7 preset operational hardening
  Closed. Presets became auditable operations with metadata, preview/diff endpoint, confirmation enforcement, structured apply result, latest-job audit linkage, and observation metadata linkage.
  Important decision: preset workflow is a foundation for future operator workflow, not a sequence runner.

Phase 2.8 frontend modularization and operator-console migration
  Active. v5 remains the default capability baseline. v7.1 is the target operator-console structure and remains static/runtime-gated by default.

Phase 2.8-H v5-to-v7 parity pass
  Active. Ensure capabilities are placed and minimally visible/usable in v7.1 before entering workflow polish.

Phase 2.8-I operator workflow polish
  Planned. Make Setup -> Instrument/Presets -> Observe -> Diagnostics feel like one coherent operator workflow.

Phase 2.9+ backend contracts
  Planned. Add or clarify backend contracts for final frontend capabilities such as image feed, quicklook, data products, persistent logs, permissions, and real hardware adapters.
```

## v7 runtime gates

The v7 runtime architecture is opt-in.

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

Recommended cleanup before starting a static-shell check:

```powershell
Remove-Item Env:JUSTLS_UI_V7_RUNTIME_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED -ErrorAction SilentlyContinue
```

Runtime rule:

```text
HTML owns durable structure.
Runtime JS enhances durable HTML skeletons.
Runtime JS must not create competing duplicate UI panels unless it is a fallback for a missing skeleton.
```

## Current v7.1 status

```text
Setup
  Present. Local session/project fields are placeholders. Durable session backend is deferred.

Instrument / Configure
  Present. Correct placement for routine slit/calibration/detector visibility.
  Current gap: slit/lamp/calibration controls are structurally placed but not yet directly controllable in v7.1 runtime.

Observe
  Present. Single-exposure lifecycle baseline exists: arm, start, finish, stop_readout, abort_discard.
  H3 baseline adds request_id/latest_job/last_error binding points.
  Further command-result polish belongs to Phase 2.8-I unless required for minimal parity.

Presets
  Present. Catalog, preview, confirmation, and apply runtime exist.
  Operator-facing diff view belongs to Phase 2.8-I.

Diagnostics
  Present. Raw status, feedback rail, request-id/error direction, and runtime diagnostics exist.

Housekeeping / Engineer
  Reserved. Unsafe/low-level controls should not enter the routine operator flow without role and safety contracts.
```

## Current H9 decision point

The key Phase 2.8-H gap is Instrument API alignment.

Backend/API support exists for slit and calibration/lamp operations, and those operations are routine operator configuration rather than hidden engineering-only concepts. v7.1 currently provides the correct Instrument / Configure placement, but not direct runtime controls.

Candidate H9 scope:

```text
H9: minimal v7 Instrument runtime for existing slit/calibration APIs

Possible endpoints:
  POST /api/v1/slit
  POST /api/v1/slit_angle
  GET  /api/v1/calibration/status
  POST /api/v1/calibration/mode
  POST /api/v1/calibration/lamp

Possible read-only visibility:
  GET /api/v1/detector/config

Likely deferred from H9:
  POST /api/v1/detector/config
  full B/G/R hardware-control contract
  EtherCAT / power / low-level engineering controls
```

If H9 is accepted, it must remain a parity-restoration baseline, not workflow polish and not new hardware-contract work.

## Phase 2.8-H close criteria

Before closing H, the project should have:

```text
- v7.1 IA completed and tested;
- runtime compatibility completed and tested;
- feedback rail baseline completed and tested;
- Observe lifecycle baseline completed and tested;
- backend/API capability visibility alignment completed;
- explicit decision on H9 minimal Instrument runtime;
- if H9 accepted, minimal slit/calibration controls implemented and tested;
- if H9 rejected, direct slit/lamp control gap explicitly carried forward.
```

Only then should the project enter Phase 2.8-I.

## Phase 2.8-I planned scope

Phase 2.8-I is operator workflow polish, not raw parity placement.

Recommended work:

```text
- Make Setup -> Instrument/Presets -> Observe -> Diagnostics feel natural.
- Convert Presets raw preview into operator-facing diff/risk views.
- Standardize Observe command result/state transition/error display.
- Standardize latest_job / request_id / error presentation.
- Standardize busy/blocked/confirmation/button availability rules.
- Keep raw JSON and deep troubleshooting in Diagnostics.
```

## Deferred backend contracts

Do not fake these in frontend-only work:

```text
- durable setup/session metadata;
- live image feed / quicklook / data watcher;
- sequence runner / observing plan model;
- persistent observation log / audit trail;
- final FITS/data-product contract;
- full B/G/R channel hardware-control contract;
- slit-monitor camera / guider / slit-width measurement contract;
- derotator / instrument-rotation control contract;
- role separation, authentication, and permission boundaries;
- real hardware adapter validation.
```

## Documentation hygiene

Long-lived docs should remain few and durable. Avoid adding one-off phase notes. Append durable decisions here or to `operator_console_requirements.md` instead.
