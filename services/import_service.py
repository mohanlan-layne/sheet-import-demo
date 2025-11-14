"""Business logic for importing coverage region data."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from database import initialize_database, session_scope
from repositories import CoverageRegionCreate, CoverageRegionRepository


@dataclass(frozen=True, slots=True)
class ImportSummary:
    """Outcome of a bulk import operation."""

    inserted: int
    skipped: int


def _normalise_records(
    records: Iterable[CoverageRegionCreate],
) -> tuple[list[CoverageRegionCreate], int]:
    """Normalise and de-duplicate incoming *records* by code.

    Returns a tuple containing the unique records and the number of skipped
    entries caused by empty codes or duplicates within the same payload.
    """

    seen: dict[str, CoverageRegionCreate] = {}
    skipped = 0
    for record in records:
        normalised_code = record.code.strip()
        if not normalised_code:
            skipped += 1
            continue

        if normalised_code in seen:
            skipped += 1
            continue

        seen[normalised_code] = CoverageRegionCreate(
            code=normalised_code,
            name=record.name.strip(),
            description=record.description.strip() if record.description else None,
        )
    return list(seen.values()), skipped


def import_coverage_regions(records: Sequence[CoverageRegionCreate]) -> ImportSummary:
    """Persist *records* while enforcing idempotency semantics."""

    initialize_database()

    normalised, skipped = _normalise_records(records)
    if not normalised:
        return ImportSummary(inserted=0, skipped=skipped)

    with session_scope() as session:
        repository = CoverageRegionRepository(session)
        existing_codes = repository.fetch_existing_codes(record.code for record in normalised)
        pending = [record for record in normalised if record.code not in existing_codes]
        inserted = repository.bulk_insert(pending)
        skipped += len(normalised) - inserted
        return ImportSummary(inserted=inserted, skipped=skipped)

