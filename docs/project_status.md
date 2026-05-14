# Project status

## Purpose

This is the durable project-status document for JUST Long-Slit ICS 2.0. It replaces the previous collection of phase-specific audit notes in `docs/`.

Keep this document focused on current direction, phase boundaries, completed milestones, open decisions, and close criteria. Do not use it as a scratchpad for every temporary idea.

Durable hardware, P0, v5 baseline, and operator-console requirements are maintained in `docs/operator_console_requirements.md`.

---

## Project goal

JUST Long-Slit ICS 2.0 is the control-system backbone for the JUST Telescope long-slit spectrograph. It is not merely a web UI project.

The system is being developed around:

```text
- simulation-first backend development;
- clear API/domain/kernel/application boundaries;
- operator-safe control surfaces;
- explicit diagnostics and request tracing;
- staged migration from the v5 capability baseline to the v7.1 operator console;
- later real-hardware integration through adapter/gateway boundaries.
```

---

## Current phase

```text
Current completed work:
  Phase 2.8-I: light operator command-feedback unification
  Phase 2.8-J: v7 default route switch

Status:
  Implemented in PR #10 and locally validated.

Latest validation reported by user:
  pytest -q
  161 passed in 1.00s
```

Current UI route strategy after Phase 2.8-J:

```text
/ui        -> v7.1 default operator-console prototype
/ui/v7     -> v7.1 explicit operator-console prototype
/ui/v5     -> v5 stable legacy fallback
/ui/legacy -> v5 stable legacy fallback alias
/ui/v6     -> v6 operational-status review shell
```

Important wording:

```text
v7.1 is now the default operator-console prototype.
This route switch does not mean v7.1 is a final product-grade GUI.
```

Runtime policy is unchanged:

```text
- v7 runtime remains opt-in through JUSTLS_UI_V7_RUNTIME_ENABLED=1.
- Status runtime is still the safest first runtime module when the master gate is enabled.
- Instrument / Presets / Observe / Guard runtime modules remain individually gated.
- Backend API semantics are unchanged by the route switch.
```

---

## Completed milestone summary

### Phase 2.6: GUI and runtime operational maturity foundation

Closed.

Key durable outcomes:

```text
- /api/v1/status/full gained GUI-facing operational status.
- /ui remained the stable default entrypoint at that time.
- /ui/v6 was added as a review shell, not a default UI.
- UI safety switches were added for v5 adapter and v6 route exposure.
- X-Request-ID / latest-job / status-summary thinking entered the UI direction.
```

### Phase 2.7: Preset operational hardening

Closed.

Key durable outcomes:

```text
- presets gained category / risk_level / requires_confirmation metadata;
- side-effect-free preset preview endpoint exists;
- high-impact/engineering presets require confirmation at the API boundary;
- apply result became structured and auditable;
- successful preset apply produces latest-job audit linkage;
- observation arm can attach the latest successful preset-apply summary.
```

Durable lesson:

```text
Presets are auditable operations and future workflow building blocks, not just configuration shortcuts.
```

### Phase 2.8-G: v7 runtime architecture stabilization

Closed.

Key durable outcomes:

```text
- v7 runtime master gate added;
- v7 module-level runtime gates added;
- /ui/v7 remains static by default when runtime is disabled;
- runtime_status.js, preset_runtime.js, observe_runtime.js, and observe_guard.js became singleton-safe/skeleton-aware;
- Presets and Observe each use one durable runtime-enhanceable skeleton;
- runtime JS enhances durable HTML instead of creating duplicate panels by default.
```

Durable rule:

```text
HTML owns durable structure. Runtime JS enhances it.
```

### Phase 2.8-H: v5 to v7 feature parity pass

Functionally closed.

Completed H work:

```text
H7: v7.1 Instrument / Configure static shell
  DONE

H8: v7.1 runtime compatibility check
  DONE

H2: v7 operator feedback rail baseline
  DONE

H3: Observe Finish + structured-result baseline
  DONE / baseline only

H9: Instrument API alignment baseline
  DONE / baseline only

H9.1: Instrument panel layout and slit dual-unit correction
  DONE

H9.2: served-shell alignment check
  DONE
```

Phase 2.8-H durable outcomes:

