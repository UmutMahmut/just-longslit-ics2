# Phase 2.8-H v5 to v7 feature parity audit

## Purpose

This is the working audit for Phase 2.8-H. It compares the current stable v5 default UI against the v7 operator-console prototype and records what must be preserved, reorganized, deferred, or retired before `/ui` can safely become v7.

This file is intentionally an audit/checklist, not a runtime implementation plan. It should drive the next code changes rather than follow them after the fact.

---

## Sources inspected

```text
src/justls/ics/app/main.py
src/justls/ics/app/ui/ui_alpha_skeleton_v5.html
src/justls/ics/app/ui/v5/phase2d6_operational_status.js
src/justls/ics/app/ui/ui_operational_v7.html
src/justls/ics/app/ui/v7/runtime_status.js
src/justls/ics/app/ui/v7/preset_runtime.js
src/justls/ics/app/ui/v7/observe_runtime.js
src/justls/ics/app/ui/v7/observe_guard.js
```

Known current route policy from `main.py`:

```text
/ui
  v5 default route.
  v5 Phase 2.6 operational-status adapter is enabled by default unless disabled.

/ui/v6
  v6 review shell, separately gated.

/ui/v7
  v7 shell, separately gated.
  v7 runtime master gate defaults false.
  v7 module gates are evaluated only after the master gate is enabled.
```

---

## Current page map

### v5 default UI

```text
Overview
Observation
Instrument
Presets
Cameras
Guider
Quicklook
Diagnostics
```

Characteristics:

```text
- Richest current operator-facing capability surface.
- Bilingual operator-facing layout.
- Day/night theme support.
- Message rail.
- Live-vision-first overview.
- Cameras / guider / quicklook have explicit demo/future/not-wired treatment.
- v5 adapter binds /api/v1/status/full into operational status, connection freshness, message rail, and selected data-bind fields.
```

### v7 operator-console prototype

```text
Setup
Observe
Presets
Diagnostics
Housekeeping
Engineer
```

Characteristics:

```text
- More disciplined fixed operator-console layout.
- Static by default.
- Runtime modules are opt-in.
- Setup local session fields are explicitly placeholders.
- Observe has durable latest exposure preview and B/G/R placeholders.
- Observe single-exposure controls are in one durable skeleton: #v7-observe-controls.
- Presets catalog/preview/apply is in one durable skeleton: #v7-presets-runtime.
- Diagnostics holds raw/status/runtime detail.
- Housekeeping and Engineer are reserved rather than filled with misleading controls.
```

---

## Parity classification summary

```text
Must-have before /ui -> v7:
  P0 route/runtime safety
  P1 top-level status and message rail
  P2 observation lifecycle single-exposure workflow
  P3 slit/calibration/detector operational visibility and controls
  P4 preset preview/confirm/apply workflow
  P5 diagnostics/raw status/request-id/latest_job visibility
  P6 live/latest exposure preview region with honest placeholder or real feed state

Nice-to-have before default switch:
  N1 day/night theme parity
  N2 overview-style quick action strip
  N3 richer operator summaries for ObservationMeta / Frame Results

Engineer-only / move out of main flow:
  E1 raw backend JSON
  E2 low-level logs and communications detail
  E3 future engineering utilities and unsafe controls

Deferred backend contract:
  D1 durable setup/session metadata
  D2 image backend / quicklook / data watcher
  D3 sequence runner / observing plan model
  D4 persistent observation log / audit trail
  D5 role separation and permissions
  D6 final FITS/data-product metadata contract
```

---

## P0: route/runtime safety

Status: **mostly satisfied / keep enforcing**

Evidence from current architecture:

```text
- /ui remains v5 default.
- /ui/v7 is separately served.
- v7 runtime master gate defaults off.
- Runtime modules are individually gated.
- v7 static shell must remain clickable without runtime JS.
```

Decision:

```text
must-have
```

Required before default switch:

```text
- keep /ui as v5 until parity checklist is explicitly accepted
- keep /ui/v7 static by default during audit
- do not add new runtime modules during Phase 2.8-H unless the parity audit identifies a concrete gap
- tests must continue to cover route roles and runtime script injection gates
```

---

## P1: top-level status, connection freshness, and message rail

v5 capability:

```text
- Global timing block: Local / UTC / LST / DATE / JD/MJD / runtime mode.
- Connection & Freshness block: connection state, API base, RTT, last OK, polling, stale threshold.
- Message rail with info/success/warning/error levels.
- v5 operational-status adapter polls /api/v1/status/full and updates status, connection, rail, and selected state fields.
```

