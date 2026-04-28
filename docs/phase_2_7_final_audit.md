# Phase 2.7 final audit

This document records the Phase 2.7 audit conclusion after the merged preset metadata, preview/diff, confirmation enforcement, structured apply result, latest-job audit linkage, and observation metadata linkage work.

## Audit date and scope

Phase audited: **Phase 2.7: Preset operational hardening**

Working baseline: remote **`main`**.

Audited scope:

- preset catalog metadata;
- preset preview/diff endpoint;
- high-risk preset confirmation enforcement;
- structured preset apply response;
- `latest_job` audit linkage for preset apply;
- observation metadata linkage to the most recent successful preset apply;
- backend tests and local manual smoke tests;
- current rollback and follow-up posture.

Out of scope:

- final GUI productization;
- frontend directory/module restructuring;
- Observation Plan / Sequence Runner;
- FITS header writing;
- persisted observation log database;
- data watcher / quicklook pipeline;
- real hardware integration;
- authentication / authorization;
- complex job queue / retry engine.

## Current repository status

Remote branch posture:

```text
main only
```

Local validation reported after syncing `main`:

```text
128 passed in 0.80s
```

Manual smoke test reported:

1. `POST /api/v1/presets/apply` with `calib_flat_default` and `confirmed=true` succeeded.
2. The apply response returned a `job_id`.
3. `POST /api/v1/observation/arm` then attached `observation_meta.preset_apply`.
4. The attached `preset_apply.job_id` matched the apply response job.

Example confirmed smoke-test result:

```json
{
  "job_id": "job-bd6a36e0e65b",
  "preset": "calib_flat_default",
  "category": "calibration",
  "risk_level": "high_impact",
  "requires_confirmation": true,
  "changed_fields_count": 8,
  "calibration_applied": true,
  "slit_applied": false,
  "finished_at": "2026-04-28T08:56:00.735476+00:00"
}
```

## Current merged Phase 2.7 commits

Remote `main` currently includes the following Phase 2.7 commits:

```text
784189253994f2972ea605e158d05d46665996eb  Phase 2.7-A: add preset operational metadata
b14f343afb351b984c3b4dd0d33f3fce120f11a8  Phase 2.7-B: add preset preview endpoint
ca296c487600923c0730d2bb83e10e58723d8012  Phase 2.7-C: enforce preset confirmation
138c6f58f0502bbbfc20a79f8a22fc988224e2c7  Phase 2.7-D: extend preset apply response schema
71c320ba5c9ef637465f364f775894d07c4b8d60  Phase 2.7-D: return structured preset apply result
10c34b87c34aa6879554bf2d5299e38d6b6cf000  Phase 2.7-D: update preset apply metadata test
86875e0f16ab5fca87191bbc2b9d130df047c44e  Phase 2.7-E1: expose preset apply job id
45410b686629d4a555eee07c556688000e8da72a  Phase 2.7-E1: record preset apply latest job
9964f9e88d003d3e80ace4cfaf889d6c4baac7c1  Phase 2.7-E1: test preset apply latest job
730aba76dd5e8f34857d22c2e447ef43e4ee485a  Phase 2.7-E2: add preset apply reference to observation metadata
e2768afe4654fe2dcae9cb72958b9ace71fff1f4  Phase 2.7-E2: carry preset apply reference into detector metadata
85804eaf0431e7ea9d9a6e3a911fe18bb4205b0d  Phase 2.7-E2: attach latest preset apply to observation arm
019244ce5749026166b215ff5bfb6575aabf52d4  Phase 2.7-E2: test observation metadata preset reference
```

Historical note: the Phase 2.7-C work was initially developed through a draft PR and then recovered/squash-committed directly to `main` after branch cleanup. The source of truth is now `main`, not the closed PR state.

## Phase 2.7-A: preset operational metadata

Status: **pass**

Built-in presets now carry operational metadata:

- `category`;
- `risk_level`;
- `requires_confirmation`.

Current intended semantics:

```text
science_default               category=science      risk_level=normal       requires_confirmation=false
rgb_safe_default              category=science      risk_level=normal       requires_confirmation=false
calib_flat_default            category=calibration  risk_level=high_impact  requires_confirmation=true
engineering_all_channels_off  category=engineering  risk_level=engineering  requires_confirmation=true
```

This is the first step from "preset as configuration shortcut" toward "preset as auditable operation".

## Phase 2.7-B: preset preview/diff

Status: **pass**

A side-effect-free preview endpoint exists:

```http
POST /api/v1/presets/preview
```

It reports:

- preset identity and operational metadata;
- whether apply would be blocked by observation-state interlock;
- detector config changes;
- calibration changes;
- slit changes;
- combined change list.

Important invariant:

```text
preview must not mutate runtime state
```

The current implementation preserves this invariant.

## Phase 2.7-C: confirmation enforcement

Status: **pass**

High-impact and engineering presets now require explicit API confirmation.

Expected behavior:

