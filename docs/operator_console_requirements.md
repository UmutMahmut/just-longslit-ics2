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

### P0 requirements PDF

`P0 PDF.pdf` is the current hard source for JUST long-slit spectrograph science, optical, calibration, slit-monitor, control-system, and OCS requirements.

Use it as a hard constraint source for:

```text
- wavelength coverage;
- B/G/R channel definitions;
- slit width range and plate scale;
- spectral resolution and dispersion requirements;
- calibration source design;
- slit-monitor camera design;
- observation flow;
- electrical/control-system scope;
- OCS functional-module expectations.
```

If UI or code assumptions conflict with P0, P0 wins unless a later project decision explicitly supersedes it.

Important interpretation rule:

```text
P0 hardware/electrical terms describe possible instrument-control scope and constraints.
They do not, by themselves, preselect the ICS 2.0 software integration route.
The software route must remain adapter-bounded and hardware-selection-driven.
```

### ICS 2.0 repository

This repository is the implementation source of truth. Current code determines what is actually available.

### v5 UI baseline

`src/justls/ics/app/ui/ui_alpha_skeleton_v5.html` remains the v5 fallback capability baseline. It is not merely an old mockup. v7.1 must not silently lose v5-visible concepts, stable API hooks, or instrument facts.

Important v5 fact:

```text
const SLIT_UM_PER_ARCSEC = 128.34;
```

This value matches the P0 telescope focal-plane plate scale and must be reused in v7.1 slit-width controls.

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

## MODS-inspired operational gap review before Phase 2.9

MODS is not a visual style target for ICS 2.0. Its useful lesson is operational completeness: mature spectrograph-control software tends to make the observing loop, data naming, command/status feedback, channel state, and observatory context visible to the operator.

Use MODS as a checklist for planning, not as a widget-by-widget UI template.

```text
Do not copy:
  - Blue/Red two-channel assumptions;
  - dense all-controls-on-one-page layout;
  - unguarded engineering controls in routine pages;
  - telescope write-control without an OCS/TCS contract.

Do translate:
  - setup/data-naming closure;
  - global command/status feedback;
  - operator-visible channel context;
  - read-only telescope/observatory context;
  - clear separation of Setup, Instrument, Observe, Housekeeping, and Engineer responsibilities.
```

### Setup and data naming

Scope:

```text
frontend + API + application service + persistence
```

Current state:

```text
- Setup exposes observer/project/session context.
- Root name, date prefix, next frame token, and data directory have visible frontend locations.
- Durable SessionDataContext exists.
- Setup context has GET/PUT/reload API endpoints.
- Setup context has service and JSON-store persistence.
- Observation arm attaches setup_context and data_preview snapshots into ObservationMeta.
- FITS/DataProduct persistence is still future work.
```

Phase 2.9-A decision:

```text
Durable Setup persistence is complete.
```

Required direction:

```text
- Keep Setup as the durable session/data-context source.
- Preserve visible filename/data preview in Setup.
- Reuse setup_context/data_preview in ObservationRequest preview and later ExposureRecord/DataProduct contracts.
- Do not over-scope this into a full observatory scheduler or proposal database.
```

### Global command and status feedback

Scope:

```text
frontend + runtime state + job/error read model
```

Current state:

```text
- v7 has a footer message rail.
- Instrument, Observe, and Presets expose command summaries.
- Request ID, latest job, last error, and result summary are visible in page-level bindings.
- The shared command/status semantics are not yet formalized as one durable read model.
```

Phase 2.9 direction:

```text
Formalize a shared command/status feedback read model before adding more command surfaces.
```

Required fields should include:

```text
last_command
request_id
latest_job
last_error
result_summary
connection/freshness when runtime polling is enabled
```

### B/G/R channel context

Scope:

```text
frontend-only summary for now; later domain/runtime/API only when hardware contracts require it
```

Current state:

```text
- B/G/R channel summary is visible in Instrument / Configure.
- P0 B/G/R wavelength ranges are preserved.
- Three-camera hardware is not yet available for real integration.
```

Phase 2.9 decision:

```text
Do not start a per-channel exposure-readiness or per-channel exposure-control model in Phase 2.9.
```

Required direction:

```text
- Keep B/G/R as an honest operator-visible summary.
- Do not introduce fake per-channel telemetry.
- Do not copy MODS Blue/Red exposure-control structure.
- Revisit channel readiness/control only when camera hardware and backend contracts are available.
```

### Telescope and external observatory context

Scope:

