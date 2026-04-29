// Phase 2.8-C/D v7 status and setup binding adapter.
// Scope:
//   - bind the v7 operator console prototype to /api/v1/status/full;
//   - keep the default /ui and /ui/v6 untouched;
//   - do not introduce new backend API requirements;
//   - preserve the live image preview area as a placeholder until a future
//     image/quicklook/data-watcher backend is intentionally added.
//
// Cleanup note:
//   This adapter owns compact runtime/setup panels with explicit data-bind
//   markers. It intentionally avoids binding by visible label text, so UI copy
//   changes in the static shell do not silently break status updates.

(function () {
  "use strict";

  const STATUS_ENDPOINT = "/api/v1/status/full";
  const POLL_INTERVAL_MS = 2000;
  const STALE_AFTER_MS = 6000;
  const RAW_STATUS_MAX_CHARS = 20000;

  const state = {
    lastOkAt: null,
    lastRequestId: null,
    pollTimer: null,
  };

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") {
      return fallback;
    }
    return String(value);
  }

  function upper(value, fallback) {
    return text(value, fallback).toUpperCase();
  }

  function setTextById(id, value, fallback) {
    const node = document.getElementById(id);
    if (!node) return;
    node.textContent = text(value, fallback);
  }

  function setBoundText(name, value, fallback) {
    const nodes = document.querySelectorAll(`[data-bind="${name}"]`);
    nodes.forEach((node) => {
      node.textContent = text(value, fallback);
    });
  }

  function setConnectionState(level, label) {
    const panel = ensureRuntimePanel();
    panel.setAttribute("data-connection", level);
    setBoundText("v7.connection", label, "unknown");
  }

  function addRuntimePanelStyles() {
    if (document.getElementById("v7-runtime-status-style")) return;

    const style = document.createElement("style");
    style.id = "v7-runtime-status-style";
    style.textContent = `
      .v7-runtime-status {
        border: 1px solid var(--border);
        background: linear-gradient(180deg, #ffffff, #edf3fb);
        margin-bottom: 12px;
      }
      .v7-runtime-status[data-connection="ok"] {
        border-color: #8fc6ae;
      }
      .v7-runtime-status[data-connection="stale"] {
        border-color: #dab36f;
        background: linear-gradient(180deg, #fffaf0, #f7edd8);
      }
      .v7-runtime-status[data-connection="error"] {
        border-color: #dc9b9b;
        background: linear-gradient(180deg, #fff2f2, #f5dddd);
      }
      .v7-runtime-status h2 {
        margin: 0;
        padding: 8px 10px;
        border-bottom: 1px solid var(--border-soft);
        background: linear-gradient(180deg, #f8fafc, #eef3f9);
        font-size: 13px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
      }
      .v7-runtime-status[data-connection="ok"] h2 {
        background: linear-gradient(180deg, #f0fff7, #e0f4ea);
      }
      .v7-runtime-status[data-connection="stale"] h2 {
        background: linear-gradient(180deg, #fff7e5, #f6e3bc);
      }
      .v7-runtime-status[data-connection="error"] h2 {
        background: linear-gradient(180deg, #fff0f0, #f4cccc);
      }
      .v7-runtime-status-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1px;
        background: var(--border-soft);
      }
      .v7-runtime-status-cell {
        background: #ffffff;
        padding: 8px 10px;
        min-width: 0;
      }
      .v7-runtime-status-cell span:first-child {
        display: block;
        color: var(--muted);
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
      }
      .v7-runtime-status-cell code,
      .v7-runtime-status-cell strong {
        font-family: var(--mono);
        font-size: 12px;
        overflow-wrap: anywhere;
      }
      [data-bind="v7.connection"][data-level="ok"] {
        color: #147a4f;
        font-weight: 700;
      }
      [data-bind="v7.connection"][data-level="stale"] {
        color: #9a5b00;
        font-weight: 700;
      }
      [data-bind="v7.connection"][data-level="error"] {
        color: #a93333;
        font-weight: 700;
      }
      .v7-setup-readiness {
        margin-bottom: 12px;
      }
      .v7-setup-readiness .hint {
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 8px;
      }
      .v7-setup-readiness code {
        font-family: var(--mono);
      }
      .v7-raw-status-preview {
        margin-top: 12px;
      }
      .v7-raw-status-preview .panel-body {
        display: grid;
        gap: 8px;
      }
      .v7-raw-status-preview pre {
        max-height: 360px;
        overflow: auto;
        white-space: pre-wrap;
        word-break: break-word;
        font-size: 11px;
        line-height: 1.45;
        background: #0f172a;
        color: #e5edf8;
        border: 1px solid #334155;
        padding: 10px;
        margin: 0;
      }
      .v7-raw-status-preview .hint {
        color: var(--muted);
        font-size: 12px;
      }
      @media (max-width: 1160px) {
        .v7-runtime-status-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      }
      @media (max-width: 720px) {
        .v7-runtime-status-grid { grid-template-columns: 1fr; }
      }
    `;
    document.head.appendChild(style);
  }

  function runtimeCell(label, bindName, initialValue) {
    const cell = document.createElement("div");
    cell.className = "v7-runtime-status-cell";

    const labelNode = document.createElement("span");
    labelNode.textContent = label;

    const valueNode = document.createElement("code");
    valueNode.setAttribute("data-bind", bindName);
    valueNode.textContent = initialValue;

    cell.appendChild(labelNode);
    cell.appendChild(valueNode);
    return cell;
  }

  function kvRow(label, bindName, initialValue) {
    const dt = document.createElement("dt");
    dt.textContent = label;

    const dd = document.createElement("dd");
    const valueNode = document.createElement("code");
    valueNode.setAttribute("data-bind", bindName);
    valueNode.textContent = initialValue;
    dd.appendChild(valueNode);

    return [dt, dd];
  }

  function appendKvRow(list, label, bindName, initialValue) {
    const row = kvRow(label, bindName, initialValue);
    list.appendChild(row[0]);
    list.appendChild(row[1]);
  }

  function ensureRuntimePanel() {
    const existing = document.getElementById("v7-runtime-status");
    if (existing) return existing;

    addRuntimePanelStyles();

    const panel = document.createElement("section");
    panel.id = "v7-runtime-status";
    panel.className = "v7-runtime-status";
    panel.setAttribute("aria-label", "v7 runtime status binding panel");
    panel.setAttribute("data-connection", "unknown");

    const title = document.createElement("h2");
    title.textContent = "Runtime Status · Bound to /api/v1/status/full";

    const grid = document.createElement("div");
    grid.className = "v7-runtime-status-grid";
    grid.appendChild(runtimeCell("Connection", "v7.connection", "connecting"));
    grid.appendChild(runtimeCell("Run Mode", "v7.run_mode", "unknown"));
    grid.appendChild(runtimeCell("Operational", "v7.operational", "unknown"));
    grid.appendChild(runtimeCell("Exposure", "v7.exposure_state", "unknown"));
    grid.appendChild(runtimeCell("Detector Profile", "v7.detector_profile", "unknown"));
    grid.appendChild(runtimeCell("Calibration", "v7.calibration", "unknown"));
    grid.appendChild(runtimeCell("Preset Context", "v7.preset_context", "not linked"));
    grid.appendChild(runtimeCell("Latest Job", "v7.latest_job", "not available"));
    grid.appendChild(runtimeCell("Request ID", "v7.request_id", "not available"));
    grid.appendChild(runtimeCell("Last Error", "v7.last_error", "none"));
    grid.appendChild(runtimeCell("Status Source", "v7.status_source", STATUS_ENDPOINT));
    grid.appendChild(runtimeCell("Last OK", "v7.last_ok", "not yet"));

    panel.appendChild(title);
    panel.appendChild(grid);

    const workspace = document.querySelector(".workspace");
    if (workspace) {
      workspace.insertBefore(panel, workspace.firstChild);
    } else {
      document.body.appendChild(panel);
    }

    return panel;
  }

  function ensureSetupReadinessPanel() {
    const existing = document.getElementById("v7-setup-readiness");
    if (existing) return existing;

    addRuntimePanelStyles();

    const setupPage = document.querySelector('[data-page-panel="setup"]');
    if (!setupPage) return null;

    const panel = document.createElement("section");
    panel.id = "v7-setup-readiness";
    panel.className = "panel v7-setup-readiness";
    panel.setAttribute("aria-label", "v7 setup readiness summary");

    const title = document.createElement("h2");
    title.textContent = "Setup Readiness · Current Instrument Context";

    const body = document.createElement("div");
    body.className = "panel-body";

    const hint = document.createElement("div");
    hint.className = "hint";
    hint.textContent = "Read-only summary from /api/v1/status/full. Session form fields remain local placeholders in Phase 2.8-D.";

    const list = document.createElement("dl");
    list.className = "kv";
    appendKvRow(list, "Connection", "v7.setup.connection", "connecting");
    appendKvRow(list, "Run Mode", "v7.setup.run_mode", "unknown");
    appendKvRow(list, "Operational", "v7.setup.operational", "unknown");
    appendKvRow(list, "Observation State", "v7.setup.observation_state", "unknown");
    appendKvRow(list, "Detector Profile", "v7.setup.detector_profile", "unknown");
    appendKvRow(list, "Calibration", "v7.setup.calibration", "unknown");
    appendKvRow(list, "Preset Context", "v7.setup.preset_context", "not linked");
    appendKvRow(list, "Save Enabled", "v7.setup.save_enabled", "unknown");
    appendKvRow(list, "Latest Job", "v7.setup.latest_job", "not available");
    appendKvRow(list, "Request ID", "v7.setup.request_id", "not available");

    body.appendChild(hint);
    body.appendChild(list);
    panel.appendChild(title);
    panel.appendChild(body);
    setupPage.insertBefore(panel, setupPage.firstChild);

    return panel;
  }

  function ensureRawStatusPreview() {
    const existing = document.getElementById("v7-raw-status-preview");
    if (existing) return existing;

    addRuntimePanelStyles();

    const diagnosticsPage = document.querySelector('[data-page-panel="diagnostics"]');
    if (!diagnosticsPage) return null;

    const panel = document.createElement("section");
    panel.id = "v7-raw-status-preview";
    panel.className = "panel v7-raw-status-preview";
    panel.setAttribute("aria-label", "bounded raw status full preview");

    const title = document.createElement("h2");
    title.textContent = "Raw Status Preview · /api/v1/status/full";

    const body = document.createElement("div");
    body.className = "panel-body";

    const hint = document.createElement("div");
    hint.className = "hint";
    hint.textContent = `Bounded diagnostic preview from the existing status endpoint. Maximum ${RAW_STATUS_MAX_CHARS} characters.`;

    const pre = document.createElement("pre");
    pre.setAttribute("data-bind", "v7.raw_status_preview");
    pre.textContent = "waiting for status/full...";

    body.appendChild(hint);
    body.appendChild(pre);
    panel.appendChild(title);
    panel.appendChild(body);
    diagnosticsPage.appendChild(panel);

    return panel;
  }

  function updateRawStatusPreview(data) {
    const panel = ensureRawStatusPreview();
    if (!panel) return;

    const rawNode = panel.querySelector('[data-bind="v7.raw_status_preview"]');
    if (!rawNode) return;

    let rendered = JSON.stringify(data, null, 2);
    if (rendered.length > RAW_STATUS_MAX_CHARS) {
      rendered = `${rendered.slice(0, RAW_STATUS_MAX_CHARS)}\n... truncated at ${RAW_STATUS_MAX_CHARS} characters ...`;
    }
    rawNode.textContent = rendered;
  }

  function updateRawStatusError(detail) {
    const panel = ensureRawStatusPreview();
    if (!panel) return;

    const rawNode = panel.querySelector('[data-bind="v7.raw_status_preview"]');
    if (!rawNode) return;

    rawNode.textContent = JSON.stringify(
      {
        status_source: STATUS_ENDPOINT,
        error: text(detail, "status fetch failed"),
        request_id: state.lastRequestId,
      },
      null,
      2
    );
  }

  function latestJobLabel(data) {
    const job = data && data.latest_job;
    if (!job) return "not available";
    const action = [job.subsystem, job.action].filter(Boolean).join(".");
    const status = job.status || "unknown";
    const jobId = job.job_id || "no-id";
    return `${status} · ${action || "command"} · ${jobId}`;
  }

  function presetLabel(data) {
    const observationMeta = data && data.observation && data.observation.observation_meta;
    const presetApply = observationMeta && observationMeta.preset_apply;
    if (presetApply) {
      return presetApply.name || presetApply.preset_name || presetApply.applied_preset || "preset linked";
    }

    const latestJob = data && data.latest_job;
    const result = latestJob && latestJob.result;
    if (result && result.applied_preset) {
      return result.applied_preset;
    }

    return "not linked";
  }

  function exposureFromObservation(observation) {
    if (!observation) return {};
    return observation.armed_exposure || observation.last_exposure || {};
  }

  function detectorProfile(data) {
    return data && data.detector_config && data.detector_config.profile_name;
  }

  function saveEnabledLabel(data) {
    const detectorConfig = data && data.detector_config;
    if (detectorConfig && detectorConfig.save_enabled !== undefined) {
      return detectorConfig.save_enabled ? "yes" : "no";
    }

    const observation = data && data.observation;
    if (observation && observation.save_enabled !== undefined) {
      return observation.save_enabled ? "yes" : "no";
    }

    return "unknown";
  }

  function calibrationLabel(data) {
    const calibration = data && data.calibration;
    if (!calibration) return "not available";

    const mode = calibration.mode || "unknown";
    const lamp = calibration.active_lamp || "no lamp";
    const enabled = calibration.lamp_enabled ? "on" : "off";
    return `${mode} · ${lamp} · ${enabled}`;
  }

  function operationalLabel(data) {
    const operational = data && data.operational_status;
    if (!operational) {
      return data && data.state && data.state.overall_state;
    }
    return operational.level || operational.state || operational.summary || operational.status || "available";
  }

  function connectionStatus(ok, detail) {
    if (ok) {
      const ageMs = state.lastOkAt ? Date.now() - state.lastOkAt : 0;
      const stale = ageMs > STALE_AFTER_MS;
      if (stale) {
        return {
          level: "stale",
          label: `STALE · last ok ${Math.round(ageMs / 1000)}s ago`,
        };
      }
      return { level: "ok", label: "CONNECTED" };
    }
    return {
      level: "error",
      label: `ERROR · ${detail || "status fetch failed"}`,
    };
  }

  function formatClock(date) {
    if (!date) return "not yet";
    return date.toLocaleTimeString("zh-CN", { hour12: false });
  }

  function updateRail(message) {
    const railBody = document.querySelector(".rail span");
    if (!railBody) return;
    railBody.textContent = message;
  }

  function updateSetupReadiness(data, connection) {
    ensureSetupReadinessPanel();

    const observation = data && data.observation;
    const runMode = data && data.run_mode;
    const operational = operationalLabel(data);
    const exposureState = observation && observation.state;
    const detector = detectorProfile(data) || "not available";
    const calibration = calibrationLabel(data);
    const preset = presetLabel(data);
    const latestJob = latestJobLabel(data);
    const saveEnabled = saveEnabledLabel(data);

    setBoundText("v7.setup.connection", connection && connection.label, "unknown");
    setBoundText("v7.setup.run_mode", runMode, "unknown");
    setBoundText("v7.setup.operational", operational, "unknown");
    setBoundText("v7.setup.observation_state", exposureState, "unknown");
    setBoundText("v7.setup.detector_profile", detector, "not available");
    setBoundText("v7.setup.calibration", calibration, "not available");
    setBoundText("v7.setup.preset_context", preset, "not linked");
    setBoundText("v7.setup.save_enabled", saveEnabled, "unknown");
    setBoundText("v7.setup.latest_job", latestJob, "not available");
    setBoundText("v7.setup.request_id", state.lastRequestId, "not available");
  }

  function updateSetupReadinessError(connection) {
    ensureSetupReadinessPanel();
    setBoundText("v7.setup.connection", connection && connection.label, "error");
    setBoundText("v7.setup.request_id", state.lastRequestId, "not available");
  }

  function bindStatus(data) {
    ensureRuntimePanel();

    const observation = data && data.observation;
    const exposure = exposureFromObservation(observation);
    const connection = connectionStatus(true);
    const runMode = data && data.run_mode;
    const operational = operationalLabel(data);
    const exposureState = observation && observation.state;
    const detector = detectorProfile(data) || "not available";
    const calibration = calibrationLabel(data);
    const preset = presetLabel(data);
    const latestJob = latestJobLabel(data);
    const lastError = data && data.latest_error_code ? data.latest_error_code : "none";

    setTextById("run-mode", upper(runMode, "UNKNOWN"));
    setTextById("operational-level", upper(operational, "UNKNOWN"));
    setTextById("exposure-state", upper(exposureState, "UNKNOWN"));

    setConnectionState(connection.level, connection.label);
    document.querySelectorAll('[data-bind="v7.connection"]').forEach((node) => {
      node.setAttribute("data-level", connection.level);
    });
    setBoundText("v7.run_mode", runMode, "unknown");
    setBoundText("v7.operational", operational, "unknown");
    setBoundText("v7.exposure_state", exposureState, "unknown");
    setBoundText("v7.detector_profile", detector, "not available");
    setBoundText("v7.calibration", calibration, "not available");
    setBoundText("v7.preset_context", preset, "not linked");
    setBoundText("v7.latest_job", latestJob, "not available");
    setBoundText("v7.request_id", state.lastRequestId, "not available");
    setBoundText("v7.last_error", lastError, "none");
    setBoundText("v7.status_source", STATUS_ENDPOINT, STATUS_ENDPOINT);
    setBoundText("v7.last_ok", formatClock(new Date(state.lastOkAt)), "not yet");
    updateSetupReadiness(data, connection);
    updateRawStatusPreview(data);

    const exposureTime = exposure.exp_time_s !== undefined ? `${exposure.exp_time_s} s` : "not armed";
    updateRail(
      `v7 status bound to ${STATUS_ENDPOINT}. Exposure: ${text(exposureState, "unknown")} / ${exposureTime}. Detector: ${detector}. Calibration: ${calibration}. Latest job: ${latestJob}.`
    );
  }

  function bindConnectionError(detail) {
    const connection = connectionStatus(false, detail);
    setConnectionState(connection.level, connection.label);
    document.querySelectorAll('[data-bind="v7.connection"]').forEach((node) => {
      node.setAttribute("data-level", connection.level);
    });
    setBoundText("v7.request_id", state.lastRequestId, "not available");
    updateSetupReadinessError(connection);
    updateRawStatusError(detail);
    updateRail(connection.label);
  }

  async function fetchStatus() {
    try {
      const response = await fetch(STATUS_ENDPOINT, {
        headers: {
          "Accept": "application/json",
          "X-Requested-With": "JUSTLS-v7-operator-console",
        },
        cache: "no-store",
      });

      state.lastRequestId = response.headers.get("X-Request-ID") || state.lastRequestId;

      if (!response.ok) {
        bindConnectionError(`HTTP ${response.status}`);
        return;
      }

      const data = await response.json();
      state.lastOkAt = Date.now();
      bindStatus(data);
    } catch (error) {
      bindConnectionError(error && error.message);
    }
  }

  function startPolling() {
    ensureRuntimePanel();
    ensureSetupReadinessPanel();
    ensureRawStatusPreview();

    if (state.pollTimer) {
      window.clearInterval(state.pollTimer);
    }

    fetchStatus();
    state.pollTimer = window.setInterval(fetchStatus, POLL_INTERVAL_MS);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startPolling, { once: true });
  } else {
    startPolling();
  }
})();
