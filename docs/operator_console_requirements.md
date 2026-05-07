# Operator console requirements

## Purpose

This is the durable operator-console requirements document for v7.1 and later. It replaces detailed phase-specific parity notes and temporary design memos.

Keep this document focused on requirements, capability visibility, hardware constraints, and long-lived UI responsibility boundaries.

---

## Core principle

Backend capability must be visible in the frontend.

```text
Backend capability must be visible.
Operator-safe capability may be controllable.
Engineering / unsafe / incomplete capability must be visible but gated, deferred, or moved to Diagnostics / Engineer.
```

The frontend must not silently drop an existing backend capability. It also must not pretend that a placeholder is real hardware telemetry.

---

## Reference sources and how to use them

### ICS 2.0 repository

This repository is the implementation source of truth. Current code determines what is actually available.

### ICS 1.0 repository

The earlier `just-longslit-ics` repository is a legacy intent source. It is outdated as implementation, but it preserves important early ideas:

```text
- API-first control under /api/v1;
- SimHAL/simulator-backed end-to-end operation;
- backend-served static UI for zero-CORS integration;
- status/full and capabilities map;
- slit width, slit angle, and lamp as a minimal closed-loop demo;
- SlitCam and B/G/R preview placeholders;
- latest.jpg fallback when camera APIs are not implemented;
- demo_flow.ps1 as a reproducible operator/developer smoke flow.
```

Use ICS 1.0 as a checklist for not losing original product intent. Do not copy it as architecture.

### MODS/BFOSC references

Use mature spectrograph-control software as responsibility and workflow references, not as hardware copies.

MODS supports these architectural lessons:

```text
- Setup is not a catch-all hardware-control page.
- Routine slit/calibration/instrument configuration belongs in an operator-facing dashboard/configuration area.
- Housekeeping and utilities/engineering areas are separated from routine observer actions.
- Raw/debug/engineering controls should not dominate the observing flow.
```

JUST-specific correction:

```text
JUST is a B/G/R three-channel spectrograph, not a MODS Blue/Red two-channel instrument.
```

---

## v7.1 information architecture

Current v7.1 target structure:

```text
Setup
Instrument / Configure
Observe
Presets
Diagnostics
Housekeeping
Engineer
```

Responsibilities:

```text
Setup
  Observer/project/session/file/data context. Local placeholders until durable backend contracts exist.

Instrument / Configure
  Routine operator configuration and visibility for slit, calibration, detector profile, and B/G/R channel summary.

Observe
  Single-exposure execution and latest exposure preview. Do not turn this into a sequence runner in Phase 2.8-H.

Presets
  Catalog, preview, confirmation, and guarded apply. Operator-facing diff polish belongs to Phase 2.8-I.

Diagnostics
  Raw JSON, request-id, latest-job, last-error, runtime status, and deeper troubleshooting.

Housekeeping
  Subsystem health, environmental/power summaries, and support-operator views.

Engineer
  Low-level hardware/maintenance/unsafe controls, role-gated later.
```

---

## Capability classification

Each backend or legacy-intent capability should be classified as one of:

```text
VISIBLE_STATUS
  The UI shows the capability and its status, but does not offer direct control.

VISIBLE_PLACEHOLDER
  The UI reserves the capability's location and labels it clearly as not wired, future, demo, or backend-contract deferred.

OPERATOR_CONTROL
  The UI provides direct operator control with request-id/error feedback and appropriate guards.

ENGINEER_ONLY
  The capability is visible only in Diagnostics, Housekeeping, or Engineer areas.

DEFERRED_BACKEND_CONTRACT
  The capability needs a backend/API/data/hardware contract before honest frontend work.

NOT_CARRIED_FORWARD
  The capability is intentionally retired with a recorded reason.
```

---

## Current backend/API capability visibility requirements

### System status and capabilities

Relevant current capabilities:

```text
GET /api/v1/health
GET /api/v1/status
GET /api/v1/status/full
GET /api/v1/capabilities
```

v7.1 requirements:

```text
- status/full must feed top cards, Diagnostics, Instrument summary, and feedback rail.
- health/status/capabilities should be visible in Diagnostics or Housekeeping.
- capabilities should eventually inform which controls are enabled, hidden, or marked not available.
```

### Slit

Relevant current capabilities:

```text
POST /api/v1/slit
POST /api/v1/slit_angle
```

v7.1 requirements:

```text
- Slit width and slit angle must be visible in Instrument / Configure.
- Since backend APIs already exist, minimal v7.1 direct operator controls are a Phase 2.8-H candidate.
- Controls must show request_id and errors.
- Controls must respect backend safety responses; frontend guards are advisory only.
```

