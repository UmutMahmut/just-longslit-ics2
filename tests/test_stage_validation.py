import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("src"))

from justls.ics.application.dispatcher import CommandDispatcher, validate_required_params
from justls.ics.application.services.health_service import HealthService
from justls.ics.application.services.management_service import ManagementService
from justls.ics.application.services.observation_service import ObservationService
from justls.ics.app.main import app
from justls.ics.domain.detector.config import DetectorConfig
from justls.ics.application.usecases.presets import (
    build_preset_config,
    build_preset_plan,
    list_presets,
)
from justls.ics.kernel.errors import (
    ErrorCode,
    InvalidParamError,
    InvalidStateError,
    UnsupportedError,
)
from justls.ics.kernel.jobs import CommandRequest, JobTracker
from justls.ics.kernel.runtime import RuntimeAssembler, RuntimeConfig, reset_runtime
from justls.ics.kernel.states import (
    CommandSource,
    ControlState,
    ExposureState,
    RunMode,
    build_initial_state,
)


@pytest.fixture(autouse=True)
def _reset_runtime_singleton():
    reset_runtime()
    yield
    reset_runtime()


def test_stage_2d2_initial_state_basics():
    state = build_initial_state(RunMode.SIM)
    data = state.to_dict()

    assert data["run_mode"] == "sim"
    assert data["overall_state"] == "disconnected"
    assert data["exposure_state"] == "ready_to_arm"
    assert "subsystems" in data
    assert data["subsystems"]["slit"]["state"] == "initializing"


def test_stage_2d2_error_code_basics():
    assert ErrorCode.OK.value == "ok"
    assert ErrorCode.INVALID_PARAM.value == "invalid_param"
    assert ErrorCode.UNSUPPORTED.value == "unsupported"


def test_stage_2d2_job_tracker_success_flow():
    tracker = JobTracker()

    req = CommandRequest.create(
        subsystem="slit",
        action="set_width",
        params={"width_um": 120.0},
        source=CommandSource.UI,
    )

    job = tracker.create_job(req, state_before="idle")
    tracker.mark_running(job.job_id)
    tracker.mark_succeeded(
        job.job_id,
        result={"width_um": 120.0},
        state_after="idle",
    )

    latest = tracker.latest_job()
    assert latest is not None
    assert latest.status.value == "succeeded"
    assert latest.result["width_um"] == 120.0
    assert latest.state_before == "idle"
    assert latest.state_after == "idle"


def test_stage_2d2_runtime_status_dict():
    runtime = RuntimeAssembler(RuntimeConfig(run_mode=RunMode.SIM)).build()
    status = runtime.status_dict()

    assert status["app_name"] == "JUST Long-Slit ICS 2.0"
    assert status["version"] == "0.0.1"
    assert status["run_mode"] == "sim"
    assert status["latest_job"] is None


def test_stage_2d2_runtime_has_slit_lamps_detector_and_capabilities():
    runtime = RuntimeAssembler().build()
    caps = runtime.get_capabilities_dict()

    assert runtime.slit is not None
    assert runtime.lamps is not None
    assert runtime.detector is not None
    assert caps["slit"] is True
    assert caps["slit_angle"] is True
    assert caps["calib_lamps"] is True


def test_stage_2d2_runtime_default_detector_config_exists():
    runtime = RuntimeAssembler().build()
    cfg = runtime.get_detector_config_dict()

    assert cfg["profile_name"] == "default"
    assert cfg["save_enabled"] is True
    assert cfg["trigger_mode"] == "internal"
    assert cfg["readout_mode"] == "normal"
    assert "channels" in cfg
    assert set(cfg["channels"].keys()) == {"B", "G", "R"}


def test_stage_2d2_runtime_can_update_detector_config():
    runtime = RuntimeAssembler().build()

    updated = runtime.set_detector_config(
        {
            "profile_name": "rgb-safe-default",
            "save_enabled": True,
            "trigger_mode": "internal",
            "readout_mode": "normal",
            "channels": {
                "B": {"enabled": True, "camera_role": "science_b"},
                "G": {"enabled": False, "camera_role": "science_g"},
                "R": {"enabled": True, "camera_role": "science_r"},
            },
        }
    )

    assert updated.profile_name == "rgb-safe-default"
    cfg = runtime.get_detector_config_dict()
    assert cfg["channels"]["B"]["enabled"] is True
    assert cfg["channels"]["G"]["enabled"] is False
    assert cfg["channels"]["R"]["enabled"] is True


def test_stage_2d2_runtime_can_update_subsystem_state():
    runtime = RuntimeAssembler().build()

    runtime.set_subsystem_connected("slit", True, message="connected")
    runtime.set_subsystem_state("slit", ControlState.IDLE, message="ready")

    slit = runtime.get_subsystem_state("slit")
    assert slit.connected is True
    assert slit.state == ControlState.IDLE
    assert slit.message == "ready"


def test_stage_2d2_dispatcher_success_flow():
    runtime = RuntimeAssembler().build()
    runtime.set_subsystem_connected("slit", True)
    runtime.set_subsystem_state("slit", ControlState.IDLE)

    dispatcher = CommandDispatcher(runtime)

    def handler(rt, request):
        return {"width_um": request.params["width_um"]}

    dispatcher.register_handler("slit", "set_width", handler)

    req = CommandRequest.create(
        subsystem="slit",
        action="set_width",
        params={"width_um": 100.0},
        source=CommandSource.UI,
    )

    result = dispatcher.dispatch(req)
    data = result.to_dict()

    assert data["job"]["status"] == "succeeded"
    assert data["payload"]["width_um"] == 100.0
    assert runtime.get_subsystem_state("slit").state == ControlState.IDLE


def test_stage_2d2_dispatcher_unsupported_action():
    runtime = RuntimeAssembler().build()
    dispatcher = CommandDispatcher(runtime)

    req = CommandRequest.create(
        subsystem="slit",
        action="not_registered",
        params={},
        source=CommandSource.UI,
    )

    try:
        dispatcher.dispatch(req)
        assert False, "Expected UnsupportedError"
    except UnsupportedError as exc:
        assert exc.code == ErrorCode.UNSUPPORTED


def test_stage_2d2_validate_required_params():
    req = CommandRequest.create(
        subsystem="slit",
        action="set_width",
        params={},
        source=CommandSource.UI,
    )

    try:
        validate_required_params(req, {"width_um"})
        assert False, "Expected InvalidParamError"
    except InvalidParamError as exc:
        assert exc.code == ErrorCode.INVALID_PARAM


