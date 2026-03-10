"""Data structures for AFK Journey Data Scraper."""

from dataclasses import dataclass
from datetime import date


@dataclass
class PlayerRecord:
    """A single player's ranking data extracted from one game mode.

    Represents raw extraction output from a single ranking card.
    """

    player_name: str
    guild: str
    rank: int
    # Mode-specific extras (afk_stage or dr_score), None for rank-only modes
    extra: str | None = None


@dataclass
class ScanResult:
    """Aggregated scan data for one player across all modes on a given date.

    Maps directly to one row in the scans SQLite table.
    """

    player_name: str
    guild: str
    scan_date: date
    afk_rank: int | None = None
    afk_stage: str | None = None
    dr_rank: int | None = None
    dr_score: str | None = None
    sa_rank: int | None = None
    al_rank: int | None = None
    hd_rank: int | None = None
