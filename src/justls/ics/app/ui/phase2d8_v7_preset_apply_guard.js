// Phase 2.8-E guarded preset apply add-on for the v7 operator console.
//
// This script intentionally does not duplicate preset catalog or preview
// loading. It observes the Runtime Presets panel created by
// phase2d8_v7_status_binding.js and only enables apply after a successful
// preview is visible. High-risk / confirmation-required presets require an
// explicit checkbox and exact preset-name text confirmation before POSTing to
// the existing /api/v1/presets/apply endpoint.

(function () {
  "use strict";

  const PRESET_APPLY_ENDPOINT = "/api/v1/presets/apply";
  const PREVIEW_BIND_SELECTOR = '[data-bind="v7.presets.preview"]';
  const STATUS_BIND_SELECTOR = '[data-bind="v7.presets.status"]';

  const state = {
    preview: null,
    applying: false,
  };

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback;
    return String(value);
  }

  function runtimePanel() {
    return document.getElementById("v7-presets-runtime");
  }

  function setPresetStatus(message) {
    const status = document.querySelector(STATUS_BIND_SELECTOR);
    if (status) status.textContent = message;
  }

  function updateRail(message) {
    const railBody = document.querySelector(".rail span");
    if (railBody) railBody.textContent = message;
  }

  function addStyles() {
    if (document.getElementById("v7-preset-apply-guard-style")) return;

    const style = document.createElement("style");
    style.id = "v7-preset-apply-guard-style";
    style.textContent = `
      .v7-preset-apply-guard {
        border: 1px solid #bb7777;
        background: #fff7f7;
        padding: 10px;
        margin-top: 10px;
      }
      .v7-preset-apply-guard[data-ready="true"] {
        border-color: #8fc6ae;
        background: #f4fff8;
      }
      .v7-preset-apply-guard h3 {
        margin: 0 0 8px;
        font-size: 13px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
      }
      .v7-preset-apply-guard .guard-note {
        color: var(--muted);
        font-size: 12px;
        line-height: 1.45;
        margin-bottom: 8px;
      }
      .v7-preset-apply-guard .guard-grid {
        display: grid;
        grid-template-columns: 150px minmax(0, 1fr);
        gap: 6px 10px;
        font-size: 12px;
        margin-bottom: 8px;
      }
      .v7-preset-apply-guard .guard-grid dt {
        color: var(--muted);
      }
      .v7-preset-apply-guard .guard-grid dd {
        margin: 0;
        overflow-wrap: anywhere;
      }
      .v7-preset-apply-guard .guard-confirm {
        display: grid;
        gap: 8px;
        margin: 8px 0;
      }
      .v7-preset-apply-guard .guard-confirm[hidden] {
        display: none;
      }
      .v7-preset-apply-guard input[type="text"] {
        width: 100%;
        border: 1px solid var(--border-soft);
        padding: 7px 8px;
        font: inherit;
        font-size: 12px;
      }
      .v7-preset-apply-guard label {
        display: flex;
        align-items: center;
        gap: 6px;
        color: var(--text);
        text-transform: none;
        letter-spacing: 0;
        font-size: 12px;
      }
      .v7-preset-apply-guard pre {
        max-height: 220px;
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
    `;
    document.head.appendChild(style);
  }

  function ensureGuardPanel() {
    const existing = document.getElementById("v7-preset-apply-guard");
    if (existing) return existing;

    const host = runtimePanel();
    if (!host) return null;

    addStyles();

    const body = host.querySelector(".panel-body") || host;
    const panel = document.createElement("section");
    panel.id = "v7-preset-apply-guard";
    panel.className = "v7-preset-apply-guard";
    panel.setAttribute("data-phase", "2.8-E");
    panel.setAttribute("data-ready", "false");
    panel.setAttribute("aria-label", "guarded preset apply control");

    panel.innerHTML = `
      <h3>Guarded Apply · Preview Required</h3>
      <div class="guard-note">
        Apply is guarded in Phase 2.8-E. You must preview a preset first. Confirmation-required presets also require the exact preset name and an explicit checkbox before calling the existing backend apply endpoint.
      </div>
      <dl class="guard-grid">
        <dt>Previewed Preset</dt><dd><code data-bind="v7.presets.apply_guard.name">none</code></dd>
        <dt>Risk</dt><dd><code data-bind="v7.presets.apply_guard.risk">unknown</code></dd>
        <dt>Requires Confirmation</dt><dd><code data-bind="v7.presets.apply_guard.confirmation">unknown</code></dd>
        <dt>Blocked</dt><dd><code data-bind="v7.presets.apply_guard.blocked">unknown</code></dd>
      </dl>
      <div class="guard-confirm" data-role="high-risk-confirmation" hidden>
        <label><input type="checkbox" data-role="confirm-risk-checkbox" /> I understand this preset requires confirmation.</label>
        <input type="text" data-role="confirm-preset-name" placeholder="Type exact preset name to confirm" autocomplete="off" />
      </div>
      <div class="preset-actions">
        <button class="btn primary" type="button" data-action="apply-previewed-preset" disabled>Apply Previewed Preset</button>
      </div>
      <pre data-bind="v7.presets.apply_result">No apply request sent.</pre>
    `;

    body.appendChild(panel);

    panel.querySelector('[data-action="apply-previewed-preset"]').addEventListener("click", applyPreviewedPreset);
    panel.querySelectorAll('[data-role="confirm-risk-checkbox"], [data-role="confirm-preset-name"]').forEach((node) => {
      node.addEventListener("input", refreshGuardPanel);
      node.addEventListener("change", refreshGuardPanel);
    });

    return panel;
  }

  function setGuardText(bindName, value) {
    const panel = ensureGuardPanel();
    if (!panel) return;
    const node = panel.querySelector(`[data-bind="${bindName}"]`);
    if (node) node.textContent = text(value, "unknown");
  }

  function parsePreviewPayload() {
    const previewNode = document.querySelector(PREVIEW_BIND_SELECTOR);
    if (!previewNode) return null;

    const raw = previewNode.textContent.trim();
    if (!raw || raw === "Select Preview for a preset." || raw === "loading preview...") return null;

    try {
      const payload = JSON.parse(raw);
      if (!payload || !payload.preset) return null;
      return payload;
    } catch (_error) {
      return null;
    }
  }

  function currentConfirmationState(panel, preview) {
    if (!preview) return false;
    if (!preview.requires_confirmation) return true;

    const checkbox = panel.querySelector('[data-role="confirm-risk-checkbox"]');
    const nameInput = panel.querySelector('[data-role="confirm-preset-name"]');
    return Boolean(checkbox && checkbox.checked && nameInput && nameInput.value === preview.preset);
  }

  function refreshGuardPanel() {
    const panel = ensureGuardPanel();
    if (!panel) return;

    const preview = parsePreviewPayload();
    state.preview = preview;

    const name = preview && preview.preset;
    const requiresConfirmation = Boolean(preview && preview.requires_confirmation);
    const blocked = Boolean(preview && preview.blocked);
    const canConfirm = currentConfirmationState(panel, preview);
    const ready = Boolean(preview && name && !blocked && canConfirm);

    setGuardText("v7.presets.apply_guard.name", name || "none");
    setGuardText("v7.presets.apply_guard.risk", preview && preview.risk_level ? preview.risk_level : "unknown");
    setGuardText("v7.presets.apply_guard.confirmation", preview ? (requiresConfirmation ? "yes" : "no") : "unknown");
    setGuardText("v7.presets.apply_guard.blocked", preview ? (blocked ? text(preview.blocked_reason, "blocked") : "no") : "unknown");

    const confirmBlock = panel.querySelector('[data-role="high-risk-confirmation"]');
    if (confirmBlock) confirmBlock.hidden = !requiresConfirmation;

    const button = panel.querySelector('[data-action="apply-previewed-preset"]');
    if (button) {
      button.disabled = !ready || state.applying;
      button.textContent = state.applying ? "Applying..." : "Apply Previewed Preset";
      button.setAttribute("data-ready", ready ? "true" : "false");
    }

    panel.setAttribute("data-ready", ready ? "true" : "false");
  }

  async function applyPreviewedPreset() {
    const panel = ensureGuardPanel();
    const preview = state.preview || parsePreviewPayload();
    if (!panel || !preview || !preview.preset || preview.blocked) {
      refreshGuardPanel();
      return;
    }

    if (!currentConfirmationState(panel, preview)) {
      refreshGuardPanel();
      return;
    }

    const confirmed = Boolean(preview.requires_confirmation);
    const resultNode = panel.querySelector('[data-bind="v7.presets.apply_result"]');

    state.applying = true;
    refreshGuardPanel();
    setPresetStatus(`applying ${preview.preset} via ${PRESET_APPLY_ENDPOINT}...`);
    if (resultNode) resultNode.textContent = "sending guarded apply request...";

    try {
      const response = await fetch(PRESET_APPLY_ENDPOINT, {
        method: "POST",
        headers: {
          "Accept": "application/json",
          "Content-Type": "application/json",
          "X-Requested-With": "JUSTLS-v7-preset-apply-guard",
        },
        cache: "no-store",
        body: JSON.stringify({ name: preview.preset, confirmed: confirmed }),
      });
      const payload = await response.json();
      if (resultNode) resultNode.textContent = JSON.stringify(payload, null, 2);
      setPresetStatus(response.ok ? `apply completed for ${preview.preset}` : `ERROR · apply HTTP ${response.status}`);
      updateRail(response.ok ? `Preset apply completed: ${preview.preset}.` : `Preset apply failed: ${preview.preset}.`);
    } catch (error) {
      const payload = { error: text(error && error.message, "preset apply failed"), preset: preview.preset };
      if (resultNode) resultNode.textContent = JSON.stringify(payload, null, 2);
      setPresetStatus(`ERROR · ${payload.error}`);
      updateRail(`Preset apply failed: ${preview.preset}.`);
    } finally {
      state.applying = false;
      refreshGuardPanel();
    }
  }

  function start() {
    ensureGuardPanel();
    refreshGuardPanel();

    const observer = new MutationObserver(refreshGuardPanel);
    const host = runtimePanel() || document.body;
    observer.observe(host, { childList: true, subtree: true, characterData: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();