def test_stage_2d2_services_read_runtime_state_calibration_observation_and_detector_config():
    runtime = RuntimeAssembler().build()

    runtime.set_detector_config(
        {
            "profile_name": "rgb-safe-default",
            "save_enabled": True,
            "trigger_mode": "internal",
            "readout_mode": "normal",
            "channels": {
                "B": {"enabled": True, "camera_role": "science_b"},
                "G": {"enabled": False, "camera_role": "science_g"},
                "R": {"enabled": True, "camera_role": "science_r"},
            },
        }
    )

    health_service = HealthService(runtime)
    management_service = ManagementService(runtime)
    observation_service = ObservationService(runtime, CommandDispatcher(runtime))

    management_service.set_connected("slit", True, message="connected")
    management_service.set_state("slit", ControlState.IDLE, message="ready")
    runtime.slit.set_width_um(150.0)
    runtime.slit.set_angle_deg(10.0)

    runtime.lamps.set_mode("calibration")
    runtime.lamps.select_lamp("flat", enable=True)

    runtime.detector.arm(
        exp_time_s=5.0,
        frame_type="science",
        operator_note="service-check",
        instrument_snapshot={"slit_width_um": 150.0, "slit_angle_deg": 10.0},
        calibration_snapshot=runtime.lamps.get_snapshot().to_dict(),
        detector_config=runtime.get_detector_config_dict(),
    )
    runtime.set_exposure_state(ExposureState.ARMED)

    state_dto = health_service.get_state_dto()
    status_full = health_service.get_status_full()
    calibration = health_service.get_calibration_status()
    observation = health_service.get_observation_status()
    exposure = observation_service.get_exposure_status()

    assert state_dto["slit_width_um"] == 150.0
    assert state_dto["slit_angle_deg"] == 10.0
    assert state_dto["lamp_on"] is True

    assert status_full["capabilities"]["calib_lamps"] is True
    assert status_full["calibration"]["mode"] == "calibration"
    assert status_full["calibration"]["active_lamp"] == "flat"
    assert status_full["calibration"]["lamp_enabled"] is True
    assert status_full["calibration"]["mirror_inserted"] is True
    assert status_full["detector_config"]["profile_name"] == "rgb-safe-default"

    assert calibration["mode"] == "calibration"
    assert calibration["active_lamp"] == "flat"

    assert observation["state"] == "armed"
    assert observation["armed_exposure"]["frame_type"] == "science"
    assert observation["observation_meta"] is not None
    assert observation["observation_meta"]["operator_note"] == "service-check"
    assert observation["observation_meta"]["detector_config"]["profile_name"] == "rgb-safe-default"

    assert exposure["state"] == "armed"


def test_stage_2d2_management_service_detector_config_roundtrip():
    runtime = RuntimeAssembler().build()
    service = ManagementService(runtime)

    default_cfg = service.get_detector_config_dict()
    assert default_cfg["profile_name"] == "default"

    updated = service.set_detector_config(
        {
            "profile_name": "rgb-safe-default",
            "save_enabled": True,
            "trigger_mode": "internal",
            "readout_mode": "normal",
            "channels": {
                "B": {"enabled": True, "camera_role": "science_b"},
                "G": {"enabled": False, "camera_role": "science_g"},
                "R": {"enabled": True, "camera_role": "science_r"},
            },
        }
    )

    assert updated["profile_name"] == "rgb-safe-default"
    assert updated["channels"]["B"]["enabled"] is True
    assert service.get_detector_config_dict()["channels"]["R"]["enabled"] is True


def test_stage_2d2_management_service_apply_preset_plan_science():
    runtime = RuntimeAssembler().build()
    service = ManagementService(runtime)

    plan = build_preset_plan("science_default")
    result = service.apply_preset_plan(plan)

    assert result["applied_preset"] == "science_default"
    assert result["detector_config"]["profile_name"] == "science-default"
    assert result["calibration"]["mode"] == "science"
    assert result["calibration_applied"] is True
    assert result["slit_applied"] is False


def test_stage_2d2_management_service_apply_preset_plan_calib_flat():
    runtime = RuntimeAssembler().build()
    service = ManagementService(runtime)

    plan = build_preset_plan("calib_flat_default")
    result = service.apply_preset_plan(plan)

    assert result["applied_preset"] == "calib_flat_default"
    assert result["detector_config"]["profile_name"] == "calib-flat-default"
    assert result["calibration"]["mode"] == "calibration"
    assert result["calibration"]["active_lamp"] == "flat"
    assert result["calibration"]["lamp_enabled"] is True
    assert result["calibration_applied"] is True
    assert result["slit_applied"] is False


def test_stage_2d2_detector_config_model_defaults():
    cfg = DetectorConfig()
    data = cfg.to_dict()

    assert data["profile_name"] == "default"
    assert data["save_enabled"] is True
    assert data["trigger_mode"] == "internal"
    assert data["readout_mode"] == "normal"
    assert data["channels"]["B"]["camera_role"] == "science_b"
    assert data["channels"]["G"]["camera_role"] == "science_g"
    assert data["channels"]["R"]["camera_role"] == "science_r"


def test_stage_2d2_presets_catalog():
    items = list_presets()
    names = {item["name"] for item in items}

    assert "science_default" in names
    assert "rgb_safe_default" in names
    assert "engineering_all_channels_off" in names
    assert "calib_flat_default" in names


def test_stage_2d2_build_preset_plan_science_default():
    plan = build_preset_plan("science_default").to_dict()

    assert plan["name"] == "science_default"
    assert plan["detector_config"]["profile_name"] == "science-default"
    assert plan["calibration"]["mode"] == "science"
    assert plan["calibration"]["enabled"] is False
    assert plan["slit"] is None


def test_stage_2d2_build_preset_plan_calib_flat_default():
    plan = build_preset_plan("calib_flat_default").to_dict()

    assert plan["name"] == "calib_flat_default"
    assert plan["detector_config"]["profile_name"] == "calib-flat-default"
    assert plan["calibration"]["mode"] == "calibration"
    assert plan["calibration"]["lamp"] == "flat"
    assert plan["calibration"]["enabled"] is True


def test_stage_2d2_build_preset_config_science_default():
    cfg = build_preset_config("science_default").to_dict()

    assert cfg["profile_name"] == "science-default"
    assert cfg["channels"]["B"]["enabled"] is True
    assert cfg["channels"]["G"]["enabled"] is True
    assert cfg["channels"]["R"]["enabled"] is True


def test_stage_2d2_build_unknown_preset_raises():
    with pytest.raises(KeyError):
        build_preset_plan("not_exists")


def test_stage_2d2_lamps_legacy_on_off_flow():
    runtime = RuntimeAssembler().build()

    on_snapshot = runtime.lamps.set_legacy_on(True)
    assert on_snapshot.mode.value == "calibration"
    assert on_snapshot.active_lamp.value == "flat"
    assert on_snapshot.lamp_enabled is True
    assert on_snapshot.mirror_inserted is True

    off_snapshot = runtime.lamps.set_legacy_on(False)
    assert off_snapshot.mode.value == "science"
    assert off_snapshot.active_lamp is None
    assert off_snapshot.lamp_enabled is False
    assert off_snapshot.mirror_inserted is False


