# Phase 2.8-H H3 Observe command-result presentation

## Purpose

This note records the H3 baseline work for v7.1 Observe command-result presentation.

H3 focuses on the existing single-exposure observation workflow. It does not introduce a sequence runner, observing-plan model, quicklook backend, or new hardware API. It improves parity with the v5 observation lifecycle by exposing the existing backend `finish` command and by adding structured command-result binding points for request and error troubleshooting.

---

## Current Phase 2.8-H status

```text
H7 v7.1 Instrument / Configure static shell
  DONE / MERGED / locally validated

H8 v7.1 runtime compatibility check
  DONE / selector-level runtime compatibility validated

H2 v7 operator feedback rail parity
  DONE / baseline feedback rail telemetry and served static rail fields validated

H3 v7 Observe command-result presentation
  IN PROGRESS / first baseline implemented

N1 night/day theme strategy
  DEFERRED by current project decision
```

Current latest user-reported validation before H3 baseline:

```text
pytest -q
156 passed in 0.97s
```

---

## H3 baseline changes

### Served `/ui/v7` Observe shell

The served v7.1 Observe shell now exposes:

```text
data-action="obs-finish"
data-bind="v7.observe.request_id"
data-bind="v7.observe.latest_job"
data-bind="v7.observe.last_error"
```

This is currently applied through the same served-shell expansion mechanism used for H2 feedback rail fields. The static HTML file can be consolidated later, but the `/ui/v7` route now exposes the durable H3 binding points.

### `observe_runtime.js`

The v7 observe runtime now includes:

```text
FINISH_ENDPOINT = "/api/v1/observation/finish"
```

and binds:

```text
Arm              -> /api/v1/observation/arm
Start            -> /api/v1/observation/start
Finish           -> /api/v1/observation/finish
Stop & Readout   -> /api/v1/observation/stop_readout
Abort & Discard  -> /api/v1/observation/abort_discard
```

It also records and renders:

```text
lastRequestId
v7.observe.request_id
v7.observe.latest_job
v7.observe.last_error
```

Command result output remains JSON-backed for now, but it now includes the command name and request identifier explicitly:

```text
{
  "command": "finish",
  "request_id": "...",
  "payload": {...}
}
```

### `observe_guard.js`

The frontend guard now recognizes:

```text
obs-finish
```

Current heuristic:

```text
Finish is enabled when the current observation state appears active/running/integrating.
```

This remains frontend-only guard logic. Backend state-machine validity remains authoritative.

---

## Test coverage

`tests/ui/test_v7_runtime_compatibility.py` now checks:

```text
- served /ui/v7 exposes obs-finish
- served /ui/v7 exposes request_id/latest_job/last_error binding points
- observe_runtime.js includes FINISH_ENDPOINT
- observe_runtime.js targets /api/v1/observation/finish
- observe_runtime.js includes requestIdFrom and structured result binding strings
- observe_guard.js includes obs-finish
```

---

## H3 current limitations

```text
- Latest Job depends on payload shape; observation status payloads may not always include latest_job.
- Command result is still partly raw JSON, though it now has a clearer wrapper.
- Guard logic is still heuristic and based on visible state labels.
- Finish enablement should be manually verified against actual backend state transitions.
- Observe result UX is not yet a full operator-facing summary table.
```

---

## Manual verification checklist

Default static shell:

```powershell
Remove-Item Env:JUSTLS_UI_V7_RUNTIME_ENABLED -ErrorAction SilentlyContinue
python -m uvicorn justls.ics.app.main:app --app-dir src --reload
```

Open:

```text
http://127.0.0.1:8000/ui/v7
```

Expected:

```text
- Observe panel shows Arm / Start / Finish / Stop & Readout / Abort & Discard.
- Observe panel shows Request ID / Latest Job / Last Error fields.
- Runtime scripts are not injected by default.
```

Observe runtime + guard:

```powershell
$env:JUSTLS_UI_V7_RUNTIME_ENABLED="1"
$env:JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED="1"
$env:JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED="1"
python -m uvicorn justls.ics.app.main:app --app-dir src --reload
```

Expected:

```text
- observe_runtime.js is injected.
- observe_guard.js is injected.
- Arm / Start / Finish / Stop & Readout / Abort & Discard remain single-exposure controls.
- Finish posts to /api/v1/observation/finish when the guard allows it.
- Request ID is populated when the backend returns X-Request-ID.
- Last Error reports command failure in a concise field.
```

---

## Next H3 polish options

Recommended follow-up before moving to H5:

```text
1. Convert Observe command output from raw JSON into a compact operator-facing summary.
2. Keep raw JSON available only as a secondary/debug detail.
3. Align button availability more closely with backend state-machine semantics.
4. Decide whether Observe should dispatch a shared v7 refresh event after commands so status/instrument/feedback rail refresh together.
```

Do not include N1 in the current version. Night/day theme strategy is deferred until after the current Phase 2.8-H workflow/parity items are stable.
