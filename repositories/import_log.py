"""Repository helpers for persisting import job logs."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import sqlite3
from typing import Any, Iterable


def _parse_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    # SQLite stores ``CURRENT_TIMESTAMP`` as ``YYYY-MM-DD HH:MM:SS``
    return datetime.fromisoformat(value)


@dataclass(frozen=True, slots=True)
class ImportJobEventRow:
    """Raw event information fetched from the persistence layer."""

    level: str
    message: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ImportJobRow:
    """Raw import job summary fetched from the persistence layer."""

    id: int
    source: str | None
    total_rows: int
    success_count: int
    failure_count: int
    status: str
    errors: list[dict[str, Any]]
    created_at: datetime
    completed_at: datetime | None
    events: tuple[ImportJobEventRow, ...]


class ImportLogRepository:
    """Read/write helpers for import job audit information."""

    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def create_job(self, source: str | None, total_rows: int) -> int:
        cursor = self._connection.execute(
            """
            INSERT INTO import_jobs (source, total_rows, status)
            VALUES (?, ?, 'running')
            """,
            (source, total_rows),
        )
        job_id = int(cursor.lastrowid)
        cursor.close()
        return job_id

    def append_event(self, job_id: int, message: str, level: str = "INFO") -> None:
        self._connection.execute(
            """
            INSERT INTO import_job_events (job_id, level, message)
            VALUES (?, ?, ?)
            """,
            (job_id, level, message),
        )

    def finalise_job(
        self,
        job_id: int,
        *,
        success_count: int,
        failure_count: int,
        errors: Iterable[dict[str, Any]],
        status: str,
    ) -> None:
        self._connection.execute(
            """
            UPDATE import_jobs
            SET success_count = ?,
                failure_count = ?,
                errors = ?,
                status = ?,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                success_count,
                failure_count,
                json.dumps(list(errors), ensure_ascii=False),
                status,
                job_id,
            ),
        )

    def fetch_jobs(self, *, limit: int, offset: int) -> tuple[list[ImportJobRow], int]:
        total_cursor = self._connection.execute("SELECT COUNT(*) FROM import_jobs")
        total_row = total_cursor.fetchone()
        total_cursor.close()
        total = int(total_row[0] if total_row and total_row[0] is not None else 0)

        cursor = self._connection.execute(
            """
            SELECT id, source, total_rows, success_count, failure_count, status, errors, created_at, completed_at
            FROM import_jobs
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )

        jobs: list[ImportJobRow] = []
        for row in cursor.fetchall():
            events_cursor = self._connection.execute(
                """
                SELECT level, message, created_at
                FROM import_job_events
                WHERE job_id = ?
                ORDER BY created_at ASC
                """,
                (row["id"],),
            )
            events = tuple(
                ImportJobEventRow(
                    level=event_row["level"],
                    message=event_row["message"],
                    created_at=_parse_timestamp(event_row["created_at"]),
                )
                for event_row in events_cursor.fetchall()
            )
            events_cursor.close()
            jobs.append(
                ImportJobRow(
                    id=row["id"],
                    source=row["source"],
                    total_rows=row["total_rows"],
                    success_count=row["success_count"],
                    failure_count=row["failure_count"],
                    status=row["status"],
                    errors=json.loads(row["errors"] or "[]"),
                    created_at=_parse_timestamp(row["created_at"]),
                    completed_at=_parse_timestamp(row["completed_at"]),
                    events=events,
                )
            )

        cursor.close()
        return jobs, total