def test_stage_2d2_lamps_explicit_mode_and_lamp_flow():
    runtime = RuntimeAssembler().build()

    snap1 = runtime.lamps.set_mode("calibration")
    assert snap1.mode.value == "calibration"
    assert snap1.mirror_inserted is True
    assert snap1.lamp_enabled is False

    snap2 = runtime.lamps.select_lamp("arc_hgar", enable=True)
    assert snap2.mode.value == "calibration"
    assert snap2.active_lamp.value == "arc_hgar"
    assert snap2.lamp_enabled is True
    assert snap2.mirror_inserted is True

    snap3 = runtime.lamps.set_mode("science")
    assert snap3.mode.value == "science"
    assert snap3.active_lamp is None
    assert snap3.lamp_enabled is False
    assert snap3.mirror_inserted is False


def test_stage_2d2_detector_initial_snapshot():
    runtime = RuntimeAssembler().build()
    snap = runtime.detector.get_snapshot()

    assert snap.state == ExposureState.READY_TO_ARM
    assert snap.armed_exposure is None
    assert snap.last_exposure is None
    assert snap.observation_meta is None


def test_stage_2d2_detector_arm_creates_observation_meta():
    runtime = RuntimeAssembler().build()

    armed = runtime.detector.arm(
        exp_time_s=30.0,
        frame_type="science",
        operator_note="meta-test",
        instrument_snapshot={"slit_width_um": 120.0, "slit_angle_deg": 0.0},
        calibration_snapshot={"mode": "science", "active_lamp": None, "lamp_enabled": False, "mirror_inserted": False},
        detector_config=runtime.get_detector_config_dict(),
    )

    assert armed.state == ExposureState.ARMED
    assert armed.armed_exposure is not None
    assert armed.observation_meta is not None
    assert armed.observation_meta["frame_type"] == "science"
    assert armed.observation_meta["operator_note"] == "meta-test"
    assert armed.observation_meta["instrument_snapshot"]["slit_width_um"] == 120.0
    assert armed.observation_meta["detector_config"]["profile_name"] == "default"


def test_stage_2d2_detector_finish_normal_flow():
    runtime = RuntimeAssembler().build()

    runtime.detector.arm(
        exp_time_s=30.0,
        frame_type="science",
        operator_note="finish-case",
        instrument_snapshot={"slit_width_um": 120.0, "slit_angle_deg": 0.0},
        calibration_snapshot={"mode": "science", "active_lamp": None, "lamp_enabled": False, "mirror_inserted": False},
        detector_config=runtime.get_detector_config_dict(),
    )

    exposing = runtime.detector.start()
    assert exposing.state == ExposureState.EXPOSING
    assert exposing.observation_meta["state"] == "exposing"

    completed = runtime.detector.finish_normal()
    assert completed.state == ExposureState.COMPLETED
    assert completed.armed_exposure is None
    assert completed.last_exposure is not None
    assert completed.last_exposure["frame_type"] == "science"
    assert completed.last_exposure["result"] == "completed"
    assert completed.last_exposure["kept"] is True
    assert completed.last_exposure["early_stop"] is False
    assert completed.last_exposure["discarded"] is False
    assert completed.observation_meta is not None
    assert completed.observation_meta["state"] == "completed"
    assert len(completed.observation_meta["frame_results"]) == 1
    assert completed.observation_meta["frame_results"][0]["kept"] is True
    assert completed.observation_meta["frame_results"][0]["early_stop"] is False


def test_stage_2d2_detector_stop_readout_flow():
    runtime = RuntimeAssembler().build()

    runtime.detector.arm(
        exp_time_s=12.0,
        frame_type="flat",
        operator_note="early-stop",
        instrument_snapshot={"slit_width_um": 80.0, "slit_angle_deg": 2.0},
        calibration_snapshot={"mode": "science", "active_lamp": None, "lamp_enabled": False, "mirror_inserted": False},
        detector_config=runtime.get_detector_config_dict(),
    )
    runtime.detector.start()

    completed = runtime.detector.stop_and_readout()
    assert completed.state == ExposureState.COMPLETED
    assert completed.last_exposure is not None
    assert completed.last_exposure["kept"] is True
    assert completed.last_exposure["early_stop"] is True
    assert completed.last_exposure["discarded"] is False
    assert completed.observation_meta["state"] == "completed"
    assert completed.observation_meta["frame_results"][0]["early_stop"] is True


def test_stage_2d2_detector_abort_discard_flow():
    runtime = RuntimeAssembler().build()

    runtime.detector.arm(
        exp_time_s=10.0,
        frame_type="flat",
        operator_note="discard-case",
        instrument_snapshot={"slit_width_um": 80.0, "slit_angle_deg": 2.0},
        calibration_snapshot={"mode": "calibration", "active_lamp": "flat", "lamp_enabled": True, "mirror_inserted": True},
        detector_config=runtime.get_detector_config_dict(),
    )
    discarded = runtime.detector.abort_discard()

    assert discarded.state == ExposureState.DISCARDED
    assert discarded.armed_exposure is None
    assert discarded.last_exposure is not None
    assert discarded.last_exposure["frame_type"] == "flat"
    assert discarded.last_exposure["result"] == "discarded"
    assert discarded.last_exposure["kept"] is False
    assert discarded.last_exposure["early_stop"] is False
    assert discarded.last_exposure["discarded"] is True
    assert discarded.observation_meta["state"] == "discarded"
    assert discarded.observation_meta["frame_results"][0]["discarded"] is True


def test_stage_2d2_detector_invalid_start_before_arm():
    runtime = RuntimeAssembler().build()

    with pytest.raises(InvalidStateError):
        runtime.detector.start()


def test_stage_2d2_detector_invalid_finish_before_start():
    runtime = RuntimeAssembler().build()

    runtime.detector.arm(
        exp_time_s=5.0,
        frame_type="science",
        operator_note=None,
        instrument_snapshot=None,
        calibration_snapshot=None,
        detector_config=runtime.get_detector_config_dict(),
    )
    with pytest.raises(InvalidStateError):
        runtime.detector.finish_normal()


def test_stage_2d2_detector_invalid_stop_before_start():
    runtime = RuntimeAssembler().build()

    runtime.detector.arm(
        exp_time_s=5.0,
        frame_type="science",
        operator_note=None,
        instrument_snapshot=None,
        calibration_snapshot=None,
        detector_config=runtime.get_detector_config_dict(),
    )
    with pytest.raises(InvalidStateError):
        runtime.detector.stop_and_readout()


def test_stage_2d2_detector_invalid_abort_before_arm():
    runtime = RuntimeAssembler().build()

    with pytest.raises(InvalidStateError):
        runtime.detector.abort_discard()


def test_stage_2d2_api_root():
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "JUST Long-Slit ICS 2.0 is running."
    assert data["docs"] == "/docs"
    assert data["openapi"] == "/openapi.json"


def test_stage_2d2_api_health():
    client = TestClient(app)
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["service"] == "just-longslit-ics-2.0"
    assert "runtime" in data


