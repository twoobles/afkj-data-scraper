"""Honor Duel mode — rank only, no extra data."""

from modes.base import BaseMode


class HonorDuelMode(BaseMode):
    """Extractor for the Honor Duel ranking list."""

    @property
    def mode_name(self) -> str:
        return "honor_duel"
