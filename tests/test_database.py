"""Tests for storage.database module."""

from datetime import date
from pathlib import Path

import pytest

from models import ScanResult
from storage.database import Database


@pytest.fixture
def db(tmp_path: Path) -> Database:
    """Create a fresh in-memory-like DB for each test."""
    return Database(tmp_path / "test.db")


@pytest.fixture
def sample_results() -> list[ScanResult]:
    return [
        ScanResult(
            player_name="Alice",
            guild="G1",
            scan_date=date(2026, 3, 9),
            afk_rank=1,
            afk_stage="1452",
            dr_rank=2,
            dr_score="169B",
        ),
        ScanResult(
            player_name="Bob",
            guild="G1",
            scan_date=date(2026, 3, 9),
            sa_rank=5,
        ),
        ScanResult(player_name="玩家", guild="公会", scan_date=date(2026, 3, 9), hd_rank=10),
    ]


class TestDatabaseInit:
    def test_creates_db_file(self, tmp_path: Path):
        db_path = tmp_path / "new.db"
        db = Database(db_path)
        assert db_path.exists()
        db.close()

    def test_schema_creates_scans_table(self, db: Database):
        cursor = db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='scans'"
        )
        assert cursor.fetchone() is not None


class TestUpsertResults:
    def test_insert_records(self, db: Database, sample_results: list[ScanResult]):
        count = db.upsert_results(sample_results)
        assert count == 3

    def test_empty_list_returns_zero(self, db: Database):
        assert db.upsert_results([]) == 0

    def test_upsert_replaces_existing(self, db: Database):
        original = ScanResult(
            player_name="Alice",
            guild="G1",
            scan_date=date(2026, 3, 9),
            afk_rank=1,
            afk_stage="1000",
        )
        db.upsert_results([original])

        updated = ScanResult(
            player_name="Alice",
            guild="G1",
            scan_date=date(2026, 3, 9),
            afk_rank=1,
            afk_stage="1452",
        )
        db.upsert_results([updated])

        results = db.get_results_for_date(date(2026, 3, 9))
        assert len(results) == 1
        assert results[0].afk_stage == "1452"

    def test_different_dates_are_separate(self, db: Database):
        r1 = ScanResult(player_name="Alice", guild="G1", scan_date=date(2026, 3, 9), sa_rank=1)
        r2 = ScanResult(player_name="Alice", guild="G1", scan_date=date(2026, 3, 10), sa_rank=2)
        db.upsert_results([r1, r2])

        assert len(db.get_results_for_date(date(2026, 3, 9))) == 1
        assert len(db.get_results_for_date(date(2026, 3, 10))) == 1


class TestHasDataForDate:
    def test_no_data(self, db: Database):
        assert db.has_data_for_date(date(2026, 3, 9)) is False

    def test_has_data(self, db: Database, sample_results: list[ScanResult]):
        db.upsert_results(sample_results)
        assert db.has_data_for_date(date(2026, 3, 9)) is True

    def test_wrong_date(self, db: Database, sample_results: list[ScanResult]):
        db.upsert_results(sample_results)
        assert db.has_data_for_date(date(2026, 3, 10)) is False


class TestGetResultsForDate:
    def test_returns_all_for_date(self, db: Database, sample_results: list[ScanResult]):
        db.upsert_results(sample_results)
        results = db.get_results_for_date(date(2026, 3, 9))
        assert len(results) == 3

    def test_results_are_scan_result_instances(
        self, db: Database, sample_results: list[ScanResult]
    ):
        db.upsert_results(sample_results)
        results = db.get_results_for_date(date(2026, 3, 9))
        assert all(isinstance(r, ScanResult) for r in results)

    def test_preserves_nullable_fields(self, db: Database, sample_results: list[ScanResult]):
        db.upsert_results(sample_results)
        results = db.get_results_for_date(date(2026, 3, 9))
        bob = next(r for r in results if r.player_name == "Bob")
        assert bob.sa_rank == 5
        assert bob.afk_rank is None
        assert bob.dr_score is None

    def test_empty_date_returns_empty(self, db: Database):
        assert db.get_results_for_date(date(2026, 1, 1)) == []


class TestGetPlayerHistory:
    def test_returns_player_across_dates(self, db: Database):
        results = [
            ScanResult(player_name="Alice", guild="G1", scan_date=date(2026, 3, d), sa_rank=d)
            for d in range(1, 4)
        ]
        db.upsert_results(results)
        history = db.get_player_history("Alice", "G1")
        assert len(history) == 3
        assert [r.scan_date.day for r in history] == [1, 2, 3]

    def test_different_guild_same_name(self, db: Database):
        r1 = ScanResult(player_name="Alice", guild="G1", scan_date=date(2026, 3, 9), sa_rank=1)
        r2 = ScanResult(player_name="Alice", guild="G2", scan_date=date(2026, 3, 9), sa_rank=2)
        db.upsert_results([r1, r2])

        g1 = db.get_player_history("Alice", "G1")
        g2 = db.get_player_history("Alice", "G2")
        assert len(g1) == 1
        assert len(g2) == 1
        assert g1[0].sa_rank == 1
        assert g2[0].sa_rank == 2

    def test_chinese_player_name(self, db: Database, sample_results: list[ScanResult]):
        db.upsert_results(sample_results)
        history = db.get_player_history("玩家", "公会")
        assert len(history) == 1
        assert history[0].hd_rank == 10
