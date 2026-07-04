import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from pipeline_notification.contract import (
    ChannelPayload,
    NotificationEvent,
    NotificationMessage,
    NotificationReport,
)


def build_notification_summary(
    events: list[NotificationEvent],
    messages: list[NotificationMessage],
    payloads: list[ChannelPayload],
) -> dict[str, Any]:
    return {
        "total_events": len(events),
        "total_messages": len(messages),
        "total_payloads": len(payloads),
        "info_events": sum(1 for event in events if event.severity == "info"),
        "warning_events": sum(1 for event in events if event.severity == "warning"),
        "error_events": sum(1 for event in events if event.severity == "error"),
    }


def determine_notification_report_status(
    events: list[NotificationEvent],
    messages: list[NotificationMessage],
    payloads: list[ChannelPayload],
) -> str:
    if not events and not messages and not payloads:
        return "empty"

    if events and messages and payloads:
        return "ready"

    return "invalid"


def build_notification_report(
    pipeline_id: str,
    events: list[NotificationEvent],
    messages: list[NotificationMessage],
    payloads: list[ChannelPayload],
    metadata: dict[str, Any] | None = None,
) -> NotificationReport:
    if not pipeline_id:
        raise ValueError("pipeline_id is required")

    return NotificationReport(
        pipeline_id=pipeline_id,
        status=determine_notification_report_status(events, messages, payloads),
        events=events,
        messages=messages,
        payloads=payloads,
        summary=build_notification_summary(events, messages, payloads),
        metadata=metadata or {},
    )


def notification_report_to_dict(report: NotificationReport) -> dict[str, Any]:
    if not isinstance(report, NotificationReport):
        raise TypeError("report must be NotificationReport")

    return {
        "pipeline_id": report.pipeline_id,
        "status": report.status,
        "events": [asdict(event) for event in report.events],
        "messages": [asdict(message) for message in report.messages],
        "payloads": [asdict(payload) for payload in report.payloads],
        "summary": report.summary,
        "metadata": report.metadata,
    }


def write_notification_report_json(
    report: NotificationReport,
    output_path: str | Path,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = notification_report_to_dict(report)

    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return path
