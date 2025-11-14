"""Create tables for tracking import job history."""
from __future__ import annotations

import sqlite3


CREATE_JOBS_SQL = """
CREATE TABLE IF NOT EXISTS import_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT,
    total_rows INTEGER NOT NULL DEFAULT 0,
    success_count INTEGER NOT NULL DEFAULT 0,
    failure_count INTEGER NOT NULL DEFAULT 0,
    errors TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
"""


CREATE_EVENTS_SQL = """
CREATE TABLE IF NOT EXISTS import_job_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(job_id) REFERENCES import_jobs(id) ON DELETE CASCADE
);
"""


CREATE_EVENT_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_import_job_events_job_id
ON import_job_events (job_id);
"""


def upgrade(connection: sqlite3.Connection) -> None:
    """Create the import job tracking tables."""

    cursor = connection.cursor()
    cursor.execute(CREATE_JOBS_SQL)
    cursor.execute(CREATE_EVENTS_SQL)
    cursor.execute(CREATE_EVENT_INDEX_SQL)
    cursor.close()
