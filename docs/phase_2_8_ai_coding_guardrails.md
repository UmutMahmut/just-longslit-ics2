# Phase 2.8 AI coding guardrails

## Purpose

This note records practical coding guardrails for Phase 2.8 frontend productization. It is intended to prevent common AI-assisted coding failure modes during iterative UI work.

The main risk is not that one individual change is large. The main risk is repeated small changes that slowly create duplicated logic, dead code, route confusion, and feature regressions.

## Guardrails

### 1. Read before adding

Before adding a new helper, route, runtime adapter, component, or document, first check whether an equivalent already exists.

For Phase 2.8 UI work, this means checking at least:

```text
src/justls/ics/app/main.py
src/justls/ics/app/ui/ui_alpha_skeleton_v5.html
src/justls/ics/app/ui/ui_operational_v6.html
src/justls/ics/app/ui/ui_operational_v7.html
src/justls/ics/app/ui/phase2d6_operational_status.js
src/justls/ics/app/ui/phase2d8_v7_status_binding.js
tests/test_ui_routes.py
docs/phase_2_8_*.md
```

Do not add another helper if a nearby existing helper can be safely extended.

### 2. Prefer modifying existing structures over adding parallel ones

AI-assisted code often creates new files or parallel functions instead of improving the existing path.

For Phase 2.8:

- do not create a second v7 status adapter unless the current one is intentionally retired;
- do not create another `/ui/v7-*` route without documenting why `/ui/v7` is insufficient;
- do not create duplicate route-serving helpers when `serve_html` / `inject_script_tag` already exist;
- do not create duplicate UI route tests when `tests/test_ui_routes.py` can be extended.

### 3. Delete or retire when replacing

If a new implementation replaces an old implementation, mark the old one as removed, retired, or explicitly preserved.

Acceptable outcomes:

```text
preserved because still used
retired because superseded
removed because dead
```

Unacceptable outcome:

```text
new code added while old unused code silently remains
```

### 4. Maintain route roles

Phase 2.8 route roles must stay stable unless explicitly changed in a documented decision:

```text
/ui    = stable default v5 baseline
/ui/v6 = operational-status review shell
/ui/v7 = operator console prototype
```

Do not change the default `/ui` route to v7 until a documented parity decision says v7 is ready.

### 5. Treat v5 as the feature baseline

`ui_alpha_skeleton_v5.html` is currently the richest UI. v7 work must not silently lose v5 operator-facing capability.

Before implementing a v7 page, compare it with v5 and record one of:

```text
implemented in v7
preserved as placeholder
deferred intentionally
not applicable
```

### 6. Avoid local-only fixes that break system behavior

Every UI change must be checked against at least these system-level questions:

```text
Does /ui still work?
Does /ui/v6 still work?
Does /ui/v7 still work?
Does the root endpoint still report the expected UI routes?
Does the change affect existing API contracts?
Does the change remove or hide any v5 capability?
```

### 7. Keep changes small but coherent

A commit should usually do one coherent thing:

```text
add v7 shell
inject v7 adapter
stabilize v7 binding
add parity inventory
```

Avoid commits that mix unrelated UI redesign, backend API changes, test rewrites, and documentation updates.

### 8. Prefer explicit binding points

For frontend runtime work, prefer stable identifiers:

```text
id="..."
data-bind="..."
data-page="..."
```

Avoid binding by visible UI copy such as labels, table headers, or translated text. Visible copy changes should not break runtime behavior.

### 9. Keep placeholders honest

If something is not wired, label it clearly:

```text
DEMO
NOT WIRED
PLACEHOLDER
FUTURE
```

Do not make a static placeholder look like real hardware telemetry.

### 10. Update tests with every route/runtime change

For Phase 2.8 route and frontend-runtime work, update or add tests for:

```text
route availability
stable default route behavior
adapter injection
static asset serving
key text / marker presence
absence of retired helper names when relevant
```

Do not rely only on visual inspection.

## Practical workflow for future Phase 2.8 tasks

For each future Phase 2.8 coding step:

```text
1. State which Phase 2.8 sub-step is being changed.
2. Inspect relevant existing files first.
3. Prefer modifying existing paths over creating parallel ones.
4. Record any intentional feature deferral.
5. Add or update a focused regression test.
6. Report the Phase 2.8 progress status after the change.
```

## Non-goals

These guardrails do not prohibit new files or new abstractions. They prohibit unnecessary duplication and undocumented divergence.

New files are acceptable when they improve structure and have a clear role, such as the v7 status adapter or parity inventory documents.
