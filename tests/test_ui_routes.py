import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("src"))

from justls.ics.app.main import app


def test_ui_root_stays_default_v5_entry():
    client = TestClient(app)

    response = client.get("/ui")

    assert response.status_code == 200
    assert "UI Alpha Skeleton" in response.text
    assert "v7 Operator Console Prototype" not in response.text


def test_ui_v6_review_shell_stays_available():
    client = TestClient(app)

    response = client.get("/ui/v6")

    assert response.status_code == 200
    assert "v6" in response.text.lower()


def test_ui_v7_operator_console_shell_is_available():
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["ui_v7"] == "/ui/v7"

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "v7 Operator Console Prototype" in response.text
    assert "Live image region preserved" in response.text
    assert "Latest Exposure Preview" in response.text


def test_ui_v7_status_binding_adapter_is_injected_and_served():
    client = TestClient(app)

    response = client.get("/ui/v7")

    assert response.status_code == 200
    assert "/ui-assets/phase2d8_v7_status_binding.js" in response.text

    adapter = client.get("/ui-assets/phase2d8_v7_status_binding.js")

    assert adapter.status_code == 200
    assert "/api/v1/status/full" in adapter.text
    assert "Latest Exposure Preview" not in adapter.text