def test_stage_2d2_api_status():
    client = TestClient(app)
    response = client.get("/api/v1/status")

    assert response.status_code == 200
    data = response.json()
    assert data["slit_width_um"] == 120.0
    assert data["slit_angle_deg"] == 0.0
    assert data["lamp_on"] is False
    assert data["temperature_c"] is None


def test_stage_2d2_api_status_full():
    client = TestClient(app)
    response = client.get("/api/v1/status/full")

    assert response.status_code == 200
    data = response.json()

    assert "state" in data
    assert "capabilities" in data
    assert "calibration" in data
    assert "observation" in data
    assert "detector_config" in data
    assert "hal" in data
    assert "run_mode" in data
    assert "timestamp_utc" in data
    assert data["state"]["slit_width_um"] == 120.0
    assert data["state"]["slit_angle_deg"] == 0.0
    assert data["state"]["lamp_on"] is False
    assert data["capabilities"]["slit"] is True
    assert data["capabilities"]["slit_angle"] is True
    assert data["capabilities"]["calib_lamps"] is True
    assert data["calibration"]["mode"] == "science"
    assert data["observation"]["state"] == "ready_to_arm"
    assert data["observation"]["observation_meta"] is None
    assert data["detector_config"]["profile_name"] == "default"


def test_stage_2d2_api_capabilities():
    client = TestClient(app)
    response = client.get("/api/v1/capabilities")

    assert response.status_code == 200
    data = response.json()

    assert data["slit"] is True
    assert data["slit_angle"] is True
    assert data["calib_lamps"] is True
    assert data["rotator"] is False
    assert data["slit_monitor_camera"] is False
    assert data["guider"] is False
    assert data["science_channels_bgr"] is False
    assert data["fast_photometry"] is False


def test_stage_2d2_api_get_detector_config():
    client = TestClient(app)

    response = client.get("/api/v1/detector/config")
    assert response.status_code == 200
    data = response.json()

    assert data["profile_name"] == "default"
    assert data["channels"]["B"]["camera_role"] == "science_b"
    assert data["channels"]["G"]["camera_role"] == "science_g"
    assert data["channels"]["R"]["camera_role"] == "science_r"


