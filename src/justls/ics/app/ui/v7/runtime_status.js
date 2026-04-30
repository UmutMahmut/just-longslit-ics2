// v7 opt-in runtime status adapter.
// Default /ui/v7 remains static. This script is injected only when
// JUSTLS_UI_V7_RUNTIME_ENABLED=1.

(function () {
  "use strict";

  const GLOBAL_KEY = "__JUSTLS_V7_RUNTIME_STATUS__";
  const STATUS_ENDPOINT = "/api/v1/status/full";
  const POLL_MS = 2000;
  const RAW_MAX_CHARS = 12000;

  const runtime = window[GLOBAL_KEY] || {
    started: false,
    intervalId: null,
    refreshInFlight: false,
    lastOkAt: null,
    lastError: null,
    refreshCount: 0,
  };
  window[GLOBAL_KEY] = runtime;

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback;
    return String(value);
  }

  function setText(selector, value, fallback) {
    document.querySelectorAll(selector).forEach((node) => {
      const next = text(value, fallback);
      if (node.textContent !== next) node.textContent = next;
    });
  }

  function panel(id, title, pageSelector) {
    const existing = document.getElementById(id);
    if (existing) return existing;

    const host = pageSelector ? document.querySelector(pageSelector) : document.querySelector(".workspace");
    if (!host) return null;

    const section = document.createElement("section");
    section.id = id;
    section.className = "panel";
    section.setAttribute("data-phase", "2.8-runtime-opt-in");
    section.innerHTML = `<h2>${title}</h2><div class="panel-body"></div>`;
    host.insertBefore(section, host.firstChild);
    return section;
  }

  function ensureRuntimePanel() {
    const section = panel("v7-runtime-status", "Runtime Status · /api/v1/status/full", null);
    if (!section) return null;
    const body = section.querySelector(".panel-body");
    if (!body.dataset.ready) {
      body.dataset.ready = "true";
      body.innerHTML = `
        <dl class="kv">
          <dt>Connection</dt><dd><code data-bind="v7.connection">connecting</code></dd>
          <dt>Run Mode</dt><dd><code data-bind="v7.run_mode">unknown</code></dd>
          <dt>Operational</dt><dd><code data-bind="v7.operational">unknown</code></dd>
          <dt>Exposure</dt><dd><code data-bind="v7.exposure_state">unknown</code></dd>
          <dt>Detector Profile</dt><dd><code data-bind="v7.detector_profile">unknown</code></dd>
          <dt>Latest Job</dt><dd><code data-bind="v7.latest_job">not available</code></dd>
          <dt>Runtime Polls</dt><dd><code data-bind="v7.runtime_status.refresh_count">0</code></dd>
        </dl>`;
    }
    return section;
  }

  function ensureSetupPanel() {
    const section = panel("v7-setup-readiness", "Setup Readiness · Current Instrument Context", '[data-page-panel="setup"]');
    if (!section) return null;
    const body = section.querySelector(".panel-body");
    if (!body.dataset.ready) {
      body.dataset.ready = "true";
      body.innerHTML = `
        <dl class="kv">
          <dt>Run Mode</dt><dd><code data-bind="v7.setup.run_mode">unknown</code></dd>
          <dt>Operational</dt><dd><code data-bind="v7.setup.operational">unknown</code></dd>
          <dt>Observation State</dt><dd><code data-bind="v7.setup.observation_state">unknown</code></dd>
          <dt>Detector Profile</dt><dd><code data-bind="v7.setup.detector_profile">unknown</code></dd>
        </dl>`;
    }
    return section;
  }

  function ensureRawPreview() {
    const section = panel("v7-raw-status-preview", "Raw Status Preview · /api/v1/status/full", '[data-page-panel="diagnostics"]');
    if (!section) return null;
    const body = section.querySelector(".panel-body");
    if (!body.dataset.ready) {
      body.dataset.ready = "true";
      body.innerHTML = `<pre data-bind="v7.raw_status_preview">waiting for status/full...</pre>`;
    }
    return section;
  }

  function latestJobLabel(data) {
    const job = data && data.latest_job;
    if (!job) return "not available";
    return [job.status, job.subsystem, job.action, job.job_id].filter(Boolean).join(" · ");
  }

  function bind(data) {
    ensureRuntimePanel();
    ensureSetupPanel();
    ensureRawPreview();

    const observation = data.observation || {};
    const operational = data.operational_status || {};
    const detector = data.detector_config || {};

    setText('[data-bind="v7.connection"]', "connected", "connected");
    setText('[data-bind="v7.run_mode"]', data.run_mode, "unknown");
    setText('[data-bind="v7.operational"]', operational.level || operational.state || operational.summary, "unknown");
    setText('[data-bind="v7.exposure_state"]', observation.state, "unknown");
    setText('[data-bind="v7.detector_profile"]', detector.profile_name, "unknown");
    setText('[data-bind="v7.latest_job"]', latestJobLabel(data), "not available");
    setText('[data-bind="v7.setup.run_mode"]', data.run_mode, "unknown");
    setText('[data-bind="v7.setup.operational"]', operational.level || operational.state || operational.summary, "unknown");
    setText('[data-bind="v7.setup.observation_state"]', observation.state, "unknown");
    setText('[data-bind="v7.setup.detector_profile"]', detector.profile_name, "unknown");
    setText('[data-bind="v7.runtime_status.refresh_count"]', runtime.refreshCount, "0");

    let raw = JSON.stringify(data, null, 2);
    if (raw.length > RAW_MAX_CHARS) raw = `${raw.slice(0, RAW_MAX_CHARS)}\n... truncated ...`;
    setText('[data-bind="v7.raw_status_preview"]', raw, raw);
  }

  async function refresh() {
    if (runtime.refreshInFlight) return;
    runtime.refreshInFlight = true;
    try {
      const response = await fetch(STATUS_ENDPOINT, { cache: "no-store", headers: { Accept: "application/json" } });
      const data = await response.json();
      runtime.refreshCount += 1;
      if (response.ok) {
        runtime.lastOkAt = new Date().toISOString();
        runtime.lastError = null;
        bind(data);
      } else {
        runtime.lastError = `HTTP ${response.status}`;
        setText('[data-bind="v7.connection"]', `error ${response.status}`, "error");
      }
    } catch (error) {
      runtime.lastError = text(error && error.message, "fetch failed");
      setText('[data-bind="v7.connection"]', `error: ${runtime.lastError}`, "error");
    } finally {
      runtime.refreshInFlight = false;
    }
  }

  function start() {
    ensureRuntimePanel();
    ensureSetupPanel();
    ensureRawPreview();

    if (runtime.started) {
      refresh();
      return;
    }

    runtime.started = true;
    refresh();
    runtime.intervalId = window.setInterval(refresh, POLL_MS);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
})();
