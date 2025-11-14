"""Business logic for importing coverage region data and tracking history."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Sequence

from database import initialize_database, session_scope
from repositories import (
    CoverageRegionCreate,
    CoverageRegionRepository,
    ImportLogRepository,
)


@dataclass(frozen=True, slots=True)
class ImportErrorDetail:
    """Description of an issue encountered during the import."""

    message: str
    row_number: int | None = None
    code: str | None = None

    def to_dict(self) -> dict[str, int | str | None]:
        return {
            "message": self.message,
            "rowNumber": self.row_number,
            "code": self.code,
        }

    @staticmethod
    def from_dict(payload: dict[str, object]) -> "ImportErrorDetail":
        return ImportErrorDetail(
            message=str(payload.get("message", "")),
            row_number=payload.get("rowNumber"),
            code=payload.get("code"),
        )


@dataclass(frozen=True, slots=True)
class ImportJobEvent:
    """Individual event recorded for an import job."""

    level: str
    message: str
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ImportJobRecord:
    """Summary of an import job including recorded events."""

    id: int
    source: str | None
    total_rows: int
    success_count: int
    failure_count: int
    status: str
    created_at: datetime
    completed_at: datetime | None
    errors: tuple[ImportErrorDetail, ...]
    events: tuple[ImportJobEvent, ...]


@dataclass(frozen=True, slots=True)
class ImportHistory:
    """Paginated view of persisted import jobs."""

    page: int
    page_size: int
    total: int
    items: tuple[ImportJobRecord, ...]


@dataclass(frozen=True, slots=True)
class ImportSummary:
    """Outcome of a bulk import operation."""

    job_id: int
    success_count: int
    failure_count: int
    errors: tuple[ImportErrorDetail, ...]


def _normalise_records(
    records: Iterable[CoverageRegionCreate],
) -> tuple[list[CoverageRegionCreate], list[ImportErrorDetail]]:
    """Normalise and de-duplicate incoming *records* by code."""

    seen: dict[str, CoverageRegionCreate] = {}
    errors: list[ImportErrorDetail] = []

    for record in records:
        row_number = record.row_number
        normalised_code = record.code.strip() if record.code else ""
        if not normalised_code:
            errors.append(
                ImportErrorDetail(
                    message="Region code is required.",
                    row_number=row_number,
                    code=None,
                )
            )
            continue

        if normalised_code in seen:
            errors.append(
                ImportErrorDetail(
                    message="Duplicate region code in upload payload.",
                    row_number=row_number,
                    code=normalised_code,
                )
            )
            continue

        seen[normalised_code] = CoverageRegionCreate(
            code=normalised_code,
            name=record.name.strip(),
            description=record.description.strip() if record.description else None,
            row_number=row_number,
        )

    return list(seen.values()), errors


def import_coverage_regions(
    records: Sequence[CoverageRegionCreate],
    *,
    source: str | None = None,
) -> ImportSummary:
    """Persist *records* while enforcing idempotency semantics."""

    initialize_database()
    total_rows = len(records)
    errors: list[ImportErrorDetail] = []

    with session_scope() as session:
        log_repository = ImportLogRepository(session)
        job_id = log_repository.create_job(source, total_rows)
        log_repository.append_event(job_id, f"Import started with {total_rows} rows")

    normalised, normalisation_errors = _normalise_records(records)
    errors.extend(normalisation_errors)

    with session_scope() as session:
        log_repository = ImportLogRepository(session)
        log_repository.append_event(
            job_id,
            f"Normalised payload produced {len(normalised)} unique rows with {len(normalisation_errors)} validation errors",
        )

    if not normalised:
        failure_count = len(errors)
        with session_scope() as session:
            log_repository = ImportLogRepository(session)
            log_repository.finalise_job(
                job_id,
                success_count=0,
                failure_count=failure_count,
                errors=(error.to_dict() for error in errors),
                status="completed",
            )
        return ImportSummary(job_id=job_id, success_count=0, failure_count=failure_count, errors=tuple(errors))

    code_to_record = {record.code: record for record in normalised}

    try:
        with session_scope() as session:
            repository = CoverageRegionRepository(session)
            log_repository = ImportLogRepository(session)

            existing_codes = repository.fetch_existing_codes(code_to_record.keys())
            if existing_codes:
                for code in sorted(existing_codes):
                    skipped_record = code_to_record.get(code)
                    errors.append(
                        ImportErrorDetail(
                            message="Region code already exists in database.",
                            row_number=skipped_record.row_number if skipped_record else None,
                            code=code,
                        )
                    )
                log_repository.append_event(
                    job_id,
                    f"Skipped {len(existing_codes)} rows that already exist",
                )

            pending = [record for record in normalised if record.code not in existing_codes]
            inserted = repository.bulk_insert(pending)

            if inserted < len(pending):
                errors.append(
                    ImportErrorDetail(
                        message="Database constraints prevented inserting some rows.",
                        row_number=None,
                        code=None,
                    )
                )
                log_repository.append_event(
                    job_id,
                    "One or more rows could not be inserted due to database constraints",
                    level="WARNING",
                )

            log_repository.append_event(job_id, f"Inserted {inserted} new rows")

    except Exception as exc:  # pragma: no cover - defensive safety net
        errors.append(
            ImportErrorDetail(
                message=f"Unexpected error: {exc}",
                row_number=None,
                code=None,
            )
        )
        with session_scope() as session:
            log_repository = ImportLogRepository(session)
            log_repository.append_event(job_id, f"Import failed: {exc}", level="ERROR")
            log_repository.finalise_job(
                job_id,
                success_count=0,
                failure_count=len(errors),
                errors=(error.to_dict() for error in errors),
                status="failed",
            )
        raise

    success_count = inserted
    failure_count = len(errors)

    with session_scope() as session:
        log_repository = ImportLogRepository(session)
        log_repository.finalise_job(
            job_id,
            success_count=success_count,
            failure_count=failure_count,
            errors=(error.to_dict() for error in errors),
            status="completed",
        )

    return ImportSummary(
        job_id=job_id,
        success_count=success_count,
        failure_count=failure_count,
        errors=tuple(errors),
    )


def list_import_jobs(*, page: int, page_size: int) -> ImportHistory:
    """Return a paginated view of import job history."""

    initialize_database()
    offset = max(page - 1, 0) * page_size

    with session_scope() as session:
        repository = ImportLogRepository(session)
        raw_jobs, total = repository.fetch_jobs(limit=page_size, offset=offset)

    items: list[ImportJobRecord] = []
    for job in raw_jobs:
        errors = tuple(ImportErrorDetail.from_dict(item) for item in job.errors)
        events = tuple(
            ImportJobEvent(level=event.level, message=event.message, created_at=event.created_at)
            for event in job.events
        )
        items.append(
            ImportJobRecord(
                id=job.id,
                source=job.source,
                total_rows=job.total_rows,
                success_count=job.success_count,
                failure_count=job.failure_count,
                status=job.status,
                created_at=job.created_at,
                completed_at=job.completed_at,
                errors=errors,
                events=events,
            )
        )

    return ImportHistory(
        page=page,
        page_size=page_size,
        total=total,
        items=tuple(items),
    )
