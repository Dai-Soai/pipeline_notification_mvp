from pipeline_notification.contract import NotificationEvent, NotificationMessage


EVENT_TITLES = {
    "pipeline_completed": "Pipeline completed",
    "pipeline_failed": "Pipeline failed",
    "pipeline_partial": "Pipeline partially completed",
    "pipeline_empty": "Pipeline produced no results",
    "pipeline_unknown": "Pipeline status unknown",
}


def build_message_title(event: NotificationEvent) -> str:
    return EVENT_TITLES.get(event.event_type, "Pipeline notification")


def build_message_body(event: NotificationEvent) -> str:
    summary = event.summary

    total_results = summary.get("total_results", 0)
    successful_results = summary.get("successful_results", 0)
    failed_results = summary.get("failed_results", 0)
    success_rate = summary.get("success_rate", 0.0)

    return (
        f"Pipeline {event.pipeline_id} status: {event.source_status}.\n"
        f"Severity: {event.severity}.\n"
        f"Total results: {total_results}.\n"
        f"Successful results: {successful_results}.\n"
        f"Failed results: {failed_results}.\n"
        f"Success rate: {success_rate:.2f}."
    )


def build_notification_message(event: NotificationEvent) -> NotificationMessage:
    return NotificationMessage(
        title=build_message_title(event),
        body=build_message_body(event),
        severity=event.severity,
        metadata={
            "pipeline_id": event.pipeline_id,
            "event_type": event.event_type,
            "source_status": event.source_status,
        },
    )


def build_notification_messages(
    events: list[NotificationEvent],
) -> list[NotificationMessage]:
    return [
        build_notification_message(event)
        for event in events
    ]
