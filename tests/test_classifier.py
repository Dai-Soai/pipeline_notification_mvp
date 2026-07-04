import pytest

from pipeline_notification.classifier import (
    classify_execution_report,
    classify_execution_reports,
    classify_status,
    get_event_summary,
)
from pipeline_notification.contract import NotificationEvent


def make_report(status: str = "completed"):
    return {
        "pipeline_id": "pipeline-001",
        "status": status,
        "generated_at": "2026-07-04T20:00:00Z",
        "results": [],
        "summary": {
            "total_results": 2,
            "successful_results": 2,
            "failed_results": 0,
            "success_rate": 1.0,
        },
        "metadata": {
            "source": "pipeline_executor",
        },
    }


def test_classify_status_completed():
    assert classify_status("completed") == ("pipeline_completed", "info")


def test_classify_status_failed():
    assert classify_status("failed") == ("pipeline_failed", "error")


def test_classify_status_partial():
    assert classify_status("partial") == ("pipeline_partial", "warning")


def test_classify_status_empty():
    assert classify_status("empty") == ("pipeline_empty", "info")


def test_classify_status_unknown():
    assert classify_status("weird") == ("pipeline_unknown", "warning")


def test_classify_execution_report_completed():
    event = classify_execution_report(make_report("completed"))

    assert isinstance(event, NotificationEvent)
    assert event.pipeline_id == "pipeline-001"
    assert event.event_type == "pipeline_completed"
    assert event.severity == "info"
    assert event.source_status == "completed"
    assert event.summary["success_rate"] == 1.0


def test_classify_execution_report_failed():
    event = classify_execution_report(make_report("failed"))

    assert event.event_type == "pipeline_failed"
    assert event.severity == "error"


def test_classify_execution_report_partial():
    event = classify_execution_report(make_report("partial"))

    assert event.event_type == "pipeline_partial"
    assert event.severity == "warning"


def test_classify_execution_report_requires_pipeline_id():
    report = make_report()
    report["pipeline_id"] = ""

    with pytest.raises(ValueError):
        classify_execution_report(report)


def test_classify_execution_report_rejects_invalid_summary_type():
    report = make_report()
    report["summary"] = []

    with pytest.raises(TypeError):
        classify_execution_report(report)


def test_classify_execution_reports():
    events = classify_execution_reports(
        [
            make_report("completed"),
            make_report("failed"),
        ]
    )

    assert len(events) == 2
    assert events[0].severity == "info"
    assert events[1].severity == "error"


def test_get_event_summary():
    events = classify_execution_reports(
        [
            make_report("completed"),
            make_report("failed"),
            make_report("partial"),
        ]
    )

    summary = get_event_summary(events)

    assert summary["total_events"] == 3
    assert summary["info_events"] == 1
    assert summary["warning_events"] == 1
    assert summary["error_events"] == 1
