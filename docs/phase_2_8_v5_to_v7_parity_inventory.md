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
| Global header / timing / runtime summary | Rich header in v5 | PARTIAL: v7 topbar + runtime status panel | Continue binding v7 to existing status/full only |
| Connection freshness | Present in v5 header | PARTIAL: v7 runtime panel shows connection / last OK | Improve stale/error visualization in v7-C only |
| Overview-first monitoring | Present in v5 | MISSING as a dedicated v7 page | Map into v7 Observe + Runtime Status, or add Overview later |
| Live image / latest frame preview | Present as live-vision-first area / placeholders | PARTIAL: v7 Observe has Latest Exposure Preview and B/G/R placeholders | Preserve as first-class feature; no new image backend yet |
| Observation lifecycle controls | Present in v5 | PARTIAL: v7 Observe has static controls | Phase 2.8-F should bind existing observation APIs |
| Observation metadata / frame result visibility | Present or planned in v5 direction | PARTIAL/MISSING in v7 | Bring into Observe after status binding is stable |
| Slit control | Present in v5 instrument pages | MISSING in v7 | Defer until v7 Instrument/Engineer split is decided |
| Calibration control | Present in v5 | PARTIAL: v7 status panel shows calibration summary only | Setup/Observe should show mode; controls can wait |
| Detector config / BGR channel state | Present in v5 | PARTIAL: v7 has detector profile and channel placeholders | Bind detector status before adding controls |
| Preset catalog | Present in v5 | PARTIAL: v7 has static list | Phase 2.8-E should bind `/api/v1/presets` |
| Preset apply feedback | Present in v5 | MISSING/PARTIAL | Phase 2.8-E should bind preview/apply/latest_job |
| High-risk preset confirmation | Present in backend and v5 direction | MISSING in v7 | Add confirmation in Phase 2.8-E only |
| Diagnostics / raw JSON visibility | Present in v5 | PARTIAL: v7 Diagnostics skeleton only | Add raw status preview after core status binding |
| Request ID visibility | Present in Phase 2.6/2.7 direction | PARTIAL: v7 runtime panel shows request id | Keep in runtime panel and diagnostics |
| Latest job feedback | Present in Phase 2.6/2.7 direction | PARTIAL: v7 runtime panel shows latest job | Improve display, do not duplicate logic |
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
- fields are currently local/static except global runtime panel
```

Status:

```text
PARTIAL
```

Next v7 action:

```text
Phase 2.8-D should keep Setup mostly frontend/local first.
Do not add new backend APIs yet.
Use existing status/full data only for current preset, detector profile, calibration mode, and latest job context.
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
- Latest Exposure Preview is visible
- B/G/R channel placeholders exist
- Arm / Start / Stop & Readout / Abort & Discard buttons exist but are static
- runtime status panel shows exposure state and latest job
```

Status:

```text
PARTIAL
```

Next v7 action:

```text
After Phase 2.8-C finishes, Phase 2.8-F should bind buttons to existing observation APIs.
Do not introduce sequence runner or new observation-plan features.
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
- static preset table exists
- static preview/apply panel exists
- no live catalog binding yet
- no preview/apply binding yet
```

Status:

```text
PARTIAL
```

Next v7 action:

```text
Phase 2.8-E should bind GET /api/v1/presets, preset preview if available, apply result, confirmation, and latest_job.
Do not redesign preset semantics.
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
- no raw JSON preview yet
```

Status:

```text
PARTIAL
```

Next v7 action:

```text
Add a bounded raw status/full preview after core status binding is stable.
Keep image feed diagnostics honest as NOT WIRED until a real backend exists.
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
- detector profile is visible in runtime panel
- calibration summary is visible in runtime panel
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

2. Phase 2.8-D Setup page
   - use status/full data only
   - keep form local/static for now
   - make Setup look like instrument preparation, not generic web form

3. Phase 2.8-E Presets page
   - bind existing preset catalog/apply/confirmation semantics
   - preserve Phase 2.7 safety behavior

4. Phase 2.8-F Observe page
   - bind single-exposure controls only
   - keep live preview region
   - no sequence runner yet

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
