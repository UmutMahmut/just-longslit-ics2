// v7 opt-in observe runtime adapter.
// Injected only when JUSTLS_UI_V7_RUNTIME_ENABLED=1.

(function () {
  "use strict";

  const STATUS_ENDPOINT = "/api/v1/observation/status";
  const ARM_ENDPOINT = "/api/v1/observation/arm";
  const START_ENDPOINT = "/api/v1/observation/start";
  const STOP_READOUT_ENDPOINT = "/api/v1/observation/stop_readout";
  const ABORT_DISCARD_ENDPOINT = "/api/v1/observation/abort_discard";

  const state = {
    busy: false,
    lastStatus: null,
  };

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback;
    return String(value);
  }

  function page() {
    return document.querySelector('[data-page-panel="observe"]');
  }

  function setText(node, value) {
    if (!node) return;
    const next = text(value, "");
    if (node.textContent !== next) node.textContent = next;
  }

  function ensurePanel() {
    let panel = document.getElementById("v7-observe-controls");
    if (panel) return panel;

    const host = page();
    if (!host) return null;

    panel = document.createElement("section");
    panel.id = "v7-observe-controls";
    panel.className = "panel";
    panel.setAttribute("data-phase", "2.8-runtime-opt-in");
    panel.innerHTML = `
      <h2>Runtime Observe Controls · Single Exposure Only</h2>
      <div class="panel-body grid">
        <div class="field-grid">
          <label>Exposure Time (s)<input type="number" min="0.001" step="0.001" value="30" data-role="obs-exp-time" /></label>
          <label>Frame Type<select data-role="obs-frame-type"><option value="science">science</option><option value="flat">flat</option><option value="arc">arc</option><option value="test">test</option></select></label>
          <label style="grid-column: 1 / -1;">Operator Note<textarea data-role="obs-operator-note" placeholder="Optional note"></textarea></label>
        </div>
        <div class="badge-row">
          <button class="btn primary" type="button" data-action="obs-arm">Arm</button>
          <button class="btn primary" type="button" data-action="obs-start">Start</button>
          <button class="btn" type="button" data-action="obs-stop-readout">Stop & Readout</button>
          <button class="btn danger" type="button" data-action="obs-abort-discard">Abort & Discard</button>
        </div>
        <label><input type="checkbox" data-role="obs-abort-confirm" /> Enable abort/discard command</label>
        <dl class="kv">
          <dt>Status Endpoint</dt><dd><code>${STATUS_ENDPOINT}</code></dd>
          <dt>Observation State</dt><dd><code data-bind="v7.observe.state">unknown</code></dd>
          <dt>Armed Exposure</dt><dd><code data-bind="v7.observe.armed">not armed</code></dd>
          <dt>Last Command</dt><dd><code data-bind="v7.observe.last_command">none</code></dd>
        </dl>
        <pre data-bind="v7.observe.result">No observation command sent.</pre>
      </div>`;
    host.insertBefore(panel, host.firstChild);

    panel.querySelector('[data-action="obs-arm"]').addEventListener("click", arm);
    panel.querySelector('[data-action="obs-start"]').addEventListener("click", () => postCommand("start", START_ENDPOINT));
    panel.querySelector('[data-action="obs-stop-readout"]').addEventListener("click", () => postCommand("stop_readout", STOP_READOUT_ENDPOINT));
    panel.querySelector('[data-action="obs-abort-discard"]').addEventListener("click", abortDiscard);
    return panel;
  }

  function bind(name) {
    const panel = ensurePanel();
    return panel ? panel.querySelector(`[data-bind="${name}"]`) : null;
  }

  function setBusy(value) {
    state.busy = value;
    const panel = ensurePanel();
    if (!panel) return;
    panel.querySelectorAll("button[data-action]").forEach((button) => {
      button.disabled = value;
    });
  }

  function readArmPayload() {
    const panel = ensurePanel();
    const expInput = panel.querySelector('[data-role="obs-exp-time"]');
    const frameInput = panel.querySelector('[data-role="obs-frame-type"]');
    const noteInput = panel.querySelector('[data-role="obs-operator-note"]');
    const expTime = Number(expInput && expInput.value);
    if (!Number.isFinite(expTime) || expTime <= 0) throw new Error("Exposure time must be greater than zero.");
    return {
      exp_time_s: expTime,
      frame_type: frameInput ? frameInput.value : "science",
      operator_note: noteInput && noteInput.value ? noteInput.value : null,
    };
  }

  function renderStatus(payload) {
    state.lastStatus = payload || {};
    const armed = state.lastStatus.armed_exposure || state.lastStatus.last_exposure || null;
    setText(bind("v7.observe.state"), state.lastStatus.state || state.lastStatus.observation_state || "unknown");
    setText(bind("v7.observe.armed"), armed ? `${armed.frame_type || "frame"} · ${armed.exp_time_s || "?"} s` : "not armed");
  }

  function renderResult(command, payload) {
    renderStatus(payload);
    setText(bind("v7.observe.last_command"), command);
    setText(bind("v7.observe.result"), JSON.stringify(payload, null, 2));
  }

  function renderError(command, error) {
    setText(bind("v7.observe.last_command"), command);
    setText(bind("v7.observe.result"), JSON.stringify({ command, error: text(error, "failed") }, null, 2));
  }

  async function refreshStatus() {
    ensurePanel();
    try {
      const response = await fetch(STATUS_ENDPOINT, { cache: "no-store", headers: { Accept: "application/json" } });
      const payload = await response.json();
      if (response.ok) renderStatus(payload);
      else renderError("status", `HTTP ${response.status}`);
    } catch (error) {
      renderError("status", error && error.message);
    }
  }

  async function postCommand(command, endpoint, body) {
    setBusy(true);
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        cache: "no-store",
        body: body ? JSON.stringify(body) : undefined,
      });
      const payload = await response.json();
      if (response.ok) renderResult(command, payload);
      else renderError(command, `HTTP ${response.status}: ${JSON.stringify(payload)}`);
    } catch (error) {
      renderError(command, error && error.message);
    } finally {
      setBusy(false);
      refreshStatus();
    }
  }

  async function arm() {
    try {
      await postCommand("arm", ARM_ENDPOINT, readArmPayload());
    } catch (error) {
      renderError("arm", error && error.message);
    }
  }

  async function abortDiscard() {
    const panel = ensurePanel();
    const confirm = panel.querySelector('[data-role="obs-abort-confirm"]');
    if (!confirm || !confirm.checked) {
      renderError("abort_discard", "Explicit checkbox is required.");
      return;
    }
    await postCommand("abort_discard", ABORT_DISCARD_ENDPOINT);
    confirm.checked = false;
  }

  function start() {
    ensurePanel();
    refreshStatus();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
})();
