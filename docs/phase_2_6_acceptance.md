# Phase 2.6 acceptance checklist

Phase 2.6 is the first MODS/BFOSC-inspired GUI and runtime maturity step for JUST Long-Slit ICS 2.0. The goal is not to add new hardware scope or introduce an Observation Plan / Sequence Runner yet. The goal is to make the current control surface more operationally mature, observable, and reviewable.

## Scope

Phase 2.6 covers:

- a derived backend `operational_status` summary for GUI state gating;
- an explicit `/ui/v6` operational shell while keeping `/ui` on the existing v5 path;
- frontend runtime separation for status polling, POST command execution, and latest-job alignment;
- visible request-id and latest-job traceability for observer-side troubleshooting;
- a clear Observer / Engineering / Diagnostics boundary in the new shell;
- environment-level UI safety switches for disabling v5 adapter injection or `/ui/v6` without reverting code.

Phase 2.6 deliberately does not cover:

- Observation Plan / Sequence Runner;
- acquisition/science/calibration/procedure script execution;
- real data watcher or quicklook pipeline;
- real alignment/guide tooling;
- authentication or role-based authorization;
- real EtherCAT/device recovery panels.

These remain later-phase work.

## Safety switches

Two environment switches provide a soft rollback path for Phase 2.6 UI features:

```bash
JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED=0
JUSTLS_UI_V6_ENABLED=0
```

Effects:

- `JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED=0` keeps `/ui` on the existing v5 HTML without injecting `phase2d6_operational_status.js`.
- `JUSTLS_UI_V6_ENABLED=0` hides `ui_v6` from `/` and makes `/ui/v6` return 404.

Accepted false values are `0`, `false`, `no`, `off`, and `disabled`.

These switches do not remove the backend `operational_status` field from `/api/v1/status/full`; they only control UI exposure.

## Delivered pieces

### A1: backend operational status base

`/api/v1/status/full` now includes `operational_status` derived from the existing runtime snapshot, exposure state, subsystem states, and latest job. This is intentionally not a second state machine.

Expected fields include:

- `level`: `ok`, `busy`, `warning`, or `error`;
- `summary`;
- `control_state`;
- `exposure_state`;
- `flags` for `busy`, `fault`, `disconnected`, `interlock_blocked`, `armed`, `exposing`, and `reading_out`;
- `latest_job`;
- `ui_hints`.

Acceptance checks:

- `GET /api/v1/status/full` returns `operational_status`.
- Ready state maps to `level == "ok"`.
- Exposing state maps to `level == "busy"` and `flags.exposing == true`.
- Existing runtime state remains the source of truth.

### A2: UI consumption and v6 shell

The existing `/ui` route keeps serving the current v5 skeleton, with a small adapter injected to consume `operational_status` when `JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED` is not disabled.

A new `/ui/v6` route serves `ui_operational_v6.html`, a structured operational shell with explicit command and risk markers when `JUSTLS_UI_V6_ENABLED` is not disabled:

- `data-command="observation.arm"`
- `data-command="observation.start"`
- `data-command="observation.stop_readout"`
- `data-command="observation.abort_discard"`
- `data-risk="high-impact-config"`

Acceptance checks:

- `GET /` advertises `ui_v6: "/ui/v6"` when v6 is enabled.
- `GET /ui` still loads the v5 route and adapter by default.
- `GET /ui/v6` loads the v6 shell by default.
- v6 does not replace `/ui` until explicitly approved.
- Setting `JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED=0` disables adapter injection into `/ui`.
- Setting `JUSTLS_UI_V6_ENABLED=0` disables `/ui/v6` and hides it from `/`.

### A2.1: status polling hardening

`phase2d6_operational_status.js` owns status polling and state binding.

Network behavior:

- GET `/api/v1/status/full` uses `AbortController` timeout.
- At most one status refresh is in flight.
- Status refresh failure degrades the message rail instead of blocking the page.

Acceptance checks:

- The adapter contains `STATUS_TIMEOUT_MS`.
- The adapter contains `statusRefreshInFlight`.
- The adapter does not issue overlapping status refreshes.

### A2.2: explicit command/risk marker model

