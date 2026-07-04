import pytest

from pipeline_notification.contract import (
    ChannelPayload,
    NotificationEvent,
    NotificationMessage,
    NotificationReport,
)


def test_notification_event_creation():
    event = NotificationEvent(
        pipeline_id="pipeline-001",
        event_type="pipeline_completed",
        severity="info",
        source_status="completed",
        summary={"success_rate": 1.0},
    )

    assert event.pipeline_id == "pipeline-001"
    assert event.event_type == "pipeline_completed"
    assert event.severity == "info"
    assert event.summary["success_rate"] == 1.0


def test_notification_event_rejects_invalid_event_type():
    with pytest.raises(ValueError):
        NotificationEvent(
            pipeline_id="pipeline-001",
            event_type="bad",
            severity="info",
            source_status="completed",
        )


def test_notification_event_rejects_invalid_summary_type():
    with pytest.raises(TypeError):
        NotificationEvent(
            pipeline_id="pipeline-001",
            event_type="pipeline_completed",
            severity="info",
            source_status="completed",
            summary=[],
        )


def test_notification_message_creation():
    message = NotificationMessage(
        title="Pipeline completed",
        body="Pipeline pipeline-001 completed successfully.",
        severity="info",
    )

    assert message.title == "Pipeline completed"
    assert message.severity == "info"


def test_notification_message_rejects_empty_title():
    with pytest.raises(ValueError):
        NotificationMessage(
            title="",
            body="Body",
            severity="info",
        )


def test_channel_payload_creation():
    payload = ChannelPayload(
        channel="telegram",
        target="radar-alerts",
        title="Pipeline completed",
        message="Pipeline completed successfully.",
        severity="info",
    )

    assert payload.channel == "telegram"
    assert payload.target == "radar-alerts"


def test_channel_payload_rejects_invalid_channel():
    with pytest.raises(ValueError):
        ChannelPayload(
            channel="sms",
            target="radar-alerts",
            title="Pipeline completed",
            message="Done",
            severity="info",
        )


def test_notification_report_creation():
    event = NotificationEvent(
        pipeline_id="pipeline-001",
        event_type="pipeline_completed",
        severity="info",
        source_status="completed",
    )
    message = NotificationMessage(
        title="Pipeline completed",
        body="Pipeline pipeline-001 completed successfully.",
        severity="info",
    )
    payload = ChannelPayload(
        channel="console",
        target="stdout",
        title=message.title,
        message=message.body,
        severity=message.severity,
    )

    report = NotificationReport(
        pipeline_id="pipeline-001",
        status="ready",
        events=[event],
        messages=[message],
        payloads=[payload],
    )

    assert report.pipeline_id == "pipeline-001"
    assert report.status == "ready"
    assert len(report.events) == 1
    assert len(report.messages) == 1
    assert len(report.payloads) == 1


def test_notification_report_rejects_invalid_event_type():
    with pytest.raises(TypeError):
        NotificationReport(
            pipeline_id="pipeline-001",
            status="ready",
            events=["bad-event"],
            messages=[],
            payloads=[],
        )


def test_notification_report_rejects_invalid_status():
    with pytest.raises(ValueError):
        NotificationReport(
            pipeline_id="pipeline-001",
            status="bad",
            events=[],
            messages=[],
            payloads=[],
        )
