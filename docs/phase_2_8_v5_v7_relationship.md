# Phase 2.8 UI relationship note: v5 baseline and v7 operator console target

## Decision

`ui_alpha_skeleton_v5.html` remains the current feature-rich default UI and must be treated as the functional baseline for Phase 2.8.

`/ui/v7` is not a replacement for v5 yet. It is the productized operator console prototype that should gradually absorb the validated operator-facing capabilities from v5 into a cleaner, more maintainable instrument-console structure.

## Why this matters

The current v5 UI has important advantages:

- it is the richest frontend currently available;
- it already exposes many observation, instrument, detector, preset, diagnostics, and live-preview concepts;
- it has a more complete operational feel than the first v7 static shell;
- it remains the safest default route for daily local development and demonstration.

The current v7 UI has a different purpose:

- it introduces a more disciplined operator-console information architecture;
- it separates Setup, Observe, Presets, Diagnostics, Housekeeping, and Engineer areas;
- it preserves the live image / latest exposure preview region as a first-class product feature;
- it creates a path toward modular frontend runtime/components/styles;
- it gives Phase 2.8 a safer prototype route without destabilizing `/ui`.

Therefore the correct Phase 2.8 strategy is not:

```text
replace v5 immediately with v7
```

The correct strategy is:

```text
keep v5 as the stable feature baseline,
use v7 as the productized console target,
and migrate only validated capabilities into v7 step by step.
```

## Route roles

```text
/ui
  Current stable default.
  Feature-rich v5 UI.
  Should not be replaced until v7 has enough parity.

/ui/v6
  Operational-status review shell.
  Useful for Phase 2.6/2.7 status/runtime review.

/ui/v7
  Phase 2.8 operator console prototype.
  Should become the future product direction only after staged parity and validation.
```

## Migration principles

### 1. Preserve v5 capability before redesigning it

If a v5 feature is useful to operators, v7 should either implement it or intentionally defer it with a visible placeholder.

Do not silently drop v5 functionality just because v7 has a cleaner layout.

### 2. Do not make v7 default prematurely

`/ui/v7` should not become the default `/ui` route until it has enough parity for daily operator use.

Minimum parity before switching defaults should include:

- status/full visibility;
- observation state and single-exposure controls;
- preset list, preview, confirmation, and apply result;
- detector profile and channel state visibility;
- calibration mode and lamp status visibility;
- diagnostics / raw status visibility;
- latest job and request-id feedback;
- live image / latest exposure preview region.

### 3. Use v5 as the checklist for v7 pages

For each v7 page, compare against v5 before considering it acceptable:

```text
Setup:
- observation/session context
- file/data context
- operator notes

Observe:
- observation lifecycle controls
- current exposure state
- frame result / latest exposure visibility
- live preview region

Presets:
- catalog
- apply feedback
- high-risk confirmation path

Diagnostics:
- raw JSON/status visibility
- request-id and error visibility
- subsystem status
```

### 4. Productize, do not merely copy

v7 should not copy v5 wholesale into a new file. The value of v7 is better information architecture and maintainability.

Where v5 is functionally richer but structurally crowded, v7 should preserve the capability but move it into clearer sections or reusable runtime/components.

### 5. Keep the live image area as a first-class feature

The live image / latest exposure preview capability is part of the product identity. It must remain visible in v7 even if the first implementation is a placeholder.

## Phase 2.8 impact

This note adjusts Phase 2.8 execution in one important way:

```text
v7 should not be evaluated only by whether it has a nicer shell.
v7 should be evaluated by whether it can eventually preserve v5's proven operator-facing richness in a cleaner structure.
```

The immediate next work after status binding should therefore be a v5-to-v7 parity inventory, not a premature default-route switch.
