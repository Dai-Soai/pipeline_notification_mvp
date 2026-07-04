import json

import pytest

from pipeline_notification.contract import (
    ChannelPayload,
    NotificationEvent,
    NotificationMessage,
    NotificationReport,
)
from pipeline_notification.report import (
    build_notification_report,
    build_notification_summary,
    determine_notification_report_status,
    notification_report_to_dict,
    write_notification_report_json,
)


def make_event(severity: str = "info") -> NotificationEvent:
    return NotificationEvent(
        pipeline_id="pipeline-001",
        event_type="pipeline_completed",
        severity=severity,
        source_status="completed",
        summary={"success_rate": 1.0},
    )


def make_message(severity: str = "info") -> NotificationMessage:
    return NotificationMessage(
        title="Pipeline completed",
        body="Pipeline pipeline-001 completed successfully.",
        severity=severity,
    )


def make_payload(severity: str = "info") -> ChannelPayload:
    return ChannelPayload(
        channel="console",
        target="stdout",
        title="Pipeline completed",
        message="Pipeline pipeline-001 completed successfully.",
        severity=severity,
    )


def test_build_notification_summary():
    summary = build_notification_summary(
        events=[make_event("info"), make_event("error")],
        messages=[make_message()],
        payloads=[make_payload()],
    )

    assert summary["total_events"] == 2
    assert summary["total_messages"] == 1
    assert summary["total_payloads"] == 1
    assert summary["info_events"] == 1
    assert summary["error_events"] == 1


def test_determine_notification_report_status_empty():
    assert determine_notification_report_status([], [], []) == "empty"


def test_determine_notification_report_status_ready():
    assert determine_notification_report_status(
        [make_event()],
        [make_message()],
        [make_payload()],
    ) == "ready"


def test_determine_notification_report_status_invalid():
    assert determine_notification_report_status(
        [make_event()],
        [],
        [],
    ) == "invalid"


def test_build_notification_report():
    report = build_notification_report(
        pipeline_id="pipeline-001",
        events=[make_event()],
        messages=[make_message()],
        payloads=[make_payload()],
        metadata={"source": "test"},
    )

    assert isinstance(report, NotificationReport)
    assert report.pipeline_id == "pipeline-001"
    assert report.status == "ready"
    assert report.summary["total_events"] == 1
    assert report.metadata["source"] == "test"


def test_build_notification_report_rejects_missing_pipeline_id():
    with pytest.raises(ValueError):
        build_notification_report(
            pipeline_id="",
            events=[],
            messages=[],
            payloads=[],
        )


def test_notification_report_to_dict():
    report = build_notification_report(
        pipeline_id="pipeline-001",
        events=[make_event()],
        messages=[make_message()],
        payloads=[make_payload()],
    )

    payload = notification_report_to_dict(report)

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["status"] == "ready"
    assert payload["events"][0]["event_type"] == "pipeline_completed"
    assert payload["messages"][0]["title"] == "Pipeline completed"
    assert payload["payloads"][0]["channel"] == "console"


def test_notification_report_to_dict_rejects_invalid_report():
    with pytest.raises(TypeError):
        notification_report_to_dict({"bad": "report"})


def test_write_notification_report_json(tmp_path):
    report = build_notification_report(
        pipeline_id="pipeline-001",
        events=[make_event()],
        messages=[make_message()],
        payloads=[make_payload()],
    )
    output_file = tmp_path / "notification_report.json"

    written_path = write_notification_report_json(report, output_file)

    assert written_path == output_file
    assert output_file.exists()

    payload = json.loads(output_file.read_text(encoding="utf-8"))

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["status"] == "ready"


def test_write_notification_report_json_creates_parent_directory(tmp_path):
    report = build_notification_report(
        pipeline_id="pipeline-001",
        events=[make_event()],
        messages=[make_message()],
        payloads=[make_payload()],
    )
    output_file = tmp_path / "nested" / "notification_report.json"

    write_notification_report_json(report, output_file)

    assert output_file.exists()
