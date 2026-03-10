"""SQLite storage for scan results."""

import logging
import sqlite3
from datetime import date
from pathlib import Path

from config import DB_SCHEMA
from models import ScanResult

logger = logging.getLogger(__name__)


class Database:
    """SQLite wrapper for the scans table."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute(DB_SCHEMA)
        self.conn.commit()

    def has_data_for_date(self, scan_date: date) -> bool:
        """Check if any scan data exists for the given date."""
        cursor = self.conn.execute(
            "SELECT 1 FROM scans WHERE scan_date = ? LIMIT 1",
            (scan_date.isoformat(),),
        )
        return cursor.fetchone() is not None

    def upsert_results(self, results: list[ScanResult]) -> int:
        """Insert or replace scan results in a single transaction.

        Returns the number of rows upserted.
        """
        if not results:
            return 0

        sql = """\
            INSERT OR REPLACE INTO scans
                (player_name, guild, scan_date,
                 afk_rank, afk_stage, dr_rank, dr_score,
                 sa_rank, al_rank, hd_rank)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        rows = [
            (
                r.player_name,
                r.guild,
                r.scan_date.isoformat(),
                r.afk_rank,
                r.afk_stage,
                r.dr_rank,
                r.dr_score,
                r.sa_rank,
                r.al_rank,
                r.hd_rank,
            )
            for r in results
        ]

        with self.conn:
            self.conn.executemany(sql, rows)

        logger.info("Upserted %d scan results to %s", len(rows), self.db_path)
        return len(rows)

    def get_results_for_date(self, scan_date: date) -> list[ScanResult]:
        """Retrieve all scan results for a given date."""
        cursor = self.conn.execute(
            "SELECT * FROM scans WHERE scan_date = ? ORDER BY player_name",
            (scan_date.isoformat(),),
        )
        return [self._row_to_result(row) for row in cursor.fetchall()]

    def get_player_history(self, player_name: str, guild: str) -> list[ScanResult]:
        """Retrieve all scan results for a specific player."""
        cursor = self.conn.execute(
            "SELECT * FROM scans WHERE player_name = ? AND guild = ? ORDER BY scan_date",
            (player_name, guild),
        )
        return [self._row_to_result(row) for row in cursor.fetchall()]

    @staticmethod
    def _row_to_result(row: sqlite3.Row) -> ScanResult:
        return ScanResult(
            player_name=row["player_name"],
            guild=row["guild"],
            scan_date=date.fromisoformat(row["scan_date"]),
            afk_rank=row["afk_rank"],
            afk_stage=row["afk_stage"],
            dr_rank=row["dr_rank"],
            dr_score=row["dr_score"],
            sa_rank=row["sa_rank"],
            al_rank=row["al_rank"],
            hd_rank=row["hd_rank"],
        )

    def close(self) -> None:
        self.conn.close()
