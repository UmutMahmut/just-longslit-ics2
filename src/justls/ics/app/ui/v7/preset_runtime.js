// v7 opt-in preset runtime adapter.
// Injected only when JUSTLS_UI_V7_RUNTIME_ENABLED=1.

(function () {
  "use strict";

  const PRESETS_ENDPOINT = "/api/v1/presets";
  const PREVIEW_ENDPOINT = "/api/v1/presets/preview";
  const APPLY_ENDPOINT = "/api/v1/presets/apply";

  const state = {
    items: [],
    preview: null,
    applying: false,
  };

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback;
    return String(value);
  }

  function setText(node, value) {
    if (!node) return;
    const next = text(value, "");
    if (node.textContent !== next) node.textContent = next;
  }

  function page() {
    return document.querySelector('[data-page-panel="presets"]');
  }

  function ensurePanel() {
    let panel = document.getElementById("v7-presets-runtime");
    if (panel) return panel;

    const host = page();
    if (!host) return null;

    panel = document.createElement("section");
    panel.id = "v7-presets-runtime";
    panel.className = "panel";
    panel.setAttribute("data-phase", "2.8-runtime-opt-in");
    panel.innerHTML = `
      <h2>Runtime Presets · Catalog / Preview / Guarded Apply</h2>
      <div class="panel-body">
        <div class="badge demo" data-bind="v7.presets.status">loading preset catalog...</div>
        <table class="table" style="margin-top: 10px;">
          <thead><tr><th>Name</th><th>Category</th><th>Risk</th><th>Confirm</th><th>Action</th></tr></thead>
          <tbody data-bind="v7.presets.catalog"></tbody>
        </table>
        <h3>Preview Result</h3>
        <pre data-bind="v7.presets.preview">Select Preview for a preset.</pre>
        <h3>Guarded Apply</h3>
        <div data-role="v7-preset-confirmation" hidden>
          <label><input type="checkbox" data-role="confirm-risk-checkbox" /> I understand this preset requires confirmation.</label>
          <input data-role="confirm-preset-name" placeholder="Type exact preset name" />
        </div>
        <button class="btn primary" type="button" data-action="apply-previewed-preset" disabled>Apply Previewed Preset</button>
        <pre data-bind="v7.presets.apply_result">No apply request sent.</pre>
      </div>`;
    host.insertBefore(panel, host.firstChild);

    panel.querySelector('[data-action="apply-previewed-preset"]').addEventListener("click", applyPreviewedPreset);
    panel.querySelectorAll('[data-role="confirm-risk-checkbox"], [data-role="confirm-preset-name"]').forEach((node) => {
      node.addEventListener("input", refreshApplyGuard);
      node.addEventListener("change", refreshApplyGuard);
    });
    return panel;
  }

  function bind(name) {
    const panel = ensurePanel();
    return panel ? panel.querySelector(`[data-bind="${name}"]`) : null;
  }

  function renderCatalog() {
    const body = bind("v7.presets.catalog");
    if (!body) return;

    body.innerHTML = "";
    state.items.forEach((item) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td><code>${item.name}</code></td>
        <td>${item.category || "unknown"}</td>
        <td>${item.risk_level || "unknown"}</td>
        <td>${item.requires_confirmation ? "yes" : "no"}</td>
        <td><button class="btn" type="button" data-preset-name="${item.name}">Preview</button></td>`;
      row.querySelector("button").addEventListener("click", () => previewPreset(item.name));
      body.appendChild(row);
    });
  }

  async function fetchCatalog() {
    setText(bind("v7.presets.status"), `loading ${PRESETS_ENDPOINT}...`);
    try {
      const response = await fetch(PRESETS_ENDPOINT, { cache: "no-store", headers: { Accept: "application/json" } });
      const payload = await response.json();
      state.items = Array.isArray(payload.items) ? payload.items : [];
      renderCatalog();
      setText(bind("v7.presets.status"), `loaded ${state.items.length} presets`);
    } catch (error) {
      setText(bind("v7.presets.status"), `catalog error: ${text(error && error.message, "failed")}`);
    }
  }

  async function previewPreset(name) {
    setText(bind("v7.presets.status"), `previewing ${name}...`);
    try {
      const response = await fetch(PREVIEW_ENDPOINT, {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({ name, confirmed: false }),
      });
      const payload = await response.json();
      state.preview = payload;
      setText(bind("v7.presets.preview"), JSON.stringify(payload, null, 2));
      setText(bind("v7.presets.status"), response.ok ? `preview loaded for ${name}` : `preview error ${response.status}`);
    } catch (error) {
      state.preview = null;
      setText(bind("v7.presets.preview"), JSON.stringify({ preset: name, error: text(error && error.message, "failed") }, null, 2));
    }
    refreshApplyGuard();
  }

  function confirmationOk(panel) {
    if (!state.preview || !state.preview.requires_confirmation) return true;
    const checkbox = panel.querySelector('[data-role="confirm-risk-checkbox"]');
    const input = panel.querySelector('[data-role="confirm-preset-name"]');
    return Boolean(checkbox && checkbox.checked && input && input.value === state.preview.preset);
  }

  function refreshApplyGuard() {
    const panel = ensurePanel();
    if (!panel) return;
    const confirmBlock = panel.querySelector('[data-role="v7-preset-confirmation"]');
    const button = panel.querySelector('[data-action="apply-previewed-preset"]');
    const blocked = Boolean(state.preview && state.preview.blocked);
    const hasPreview = Boolean(state.preview && state.preview.preset);
    const needsConfirm = Boolean(state.preview && state.preview.requires_confirmation);
    if (confirmBlock) confirmBlock.hidden = !needsConfirm;
    if (button) button.disabled = state.applying || !hasPreview || blocked || !confirmationOk(panel);
  }

  async function applyPreviewedPreset() {
    const panel = ensurePanel();
    if (!panel || !state.preview || !state.preview.preset || !confirmationOk(panel)) return;
    state.applying = true;
    refreshApplyGuard();
    setText(bind("v7.presets.apply_result"), "sending guarded apply request...");
    try {
      const response = await fetch(APPLY_ENDPOINT, {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        cache: "no-store",
        body: JSON.stringify({ name: state.preview.preset, confirmed: Boolean(state.preview.requires_confirmation) }),
      });
      const payload = await response.json();
      setText(bind("v7.presets.apply_result"), JSON.stringify(payload, null, 2));
    } catch (error) {
      setText(bind("v7.presets.apply_result"), JSON.stringify({ error: text(error && error.message, "failed") }, null, 2));
    } finally {
      state.applying = false;
      refreshApplyGuard();
    }
  }

  function start() {
    ensurePanel();
    fetchCatalog();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
})();
