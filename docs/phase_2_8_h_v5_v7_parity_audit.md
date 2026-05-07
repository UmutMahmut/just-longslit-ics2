# Phase 2.8-H v5 to v7 feature parity audit

## Purpose

This is the working audit for Phase 2.8-H. It compares the current stable v5 default UI against the v7 operator-console prototype and records what must be preserved, reorganized, deferred, or retired before `/ui` can safely become v7.

This file is intentionally an audit/checklist, not a runtime implementation plan. It should drive the next code changes rather than follow them after the fact.

---

## Sources inspected

Repository sources:

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

External/reference sources used for the H4 architecture decision:

```text
MODS Instrument Manual, Section 4 Observing with MODS
BFOSC operating manual
P0 PDF hardware/design material for JUST long-slit spectrograph
```

The external sources are design inputs and constraints. They do not imply that the corresponding software behavior is already implemented in this repository.

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

## External reference conclusion: MODS dashboard structure

The MODS manual directly informs the H4 placement decision. It describes four user-visible MODS observing components: the MODS Control Panel GUI, modsDisp raw image display, acqMODS/execMODS scripting engines, and modsAlign. It also states that routine observers generally use the Setup and Dashboard screens, while support astronomers have access to engineering programs for health and problem handling.

MODS Setup is not the main instrument-control page. It mainly handles observer/project metadata and the next FITS filename context. These values are written into FITS headers or saved as defaults.

MODS Dashboard is the main operational control surface. Its layout follows the photon path through the instrument. It includes:

```text
Calibration and AGw Unit
  - Calibration / Observing mode
  - hatch open/closed
  - calibration projector in/out
  - calibration lamps on/off
  - all-lamps-off control
  - guide probe / guide filter / home controls

Telescope Preset Control Panel
  - target and guide-star coordinates
  - rotator / preset mode
  - telescope offsets in sky or slit-plane coordinates

Instrument Configuration
  - slit mask selection
  - dichroic selection
  - blue-channel mode
  - red-channel mode
  - Commit / Clear action model

Blue and Red Instrument Channel Control Panels
  - disperser / filter selection
  - focus and actuator information
  - exposure type, exposure time, image count
  - binning and CCD readout mode
  - GO / Pause / Stop / Abort controls
  - exposure and readout progress
  - channel status and IMCS controls

Interactive Command Entry
  - by-hand command execution for commands also available to scripts

Other Controls
  - Refresh
  - View Log
```

MODS also separates engineering detail:

```text
Housekeeping
  - power, temperature, pressure, and system housekeeping status
  - mainly useful to support astronomers or telescope operators

Utilities
  - engineering functions and instrument power management
  - regular observers should treat this area as read-only
  - unlocking/operation belongs to qualified support or instrument team members
```

Implication for ICS2.0:

```text
Setup should not become a catch-all instrument-control page.
Routine slit, calibration, and detector/channel configuration should not be buried in Engineer.
A v7 operator-facing Instrument / Configure / Dashboard-like area is justified.
Engineering-only and dangerous controls should remain in Housekeeping / Engineer / Diagnostics.
```

---

## JUST hardware facts that constrain software design

The P0 JUST long-slit spectrograph material is a binding design input for software architecture. The following facts must be considered before proposing v7 UI/API/workflow solutions:

```text
- JUST long-slit spectrograph targets 370 nm to 980 nm science spectroscopy.
- The spectrograph is a three-channel B/G/R system, not a two-channel MODS-like system.
- Nominal channel coverage:
    B: 365 nm to 573 nm
    G: 546 nm to 772 nm
    R: 747 nm to 985 nm
- Long-slit direction field requirement is >= 10 arcmin.
- Multiple slit widths are required, approximately 0.5 arcsec to 5 arcsec.
- Spectral resolution is adjustable and specified around R >= 1000 at 1 arcsec slit, with broader target range around 500 to 4500.
- Calibration includes flat-field and wavelength calibration functions.
- Calibration sources include flat-field source and wavelength lamps such as Hg(Ar), Ne, and possible ThAr/FeAr style sources.
- Slit monitoring camera is part of the instrument concept and is used to monitor/guide the target onto the slit.
- The slit camera/monitoring concept also intersects with guiding and slit-width measurement.
- The control system includes slit drive, B/G/R camera focus, B/G/R camera exposure/readout, slit-monitor camera readout and slit-width measurement, fast photometry channel, calibration lamp switching, and whole-instrument derotation.
- EtherCAT distributed control is part of the current electrical/control design direction.
```

Software implication:

