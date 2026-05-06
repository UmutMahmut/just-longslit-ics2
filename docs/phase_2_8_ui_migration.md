# Phase 2.8 UI migration

## Purpose

This document is the durable Phase 2.8 record for migrating from the current feature-rich default UI (`ui_alpha_skeleton_v5.html`) toward the productized v7 operator console prototype (`/ui/v7`).

The goal is not to copy v5 wholesale. The goal is to preserve validated operator-facing capability while reorganizing it into a cleaner, safer v7 information architecture.

This file now also absorbs the earlier `phase_2_8_v5_v7_relationship.md` decision note. Keep future Phase 2.8 route, parity, and migration decisions here instead of creating parallel planning notes.

---

## Current strategic conclusion

```text
/ui      -> v5 stable default capability baseline
/ui/v6   -> v6 operational-status review shell
/ui/v7   -> future operator console prototype, static by default
```

Do **not** switch `/ui` to v7 yet.

v7 is structurally healthier than the earlier prototype: it has a stable static shell, versioned runtime assets, opt-in runtime gates, singleton-safe runtime modules, and consolidated Presets / Observe DOM skeletons. It is still not the final default operator UI.

The next mainline is:

```text
Phase 2.8-H: v5 to v7 feature parity pass
```

Avoid more scattered runtime expansion before the parity pass is complete.

---

## Route roles

### `/ui`

Stable default UI.

```text
src/justls/ics/app/ui/ui_alpha_skeleton_v5.html
```

Treat this as the current operator-facing capability baseline. It is the richest frontend currently available and remains the safest default route for daily local development and demonstration.

### `/ui/v6`

Operational-status review shell.

```text
src/justls/ics/app/ui/ui_operational_v6.html
```

Keep available for Phase 2.6/2.7 review and continuity.

### `/ui/v7`

Future operator console prototype.

```text
src/justls/ics/app/ui/ui_operational_v7.html
```

Static shell is available by default. Runtime add-ons are opt-in only. v7 should become the product direction only after staged parity and validation.

---

## Current UI asset layout

```text
src/justls/ics/app/ui/
  ui_alpha_skeleton_v5.html
  ui_operational_v6.html
  ui_operational_v7.html

  v5/
    phase2d6_operational_status.js

  v6/
    command_runtime.js
    job_alignment.js

  v7/
    runtime_status.js
    preset_runtime.js
    observe_runtime.js
    observe_guard.js
```

The default `/ui/v7` page must remain static and clickable without runtime add-ons.

---

## v7 runtime gate policy

Master gate:

```text
JUSTLS_UI_V7_RUNTIME_ENABLED=1
```

Module-level gates:

```text
JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED=1   # status module; effectively defaults on when master gate is enabled
JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED=1   # presets module
JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED=1  # observe module
JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED=1    # frontend-only observe guard
```

Recommended cleanup before starting a local server:

```powershell
Remove-Item Env:JUSTLS_UI_V7_RUNTIME_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED -ErrorAction SilentlyContinue
```

Important runtime rule:

```text
HTML owns durable structure.
Runtime JS enhances durable HTML skeletons.
Runtime JS should not create competing duplicate UI panels unless it is a fallback for a missing skeleton.
```

---

## Revised Phase 2.8 roadmap

```text
Phase 2.8-A route stabilization
  DONE

Phase 2.8-B v7 static shell
  DONE

Phase 2.8-C v7 runtime status prototype
  OPT-IN PROTOTYPE DONE / SINGLETON-SAFE / VERIFIED

Phase 2.8-C/D bridge: v5 to v7 parity inventory
  DONE / MERGED INTO THIS DOCUMENT

Remote hygiene guardrails
  DONE / CONTINUING DISCIPLINE

Phase 2.8-D v7 Setup static baseline
  STATIC DONE / RUNTIME STATUS CONTEXT OPT-IN

Phase 2.8-E v7 Presets page
  STATIC SKELETON CONSOLIDATED / RUNTIME PRESET OPT-IN VERIFIED

Phase 2.8-F v7 Observe page
  STATIC SKELETON CONSOLIDATED / SINGLE-EXPOSURE RUNTIME + GUARD OPT-IN VERIFIED

Phase 2.8-G v7 runtime architecture stabilization
  CORE STABILIZATION DONE / CURRENT BATCH CLOSED

Phase 2.8-H v5 to v7 feature parity pass
  PLANNED / NEXT

Phase 2.8-I operator workflow polish
  PLANNED

Phase 2.9 new backend contracts for final frontend
  PLANNED
```

---

## Phase 2.8-G closure record

Phase 2.8-G should no longer expand in scope. Its core purpose was to stabilize the v7 runtime architecture before any default-route decision or deeper operator workflow polish.

Actual result:

