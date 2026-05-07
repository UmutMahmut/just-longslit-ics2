# Phase 2.8-H mainline reconciliation

## Purpose

This reconciliation pass realigns the Phase 2.8-H mainline with the current repository state after the v7.1 shell rebuild, H8 runtime-compatibility check, H2 feedback-rail baseline, and H3 Observe baseline.

The goal is to distinguish three things clearly:

```text
1. capability already implemented in backend/API;
2. capability structurally placed in v7.1 UI;
3. capability actually available as v7.1 operator-facing runtime control.
```

This matters because v7.1 now has a much healthier information architecture, but some capabilities are currently only placed as skeletons/placeholders rather than fully wired controls.

---

## Current mainline

```text
Current phase:
  Phase 2.8-H: v5 to v7 feature parity pass

Completed:
  H7 v7.1 Instrument / Configure static shell
  H8 v7.1 runtime compatibility check
  H2 v7 operator feedback rail baseline
  H3 Observe Finish + structured-result baseline, locally validated by user

Immediate work:
  H-reconcile: true v5/v7.1 parity table
  Decide whether slit/lamp direct controls belong inside Phase 2.8-H

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

---

## Phase boundary correction

Some items previously discussed as possible next H work are better classified as Phase 2.8-I.

Phase 2.8-H should remain focused on:

```text
- true parity inventory;
- correct v7.1 placement;
- minimal runtime baselines needed for parity;
- honest classification of gaps;
- preserving route/runtime safety.
```

Phase 2.8-I should handle operator workflow polish:

```text
- Setup -> Presets -> Observe -> Diagnostics flow polish;
- unified command feedback;
- unified latest_job / request_id / error display;
- unified button availability rules;
- unified visual language for runtime state / busy / blocked / confirmation;
- Presets diff views and higher-level operator presentation.
```

Therefore, Presets preview diff tables and full Observe result UX polish are not required to close H unless they are needed to establish minimal parity. They should be recorded as Phase 2.8-I follow-up unless explicitly promoted.

---

## Backend/API reality check

### Slit APIs exist

```text
POST /api/v1/slit
  request: { width_um: float > 0 }
  dispatch: subsystem="slit", action="set_width"

POST /api/v1/slit_angle
  request: { angle_deg: float, -90 <= angle_deg <= 90 }
  dispatch: subsystem="slit", action="set_angle"
```

### Calibration/lamp APIs exist

```text
POST /api/v1/lamp
  legacy lamp on/off control

GET /api/v1/calibration/status
  calibration subsystem status

POST /api/v1/calibration/mode
  request: { mode: "science" | "calibration" }
  dispatch: subsystem="lamps", action="set_mode"

POST /api/v1/calibration/lamp
  request: { lamp: "flat" | "arc_hgar" | "arc_ne", enabled: bool }
  dispatch: subsystem="lamps", action="select_lamp"
