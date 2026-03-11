"""Tests for validator module."""

from models import PlayerRecord
from validator import validate_records, validate_score, validate_stage

# --- validate_score ---


class TestValidateScore:
    def test_valid_billions(self):
        assert validate_score("169B") is True

    def test_valid_millions(self):
        assert validate_score("210M") is True

    def test_valid_thousands(self):
        assert validate_score("50K") is True

    def test_valid_trillions(self):
        assert validate_score("5T") is True

    def test_valid_lowercase(self):
        assert validate_score("100m") is True

    def test_invalid_no_suffix(self):
        assert validate_score("169") is False

    def test_invalid_decimal(self):
        assert validate_score("1.5B") is False

    def test_invalid_text(self):
        assert validate_score("abc") is False

    def test_invalid_empty(self):
        assert validate_score("") is False


# --- validate_stage ---


class TestValidateStage:
    def test_valid_plain_number(self):
        assert validate_stage("1452") is True

    def test_valid_apex(self):
        assert validate_stage("A252") is True

    def test_valid_apex_lowercase(self):
        assert validate_stage("a100") is True

    def test_invalid_text(self):
        assert validate_stage("Stage5") is False

    def test_invalid_empty(self):
        assert validate_stage("") is False

    def test_invalid_special_chars(self):
        assert validate_stage("14-52") is False


# --- validate_records ---


def _make_record(name: str = "Player", guild: str = "G1", rank: int = 1, extra=None):
    return PlayerRecord(player_name=name, guild=guild, rank=rank, extra=extra)


class TestValidateRecords:
    def test_valid_records_no_errors(self):
        records = [
            _make_record("Alice", "G1", 1),
            _make_record("Bob", "G1", 2),
        ]
        assert validate_records(records, "supreme_arena") == []

    def test_duplicate_detected(self):
        records = [
            _make_record("Alice", "G1", 1),
            _make_record("Alice", "G1", 2),
        ]
        errors = validate_records(records, "supreme_arena")
        assert len(errors) == 1
        assert "Duplicate" in errors[0]

    def test_empty_name(self):
        records = [_make_record("", "G1", 1)]
        errors = validate_records(records, "supreme_arena")
        assert any("empty player name" in e for e in errors)

    def test_empty_guild(self):
        records = [_make_record("Alice", "", 1)]
        errors = validate_records(records, "supreme_arena")
        assert any("empty guild" in e for e in errors)

    def test_invalid_rank(self):
        records = [_make_record("Alice", "G1", 0)]
        errors = validate_records(records, "supreme_arena")
        assert any("Invalid rank" in e for e in errors)

    def test_invalid_stage_in_afk_mode(self):
        records = [_make_record("Alice", "G1", 1, extra="BadStage")]
        errors = validate_records(records, "afk_stages")
        assert any("Invalid stage" in e for e in errors)

    def test_valid_stage_in_afk_mode(self):
        records = [_make_record("Alice", "G1", 1, extra="A252")]
        errors = validate_records(records, "afk_stages")
        assert errors == []

    def test_invalid_score_in_dream_realm(self):
        records = [_make_record("Alice", "G1", 1, extra="999")]
        errors = validate_records(records, "dream_realm")
        assert any("Invalid score" in e for e in errors)

    def test_valid_score_in_dream_realm(self):
        records = [_make_record("Alice", "G1", 1, extra="169B")]
        errors = validate_records(records, "dream_realm")
        assert errors == []

    def test_extra_ignored_for_rank_only_modes(self):
        """Extra field is not validated for rank-only modes."""
        records = [_make_record("Alice", "G1", 1, extra="anything")]
        errors = validate_records(records, "supreme_arena")
        assert errors == []

    def test_whitespace_only_name(self):
        records = [_make_record("   ", "G1", 1)]
        errors = validate_records(records, "supreme_arena")
        assert any("empty player name" in e for e in errors)