```text
- v7.1 IA has Setup / Instrument / Observe / Presets / Diagnostics / Housekeeping / Engineer.
- Existing runtime modules remain opt-in and skeleton-aware.
- H2 feedback rail baseline exists.
- H3 Observe lifecycle baseline exists.
- H9 Instrument API visibility/control baseline exists for routine slit/calibration plus detector read-only visibility.
- P0/v5 slit-width unit contract is preserved in code and tests.
- Docs are consolidated into project_status.md and operator_console_requirements.md.
```

### Phase 2.8-I: light command-feedback unification

Implemented and locally validated.

Goal:

```text
Make Instrument, Observe, Presets, Feedback rail, and Diagnostics speak the same command-feedback vocabulary:

last_command
request_id
latest_job
last_error
result_summary
raw_json
```

Scope:

```text
- keep Setup -> Presets -> Instrument -> Observe -> Diagnostics as the operator flow;
- add served-shell bindings for unified command summaries;
- keep raw JSON available, but make Diagnostics the deeper troubleshooting home;
- keep endpoint semantics unchanged;
- avoid new backend API requirements.
```

Non-goals:

```text
- no OCS protocol implementation;
- no TCS sync implementation;
- no sequence runner;
- no detector config write UI;
- no full B/G/R hardware control;
- no real hardware integration.
```

### Phase 2.8-J: v7 default route switch

Implemented and locally validated.

Goal:

```text
Make /ui serve the v7.1 operator-console prototype by default while preserving v5 as explicit fallback.
```

Required invariants:

```text
- /ui and /ui/v7 serve the same v7.1 shell.
- /ui/v5 and /ui/legacy preserve the v5 stable fallback.
- /api/v1/* behavior is unchanged.
- v7 runtime remains disabled by default unless explicitly enabled by environment variables.
- This is a default-entrypoint decision, not a production GUI acceptance claim.
```

---

## Technology adoption gate

New infrastructure, protocol, database, event-streaming, hardware-bus, external platform, or observatory-integration technology must not be promoted into the main roadmap merely because it is powerful or familiar.

Before adoption, it must answer:

```text
1. What current project problem does it solve?
2. Is that problem present in the current phase?
3. Is there real hardware, real operations, or a real interface contract behind it?
4. Can a simpler schema, simulator, file contract, or adapter boundary solve it for now?
5. Does it preserve Domain / Kernel / Application / Adapter boundaries?
6. Does it avoid exposing low-level engineering complexity in routine operator UI?
7. Can it be tested through pytest or integration tests?
8. If we do not adopt it now, can the current phase still move forward cleanly?
```

If these questions are not answerable, the item remains `TBD`, `candidate`, or `adapter-bounded`, not a named implementation route.

---

## Phase 2.9+ deferred backend contracts

Deferred until after 2.8-I/J clarify the operator surface:

```text
- durable setup/session metadata API;
- OCS request/response/lifecycle contract;
- TCS read-only status/readiness contract;
- image feed / latest exposure backend / quicklook / data watcher;
- sequence runner / observing plan model;
- persistent observation log / audit trail;
- role separation / authentication / permission boundaries;
- final FITS/data-product metadata contract;
- full B/G/R channel hardware-control contract;
- slit-monitor camera / guider / slit-width measurement contract;
- derotator / instrument-rotation control contract;
- real hardware adapter validation;
- hardware communication protocol validation after hardware selection.
```

---

## Route and runtime invariants

These must remain true unless explicitly changed by a major decision:

```text
- /ui is the v7.1 default operator-console prototype.
- /ui/v5 and /ui/legacy remain v5 fallback routes.
- /ui/v7 remains static and clickable by default.
- v7 runtime is opt-in through JUSTLS_UI_V7_RUNTIME_ENABLED=1.
- v7 module-level runtime gates remain opt-in or master-gated.
- runtime JS must enhance durable skeletons and avoid duplicate competing panels.
- routine pages show command summaries first.
- raw JSON belongs in page detail areas and Diagnostics, not as the dominant main flow.
- unsafe engineering actions belong in Engineer/Housekeeping/Diagnostics, not routine operator flow.
- bottom-layer hardware protocols remain hardware-selection-driven and adapter-bounded.
```

---

## Documentation policy

`docs/` should remain small and durable.

Current durable docs:

```text
docs/ics2_software_development_strategy.md
docs/project_status.md
docs/operator_console_requirements.md
```

Avoid reintroducing one-off phase notes. If a decision remains useful, fold it into one of these files.
