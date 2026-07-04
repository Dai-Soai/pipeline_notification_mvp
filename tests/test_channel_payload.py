import pytest

from pipeline_notification.channel_payload import (
    build_channel_payload,
    build_channel_payloads,
    get_default_target,
    get_payload_summary,
)
from pipeline_notification.contract import ChannelPayload, NotificationMessage


def make_message(severity: str = "info") -> NotificationMessage:
    return NotificationMessage(
        title="Pipeline completed",
        body="Pipeline pipeline-001 completed successfully.",
        severity=severity,
        metadata={
            "pipeline_id": "pipeline-001",
        },
    )


def test_get_default_target_console():
    assert get_default_target("console") == "stdout"


def test_get_default_target_telegram():
    assert get_default_target("telegram") == "radar-alerts"


def test_get_default_target_rejects_invalid_channel():
    with pytest.raises(ValueError):
        get_default_target("sms")


def test_build_channel_payload_default_console():
    payload = build_channel_payload(make_message())

    assert isinstance(payload, ChannelPayload)
    assert payload.channel == "console"
    assert payload.target == "stdout"
    assert payload.title == "Pipeline completed"
    assert payload.severity == "info"


def test_build_channel_payload_custom_target():
    payload = build_channel_payload(
        make_message(),
        channel="telegram",
        target="ops-chat",
    )

    assert payload.channel == "telegram"
    assert payload.target == "ops-chat"


def test_build_channel_payload_webhook():
    payload = build_channel_payload(
        make_message("warning"),
        channel="webhook",
    )

    assert payload.channel == "webhook"
    assert payload.target == "default-webhook"
    assert payload.severity == "warning"


def test_build_channel_payload_email():
    payload = build_channel_payload(
        make_message("error"),
        channel="email",
    )

    assert payload.channel == "email"
    assert payload.target == "default-email"
    assert payload.severity == "error"


def test_build_channel_payloads():
    messages = [
        make_message("info"),
        make_message("error"),
    ]

    payloads = build_channel_payloads(messages, channel="console")

    assert len(payloads) == 2
    assert payloads[0].channel == "console"
    assert payloads[1].severity == "error"


def test_get_payload_summary():
    payloads = [
        build_channel_payload(make_message(), channel="console"),
        build_channel_payload(make_message(), channel="telegram"),
        build_channel_payload(make_message(), channel="webhook"),
        build_channel_payload(make_message(), channel="email"),
    ]

    summary = get_payload_summary(payloads)

    assert summary["total_payloads"] == 4
    assert summary["console_payloads"] == 1
    assert summary["telegram_payloads"] == 1
    assert summary["webhook_payloads"] == 1
    assert summary["email_payloads"] == 1
