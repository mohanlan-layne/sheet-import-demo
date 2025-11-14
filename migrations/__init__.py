"""Simple migration runner used by the demo backend."""
from __future__ import annotations

import sqlite3

from . import v0001_create_coverage_regions


def run_all(connection: sqlite3.Connection) -> None:
    """Apply all migrations in order."""

    migrations = [v0001_create_coverage_regions.upgrade]
    for upgrade in migrations:
        upgrade(connection)

