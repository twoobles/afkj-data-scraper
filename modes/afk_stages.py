"""AFK Stages mode — extracts rank, player info, and stage number."""

from extraction.ocr import parse_stage
from modes.base import BaseMode


class AfkStagesMode(BaseMode):
    """Extractor for the AFK Stages ranking list."""

    @property
    def mode_name(self) -> str:
        return "afk_stages"

    def parse_extra(self, text: str) -> str | None:
        """Parse an AFK stage value (e.g. '1452', 'A252')."""
        return parse_stage(text)
