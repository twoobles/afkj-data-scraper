"""Validation for extracted player records before DB commit."""

import logging

from config import SCORE_PATTERN, STAGE_PATTERN
from models import PlayerRecord

logger = logging.getLogger(__name__)


def validate_score(score: str) -> bool:
    """Check if a Dream Realm score string is valid (e.g. '169B', '210M', '1.5K')."""
    return bool(SCORE_PATTERN.match(score))


def validate_stage(stage: str) -> bool:
    """Check if an AFK Stages string is valid (e.g. '1452', 'A252')."""
    return bool(STAGE_PATTERN.match(stage))


def validate_records(records: list[PlayerRecord], mode: str) -> list[str]:
    """Validate a list of extracted records for a given mode.

    Returns a list of warning/error messages. Empty list means all valid.
    """
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()

    for record in records:
        key = (record.player_name, record.guild)

        # Duplicate check
        if key in seen:
            msg = f"Duplicate player ({record.player_name}, {record.guild}) in {mode} — skipping"
            logger.warning(msg)
            errors.append(msg)
            continue
        seen.add(key)

        # Blank name/guild
        if not record.player_name.strip():
            errors.append(f"Rank {record.rank}: empty player name")
        if not record.guild.strip():
            errors.append(f"Rank {record.rank}: empty guild for '{record.player_name}'")

        # Rank sanity
        if record.rank < 1:
            errors.append(f"Invalid rank {record.rank} for '{record.player_name}'")

        # Mode-specific extra field validation
        if mode == "afk_stages" and record.extra is not None and not validate_stage(record.extra):
            errors.append(f"Invalid stage '{record.extra}' for '{record.player_name}'")

        if mode == "dream_realm" and record.extra is not None and not validate_score(record.extra):
            errors.append(f"Invalid score '{record.extra}' for '{record.player_name}'")

    return errors
