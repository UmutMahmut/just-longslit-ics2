from fastapi.testclient import TestClient

from justls.ics.app.main import app


def test_v7_default_shell_exposes_unified_command_feedback_static_bindings():
    client = TestClient(app)

    response = client.get("/ui")

    assert response.status_code == 200
    assert "v7.1 Operator Console Prototype" in response.text
    assert 'data-role="diagnostics-command-feedback"' in response.text
    assert "last_command / request_id / latest_job / last_error / result_summary / raw_json" in response.text

    for prefix in ("instrument", "observe", "presets"):
        assert f'data-bind="v7.{prefix}.last_command"' in response.text
        assert f'data-bind="v7.{prefix}.request_id"' in response.text
        assert f'data-bind="v7.{prefix}.latest_job"' in response.text
        assert f'data-bind="v7.{prefix}.last_error"' in response.text
        assert f'data-bind="v7.{prefix}.result_summary"' in response.text


def test_v7_default_and_explicit_v7_shells_are_aligned():
    client = TestClient(app)

    default_response = client.get("/ui")
    explicit_response = client.get("/ui/v7")

    assert default_response.status_code == 200
    assert explicit_response.status_code == 200
    assert default_response.text == explicit_response.text