```text
DONE
  - v7 runtime master gate added.
  - v7 module-level runtime gates added.
  - /ui/v7 remains static by default.
  - runtime_status.js is singleton-safe.
  - preset_runtime.js is singleton-safe and in-flight guarded.
  - observe_runtime.js is singleton-safe and skeleton-aware.
  - observe_guard.js is singleton-safe and uses a narrow MutationObserver fallback.
  - Presets static fallback was consolidated into one runtime-enhanceable skeleton.
  - Observe static fallback was consolidated into one runtime-enhanceable skeleton.
  - runtime_status.js binds top status cards and Diagnostics detail slots.
  - Presets runtime was locally verified with catalog and preview flow.
  - Observe runtime was locally verified.
  - Observe guard was locally verified.
  - Latest reported local test status: 144 passed.
```

Explicitly not included in Phase 2.8-G:

```text
- default-enable v7 runtime
- switch /ui to v7
- add sequence runner
- add image backend
- add quicklook / data watcher
- finish production preset UX
- add durable setup/session backend
```

---

## Phase 2.8-H parity pass

### Goal

Systematically compare v5 capabilities against v7 and decide which operator-facing functions must migrate into the final operator console.

This is a capability and workflow audit, not a blind HTML-copying exercise.

### Method

For each item found in v5:

```text
1. Identify the v5 operator-facing capability.
2. Identify the current v7 home: Setup, Observe, Presets, Diagnostics, Housekeeping, or Engineer.
3. Classify the parity decision.
4. Decide whether implementation needs only frontend restructuring or a Phase 2.9 backend contract.
5. Record a test expectation before changing runtime behavior.
```

### Classification vocabulary

```text
must-have
  Required before v7 can become the default operator console.

nice-to-have
  Useful but not required for default-route promotion.

engineer-only
  Should move to Diagnostics, Housekeeping, or Engineer areas rather than main operator flow.

deferred backend contract
  Requires new or clarified backend/API/data contracts before frontend work can be honest.

not carried forward
  Intentionally retired after review.
```

### Minimum parity before `/ui` can become v7

```text
- status/full visibility
- observation state and single-exposure controls
- preset list, preview, confirmation, and apply result
- detector profile and B/G/R channel state visibility
- calibration mode and lamp status visibility
- diagnostics / raw status visibility
- latest_job and request_id feedback
- live image / latest exposure preview region
- clear placeholder treatment for not-yet-wired session/image/quicklook capabilities
```

### Initial page-by-page audit checklist

#### Setup

Compare:

```text
- observer/session context
- project / PI / support / note fields
- file/data/root-name context
- local placeholder vs backend-persisted state labeling
- data-product context and FITS/header implications
```

Likely decisions:

```text
- keep Setup fields honest as local placeholders until backend persistence exists
- defer durable session metadata API to Phase 2.9
```

#### Observe

Compare:

```text
- observation lifecycle controls
- arm/start/finish/stop_readout/abort_discard visibility
- current exposure state
- frame result / latest exposure visibility
- command feedback
- latest_job / request_id / error presentation
- live preview region
- B/G/R channel visibility
```

Likely decisions:

```text
- preserve single-exposure workflow before adding sequence runner
- defer live image backend / quicklook / data watcher to Phase 2.9 or later
```

#### Presets

Compare:

```text
- preset catalog
- preset preview
- high-risk confirmation path
- apply result feedback
- affected subsystem explanation
- blocked reason display
- latest status refresh after apply
```

Likely decisions:

```text
- preserve preview-before-apply and confirmation-required semantics
- improve operator-facing diff views before calling preset UX production-ready
```

#### Diagnostics

Compare:

```text
- raw JSON/status visibility
- subsystem status
- request-id and error visibility
- communications / event-log direction
- image/feed diagnostics placeholders
```

Likely decisions:

```text
- keep raw JSON and engineering detail in Diagnostics
- avoid pushing raw backend shape into main Observe workflow
```

#### Housekeeping / Engineer

Compare:

```text
- health and safety status
- environment and engineering telemetry placeholders
- future power / utility / locked controls
- real hardware adapter health
```

Likely decisions:

```text
- do not expose dangerous engineering controls as routine operator controls
- defer role separation and permission boundaries until contracts are clearer
```

---

## Migration principles

### 1. Preserve v5 capability before redesigning it

If a v5 feature is useful to operators, v7 should either implement it or intentionally defer it with a visible placeholder.

Do not silently drop v5 functionality just because v7 has a cleaner layout.

### 2. Do not make v7 default prematurely

`/ui/v7` should not become the default `/ui` route until it has enough parity for daily operator use.

### 3. Use v5 as the checklist for v7 pages

For each v7 page, compare against v5 before considering it acceptable.

### 4. Productize, do not merely copy

v7 should not copy v5 wholesale into a new file. The value of v7 is better information architecture and maintainability.

Where v5 is functionally richer but structurally crowded, v7 should preserve the capability but move it into clearer sections or reusable runtime/components.

### 5. Keep the live image area as a first-class feature

The live image / latest exposure preview capability is part of the product identity. It must remain visible in v7 even if the first implementation is a placeholder.

---

## Repository hygiene checklist

Run this checklist before ending each Phase 2.8 work batch:

```text
UI assets
  - Are v5/v6/v7 assets still under versioned UI directories?
  - Are there any unused phase2d6_* or phase2d8_* files left in ui/ root?
  - Does /ui/v7 remain static by default?
  - Does the v7 HTML own the durable skeleton, with runtime JS enhancing it?

Tests
  - Are new tests placed under tests/ui/, tests/api/, or tests/kernel/ by domain?
  - Did any root-level test_stage_* file get reintroduced?
  - Did the test count change for a deliberate reason?

Docs
  - Does this document reflect the current route/runtime/parity state?
  - Were temporary planning notes either merged or deleted?

Runtime safety
  - Does any new frontend observer write to the same DOM subtree it observes?
  - Are fetch loops bounded or deliberately polled?
  - Can the page still open and click with runtime disabled?
```

---

## Coding guardrails

### Read before adding

Before adding a helper, route, adapter, component, or document, check nearby existing files first. Prefer modifying an existing durable path over creating a parallel one.

For UI work, inspect at least:

```text
src/justls/ics/app/main.py
src/justls/ics/app/ui/ui_alpha_skeleton_v5.html
src/justls/ics/app/ui/ui_operational_v6.html
src/justls/ics/app/ui/ui_operational_v7.html
src/justls/ics/app/ui/v5/
src/justls/ics/app/ui/v6/
src/justls/ics/app/ui/v7/
tests/ui/
tests/api/
docs/phase_2_8_ui_migration.md
```

### Delete or retire when replacing

If a new implementation replaces an old implementation, explicitly classify the old one:

```text
preserved because still used
retired because superseded
removed because dead
```

Do not silently leave unused root-level assets after moving them into versioned UI folders.

### Keep placeholders honest

If something is not wired, label it clearly as placeholder, demo, not-wired, future, or opt-in. Static placeholders must not look like real hardware telemetry.

### Prefer explicit binding points

Runtime frontend code should bind through stable attributes such as:

```text
id="..."
data-bind="..."
data-role="..."
data-page-panel="..."
data-action="..."
```

Avoid binding by visible label text or translated copy.

### Keep tests close to their domain

```text
tests/ui/      UI routes, static shell, static assets, runtime injection gates
tests/api/     API behavior and response contracts
tests/kernel/  kernel/runtime/domain behavior
```

Avoid reintroducing root-level `test_stage_*` files. Stage history belongs in commit messages and docs; test files should describe the domain they cover.

---

## Current v7 parity status

### Setup

```text
PARTIAL / PHASE 2.8-D BASELINE DONE
```

Current state:

```text
- Setup page exists.
- Local observer/session fields are explicit placeholders.
- Data product context panel exists.
- Runtime setup readiness is available only through opt-in v7 runtime assets.
- No durable Setup backend persistence contract exists yet.
```

### Observe

```text
PARTIAL / PHASE 2.8-F BASELINE DONE / PHASE 2.8-G SKELETON CONSOLIDATED / RUNTIME OPT-IN VERIFIED
```

Current state:

```text
- Observe page exists.
- Latest Exposure Preview remains visible as a first-class placeholder.
- B/G/R placeholders remain static.
- Single Exposure Control is one runtime-enhanceable HTML skeleton: #v7-observe-controls.
- observe_runtime.js is singleton-safe and skeleton-aware.
- observe_guard.js is singleton-safe and uses a narrow observer fallback.
- No sequence runner, observation-plan editor, quicklook, or image backend is added in Phase 2.8-G.
```

### Presets

```text
PARTIAL / PHASE 2.8-E BASELINE DONE / PHASE 2.8-G SKELETON CONSOLIDATED / RUNTIME OPT-IN VERIFIED
```

Current state:

```text
- Presets page exists.
- Presets page has one runtime-enhanceable HTML skeleton: #v7-presets-runtime.
- Runtime catalog/preview/guarded-apply behavior lives in ui/v7/preset_runtime.js.
- preset_runtime.js is singleton-safe and in-flight guarded.
- Runtime preset behavior is opt-in only.
- Catalog and preview flow have been locally verified.
- Preview-before-apply and confirmation-required flows must not be bypassed.
```

### Diagnostics

```text
PARTIAL / PHASE 2.8-C BASELINE DONE / RUNTIME OPT-IN VERIFIED
```

Current state:

```text
- Diagnostics page exists.
- Runtime raw status preview lives in ui/v7/runtime_status.js.
- runtime_status.js is singleton-safe.
- Runtime Status / Setup Readiness / Raw Status Preview are consolidated under Diagnostics, not unrelated top-level clutter.
- Image feed diagnostics remain placeholders.
```

---

## Explicit non-goals

```text
- Do not replace /ui with /ui/v7.
- Do not delete v5.
- Do not default-enable v7 runtime.
- Do not add new hardware APIs in Phase 2.8-H.
- Do not add quicklook/data watcher in Phase 2.8-H.
- Do not add sequence runner in Phase 2.8-H.
- Do not copy v5 wholesale into v7.
```

---

## Current conclusion

v5 remains the capability baseline. v7 is the target structure.

Phase 2.8 continues by measured migration:

```text
v5 richness -> v7 structure -> parity audit -> local validation -> stable operator console
```