```

### Safety guard exists in the dispatcher layer

Slit and lamp/calibration mutation handlers call an observation-mutation guard. If the detector is in `armed` or `exposing`, mutation commands are blocked with an invalid-state error.

This is important because slit/lamp direct controls are not purely speculative future backend work. They already have backend/API support and an initial safety boundary.

---

## True parity table

| Capability | Backend/API exists? | v5 capability baseline? | v7.1 placement? | v7.1 runtime/control? | Current H status | Recommended classification |
| --- | --- | --- | --- | --- | --- | --- |
| `/ui` route safety | yes | yes | n/a | yes | v5 remains default, v7 static by default | H done |
| v7 runtime gates | yes | n/a | n/a | yes | master + module gates tested | H done |
| Top status cards | yes via `/api/v1/status/full` | yes | top bar | yes via `runtime_status.js` | implemented | H done |
| Operator feedback rail | yes via response timing/headers/status | yes | footer rail + Diagnostics | baseline yes | H2 baseline done | H done; polish in I |
| Request ID visibility | yes, middleware returns `X-Request-ID` | partial/yes | feedback rail, Diagnostics, Observe | baseline yes | implemented in H2/H3 paths | H done; unify in I |
| Latest job visibility | yes/partial via status/job tracker | yes/partial | Diagnostics, Observe | partial | status path present; Observe payload-dependent | partial; unify in I |
| Setup observer/project/session fields | no durable persistence API | yes/local UI | Setup | local placeholder only | honest placeholder | deferred backend contract |
| Setup data/FITS context | no final data-product contract | yes/local UI | Setup | placeholder only | honest placeholder | deferred backend contract |
| Slit width | yes: `/api/v1/slit` | yes | Instrument / Configure | no v7.1 direct runtime control | structural only | H gap; candidate minimal Instrument runtime |
| Slit angle | yes: `/api/v1/slit_angle` | yes | Instrument / Configure | no v7.1 direct runtime control | structural only | H gap; candidate minimal Instrument runtime |
| Calibration mode | yes: `/api/v1/calibration/mode` | yes | Instrument / Configure | no v7.1 direct runtime control | structural only | H gap; candidate minimal Instrument runtime |
| Calibration lamp select/on/off | yes: `/api/v1/calibration/lamp` and legacy `/api/v1/lamp` | yes | Instrument / Configure | no v7.1 direct runtime control | structural only | H gap; candidate minimal Instrument runtime |
| Detector profile/config visibility | yes/partial | yes | Instrument / Configure | status binding partial | partial | H partial; deeper control may be later |
| B/G/R channel state | yes/partial in detector config/status | yes in v5 surface | Instrument / Configure | summary/status partial | partial | H partial; backend contract later |
| Observation status | yes: `/api/v1/observation/status` | yes | Observe | yes via `observe_runtime.js` | implemented | H done |
| Observation Arm | yes | yes | Observe | yes | implemented | H done |
| Observation Start | yes | yes | Observe | yes | implemented | H done |
| Observation Finish | yes: `/api/v1/observation/finish` | yes | Observe | baseline yes | H3 baseline implemented/validated | H done; polish in I |
| Stop & Readout | yes | yes | Observe | yes | implemented | H done |
| Abort & Discard | yes | yes | Observe | yes + checkbox guard | implemented | H done |
| Observe command result | yes | yes/partial | Observe | structured baseline | H3 baseline done | H done; polish in I |
| Preset catalog | yes | yes | Presets | yes via `preset_runtime.js` | implemented | H done |
| Preset preview | yes | yes | Presets | raw preview yes | implemented but raw | H done; diff polish in I |
| Preset guarded apply | yes | yes | Presets | yes | implemented | H done |
| Diagnostics raw status | yes | yes | Diagnostics | yes | implemented | H done |
| Image/latest exposure preview | no final image backend | v5 placeholder/region | Observe | placeholder only | structurally preserved | deferred backend contract |
| Cameras / Guider / Quicklook pages | no final backend | v5 first-class demo/future pages | Observe/Diagnostics placeholders | no separate pages | intentionally not copied | deferred; revisit after H/I |
| Day/night theme | frontend only | yes | not in v7.1 | no | intentionally deferred | N1 deferred |
| Sequence runner / observing plan | no final backend contract | no/limited | none | no | not in H | Phase 2.9+ |
| Role/permission separation | no final contract | no/limited | Housekeeping/Engineer reserved | no | not in H | Phase 2.9+ |

---

## Main discrepancy found

Before this reconciliation, there was a risk of treating v7.1 Instrument / Configure placement as functional parity. That is not accurate.

Correct status:

```text
Instrument / Configure placement:
  DONE

Slit/lamp direct operator control in v7.1:
  NOT DONE

Backend/API support for slit/lamp direct control:
  EXISTS
```

This is the most important Phase 2.8-H gap found by reconciliation.

---

## Decision point: slit/lamp direct controls in H?

### Option A: add minimal Instrument runtime inside Phase 2.8-H

Scope:

```text
- Add a small opt-in v7 Instrument runtime module.
- Target existing APIs only:
    POST /api/v1/slit
    POST /api/v1/slit_angle
    GET  /api/v1/calibration/status
    POST /api/v1/calibration/mode
    POST /api/v1/calibration/lamp
