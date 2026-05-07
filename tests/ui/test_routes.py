from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_ui_root_stays_default_v5_entry():
    client = TestClient(app)

    response = client.get("/ui")

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
    assert root.json()["ui_v7"] == "/ui/v7"
    assert root.json()["ui_safety_switches"]["phase2d8_v7_runtime_enabled"] is False

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "v7.1 Operator Console Prototype" in response.text
    assert "Instrument / Configure" in response.text
    assert "/ui-assets/v7/runtime_status.js" not in response.text
    assert "/ui-assets/v7/observe_runtime.js" not in response.text
