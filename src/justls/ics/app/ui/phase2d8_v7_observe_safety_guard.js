// Phase 2.8-F conservative button-availability guard for v7 Observe.
//
// This is a narrow add-on that observes the Runtime Observe Controls panel
// created by phase2d8_v7_observe_controls.js. It does not call backend APIs
// and does not add any new observing capability. The backend remains the final
// authority for valid state transitions.

(function () {
  "use strict";

  const state = {
    refreshQueued: false,
  };

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback;
    return String(value);
  }

  function panel() {
    return document.getElementById("v7-observe-controls");
  }

  function stateText() {
    const node = document.querySelector('[data-bind="v7.observe.state"]');
    return text(node && node.textContent, "unknown").toLowerCase();
  }

  function armedText() {
    const node = document.querySelector('[data-bind="v7.observe.armed"]');
    return text(node && node.textContent, "not armed").toLowerCase();
  }

  function setTextIfChanged(node, value) {
    const next = text(value, "");
    if (node && node.textContent !== next) {
      node.textContent = next;
    }
  }

  function setAttributeIfChanged(node, name, value) {
    const next = text(value, "");
    if (node && node.getAttribute(name) !== next) {
      node.setAttribute(name, next);
    }
  }

  function setDisabledIfChanged(button, disabled) {
    if (button && button.disabled !== disabled) {
      button.disabled = disabled;
    }
  }

  function setStatus(message) {
    const host = panel();
    if (!host) return;

    let node = host.querySelector('[data-bind="v7.observe.guard"]');
    if (!node) {
      node = document.createElement("div");
      node.className = "hint";
      node.setAttribute("data-bind", "v7.observe.guard");
      node.setAttribute("data-phase", "2.8-F");
      const body = host.querySelector(".observe-body") || host;
      body.insertBefore(node, body.firstChild);
    }
    setTextIfChanged(node, message);
  }

  function allowedActions() {
    const name = stateText();
    const armed = armedText() !== "not armed" || name.includes("armed");
    const active = name.includes("expos") || name.includes("integrat") || name.includes("running");
    const reading = name.includes("readout") || name.includes("reading");
    const ready = name === "unknown" || name.includes("idle") || name.includes("ready") || name.includes("complete") || name.includes("finish") || name.includes("abort") || name.includes("discard");

    return {
      "obs-arm": ready && !active && !reading,
      "obs-start": armed && !active && !reading,
      "obs-stop-readout": armed || active || reading,
      "obs-abort-discard": armed || active || reading,
    };
  }

  function refreshButtons() {
    state.refreshQueued = false;

    const host = panel();
    if (!host) return;

    const rules = allowedActions();
    const explicitConfirm = Boolean(host.querySelector('[data-role="obs-abort-confirm"]:checked'));
    const labels = [];

    Object.entries(rules).forEach(([action, allowed]) => {
      const button = host.querySelector(`[data-action="${action}"]`);
      if (!button) return;

      const finalAllowed = action === "obs-abort-discard" ? allowed && explicitConfirm : allowed;
      setDisabledIfChanged(button, !finalAllowed);
      setAttributeIfChanged(button, "data-guard-available", finalAllowed ? "true" : "false");
      if (allowed) labels.push(action.replace("obs-", ""));
    });

    setStatus(`Phase 2.8-F guard: allowed actions from current visible state = ${labels.join(", ") || "none"}. Backend still validates final transitions.`);
  }

  function scheduleRefresh() {
    if (state.refreshQueued) return;
    state.refreshQueued = true;
    window.setTimeout(refreshButtons, 0);
  }

  function start() {
    const host = panel();
    if (!host) {
      window.setTimeout(start, 250);
      return;
    }

    const checkbox = host.querySelector('[data-role="obs-abort-confirm"]');
    if (checkbox) checkbox.addEventListener("change", scheduleRefresh);

    const observer = new MutationObserver(scheduleRefresh);
    observer.observe(host, { childList: true, subtree: true, characterData: true });
    scheduleRefresh();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();
