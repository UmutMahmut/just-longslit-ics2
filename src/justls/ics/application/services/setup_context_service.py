from __future__ import annotations

from datetime import date
from typing import Any

from justls.ics.domain.setup import SessionDataContext


class SetupContextService:
    def __init__(self, context: SessionDataContext | None = None) -> None:
        self._context = context or SessionDataContext()

    def get_context(self) -> SessionDataContext:
        return self._context

    def get_context_payload(self, observing_date: date | str | None = None) -> dict[str, Any]:
        return self._context.to_dict(observing_date)