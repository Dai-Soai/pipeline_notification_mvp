import json

import pytest

from pipeline_notification.loader import (
    ExecutionReportLoaderError,
    load_execution_report,
    normalize_execution_report,
)


def test_load_execution_report_from_file(tmp_path):
    report_file = tmp_path / "execution_report.json"
    report_file.write_text(
        json.dumps(
            {
                "pipeline_id": "pipeline-001",
                "status": "completed",
                "generated_at": "2026-07-04T20:00:00Z",
                "results": [],
                "summary": {},
                "metadata": {},
            }
        ),
        encoding="utf-8",
    )

    payload = load_execution_report(report_file)

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["status"] == "completed"
    assert payload["generated_at"] == "2026-07-04T20:00:00Z"
    assert payload["results"] == []


def test_load_execution_report_rejects_missing_file(tmp_path):
    with pytest.raises(ExecutionReportLoaderError):
        load_execution_report(tmp_path / "missing.json")


def test_load_execution_report_rejects_invalid_json(tmp_path):
    report_file = tmp_path / "bad.json"
    report_file.write_text("{bad-json", encoding="utf-8")

    with pytest.raises(ExecutionReportLoaderError):
        load_execution_report(report_file)


def test_load_execution_report_rejects_non_object_json(tmp_path):
    report_file = tmp_path / "list.json"
    report_file.write_text(json.dumps([]), encoding="utf-8")

    with pytest.raises(ExecutionReportLoaderError):
        load_execution_report(report_file)


def test_normalize_execution_report_defaults_optional_fields():
    payload = normalize_execution_report(
        {
            "pipeline_id": "pipeline-001",
            "generated_at": "2026-07-04T20:00:00Z",
            "results": None,
            "summary": {},
            "metadata": {},
        }
    )

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["status"] == "unknown"
    assert payload["results"] == []


def test_normalize_execution_report_rejects_missing_pipeline_id():
    with pytest.raises(ExecutionReportLoaderError):
        normalize_execution_report(
            {
                "generated_at": "2026-07-04T20:00:00Z",
                "results": [],
            }
        )


def test_normalize_execution_report_rejects_missing_generated_at():
    with pytest.raises(ExecutionReportLoaderError):
        normalize_execution_report(
            {
                "pipeline_id": "pipeline-001",
                "results": [],
            }
        )


def test_normalize_execution_report_rejects_invalid_results_type():
    with pytest.raises(ExecutionReportLoaderError):
        normalize_execution_report(
            {
                "pipeline_id": "pipeline-001",
                "generated_at": "2026-07-04T20:00:00Z",
                "results": {},
            }
        )


def test_normalize_execution_report_rejects_invalid_summary_type():
    with pytest.raises(ExecutionReportLoaderError):
        normalize_execution_report(
            {
                "pipeline_id": "pipeline-001",
                "generated_at": "2026-07-04T20:00:00Z",
                "results": [],
                "summary": [],
            }
        )


def test_normalize_execution_report_rejects_invalid_metadata_type():
    with pytest.raises(ExecutionReportLoaderError):
        normalize_execution_report(
            {
                "pipeline_id": "pipeline-001",
                "generated_at": "2026-07-04T20:00:00Z",
                "results": [],
                "summary": {},
                "metadata": [],
            }
        )
