// Phase 2.8-F guarded single-exposure observe controls for /ui/v7.
//
// Scope:
//   - bind only existing single-exposure observation endpoints;
//   - do not introduce a sequence runner or observation-plan editor;
//   - keep the live image / latest exposure preview region untouched;
//   - keep the static Observe controls visibly secondary to this runtime panel.

(function () {
  "use strict";

  const OBS_STATUS_ENDPOINT = "/api/v1/observation/status";
  const OBS_ARM_ENDPOINT = "/api/v1/observation/arm";
  const OBS_START_ENDPOINT = "/api/v1/observation/start";
  const OBS_STOP_READOUT_ENDPOINT = "/api/v1/observation/stop_readout";
  const OBS_ABORT_DISCARD_ENDPOINT = "/api/v1/observation/abort_discard";

  const state = {
    busy: false,
    lastStatus: null,
  };

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback;
    return String(value);
  }

  function observePage() {
    return document.querySelector('[data-page-panel="observe"]');
  }

  function updateRail(message) {
    const railBody = document.querySelector(".rail span");
    if (railBody) railBody.textContent = message;
  }

  function setPanelText(bindName, value, fallback) {
    const panel = ensureObserveControlsPanel();
    if (!panel) return;
    panel.querySelectorAll(`[data-bind="${bindName}"]`).forEach((node) => {
      node.textContent = text(value, fallback);
    });
  }

  function addStyles() {
    if (document.getElementById("v7-observe-controls-style")) return;

    const style = document.createElement("style");
    style.id = "v7-observe-controls-style";
    style.textContent = `
      .v7-observe-controls {
        margin-bottom: 12px;
        border: 1px solid var(--border);
        background: linear-gradient(180deg, #ffffff, #f3f7fc);
      }
      .v7-observe-controls h2 {
        margin: 0;
        padding: 8px 10px;
        border-bottom: 1px solid var(--border-soft);
        background: linear-gradient(180deg, #f8fafc, #eef3f9);
        font-size: 13px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
      }
      .v7-observe-controls .observe-body {
        display: grid;
        grid-template-columns: minmax(300px, 0.9fr) minmax(0, 1.1fr);
        gap: 12px;
        padding: 10px;
      }
      .v7-observe-controls .hint {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.45;
        margin-bottom: 8px;
      }
      .v7-observe-controls .field-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 8px;
      }
      .v7-observe-controls label {
        display: grid;
        gap: 4px;
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
      }
      .v7-observe-controls input,
      .v7-observe-controls select,
      .v7-observe-controls textarea {
        border: 1px solid var(--border-soft);
        padding: 7px 8px;
        font: inherit;
        font-size: 12px;
        background: #ffffff;
        color: var(--text);
      }
      .v7-observe-controls textarea {
        min-height: 62px;
        resize: vertical;
        grid-column: 1 / -1;
      }
      .v7-observe-controls .observe-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
      }
      .v7-observe-controls .abort-confirm {
        display: flex;
        align-items: center;
        gap: 6px;
        margin-top: 8px;
        color: var(--red);
        text-transform: none;
        letter-spacing: 0;
        font-size: 12px;
      }
      .v7-observe-controls pre {
        max-height: 260px;
        overflow: auto;
        white-space: pre-wrap;
        word-break: break-word;
        font-size: 11px;
        line-height: 1.45;
        background: #0f172a;
        color: #e5edf8;
        border: 1px solid #334155;
        padding: 10px;
        margin: 8px 0 0;
      }
      .v7-static-observe-fallback-note {
        border: 1px solid #dab36f;
        background: #fff8e8;
        color: #9a5b00;
        padding: 8px 10px;
        margin: 0 0 12px;
        font-size: 12px;
        line-height: 1.45;
      }
      .v7-static-observe-fallback {
        border-color: #dab36f;
        background: #fffdf7;
      }
      @media (max-width: 960px) {
        .v7-observe-controls .observe-body { grid-template-columns: 1fr; }
        .v7-observe-controls .field-grid { grid-template-columns: 1fr; }
      }
    `;
    document.head.appendChild(style);
  }

  function markStaticObserveFallback() {
    const page = observePage();
    if (!page) return;

    const staticGrid = page.querySelector(".grid.grid-2-1");
    if (!staticGrid) return;

    staticGrid.setAttribute("data-role", "static-observe-fallback-grid");
    staticGrid.setAttribute("data-phase", "fallback-demo");

    if (!document.getElementById("v7-static-observe-fallback-note")) {
      const note = document.createElement("div");
      note.id = "v7-static-observe-fallback-note";
      note.className = "v7-static-observe-fallback-note";
      note.setAttribute("data-role", "static-observe-fallback-note");
      note.setAttribute("data-phase", "fallback-demo");
      note.textContent = "Static Observe panels below are fallback/demo reference only. Runtime single-exposure controls are shown in the Phase 2.8-F panel above. Live preview remains visible and is not rewired in this phase.";
      page.insertBefore(note, staticGrid);
    }

    staticGrid.querySelectorAll(":scope > .panel").forEach((panel, index) => {
      panel.classList.add("v7-static-observe-fallback");
      panel.setAttribute("data-phase", "fallback-demo");
      panel.setAttribute("data-role", index === 0 ? "static-live-preview-fallback" : "static-exposure-control-fallback");
    });

    staticGrid.querySelectorAll("button").forEach((button) => {
      button.disabled = true;
      button.setAttribute("data-phase", "fallback-demo");
      button.setAttribute("data-role", "static-observe-placeholder-action");
      button.setAttribute("title", "Use the Runtime Observe Controls panel for Phase 2.8-F single-exposure actions.");
    });
  }

  function ensureObserveControlsPanel() {
    const existing = document.getElementById("v7-observe-controls");
    if (existing) return existing;

    const page = observePage();
    if (!page) return null;

    addStyles();

    const panel = document.createElement("section");
    panel.id = "v7-observe-controls";
    panel.className = "v7-observe-controls";
    panel.setAttribute("aria-label", "v7 runtime single exposure controls");
    panel.setAttribute("data-phase", "2.8-F");

    panel.innerHTML = `
      <h2>Runtime Observe Controls · Single Exposure Only</h2>
      <div class="observe-body">
        <div>
          <div class="hint">Phase 2.8-F binds existing single-exposure endpoints only. No sequence runner, observation plan editor, or image backend is added here.</div>
          <div class="field-grid">
            <label>Exposure Time (s)<input type="number" min="0.001" step="0.001" value="30" data-role="obs-exp-time" /></label>
            <label>Frame Type<select data-role="obs-frame-type"><option value="science">science</option><option value="flat">flat</option><option value="arc">arc</option><option value="test">test</option></select></label>
            <label style="grid-column: 1 / -1;">Operator Note<textarea data-role="obs-operator-note" placeholder="Optional note for this armed exposure"></textarea></label>
          </div>
          <div class="observe-actions">
            <button class="btn primary" type="button" data-action="obs-arm">Arm</button>
            <button class="btn primary" type="button" data-action="obs-start">Start</button>
            <button class="btn" type="button" data-action="obs-stop-readout">Stop & Readout</button>
            <button class="btn danger" type="button" data-action="obs-abort-discard">Abort & Discard</button>
          </div>
          <label class="abort-confirm"><input type="checkbox" data-role="obs-abort-confirm" /> Enable abort/discard command</label>
        </div>
        <div>
          <dl class="kv">
            <dt>Status Endpoint</dt><dd><code>${OBS_STATUS_ENDPOINT}</code></dd>
            <dt>Observation State</dt><dd><code data-bind="v7.observe.state">unknown</code></dd>
            <dt>Armed Exposure</dt><dd><code data-bind="v7.observe.armed">not armed</code></dd>
            <dt>Last Command</dt><dd><code data-bind="v7.observe.last_command">none</code></dd>
          </dl>
          <pre data-bind="v7.observe.result">No observation command sent.</pre>
        </div>
      </div>
    `;

    page.insertBefore(panel, page.firstChild);

    panel.querySelector('[data-action="obs-arm"]').addEventListener("click", armObservation);
    panel.querySelector('[data-action="obs-start"]').addEventListener("click", () => postObservationCommand("start", OBS_START_ENDPOINT));
    panel.querySelector('[data-action="obs-stop-readout"]').addEventListener("click", () => postObservationCommand("stop_readout", OBS_STOP_READOUT_ENDPOINT));
    panel.querySelector('[data-action="obs-abort-discard"]').addEventListener("click", abortDiscardObservation);

    markStaticObserveFallback();
    return panel;
  }

  function setBusy(value) {
    state.busy = value;
    const panel = ensureObserveControlsPanel();
    if (!panel) return;
    panel.querySelectorAll("button[data-action]").forEach((button) => {
      button.disabled = value;
    });
    const abortButton = panel.querySelector('[data-action="obs-abort-discard"]');
    const abortConfirm = panel.querySelector('[data-role="obs-abort-confirm"]');
    if (abortButton && abortConfirm) abortButton.disabled = value || !abortConfirm.checked;
  }

  function readArmPayload() {
    const panel = ensureObserveControlsPanel();
    const expInput = panel && panel.querySelector('[data-role="obs-exp-time"]');
    const frameInput = panel && panel.querySelector('[data-role="obs-frame-type"]');
    const noteInput = panel && panel.querySelector('[data-role="obs-operator-note"]');

    const expTime = Number(expInput && expInput.value);
    if (!Number.isFinite(expTime) || expTime <= 0) {
      throw new Error("Exposure time must be greater than zero.");
    }

    return {
      exp_time_s: expTime,
      frame_type: frameInput ? frameInput.value : "science",
      operator_note: noteInput && noteInput.value ? noteInput.value : null,
    };
  }

  function renderObservationStatus(payload) {
    state.lastStatus = payload;
    const status = payload || {};
    const armed = status.armed_exposure || status.last_exposure || null;
    const armedLabel = armed ? `${armed.frame_type || "frame"} · ${armed.exp_time_s || "?"} s` : "not armed";

    setPanelText("v7.observe.state", status.state || status.observation_state || "unknown", "unknown");
    setPanelText("v7.observe.armed", armedLabel, "not armed");
  }

  function renderCommandResult(command, payload) {
    renderObservationStatus(payload);
    setPanelText("v7.observe.last_command", command, "none");
    setPanelText("v7.observe.result", JSON.stringify(payload, null, 2), "No observation command sent.");
    updateRail(`Observation command completed: ${command}.`);
  }

  function renderCommandError(command, detail) {
    const payload = { command: command, error: text(detail, "observation command failed") };
    setPanelText("v7.observe.last_command", command, "none");
    setPanelText("v7.observe.result", JSON.stringify(payload, null, 2), "observation command failed");
    updateRail(`Observation command failed: ${command}.`);
  }

  async function refreshObservationStatus() {
    ensureObserveControlsPanel();
    try {
      const response = await fetch(OBS_STATUS_ENDPOINT, {
        headers: { "Accept": "application/json", "X-Requested-With": "JUSTLS-v7-observe-controls" },
        cache: "no-store",
      });
      const payload = await response.json();
      if (response.ok) renderObservationStatus(payload);
      else renderCommandError("status", `HTTP ${response.status}`);
    } catch (error) {
      renderCommandError("status", error && error.message);
    }
  }

  async function postObservationCommand(command, endpoint, body) {
    setBusy(true);
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Accept": "application/json",
          "Content-Type": "application/json",
          "X-Requested-With": "JUSTLS-v7-observe-controls",
        },
        cache: "no-store",
        body: body ? JSON.stringify(body) : undefined,
      });
      const payload = await response.json();
      if (response.ok) renderCommandResult(command, payload);
      else renderCommandError(command, `HTTP ${response.status}: ${JSON.stringify(payload)}`);
    } catch (error) {
      renderCommandError(command, error && error.message);
    } finally {
      setBusy(false);
    }
  }

  async function armObservation() {
    try {
      const payload = readArmPayload();
      await postObservationCommand("arm", OBS_ARM_ENDPOINT, payload);
    } catch (error) {
      renderCommandError("arm", error && error.message);
    }
  }

  async function abortDiscardObservation() {
    const panel = ensureObserveControlsPanel();
    const confirm = panel && panel.querySelector('[data-role="obs-abort-confirm"]');
    if (!confirm || !confirm.checked) {
      renderCommandError("abort_discard", "Abort/discard requires the explicit checkbox.");
      return;
    }
    await postObservationCommand("abort_discard", OBS_ABORT_DISCARD_ENDPOINT);
    confirm.checked = false;
    setBusy(false);
  }

  function start() {
    const panel = ensureObserveControlsPanel();
    if (!panel) return;

    const abortConfirm = panel.querySelector('[data-role="obs-abort-confirm"]');
    if (abortConfirm) abortConfirm.addEventListener("change", () => setBusy(state.busy));

    setBusy(false);
    refreshObservationStatus();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();