```text
external observatory / OCS boundary + read-only frontend context + future feedback-to-OCS candidate
```

Current state:

```text
- ICS 2.0 does not own telescope control.
- The current frontend does not expose target, RA/Dec, guiding, rotator, offset, or OCS context.
- P0 observation flow clearly involves OCS/TCS/weather/dome responsibilities beyond the instrument alone.
```

Phase 2.9 decision:

```text
Adopt read-only telescope/observatory context only where useful.
Do not implement telescope write-control inside ICS 2.0.
```

Boundary rule:

```text
ICS 2.0 must not bypass OCS/TCS authority.
Telescope pointing, rotator, guiding, offsets, dome, and weather authority remain outside routine ICS write-control unless a formal OCS/TCS interface contract says otherwise.
```

### Instrument mode, mask, and disperser semantics

Scope:

```text
domain + API + frontend only if JUST hardware/design requires it
```

Current state:

```text
- Slit, calibration, detector profile, presets, and B/G/R summary are visible.
- No committed mask/disperser/channel-mode domain object exists in ICS 2.0.
```

Phase 2.9 direction:

```text
Keep mask/disperser/channel-mode semantics as TBD unless current JUST hardware/design requires them.
```

Do not import MODS-specific slit-mask/dichroic/grating/prism controls unless they map to a real JUST mechanism and a real backend/hardware contract.

### Housekeeping and Engineer boundary

Scope:

```text
frontend IA + future API safety/authorization model
```

Current state:

```text
- Navigation reserves Housekeeping and Engineer pages.
- Detailed operational-maintenance and engineering-control responsibilities are not fully specified.
```

Phase 2.9 direction:

```text
Housekeeping = read-only operational maintenance and health context.
Engineer = guarded, unsafe, low-level, recovery, or hardware-maintenance controls.
```

Routine observing pages must not expose low-level bus, power, PLC, vendor-SDK, emergency, or recovery controls.

---

## Technology-adoption boundary

A requirement may mention a technology, but the software roadmap must not treat that technology as selected until hardware, operations, and integration contracts justify it.

Before a new technology or protocol becomes part of an implementation phase, it must pass this gate:

```text
- Does it solve a current phase problem?
- Is there real hardware or a real external interface contract behind it?
- Can the need be represented first as a schema, simulator, or adapter boundary?
- Does it preserve the Domain / Kernel / Application / Adapter layering?
- Does it keep low-level engineering detail out of routine operator flow?
- Can it be tested by unit, integration, or hardware-in-loop tests?
```

If not, it remains a candidate or placeholder, not a product requirement.

---

## P0 hard constraints for v7.1 and later

### Functional requirements

JUST long-slit spectrograph must support:

```text
- 370 nm - 980 nm wide-band low/medium-resolution science spectroscopy;
- 370 nm - 980 nm wide-band flat-field and wavelength calibration;
- adjustable spectral resolution over the 370 nm - 980 nm band;
- slit monitoring;
- dark-frame acquisition;
- offset guiding if practical;
- arbitrary long-slit direction setting.
```

v7.1 may stage these capabilities, but it must preserve visible locations for them and label incomplete backend contracts honestly.

### Spectrograph performance requirements

```text
Single exposure coverage:
  370 nm - 980 nm continuous spectral range

Channel split:
  B: 365 nm - 573 nm
  G: 546 nm - 772 nm
  R: 747 nm - 985 nm

Long-slit field:
  >= 10 arcmin along the slit

Selectable slit width design range:
  0.5 arcsec - 5.0 arcsec

Spectral resolution:
  R >= 1000 @ 1 arcsec slit
  adjustable R = 500 - 4500

Linear dispersion:
  B: 0.1113 nm / pixel
  G: 0.1006 nm / pixel
  R: 0.1162 nm / pixel

Overall efficiency:
  >= 30%

Focus / image quality:
  imaging focus precision <= 5 um (TBC)
  EE80 <= 27 um
  typical ghost PSF <= 1e-4
```

Do not introduce any Blue/Red two-channel wording or assumptions. Use B/G/R consistently.

These values are instrument/optical constraints. The software must preserve, display, validate, and record relevant configuration and metadata, but it cannot improve or guarantee optical performance by software alone.

### Telescope interface and plate scale

```text
Small-field Nasmyth interface:
  design field: 10 arcmin
  working band: 350 nm - 1000 nm
  design focal length: 26472 mm
  plate scale: 128.34 um / arcsec
  design focal surface: spherical, R2074 mm

Telescope effective aperture:
  approximately 4 m after obstruction

Main optical path throughput:
  approximately 65%

Mechanical interface:
  flange diameter: Phi 1100 mm
```

