from datetime import date

from justls.ics.application.services.setup_context_service import SetupContextService
from justls.ics.domain.setup import SessionDataContext


def test_setup_context_service_returns_default_context() -> None:
    service = SetupContextService()

    context = service.get_context()

    assert isinstance(context, SessionDataContext)
    assert context.root_name == "justls"
    assert context.date_prefix == "AUTO"
    assert context.next_frame_index == 1


def test_setup_context_service_returns_derived_payload() -> None:
    service = SetupContextService(
        SessionDataContext(
            observers="Observer",
            project_id="P-001",
            root_name="science",
            date_prefix="AUTO",
            next_frame_index=5,
            data_directory="/data/just",
        )
    )

    payload = service.get_context_payload(date(2026, 5, 27))

    assert payload["observers"] == "Observer"
    assert payload["project_id"] == "P-001"
    assert payload["root_name"] == "science"
    assert payload["date_prefix"] == "AUTO"
    assert payload["next_frame_index"] == 5
    assert payload["data_directory"] == "/data/just"
    assert payload["next_frame_token"] == "20260527-0005"
    assert payload["file_stem"] == "science_20260527_0005"
    assert payload["fits_filename"] == "science_20260527_0005.fits"