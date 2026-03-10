"""Tests for models module."""

from datetime import date

from models import PlayerRecord, ScanResult


def test_player_record_defaults():
    record = PlayerRecord(player_name="Alice", guild="TestGuild", rank=1)
    assert record.extra is None


def test_player_record_with_extra():
    record = PlayerRecord(player_name="Bob", guild="G1", rank=5, extra="A252")
    assert record.extra == "A252"


def test_scan_result_defaults():
    result = ScanResult(player_name="Alice", guild="TestGuild", scan_date=date(2026, 3, 9))
    assert result.afk_rank is None
    assert result.afk_stage is None
    assert result.dr_rank is None
    assert result.dr_score is None
    assert result.sa_rank is None
    assert result.al_rank is None
    assert result.hd_rank is None


def test_scan_result_with_all_fields():
    result = ScanResult(
        player_name="Bob",
        guild="G1",
        scan_date=date(2026, 3, 9),
        afk_rank=1,
        afk_stage="1452",
        dr_rank=3,
        dr_score="169B",
        sa_rank=10,
        al_rank=20,
        hd_rank=50,
    )
    assert result.afk_rank == 1
    assert result.afk_stage == "1452"
    assert result.dr_rank == 3
    assert result.dr_score == "169B"
    assert result.sa_rank == 10
    assert result.al_rank == 20
    assert result.hd_rank == 50


def test_scan_result_partial_modes():
    """A single-mode run leaves other fields as None."""
    result = ScanResult(
        player_name="Charlie",
        guild="G2",
        scan_date=date(2026, 3, 9),
        sa_rank=7,
    )
    assert result.sa_rank == 7
    assert result.afk_rank is None
    assert result.dr_rank is None


def test_player_record_chinese_name():
    record = PlayerRecord(player_name="玩家一号", guild="公会", rank=1)
    assert record.player_name == "玩家一号"
    assert record.guild == "公会"