v7 current state:

```text
- Top status strip exists: Run Mode / Operational / Exposure / Local Time.
- runtime_status.js can bind top status cards and Diagnostics slots when runtime is enabled.
- Message rail exists only as a static footer rail, not yet equivalent to v5's operational feedback rail.
```

Decision:

```text
must-have
```

Recommended target:

```text
- Add a durable v7 message rail or promote existing footer rail into an operator feedback rail.
- Keep raw JSON in Diagnostics, but show concise status summary in the top strip.
- Preserve request freshness language: last update, stale/online/degraded, and request-id when available.
```

Do not:

```text
- create another injected floating status panel
- bind by visible label text
```

---

## P2: observation lifecycle and single-exposure workflow

v5 capability:

```text
- Overview quick actions expose Arm / Start / Finish / Stop & Readout / Abort & Discard.
- Observation state appears in multiple summary cards.
- Observation status is sourced from /api/v1/observation/status and /api/v1/status/full.
- Operator note and observation metadata are represented in the UI surface.
```

v7 current state:

```text
- Observe page has latest exposure preview placeholder.
- Observe page has B/G/R channel placeholders.
- #v7-observe-controls contains exposure time, frame type, operator note, observation state, armed exposure, last command, runtime state, command buttons, abort confirmation, and command result.
- observe_runtime.js is opt-in and skeleton-aware.
- observe_guard.js is opt-in and frontend-only.
```

Decision:

```text
must-have
```

Recommended target:

```text
- Keep single-exposure workflow as the only Phase 2.8-H Observe runtime target.
- Present command results in a unified form: command, request_id, latest_job, state transition, and error detail.
- Reconcile button availability with backend state machine.
- Preserve abort/discard confirmation behavior.
```

Deferred:

```text
- sequence runner
- observation plan editor
- queue execution
```

---

## P3: slit, calibration, and detector controls

v5 capability:

```text
- Instrument page represents slit width and slit angle control.
- Calibration mode and lamp control are visible.
- Detector config includes profile, save, trigger, readout, B/G/R enable state, and B/G/R role mapping.
- Overview also summarizes slit/calibration/detector state.
```

v7 current state:

```text
- Setup shows current preset and detector profile as runtime-summary placeholders.
- Observe shows B/G/R visual placeholders but does not yet expose full detector config parity.
- Presets can affect detector/calibration state through backend preview/apply semantics.
- There is no dedicated v7 Instrument page; Housekeeping and Engineer are reserved.
```

Decision:

```text
must-have, with page placement decision required
```

Open design decision:

```text
Should routine slit/calibration/detector controls live in Setup, Observe, Presets, or a new/renamed Instrument area?
```

Recommended direction:

```text
- Keep routine observing controls visible to operators, not buried in Engineer.
- Put dangerous/low-level engineering actions in Engineer or Diagnostics.
- Consider a v7 "Instrument" or "Configure" page only if Setup becomes too broad.
```

Need user/team confirmation before implementation:

```text
- Which slit controls are routine observer controls versus support/engineer controls?
- Which calibration lamp/mirror actions should be directly operator-accessible?
- Whether detector B/G/R config belongs in Observe or a dedicated configuration page.
```

---

## P4: presets catalog / preview / guarded apply

v5 capability:

```text
- Presets page exposes catalog and apply feedback.
- Presets are already part of the main workflow surface.
```

v7 current state:

```text
- #v7-presets-runtime is a durable skeleton for Catalog / Preview / Guarded Apply.
- Static fallback lists the four known built-in presets.
- preset_runtime.js is opt-in, singleton-safe, and in-flight guarded.
- Preview-before-apply and confirmation-required semantics are already directionally correct.
```

Decision:

```text
must-have
```

Recommended target:

```text
- Convert preview JSON into operator-facing diff tables.
- Show affected subsystems and blocked reasons explicitly.
- On apply success, refresh status / setup / observe context.
- Keep high-risk confirmation strict.
```

Deferred:

```text
- configurable/versioned/site-specific preset source
- complete slit-preset execution chain if backend contract is incomplete
```

---

## P5: diagnostics, raw status, request-id, latest_job, and error detail

v5 capability:

```text
- Diagnostics page exists.
- Raw JSON/status visibility exists through debug/status bindings.
- v5 adapter records X-Request-ID on the operational panel title/dataset when available.
```

v7 current state:

```text
- Diagnostics page exists.
- Status / Request Troubleshooting panel contains placeholders for status source, X-Request-ID, last command, last error, and latest job.
- runtime_status.js provides opt-in raw status preview and runtime status diagnostics.
- Image Feed Diagnostics remain placeholder.
```

