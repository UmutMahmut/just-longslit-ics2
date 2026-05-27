from __future__ import annotations

from datetime import date
from typing import Any

from justls.ics.application.services.setup_context_store import (
    InMemorySetupContextStore,
    SetupContextStore,
)
from justls.ics.domain.setup import SessionDataContext


class SetupContextService:
    def __init__(
        self,
        context: SessionDataContext | None = None,
        store: SetupContextStore | None = None,
    ) -> None:
        if context is not None and store is not None:
            raise ValueError("Provide either context or store, not both.")
        self._store = store or InMemorySetupContextStore(context)

    def get_context(self) -> SessionDataContext:
        return self._store.load()

    def save_context(self, context: SessionDataContext) -> SessionDataContext:
        return self._store.save(context)

    def get_context_payload(self, observing_date: date | str | None = None) -> dict[str, Any]:
        return self.get_context().to_dict(observing_date)