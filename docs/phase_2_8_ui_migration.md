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

  v7/
    runtime_status.js
    preset_runtime.js
    observe_runtime.js
    observe_guard.js
```

The v7 runtime assets are injected only when:

```text
JUSTLS_UI_V7_RUNTIME_ENABLED=1
```

The default `/ui/v7` page must remain static and clickable without runtime add-ons.

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
```

Avoid binding by visible label text or translated copy.

### Keep tests close to their domain

```text
tests/ui/   UI routes, static shell, static assets, runtime injection gates
tests/api/  API behavior and response contracts
tests/kernel/ kernel/runtime/domain behavior
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
PARTIAL / PHASE 2.8-F BASELINE DONE / RUNTIME OPT-IN
```

v7 current state:

```text
- Observe page exists.
- Latest Exposure Preview remains visible as a first-class placeholder.
- B/G/R placeholders remain static.
- Runtime single-exposure controls live in ui/v7/observe_runtime.js and are opt-in only.
- Frontend-only observe guard lives in ui/v7/observe_guard.js and is opt-in only.
- No sequence runner, observation-plan editor, quicklook, or image backend is added in Phase 2.8-F.
```

Next action:

```text
Future Observe cleanup should be driven by local testing of the single-exposure workflow.
```

### Presets

Status:

```text
PARTIAL / PHASE 2.8-E BASELINE DONE / RUNTIME OPT-IN
```

v7 current state:

```text
- Presets page exists.
- Runtime catalog/preview/guarded-apply behavior lives in ui/v7/preset_runtime.js.
- Runtime preset behavior is opt-in only.
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
- Image feed diagnostics remain placeholders.
```

Next action:

```text
Do not add quicklook/data watcher or image backend in Phase 2.8 without a separate backend contract.
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
