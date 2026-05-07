# Phase 2.8-H H8 runtime compatibility and v5 parity review

## Purpose

This document records the post-merge H8 check after the v7.1 static shell was merged to `main`.

H8 is not a feature-expansion batch. Its purpose is to verify that the existing v7 runtime modules still target the new v7.1 durable DOM skeleton correctly, and to re-check v5 capability parity against the new Setup / Instrument / Observe / Presets / Diagnostics / Housekeeping / Engineer information architecture.

---

## Current baseline

```text
/ui      -> v5 stable default capability baseline
/ui/v6   -> v6 operational-status review shell
/ui/v7   -> v7.1 operator-console prototype, static by default
```

v7.1 current IA:

```text
Setup
Instrument / Configure
Observe
Presets
Diagnostics
Housekeeping
Engineer
```

Current runtime assets:

```text
src/justls/ics/app/ui/v7/runtime_status.js
src/justls/ics/app/ui/v7/preset_runtime.js
src/justls/ics/app/ui/v7/observe_runtime.js
src/justls/ics/app/ui/v7/observe_guard.js
```

Runtime remains opt-in:

```text
JUSTLS_UI_V7_RUNTIME_ENABLED=1
JUSTLS_UI_V7_RUNTIME_STATUS_ENABLED=1
JUSTLS_UI_V7_PRESET_RUNTIME_ENABLED=1
JUSTLS_UI_V7_OBSERVE_RUNTIME_ENABLED=1
JUSTLS_UI_V7_OBSERVE_GUARD_ENABLED=1
```

---

## H8 runtime compatibility result

### H8.1 default static shell

Status: **PASS / KEEP ENFORCING**

```text
- /ui/v7 remains available as a static shell.
- v7 runtime scripts are not injected by default.
- Instrument / Configure is present in static HTML.
- Durable skeleton IDs remain unique.
```

Relevant durable IDs:

```text
#run-mode
#operational-level
#exposure-state
#local-time
#v7-runtime-status
#v7-raw-status-preview
#v7-setup-readiness
#v7-observe-controls
#v7-presets-runtime
```

### H8.2 runtime gate matrix

Status: **PASS / TESTED BY STATIC ROUTE ASSERTIONS**

Expected behavior:

```text
Default:
  no v7 runtime scripts injected

Master gate only:
  runtime_status.js injected
  preset_runtime.js not injected
  observe_runtime.js not injected
  observe_guard.js not injected

Master + presets + observe + guard:
  runtime_status.js injected first
  preset_runtime.js injected second
  observe_runtime.js injected third
  observe_guard.js injected fourth

Master + status disabled:
  no status runtime script injected
```

### H8.3 runtime_status.js compatibility

Status: **PASS / COMPATIBLE WITH v7.1 SKELETON**

Current responsibilities:

```text
- Poll /api/v1/status/full.
- Bind top status cards.
- Bind Setup Readiness.
- Bind Diagnostics runtime status and raw status preview.
- Bind Instrument / Configure summary and B/G/R placeholders when fields exist in the payload.
- Bind the v7 message rail text.
- Preserve fallback panel behavior only for missing skeletons.
```

Current limitation:

```text
- Request ID is not yet captured from response headers into Diagnostics.
- Connection freshness is not yet equivalent to v5; v5 shows RTT, last OK, polling, and stale threshold.
- Some Instrument fields are bound opportunistically because the backend status payload does not yet expose all final JUST hardware contracts.
```

Decision:

```text
Compatible for H8.
Needs H2/H3 follow-up for operator feedback rail, request_id, freshness, and command-result presentation.
```

### H8.4 preset_runtime.js compatibility

Status: **PASS / COMPATIBLE WITH v7.1 SKELETON**

Current responsibilities:

```text
- Enhance #v7-presets-runtime if present.
- Load catalog from /api/v1/presets.
- Preview preset through /api/v1/presets/preview.
- Apply previewed preset through /api/v1/presets/apply.
- Keep singleton runtime state.
- Guard in-flight catalog, preview, and apply operations.
- Use fallback skeleton only if #v7-presets-runtime is missing.
```

Current limitation:

```text
- Preview result is still raw JSON, not an operator-facing diff table.
- Apply success does not yet broadcast a shared v7 refresh event for status/instrument/observe context.
```

Decision:

```text
Compatible for H8.
Needs H5 follow-up for operator-facing diff tables and better affected-subsystem/risk display.
```

### H8.5 observe_runtime.js compatibility

Status: **PASS / COMPATIBLE WITH v7.1 SKELETON**

Current responsibilities:

```text
- Enhance #v7-observe-controls if present.
- Bind exposure time, frame type, operator note, abort confirmation, command buttons, state, armed exposure, last command, runtime state, and result output.
- Call /api/v1/observation/status.
- Call /api/v1/observation/arm.
- Call /api/v1/observation/start.
- Call /api/v1/observation/stop_readout.
- Call /api/v1/observation/abort_discard.
- Dispatch justls:v7-observe-state after status updates.
```

Current limitation:

```text
- Finish exposure is available in v5's capability surface but is not currently exposed in v7.1 Observe.
- Command result remains raw JSON.
- Request ID / latest_job / error summary are not yet rendered in a structured operator-facing form.
```

