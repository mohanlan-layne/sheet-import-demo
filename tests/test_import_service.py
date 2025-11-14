from __future__ import annotations

import pytest

from database import configure_database, initialize_database
from repositories import CoverageRegionCreate
from services import import_coverage_regions


@pytest.fixture(autouse=True)
def temp_database(tmp_path):
    configure_database(f"sqlite:///{tmp_path / 'test.db'}")
    initialize_database()
    yield


def test_import_regions_inserts_new_rows() -> None:
    summary = import_coverage_regions(
        [
            CoverageRegionCreate(code="CN-110000", name="北京", description="重点客户数量 120"),
            CoverageRegionCreate(code="CN-310000", name="上海", description="重点客户数量 86"),
        ]
    )

    assert summary.inserted == 2
    assert summary.skipped == 0


def test_import_regions_is_idempotent() -> None:
    summary_first = import_coverage_regions(
        [
            CoverageRegionCreate(code="CN-110000", name="北京"),
            CoverageRegionCreate(code="CN-110000", name="北京"),
            CoverageRegionCreate(code="CN-440300", name="深圳"),
        ]
    )
    assert summary_first.inserted == 2
    assert summary_first.skipped == 1

    summary_second = import_coverage_regions(
        [
            CoverageRegionCreate(code="CN-110000", name="北京"),
            CoverageRegionCreate(code="CN-510100", name="成都"),
        ]
    )

    assert summary_second.inserted == 1
    assert summary_second.skipped == 1

