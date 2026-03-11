"""Supreme Arena mode — rank only, no extra data."""

from modes.base import BaseMode


class SupremeArenaMode(BaseMode):
    """Extractor for the Supreme Arena ranking list."""

    @property
    def mode_name(self) -> str:
        return "supreme_arena"