### Calibration and lamps

Relevant current capabilities:

```text
POST /api/v1/lamp               legacy lamp on/off
GET  /api/v1/calibration/status
POST /api/v1/calibration/mode
POST /api/v1/calibration/lamp
```

v7.1 requirements:

```text
- Calibration mode and lamp state must be visible in Instrument / Configure.
- Prefer the newer calibration endpoints over the legacy /api/v1/lamp path for v7.1 operator controls.
- Minimal calibration mode and lamp select/enable controls are a Phase 2.8-H candidate.
- Unsafe/low-level lamp or power behavior belongs outside the routine operator flow.
```

### Detector and B/G/R channels

Relevant current capabilities:

```text
GET  /api/v1/detector/config
POST /api/v1/detector/config
```

v7.1 requirements:

```text
- Detector profile/config and B/G/R channel summaries must be visible in Instrument / Configure.
- Read-only detector config visibility is suitable for Phase 2.8-H.
- Direct detector config write control requires caution and may be deferred.
- Full B/G/R hardware-control contracts are later backend/hardware work.
```

### Observation

Relevant current capabilities:

```text
GET  /api/v1/observation/status
POST /api/v1/observation/arm
POST /api/v1/observation/start
POST /api/v1/observation/finish
POST /api/v1/observation/stop_readout
POST /api/v1/observation/abort_discard
```

v7.1 requirements:

```text
- Observe must cover the single-exposure lifecycle.
- Arm / Start / Finish / Stop & Readout / Abort & Discard belong in Observe.
- Abort/discard needs explicit confirmation.
- Request ID, latest job, last error, and state transition feedback must be visible.
- Deeper workflow polish belongs to Phase 2.8-I.
```

### Presets

Relevant current capabilities:

```text
GET  /api/v1/presets
POST /api/v1/presets/preview
POST /api/v1/presets/apply
```

v7.1 requirements:

```text
- Preset catalog, preview, and guarded apply must remain available.
- Confirmation-required and high-risk semantics must not be bypassed.
- Raw JSON preview is acceptable for Phase 2.8-H parity baseline.
- Operator-facing diff/risk/affected-subsystem presentation belongs to Phase 2.8-I.
```

---

## Live image and preview requirement

The live/latest exposure preview is a first-class operator-console requirement.

Minimum v7.1 requirement:

```text
- Preserve a visible Latest Exposure Preview region in Observe.
- Preserve B/G/R preview placeholders.
- Preserve explicit LIVE / DEMO / NOT WIRED or equivalent honesty labels.
- Keep image feed diagnostics in Diagnostics.
```

Deferred backend contracts:

```text
- latest exposure image endpoint;
- detector preview endpoint;
- quicklook/data watcher;
- slit-monitor/guider image feed;
- frame freshness and last-frame metadata.
```

---

## JUST hardware constraints

The v7 operator console must respect these design constraints:

```text
- JUST long-slit spectrograph is B/G/R three-channel, not Blue/Red.
- Nominal design context:
    B: 365-573 nm
    G: 546-772 nm
    R: 747-985 nm
- Long-slit direction field requirement is >= 10 arcmin.
- Multiple slit widths are required, approximately 0.5 arcsec to 5 arcsec.
- Calibration includes flat-field and wavelength calibration.
- Calibration sources include flat-field source and lamps such as Hg(Ar), Ne, and possible ThAr/FeAr-style sources.
- Slit monitoring camera is part of the instrument concept.
- Future control scope includes slit drive, B/G/R camera focus/exposure/readout, slit-monitor readout, slit-width measurement, fast photometry channel, calibration lamp switching, and derotation.
- EtherCAT distributed control is part of the electrical/control design direction.
```

Do not introduce UI copy or code assumptions that contradict these facts.

---

## Current H9 candidate

H9 should be considered only after backend/API visibility alignment is accepted.

Recommended minimal H9 scope:

```text
H9: minimal v7 Instrument runtime for existing slit/calibration APIs

Add or expose controls for:
  - slit width;
  - slit angle;
  - calibration/science mode;
  - flat / arc_hgar / arc_ne lamp enable state;
  - calibration status refresh;
  - detector config read-only visibility if practical.
```

Non-goals for H9:

```text
- no EtherCAT node controls;
- no power management controls;
- no unsafe maintenance actions;
- no full B/G/R hardware control;
- no sequence runner;
- no Presets diff UX polish;
- no night/day theme work.
```

---

## Documentation policy

Do not add one-off phase notes for each small batch. Durable requirements belong here. Current phase state belongs in `project_status.md`. Temporary analysis may stay local or in conversation history rather than becoming permanent repository files.