```text
Do not copy MODS' two-channel Blue/Red model literally.
Use MODS as a layout and responsibility-separation reference, while modeling JUST as a B/G/R three-channel system.
Do not introduce UI or backend assumptions that contradict the P0 hardware/design material.
If a required hardware behavior is not yet implemented in the backend, mark it as deferred/backend-contract rather than faking it in frontend copy.
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
  D7 full B/G/R channel hardware-control contract
  D8 slit-monitor camera / guider / slit-width measurement contract
  D9 derotator / instrument-rotation control contract
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

## P3: slit, calibration, and detector/channel controls

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
must-have, with page placement decision now directionally resolved
```

MODS-informed direction:

```text
- v7 should add or reserve an operator-facing Instrument / Configure page.
- Routine observing controls belong there, not in Setup and not hidden under Engineer.
- This area should be Dashboard-like in responsibility, but not a literal MODS copy.
```

Recommended v7 Instrument / Configure scope:

```text
Routine operator controls and visibility:
  - slit width and slit angle
  - calibration/science mode state
  - calibration lamp state and safe lamp off action
  - detector profile and save/trigger/readout mode summary
  - B/G/R channel enable state and role mapping
  - B/G/R focus/status placeholders where backend contracts are not ready
  - clear links to Presets for common configuration actions
  - clear links to Diagnostics for raw status and request troubleshooting

Do not include as routine operator controls yet:
  - power management
  - low-level motor/drive engineering controls
  - direct EtherCAT node controls
  - unsafe maintenance actions
  - role-protected engineering operations without permission design
```

JUST-specific correction to MODS analogy:

```text
MODS has Blue and Red instrument channel panels.
JUST must be modeled as B/G/R three-channel control, with independent or coordinated status for all three channels.
Any v7 channel panel, table, or API vocabulary should use B/G/R and avoid hard-coding Blue/Red assumptions.
```

Instrument Channel Control Panels reference:

```text
MODS channel panels are useful as a responsibility model:
  - per-channel configuration
  - per-channel exposure settings
  - per-channel readout/status/progress
  - per-channel feedback during acquisition

For ICS2.0, this suggests a future B/G/R channel section, but the backend is not ready for a full per-channel control implementation. Phase 2.8-H should preserve visible B/G/R structure and classify detailed channel configuration as a backend-contract gap where needed.
```

Need user/team confirmation before implementation:

```text
- Final name: Instrument, Configure, or Dashboard.
- Which slit/calibration controls are routine observer controls versus support controls.
- Whether B/G/R detector configuration belongs entirely in Instrument/Configure, or whether exposure execution remains in Observe with configuration summary in Instrument.
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

## D1-D9 backend-contract backlog

Do not implement these as frontend-only illusions:

```text
D1 durable setup/session metadata API
D2 image feed / latest exposure backend / quicklook / data watcher
D3 sequence runner / observing plan model
D4 persistent observation log / audit trail
D5 role separation / authentication / permission boundaries
D6 final FITS/data-product metadata contract
D7 full B/G/R channel hardware-control contract
D8 slit-monitor camera / guider / slit-width measurement contract
D9 derotator / instrument-rotation control contract
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

Status: **directionally resolved; implementation not started**

```text
- v7 should have an operator-facing Instrument / Configure page or equivalent area.
- It should cover routine slit, calibration, and detector/channel configuration.
- It must model JUST as B/G/R, not MODS Blue/Red.
- Dangerous/engineering controls remain in Housekeeping / Engineer / Diagnostics.
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

### H7: v7 Instrument / Configure static placement proposal

Status: **new / next candidate**

```text
- Propose the static IA for routine instrument configuration.
- Keep it static-first and honest.
- Do not wire new backend behavior in the first pass.
- Include B/G/R channel structure as placeholder/summary where backend contracts are incomplete.
```

---

## Current audit conclusion

v7 is on the right structural path, but it is not yet a default replacement for v5. The largest remaining parity question is not Presets or Observe skeleton safety; those now have reasonable opt-in prototypes. The largest functional gap is where v7 should place the broad v5 Instrument capabilities: slit, calibration, detector configuration, and their operator-vs-engineer boundaries.

MODS supports the conclusion that routine instrument configuration belongs in an operator dashboard/configuration area, while housekeeping, utilities, logs, and unsafe controls belong elsewhere. JUST-specific hardware facts require a B/G/R three-channel interpretation rather than a literal MODS Blue/Red channel copy.

Next recommended action:

```text
Draft a v7 Instrument / Configure static page proposal, then implement it in a small static-only batch if approved.
```
