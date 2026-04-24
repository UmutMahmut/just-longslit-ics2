(function () {
  "use strict";

  const STATUS_URL = "/api/v1/status/full";
  const LEVEL_TO_RAIL = {
    ok: "success",
    busy: "info",
    warning: "warning",
    error: "error",
  };

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

  function applyButtonGates(data) {
    const operational = data.operational_status || {};
    const flags = operational.flags || {};
    const blockHighImpact = !!(flags.armed || flags.exposing || flags.reading_out || flags.fault || flags.disconnected);
    const blockStart = !!(flags.exposing || flags.reading_out || flags.fault || flags.disconnected);
    const blockStopAbort = !!(flags.reading_out || flags.fault || flags.disconnected);

    document.querySelectorAll("button, .btn").forEach((button) => {
      const label = (button.textContent || "").trim().toLowerCase();
      const endpoint = (button.getAttribute("data-endpoint") || button.getAttribute("data-action") || "").toLowerCase();
      const isStart = label.includes("start") || endpoint.includes("observation/start");
      const isStopOrAbort = label.includes("abort") || label.includes("discard") || label.includes("stop") || endpoint.includes("abort_discard") || endpoint.includes("stop_readout");
      const isHighImpactConfig = label.includes("apply preset") || label.includes("slit") || label.includes("lamp") || endpoint.includes("/slit") || endpoint.includes("/lamp") || endpoint.includes("presets/apply") || endpoint.includes("detector/config");

      if (isStopOrAbort) {
        button.disabled = blockStopAbort;
        button.title = blockStopAbort ? "Blocked by operational status." : "";
      } else if (isStart) {
        button.disabled = blockStart;
        button.title = blockStart ? "Blocked by operational status." : "";
      } else if (isHighImpactConfig) {
        button.disabled = blockHighImpact;
        button.title = blockHighImpact ? "High-impact configuration is blocked by operational status." : "";
      }
    });
  }

  async function refreshOperationalStatus() {
    const t0 = performance.now();
    const response = await fetch(STATUS_URL, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
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
  }

  function start() {
    ensureOperationalPanel();
    refreshOperationalStatus().catch((err) => {
      const rail = document.querySelector(".message-rail");
      if (rail) {
        rail.setAttribute("data-level", "error");
        const body = rail.querySelector(".rail-body-text") || rail.querySelector(".rail-body");
        if (body) body.textContent = err.message || "Operational status refresh failed.";
      }
    });
    window.setInterval(() => {
      refreshOperationalStatus().catch(() => {});
    }, 1500);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();