- Add direct controls for:
    slit width
    slit angle
    calibration/science mode
    flat / arc_hgar / arc_ne lamp enable state
- Reuse existing request_id/error/message-rail conventions.
- Keep unsafe/low-level engineering controls out.
```

Advantages:

```text
- Restores real v5 Instrument parity in v7.1.
- Uses existing backend contracts.
- Aligns with MODS-informed conclusion that routine slit/calibration controls are operator-facing, not Engineer-only.
```

Risks:

```text
- Expands H scope.
- Requires new runtime module and route gate.
- Needs careful labeling so simulated/local backend is not mistaken for final hardware readiness.
```

### Option B: record as gap and defer direct controls

Scope:

```text
- Keep v7.1 Instrument / Configure as structural placement only.
- Do not add direct slit/lamp runtime controls in H.
- Carry the gap into Phase 2.8-I or Phase 2.9.
```

Advantages:

```text
- Keeps H from expanding further.
- Avoids adding another runtime module now.
```

Risks:

```text
- v7.1 cannot claim true Instrument parity with v5.
- Routine controls with existing APIs remain inaccessible from the target operator console.
- Later workflow polish may be based on an incomplete control surface.
```

### Recommendation

Adopt Option A as a narrowly scoped Phase 2.8-H item:

```text
H9: minimal v7 Instrument runtime for existing slit/calibration APIs
```

This should not be full hardware-control work. It should be a parity-restoration baseline only.

---

## Proposed H9 scope if approved

### UI shell

Expose durable controls in served `/ui/v7` Instrument / Configure:

```text
Slit Configuration:
  input data-role="instrument-slit-width-um"
  input data-role="instrument-slit-angle-deg"
  button data-action="instrument-set-slit-width"
  button data-action="instrument-set-slit-angle"

Calibration Configuration:
  select data-role="instrument-calibration-mode"
  button data-action="instrument-set-calibration-mode"
  select data-role="instrument-calibration-lamp"
  checkbox data-role="instrument-calibration-lamp-enabled"
  button data-action="instrument-set-calibration-lamp"
  button data-action="instrument-refresh-calibration"

Result fields:
  data-bind="v7.instrument.request_id"
  data-bind="v7.instrument.last_command"
  data-bind="v7.instrument.last_error"
  data-bind="v7.instrument.result"
```

### Runtime

Add:

```text
src/justls/ics/app/ui/v7/instrument_runtime.js
```

Gate with:

```text
JUSTLS_UI_V7_INSTRUMENT_RUNTIME_ENABLED=1
```

Only injected when the v7 master runtime gate is enabled.

### Tests

Add/extend UI tests to cover:

```text
- default /ui/v7 does not inject instrument_runtime.js;
- master + instrument gate injects instrument_runtime.js;
- served /ui/v7 exposes durable Instrument controls;
- instrument_runtime.js references only existing slit/calibration endpoints;
- no Blue/Red two-channel assumptions are introduced.
```

### Non-goals

```text
- no EtherCAT node controls;
- no power-management controls;
- no unsafe maintenance actions;
- no full B/G/R detector hardware control;
- no sequence runner;
- no Phase 2.8-I workflow polish.
```

---

## Updated Phase 2.8-H close criteria

Before closing H, the project should have:

```text
- H7 v7.1 IA completed;
- H8 runtime compatibility completed;
- H2 feedback rail baseline completed;
- H3 Observe lifecycle baseline completed;
- H-reconcile true parity table recorded;
- explicit decision on H9 minimal Instrument runtime;
- if H9 accepted, minimal slit/calibration controls implemented and tested;
- if H9 rejected, slit/lamp direct control gap explicitly carried forward.
```

Only after that should we proceed to Phase 2.8-I operator workflow polish.
