"""Repository helpers backed by SQLite."""
from __future__ import annotations

from dataclasses import dataclass
import sqlite3
from typing import Iterable, Sequence


@dataclass(frozen=True, slots=True)
class CoverageRegionCreate:
    """Schema describing a region to be persisted."""

    code: str
    name: str
    description: str | None = None
    row_number: int | None = None


class CoverageRegionRepository:
    """Data access helpers for coverage regions."""

    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def fetch_existing_codes(self, codes: Iterable[str]) -> set[str]:
        """Return the subset of *codes* already persisted."""

        codes_list = [code for code in codes]
        if not codes_list:
            return set()

        placeholders = ",".join("?" for _ in codes_list)
        query = f"SELECT code FROM coverage_regions WHERE code IN ({placeholders})"
        cursor = self._connection.execute(query, codes_list)
        existing = {row[0] for row in cursor.fetchall()}
        cursor.close()
        return existing

    def bulk_insert(self, records: Sequence[CoverageRegionCreate]) -> int:
        """Persist *records* in a single batch and return the inserted count."""

        if not records:
            return 0

        payload = [(item.code, item.name, item.description) for item in records]
        before = self._connection.total_changes
        self._connection.executemany(
            "INSERT OR IGNORE INTO coverage_regions (code, name, description) VALUES (?, ?, ?)",
            payload,
        )
        return self._connection.total_changes - before

