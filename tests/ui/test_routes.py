from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_ui_root_is_default_v7_operator_console_prototype():
    client = TestClient(app)

    response = client.get("/ui")

    assert response.status_code == 200
    assert "v7.1 Operator Console Prototype" in response.text
    assert "UI Alpha Skeleton" not in response.text
    assert "/ui-assets/v5/phase2d6_operational_status.js" not in response.text
    assert "/ui-assets/v7/runtime_status.js" not in response.text
    assert "Phase 2.8-J default route" in response.text


def test_v5_legacy_fallback_routes_stay_available():
    client = TestClient(app)

    for route in ("/ui/v5", "/ui/legacy"):
        response = client.get(route)

        assert response.status_code == 200
        assert "UI Alpha Skeleton" in response.text
        assert "v7.1 Operator Console Prototype" not in response.text
        assert "/ui-assets/v5/phase2d6_operational_status.js" in response.text


def test_ui_v6_review_shell_stays_available():
    client = TestClient(app)

    response = client.get("/ui/v6")

    assert response.status_code == 200
    assert "v6" in response.text.lower()


def test_ui_v7_static_shell_stays_available_with_runtime_disabled_by_default():
    client = TestClient(app)

    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["ui"] == "/ui"
    assert root.json()["ui_default"] == "v7"
    assert root.json()["ui_v5"] == "/ui/v5"
    assert root.json()["ui_legacy"] == "/ui/legacy"
    assert root.json()["ui_v7"] == "/ui/v7"
    assert root.json()["ui_safety_switches"]["phase2d8_v7_runtime_enabled"] is False

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "v7.1 Operator Console Prototype" in response.text
    assert "Instrument / Configure" in response.text
    assert "/ui-assets/v7/runtime_status.js" not in response.text
    assert "/ui-assets/v7/observe_runtime.js" not in response.text
