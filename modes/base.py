"""Base class for game mode ranking extraction."""

import logging
from abc import ABC, abstractmethod

import extraction.ocr
from models import PlayerRecord

logger = logging.getLogger(__name__)


class BaseMode(ABC):
    """Abstract base for all game mode extractors.

    Subclasses must define ``mode_name``.  The default ``parse_card``
    implementation extracts rank, player name, and guild from OCR text
    lines.  Modes with extra right-side data (AFK Stages, Dream Realm)
    override ``parse_extra`` to pull the additional field.
    """

    @property
    @abstractmethod
    def mode_name(self) -> str:
        """Return the canonical mode identifier (e.g. 'afk_stages')."""

    def parse_card(self, lines: list[str]) -> PlayerRecord | None:
        """Parse OCR text lines from a single ranking card.

        Expected line order (top-to-bottom from ``extract_text_lines``):
        rank, player_name, guild, and optionally mode-specific extra.

        Args:
            lines: OCR text strings from one ranking card, sorted
                   top-to-bottom.

        Returns:
            A ``PlayerRecord``, or ``None`` if the card could not be
            parsed (e.g. too few lines or no valid rank).
        """
        rank, extra = None, None
        name_and_guild = []

        for line in lines:
            if rank is None and (rank := extraction.ocr.parse_rank(line)) is not None:
                continue

            if extra is None and (extra := self.parse_extra(line)) is not None:
                continue

            name_and_guild.append(line)

        if rank is None or len(name_and_guild) < 2:
            return None

        return PlayerRecord(
            player_name=name_and_guild[0], guild=name_and_guild[1], rank=rank, extra=extra
        )

    def parse_extra(self, text: str) -> str | None:
        """Parse mode-specific data from a text line.

        The base implementation returns ``None`` (no extra data).
        Override in subclasses that have right-side card data.

        Args:
            text: A single OCR text string to check.

        Returns:
            Normalized extra value, or ``None`` if not recognized.
        """
        return None