Decision:

```text
must-have
```

Recommended target:

```text
- Make Diagnostics the canonical home for raw JSON.
- Show request_id/latest_job/last_error in Diagnostics.
- Surface a concise command outcome in Observe/Presets while linking/debugging through Diagnostics.
```

Deferred:

```text
- full event log
- persistent observation log
- communications-log viewer
```

---

## P6: live image / latest exposure preview

v5 capability:

```text
- Overview has a Live Vision Strip.
- Slit/Guide live tile and B/G/R channel live tiles are first-class UI regions.
- Cameras, Guider, and Quicklook have their own top-level pages, marked demo/future/not-wired as appropriate.
```

v7 current state:

```text
- Observe preserves Latest Exposure Preview as a first-class placeholder.
- B/G/R preview placeholders are present.
- Diagnostics has Image Feed Diagnostics placeholder.
- No image backend is connected.
```

Decision:

```text
must-have as a region; deferred backend contract for real data
```

Recommended target for Phase 2.8-H:

```text
- Preserve the region and stale/not-wired semantics.
- Do not connect a fake image backend.
- Do not claim quicklook/data watcher is implemented.
```

Deferred to Phase 2.9 or later:

```text
- detector preview endpoint
- latest exposure image feed
- quicklook / data watcher
- frame freshness and last-frame backend contract
```

---

## N1: day/night theme parity

v5 capability:

```text
- v5 supports white/day and night themes through persisted local theme state.
```

v7 current state:

```text
- v7 currently uses a fixed console visual style.
```

Decision:

```text
nice-to-have before default switch, likely must-have before real night operations
```

Recommendation:

```text
- Do not prioritize theme parity ahead of control/workflow parity.
- Revisit after P1-P6 are stable.
```

---

## E1/E2/E3: engineering-only separation

v5 capability:

```text
- v5 exposes many broad surfaces in one rich UI.
- Some future/demo areas are visible as operator pages.
```

v7 current state:

```text
- v7 reserves Housekeeping and Engineer pages.
- Diagnostics is already the intended raw detail home.
```

Decision:

```text
engineer-only / route to Diagnostics, Housekeeping, or Engineer
```

Recommendation:

```text
- Keep raw JSON, logs, event streams, and low-level debug details out of the primary Observe flow.
- Keep unsafe future engineering controls locked, absent, or clearly read-only until role/permission contracts exist.
```

---

## D1-D6 backend-contract backlog

Do not implement these as frontend-only illusions:

```text
D1 durable setup/session metadata API
D2 image feed / latest exposure backend / quicklook / data watcher
D3 sequence runner / observing plan model
D4 persistent observation log / audit trail
D5 role separation / authentication / permission boundaries
D6 final FITS/data-product metadata contract
```

These should be designed under Phase 2.9 or later after the Phase 2.8-H parity and Phase 2.8-I workflow gaps are clearer.

---

## Initial Phase 2.8-H work queue

### H1: document and test route/runtime invariants

Status: **mostly done; verify tests**

```text
- /ui remains v5.
- /ui/v7 remains static by default.
- v7 runtime script injection is gated.
```

### H2: v7 operator feedback rail parity

Status: **not started**

```text
- Add/standardize v7 message rail binding points.
- Keep runtime_status.js binding durable elements.
```

### H3: v7 Observe result presentation parity

Status: **not started**

```text
- Standardize command result display.
- Include request_id / latest_job / state / error.
- Preserve abort confirmation.
```

### H4: slit/calibration/detector placement decision

Status: **requires user/team decision**

```text
- Decide whether v7 needs an Instrument page or whether controls are split across Setup/Observe/Presets/Engineer.
```

### H5: Presets preview UX polish

Status: **not started**

```text
- Convert raw preview JSON into operator-facing diff tables.
- Show risk, affected subsystems, blocked reasons.
```

### H6: live/quicklook placeholder hygiene

Status: **not started**

```text
- Preserve latest exposure and B/G/R placeholders.
- Make stale/not-wired status explicit.
- Defer real image backend.
```

---

## Current audit conclusion

v7 is on the right structural path, but it is not yet a default replacement for v5. The largest remaining parity question is not Presets or Observe skeleton safety; those now have reasonable opt-in prototypes. The largest functional gap is where v7 should place the broad v5 Instrument capabilities: slit, calibration, detector configuration, and their operator-vs-engineer boundaries.

Next recommended action:

```text
Resolve H4 placement decision first, then implement H2/H3/H5 in small reviewable batches.
```
