"""Utilities for parsing spreadsheet-like data sources.

This module chooses an appropriate parser implementation based on the
input file extension, validates the parsed rows against a configurable
schema and returns a structured result that contains both the accepted
rows and the validation errors.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Tuple
from collections.abc import Sequence
import csv
import json
import pathlib

Row = Dict[str, Any]
Validator = Callable[[Any], Any]
Schema = Mapping[str, Validator]


@dataclass(frozen=True)
class ValidationIssue:
    """Description of a validation failure for a specific field."""

    row_number: int
    field: str
    reason: str


@dataclass
class ParseResult:
    """Structured result of a parsing operation."""

    rows: List[Row] = field(default_factory=list)
    errors: List[ValidationIssue] = field(default_factory=list)


class UnsupportedExtensionError(ValueError):
    """Raised when no parser is registered for the given file extension."""


def parse_data(
    file_content: str,
    *,
    filename: str,
    schema: Optional[Schema] = None,
) -> ParseResult:
    """Parse *file_content* using the parser determined by ``filename``.

    Parameters
    ----------
    file_content:
        The textual content of the uploaded file.  This module operates on text
        to avoid leaking file handles to consumers.
    filename:
        The name of the file as provided by the user.  The suffix determines the
        parser that will be used.
    schema:
        Optional mapping of field name to validator function.  Validators should
        accept a value and return ``None``/``True`` when the value is valid.
        Returning a string marks the value as invalid and uses the string as the
        error message.  Returning ``False`` results in a generic error message.

    Returns
    -------
    ParseResult
        A ``ParseResult`` instance that contains validated rows in
        ``ParseResult.rows`` and validation errors in ``ParseResult.errors``.
    """

    extension = pathlib.Path(filename).suffix.lower()
    try:
        parser, starting_row = _PARSERS[extension]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise UnsupportedExtensionError(f"Unsupported file extension: {extension}") from exc

    raw_rows = parser(file_content)
    return _validate_rows(raw_rows, schema or {}, starting_row)


def _parse_csv(file_content: str) -> List[Row]:
    reader = csv.DictReader(file_content.splitlines())
    return [dict(row) for row in reader]


def _parse_json(file_content: str) -> List[Row]:
    data = json.loads(file_content or "[]")
    if isinstance(data, Mapping):
        data = [data]
    if not isinstance(data, Sequence) or isinstance(data, (str, bytes)):
        raise ValueError("JSON data must be an object or array of objects")

    rows: List[Row] = []
    for item in data:
        if not isinstance(item, Mapping):
            raise ValueError("JSON array must contain objects")
        rows.append(dict(item))
    return rows


_PARSERS: Dict[str, Tuple[Callable[[str], List[Row]], int]] = {
    ".csv": (_parse_csv, 2),
    ".json": (_parse_json, 1),
}


def register_parser(extension: str, parser: Callable[[str], List[Row]], *, starting_row: int = 1) -> None:
    """Register a parser for *extension* at runtime.

    ``extension`` must include the leading ``.``.  Registered parsers override
    existing ones, which allows consumers to provide project-specific parsing
    logic for formats such as XLSX.
    """

    if not extension.startswith('.'):
        raise ValueError("Extension must start with a dot (.)")
    _PARSERS[extension.lower()] = (parser, starting_row)


def _validate_rows(rows: Iterable[Row], schema: Schema, starting_row: int) -> ParseResult:
    parsed_rows: List[Row] = []
    errors: List[ValidationIssue] = []

    for index, row in enumerate(rows, start=starting_row):
        row_errors = _validate_row(row, index, schema)
        if row_errors:
            errors.extend(row_errors)
        else:
            parsed_rows.append(row)

    return ParseResult(rows=parsed_rows, errors=errors)


def _validate_row(row: Row, row_number: int, schema: Schema) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    for field_name, validator in schema.items():
        if field_name not in row:
            issues.append(
                ValidationIssue(
                    row_number=row_number,
                    field=field_name,
                    reason="Missing value",
                )
            )
            continue

        value = row[field_name]
        reason = _execute_validator(validator, value)
        if reason is not None:
            issues.append(
                ValidationIssue(
                    row_number=row_number,
                    field=field_name,
                    reason=reason,
                )
            )

    return issues


def _execute_validator(validator: Validator, value: Any) -> Optional[str]:
    try:
        result = validator(value)
    except Exception as exc:  # pragma: no cover - defensive, logged upstream
        return f"Validator raised {exc.__class__.__name__}: {exc}"

    if result is None or result is True:
        return None
    if result is False:
        return "Invalid value"
    if isinstance(result, str):
        return result
    if isinstance(result, tuple) and len(result) == 2:
        is_valid, message = result
        if is_valid:
            return None
        return message or "Invalid value"

    raise TypeError(
        "Validator must return None/True for valid values, False for invalid values, "
        "or a string/tuple describing the error"
    )
