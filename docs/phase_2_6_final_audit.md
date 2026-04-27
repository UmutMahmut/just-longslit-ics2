# Phase 2.6 final audit

This document records the final Phase 2.6 audit conclusion after the merged Phase 2.6 backend/UI work, safety-switch follow-up, documentation closeout, and local manual validation.

## Audit date and scope

Phase audited: **Phase 2.6: GUI and runtime operational maturity**

Audited scope:

- backend `operational_status` in `/api/v1/status/full`;
- `/ui` stable entrypoint behavior;
- `/ui/v6` review-shell behavior;
- Phase 2.6 frontend runtimes;
- UI safety switches;
- documentation and rollback posture;
- local smoke-test and test-suite result.

Out of scope:

- final GUI productization;
- Observation Plan / Sequence Runner;
- real hardware integration;
- data watcher / quicklook pipeline;
- guide/alignment tooling;
- engineering recovery panels;
- authentication / authorization.

## Current merged Phase 2.6 commits

Remote `main` currently includes the following Phase 2.6 commits:

```text
5b90aa7591327fdaf645f6526e6391f84bd5bba3  Phase 2.6: operational status and UI v6 shell
ea22d7e6e620e05a4688e95a5d62f1045b93d457  Phase 2.6 follow-up: add UI safety switches
fa4040fd709e7861cfb665e9d4a280ad398c5b4e  Phase 2.6: add A3/A4 documentation
```

## Local validation result

Manual validation was performed from an updated local checkout of remote `main`.

The following endpoints were manually opened successfully:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/api/v1/status/full`
- `http://127.0.0.1:8000/ui`
- `http://127.0.0.1:8000/ui/v6`

The test suite passed under a Python 3.11 environment:

```text
109 passed in 0.91s
```

A Python version issue was observed under an older environment because the codebase uses `@dataclass(slots=True)`, which requires Python 3.10 or newer. This is an environment/documentation issue, not a Phase 2.6 logic failure.

## Audit checklist

### 1. `/api/v1/status/full` schema consistency

Status: **pass**

`/api/v1/status/full` now includes `operational_status`, and the response schema has been aligned with the actual response body.

The `operational_status` block is a derived GUI-facing status summary. It does not replace the backend state machine.

### 2. `/ui` remains stable default entrypoint

Status: **pass with caution**

`/ui` remains the default stable UI route.

By default, the Phase 2.6 operational-status adapter is injected into `/ui`, allowing the existing v5 UI to consume `operational_status`.

A safety switch exists to disable this injection:

```bash
JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED=0
```

This preserves a soft rollback path if adapter behavior is disruptive.

### 3. `/ui/v6` remains review shell

Status: **pass**

`/ui/v6` is available and loads successfully.

It is explicitly a review shell, not the default UI. It contains the Phase 2.6 concepts:

- observer state summary;
- command status;
- latest-job alignment;
- `X-Request-ID` visibility;
- observer / engineering / diagnostics separation;
- high-impact configuration gating markers.

It should not be promoted to `/ui` yet.

### 4. UI safety switches

Status: **pass**

Two environment-level UI safety switches are available:

```bash
JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED=0
JUSTLS_UI_V6_ENABLED=0
```

The first disables adapter injection into `/ui`.

The second hides `/ui/v6` and makes it return 404.

These switches control UI exposure only; they do not remove backend `operational_status`.

### 5. A2 expansion stopped

Status: **pass**

A2 is frozen except for bug fixes.

No more new command types, hardware controls, frontend runtime layers, Observation Plan behavior, data watcher behavior, or guide/alignment tooling should be added under Phase 2.6-A2.

### 6. Remaining MODS/BFOSC-inspired items deferred correctly

Status: **pass**

The following are intentionally deferred:

- preset-as-operation hardening: Phase 2.7;
- acquisition / science / calibration / procedure classification: Phase 2.7 foundation and Phase 4 completion;
- Observation Plan / Sequence Runner: Phase 4;
- data watcher / quicklook agent: Phase 3;
- alignment / guide workspace: Phase 3;
- real engineering panels: later hardware-integration work;
- authentication / role authorization: later security/operations work.

## Important product/UI finding

Phase 2.6 should be considered successful as an operational-maturity foundation, but **not** as final GUI productization.

The local user experience review found that `/ui/v6` is technically healthy but less usable than the original `/ui` for normal operation.

This is expected because `/ui/v6` was built as a review shell for operational status concepts, not as a complete replacement for the existing operator UI.

Conclusion:

```text
Do not promote /ui/v6 to the default /ui route.
```

The correct future UI strategy is:

```text
Keep /ui as stable default.
Keep /ui/v6 as review shell.
Carry the useful Phase 2.6 mechanisms into future UI productization.
```

## Known issues and follow-up items

### README local setup instructions are outdated

The current repository does not provide `setup.py` or `pyproject.toml`, so `pip install -e .` is not valid.

Current practical local startup requires `PYTHONPATH=src`, for example on PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m uvicorn justls.ics.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Testing similarly requires:

```powershell
$env:PYTHONPATH="src"
pytest -q
```

A follow-up documentation or packaging cleanup should address this.

### Python version requirement should be documented

The codebase uses `@dataclass(slots=True)`, so Python 3.10 or newer is required.

Recommended environment for current validation: Python 3.11.

### `/ui/v6` is not production-grade UI

`/ui/v6` should remain review-only until a later UI productization phase.

It lacks the full usability and workflow maturity of the existing `/ui`.

## Rollback posture

Soft rollback options:

```bash
JUSTLS_UI_PHASE2D6_ADAPTER_ENABLED=0
JUSTLS_UI_V6_ENABLED=0
```

Code-level rollback, in reverse order:

```bash
git revert fa4040fd709e7861cfb665e9d4a280ad398c5b4e
git revert ea22d7e6e620e05a4688e95a5d62f1045b93d457
git revert 5b90aa7591327fdaf645f6526e6391f84bd5bba3
```

## Final conclusion

Phase 2.6 is ready to close.

It achieved the intended engineering goal:

```text
GUI and runtime operational maturity foundation established.
```

It should not claim:

```text
Final GUI productization complete.
```

The next recommended phase is:

```text
Phase 2.7: Preset operational hardening
```

Phase 2.7 should focus on turning presets from configuration shortcuts into auditable operations:

- preset categories;
- preset diff before apply;
- dangerous preset confirmation;
- structured apply result;
- integration with job result / observation metadata;
- foundation for future Observation Plan / Sequence Runner.
