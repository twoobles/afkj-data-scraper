"""Dream Realm mode — extracts rank, player info, and score."""

from extraction.ocr import parse_score
from modes.base import BaseMode


class DreamRealmMode(BaseMode):
    """Extractor for the Dream Realm ranking list."""

    @property
    def mode_name(self) -> str:
        return "dream_realm"

    def parse_extra(self, text: str) -> str | None:
        """Parse a Dream Realm score (e.g. '169B', '210M')."""
        return parse_score(text)
