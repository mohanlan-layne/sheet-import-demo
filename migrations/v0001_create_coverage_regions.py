"""Initial migration for the ``coverage_regions`` table."""
from __future__ import annotations

import sqlite3


SQL = """
CREATE TABLE IF NOT EXISTS coverage_regions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


CREATE_TRIGGER_SQL = """
CREATE TRIGGER IF NOT EXISTS trg_coverage_regions_updated
AFTER UPDATE ON coverage_regions
FOR EACH ROW
BEGIN
    UPDATE coverage_regions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
"""


def upgrade(connection: sqlite3.Connection) -> None:
    """Create the base table and update trigger."""

    cursor = connection.cursor()
    cursor.execute(SQL)
    cursor.execute(CREATE_TRIGGER_SQL)
    cursor.close()

