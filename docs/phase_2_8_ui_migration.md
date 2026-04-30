# Phase 2.8 UI migration

## Purpose

This document is the durable Phase 2.8 record for migrating from the current feature-rich default UI (`ui_alpha_skeleton_v5.html`) toward the productized v7 operator console prototype (`/ui/v7`).

The goal is not to copy v5 wholesale. The goal is to preserve validated operator-facing capability while reorganizing it into a cleaner, safer v7 information architecture.

## Route roles

```text
/ui
  Stable default UI.
  Backed by ui_alpha_skeleton_v5.html.
  Treat as the capability baseline.

/ui/v6
  Operational-status review shell.
  Keep available for Phase 2.6/2.7 review.

/ui/v7
  Phase 2.8 operator console prototype.
  Static shell is available by default.
  Runtime add-ons are opt-in only.
```

Do not change `/ui` to v7 until a documented parity decision says v7 is ready.

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

The v7 runtime master gate is:

```text
JUSTLS_UI_V7_RUNTIME_ENABLED=1
```

Module-level v7 runtime gates are:

```text
JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED=1   # defaults on only when the master gate is enabled
JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED=1   # opt-in
JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED=1  # opt-in
JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED=1    # opt-in
```

## Revised Phase 2.8 roadmap

```text
Phase 2.8-A route stabilization
  DONE

Phase 2.8-B v7 static shell
  DONE

Phase 2.8-C v7 runtime status prototype
  OPT-IN PROTOTYPE DONE / SINGLETON-SAFE

Phase 2.8-C/D bridge: v5 to v7 parity inventory
  DONE / MERGED INTO THIS DOCUMENT

Remote hygiene guardrails
  DONE / CONTINUING DISCIPLINE

Phase 2.8-D v7 Setup static baseline
  STATIC DONE / RUNTIME STATUS CONTEXT OPT-IN

Phase 2.8-E v7 Presets page
  STATIC SKELETON CONSOLIDATED / RUNTIME PRESET OPT-IN VERIFIED

Phase 2.8-F v7 Observe page
  STATIC SKELETON CONSOLIDATED / SINGLE-EXPOSURE RUNTIME OPT-IN READY FOR LOCAL INTERACTION TEST

Phase 2.8-G v7 runtime architecture stabilization
  IN PROGRESS / CORE DOM CONSOLIDATION MOSTLY DONE

Phase 2.8-H v5 to v7 feature parity pass
  PLANNED

Phase 2.8-I operator workflow polish
  PLANNED

Phase 2.9 new backend contracts for final frontend
  PLANNED
```

Phase 2.8-G is no longer a broad frontend extraction task. It is a runtime-stabilization task. Module extraction is allowed only when it reduces risk, duplication, or runtime instability.

## Phase 2.8-G current progress

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
  - Presets runtime was locally verified with catalog and preview flow.

NEXT
  - Local interaction test for observe_runtime.js with observe_guard.js still separately gated.
  - runtime_status.js should bind top status cards and Diagnostics slots, instead of relying mainly on extra injected panels.
  - Decide whether observe_guard.js remains a separate module or folds into observe_runtime.js after local interaction testing.
```

## Phase 2.8-G operating rules

```text
1. Keep v7 runtime add-ons opt-in by default.
2. Re-enable or revise one runtime module at a time.
3. Test locally after each runtime module change.
4. Do not add sequence runner, quicklook, image backend, or new hardware APIs in Phase 2.8-G.
5. Do not create parallel files when a durable file can be safely modified.
6. If a new file replaces an old file, delete or explicitly retire the old file in the same cleanup pass.
7. Keep /ui as v5 until v7 parity is explicitly approved.
8. Runtime JS should enhance durable HTML skeletons before creating fallback panels.
```

## Repository hygiene checklist

Run this checklist before ending each Phase 2.8-G work batch:

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
  - Does docs/phase_2_8_ui_migration.md reflect the current route/runtime state?
  - Were temporary planning notes either merged or deleted?

Runtime safety
  - Does any new frontend observer write to the same DOM subtree it observes?
  - Are fetch loops bounded or deliberately polled?
  - Can the page still open and click with runtime disabled?
```

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

## v5 to v7 parity status

### Setup

Status:

```text
PARTIAL / PHASE 2.8-D BASELINE DONE
```

v7 current state:

```text
- Setup page exists.
- Local observer/session fields are explicit placeholders.
- Data product context panel exists.
- Runtime setup readiness is available only through opt-in v7 runtime assets.
- No durable Setup backend persistence contract exists yet.
```

Next action:

```text
Do not make local session form persistence look real until a backend contract exists.
```

### Observe

Status:

```text
PARTIAL / PHASE 2.8-F BASELINE DONE / PHASE 2.8-G SKELETON CONSOLIDATED / RUNTIME OPT-IN
```

v7 current state:

```text
- Observe page exists.
- Latest Exposure Preview remains visible as a first-class placeholder.
- B/G/R placeholders remain static.
- Single Exposure Control is now a single runtime-enhanceable HTML skeleton: #v7-observe-controls.
- Runtime single-exposure controls live in ui/v7/observe_runtime.js and are opt-in only.
- observe_runtime.js is singleton-safe and skeleton-aware.
- Frontend-only observe guard lives in ui/v7/observe_guard.js and is opt-in only.
- observe_guard.js is singleton-safe and uses narrow observer fallback.
- No sequence runner, observation-plan editor, quicklook, or image backend is added in Phase 2.8-G.
```

Next action:

```text
Local interaction test should enable observe_runtime.js first, then observe_guard.js separately.
```

### Presets

Status:

```text
PARTIAL / PHASE 2.8-E BASELINE DONE / PHASE 2.8-G SKELETON CONSOLIDATED / RUNTIME OPT-IN VERIFIED
```

v7 current state:

```text
- Presets page exists.
- Presets page now has a single runtime-enhanceable HTML skeleton: #v7-presets-runtime.
- Runtime catalog/preview/guarded-apply behavior lives in ui/v7/preset_runtime.js.
- preset_runtime.js is singleton-safe and in-flight guarded.
- Runtime preset behavior is opt-in only.
- Catalog and preview flow have been locally verified.
- Preview-before-apply and confirmation-required flows must not be bypassed.
```

Next action:

```text
Do not add new preset endpoints. Keep guarded apply semantics aligned with backend confirmation rules.
```

### Diagnostics

Status:

```text
PARTIAL / PHASE 2.8-C BASELINE DONE / RUNTIME OPT-IN
```

v7 current state:

```text
- Diagnostics page exists.
- Runtime raw status preview lives in ui/v7/runtime_status.js.
- runtime_status.js is singleton-safe.
- Image feed diagnostics remain placeholders.
- Top status cards and Diagnostics slots are not yet fully consolidated into durable HTML binding points.
```

Next action:

```text
runtime_status.js should bind existing top status cards and durable Diagnostics slots before adding more status UI.
```

## Explicit non-goals

```text
- Do not replace /ui with /ui/v7.
- Do not delete v5.
- Do not add new hardware APIs.
- Do not add quicklook/data watcher.
- Do not add sequence runner.
- Do not copy v5 wholesale into v7.
```

## Current conclusion

v5 remains the capability baseline. v7 is the target structure.

Phase 2.8 should continue by measured migration:

```text
v5 richness -> v7 structure -> local validation -> stable operator console
```