The operational status adapter prefers explicit markers and only uses a command marker catalog for v5 transition support.

Acceptance checks:

- v6 shell has explicit command/risk markers.
- The adapter recognizes `data-command` and `data-risk`.
- The adapter preserves original disabled state and does not force-enable originally disabled controls.

### A2.3: v6 status binding

The v6 shell binds key fields from `/api/v1/status/full`:

- runtime mode;
- API base;
- slit width;
- slit angle;
- lamp state;
- detector profile;
- calibration mode;
- observation state;
- operational level and summary.

Acceptance checks:

- The status panel updates from `/api/v1/status/full`.
- Manual refresh is available through `data-command="status.refresh"`.

### A2.4: command runtime hardening

`phase2d6_command_runtime.js` owns POST command execution.

Command behavior:

- POST commands use a timeout.
- POST commands are not automatically retried.
- A single `commandInFlight` guard prevents duplicate command submission.
- Each command sends `X-Request-ID`.
- Command status, action, and request id are displayed in a command panel.
- Dangerous actions still require confirmation.

Acceptance checks:

- The command runtime contains `COMMAND_TIMEOUT_MS`.
- The command runtime contains `commandInFlight`.
- The command runtime sends `X-Request-ID`.
- `Stop & Readout` and `Abort & Discard` still confirm before execution.

### A2.5: latest job alignment

`phase2d6_job_alignment.js` owns latest job and command result alignment.

It listens for:

- `phase2d6:status-full`;
- `phase2d6:command-result`.

It displays:

- latest job status;
- subsystem;
- action;
- job id;
- error;
- alignment state between the last command result and backend latest job.

Acceptance checks:

- The job alignment adapter listens to explicit events.
- It does not monkey-patch `window.fetch`.
- It does not own status polling or command execution.

### A2.6: frontend runtime responsibility cleanup

Final frontend runtime responsibility boundary:

- `phase2d6_operational_status.js`: GET `/status/full`, status binding, operational gating, and `phase2d6:status-full` event emission.
- `phase2d6_command_runtime.js`: POST command execution, timeout, request id, anti-double-submit, and `phase2d6:command-result` event emission.
- `phase2d6_job_alignment.js`: listen-only latest job / command result alignment.

Acceptance checks:

- `phase2d6_operational_status.js` emits `phase2d6:status-full` explicitly.
- `phase2d6_job_alignment.js` does not contain `installStatusFetchTap`.
- `phase2d6_job_alignment.js` does not assign `window.fetch = ...`.

## Suggested local validation before merge

Run the test suite:

```bash
pytest
```

Manual smoke test on the PR branch:

```bash
git fetch origin
git checkout phase-2.6-ui-safety-switches
uvicorn justls.ics.app.main:app --reload
```

Then open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/ui`
- `http://127.0.0.1:8000/ui/v6`
- `http://127.0.0.1:8000/api/v1/status/full`

Safety-switch smoke tests:

```bash
JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED=0 uvicorn justls.ics.app.main:app --reload
JUSTLS_UI_V6_ENABLED=0 uvicorn justls.ics.app.main:app --reload
```

Manual behavior checks:

1. `/ui` still loads the existing v5 UI path.
2. `/ui/v6` loads the operational shell when enabled.
3. `Operational`, `Command`, and `Latest Job` panels appear in v6.
4. `Arm` is allowed in ready state.
5. `Start` is disabled until armed.
6. `Stop & Readout` and `Abort & Discard` are gated by exposure state and confirmation dialogs.
7. High-impact config controls are blocked when armed/exposing/reading out.
8. Command panel shows command status and request id after a POST command.
9. Latest Job panel updates after status refresh.
10. Adapter injection and `/ui/v6` can be disabled independently by environment variables.

## Merge decision boundary

Merge is reasonable after:

- automated tests pass locally or in CI;
- `/ui/v6` smoke test is acceptable;
- the user confirms whether `/ui` should remain v5 for now.

Recommended default: keep `/ui` on v5 and expose `/ui/v6` as a reviewable new shell. Promote v6 to the default `/ui` only in a later, explicit PR or after direct approval.
