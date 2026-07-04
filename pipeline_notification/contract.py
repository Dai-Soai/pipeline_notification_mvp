from dataclasses import dataclass, field
from typing import Any


VALID_EVENT_TYPES = {
    "pipeline_completed",
    "pipeline_failed",
    "pipeline_partial",
    "pipeline_empty",
    "pipeline_unknown",
}

VALID_SEVERITIES = {
    "info",
    "warning",
    "error",
}

VALID_CHANNELS = {
    "telegram",
    "webhook",
    "email",
    "console",
}

VALID_REPORT_STATUSES = {
    "ready",
    "empty",
    "invalid",
}


@dataclass(frozen=True)
class NotificationEvent:
    pipeline_id: str
    event_type: str
    severity: str
    source_status: str
    summary: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.pipeline_id:
            raise ValueError("pipeline_id is required")

        if self.event_type not in VALID_EVENT_TYPES:
            raise ValueError(f"invalid event_type: {self.event_type}")

        if self.severity not in VALID_SEVERITIES:
            raise ValueError(f"invalid severity: {self.severity}")

        if not self.source_status:
            raise ValueError("source_status is required")

        if not isinstance(self.summary, dict):
            raise TypeError("summary must be dict")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be dict")


@dataclass(frozen=True)
class NotificationMessage:
    title: str
    body: str
    severity: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("title is required")

        if not self.body:
            raise ValueError("body is required")

        if self.severity not in VALID_SEVERITIES:
            raise ValueError(f"invalid severity: {self.severity}")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be dict")


@dataclass(frozen=True)
class ChannelPayload:
    channel: str
    target: str
    title: str
    message: str
    severity: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.channel not in VALID_CHANNELS:
            raise ValueError(f"invalid channel: {self.channel}")

        if not self.target:
            raise ValueError("target is required")

        if not self.title:
            raise ValueError("title is required")

        if not self.message:
            raise ValueError("message is required")

        if self.severity not in VALID_SEVERITIES:
            raise ValueError(f"invalid severity: {self.severity}")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be dict")


@dataclass(frozen=True)
class NotificationReport:
    pipeline_id: str
    status: str
    events: list[NotificationEvent]
    messages: list[NotificationMessage]
    payloads: list[ChannelPayload]
    summary: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.pipeline_id:
            raise ValueError("pipeline_id is required")

        if self.status not in VALID_REPORT_STATUSES:
            raise ValueError(f"invalid report status: {self.status}")

        for event in self.events:
            if not isinstance(event, NotificationEvent):
                raise TypeError("events must contain NotificationEvent items")

        for message in self.messages:
            if not isinstance(message, NotificationMessage):
                raise TypeError("messages must contain NotificationMessage items")

        for payload in self.payloads:
            if not isinstance(payload, ChannelPayload):
                raise TypeError("payloads must contain ChannelPayload items")

        if not isinstance(self.summary, dict):
            raise TypeError("summary must be dict")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be dict")
