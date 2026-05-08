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

  function requestIdFrom(response) {
    return response.headers.get("x-request-id") || response.headers.get("X-Request-ID") || runtime.lastRequestId;
  }

  function setRuntimeState(value) {
    setText(bind("v7.instrument.runtime_state"), value);
  }

  function setBusy(value) {
    runtime.busy = value;
    const host = panel();
    if (host) {
      host.querySelectorAll("button[data-action]").forEach((button) => {
        button.disabled = value;
      });
      host.setAttribute("data-runtime-busy", value ? "true" : "false");
    }
    setRuntimeState(value ? "command in flight" : "ready");
  }

  function renderResult(command, payload) {
    runtime.lastCommand = command;
    runtime.lastResult = payload;
    runtime.lastError = null;
    setText(bind("v7.instrument.last_command"), command);
    setText(bind("v7.instrument.request_id"), runtime.lastRequestId || "not available");
    setText(bind("v7.instrument.last_error"), "none");
    setText(bind("v7.instrument.result"), JSON.stringify({ command, request_id: runtime.lastRequestId, payload }, null, 2));
    window.dispatchEvent(new CustomEvent("justls:v7-local-refresh", { detail: { source: "instrument", command } }));
  }

  function renderError(command, error) {
    runtime.lastCommand = command;
    runtime.lastError = text(error, "failed");
    setText(bind("v7.instrument.last_command"), command || "none");
    setText(bind("v7.instrument.request_id"), runtime.lastRequestId || "not available");
    setText(bind("v7.instrument.last_error"), runtime.lastError);
    setText(bind("v7.instrument.result"), JSON.stringify({ command, request_id: runtime.lastRequestId, error: runtime.lastError }, null, 2));
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
    const host = panel();
    const input = host && host.querySelector(`[data-role="${role}"]`);
    const value = Number(input && input.value);
    if (!Number.isFinite(value)) throw new Error(`${label} must be a number.`);
    return value;
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

  function bindEvents() {
    bindButton("instrument-set-slit-width", () => {
      try {
        postJson("set_slit_width", SLIT_ENDPOINT, { width_um: readNumber("instrument-slit-width-um", "Slit width") });
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
      const host = panel();
      const select = host && host.querySelector('[data-role="instrument-calibration-mode"]');
      postJson("set_calibration_mode", CALIBRATION_MODE_ENDPOINT, { mode: select ? select.value : "science" });
    });
    bindButton("instrument-set-calibration-lamp", () => {
      const host = panel();
      const select = host && host.querySelector('[data-role="instrument-calibration-lamp"]');
      const enabled = host && host.querySelector('[data-role="instrument-calibration-lamp-enabled"]');
      postJson("set_calibration_lamp", CALIBRATION_LAMP_ENDPOINT, { lamp: select ? select.value : "flat", enabled: Boolean(enabled && enabled.checked) });
    });
    bindButton("instrument-refresh-calibration", () => getJson("refresh_calibration", CALIBRATION_STATUS_ENDPOINT, updateCalibrationFields));
    bindButton("instrument-refresh-detector-config", () => getJson("refresh_detector_config", DETECTOR_CONFIG_ENDPOINT, updateDetectorFields));
  }

  function start() {
    const host = panel();
    if (!host) return;
    host.setAttribute("data-runtime", "enabled");
    bindEvents();
    setRuntimeState("ready");
    getJson("refresh_calibration", CALIBRATION_STATUS_ENDPOINT, updateCalibrationFields);
    getJson("refresh_detector_config", DETECTOR_CONFIG_ENDPOINT, updateDetectorFields);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
})();
