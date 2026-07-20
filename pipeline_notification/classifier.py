from typing import Any

from pipeline_notification.contract import NotificationEvent


STATUS_TO_EVENT = {
    "completed": ("pipeline_completed", "info"),
    "failed": ("pipeline_failed", "error"),
    "partial": ("pipeline_partial", "warning"),
    "empty": ("pipeline_empty", "info"),
}


def classify_status(status: str) -> tuple[str, str]:
    return STATUS_TO_EVENT.get(status, ("pipeline_unknown", "warning"))


def classify_execution_report(report: dict[str, Any]) -> NotificationEvent:
    pipeline_id = report.get("pipeline_id")
    status = report.get("status", "unknown")
    summary = report.get("summary", {})
    metadata = report.get("metadata", {})

    if not pipeline_id:
        raise ValueError("execution report requires pipeline_id")

    if not isinstance(summary, dict):
        raise TypeError("summary must be dict")

    if not isinstance(metadata, dict):
        raise TypeError("metadata must be dict")

    event_type, severity = classify_status(str(status))

    return NotificationEvent(
        pipeline_id=str(pipeline_id),
        event_type=event_type,
        severity=severity,
        source_status=str(status),
        summary=summary,
        metadata={
            "source": "execution_report",
            "execution_metadata": metadata,
        },
    )


def classify_execution_reports(
    reports: list[dict[str, Any]],
) -> list[NotificationEvent]:
    return [classify_execution_report(report) for report in reports]


def get_event_summary(events: list[NotificationEvent]) -> dict[str, Any]:
    return {
        "total_events": len(events),
        "info_events": sum(1 for event in events if event.severity == "info"),
        "warning_events": sum(1 for event in events if event.severity == "warning"),
        "error_events": sum(1 for event in events if event.severity == "error"),
    }
