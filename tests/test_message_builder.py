from pipeline_notification.contract import NotificationEvent, NotificationMessage
from pipeline_notification.message_builder import (
    build_message_body,
    build_message_title,
    build_notification_message,
    build_notification_messages,
)


def make_event(
    event_type: str = "pipeline_completed",
    severity: str = "info",
    source_status: str = "completed",
) -> NotificationEvent:
    return NotificationEvent(
        pipeline_id="pipeline-001",
        event_type=event_type,
        severity=severity,
        source_status=source_status,
        summary={
            "total_results": 2,
            "successful_results": 2,
            "failed_results": 0,
            "success_rate": 1.0,
        },
    )


def test_build_message_title_completed():
    event = make_event("pipeline_completed")

    assert build_message_title(event) == "Pipeline completed"


def test_build_message_title_failed():
    event = make_event(
        event_type="pipeline_failed",
        severity="error",
        source_status="failed",
    )

    assert build_message_title(event) == "Pipeline failed"


def test_build_message_title_partial():
    event = make_event(
        event_type="pipeline_partial",
        severity="warning",
        source_status="partial",
    )

    assert build_message_title(event) == "Pipeline partially completed"


def test_build_message_body_contains_pipeline_id():
    event = make_event()

    body = build_message_body(event)

    assert "pipeline-001" in body
    assert "completed" in body
    assert "Success rate: 1.00" in body


def test_build_message_body_handles_missing_summary_values():
    event = NotificationEvent(
        pipeline_id="pipeline-001",
        event_type="pipeline_unknown",
        severity="warning",
        source_status="unknown",
        summary={},
    )

    body = build_message_body(event)

    assert "Total results: 0" in body
    assert "Success rate: 0.00" in body


def test_build_notification_message():
    event = make_event()

    message = build_notification_message(event)

    assert isinstance(message, NotificationMessage)
    assert message.title == "Pipeline completed"
    assert message.severity == "info"
    assert "Pipeline pipeline-001 status" in message.body
    assert message.metadata["pipeline_id"] == "pipeline-001"


def test_build_notification_message_failed():
    event = make_event(
        event_type="pipeline_failed",
        severity="error",
        source_status="failed",
    )

    message = build_notification_message(event)

    assert message.title == "Pipeline failed"
    assert message.severity == "error"


def test_build_notification_messages():
    events = [
        make_event("pipeline_completed", "info", "completed"),
        make_event("pipeline_failed", "error", "failed"),
    ]

    messages = build_notification_messages(events)

    assert len(messages) == 2
    assert messages[0].title == "Pipeline completed"
    assert messages[1].title == "Pipeline failed"
