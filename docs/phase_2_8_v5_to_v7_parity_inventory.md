# Phase 2.8 v5 to v7 parity inventory

## Purpose

This document is the working inventory for migrating from the current feature-rich default UI (`ui_alpha_skeleton_v5.html`) toward the productized v7 operator console prototype (`/ui/v7`).

The goal is not to copy v5 wholesale. The goal is to preserve v5's validated operator-facing capability while reorganizing it into a cleaner v7 information architecture.

## Current route roles

```text
/ui
  Current stable default.
  Backed by ui_alpha_skeleton_v5.html.
  Treat as the feature-rich baseline.

/ui/v6
  Operational-status review shell.
  Keep available for Phase 2.6/2.7 runtime review.

/ui/v7
  Phase 2.8 operator console prototype.
  Treat as the future productized target, not yet default.
```

## Inventory status legend

```text
DONE
  v7 already has a first usable version.

PARTIAL
  v7 has a skeleton or placeholder, but not enough parity yet.

MISSING
  v7 does not yet cover the v5 capability.

DEFERRED
  Intentionally postponed beyond the current Phase 2.8 slice.

NOT APPLICABLE
  v5 item should not be carried into v7.
```

## High-level parity table

| v5 capability area | v5 status | v7 status | Phase 2.8 action |
| --- | --- | --- | --- |
| Stable default route | Available at `/ui` | Preserved; v7 separate | Keep `/ui` on v5 until parity decision |
| Global header / timing / runtime summary | Rich header in v5 | PARTIAL: v7 topbar + runtime status panel bound to status/full | Continue using existing status/full only |
| Connection freshness | Present in v5 header | DONE/PARTIAL: v7 runtime panel shows ok/stale/error + last OK | Keep lightweight; no new heartbeat API |
| Overview-first monitoring | Present in v5 | MISSING as a dedicated v7 page | Map into v7 Observe + Runtime Status, or add Overview later |
| Live image / latest frame preview | Present as live-vision-first area / placeholders | PARTIAL: v7 Observe has Latest Exposure Preview and B/G/R placeholders | Preserve as first-class feature; no new image backend yet |
| Observation lifecycle controls | Present in v5 | DONE/PARTIAL: v7 has runtime single-exposure controls bound to existing observation endpoints | Keep single-exposure only; no sequence runner |
| Observation metadata / frame result visibility | Present or planned in v5 direction | DONE/PARTIAL: v7 observe runtime panel shows current state, armed exposure, last command, and command result JSON | Keep display lightweight until local testing |
| Slit control | Present in v5 instrument pages | MISSING in v7 | Defer until v7 Instrument/Engineer split is decided |
| Calibration control | Present in v5 | PARTIAL: v7 status/setup panels show calibration summary only | Setup/Observe should show mode; controls can wait |
| Detector config / BGR channel state | Present in v5 | PARTIAL: v7 shows detector profile and channel placeholders | Bind detector status before adding controls |
| Preset catalog | Present in v5 | DONE/PARTIAL: v7 runtime catalog is bound to existing preset endpoint | Keep static fallback marked demo/fallback |
| Preset apply feedback | Present in v5 | DONE/PARTIAL: v7 has preview result and guarded apply result | Keep guarded; do not bypass preview requirement |
| High-risk preset confirmation | Present in backend and v5 direction | DONE/PARTIAL: v7 guarded apply requires exact-name confirmation for confirmation-required presets | Preserve Phase 2.7 safety behavior |
| Diagnostics / raw JSON visibility | Present in v5 | DONE/PARTIAL: v7 Diagnostics has bounded raw status/full preview | Keep bounded and read-only |
| Request ID visibility | Present in Phase 2.6/2.7 direction | DONE/PARTIAL: v7 runtime/setup panels show request id | Keep in runtime panel and diagnostics |
| Latest job feedback | Present in Phase 2.6/2.7 direction | DONE/PARTIAL: v7 runtime/setup panels show latest job | Improve display, do not duplicate logic |
| Day/night theme support | Present in v5 | MISSING in v7 | Defer until v7 structure stabilizes |
| Cameras / guider first-class pages | Present as v5 concept / placeholders | MISSING in v7 | Defer; do not add until Phase 2.8 scope allows |
| Housekeeping | Present or conceptual in v5 direction | PARTIAL: v7 route placeholder | Defer binding |
| Engineer utilities | Present or conceptual in v5 direction | PARTIAL: v7 route placeholder | Defer binding |

## Page-by-page parity notes

### 1. Setup

v5 baseline:

```text
- general operator context
- observation/session context concepts
- data product / frame context concepts
- detector and preset context visible in broader UI
```

v7 current:

```text
- Setup page exists
- Observer(s), Project ID, PI, Support, Comment fields exist
- Root Name / Date Prefix / Current Preset / Detector Profile fields exist
- Data Product Context panel exists
- Setup Readiness panel is injected by the v7 status adapter
- Setup Readiness uses existing /api/v1/status/full only
- runtime summary includes connection, run mode, operational level, observation state, detector profile, calibration, preset context, save enabled, latest job, and request id
- local session fields are explicitly marked with data-role/data-phase as local placeholders
- placeholder actions are marked not-wired
```

Status:

```text
PARTIAL / PHASE 2.8-D BASELINE DONE
```

Next v7 action:

```text
Do not add new Setup backend APIs yet.
Do not make local session form persistence look real until a durable backend contract exists.
Future Setup work should either keep the form local or explicitly define a session-context API before binding Save/Apply.
```

