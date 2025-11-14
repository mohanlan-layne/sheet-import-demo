from __future__ import annotations

import pytest

from database import configure_database, initialize_database
from repositories import CoverageRegionCreate
from services import import_coverage_regions, list_import_jobs


@pytest.fixture(autouse=True)
def temp_database(tmp_path):
    configure_database(f"sqlite:///{tmp_path / 'test.db'}")
    initialize_database()
    yield


def test_import_regions_inserts_new_rows() -> None:
    summary = import_coverage_regions(
        [
            CoverageRegionCreate(code="CN-110000", name="北京", description="重点客户数量 120", row_number=2),
            CoverageRegionCreate(code="CN-310000", name="上海", description="重点客户数量 86", row_number=3),
        ],
        source="coverage.csv",
    )

    assert summary.job_id > 0
    assert summary.success_count == 2
    assert summary.failure_count == 0
    assert summary.errors == ()

    history = list_import_jobs(page=1, page_size=10)
    assert history.total == 1
    assert len(history.items) == 1

    job = history.items[0]
    assert job.id == summary.job_id
    assert job.success_count == summary.success_count
    assert job.failure_count == summary.failure_count
    assert job.total_rows == 2
    assert job.source == "coverage.csv"
    assert len(job.events) >= 2


def test_import_regions_is_idempotent() -> None:
    summary_first = import_coverage_regions(
        [
            CoverageRegionCreate(code="CN-110000", name="北京", row_number=2),
            CoverageRegionCreate(code="CN-110000", name="北京", row_number=3),
            CoverageRegionCreate(code="CN-440300", name="深圳", row_number=4),
        ]
    )
    assert summary_first.success_count == 2
    assert summary_first.failure_count == 1
    assert len(summary_first.errors) == 1
    assert summary_first.errors[0].code == "CN-110000"
    assert "Duplicate" in summary_first.errors[0].message

    summary_second = import_coverage_regions(
        [
            CoverageRegionCreate(code="CN-110000", name="北京", row_number=5),
            CoverageRegionCreate(code="CN-510100", name="成都", row_number=6),
        ]
    )

    assert summary_second.success_count == 1
    assert summary_second.failure_count == 1
    assert len(summary_second.errors) == 1
    assert summary_second.errors[0].code == "CN-110000"
    assert "already exists" in summary_second.errors[0].message

