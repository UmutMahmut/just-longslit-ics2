// Phase 2.8-C v7 status binding adapter.
// Scope:
//   - bind the v7 operator console prototype to /api/v1/status/full;
//   - keep the default /ui and /ui/v6 untouched;
//   - do not introduce new backend API requirements;
//   - preserve the live image preview area as a placeholder until a future
//     image/quicklook/data-watcher backend is intentionally added.

(function () {
  "use strict";

  const STATUS_ENDPOINT = "/api/v1/status/full";
  const POLL_INTERVAL_MS = 2000;
  const STALE_AFTER_MS = 6000;

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

  function setInputByLabel(labelText, value) {
    const labels = Array.from(document.querySelectorAll("label"));
    const label = labels.find((candidate) => {
      const firstText = Array.from(candidate.childNodes)
        .filter((node) => node.nodeType === Node.TEXT_NODE)
        .map((node) => node.textContent.trim())
        .join(" ");
      return firstText.toLowerCase() === labelText.toLowerCase();
    });
    if (!label) return;

    const field = label.querySelector("input, textarea, select");
    if (!field) return;
    field.value = text(value, field.value || "");
  }

  function setDescriptionValue(termText, value) {
    const terms = Array.from(document.querySelectorAll("dt"));
    const term = terms.find((candidate) => candidate.textContent.trim().toLowerCase() === termText.toLowerCase());
    if (!term) return;

    const valueNode = term.nextElementSibling;
    if (!valueNode || valueNode.tagName.toLowerCase() !== "dd") return;
    valueNode.textContent = text(value, "not available");
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

  function connectionLabel(ok, detail) {
    if (ok) {
      const ageMs = state.lastOkAt ? Date.now() - state.lastOkAt : 0;
      const stale = ageMs > STALE_AFTER_MS;
      return stale ? `STALE · last ok ${Math.round(ageMs / 1000)}s ago` : "CONNECTED";
    }
    return `ERROR · ${detail || "status fetch failed"}`;
  }

  function updateRail(message) {
    const railBody = document.querySelector(".rail span");
    if (!railBody) return;
    railBody.textContent = message;
  }

  function bindStatus(data) {
    const observation = data && data.observation;
    const exposure = exposureFromObservation(observation);

    setTextById("run-mode", upper(data && data.run_mode, "UNKNOWN"));
    setTextById("operational-level", upper(operationalLabel(data), "UNKNOWN"));
    setTextById("exposure-state", upper(observation && observation.state, "UNKNOWN"));

    setInputByLabel("Current Preset", presetLabel(data));
    setInputByLabel("Detector Profile", detectorProfile(data) || "not available");

    setDescriptionValue("Observation State", observation && observation.state);
    setDescriptionValue("Exposure Time", exposure.exp_time_s !== undefined ? `${exposure.exp_time_s} s` : "not armed");
    setDescriptionValue("Frame Type", exposure.frame_type || "not available");
    setDescriptionValue("Preset Context", presetLabel(data));
    setDescriptionValue("Latest Job", latestJobLabel(data));

    setDescriptionValue("Status Source", STATUS_ENDPOINT);
    setDescriptionValue("X-Request-ID", state.lastRequestId || "not available");
    setDescriptionValue("Last Error", data && data.latest_error_code ? data.latest_error_code : "none");

    const detector = detectorProfile(data) || "no detector profile";
    const calibration = calibrationLabel(data);
    const latestJob = latestJobLabel(data);
    updateRail(`v7 status bound to ${STATUS_ENDPOINT}. Detector: ${detector}. Calibration: ${calibration}. Latest job: ${latestJob}.`);
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
        updateRail(connectionLabel(false, `HTTP ${response.status}`));
        return;
      }

      const data = await response.json();
      state.lastOkAt = Date.now();
      bindStatus(data);
    } catch (error) {
      updateRail(connectionLabel(false, error && error.message));
    }
  }

  function startPolling() {
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