def test_stage_2d2_api_set_detector_config():
    client = TestClient(app)

    response = client.post(
        "/api/v1/detector/config",
        json={
            "profile_name": "rgb-safe-default",
            "save_enabled": True,
            "trigger_mode": "internal",
            "readout_mode": "normal",
            "channels": {
                "B": {"enabled": True, "camera_role": "science_b"},
                "G": {"enabled": False, "camera_role": "science_g"},
                "R": {"enabled": True, "camera_role": "science_r"},
            },
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["profile_name"] == "rgb-safe-default"
    assert data["channels"]["B"]["enabled"] is True
    assert data["channels"]["G"]["enabled"] is False
    assert data["channels"]["R"]["enabled"] is True

    readback = client.get("/api/v1/detector/config")
    assert readback.status_code == 200
    read_data = readback.json()
    assert read_data["profile_name"] == "rgb-safe-default"
    assert read_data["channels"]["R"]["enabled"] is True


def test_stage_2d2_api_detector_config_invalid_payload_returns_422():
    client = TestClient(app)

    response = client.post(
        "/api/v1/detector/config",
        json={
            "profile_name": "bad",
            "save_enabled": True,
            "trigger_mode": "invalid",
            "readout_mode": "normal",
            "channels": {
                "B": {"enabled": True, "camera_role": "science_b"},
                "G": {"enabled": False, "camera_role": "science_g"},
                "R": {"enabled": True, "camera_role": "science_r"},
            },
        },
    )
    assert response.status_code == 422


def test_stage_2d2_api_list_presets():
    client = TestClient(app)

    response = client.get("/api/v1/presets")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    names = {item["name"] for item in data["items"]}
    assert "science_default" in names
    assert "rgb_safe_default" in names
    assert "engineering_all_channels_off" in names
    assert "calib_flat_default" in names


def test_stage_2d2_api_apply_preset_science_default():
    client = TestClient(app)

    response = client.post("/api/v1/presets/apply", json={"name": "science_default"})
    assert response.status_code == 200
    data = response.json()

    assert data["applied_preset"] == "science_default"
    assert data["detector_config"]["profile_name"] == "science-default"
    assert data["detector_config"]["channels"]["B"]["enabled"] is True
    assert data["detector_config"]["channels"]["G"]["enabled"] is True
    assert data["detector_config"]["channels"]["R"]["enabled"] is True
    assert data["calibration"]["mode"] == "science"
    assert data["calibration"]["lamp_enabled"] is False
    assert data["calibration_applied"] is True
    assert data["slit_applied"] is False

    readback = client.get("/api/v1/detector/config")
    assert readback.status_code == 200
    cfg = readback.json()
    assert cfg["profile_name"] == "science-default"

    calib = client.get("/api/v1/calibration/status")
    assert calib.status_code == 200
    calib_data = calib.json()
    assert calib_data["mode"] == "science"
    assert calib_data["active_lamp"] is None
    assert calib_data["lamp_enabled"] is False


def test_stage_2d2_api_apply_preset_calib_flat_default():
    client = TestClient(app)

    response = client.post("/api/v1/presets/apply", json={"name": "calib_flat_default", "confirmed": True})
    assert response.status_code == 200
    data = response.json()

    assert data["applied_preset"] == "calib_flat_default"
    assert data["detector_config"]["profile_name"] == "calib-flat-default"
    assert data["calibration"]["mode"] == "calibration"
    assert data["calibration"]["active_lamp"] == "flat"
    assert data["calibration"]["lamp_enabled"] is True
    assert data["calibration_applied"] is True
    assert data["slit_applied"] is False

    calib = client.get("/api/v1/calibration/status")
    assert calib.status_code == 200
    calib_data = calib.json()
    assert calib_data["mode"] == "calibration"
    assert calib_data["active_lamp"] == "flat"
    assert calib_data["lamp_enabled"] is True
    assert calib_data["mirror_inserted"] is True


def test_stage_2d2_api_apply_unknown_preset_returns_404():
    client = TestClient(app)

    response = client.post("/api/v1/presets/apply", json={"name": "not_exists"})
    assert response.status_code == 404


def test_stage_2d2_api_observation_arm_reflects_applied_calib_preset():
    client = TestClient(app)

    preset = client.post(
        "/api/v1/presets/apply",
        json={"name": "calib_flat_default", "confirmed": True},
    )
    assert preset.status_code == 200

    response = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 6.0, "frame_type": "flat", "operator_note": "preset-calib-link"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["observation_meta"]["detector_config"]["profile_name"] == "calib-flat-default"
    assert data["observation_meta"]["calibration_snapshot"]["mode"] == "calibration"
    assert data["observation_meta"]["calibration_snapshot"]["active_lamp"] == "flat"
    assert data["observation_meta"]["calibration_snapshot"]["lamp_enabled"] is True


def test_stage_2d2_api_set_slit_width():
    client = TestClient(app)

    response = client.post("/api/v1/slit", json={"width_um": 220.0})
    assert response.status_code == 200
    data = response.json()
    assert data["slit_width_um"] == 220.0
    assert data["slit_angle_deg"] == 0.0

    status = client.get("/api/v1/status")
    assert status.status_code == 200
    status_data = status.json()
    assert status_data["slit_width_um"] == 220.0
    assert status_data["slit_angle_deg"] == 0.0


def test_stage_2d2_api_set_slit_angle():
    client = TestClient(app)

    response = client.post("/api/v1/slit_angle", json={"angle_deg": 12.5})
    assert response.status_code == 200
    data = response.json()
    assert data["slit_width_um"] == 120.0
    assert data["slit_angle_deg"] == 12.5

    status = client.get("/api/v1/status")
    assert status.status_code == 200
    status_data = status.json()
    assert status_data["slit_width_um"] == 120.0
    assert status_data["slit_angle_deg"] == 12.5


def test_stage_2d2_api_invalid_slit_width_returns_422():
    client = TestClient(app)
    response = client.post("/api/v1/slit", json={"width_um": 0})

    assert response.status_code == 422


def test_stage_2d2_api_invalid_slit_angle_returns_422():
    client = TestClient(app)
    response = client.post("/api/v1/slit_angle", json={"angle_deg": 120.0})

    assert response.status_code == 422


def test_stage_2d2_api_lamp_legacy_on_and_off():
    client = TestClient(app)

    on_response = client.post("/api/v1/lamp", json={"on": True})
    assert on_response.status_code == 200
    assert on_response.json()["lamp_on"] is True

    off_response = client.post("/api/v1/lamp", json={"on": False})
    assert off_response.status_code == 200
    assert off_response.json()["lamp_on"] is False


def test_stage_2d2_api_get_calibration_status():
    client = TestClient(app)

    response = client.get("/api/v1/calibration/status")
    assert response.status_code == 200
    data = response.json()

    assert data["mode"] == "science"
    assert data["active_lamp"] is None
    assert data["lamp_enabled"] is False
    assert data["mirror_inserted"] is False


def test_stage_2d2_api_set_calibration_mode_and_lamp():
    client = TestClient(app)

    response1 = client.post("/api/v1/calibration/mode", json={"mode": "calibration"})
    assert response1.status_code == 200
    assert response1.json()["mode"] == "calibration"

    response2 = client.post("/api/v1/calibration/lamp", json={"lamp": "flat", "enabled": True})
    assert response2.status_code == 200
    data = response2.json()

    assert data["mode"] == "calibration"
    assert data["active_lamp"] == "flat"
    assert data["lamp_enabled"] is True
    assert data["mirror_inserted"] is True

    legacy = client.get("/api/v1/status")
    assert legacy.json()["lamp_on"] is True


def test_stage_2d2_api_invalid_calibration_mode_returns_422():
    client = TestClient(app)
    response = client.post("/api/v1/calibration/mode", json={"mode": "invalid"})

    assert response.status_code == 422


def test_stage_2d2_api_invalid_calibration_lamp_returns_422():
    client = TestClient(app)
    response = client.post("/api/v1/calibration/lamp", json={"lamp": "invalid", "enabled": True})

    assert response.status_code == 422


def test_stage_2d2_api_observation_initial_status():
    client = TestClient(app)

    response = client.get("/api/v1/observation/status")
    assert response.status_code == 200
    data = response.json()

    assert data["state"] == "ready_to_arm"
    assert data["armed_exposure"] is None
    assert data["last_exposure"] is None
    assert data["observation_meta"] is None


def test_stage_2d2_api_observation_arm_includes_detector_config():
    client = TestClient(app)

    client.post(
        "/api/v1/detector/config",
        json={
            "profile_name": "rgb-safe-default",
            "save_enabled": True,
            "trigger_mode": "internal",
            "readout_mode": "normal",
            "channels": {
                "B": {"enabled": True, "camera_role": "science_b"},
                "G": {"enabled": False, "camera_role": "science_g"},
                "R": {"enabled": True, "camera_role": "science_r"},
            },
        },
    )

    response = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 15.0, "frame_type": "science", "operator_note": "detector-config-link"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["state"] == "armed"
    assert data["armed_exposure"] is not None
    assert data["armed_exposure"]["operator_note"] == "detector-config-link"
    assert data["observation_meta"] is not None
    assert data["observation_meta"]["detector_config"]["profile_name"] == "rgb-safe-default"
    assert data["observation_meta"]["detector_config"]["channels"]["B"]["enabled"] is True
    assert data["observation_meta"]["detector_config"]["channels"]["G"]["enabled"] is False
    assert data["observation_meta"]["detector_config"]["channels"]["R"]["enabled"] is True


def test_stage_2d2_api_observation_start_returns_exposing():
    client = TestClient(app)

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 20.0, "frame_type": "science", "operator_note": "api-meta-check"},
    )
    assert arm.status_code == 200

    response = client.post("/api/v1/observation/start")
    assert response.status_code == 200
    data = response.json()

    assert data["state"] == "exposing"
    assert data["armed_exposure"] is not None
    assert data["armed_exposure"]["frame_type"] == "science"
    assert data["last_exposure"] is None
    assert data["observation_meta"] is not None
    assert data["observation_meta"]["state"] == "exposing"
    assert data["observation_meta"]["started_at_utc"] is not None


def test_stage_2d2_api_observation_finish():
    client = TestClient(app)

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 20.0, "frame_type": "science", "operator_note": "api-meta-check"},
    )
    assert arm.status_code == 200

    start = client.post("/api/v1/observation/start")
    assert start.status_code == 200

    response = client.post("/api/v1/observation/finish")
    assert response.status_code == 200
    data = response.json()

    assert data["state"] == "completed"
    assert data["armed_exposure"] is None
    assert data["last_exposure"] is not None
    assert data["last_exposure"]["frame_type"] == "science"
    assert data["last_exposure"]["kept"] is True
    assert data["last_exposure"]["early_stop"] is False
    assert data["last_exposure"]["discarded"] is False
    assert data["observation_meta"] is not None
    assert data["observation_meta"]["state"] == "completed"
    assert len(data["observation_meta"]["frame_results"]) == 1
    assert data["observation_meta"]["frame_results"][0]["kept"] is True
    assert data["observation_meta"]["frame_results"][0]["early_stop"] is False


def test_stage_2d2_api_observation_stop_readout():
    client = TestClient(app)

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 8.0, "frame_type": "flat", "operator_note": "early-stop-case"},
    )
    assert arm.status_code == 200

    start = client.post("/api/v1/observation/start")
    assert start.status_code == 200

    response = client.post("/api/v1/observation/stop_readout")
    assert response.status_code == 200
    data = response.json()

    assert data["state"] == "completed"
    assert data["armed_exposure"] is None
    assert data["last_exposure"] is not None
    assert data["last_exposure"]["frame_type"] == "flat"
    assert data["last_exposure"]["kept"] is True
    assert data["last_exposure"]["early_stop"] is True
    assert data["last_exposure"]["discarded"] is False
    assert data["observation_meta"] is not None
    assert data["observation_meta"]["state"] == "completed"
    assert len(data["observation_meta"]["frame_results"]) == 1
    assert data["observation_meta"]["frame_results"][0]["kept"] is True
    assert data["observation_meta"]["frame_results"][0]["early_stop"] is True