```json
{"name": "calib_flat_default"}
```

returns:

```text
400 confirmation_required
```

while:

```json
{"name": "calib_flat_default", "confirmed": true}
```

succeeds when runtime state permits mutation.

The service layer remains internally backward-compatible by defaulting service-level calls to `confirmed=True`, while the API boundary defaults to `confirmed=False`.

This is intentional:

```text
API/users must explicitly confirm risky operations.
Internal tests/services that call the service directly remain compatible unless they opt into strict confirmation behavior.
```

## Phase 2.7-D: structured apply result

Status: **pass**

`POST /api/v1/presets/apply` now returns a structured result while preserving existing fields.

The response includes:

- `applied_preset`;
- `summary`;
- `category`;
- `risk_level`;
- `requires_confirmation`;
- `job_id`;
- `detector_config`;
- `calibration`;
- `calibration_applied`;
- `slit_plan`;
- `slit_applied`;
- `detector_config_changes`;
- `calibration_changes`;
- `slit_changes`;
- `changed_fields`;
- `skipped_fields`;
- `blocked_fields`.

Important implementation detail:

```text
The diff is computed before apply, then returned together with the apply result.
```

This avoids the common bug where computing the diff after apply would hide the change because the target state has already become current state.

Current limitation:

```text
skipped_fields and blocked_fields are minimal/preparatory fields, not a full hardware-execution audit model yet.
```

That limitation is acceptable at Phase 2.7.

## Phase 2.7-E1: preset apply latest-job audit event

Status: **pass**

Successful preset apply now creates a job/audit event visible through status.

Expected linkage:

```text
POST /api/v1/presets/apply
→ apply response includes job_id
→ /api/v1/status/full operational_status.latest_job exposes the same job
```

The latest-job result summarizes:

- `kind=preset_apply`;
- preset name;
- category;
- risk level;
- confirmation requirement;
- changed field count;
- calibration/slit apply flags;
- skipped/blocked fields;
- success/error status.

This makes preset apply visible to operator diagnostics and future UI surfaces.

## Phase 2.7-E2: observation metadata preset linkage

Status: **pass**

Observation arm now attaches the most recent successful `preset_apply` job summary into observation metadata when available.

Expected linkage:

```text
POST /api/v1/presets/apply
→ successful preset_apply latest job
→ POST /api/v1/observation/arm
→ observation_meta.preset_apply references the preset apply job
```

If no successful preset apply exists, `observation_meta.preset_apply` remains `null`.

This is intentionally a lightweight metadata link, not a full persisted observation log or FITS-header implementation.

## Manual smoke-test interpretation

A failed preset apply while observation state is `armed` is expected and healthy:

```text
apply_preset_plan is blocked while observation state is armed
```

A failed second arm while observation state is already `armed` is also expected:

```text
detector is not ready to arm a new exposure
```

For manual smoke tests, the runtime should be in `ready_to_arm`, or the current armed/exposing observation should be cleared with `abort_discard`, or the server should be restarted.

Recommended E2 manual smoke-test shape:

```powershell
$status = Invoke-RestMethod http://127.0.0.1:8000/api/v1/status/full
$state = $status.observation.state

if ($state -eq "armed" -or $state -eq "exposing") {
  Invoke-RestMethod `
    -Method Post `
    -Uri http://127.0.0.1:8000/api/v1/observation/abort_discard
}

$apply = Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/presets/apply `
  -ContentType "application/json" `
  -Body '{"name":"calib_flat_default","confirmed":true}'

$arm = Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/observation/arm `
  -ContentType "application/json" `
  -Body '{"exp_time_s":5.0,"frame_type":"flat","operator_note":"preset-link"}'

$arm.observation_meta.preset_apply | ConvertTo-Json -Depth 10
```

## System-level assessment after Phase 2.7

Overall project state after Phase 2.7:

```text
approximately 68/100 to 72/100
```

This number is not a scientific metric. It is an engineering maturity estimate relative to the project goal: a robust long-slit spectrograph ICS suitable for simulator-backed development and later real-hardware expansion.

Compared with the pre-Phase-2.6 state, the system has moved from:

```text
prototype/control-surface assembly
```

toward:

```text
early operational-control architecture
```

The strongest areas now are:

- backend state-machine discipline;
- invalid operation handling;
- structured API errors;
- X-Request-ID and request troubleshooting basis;
- GUI-facing operational status;
- preset metadata, preview, confirmation, structured result, job audit, and observation metadata linkage;
- simulator-backed test coverage.

The weaker areas remain:

- frontend architecture is still transitional;
- `/ui/v6` is a review shell, not a production operator console;
- no persistent observation log exists;
- no FITS header/data-product pipeline exists;
- no quicklook/data watcher exists;
- no real hardware adapter validation exists;
- no acquisition/guide/alignment workflow exists;
- no Observation Plan / Sequence Runner exists;
- no authentication/role separation exists;
- package/developer setup documentation is still incomplete.

