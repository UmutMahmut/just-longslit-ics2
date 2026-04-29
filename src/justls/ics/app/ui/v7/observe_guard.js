// v7 opt-in observe button guard.
// This frontend-only guard does not call backend APIs.

(function () {
  "use strict";

  function text(value, fallback) {
    if (value === null || value === undefined || value === "") return fallback;
    return String(value);
  }

  function panel() {
    return document.getElementById("v7-observe-controls");
  }

  function currentState() {
    const node = document.querySelector('[data-bind="v7.observe.state"]');
    return text(node && node.textContent, "unknown").toLowerCase();
  }

  function armedLabel() {
    const node = document.querySelector('[data-bind="v7.observe.armed"]');
    return text(node && node.textContent, "not armed").toLowerCase();
  }

  function allowed() {
    const name = currentState();
    const armed = armedLabel() !== "not armed" || name.includes("armed");
    const active = name.includes("expos") || name.includes("integrat") || name.includes("running");
    const reading = name.includes("readout") || name.includes("reading");
    const ready = name === "unknown" || name.includes("idle") || name.includes("ready") || name.includes("complete") || name.includes("finish");
    return {
      "obs-arm": ready && !active && !reading,
      "obs-start": armed && !active && !reading,
      "obs-stop-readout": armed || active || reading,
      "obs-abort-discard": armed || active || reading,
    };
  }

  function setDisabled(button, value) {
    if (button && button.disabled !== value) button.disabled = value;
  }

  function refresh() {
    const host = panel();
    if (!host) return;
    const rules = allowed();
    const confirmed = Boolean(host.querySelector('[data-role="obs-abort-confirm"]:checked'));
    Object.entries(rules).forEach(([action, isAllowed]) => {
      const button = host.querySelector(`[data-action="${action}"]`);
      const finalAllowed = action === "obs-abort-discard" ? isAllowed && confirmed : isAllowed;
      setDisabled(button, !finalAllowed);
      if (button) button.setAttribute("data-guard-available", finalAllowed ? "true" : "false");
    });
  }

  function start() {
    const host = panel();
    if (!host) {
      window.setTimeout(start, 250);
      return;
    }
    const checkbox = host.querySelector('[data-role="obs-abort-confirm"]');
    if (checkbox) checkbox.addEventListener("change", refresh);
    const observer = new MutationObserver(() => window.setTimeout(refresh, 0));
    observer.observe(host, { childList: true, subtree: true, characterData: true });
    refresh();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, { once: true });
  else start();
})();
