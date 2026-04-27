# Phase 2.6 operator notes

This note explains how to use and roll back the Phase 2.6 GUI/runtime maturity changes.

Phase 2.6 is not a new observing-plan system. It does not add real hardware devices, a data watcher, guide/alignment tools, or a MODS-style script runner. It only adds a more explicit operational status layer and a reviewable UI v6 shell.

## Current UI entrypoints

### `/ui`

`/ui` remains the stable default UI path.

By default, it serves the existing v5 HTML and injects a small Phase 2.6 operational-status adapter. This adapter lets the older UI consume the new `/api/v1/status/full.operational_status` block.

Use `/ui` when you want the least surprising path.

### `/ui/v6`

`/ui/v6` is the Phase 2.6 operational shell.

It is intended for review and controlled testing. It is not yet promoted to the default `/ui` route.

It contains:

- observer state summary;
- observation controls with explicit `data-command` markers;
- high-impact configuration controls with explicit `data-risk` markers;
- engineering/diagnostics separation;
- command status and `X-Request-ID` display;
- latest-job alignment display.

Use `/ui/v6` when reviewing the new operational workflow.

## Backend status entrypoint

`GET /api/v1/status/full` now includes:

```json
{
  "operational_status": {
    "level": "ok | busy | warning | error",
    "summary": "...",
    "control_state": "...",
    "exposure_state": "...",
    "flags": {
      "busy": false,
      "fault": false,
      "disconnected": false,
      "interlock_blocked": false,
      "armed": false,
      "exposing": false,
      "reading_out": false
    },
    "latest_job": null
  }
}
```

This is a derived status block. It does not replace the backend state machine.

## UI safety switches

Two environment variables can soften or disable the Phase 2.6 UI exposure without reverting code.

### Disable Phase 2.6 adapter injection into `/ui`

```bash
JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED=0
```

Effect:

- `/ui` still serves the v5 HTML;
- `phase2d6_operational_status.js` is not injected into `/ui`;
- `/api/v1/status/full.operational_status` remains available.

Use this if the v5 adapter causes unexpected UI behavior.

### Disable `/ui/v6`

```bash
JUSTLS_UI_V6_ENABLED=0
```

Effect:

- `/` reports `ui_v6: null`;
- `/ui/v6` returns 404;
- `/ui` remains available.

Use this if the review shell should not be exposed.

Accepted false values are:

```text
0, false, no, off, disabled
```

## Suggested local launch commands

Normal launch:

```bash
uvicorn justls.ics.app.main:app --reload
```

Launch with v5 adapter disabled:

```bash
JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED=0 uvicorn justls.ics.app.main:app --reload
```

Launch with v6 disabled:

```bash
JUSTLS_UI_V6_ENABLED=0 uvicorn justls.ics.app.main:app --reload
```

Disable both UI exposures:

```bash
JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED=0 JUSTLS_UI_V6_ENABLED=0 uvicorn justls.ics.app.main:app --reload
```

## What to check manually

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/ui`
- `http://127.0.0.1:8000/ui/v6`
- `http://127.0.0.1:8000/api/v1/status/full`

Expected default behavior:

- `/` advertises `/ui` and `/ui/v6`;
- `/ui` loads the stable UI path;
- `/ui/v6` loads the review shell;
- `/api/v1/status/full` includes `operational_status`;
- `/` includes `ui_safety_switches` showing both UI switches enabled.

Expected behavior with `JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED=0`:

- `/ui` does not include `phase2d6_operational_status.js`;
- `/ui/v6` still works unless separately disabled.

Expected behavior with `JUSTLS_UI_V6_ENABLED=0`:

- `/` reports `ui_v6: null`;
- `/ui/v6` returns 404.

## Code-level rollback

If Phase 2.6 needs to be reverted from remote `main`, revert the two squash merge commits in reverse order.

Current Phase 2.6 commits:

```text
ea22d7e6e620e05a4688e95a5d62f1045b93d457  Phase 2.6 follow-up: add UI safety switches
5b90aa7591327fdaf645f6526e6391f84bd5bba3  Phase 2.6: operational status and UI v6 shell
```

Revert commands:

```bash
git revert ea22d7e6e620e05a4688e95a5d62f1045b93d457
git revert 5b90aa7591327fdaf645f6526e6391f84bd5bba3
```

If your local `main` has not pulled the remote Phase 2.6 commits, your local copy is still a pre-Phase-2.6 fallback. Do not pull until you are ready to validate the remote changes locally.

## Known limitations

- `/ui/v6` is a review shell, not the default UI.
- UI v6 does not implement real guide/alignment tooling.
- UI v6 does not implement a data watcher or quicklook pipeline.
- UI v6 does not implement authentication or role authorization.
- Observation Plan / Sequence Runner remains deferred.
- Engineering panels are placeholders, not real device recovery controls.

## Current recommendation

Keep `/ui` as the stable default route.

Use `/ui/v6` for review only.

Do not promote v6 to `/ui` until a later explicit decision.