## MODS/BFOSC-inspired maturity mapping

Phase 2.7 directly advances these MODS/BFOSC-inspired goals:

- preset operations are no longer silent configuration shortcuts;
- calibration/science/engineering semantics are explicit;
- dangerous/high-impact operations require confirmation;
- operators can preview state changes before apply;
- apply results are auditable;
- apply results are visible through latest-job status;
- observation metadata can reference the preset context used before arm.

Phase 2.7 only partially advances these goals:

- observation procedure structure;
- recoverable sequences;
- acquisition/science/calibration/procedure workflows;
- persistent observing logs;
- GUI timeline/history;
- data watcher linkage.

These should remain future work, not retroactively claimed by Phase 2.7.

## Important implementation caveats

### 1. `latest successful preset_apply` is an in-memory runtime concept

The current preset linkage is held in runtime/job-tracker memory. It is not persisted across server restarts.

This is acceptable at Phase 2.7, but Phase 3/4 should not confuse it with durable observation logging.

### 2. Observation metadata points to the most recent successful preset apply

The current rule is simple:

```text
arm observation uses the most recent successful preset_apply job available in runtime
```

This is useful, but future Observation Plan / Sequence Runner work should make the relationship explicit per planned step rather than relying only on latest-job lookup.

### 3. `preset_apply` metadata is summary-level

The observation metadata stores a compact reference and summary, not the full diff list.

This is intentional. The detailed diff remains in the apply response and job result.

### 4. UI still needs later productization

The backend is now significantly more mature than the frontend structure.

The `src/justls/ics/app/ui` directory is still transitional and somewhat crowded. This should not be cleaned opportunistically during backend Phase 2.7 closure. It should be handled under a dedicated frontend modularization phase.

## Rollback posture

There is no Phase 2.7 feature flag comparable to the Phase 2.6 UI safety switches.

Rollback is therefore code-level. Revert in reverse order if needed.

Representative reverse-order rollback commands:

```bash
git revert 019244ce5749026166b215ff5bfb6575aabf52d4
git revert 85804eaf0431e7ea9d9a6e3a911fe18bb4205b0d
git revert e2768afe4654fe2dcae9cb72958b9ace71fff1f4
git revert 730aba76dd5e8f34857d22c2e447ef43e4ee485a
git revert 9964f9e88d003d3e80ace4cfaf889d6c4baac7c1
git revert 45410b686629d4a555eee07c556688000e8da72a
git revert 86875e0f16ab5fca87191bbc2b9d130df047c44e
git revert 10c34b87c34aa6879554bf2d5299e38d6b6cf000
git revert 71c320ba5c9ef637465f364f775894d07c4b8d60
git revert 138c6f58f0502bbbfc20a79f8a22fc988224e2c7
git revert ca296c487600923c0730d2bb83e10e58723d8012
git revert b14f343afb351b984c3b4dd0d33f3fce120f11a8
git revert 784189253994f2972ea605e158d05d46665996eb
```

In practice, if only the observation metadata linkage is problematic, revert only E2 first.

## Recommended next phase decision

Phase 2.7 should now close.

The next step should **not** be additional Phase 2.7 feature expansion unless a bug is found.

Recommended options:

### Preferred next phase: Phase 2.8 frontend modularization and operator UI productization

Rationale:

- backend operational semantics are now stronger than the UI structure;
- `app/ui` is becoming crowded;
- `/ui/v6` is useful as a concept shell but is not a better operator experience than the existing UI;
- future Sequence Runner / data watcher / guide alignment panels will be hard to add safely without a modular frontend structure.

Suggested Phase 2.8 scope:

- keep `/ui` as stable default;
- keep `/ui/v6` as review shell unless promoted deliberately;
- separate API client, command runtime, status runtime, and UI modules;
- preserve existing routes and behavior;
- no new instrument features;
- no Sequence Runner;
- no major visual redesign until module boundaries are clean.

### Alternative next phase: Phase 3 real subsystem/data-link expansion

Rationale:

- backend state machine and preset workflow foundation are strong enough to support early hardware/data abstractions.

Risk:

- frontend and project structure may become harder to maintain if more hardware-facing concepts are added before UI modularization.

### Deferred phase: Phase 4 Observation Plan / Sequence Runner

Do not start Phase 4 yet.

The current preset system is now a good foundation for Observation Plan, but the project still lacks data watcher, guide/alignment, persistent logging, and frontend modularity.

## Final conclusion

Phase 2.7 is ready to close.

It achieved the intended engineering goal:

```text
Presets have been upgraded from configuration shortcuts into auditable, confirmed, operation-linked control actions.
```

It should not claim:

```text
Full observation scripting or recoverable sequence execution is complete.
```

Recommended next move:

```text
Begin Phase 2.8: frontend modularization and operator UI productization.
```

This keeps the project aligned with the broader MODS/BFOSC-inspired maturity path without prematurely entering full Sequence Runner or hardware-expansion work.
