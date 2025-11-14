"""Simple migration runner used by the demo backend."""
from __future__ import annotations

import sqlite3

from . import v0001_create_coverage_regions, v0002_create_import_logs


def run_all(connection: sqlite3.Connection) -> None:
    """Apply all migrations in order."""

    migrations = [
        v0001_create_coverage_regions.upgrade,
        v0002_create_import_logs.upgrade,
    ]
    for upgrade in migrations:
        upgrade(connection)

