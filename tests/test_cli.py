import json

from pipeline_notification.cli import main


def sample_execution_report(status: str = "completed"):
    return {
        "pipeline_id": "pipeline-001",
        "status": status,
        "generated_at": "2026-07-04T20:00:00Z",
        "results": [],
        "summary": {
            "total_results": 2,
            "successful_results": 2 if status == "completed" else 1,
            "failed_results": 0 if status == "completed" else 1,
            "success_rate": 1.0 if status == "completed" else 0.5,
        },
        "metadata": {
            "source": "pipeline_executor",
        },
    }


def test_cli_prints_help_when_no_command(capsys):
    exit_code = main([])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "pipeline-notification" in captured.out


def test_cli_preview_outputs_notification(tmp_path, capsys):
    report_file = tmp_path / "execution_report.json"
    report_file.write_text(json.dumps(sample_execution_report()), encoding="utf-8")

    exit_code = main(["preview", str(report_file)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Pipeline Notification Preview" in captured.out
    assert "Pipeline ID: pipeline-001" in captured.out
    assert "Event Type: pipeline_completed" in captured.out
    assert "Severity: info" in captured.out
    assert "Pipeline completed" in captured.out
    assert "channel=console" in captured.out


def test_cli_preview_failed_report(tmp_path, capsys):
    report_file = tmp_path / "execution_report.json"
    report_file.write_text(json.dumps(sample_execution_report("failed")), encoding="utf-8")

    exit_code = main(["preview", str(report_file)])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Event Type: pipeline_failed" in captured.out
    assert "Severity: error" in captured.out
    assert "Pipeline failed" in captured.out


def test_cli_preview_custom_channel_and_target(tmp_path, capsys):
    report_file = tmp_path / "execution_report.json"
    report_file.write_text(json.dumps(sample_execution_report()), encoding="utf-8")

    exit_code = main(
        [
            "preview",
            str(report_file),
            "--channel",
            "telegram",
            "--target",
            "ops-chat",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "channel=telegram" in captured.out
    assert "target=ops-chat" in captured.out


def test_cli_preview_verbose_outputs_payload_details(tmp_path, capsys):
    report_file = tmp_path / "execution_report.json"
    report_file.write_text(json.dumps(sample_execution_report()), encoding="utf-8")

    exit_code = main(["preview", str(report_file), "--verbose"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "title=Pipeline completed" in captured.out
    assert "message=Pipeline pipeline-001 status" in captured.out


def test_cli_preview_missing_file_returns_error(capsys):
    exit_code = main(["preview", "missing.json"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert "error:" in captured.err


def test_cli_preview_json_writes_notification_report(tmp_path, capsys):
    report_file = tmp_path / "execution_report.json"
    output_file = tmp_path / "notification_report.json"

    report_file.write_text(json.dumps(sample_execution_report()), encoding="utf-8")

    exit_code = main(
        [
            "preview",
            str(report_file),
            "--json",
            "--output",
            str(output_file),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "JSON notification report written:" in captured.out
    assert output_file.exists()

    payload = json.loads(output_file.read_text(encoding="utf-8"))

    assert payload["pipeline_id"] == "pipeline-001"
    assert payload["status"] == "ready"
    assert payload["summary"]["total_payloads"] == 1
