"""Tests for modes package — base class, subclasses, and registry."""

import pytest

from models import PlayerRecord
from modes import MODE_REGISTRY
from modes.afk_stages import AfkStagesMode
from modes.arcane_labyrinth import ArcaneLabyrinthMode
from modes.base import BaseMode
from modes.dream_realm import DreamRealmMode
from modes.honor_duel import HonorDuelMode
from modes.supreme_arena import SupremeArenaMode

# ---------------------------------------------------------------------------
# BaseMode — cannot be instantiated directly
# ---------------------------------------------------------------------------


def test_base_mode_is_abstract():
    """BaseMode cannot be instantiated without implementing mode_name."""
    with pytest.raises(TypeError):
        BaseMode()


# ---------------------------------------------------------------------------
# BaseMode.parse_card — rank-only modes
# ---------------------------------------------------------------------------


class TestParseCardRankOnly:
    """parse_card on modes with no extra data."""

    def test_basic_card(self):
        """Three lines: rank, name, guild."""
        mode = SupremeArenaMode()
        result = mode.parse_card(["1", "PlayerOne", "MyGuild"])
        assert result == PlayerRecord(player_name="PlayerOne", guild="MyGuild", rank=1)

    def test_rank_with_ocr_misread(self):
        """OCR misreads like 'O' for '0' should be corrected."""
        mode = SupremeArenaMode()
        result = mode.parse_card(["1O", "Player", "Guild"])
        assert result is not None
        assert result.rank == 10

    def test_extra_is_none_for_rank_only(self):
        """Rank-only modes should always have extra=None."""
        mode = HonorDuelMode()
        result = mode.parse_card(["5", "Player", "Guild"])
        assert result is not None
        assert result.extra is None

    def test_too_few_lines(self):
        """Fewer than rank + name + guild should return None."""
        mode = SupremeArenaMode()
        assert mode.parse_card(["1", "PlayerOnly"]) is None

    def test_empty_lines(self):
        mode = SupremeArenaMode()
        assert mode.parse_card([]) is None

    def test_no_valid_rank(self):
        """If no line parses as a rank, return None."""
        mode = SupremeArenaMode()
        assert mode.parse_card(["abc", "Player", "Guild"]) is None

    def test_extra_text_lines_ignored(self):
        """Extra text beyond name+guild doesn't break parsing."""
        mode = SupremeArenaMode()
        result = mode.parse_card(["3", "Player", "Guild", "garbage"])
        assert result is not None
        assert result.player_name == "Player"
        assert result.guild == "Guild"

    def test_chinese_player_name(self):
        """Chinese characters in player name should pass through."""
        mode = ArcaneLabyrinthMode()
        result = mode.parse_card(["7", "\u5f20\u4e09", "MyGuild"])
        assert result is not None
        assert result.player_name == "\u5f20\u4e09"


# ---------------------------------------------------------------------------
# BaseMode.parse_card — modes with extra data
# ---------------------------------------------------------------------------


class TestParseCardWithExtra:
    """parse_card on AFK Stages and Dream Realm (have extra field)."""

    def test_afk_stages_plain(self):
        mode = AfkStagesMode()
        result = mode.parse_card(["1", "Player", "Guild", "1452"])
        assert result == PlayerRecord(player_name="Player", guild="Guild", rank=1, extra="1452")

    def test_afk_stages_apex(self):
        mode = AfkStagesMode()
        result = mode.parse_card(["2", "Player", "Guild", "Apex 252"])
        assert result is not None
        assert result.extra == "A252"

    def test_dream_realm_score(self):
        mode = DreamRealmMode()
        result = mode.parse_card(["1", "Player", "Guild", "169B"])
        assert result == PlayerRecord(player_name="Player", guild="Guild", rank=1, extra="169B")

    def test_dream_realm_lowercase(self):
        mode = DreamRealmMode()
        result = mode.parse_card(["3", "Player", "Guild", "210m"])
        assert result is not None
        assert result.extra == "210M"

    def test_missing_extra_still_parses(self):
        """Card without extra data should still return a record."""
        mode = AfkStagesMode()
        result = mode.parse_card(["1", "Player", "Guild"])
        assert result is not None
        assert result.extra is None

    def test_extra_not_consumed_as_name(self):
        """Extra value should not end up as player_name or guild."""
        mode = DreamRealmMode()
        result = mode.parse_card(["1", "Player", "Guild", "500T"])
        assert result is not None
        assert result.player_name == "Player"
        assert result.guild == "Guild"
        assert result.extra == "500T"

    def test_only_first_rank_consumed(self):
        """If multiple lines parse as rank, only first is used."""
        mode = AfkStagesMode()
        result = mode.parse_card(["1", "Player", "Guild", "1452"])
        assert result is not None
        assert result.rank == 1
        # "1452" matches as stage extra, not as a second rank
        assert result.extra == "1452"

    def test_only_first_extra_consumed(self):
        """If multiple lines match extra, only first is used."""
        mode = DreamRealmMode()
        result = mode.parse_card(["1", "Player", "Guild", "169B", "210M"])
        assert result is not None
        assert result.extra == "169B"


