# Phase 2.8-H H2 operator feedback rail

## Purpose

This note records the H2 work on v7.1 operator feedback rail parity.

H2 focuses on global operator feedback: connection state, request freshness, request identifiers, runtime polling status, and severity-aware messages. It does not change the `/ui` default route, does not add new backend APIs, and does not restructure Observe command results; the latter belongs to H3.

---

## Current baseline

```text
/ui      -> v5 stable default capability baseline
/ui/v7   -> v7.1 static-by-default operator-console prototype
```

Current v7.1 relevant components:

```text
Top cards:
  #run-mode
  #operational-level
  #exposure-state
  #local-time

Diagnostics:
  #v7-runtime-status
  #v7-raw-status-preview

Footer rail:
  data-role="v7-message-rail"
  data-bind="v7.message.text"
  data-bind="v7.message.phase"
```

---

## H2 runtime update

`src/justls/ics/app/ui/v7/runtime_status.js` now maintains additional feedback telemetry:

```text
lastRequestId
lastRttMs
lastOkAt
connectionState
```

It also includes helper logic for:

```text
requestIdFrom(response)
rttLabel()
connectionLabel()
severityForState()
bindConnectionDiagnostics()
bindMessage(message, phase, severity)
```

Runtime fetch behavior now records:

```text
- RTT using performance.now() when available.
- X-Request-ID / x-request-id response header when present.
- last OK timestamp after successful status refresh.
- connected / degraded / error connection state.
- info / success / warning / error severity for the message rail.
```

The runtime writes these values into Diagnostics bindings when available:

```text
data-bind="v7.connection"
data-bind="v7.connection.state"
data-bind="v7.connection.rtt_ms"
data-bind="v7.connection.last_ok_at"
data-bind="v7.request_id"
data-bind="v7.last_error"
```

It also writes rail-level attributes:

```text
data-severity
data-connection
data-request-id
data-rtt-ms
```

---

## H2 test coverage

`tests/ui/test_v7_runtime_compatibility.py` now checks that `runtime_status.js` contains the H2 telemetry paths:

```text
lastRequestId
lastRttMs
lastOkAt
connectionState
requestIdFrom
X-Request-ID
x-request-id
performance.now
data-severity
data-connection
data-request-id
v7.message.severity
v7.connection.rtt_ms
v7.connection.last_ok_at
v7.request_id
```

This is a selector/static-asset compatibility test. It does not replace manual browser verification with runtime enabled.

---

## Manual runtime verification checklist

After pulling H2, verify the default static shell first:

```powershell
Remove-Item Env:JUSTLS_UI_V7_RUNTIME_ENABLED -ErrorAction SilentlyContinue
Remove-Item Env:JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED -ErrorAction SilentlyContinue
python -m uvicorn justls.ics.app.main:app --app-dir src --reload
```

Open:

```text
http://127.0.0.1:8000/ui/v7
```

Expected:

```text
- No runtime scripts are injected.
- Message rail remains static and readable.
- Instrument / Configure remains accessible.
```

Then verify status runtime:

```powershell
$env:JUSTLS_UI_V7_RUNTIME_ENABLED="1"
python -m uvicorn justls.ics.app.main:app --app-dir src --reload
```

Expected after opening `/ui/v7`:

```text
- runtime_status.js is injected.
- Top cards update from /api/v1/status/full.
- Diagnostics status panel shows connection/request/freshness details where binding points exist.
- Footer rail gets data-severity and data-connection attributes.
- data-request-id is populated when the backend returns X-Request-ID.
```

---

## Current H2 status

```text
H2 runtime telemetry baseline: DONE
H2 static footer rail display expansion: PARTIAL
```

The runtime can now compute and propagate the right feedback values. The static v7.1 footer rail still has a compact display and does not yet expose every feedback field as visible text by default.

This is acceptable as an incremental H2 baseline because:

```text
- The runtime has a durable rail target.
- Diagnostics now has the richer data path.
- No new backend API is required.
- The next visible polish can be done without touching Observe/Preset semantics.
```

Recommended next refinement, before or during H3:

```text
- Expand the static footer rail into a two-line or multi-cell operator feedback rail.
- Make severity, connection, RTT, last OK, and request ID visible without opening Diagnostics.
- Keep raw JSON and long diagnostics out of the main rail.
```

---

## Remaining v5 parity gaps after H2

```text
Still not fully matched from v5:
  - UTC / LST / DATE / JD/MJD timing richness.
  - Full v5-style connection freshness block with API base, polling, and stale threshold.
  - Full message severity styling in static CSS.
  - Observe command-result presentation with request_id/latest_job/error summary.
  - Finish-command decision in Observe.
  - Preset preview diff table.
  - Day/night theme strategy.
```

Next recommended phase step:

```text
H3: v7 Observe command-result presentation and Finish-command decision.
```
