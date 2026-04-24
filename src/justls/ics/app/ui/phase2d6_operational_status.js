(function () {
  "use strict";

  const STATUS_URL = "/api/v1/status/full";
  const POLL_INTERVAL_MS = 1500;
  const STATUS_TIMEOUT_MS = 1200;
  const LEVEL_TO_RAIL = {
    ok: "success",
    busy: "info",
    warning: "warning",
    error: "error",
  };
  const CONTROLLED_COMMANDS = new Set([
    "observation.arm",
    "observation.start",
    "observation.stop_readout",
    "observation.abort_discard",
    "config.high_impact",
  ]);
  const COMMAND_MARKER_CATALOG = [
    {
      command: "observation.arm",
      labels: ["Arm", "Arm Observation", "准备曝光"],
      endpoints: ["observation/arm"],
    },
    {
      command: "observation.start",
      labels: ["Start", "Start Exposure", "Start Observation", "开始曝光"],
      endpoints: ["observation/start"],
    },
    {
      command: "observation.stop_readout",
      labels: ["Stop & Readout", "Stop and Readout", "停止并读出"],
      endpoints: ["observation/stop_readout"],
    },
    {
      command: "observation.abort_discard",
      labels: ["Abort & Discard", "Abort and Discard", "中止并丢弃"],
      endpoints: ["observation/abort_discard"],
    },
    {
      risk: "high-impact-config",
      labels: [
        "Apply Preset",
        "Set Slit",
        "Set Slit Width",
        "Set Slit Angle",
        "Lamp On",
        "Lamp Off",
        "Set Lamp",
        "Set Calibration Mode",
        "Save Detector Config",
        "Apply Detector Config",
        "应用预置",
        "设置狭缝",
        "设置狭缝角",
        "打开灯源",
        "关闭灯源",
      ],
      endpoints: [
        "/api/v1/slit",
        "/api/v1/slit_angle",
        "/api/v1/lamp",
        "/api/v1/presets/apply",
        "/api/v1/detector/config",
        "/api/v1/calibration/mode",
        "/api/v1/calibration/lamp",
      ],
    },
  ];

  let statusRefreshInFlight = false;

  function byBind(name) {
    return document.querySelector(`[data-bind="${name}"]`);
  }

  function byState(name) {
    return document.querySelector(`[data-state="${name}"]`);
  }

  function ensureOperationalPanel() {
    let panel = document.querySelector("[data-phase2d6-operational-panel]");
    if (panel) return panel;

    const rail = document.querySelector(".message-rail");
    panel = document.createElement("div");
    panel.setAttribute("data-phase2d6-operational-panel", "true");
    panel.innerHTML = `
      <span class="mini-badge" data-phase2d6-level>Operational: pending</span>
      <span class="mini-badge" data-phase2d6-exposure>Exposure: unknown</span>
      <span class="mini-badge" data-phase2d6-control>Control: unknown</span>
    `;
    panel.style.display = "flex";
    panel.style.flexWrap = "wrap";
    panel.style.gap = "8px";
    panel.style.margin = "10px 18px";

    if (rail && rail.parentElement) {
      rail.parentElement.insertBefore(panel, rail.nextSibling);
    } else {
      document.body.prepend(panel);
    }
    return panel;
  }

  function setText(selector, value) {
    const el = typeof selector === "string" ? document.querySelector(selector) : selector;
    if (el) el.textContent = value == null ? "—" : String(value);
  }

  function bind(name, value) {
    setText(byBind(name), value);
  }

  function normalizeText(value) {
    return (value || "").replace(/\s+/g, " ").trim().toLowerCase();
  }

  function normalizeLevel(level) {
    return level === "ok" || level === "busy" || level === "warning" || level === "error"
      ? level
      : "warning";
  }

  function readActionSurface(button) {
    const attrs = [
      "data-endpoint",
      "data-action",
      "data-api-path",
      "onclick",
      "aria-label",
      "title",
      "data-route",
    ];
    const values = attrs.map((name) => button.getAttribute(name) || "");
    values.push(button.textContent || "");
    return values.join(" ").toLowerCase();
  }

  function markerMatches(button, marker) {
    const surface = readActionSurface(button);
    const label = normalizeText(button.textContent || "");
    const labels = marker.labels || [];
    const endpoints = marker.endpoints || [];

    if (labels.some((candidate) => label === normalizeText(candidate))) return true;
    return endpoints.some((endpoint) => surface.includes(endpoint.toLowerCase()));
  }

  function annotateCommandMarkers() {
    document.querySelectorAll("button, .btn").forEach((button) => {
      if (button.hasAttribute("data-command") || button.hasAttribute("data-risk")) return;

      const marker = COMMAND_MARKER_CATALOG.find((candidate) => markerMatches(button, candidate));
      if (!marker) return;

      if (marker.command) {
        button.setAttribute("data-command", marker.command);
      }
      if (marker.risk) {
        button.setAttribute("data-risk", marker.risk);
      }
      button.setAttribute("data-phase2d6-marker-source", "catalog");
    });
  }

  function updateRail(operational) {
    const level = normalizeLevel(operational.level);
    const railLevel = LEVEL_TO_RAIL[level] || "info";
    const rail = document.querySelector(".message-rail");
    if (rail) {
      rail.setAttribute("data-level", railLevel);
      const body = rail.querySelector(".rail-body-text") || rail.querySelector(".rail-body");
      if (body) {
        body.textContent = operational.summary || "Operational status updated.";
      }
    }
  }

  function setDegradedRail(message) {
    const rail = document.querySelector(".message-rail");
    if (!rail) return;
    rail.setAttribute("data-level", "warning");
    const body = rail.querySelector(".rail-body-text") || rail.querySelector(".rail-body");
    if (body) body.textContent = message || "Operational status refresh degraded.";
  }

  function updateConnectionBlock(data, responseTimeMs, requestId) {
    const operational = data.operational_status || {};
    const level = normalizeLevel(operational.level);
    const dot = byState("conn.dot");
    const state = byBind("conn.state");

    if (dot) {
      dot.classList.remove("ok", "warn", "err", "info");
      dot.classList.add(level === "ok" ? "ok" : level === "busy" ? "info" : level === "warning" ? "warn" : "err");
    }
    if (state) state.textContent = level === "ok" ? "Ready" : level.toUpperCase();

    bind("conn.rtt", `${Math.round(responseTimeMs)} ms`);
    bind("conn.last_ok", new Date().toLocaleTimeString());
    bind("conn.poll", `${(POLL_INTERVAL_MS / 1000).toFixed(1)} s`);
    if (operational.stale_threshold_s != null) {
      bind("conn.staleThreshold", `${operational.stale_threshold_s.toFixed(1)} s`);
    }
    if (requestId) {
      const panel = ensureOperationalPanel();
      panel.dataset.lastRequestId = requestId;
      panel.title = `Last X-Request-ID: ${requestId}`;
    }
  }

  function updateOperationalPanel(data) {
    const operational = data.operational_status || {};
    const panel = ensureOperationalPanel();
    setText(panel.querySelector("[data-phase2d6-level]"), `Operational: ${normalizeLevel(operational.level).toUpperCase()}`);
    setText(panel.querySelector("[data-phase2d6-exposure]"), `Exposure: ${operational.exposure_state || "unknown"}`);
    setText(panel.querySelector("[data-phase2d6-control]"), `Control: ${operational.control_state || "unknown"}`);
  }

  function updateStatusFullFields(data) {
    const state = data.state || {};
    const detectorConfig = data.detector_config || {};
    const calibration = data.calibration || {};
    const observation = data.observation || {};

    bind("runtime.mode", data.run_mode || data.hal || "unknown");
    bind("api.base", window.location.origin || "same-origin");
    bind("state.slit_width_um", state.slit_width_um == null ? "—" : `${state.slit_width_um} µm`);
    bind("state.slit_angle_deg", state.slit_angle_deg == null ? "—" : `${state.slit_angle_deg}°`);
    bind("state.lamp_on", state.lamp_on ? "on" : "off");
    bind("detector.profile", detectorConfig.profile_name || "—");
    bind("calibration.mode", calibration.mode || "—");
    bind("observation.state", observation.state || "—");

    const debugEl = byBind("debug.status");
    if (debugEl && !debugEl.dataset.phase2d6CommandOutput) {
      debugEl.textContent = JSON.stringify(
        {
          operational_status: data.operational_status,
          observation: data.observation,
          detector_config: data.detector_config,
          timestamp_utc: data.timestamp_utc,
        },
        null,
        2,
      );
    }
  }

  function rememberInitialDisabled(button) {
    if (!button.dataset.phase2d6InitialDisabled) {
      button.dataset.phase2d6InitialDisabled = button.disabled ? "true" : "false";
    }
  }

  function inferCommand(button) {
    const explicitCommand = (button.getAttribute("data-command") || "").trim().toLowerCase();
    if (explicitCommand) return explicitCommand;

    const explicitRisk = (button.getAttribute("data-risk") || "").trim().toLowerCase();
    if (explicitRisk === "high-impact-config") return "config.high_impact";

    const endpoint = (button.getAttribute("data-endpoint") || button.getAttribute("data-action") || button.getAttribute("data-api-path") || "").toLowerCase();
    if (endpoint.includes("observation/arm")) return "observation.arm";
    if (endpoint.includes("observation/start")) return "observation.start";
    if (endpoint.includes("observation/stop_readout")) return "observation.stop_readout";
    if (endpoint.includes("observation/abort_discard")) return "observation.abort_discard";
    if (
      endpoint.includes("/slit") ||
      endpoint.includes("/lamp") ||
      endpoint.includes("presets/apply") ||
      endpoint.includes("detector/config") ||
      endpoint.includes("calibration/mode") ||
      endpoint.includes("calibration/lamp")
    ) {
      return "config.high_impact";
    }

    return "";
  }

  function shouldDisableCommand(command, flags) {
    if (command === "status.refresh") return false;
    if (flags.fault || flags.disconnected) return true;

    if (command === "observation.arm") {
      return !!(flags.armed || flags.exposing || flags.reading_out);
    }
    if (command === "observation.start") {
      return !flags.armed || flags.exposing || flags.reading_out;
    }
    if (command === "observation.stop_readout") {
      return !flags.exposing || flags.reading_out;
    }
    if (command === "observation.abort_discard") {
      return !(flags.armed || flags.exposing) || flags.reading_out;
    }
    if (command === "config.high_impact") {
      return !!(flags.armed || flags.exposing || flags.reading_out);
    }
    return false;
  }

  function applyButtonGates(data) {
    annotateCommandMarkers();

    const operational = data.operational_status || {};
    const flags = operational.flags || {};

    document.querySelectorAll("button, .btn").forEach((button) => {
      rememberInitialDisabled(button);
      const command = inferCommand(button);
      if (!CONTROLLED_COMMANDS.has(command)) return;

      const initiallyDisabled = button.dataset.phase2d6InitialDisabled === "true";
      const disableByOperationalStatus = shouldDisableCommand(command, flags);
      button.disabled = initiallyDisabled || disableByOperationalStatus;
      button.title = disableByOperationalStatus ? "Blocked by operational status." : "";
      button.dataset.phase2d6Command = command;
    });
  }

  async function fetchStatusWithTimeout() {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), STATUS_TIMEOUT_MS);
    try {
      return await fetch(STATUS_URL, {
        cache: "no-store",
        headers: { Accept: "application/json" },
        signal: controller.signal,
      });
    } finally {
      window.clearTimeout(timeoutId);
    }
  }

  async function refreshOperationalStatus() {
    if (statusRefreshInFlight) return;
    statusRefreshInFlight = true;
    const t0 = performance.now();
    try {
      const response = await fetchStatusWithTimeout();
      const requestId = response.headers.get("X-Request-ID") || "";
      const data = await response.json();
      const responseTimeMs = performance.now() - t0;
      if (!response.ok) {
        throw new Error(data?.detail?.message || `Status refresh failed: ${response.status}`);
      }
      updateRail(data.operational_status || {});
      updateConnectionBlock(data, responseTimeMs, requestId);
      updateOperationalPanel(data);
      updateStatusFullFields(data);
      applyButtonGates(data);
    } finally {
      statusRefreshInFlight = false;
    }
  }

  function installManualRefresh() {
    document.addEventListener("click", (event) => {
      const button = event.target.closest('[data-command="status.refresh"]');
      if (!button) return;
      event.preventDefault();
      refreshOperationalStatus().catch((err) => {
        setDegradedRail(err.name === "AbortError" ? "Operational status refresh timed out." : err.message);
      });
    });
  }

  function start() {
    ensureOperationalPanel();
    annotateCommandMarkers();
    installManualRefresh();
    refreshOperationalStatus().catch((err) => {
      setDegradedRail(err.name === "AbortError" ? "Operational status refresh timed out." : err.message);
    });
    window.setInterval(() => {
      refreshOperationalStatus().catch((err) => {
        setDegradedRail(err.name === "AbortError" ? "Operational status refresh timed out." : err.message);
      });
    }, POLL_INTERVAL_MS);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();
