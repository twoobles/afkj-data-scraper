"""Arcane Labyrinth mode — rank only, no extra data."""

from modes.base import BaseMode


class ArcaneLabyrinthMode(BaseMode):
    """Extractor for the Arcane Labyrinth ranking list."""

    @property
    def mode_name(self) -> str:
        return "arcane_labyrinth"