The plate scale is a software-control constraint, not just an optical note.

### Slit width units and defaults

v7.1 slit controls must expose both angular and mechanical units:

```text
primary operator unit:
  arcsec

backend command unit:
  um

fixed conversion:
  1 arcsec = 128.34 um
```

The backend currently accepts:

```text
POST /api/v1/slit
body: { width_um: ... }
```

Therefore v7.1 must convert before command submission, while still displaying the angular slit width to the operator.

Common v7.1 slit-width shortcuts:

```text
1.0 arcsec = 128.34 um
1.5 arcsec = 192.51 um
2.0 arcsec = 256.68 um
3.0 arcsec = 385.02 um
```

Do not use `0.1 arcsec` as a common default. The P0 design range remains 0.5-5.0 arcsec, but normal UI shortcuts should focus on 1.0, 1.5, 2.0, and 3.0 arcsec unless later operations experience changes this.

### Calibration system

The calibration system must support flat-field and wavelength calibration.

```text
flat source:
  continuous 365 nm - 985 nm coverage
  blue/red power-density difference < 50% (TBC)
  spatial non-uniformity <= 5% (TBC)

wavelength calibration:
  multiple stable emission-line lamps
  lines should be distributed across the observed spectral range

science/calibration path switching:
  flat mirror inserted/removed from the beam path

lamp switching:
  remote control through network power or equivalent control layer

known lamp/source concepts:
  deuterium-halogen / halogen flat-field source
  Hg(Ar)
  Ne
  possible ThAr or FeAr source

integrating sphere:
  inner diameter 150 mm
  PTFE material
  multiple fiber input/direct-mount interfaces
  replaceable exit slit, regular size 35 mm x 2 mm

calibration optics:
  3.3x magnification imaging system
  input focal ratio F5.42
  effective aperture 85 mm
  1 group of 3 fused-silica lenses + one 45-degree flat mirror
  flat mirror on electrically controlled translation stage
```

v7.1 implication:

```text
Calibration Configuration must distinguish mode/path, lamp/source state, and frame-type compatibility.
It must not collapse the system into a generic lamp on/off control.
If the mirror/path, shutter, power, or integrating-sphere details are not wired yet, show them as backend-contract placeholders rather than real controls.
```

Current UI decision:

```text
- Keep backend-aligned Mode/Lamp terminology in routine UI.
- Lamp selection is a candidate selector.
- Enable lamp determines whether the selected lamp is actually enabled.
- Set Lamp with Enable lamp off turns calibration lamps off and returns to science mode in the simulator.
- Set Lamp with Enable lamp on enters calibration mode and enables the selected lamp in the simulator.
- Science frame advisory: science mode + lamps off.
- Flat frame advisory: calibration mode + flat lamp.
- Arc frame advisory: calibration mode + Hg(Ar) or Ne arc lamp.
- Observe Frame, Expected for Frame, and Compatibility advisory fields should remain visible.
- Use Frame-Type Defaults may prepare the local form but must not dispatch commands by itself.
- Blocking validation belongs to the future Observation preview contract, not frontend-only logic.
```

### Slit monitor / slit camera / guider

The slit-monitor camera is a first-class instrument subsystem.

```text
functions:
  monitor slit switching;
  guide target image onto the slit center;
  monitor science target or calibration source at the slit;
  measure slit width.

camera:
  QHY268M
  Sony IMX571M
  26 MP
  pixel size 3.76 um x 3.76 um
  native 16-bit ADC
  two-stage semiconductor cooling

combined slit-camera result:
  field of view: 14.3 arcmin x 9.6 arcmin
  sampling: 0.1375 arcsec / pixel
  0.5 arcsec slit sampling: 3.63 pixel
```

v7.1 implication:

```text
Slit monitor / guider / live preview must not disappear from the operator console.
Until image backend contracts exist, show visible and honest placeholders.
```

### Observation workflow

P0 observation flow involves the whole observatory, not just detector exposure:

```text
1. control room checks weather, seeing, humidity, temperature, and observing conditions;
2. dome and ventilation/louver systems are opened when conditions are safe;
3. telescope self-check is completed;
4. telescope points to target coordinates;
5. tertiary mirror switches to the long-slit spectrograph terminal;
6. slit width and exposure time are set according to weather and science target;
7. telescope tracking and dome following start;
8. spectrograph exposure starts;
9. after exposure, tracking stops and data are transferred/stored;
10. calibration, dark, and bias/dark-field frames are acquired as needed;
11. target is completed and the next target begins;
12. after science observations, telescope returns to safe standby;
13. dome closes.
```

