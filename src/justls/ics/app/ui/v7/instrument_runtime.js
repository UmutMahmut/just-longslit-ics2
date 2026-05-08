// v7 opt-in Instrument runtime adapter.
// Injected only when JUSTLS_UI_V7_RUNTIME_ENABLED=1 and
// JUSTLS_UI_V7_INSTRUMENT_RUNTIME_ENABLED=1.

(function () {
  "use strict";

  const GLOBAL_KEY = "__JUSTLS_V7_INSTRUMENT_RUNTIME__";
  const SLIT_ENDPOINT = "/api/v1/slit";
  const SLIT_ANGLE_ENDPOINT = "/api/v1/slit_angle";
  const CALIBRATION_STATUS_ENDPOINT = "/api/v1/calibration/status";
  const CALIBRATION_MODE_ENDPOINT = "/api/v1/calibration/mode";
  const CALIBRATION_LAMP_ENDPOINT = "/api/v1/calibration/lamp";
  const DETECTOR_CONFIG_ENDPOINT = "/api/v1/detector/config";

  const SLIT_UM_PER_ARCSEC = 128.34;
  const COMMON_SLIT_WIDTH_ARCSEC = [1.0, 1.5, 2.0, 3.0];

  const runtime = window[GLOBAL_KEY] || {
    started: false,
    busy: false,
    lastCommand: null,
    lastResult: null,
    lastError: null,
    lastRequestId: null,
  };
  window[GLOBAL_KEY] = runtime;

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback;
    return String(value);
  }

  function panel() {
    return document.getElementById("v7-instrument-controls");
  }

  function setText(node, value) {
    if (!node) return;
    const next = text(value, "");
    if (node.textContent !== next) node.textContent = next;
  }

  function bind(name) {
    const host = panel();
    return host ? host.querySelector(`[data-bind="${name}"]`) || document.querySelector(`[data-bind="${name}"]`) : document.querySelector(`[data-bind="${name}"]`);
  }

  function byRole(role) {
    const host = panel();
    return host && host.querySelector(`[data-role="${role}"]`);
  }

  function requestIdFrom(response) {
    return response.headers.get("x-request-id") || response.headers.get("X-Request-ID") || runtime.lastRequestId;
  }

  function umFromArcsec(arcsec) {
    return arcsec * SLIT_UM_PER_ARCSEC;
  }

  function arcsecFromUm(um) {
    return um / SLIT_UM_PER_ARCSEC;
  }

  function formatNumber(value, digits) {
    if (!Number.isFinite(value)) return "";
    return Number(value.toFixed(digits)).toString();
  }

  function ensurePanelLayout() {
    const host = panel();
    if (!host || host.querySelector('[data-role="instrument-slit-width-arcsec"]')) return host;

    host.innerHTML = `
      <h2>Instrument Controls · Slit / Calibration / Detector Visibility</h2>
      <div class="panel-body grid">
        <div class="phase-note"><strong>H9.1:</strong> Existing backend capabilities are visible here. Slit width uses arcsec for operator intent and um for backend commands. Runtime remains opt-in; backend state-machine guards remain authoritative.</div>

        <section class="panel" data-role="instrument-slit-controls">
          <h3>Slit Controls</h3>
          <div class="panel-body">
            <div class="field-grid">
              <label>Slit Width (arcsec)<input type="number" min="0.001" step="0.001" value="1.0" data-role="instrument-slit-width-arcsec" /></label>
              <label>Slit Width (um)<input type="number" min="0.001" step="0.001" value="128.34" data-role="instrument-slit-width-um" /></label>
              <label>Slit Angle (deg)<input type="number" min="-90" max="90" step="0.001" value="0" data-role="instrument-slit-angle-deg" /></label>
              <button class="btn primary" type="button" data-action="instrument-set-slit-width" disabled>Set Slit Width</button>
              <button class="btn" type="button" data-action="instrument-set-slit-angle" disabled>Set Slit Angle</button>
            </div>
            <div class="badge-row" data-role="instrument-slit-shortcuts" aria-label="common slit width shortcuts">
              <span class="badge future">1 arcsec = <code data-bind="v7.instrument.slit.conversion_um_per_arcsec">128.34</code> um</span>
              <button class="btn" type="button" data-role="instrument-slit-shortcut" data-arcsec="1.0" disabled>1.0 arcsec</button>
              <button class="btn" type="button" data-role="instrument-slit-shortcut" data-arcsec="1.5" disabled>1.5 arcsec</button>
              <button class="btn" type="button" data-role="instrument-slit-shortcut" data-arcsec="2.0" disabled>2.0 arcsec</button>
              <button class="btn" type="button" data-role="instrument-slit-shortcut" data-arcsec="3.0" disabled>3.0 arcsec</button>
              <span class="badge demo">design range 0.5-5.0 arcsec</span>
            </div>
          </div>
        </section>

        <section class="panel" data-role="instrument-calibration-controls">
          <h3>Calibration Controls</h3>
          <div class="panel-body">
            <div class="field-grid">
              <label>Calibration Mode<select data-role="instrument-calibration-mode"><option value="science">science</option><option value="calibration">calibration</option></select></label>
              <label>Calibration Lamp<select data-role="instrument-calibration-lamp"><option value="flat">flat</option><option value="arc_hgar">arc_hgar</option><option value="arc_ne">arc_ne</option></select></label>
              <label><input type="checkbox" data-role="instrument-calibration-lamp-enabled" checked /> Enable selected lamp</label>
              <button class="btn" type="button" data-action="instrument-set-calibration-mode" disabled>Set Calibration Mode</button>
              <button class="btn" type="button" data-action="instrument-set-calibration-lamp" disabled>Set Calibration Lamp</button>
              <button class="btn" type="button" data-action="instrument-refresh-calibration" disabled>Refresh Calibration</button>
            </div>
            <div class="badge-row">
              <span class="badge live">flat source</span>
              <span class="badge live">Hg(Ar)</span>
              <span class="badge live">Ne</span>
              <span class="badge future">ThAr / FeAr possible</span>
              <span class="badge future">mirror path details deferred</span>
            </div>
          </div>
        </section>

        <section class="panel" data-role="instrument-detector-visibility">
          <h3>Detector Visibility · Read-only</h3>
          <div class="panel-body">
            <button class="btn" type="button" data-action="instrument-refresh-detector-config" disabled>Refresh Detector Config</button>
            <dl class="kv">
              <dt>Endpoint</dt><dd><code>/api/v1/detector/config</code></dd>
              <dt>Write Control</dt><dd><code>deferred</code></dd>
              <dt>B/G/R Hardware</dt><dd><code>visibility only in H9.1</code></dd>
            </dl>
          </div>
        </section>

        <section class="panel" data-role="instrument-command-summary">
          <h3>Command Summary</h3>
          <div class="panel-body">
            <dl class="kv">
              <dt>Last Command</dt><dd><code data-bind="v7.instrument.last_command">none</code></dd>
              <dt>Request ID</dt><dd><code data-bind="v7.instrument.request_id">not available</code></dd>
              <dt>Last Error</dt><dd><code data-bind="v7.instrument.last_error">none</code></dd>
              <dt>Runtime State</dt><dd><code data-bind="v7.instrument.runtime_state">static fallback</code></dd>
              <dt>Summary</dt><dd><code data-bind="v7.instrument.result_summary">runtime not enabled</code></dd>
            </dl>
          </div>
        </section>

        <details class="panel" data-role="instrument-raw-debug">
          <summary>Raw Result JSON · Diagnostics Detail</summary>
          <pre data-bind="v7.instrument.result">Instrument runtime is opt-in. Raw command result JSON is kept here for diagnostics.</pre>
        </details>
      </div>`;
    return host;
  }

  function setRuntimeState(value) {
    setText(bind("v7.instrument.runtime_state"), value);
  }

  function setBusy(value) {
    runtime.busy = value;
    const host = panel();
    if (host) {
      host.querySelectorAll("button[data-action], button[data-role='instrument-slit-shortcut']").forEach((button) => {
        button.disabled = value;
      });
      host.setAttribute("data-runtime-busy", value ? "true" : "false");
    }
    setRuntimeState(value ? "command in flight" : "ready");
  }

  function resultSummary(command, payload) {
    if (!payload || typeof payload !== "object") return `${command}: done`;
    if (command === "set_slit_width") {
      const widthUm = payload.width_um || payload.slit_width_um || payload.width;
      if (Number.isFinite(Number(widthUm))) return `set_slit_width: ${formatNumber(arcsecFromUm(Number(widthUm)), 3)} arcsec / ${formatNumber(Number(widthUm), 3)} um`;
    }
    if (command === "set_slit_angle") return `set_slit_angle: ${payload.angle_deg || payload.slit_angle_deg || payload.angle || "accepted"} deg`;
    if (command === "set_calibration_mode") return `set_calibration_mode: ${payload.mode || payload.calibration_mode || "accepted"}`;
    if (command === "set_calibration_lamp") return `set_calibration_lamp: ${payload.lamp || payload.active_lamp || "accepted"}`;
    if (command === "refresh_detector_config") return `refresh_detector_config: ${payload.profile_name || "profile visible"}`;
    if (command === "refresh_calibration") return `refresh_calibration: ${payload.mode || payload.calibration_mode || "status visible"}`;
    return `${command}: done`;
  }

  function renderResult(command, payload) {
    runtime.lastCommand = command;
    runtime.lastResult = payload;
    runtime.lastError = null;
    setText(bind("v7.instrument.last_command"), command);
    setText(bind("v7.instrument.request_id"), runtime.lastRequestId || "not available");
    setText(bind("v7.instrument.last_error"), "none");
    setText(bind("v7.instrument.result_summary"), resultSummary(command, payload));
    setText(bind("v7.instrument.result"), JSON.stringify({ command, request_id: runtime.lastRequestId, payload }, null, 2));
    window.dispatchEvent(new CustomEvent("justls:v7-local-refresh", { detail: { source: "instrument", command } }));
  }

  function renderError(command, error) {
    runtime.lastCommand = command;
    runtime.lastError = text(error, "failed");
    setText(bind("v7.instrument.last_command"), command || "none");
    setText(bind("v7.instrument.request_id"), runtime.lastRequestId || "not available");
    setText(bind("v7.instrument.last_error"), runtime.lastError);
    setText(bind("v7.instrument.result_summary"), `${command || "command"}: ${runtime.lastError}`);
    setText(bind("v7.instrument.result"), JSON.stringify({ command, request_id: runtime.lastRequestId, error: runtime.lastError }, null, 2));
  }

  function updateSlitFieldsFromUm(widthUm) {
    const value = Number(widthUm);
    if (!Number.isFinite(value) || value <= 0) return;
    const arcsec = arcsecFromUm(value);
    const arcInput = byRole("instrument-slit-width-arcsec");
    const umInput = byRole("instrument-slit-width-um");
    if (arcInput) arcInput.value = formatNumber(arcsec, 3);
    if (umInput) umInput.value = formatNumber(value, 3);
    setText(document.querySelector('[data-bind="v7.instrument.slit.width_current"]'), `${formatNumber(arcsec, 3)} arcsec / ${formatNumber(value, 3)} um`);
  }

  function updateCalibrationFields(payload) {
    if (!payload || typeof payload !== "object") return;
    const mode = payload.mode || payload.calibration_mode;
    const activeLamp = payload.active_lamp || payload.lamp || payload.selected_lamp;
    const lamps = payload.lamps || payload.lamp_states || {};
    setText(document.querySelector('[data-bind="v7.instrument.calibration.mode"]'), mode || "unknown");
    setText(document.querySelector('[data-bind="v7.instrument.calibration.flat"]'), text(lamps.flat, activeLamp === "flat" ? "enabled" : "unknown"));
    setText(document.querySelector('[data-bind="v7.instrument.calibration.arc"]'), activeLamp ? `${activeLamp}` : "unknown");
  }

  function updateDetectorFields(payload) {
    if (!payload || typeof payload !== "object") return;
    setText(document.querySelector('[data-bind="v7.instrument.detector.profile"]'), payload.profile_name || "unknown");
    setText(document.querySelector('[data-bind="v7.instrument.detector.save_enabled"]'), payload.save_enabled === undefined ? "unknown" : String(payload.save_enabled));
    setText(document.querySelector('[data-bind="v7.instrument.detector.trigger_mode"]'), payload.trigger_mode || "unknown");
    setText(document.querySelector('[data-bind="v7.instrument.detector.readout_mode"]'), payload.readout_mode || "unknown");
    const channels = payload.channels || payload.channel_state || {};
    ["B", "G", "R"].forEach((channel) => {
      const data = channels[channel] || channels[channel.toLowerCase()] || {};
      setText(document.querySelector(`[data-bind="v7.instrument.channel.${channel}.enabled"]`), data.enabled === undefined ? "visible" : String(data.enabled));
      setText(document.querySelector(`[data-bind="v7.instrument.channel.${channel}.role"]`), data.role || `science_${channel.toLowerCase()}`);
    });
  }

  async function fetchJson(endpoint, options) {
    const response = await fetch(endpoint, options);
    runtime.lastRequestId = requestIdFrom(response);
    const payload = await response.json();
    if (!response.ok) throw new Error(`HTTP ${response.status}: ${JSON.stringify(payload)}`);
    return payload;
  }

  async function postJson(command, endpoint, body) {
    if (runtime.busy) return;
    setBusy(true);
    try {
      const payload = await fetchJson(endpoint, {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify(body),
      });
      if (command === "set_slit_width") updateSlitFieldsFromUm(body.width_um);
      if (command === "set_calibration_mode" || command === "set_calibration_lamp") updateCalibrationFields(payload);
      renderResult(command, payload);
    } catch (error) {
      renderError(command, error && error.message);
    } finally {
      setBusy(false);
    }
  }

  async function getJson(command, endpoint, onPayload) {
    if (runtime.busy) return;
    setBusy(true);
    try {
      const payload = await fetchJson(endpoint, { cache: "no-store", headers: { Accept: "application/json" } });
      if (onPayload) onPayload(payload);
      renderResult(command, payload);
    } catch (error) {
      renderError(command, error && error.message);
    } finally {
      setBusy(false);
    }
  }

  function readNumber(role, label) {
    const input = byRole(role);
    const value = Number(input && input.value);
    if (!Number.isFinite(value)) throw new Error(`${label} must be a number.`);
    return value;
  }

  function readSlitWidthUm() {
    const arcInput = byRole("instrument-slit-width-arcsec");
    const umInput = byRole("instrument-slit-width-um");
    const arcsec = Number(arcInput && arcInput.value);
    if (Number.isFinite(arcsec) && arcsec > 0) {
      const widthUm = umFromArcsec(arcsec);
      if (umInput) umInput.value = formatNumber(widthUm, 3);
      return widthUm;
    }
    const widthUm = Number(umInput && umInput.value);
    if (!Number.isFinite(widthUm) || widthUm <= 0) throw new Error("Slit width must be greater than zero.");
    if (arcInput) arcInput.value = formatNumber(arcsecFromUm(widthUm), 3);
    return widthUm;
  }

  function action(name) {
    const host = panel();
    return host && host.querySelector(`[data-action="${name}"]`);
  }

  function bindButton(name, handler) {
    const button = action(name);
    if (!button || button.dataset.bound) return;
    button.dataset.bound = "true";
    button.disabled = false;
    button.addEventListener("click", handler);
  }

  function bindSlitUnitSync() {
    const arcInput = byRole("instrument-slit-width-arcsec");
    const umInput = byRole("instrument-slit-width-um");
    if (arcInput && !arcInput.dataset.bound) {
      arcInput.dataset.bound = "true";
      arcInput.addEventListener("input", () => {
        const arcsec = Number(arcInput.value);
        if (Number.isFinite(arcsec) && arcsec > 0 && umInput) umInput.value = formatNumber(umFromArcsec(arcsec), 3);
      });
    }
    if (umInput && !umInput.dataset.bound) {
      umInput.dataset.bound = "true";
      umInput.addEventListener("input", () => {
        const widthUm = Number(umInput.value);
        if (Number.isFinite(widthUm) && widthUm > 0 && arcInput) arcInput.value = formatNumber(arcsecFromUm(widthUm), 3);
      });
    }
    setText(bind("v7.instrument.slit.conversion_um_per_arcsec"), SLIT_UM_PER_ARCSEC);
  }

  function bindSlitShortcuts() {
    const host = panel();
    if (!host) return;
    host.querySelectorAll('[data-role="instrument-slit-shortcut"]').forEach((button) => {
      if (button.dataset.bound) return;
      button.dataset.bound = "true";
      button.disabled = false;
      button.addEventListener("click", () => {
        const arcsec = Number(button.dataset.arcsec);
        if (!Number.isFinite(arcsec) || !COMMON_SLIT_WIDTH_ARCSEC.includes(arcsec)) return;
        updateSlitFieldsFromUm(umFromArcsec(arcsec));
      });
    });
  }

  function bindEvents() {
    bindSlitUnitSync();
    bindSlitShortcuts();
    bindButton("instrument-set-slit-width", () => {
      try {
        postJson("set_slit_width", SLIT_ENDPOINT, { width_um: readSlitWidthUm() });
      } catch (error) {
        renderError("set_slit_width", error && error.message);
      }
    });
    bindButton("instrument-set-slit-angle", () => {
      try {
        postJson("set_slit_angle", SLIT_ANGLE_ENDPOINT, { angle_deg: readNumber("instrument-slit-angle-deg", "Slit angle") });
      } catch (error) {
        renderError("set_slit_angle", error && error.message);
      }
    });
    bindButton("instrument-set-calibration-mode", () => {
      const select = byRole("instrument-calibration-mode");
      postJson("set_calibration_mode", CALIBRATION_MODE_ENDPOINT, { mode: select ? select.value : "science" });
    });
    bindButton("instrument-set-calibration-lamp", () => {
      const select = byRole("instrument-calibration-lamp");
      const enabled = byRole("instrument-calibration-lamp-enabled");
      postJson("set_calibration_lamp", CALIBRATION_LAMP_ENDPOINT, { lamp: select ? select.value : "flat", enabled: Boolean(enabled && enabled.checked) });
    });
    bindButton("instrument-refresh-calibration", () => getJson("refresh_calibration", CALIBRATION_STATUS_ENDPOINT, updateCalibrationFields));
    bindButton("instrument-refresh-detector-config", () => getJson("refresh_detector_config", DETECTOR_CONFIG_ENDPOINT, updateDetectorFields));
  }

  function start() {
    const host = ensurePanelLayout();
    if (!host) return;
    host.setAttribute("data-runtime", "enabled");
    bindEvents();
    setRuntimeState("ready");
    updateSlitFieldsFromUm(SLIT_UM_PER_ARCSEC);
    getJson("refresh_calibration", CALIBRATION_STATUS_ENDPOINT, updateCalibrationFields);
    getJson("refresh_detector_config", DETECTOR_CONFIG_ENDPOINT, updateDetectorFields);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
})();
