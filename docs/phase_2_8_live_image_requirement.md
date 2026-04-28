# Phase 2.8 live image display preservation requirement

## Decision

During Phase 2.8 frontend modularization and v7 operator console work, the live image / realtime preview capability from the current default UI must be preserved as a first-class operator-facing feature.

This requirement applies even if the first v7 implementation only keeps the image area as a stable LIVE / DEMO / NOT WIRED placeholder.

## Rationale

The realtime image display is not just visual decoration. It is one of the UI features that makes the JUST Long-Slit ICS feel like an observing instrument console rather than a generic web administration page.

It provides:

- immediate observing-site feedback during exposure and readout workflows;
- a natural mental model for operators watching the current frame, channel state, and acquisition context;
- a distinctive product feature for the JUST ICS frontend;
- a stable future landing area for quicklook, guider, acquisition, detector preview, and data watcher integrations.

## v7 design rule

The v7 operator console must not regress into a form-only or button-only interface.

At minimum, v7 should reserve a stable visual preview region in the Observe or Overview area:

```text
Observe / Overview:
- Main Live Frame or Latest Exposure Preview
- B / G / R channel preview placeholders when useful
- exposure state overlay
- latest file / last frame token placeholder
- stale image warning placeholder
```

Diagnostics may also expose image-feed status:

```text
Diagnostics:
- latest preview source
- last frame update time
- image feed freshness / stale state
- placeholder for future detector or quicklook backend status
```

## Phase 2.8 acceptance impact

A v7 shell can be considered acceptable only if it keeps an explicit live image / preview section in the UI information architecture.

Phase 2.8 does not require a real image stream, FITS quicklook, data watcher, or full detector image API yet. Those remain future work.

However, Phase 2.8 must preserve the live-vision-first direction so later real image integration has a stable UI home.

## Practical implementation guidance

Do not delete or weaken the current default `/ui` realtime preview behavior while building `/ui/v7`.

Do not make `/ui/v7` the default route until the v7 console has at least feature parity for the live image / preview area.

If v7 starts as a static shell, use explicit labels such as:

```text
LIVE / DEMO / NOT WIRED
Latest Exposure Preview
Image feed not wired yet
```

This keeps the engineering truth visible without losing the product direction.
