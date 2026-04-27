# Phase 2.6 status and A3 UX plan

This document freezes the current Phase 2.6-A2 work and defines the next Phase 2.6 steps.

## Current phase position

Phase 2.6 is the MODS/BFOSC-inspired GUI and runtime maturity stage. It sits after Phase 2.5 and before broader Phase 3 hardware / OCS / data-chain expansion.

Current status after the merged Phase 2.6 PRs:

- A1 backend operational status base: complete enough for current use.
- A2 UI consumption chain: complete enough for current use; no more adapter/runtime feature work should be added in A2.
- A3 default entrypoint and user-experience closure: next focus.
- A4 documentation / operator notes: partly complete, still needs a short operator-facing guide.
- A5 final Phase 2.6 audit: not started.

Approximate Phase 2.6 completion: 65% to 70%.

## A2 freeze

A2 introduced the following pieces:

- `operational_status` in `/api/v1/status/full`;
- `/ui` remains the existing v5 route;
- `/ui/v6` provides a reviewable operational shell;
- `phase2d6_operational_status.js` handles status polling and operational gating;
- `phase2d6_command_runtime.js` handles POST command execution;
- `phase2d6_job_alignment.js` handles latest-job / command-result alignment;
- environment switches can disable v5 adapter injection or `/ui/v6` exposure.

A2 should now be treated as frozen except for bug fixes.

Do not add the following under A2 anymore:

- new command types;
- new hardware controls;
- additional frontend runtime layers;
- Observation Plan / Sequence Runner behavior;
- data watcher or quicklook behavior;
- real guide/alignment tooling.

## A3 goal

A3 is not a rewrite and not a promotion of v6 to default by default.

A3 answers one operational question:

> What should an observer see first, and how do they understand which UI path is safe to use?

A3 should produce a small, explicit entrypoint policy rather than another large UI implementation.

## A3 recommended decision

For now:

- Keep `/ui` as the stable default route.
- Keep `/ui/v6` as the reviewable operational shell.
- Do not promote v6 to `/ui` until it has been manually reviewed.
- Keep both UI safety switches available.

This preserves the current stable path while allowing Phase 2.6 review and iteration.

## A3 minimum implementation options

Preferred minimal A3 implementation:

1. Add a short UI entrypoint note to the repository documentation.
2. Add a small operator-facing guide explaining:
   - `/ui` is the stable v5 route;
   - `/ui/v6` is the Phase 2.6 operational shell;
   - how to disable v5 adapter injection;
   - how to disable `/ui/v6`;
   - how to revert the merged Phase 2.6 commits if needed.
3. Avoid adding new tests unless a code change requires them.

Optional later implementation:

- Add a lightweight `/ui/help` or `/ui/entry` page only if manual use shows that `/`, `/ui`, and `/ui/v6` are confusing.

## A4 target

A4 should be a short operator note, not a large manual.

Recommended document:

- `docs/phase_2_6_operator_notes.md`

It should explain:

- current UI entrypoints;
- safety switches;
- expected status panels;
- known limitations;
- rollback commands.

## A5 target

A5 should be the final Phase 2.6 audit.

Audit questions:

1. Does `/api/v1/status/full` remain schema-consistent?
2. Does `/ui` remain stable and recoverable?
3. Does `/ui/v6` remain review-only?
4. Are safety switches documented and functional?
5. Has A2 stopped expanding?
6. Are the remaining MODS/BFOSC-inspired items correctly deferred to Phase 2.7 / Phase 3 / Phase 4?

## Deferred items

The following are intentionally deferred:

- preset-as-operation hardening;
- acquisition / science / calibration / procedure classification;
- Observation Plan / Sequence Runner;
- data watcher / quicklook agent;
- alignment / guide workspace;
- real engineering panels;
- authentication / role authorization.

These should not be pulled back into Phase 2.6-A3.