Current Phase 2.9 may keep Observe as a single-exposure control baseline. Later phases must not forget the broader OCS/TCS/weather/dome/data workflow.

### Electrical/control-system scope

P0 control scope includes:

```text
- continuously adjustable slit drive;
- B/G/R camera focusing;
- B/G/R camera and shutter exposure/readout;
- slit-monitor camera readout;
- slit-width measurement;
- fast photometry channel exposure/readout;
- flat and calibration lamp switching;
- whole-instrument derotation;
- EtherCAT distributed control.
```

Interpretation for ICS 2.0:

```text
- This list records P0 hardware/electrical-control scope.
- It does not preselect the ICS 2.0 software integration protocol.
- Actual hardware communication remains hardware-selection-driven.
- The software should keep hardware access adapter/gateway-bounded.
- Do not expose low-level bus, power, PLC, motion-controller, or vendor-SDK controls in the routine operator flow.
- Reserve low-level hardware details for Engineer / Housekeeping / Diagnostics and later role gating.
```

### OCS software modules and observing-plan intent

P0 describes the long-slit OCS as the interaction interface between JUST terminal instrument and astronomers. Its modules include:

```text
- telescope alignment/fine-adjustment module;
- environment monitoring module;
- long-slit observation module;
- slit monitoring module;
- offset guiding module;
- data storage and quick display;
- spectrograph exposure-control module split into B, G, and R channels.
```

P0 also references observing-plan fields:

```text
- target status;
- target name;
- RA;
- DEC;
- required exposure time;
- designed exposure time;
- required slit width;
- designed slit width;
- required slit angle;
- set slit angle;
- airmass;
- OTMSNR;
- note;
- whether flat and wavelength calibration plans are needed;
- ETC exposure-time calculator.
```

These are not immediate implementation requirements, but they must inform Phase 2.9+ workflow planning.

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
  Durable observer/project/session/file/data context backed by setup context API and JSON persistence.

Instrument / Configure
  Routine operator configuration and visibility for slit, calibration, detector profile, and B/G/R channel summary.

Observe
  Single-exposure execution and latest exposure preview. Do not turn this into a sequence runner until sequence contracts exist.

Presets
  Catalog, preview, confirmation, and guarded apply. Operator-facing diff polish belongs to the next UI workflow pass.

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
- Slit width controls must expose arcsec and um together.
- The only accepted conversion constant is 128.34 um / arcsec unless superseded by a later design decision.
- Common shortcut widths are 1.0, 1.5, 2.0, and 3.0 arcsec.
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
- Keep backend-aligned Mode/Lamp terminology in routine UI.
- Lamp selection is a candidate selector; Enable lamp determines whether the selected lamp is actually enabled.
- Science frame advisory: science mode + lamps off.
- Flat frame advisory: calibration mode + flat lamp.
- Arc frame advisory: calibration mode + Hg(Ar) or Ne arc lamp.
- Observe Frame, Expected for Frame, and Compatibility advisory fields should remain visible.
- Use Frame-Type Defaults may prepare the local form but must not dispatch commands by itself.
- Blocking validation belongs to the future Observation preview contract, not frontend-only logic.
- Unsafe/low-level lamp, mirror, shutter, or power behavior belongs outside the routine operator flow unless the backend contract is explicit.
```

### Detector and B/G/R channels

Relevant current capabilities:

```text
GET  /api/v1/detector/config
POST /api/v1/detector/config
```

v7.1 requirements:

```text
- Detector profile/config visibility is useful in Instrument / Configure.
- Complex detector write controls should remain limited until detector hardware and safety contracts are clearer.
- B/G/R must remain visible as three JUST channels, not as MODS Blue/Red.
- Per-channel exposure readiness/control must not be faked.
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
- Observe should preserve the single-exposure lifecycle until ObservationRequest/Preview and sequence contracts exist.
- Arm/start/finish/stop/abort controls must remain auditable and expose latest status.
- Do not imply that sequence runner, scheduler, OCS, FITS writer, or DataProduct pipeline exists before the backend does.
- Frame-type calibration compatibility should be advisory in the current UI and become blocking only through the future Observation preview contract.
```

---

## Documentation policy

Keep this requirements document durable. Do not add one-off phase notes here. Fold only long-lived requirements, capability classifications, and boundary decisions into this file.
