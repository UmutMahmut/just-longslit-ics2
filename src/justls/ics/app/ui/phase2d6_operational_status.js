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
    "observation.start",
    "observation.stop_readout",
    "observation.abort_discard",
    "config.high_impact",
  ]);

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

  function normalizeLevel(level) {
    return level === "ok" || level === "busy" || level === "warning" || level === "error"
      ? level
      : "warning";
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

    setText(byBind("conn.rtt"), `${Math.round(responseTimeMs)} ms`);
    setText(byBind("conn.last_ok"), new Date().toLocaleTimeString());
    if (operational.stale_threshold_s != null) {
      setText(byBind("conn.staleThreshold"), `${operational.stale_threshold_s.toFixed(1)} s`);
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

    const endpoint = (button.getAttribute("data-endpoint") || button.getAttribute("data-action") || "").toLowerCase();
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
    if (flags.fault || flags.disconnected) return true;

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
      applyButtonGates(data);
    } finally {
      statusRefreshInFlight = false;
    }
  }

  function start() {
    ensureOperationalPanel();
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