def test_stage_2d2_api_observation_abort_discard():
    client = TestClient(app)

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 10.0, "frame_type": "flat", "operator_note": "discard-case"},
    )
    assert arm.status_code == 200

    response = client.post("/api/v1/observation/abort_discard")
    assert response.status_code == 200
    data = response.json()

    assert data["state"] == "discarded"
    assert data["armed_exposure"] is None
    assert data["last_exposure"] is not None
    assert data["last_exposure"]["frame_type"] == "flat"
    assert data["last_exposure"]["kept"] is False
    assert data["last_exposure"]["early_stop"] is False
    assert data["last_exposure"]["discarded"] is True
    assert data["observation_meta"] is not None
    assert data["observation_meta"]["state"] == "discarded"
    assert len(data["observation_meta"]["frame_results"]) == 1
    assert data["observation_meta"]["frame_results"][0]["discarded"] is True


def test_stage_2d2_api_observation_invalid_start_before_arm():
    client = TestClient(app)

    response = client.post("/api/v1/observation/start")
    assert response.status_code == 400


def test_stage_2d2_api_observation_invalid_finish_before_start():
    client = TestClient(app)

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 5.0, "frame_type": "science", "operator_note": "bad-finish"},
    )
    assert arm.status_code == 200

    response = client.post("/api/v1/observation/finish")
    assert response.status_code == 400


def test_stage_2d2_api_observation_invalid_stop_before_start():
    client = TestClient(app)

    response = client.post("/api/v1/observation/stop_readout")
    assert response.status_code == 400


def test_stage_2d2_api_observation_invalid_abort_before_arm():
    client = TestClient(app)

    response = client.post("/api/v1/observation/abort_discard")
    assert response.status_code == 400


def test_stage_2d2_api_status_full_reflects_observation_meta_and_detector_config():
    client = TestClient(app)

    client.post(
        "/api/v1/presets/apply",
        json={"name": "calib_flat_default", "confirmed": True},
    )

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 8.0, "frame_type": "flat", "operator_note": "full-status-check"},
    )
    assert arm.status_code == 200

    response = client.get("/api/v1/status/full")
    assert response.status_code == 200
    data = response.json()

    assert data["observation"]["state"] == "armed"
    assert data["observation"]["armed_exposure"] is not None
    assert data["observation"]["last_exposure"] is None
    assert data["observation"]["observation_meta"] is not None
    assert data["observation"]["observation_meta"]["operator_note"] == "full-status-check"
    assert data["observation"]["observation_meta"]["detector_config"]["profile_name"] == "calib-flat-default"
    assert data["observation"]["observation_meta"]["calibration_snapshot"]["mode"] == "calibration"
    assert data["observation"]["observation_meta"]["calibration_snapshot"]["active_lamp"] == "flat"
    assert data["detector_config"]["profile_name"] == "calib-flat-default"

