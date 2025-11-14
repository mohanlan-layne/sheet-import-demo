"""Endpoints for managing import jobs and history."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from repositories import CoverageRegionCreate
from services import (
    ImportErrorDetail,
    ImportHistory,
    ImportJobEvent,
    ImportJobRecord,
    ImportSummary,
    import_coverage_regions,
    list_import_jobs,
)


router = APIRouter(prefix="/imports", tags=["imports"])


class ImportRecordPayload(BaseModel):
    code: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    row_number: int | None = Field(default=None, ge=1, alias="rowNumber")

    class Config:
        allow_population_by_field_name = True


class ImportRequest(BaseModel):
    source_filename: str | None = Field(default=None, max_length=255, alias="sourceFilename")
    records: list[ImportRecordPayload] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True


class ImportErrorResponse(BaseModel):
    row_number: int | None = Field(default=None, alias="rowNumber")
    code: str | None = None
    message: str

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def from_domain(cls, error: ImportErrorDetail) -> "ImportErrorResponse":
        return cls(row_number=error.row_number, code=error.code, message=error.message)


class ImportEventResponse(BaseModel):
    level: str
    message: str
    created_at: datetime = Field(alias="createdAt")

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def from_domain(cls, event: ImportJobEvent) -> "ImportEventResponse":
        return cls(level=event.level, message=event.message, created_at=event.created_at)


class ImportJobResponse(BaseModel):
    id: int
    source_filename: str | None = Field(default=None, alias="sourceFilename")
    total_rows: int = Field(alias="totalRows")
    success_count: int = Field(alias="successCount")
    failure_count: int = Field(alias="failureCount")
    status: str
    created_at: datetime = Field(alias="createdAt")
    completed_at: datetime | None = Field(default=None, alias="completedAt")
    errors: list[ImportErrorResponse]
    events: list[ImportEventResponse]

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def from_domain(cls, record: ImportJobRecord) -> "ImportJobResponse":
        return cls(
            id=record.id,
            source_filename=record.source,
            total_rows=record.total_rows,
            success_count=record.success_count,
            failure_count=record.failure_count,
            status=record.status,
            created_at=record.created_at,
            completed_at=record.completed_at,
            errors=[ImportErrorResponse.from_domain(error) for error in record.errors],
            events=[ImportEventResponse.from_domain(event) for event in record.events],
        )


class ImportHistoryResponse(BaseModel):
    page: int
    page_size: int = Field(alias="pageSize")
    total: int
    items: list[ImportJobResponse]

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def from_domain(cls, history: ImportHistory) -> "ImportHistoryResponse":
        return cls(
            page=history.page,
            page_size=history.page_size,
            total=history.total,
            items=[ImportJobResponse.from_domain(item) for item in history.items],
        )


class ImportResponse(BaseModel):
    job_id: int = Field(alias="jobId")
    success_count: int = Field(alias="successCount")
    failure_count: int = Field(alias="failureCount")
    errors: list[ImportErrorResponse]

    class Config:
        allow_population_by_field_name = True

    @classmethod
    def from_summary(cls, summary: ImportSummary) -> "ImportResponse":
        return cls(
            job_id=summary.job_id,
            success_count=summary.success_count,
            failure_count=summary.failure_count,
            errors=[ImportErrorResponse.from_domain(error) for error in summary.errors],
        )


def _to_domain_records(payloads: Iterable[ImportRecordPayload]) -> list[CoverageRegionCreate]:
    return [
        CoverageRegionCreate(
            code=item.code,
            name=item.name,
            description=item.description,
            row_number=item.row_number,
        )
        for item in payloads
    ]


@router.post("/", response_model=ImportResponse, status_code=status.HTTP_201_CREATED)
async def submit_import(request: ImportRequest) -> ImportResponse:
    if not request.records:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="records must not be empty")

    summary = import_coverage_regions(
        _to_domain_records(request.records),
        source=request.source_filename,
    )
    return ImportResponse.from_summary(summary)


@router.get("/", response_model=ImportHistoryResponse)
async def list_import_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100, alias="pageSize"),
) -> ImportHistoryResponse:
    history = list_import_jobs(page=page, page_size=page_size)
    return ImportHistoryResponse.from_domain(history)
