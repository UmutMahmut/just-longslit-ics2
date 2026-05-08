# Project status

## Purpose

This is the durable project-status document for JUST Long-Slit ICS 2.0. It replaces the previous collection of phase-specific audit notes in `docs/`.

Keep this document focused on current direction, phase boundaries, completed milestones, open decisions, and close criteria. Do not use it as a scratchpad for every temporary idea.

Durable hardware, P0, v5 baseline, and operator-console requirements are maintained in `docs/operator_console_requirements.md`.

---

## Project goal

JUST Long-Slit ICS 2.0 is the control-system backbone for the JUST Telescope long-slit spectrograph. It is not merely a web UI project.

The system is being developed around:

```text
- simulation-first backend development;
- clear API/domain/kernel/application boundaries;
- operator-safe control surfaces;
- explicit diagnostics and request tracing;
- staged migration from the current v5 UI capability baseline to a cleaner v7.1 operator console;
- later real-hardware integration.
```

---

## Current phase

```text
Current phase:
  Phase 2.8-H: functionally closed, pending final user acceptance

Next planned phase:
  Phase 2.8-I: operator workflow polish
  Status: not started

Latest validation reported by user:
  pytest -q passed after H9.2 served-shell alignment
```

Current UI route strategy:

```text
/ui      -> v5 stable default capability baseline
/ui/v6   -> v6 operational-status review shell
/ui/v7   -> v7.1 operator-console prototype, static by default
```

Do **not** switch `/ui` to v7 yet.

---

## Completed milestone summary

### Phase 2.6: GUI and runtime operational maturity foundation

Closed.

Key durable outcomes:

```text
- `/api/v1/status/full` gained GUI-facing operational status.
- `/ui` remained the stable default entrypoint.
- `/ui/v6` was added as a review shell, not a default UI.
- UI safety switches were added for v5 adapter and v6 route exposure.
- X-Request-ID / latest-job / status-summary thinking entered the UI direction.
```

Durable lesson:

```text
Do not promote a technically healthy review shell to the default operator UI before it is more usable than the current default.
```

### Phase 2.7: Preset operational hardening

Closed.

Key durable outcomes:

```text
- presets gained category / risk_level / requires_confirmation metadata;
- side-effect-free preset preview endpoint exists;
- high-impact/engineering presets require confirmation at the API boundary;
- apply result became structured and auditable;
- successful preset apply produces latest-job audit linkage;
- observation arm can attach the latest successful preset-apply summary.
```

Durable lesson:

```text
Presets are not just configuration shortcuts. They are auditable operations and future workflow building blocks.
```

### Phase 2.8-G: v7 runtime architecture stabilization

Closed.

Key durable outcomes:

```text
- v7 runtime master gate added;
- v7 module-level runtime gates added;
- `/ui/v7` remains static by default;
- runtime_status.js, preset_runtime.js, observe_runtime.js, and observe_guard.js became singleton-safe/skeleton-aware;
- Presets and Observe each use one durable runtime-enhanceable skeleton;
- runtime JS enhances durable HTML instead of creating duplicate panels by default.
```

Durable rule:

```text
HTML owns durable structure. Runtime JS enhances it.
```

### Phase 2.8-H: v5 to v7 feature parity pass

Functionally closed, pending final user acceptance.

Completed H work:

```text
H7: v7.1 Instrument / Configure static shell
  DONE
  v7.1 IA is now Setup / Instrument / Observe / Presets / Diagnostics / Housekeeping / Engineer.

H8: v7.1 runtime compatibility check
  DONE
  Existing v7 runtime modules target the v7.1 durable skeletons.

H2: v7 operator feedback rail baseline
  DONE
  v7 status runtime now tracks request_id, RTT, last OK, connection state, severity, poll count, and freshness.

H3: Observe Finish + structured-result baseline
  DONE / baseline only
  v7 Observe now exposes Finish and structured request_id/latest_job/last_error fields.

H9: Instrument API alignment baseline
  DONE / baseline only
  v7 has an opt-in Instrument runtime gate and minimal slit/calibration/detector-read capability exposure.

H9.1: Instrument panel layout and slit dual-unit correction
  DONE
  v7 Instrument exposes arcsec and um slit-width fields, uses 128.34 um/arcsec, and provides 1.0 / 1.5 / 2.0 / 3.0 arcsec shortcuts.

H9.2: served-shell alignment check
  DONE
  The default served /ui/v7 static shell now reflects the H9.1 structure even before runtime enhancement.
```

Phase 2.8-H close criteria met:

```text
- v7.1 IA has a durable Instrument / Configure page.
- Existing runtime modules remain opt-in and skeleton-aware.
- v7.1 default route stays static and safe.
- H2 feedback rail baseline exists.
- H3 Observe lifecycle baseline exists.
- H9 Instrument API visibility/control baseline exists for routine slit/calibration plus detector read-only visibility.
- P0/v5 slit-width unit contract is preserved in code and tests.
- Docs are consolidated into project_status.md and operator_console_requirements.md.
```

---

## Phase 2.8-I: operator workflow polish

Planned after final H acceptance. Not started.

Goal:

```text
Make Setup -> Presets -> Instrument -> Observe -> Diagnostics feel like a natural operator flow.
```

Recommended I work:

```text
- clarify which Setup fields are local placeholders and which are runtime-derived;
- convert Presets JSON preview into operator-facing diff views;
- standardize Observe command result / state transition / error display;
- make Diagnostics the home for raw JSON and deeper debugging;
- clarify roles of top status cards, feedback rail, and runtime panels;
- unify latest_job / request_id / error detail presentation;
- unify button availability rules;
- unify visual language for runtime state / busy / blocked / confirmation.
```

Do not start Phase 2.8-I until explicitly approved.

---

## Items intentionally not included in Phase 2.8-H

These were intentionally held out of H, either because they are Phase 2.8-I workflow polish or later backend/hardware contracts:

```text
- N1 night/day theme strategy;
- further H3 Observe polish;
- Presets diff polish;
- workflow-level unification;
- sequence runner;
- observation plan editor;
- quicklook/data watcher backend;
- real hardware adapter integration;
- low-level EtherCAT / power / engineering controls;
- detector config write UI;
- full B/G/R hardware control;
- `/ui` -> v7 route switch.
```

---

## Phase 2.9+ deferred backend contracts

Deferred until after H/I clarify the operator surface:

```text
- durable setup/session metadata API;
- image feed / latest exposure backend / quicklook / data watcher;
- sequence runner / observing plan model;
- persistent observation log / audit trail;
- role separation / authentication / permission boundaries;
- final FITS/data-product metadata contract;
- full B/G/R channel hardware-control contract;
- slit-monitor camera / guider / slit-width measurement contract;
- derotator / instrument-rotation control contract;
- real hardware adapter validation.
```

---

## Route and runtime invariants

These must remain true unless explicitly changed by a major decision:

```text
- `/ui` remains v5 default.
- `/ui/v7` remains static and clickable by default.
- v7 runtime is opt-in through `JUSTLS_UI_V7_RUNTIME_ENABLED=1`.
- v7 module-level runtime gates remain opt-in or master-gated.
- runtime JS must enhance durable skeletons and avoid duplicate competing panels.
- raw JSON belongs in Diagnostics, not in the main Observe/Presets flow.
- unsafe engineering actions belong in Engineer/Housekeeping/Diagnostics, not routine operator flow.
```

---

## Documentation policy

`docs/` should remain small and durable.

Current durable docs:

```text
docs/project_status.md
docs/operator_console_requirements.md
```

Avoid reintroducing one-off phase notes. If a decision remains useful, fold it into one of these two files.