# ---------------------------------------------------------------------------
# BaseMode.parse_extra — default returns None
# ---------------------------------------------------------------------------


def test_base_parse_extra_returns_none():
    """Default parse_extra returns None for any input."""
    mode = SupremeArenaMode()
    assert mode.parse_extra("anything") is None
    assert mode.parse_extra("169B") is None
    assert mode.parse_extra("1452") is None


# ---------------------------------------------------------------------------
# Mode names
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "mode_cls, expected_name",
    [
        (AfkStagesMode, "afk_stages"),
        (DreamRealmMode, "dream_realm"),
        (SupremeArenaMode, "supreme_arena"),
        (ArcaneLabyrinthMode, "arcane_labyrinth"),
        (HonorDuelMode, "honor_duel"),
    ],
)
def test_mode_name(mode_cls, expected_name):
    """Each mode subclass returns the correct mode_name."""
    mode = mode_cls()
    assert mode.mode_name == expected_name


# ---------------------------------------------------------------------------
# AfkStagesMode.parse_extra
# ---------------------------------------------------------------------------


class TestAfkStagesParseExtra:
    """AfkStagesMode.parse_extra delegates to parse_stage."""

    def test_plain_stage(self):
        mode = AfkStagesMode()
        assert mode.parse_extra("1452") == "1452"

    def test_apex_stage_full(self):
        mode = AfkStagesMode()
        assert mode.parse_extra("Apex 252") == "A252"

    def test_apex_stage_short(self):
        mode = AfkStagesMode()
        assert mode.parse_extra("A252") == "A252"

    def test_apex_lowercase(self):
        mode = AfkStagesMode()
        assert mode.parse_extra("apex 100") == "A100"

    def test_invalid_stage(self):
        mode = AfkStagesMode()
        assert mode.parse_extra("not a stage") is None

    def test_empty_string(self):
        mode = AfkStagesMode()
        assert mode.parse_extra("") is None

    def test_score_not_a_stage(self):
        """Scores (like 169B) should not parse as a stage."""
        mode = AfkStagesMode()
        assert mode.parse_extra("169B") is None


# ---------------------------------------------------------------------------
# DreamRealmMode.parse_extra
# ---------------------------------------------------------------------------


class TestDreamRealmParseExtra:
    """DreamRealmMode.parse_extra delegates to parse_score."""

    def test_billions(self):
        mode = DreamRealmMode()
        assert mode.parse_extra("169B") == "169B"

    def test_millions(self):
        mode = DreamRealmMode()
        assert mode.parse_extra("210M") == "210M"

    def test_trillions(self):
        mode = DreamRealmMode()
        assert mode.parse_extra("5T") == "5T"

    def test_thousands(self):
        mode = DreamRealmMode()
        assert mode.parse_extra("800K") == "800K"

    def test_lowercase_suffix(self):
        mode = DreamRealmMode()
        assert mode.parse_extra("169b") == "169B"

    def test_invalid_score(self):
        mode = DreamRealmMode()
        assert mode.parse_extra("not a score") is None

    def test_empty_string(self):
        mode = DreamRealmMode()
        assert mode.parse_extra("") is None

    def test_plain_number_not_a_score(self):
        """Plain numbers without suffix should not parse as score."""
        mode = DreamRealmMode()
        assert mode.parse_extra("1452") is None


# ---------------------------------------------------------------------------
# Rank-only modes — parse_extra always returns None
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "mode_cls",
    [SupremeArenaMode, ArcaneLabyrinthMode, HonorDuelMode],
)
class TestRankOnlyParseExtra:
    """Rank-only modes inherit default parse_extra (always None)."""

    def test_returns_none_for_score(self, mode_cls):
        assert mode_cls().parse_extra("169B") is None

    def test_returns_none_for_stage(self, mode_cls):
        assert mode_cls().parse_extra("1452") is None

    def test_returns_none_for_text(self, mode_cls):
        assert mode_cls().parse_extra("PlayerName") is None


# ---------------------------------------------------------------------------
# MODE_REGISTRY
# ---------------------------------------------------------------------------


def test_registry_has_all_modes():
    """Registry should contain all five game modes."""
    expected = {
        "afk_stages",
        "dream_realm",
        "supreme_arena",
        "arcane_labyrinth",
        "honor_duel",
    }
    assert set(MODE_REGISTRY.keys()) == expected


def test_registry_values_are_base_mode_subclasses():
    """All registry values should be subclasses of BaseMode."""
    for cls in MODE_REGISTRY.values():
        assert issubclass(cls, BaseMode)


def test_registry_mode_names_match_keys():
    """Instantiated mode_name should match the registry key."""
    for key, cls in MODE_REGISTRY.items():
        assert cls().mode_name == key


def test_registry_classes_are_correct():
    """Registry maps to the correct concrete classes."""
    assert MODE_REGISTRY["afk_stages"] is AfkStagesMode
    assert MODE_REGISTRY["dream_realm"] is DreamRealmMode
    assert MODE_REGISTRY["supreme_arena"] is SupremeArenaMode
    assert MODE_REGISTRY["arcane_labyrinth"] is ArcaneLabyrinthMode
    assert MODE_REGISTRY["honor_duel"] is HonorDuelMode
