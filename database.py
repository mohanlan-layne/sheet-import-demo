"""Lightweight SQLite database helpers for the demo backend."""
from __future__ import annotations

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
from typing import Iterator


def _resolve_database_target(url: str) -> str:
    if url == "sqlite:///:memory:":
        return ":memory:"
    if url.startswith("sqlite:///"):
        path = Path(url.removeprefix("sqlite:///"))
        if path.parent and path.parent != Path(""):
            path.parent.mkdir(parents=True, exist_ok=True)
        return str(path)
    raise ValueError(f"Unsupported database URL: {url}")


_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sheet_import.db")
_TARGET = _resolve_database_target(_DATABASE_URL)
_IN_MEMORY_CONNECTION: sqlite3.Connection | None = None


def configure_database(url: str) -> None:
    """Switch the active database connection to *url*."""

    global _DATABASE_URL, _TARGET, _IN_MEMORY_CONNECTION

    if _IN_MEMORY_CONNECTION is not None:
        _IN_MEMORY_CONNECTION.close()
        _IN_MEMORY_CONNECTION = None

    _DATABASE_URL = url
    _TARGET = _resolve_database_target(url)


def get_database_url() -> str:
    """Return the currently configured database URL."""

    return _DATABASE_URL


@contextmanager
def session_scope() -> Iterator[sqlite3.Connection]:
    """Provide a transaction scope using a SQLite connection."""

    global _IN_MEMORY_CONNECTION

    if _TARGET == ":memory:":
        if _IN_MEMORY_CONNECTION is None:
            _IN_MEMORY_CONNECTION = sqlite3.connect(_TARGET)
            _IN_MEMORY_CONNECTION.row_factory = sqlite3.Row
        connection = _IN_MEMORY_CONNECTION
        should_close = False
    else:
        connection = sqlite3.connect(_TARGET)
        connection.row_factory = sqlite3.Row
        should_close = True
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        if should_close:
            connection.close()


def initialize_database() -> None:
    """Apply pending migrations to the configured database."""

    from migrations import run_all

    with session_scope() as conn:
        run_all(conn)

