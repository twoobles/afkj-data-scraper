"""Game mode registry — maps mode names to their extractor classes."""

from modes.afk_stages import AfkStagesMode
from modes.arcane_labyrinth import ArcaneLabyrinthMode
from modes.base import BaseMode
from modes.dream_realm import DreamRealmMode
from modes.honor_duel import HonorDuelMode
from modes.supreme_arena import SupremeArenaMode

MODE_REGISTRY: dict[str, type[BaseMode]] = {
    "afk_stages": AfkStagesMode,
    "dream_realm": DreamRealmMode,
    "supreme_arena": SupremeArenaMode,
    "arcane_labyrinth": ArcaneLabyrinthMode,
    "honor_duel": HonorDuelMode,
}

__all__ = [
    "MODE_REGISTRY",
    "AfkStagesMode",
    "ArcaneLabyrinthMode",
    "BaseMode",
    "DreamRealmMode",
    "HonorDuelMode",
    "SupremeArenaMode",
]
