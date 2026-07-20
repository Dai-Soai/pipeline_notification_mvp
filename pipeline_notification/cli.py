import argparse
import sys

from pipeline_notification.channel_payload import build_channel_payloads
from pipeline_notification.classifier import classify_execution_report
from pipeline_notification.loader import (
    ExecutionReportLoaderError,
    load_execution_report,
)
from pipeline_notification.message_builder import build_notification_messages
from pipeline_notification.report import (
    build_notification_report,
    write_notification_report_json,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pipeline-notification",
        description="Build notification previews from pipeline execution reports.",
    )

    subparsers = parser.add_subparsers(dest="command")

    preview_parser = subparsers.add_parser(
        "preview",
        help="Preview notification payloads from an execution report.",
    )
    preview_parser.add_argument(
        "execution_report",
        help="Path to execution_report.json.",
    )
    preview_parser.add_argument(
        "--channel",
        default="console",
        choices=["console", "telegram", "webhook", "email"],
        help="Notification channel.",
    )
    preview_parser.add_argument(
        "--target",
        default=None,
        help="Notification target.",
    )
    preview_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show payload details.",
    )
    preview_parser.add_argument(
        "--json",
        action="store_true",
        help="Write notification report as JSON.",
    )
    preview_parser.add_argument(
        "--output",
        default="outputs/notification_report.json",
        help="Output path for JSON notification report.",
    )

    return parser


def run_preview(args: argparse.Namespace) -> int:
    try:
        report = load_execution_report(args.execution_report)
        event = classify_execution_report(report)
        messages = build_notification_messages([event])
        payloads = build_channel_payloads(
            messages,
            channel=args.channel,
            target=args.target,
        )
        notification_report = build_notification_report(
            pipeline_id=event.pipeline_id,
            events=[event],
            messages=messages,
            payloads=payloads,
            metadata={
                "source": "pipeline_notification",
                "execution_report": args.execution_report,
                "channel": args.channel,
                "target": args.target,
            },
        )
    except (ExecutionReportLoaderError, ValueError, TypeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    if args.json:
        output_path = write_notification_report_json(notification_report, args.output)
        print(f"JSON notification report written: {output_path}")
        return 0

    print("Pipeline Notification Preview")
    print("=============================")
    print(f"Pipeline ID: {event.pipeline_id}")
    print(f"Event Type: {event.event_type}")
    print(f"Severity: {event.severity}")
    print(f"Source Status: {event.source_status}")
    print()
    print("Messages")
    print("--------")
    for message in messages:
        print(f"Title: {message.title}")
        print(message.body)

    print()
    print("Payloads")
    print("--------")
    for payload in payloads:
        print(
            f"- channel={payload.channel} | "
            f"target={payload.target} | "
            f"severity={payload.severity}"
        )
        if args.verbose:
            print(f"  title={payload.title}")
            print(f"  message={payload.message}")

    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "preview":
        return run_preview(args)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