Decision:

```text
Compatible for H8.
Needs H3 follow-up before v7 can claim full v5 observation-control parity.
```

### H8.6 observe_guard.js compatibility

Status: **PASS / COMPATIBLE WITH v7.1 SKELETON**

Current responsibilities:

```text
- Enhance #v7-observe-controls.
- Use current observation state and armed-exposure labels to determine frontend button availability.
- Require explicit checkbox confirmation for Abort & Discard.
- Listen to justls:v7-observe-state events.
- Keep a narrow MutationObserver fallback on the observe-controls skeleton only.
```

Current limitation:

```text
- Guard logic is frontend-only and heuristic.
- Final enable/disable behavior should eventually align with backend state-machine contracts rather than label parsing.
```

Decision:

```text
Compatible for H8.
Do not fold observe_guard.js into observe_runtime.js yet; defer that decision until H3 interaction polish.
```

---

## v5 to v7.1 parity review

### Capability groups now covered or structurally placed

```text
P0 route/runtime safety
  Covered. /ui remains v5, /ui/v7 remains separate and static by default.

P1 top-level status
  Partially covered. v7.1 has top cards and runtime_status.js binds them.

P2 observation lifecycle
  Partially covered. v7.1 supports single-exposure Arm / Start / Stop & Readout / Abort & Discard through opt-in observe runtime.

P3 slit/calibration/detector visibility
  Structurally placed. v7.1 has Instrument / Configure with Slit, Calibration, Detector, B/G/R Channel Panels, and Safety Boundary.

P4 presets
  Covered at runtime skeleton level. Catalog / Preview / Guarded Apply remain available through opt-in preset runtime.

P5 diagnostics/raw status
  Partially covered. Diagnostics owns raw status preview and troubleshooting context.

P6 live/latest exposure preview
  Structurally covered. Latest Exposure Preview and B/G/R placeholders remain first-class in Observe.
```

### v5 capabilities not yet fully matched by v7.1

```text
1. Global timing richness
   v5 shows Local / UTC / LST / DATE / JD/MJD / runtime mode.
   v7.1 currently shows Local Time plus high-level run/operational/exposure cards.
   Decision: nice-to-have before default switch; likely important before real night operations.

2. Connection freshness richness
   v5 shows API base, RTT, last OK, polling, and stale threshold.
   v7.1 currently has a message rail and status runtime count but not full freshness parity.
   Decision: H2 follow-up.

3. Message rail severity parity
   v5 message rail has info/success/warning/error level semantics.
   v7.1 message rail is present and bindable but does not yet use equivalent severity state.
   Decision: H2 follow-up.

4. Observation Finish command
   v5 capability surface includes Finish in the observation lifecycle.
   v7.1 currently exposes Arm / Start / Stop & Readout / Abort & Discard, but not Finish.
   Decision: H3 follow-up; verify backend semantics before adding to v7 Observe.

5. Structured command-result presentation
   v5 and v7 both can surface raw/debug output, but v7.1 still needs a better operator-facing command outcome model.
   Decision: H3 follow-up.

6. Preset preview UX
   v7.1 can preview/apply presets, but preview remains raw JSON.
   Decision: H5 follow-up for diff/risk/affected-subsystem display.

7. Cameras / Guider / Quicklook pages
   v5 has first-class Cameras, Guider, and Quicklook pages, marked demo/future/not-wired.
   v7.1 preserves latest exposure preview and B/G/R placeholders, but does not have separate Cameras/Guider/Quicklook pages.
   Decision: acceptable for now if placeholders remain honest; detailed image backend / quicklook / data watcher remain deferred backend contracts.

8. Day/night theme
   v5 supports persisted day/night theme selection.
   v7.1 currently uses a fixed console visual style.
   Decision: nice-to-have before default switch; likely required before real observing operations.
```

### v5 capabilities intentionally reorganized in v7.1

```text
Instrument
  v5 Instrument page maps to v7.1 Instrument / Configure.

Observation
  v5 Observation and overview quick actions map to v7.1 Observe.

Presets
  v5 Presets maps to v7.1 Presets.

Diagnostics
  v5 Diagnostics maps to v7.1 Diagnostics.

Cameras / Guider / Quicklook
  v5 first-class pages are not copied directly. v7.1 keeps latest exposure preview, B/G/R placeholders, and Diagnostics image-feed placeholder while deferring real image/backend contracts.
```

---

## H8 conclusion

```text
H8 runtime compatibility: PASS at route/static-selector level.
Existing v7 runtime modules still target the v7.1 durable skeletons.
No new backend API is required by the H8 compatibility check.
No runtime module needs to be rewritten immediately.
```

v7.1 is now structurally healthier than the earlier v7 shell, but it is not yet ready to replace `/ui` as the default operator UI. The remaining high-priority gaps are not IA placement gaps; they are operator-feedback and workflow-polish gaps.

Recommended next sequence:

```text
H2: v7 operator feedback rail parity
H3: v7 Observe command-result presentation and Finish-command decision
H5: Presets preview UX polish
N1: night/day theme strategy
```