def test_stage_2d2_openapi_presets_responses_are_typed():
    client = TestClient(app)
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    data = openapi.json()

    list_schema = data["paths"]["/api/v1/presets"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    apply_schema = data["paths"]["/api/v1/presets/apply"]["post"]["responses"]["200"]["content"]["application/json"]["schema"]

    assert "$ref" in list_schema
    assert list_schema["$ref"].endswith("/PresetListResponse")
    assert "$ref" in apply_schema
    assert apply_schema["$ref"].endswith("/PresetApplyResponse")


def test_stage_2d2_openapi_observation_responses_are_typed():
    client = TestClient(app)
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    data = openapi.json()

    status_schema = data["paths"]["/api/v1/observation/status"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    arm_schema = data["paths"]["/api/v1/observation/arm"]["post"]["responses"]["200"]["content"]["application/json"]["schema"]
    start_schema = data["paths"]["/api/v1/observation/start"]["post"]["responses"]["200"]["content"]["application/json"]["schema"]

    assert "$ref" in status_schema
    assert status_schema["$ref"].endswith("/ObservationStatusResponse")
    assert "$ref" in arm_schema
    assert arm_schema["$ref"].endswith("/ObservationStatusResponse")
    assert "$ref" in start_schema
    assert start_schema["$ref"].endswith("/ObservationStatusResponse")


def test_stage_2d2_openapi_response_components_include_new_models():
    client = TestClient(app)
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    data = openapi.json()

    schemas = data["components"]["schemas"]

    assert "PresetListResponse" in schemas
    assert "PresetApplyResponse" in schemas
    assert "ObservationStatusResponse" in schemas
def test_stage_2d2_openapi_system_and_detector_responses_are_typed():
    client = TestClient(app)
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    data = openapi.json()

    health_schema = data["paths"]["/api/v1/health"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    status_schema = data["paths"]["/api/v1/status"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    status_full_schema = data["paths"]["/api/v1/status/full"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    capabilities_schema = data["paths"]["/api/v1/capabilities"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    detector_get_schema = data["paths"]["/api/v1/detector/config"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    detector_post_schema = data["paths"]["/api/v1/detector/config"]["post"]["responses"]["200"]["content"]["application/json"]["schema"]

    assert "$ref" in health_schema
    assert health_schema["$ref"].endswith("/HealthResponse")

    assert "$ref" in status_schema
    assert status_schema["$ref"].endswith("/StateDtoResponse")

    assert "$ref" in status_full_schema
    assert status_full_schema["$ref"].endswith("/StatusFullResponse")

    assert "$ref" in capabilities_schema
    assert capabilities_schema["$ref"].endswith("/CapabilitiesResponse")

    assert "$ref" in detector_get_schema
    assert detector_get_schema["$ref"].endswith("/DetectorConfig-Output")

    assert "$ref" in detector_post_schema
    assert detector_post_schema["$ref"].endswith("/DetectorConfig-Output")


def test_stage_2d2_openapi_response_components_include_system_models():
    client = TestClient(app)
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    data = openapi.json()

    schemas = data["components"]["schemas"]

    assert "HealthResponse" in schemas
    assert "StateDtoResponse" in schemas
    assert "StatusFullResponse" in schemas
    assert "CapabilitiesResponse" in schemas
    assert "RuntimeStatusResponse" in schemas
    assert "RuntimeStateResponse" in schemas
    assert "RuntimeSubsystemStateResponse" in schemas

def test_stage_2d2_openapi_control_responses_are_typed():
    client = TestClient(app)
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    data = openapi.json()

    lamp_schema = data["paths"]["/api/v1/lamp"]["post"]["responses"]["200"]["content"]["application/json"]["schema"]
    calib_status_schema = data["paths"]["/api/v1/calibration/status"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    calib_mode_schema = data["paths"]["/api/v1/calibration/mode"]["post"]["responses"]["200"]["content"]["application/json"]["schema"]
    calib_lamp_schema = data["paths"]["/api/v1/calibration/lamp"]["post"]["responses"]["200"]["content"]["application/json"]["schema"]
    slit_schema = data["paths"]["/api/v1/slit"]["post"]["responses"]["200"]["content"]["application/json"]["schema"]
    slit_angle_schema = data["paths"]["/api/v1/slit_angle"]["post"]["responses"]["200"]["content"]["application/json"]["schema"]

    assert "$ref" in lamp_schema
    assert lamp_schema["$ref"].endswith("/StateDtoResponse")

    assert "$ref" in calib_status_schema
    assert calib_status_schema["$ref"].endswith("/CalibrationStatusResponse")

    assert "$ref" in calib_mode_schema
    assert calib_mode_schema["$ref"].endswith("/CalibrationStatusResponse")

    assert "$ref" in calib_lamp_schema
    assert calib_lamp_schema["$ref"].endswith("/CalibrationStatusResponse")

    assert "$ref" in slit_schema
    assert slit_schema["$ref"].endswith("/StateDtoResponse")

    assert "$ref" in slit_angle_schema
    assert slit_angle_schema["$ref"].endswith("/StateDtoResponse")
def test_stage_2d2_openapi_control_response_components_exist():
    client = TestClient(app)
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    data = openapi.json()

    schemas = data["components"]["schemas"]

    assert "CalibrationStatusResponse" in schemas
    assert "StateDtoResponse" in schemas

def test_stage_2d2_openapi_error_response_models_are_declared():
    client = TestClient(app)
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    data = openapi.json()

    obs_start_400 = data["paths"]["/api/v1/observation/start"]["post"]["responses"]["400"]["content"]["application/json"]["schema"]
    slit_400 = data["paths"]["/api/v1/slit"]["post"]["responses"]["400"]["content"]["application/json"]["schema"]
    calib_status_404 = data["paths"]["/api/v1/calibration/status"]["get"]["responses"]["404"]["content"]["application/json"]["schema"]
    preset_apply_404 = data["paths"]["/api/v1/presets/apply"]["post"]["responses"]["404"]["content"]["application/json"]["schema"]

    assert "$ref" in obs_start_400
    assert obs_start_400["$ref"].endswith("/ApiErrorResponse")

    assert "$ref" in slit_400
    assert slit_400["$ref"].endswith("/ApiErrorResponse")

    assert "$ref" in calib_status_404
    assert calib_status_404["$ref"].endswith("/ApiErrorResponse")

    assert "$ref" in preset_apply_404
    assert preset_apply_404["$ref"].endswith("/ApiErrorResponse")


def test_stage_2d2_openapi_error_components_exist():
    client = TestClient(app)
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    data = openapi.json()

    schemas = data["components"]["schemas"]

    assert "ApiErrorResponse" in schemas
    assert "ApiErrorDetailResponse" in schemas

def test_stage_2d2_api_observation_invalid_start_returns_structured_error():
    client = TestClient(app)

    response = client.post("/api/v1/observation/start")
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert data["detail"]["code"] == "invalid_state"
    assert isinstance(data["detail"]["message"], str)
    assert data["detail"]["message"]


def test_stage_2d2_api_apply_unknown_preset_returns_structured_error():
    client = TestClient(app)

    response = client.post("/api/v1/presets/apply", json={"name": "not_exists"})
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert data["detail"]["code"] == "preset_not_found"
    assert data["detail"]["message"] == "Preset not found: not_exists"

def test_stage_2d2_dispatcher_invalid_state_does_not_fault_detector_subsystem():
    runtime = RuntimeAssembler().build()
    dispatcher = CommandDispatcher(runtime)

    def handler(rt, request):
        raise InvalidStateError(
            "detector is not ready for this transition",
            subsystem="detector",
            details={"state": "ready_to_arm"},
        )

    dispatcher.register_handler("detector", "bad_transition", handler)

    req = CommandRequest.create(
        subsystem="detector",
        action="bad_transition",
        params={},
        source=CommandSource.API,
    )

    result = dispatcher.dispatch(req)
    data = result.to_dict()

    assert data["job"]["status"] == "failed"
    assert data["payload"]["error"]["code"] == "invalid_state"
    assert runtime.get_subsystem_state("detector").state == ControlState.IDLE
    assert runtime.get_snapshot().overall_state == ControlState.IDLE


def test_stage_2d2_dispatcher_invalid_param_does_not_fault_slit_subsystem():
    runtime = RuntimeAssembler().build()
    dispatcher = CommandDispatcher(runtime)

    def handler(rt, request):
        raise InvalidParamError(
            "width_um must be > 0",
            subsystem="slit",
            details={"width_um": 0},
        )

    dispatcher.register_handler("slit", "bad_width", handler)

    req = CommandRequest.create(
        subsystem="slit",
        action="bad_width",
        params={"width_um": 0},
        source=CommandSource.API,
    )

    result = dispatcher.dispatch(req)
    data = result.to_dict()

    assert data["job"]["status"] == "failed"
    assert data["payload"]["error"]["code"] == "invalid_param"
    assert runtime.get_subsystem_state("slit").state == ControlState.IDLE
    assert runtime.get_snapshot().overall_state == ControlState.IDLE


def test_stage_2d2_api_observation_invalid_start_does_not_fault_runtime_state():
    client = TestClient(app)

    response = client.post("/api/v1/observation/start")
    assert response.status_code == 400

    health = client.get("/api/v1/health")
    assert health.status_code == 200
    data = health.json()

    runtime_state = data["runtime"]["state"]
    assert runtime_state["overall_state"] != "fault"
    assert runtime_state["subsystems"]["detector"]["state"] == "idle"
    assert runtime_state["exposure_state"] == "ready_to_arm"

def test_stage_2d2_runtime_snapshot_exposure_state_is_derived_from_detector():
    runtime = RuntimeAssembler().build()

    runtime.detector.arm(
        exp_time_s=5.0,
        frame_type="science",
        operator_note="derive-check",
        instrument_snapshot=None,
        calibration_snapshot=None,
        detector_config=runtime.get_detector_config_dict(),
    )

    runtime_snapshot = runtime.get_snapshot()
    detector_snapshot = runtime.detector.get_snapshot()

    assert runtime_snapshot.exposure_state == detector_snapshot.state
    assert runtime_snapshot.exposure_state.value == "armed"


def test_stage_2d2_runtime_snapshot_exposure_state_tracks_detector_after_start_and_finish():
    runtime = RuntimeAssembler().build()

    runtime.detector.arm(
        exp_time_s=5.0,
        frame_type="science",
        operator_note="derive-check",
        instrument_snapshot=None,
        calibration_snapshot=None,
        detector_config=runtime.get_detector_config_dict(),
    )
    runtime.detector.start()

    runtime_snapshot = runtime.get_snapshot()
    detector_snapshot = runtime.detector.get_snapshot()
    assert runtime_snapshot.exposure_state == detector_snapshot.state
    assert runtime_snapshot.exposure_state.value == "exposing"

    runtime.detector.finish_normal()

    runtime_snapshot = runtime.get_snapshot()
    detector_snapshot = runtime.detector.get_snapshot()
    assert runtime_snapshot.exposure_state == detector_snapshot.state
    assert runtime_snapshot.exposure_state.value == "completed"


def test_stage_2d2_api_health_runtime_exposure_state_matches_observation_status_across_flow():
    client = TestClient(app)

    initial_health = client.get("/api/v1/health")
    initial_obs = client.get("/api/v1/observation/status")
    assert initial_health.status_code == 200
    assert initial_obs.status_code == 200
    assert initial_health.json()["runtime"]["state"]["exposure_state"] == initial_obs.json()["state"] == "ready_to_arm"

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 5.0, "frame_type": "science", "operator_note": "api-sync-check"},
    )
    assert arm.status_code == 200

    armed_health = client.get("/api/v1/health")
    armed_obs = client.get("/api/v1/observation/status")
    assert armed_health.status_code == 200
    assert armed_obs.status_code == 200
    assert armed_health.json()["runtime"]["state"]["exposure_state"] == armed_obs.json()["state"] == "armed"

    start = client.post("/api/v1/observation/start")
    assert start.status_code == 200

    exposing_health = client.get("/api/v1/health")
    exposing_obs = client.get("/api/v1/observation/status")
    assert exposing_health.status_code == 200
    assert exposing_obs.status_code == 200
    assert exposing_health.json()["runtime"]["state"]["exposure_state"] == exposing_obs.json()["state"] == "exposing"

    finish = client.post("/api/v1/observation/finish")
    assert finish.status_code == 200

    completed_health = client.get("/api/v1/health")
    completed_obs = client.get("/api/v1/observation/status")
    assert completed_health.status_code == 200
    assert completed_obs.status_code == 200
    assert completed_health.json()["runtime"]["state"]["exposure_state"] == completed_obs.json()["state"] == "completed"

def test_stage_2d2_armed_blocks_detector_config_mutation():
    client = TestClient(app)

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 5.0, "frame_type": "science", "operator_note": "lock-detector"},
    )
    assert arm.status_code == 200

    response = client.post(
        "/api/v1/detector/config",
        json={
            "profile_name": "locked-armed",
            "save_enabled": True,
            "trigger_mode": "internal",
            "readout_mode": "normal",
            "channels": {
                "B": {"enabled": True, "camera_role": "science_b"},
                "G": {"enabled": True, "camera_role": "science_g"},
                "R": {"enabled": True, "camera_role": "science_r"},
            },
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_state"


def test_stage_2d2_armed_blocks_preset_apply():
    client = TestClient(app)

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 5.0, "frame_type": "science", "operator_note": "lock-preset"},
    )
    assert arm.status_code == 200

    response = client.post("/api/v1/presets/apply", json={"name": "science_default"})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_state"


def test_stage_2d2_armed_blocks_slit_and_calibration_mutation():
    client = TestClient(app)

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 5.0, "frame_type": "science", "operator_note": "lock-slit-cal"},
    )
    assert arm.status_code == 200

    slit = client.post("/api/v1/slit", json={"width_um": 140.0})
    assert slit.status_code == 400
    assert slit.json()["detail"]["code"] == "invalid_state"

    calibration = client.post("/api/v1/calibration/mode", json={"mode": "calibration"})
    assert calibration.status_code == 400
    assert calibration.json()["detail"]["code"] == "invalid_state"


def test_stage_2d2_armed_still_allows_observation_start():
    client = TestClient(app)

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 5.0, "frame_type": "science", "operator_note": "start-still-allowed"},
    )
    assert arm.status_code == 200

    start = client.post("/api/v1/observation/start")
    assert start.status_code == 200
    assert start.json()["state"] == "exposing"


