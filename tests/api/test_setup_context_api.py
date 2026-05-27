import re

from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_get_setup_context_returns_default_context() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/setup/context")

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")

    payload = response.json()
    assert payload["observers"] == ""
    assert payload["project_id"] == ""
    assert payload["pi_name"] == ""
    assert payload["support_operator"] == ""
    assert payload["root_name"] == "justls"
    assert payload["date_prefix"] == "AUTO"
    assert payload["comment"] == ""
    assert payload["next_frame_index"] == 1
    assert payload["data_directory"] == ""
    assert re.match(r"^\d{8}-0001$", payload["next_frame_token"])
    assert re.match(r"^justls_\d{8}_0001$", payload["file_stem"])
    assert re.match(r"^justls_\d{8}_0001\.fits$", payload["fits_filename"])


def test_get_setup_context_rejects_extra_response_fields_contractually() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/setup/context")

    assert response.status_code == 200
    assert set(response.json()) == {
        "observers",
        "project_id",
        "pi_name",
        "support_operator",
        "root_name",
        "date_prefix",
        "comment",
        "next_frame_index",
        "data_directory",
        "next_frame_token",
        "file_stem",
        "fits_filename",
    }