### 2. Observe

v5 baseline:

```text
- observation lifecycle controls
- exposure state visibility
- last exposure / frame results direction
- live-vision-first preview area
```

v7 current:

```text
- Observe page exists
- Latest Exposure Preview is visible and remains a first-class placeholder
- B/G/R channel placeholders exist and are not rewired in Phase 2.8-F
- Runtime Observe Controls panel is injected by phase2d8_v7_observe_controls.js
- runtime observe controls bind only existing single-exposure endpoints:
  - GET /api/v1/observation/status
  - POST /api/v1/observation/arm
  - POST /api/v1/observation/start
  - POST /api/v1/observation/stop_readout
  - POST /api/v1/observation/abort_discard
- static Observe control panel is explicitly marked fallback/demo and disabled
- abort/discard requires an explicit checkbox in the runtime controls
- frontend-only observe safety guard is injected by phase2d8_v7_observe_safety_guard.js after the observe controls
- observe safety guard does not call backend APIs; it only constrains visible button availability
- backend remains the final authority for valid observation state transitions
```

Status:

```text
PARTIAL / PHASE 2.8-F BASELINE DONE
```

Next v7 action:

```text
Do not introduce sequence runner or observation-plan features.
Do not add quicklook/data watcher or image backend in Phase 2.8-F.
Future cleanup should be driven by local testing of the single-exposure workflow and button-state behavior.
```

### 3. Presets

v5 baseline:

```text
- preset catalog
- preset apply visibility
- detector/calibration result feedback
- high-risk confirmation direction from Phase 2.7
```

v7 current:

```text
- Presets page exists
- Runtime Presets panel is injected by phase2d8_v7_status_binding.js
- runtime catalog is bound to GET /api/v1/presets
- runtime preview is bound to POST /api/v1/presets/preview
- static preset table and static preview/apply panel are explicitly marked fallback/demo
- guarded apply add-on is injected by phase2d8_v7_preset_apply_guard.js after the status/preset adapter
- guarded apply calls existing POST /api/v1/presets/apply only after a preview is available
- confirmation-required presets require an explicit checkbox and exact preset-name text confirmation before apply
- apply result is shown in the guarded apply panel
```

Status:

```text
PARTIAL / PHASE 2.8-E BASELINE DONE
```

Next v7 action:

```text
Do not add new preset endpoints.
Do not remove the preview-before-apply guard.
Do not let static fallback/demo controls become active.
Future cleanup can consolidate preset UI once local testing confirms the guarded workflow feels acceptable.
```

### 4. Diagnostics

v5 baseline:

```text
- diagnostics page
- raw JSON/status visibility
- request troubleshooting direction
```

v7 current:

```text
- Diagnostics page exists
- Status / Request Troubleshooting panel exists
- Image Feed Diagnostics placeholder exists
- runtime panel shows request id and latest error
- bounded raw status/full preview is injected by the v7 status adapter
- raw preview is read-only and capped to avoid oversized UI payloads
```

Status:

```text
PARTIAL / PHASE 2.8-C BASELINE DONE
```

Next v7 action:

```text
Keep image feed diagnostics honest as NOT WIRED until a real backend exists.
Do not add quicklook/data watcher in Phase 2.8-C/D/E/F.
```

### 5. Instrument / Detector / Calibration / Slit

v5 baseline:

```text
- instrument pages for slit, calibration, detector
- detector channel configuration and status concepts
- calibration/lamp controls
- slit width and angle controls
```

v7 current:

```text
- no dedicated Instrument page yet
- detector profile is visible in runtime/setup panels
- calibration summary is visible in runtime/setup panels
- channel preview placeholders exist in Observe
```

Status:

```text
MISSING/PARTIAL
```

Next v7 action:

```text
Do not add all instrument controls at once.
First decide whether these belong in Observe, Housekeeping, or Engineer.
Prefer status visibility before command controls.
```

## Immediate recommended sequence

To avoid AI-style drift and duplication, continue Phase 2.8 in this order:

```text
1. Finish Phase 2.8-C status binding polish
   - connection stale/error display
   - bounded raw status preview if useful
   - no new APIs
   - status: baseline done

2. Phase 2.8-D Setup page
   - use status/full data only
   - keep form local/static for now
   - make Setup look like instrument preparation, not generic web form
   - status: baseline done; future backend persistence deferred

3. Phase 2.8-E Presets page
   - inspect existing preset API semantics first
   - bind existing preset catalog/apply/confirmation semantics
   - preserve Phase 2.7 safety behavior
   - status: baseline done; future UX cleanup deferred until local testing

4. Phase 2.8-F Observe page
   - inspect existing observation API semantics first
   - bind single-exposure controls only
   - keep live preview region
   - no sequence runner yet
   - status: baseline done; future UX cleanup deferred until local testing

5. Phase 2.8-G extraction
   - extract only stable runtime/components after behavior settles
```

## Explicit non-goals for this inventory step

```text
- Do not replace /ui with /ui/v7.
- Do not delete v5.
- Do not add new hardware APIs.
- Do not add quicklook/data watcher.
- Do not add sequence runner.
- Do not copy v5 wholesale into v7.
```

## Current conclusion

v5 is the current capability baseline. v7 is the target structure.

Phase 2.8 should proceed by measured parity migration:

```text
v5 richness -> v7 structure -> stable operator console
```