def test_stage_2d2_exposing_blocks_detector_preset_and_slit_mutation():
    client = TestClient(app)

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 5.0, "frame_type": "science", "operator_note": "lock-exposing"},
    )
    assert arm.status_code == 200

    start = client.post("/api/v1/observation/start")
    assert start.status_code == 200
    assert start.json()["state"] == "exposing"

    detector = client.post(
        "/api/v1/detector/config",
        json={
            "profile_name": "locked-exposing",
            "save_enabled": True,
            "trigger_mode": "internal",
            "readout_mode": "normal",
            "channels": {
                "B": {"enabled": True, "camera_role": "science_b"},
                "G": {"enabled": True, "camera_role": "science_g"},
                "R": {"enabled": True, "camera_role": "science_r"},
            },
        },
    )
    assert detector.status_code == 400
    assert detector.json()["detail"]["code"] == "invalid_state"

    preset = client.post("/api/v1/presets/apply", json={"name": "science_default"})
    assert preset.status_code == 400
    assert preset.json()["detail"]["code"] == "invalid_state"

    slit = client.post("/api/v1/slit", json={"width_um": 150.0})
    assert slit.status_code == 400
    assert slit.json()["detail"]["code"] == "invalid_state"


def test_stage_2d2_exposing_still_allows_observation_finish():
    client = TestClient(app)

    arm = client.post(
        "/api/v1/observation/arm",
        json={"exp_time_s": 5.0, "frame_type": "science", "operator_note": "finish-still-allowed"},
    )
    assert arm.status_code == 200

    start = client.post("/api/v1/observation/start")
    assert start.status_code == 200
    assert start.json()["state"] == "exposing"

    finish = client.post("/api/v1/observation/finish")
    assert finish.status_code == 200
    assert finish.json()["state"] == "completed"


def test_stage_2d2_api_success_response_includes_request_id_header():
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]


def test_stage_2d2_api_preserves_incoming_request_id_header():
    client = TestClient(app)

    response = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": "test-req-123"},
    )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-req-123"


def test_stage_2d2_api_validation_error_includes_request_id_header():
    client = TestClient(app)

    response = client.post("/api/v1/slit", json={"width_um": 0})
    assert response.status_code == 422
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]


def test_stage_2d2_api_internal_error_includes_request_id_header_and_detail():
    route_path = "/api/v1/_test/internal-error-request-id"

    existing_paths = {route.path for route in app.router.routes}
    if route_path not in existing_paths:
        @app.get(route_path, include_in_schema=False)
        def _test_internal_error_request_id():
            raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)

    response = client.get(route_path)
    assert response.status_code == 500

    data = response.json()
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]

    assert "detail" in data
    assert data["detail"]["code"] == "internal_error"
    assert data["detail"]["message"] == "Internal server error."
    assert data["detail"]["request_id"] == response.headers["X-Request-ID"]
