from pipeline_notification.contract import ChannelPayload, NotificationMessage


DEFAULT_TARGETS = {
    "console": "stdout",
    "telegram": "radar-alerts",
    "webhook": "default-webhook",
    "email": "default-email",
}


def get_default_target(channel: str) -> str:
    if channel not in DEFAULT_TARGETS:
        raise ValueError(f"unsupported channel: {channel}")

    return DEFAULT_TARGETS[channel]


def build_channel_payload(
    message: NotificationMessage,
    channel: str = "console",
    target: str | None = None,
) -> ChannelPayload:
    if target is None:
        target = get_default_target(channel)

    return ChannelPayload(
        channel=channel,
        target=target,
        title=message.title,
        message=message.body,
        severity=message.severity,
        metadata={
            "source": "notification_message",
            "message_metadata": message.metadata,
        },
    )


def build_channel_payloads(
    messages: list[NotificationMessage],
    channel: str = "console",
    target: str | None = None,
) -> list[ChannelPayload]:
    return [
        build_channel_payload(
            message=message,
            channel=channel,
            target=target,
        )
        for message in messages
    ]


def get_payload_summary(payloads: list[ChannelPayload]) -> dict[str, int]:
    return {
        "total_payloads": len(payloads),
        "console_payloads": sum(1 for payload in payloads if payload.channel == "console"),
        "telegram_payloads": sum(1 for payload in payloads if payload.channel == "telegram"),
        "webhook_payloads": sum(1 for payload in payloads if payload.channel == "webhook"),
        "email_payloads": sum(1 for payload in payloads if payload.channel == "email"),
    }
