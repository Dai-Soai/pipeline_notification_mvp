import json
from pathlib import Path
from typing import Any


class ExecutionReportLoaderError(Exception):
    """Raised when an execution report cannot be loaded or normalized."""


def load_execution_report(file_path: str | Path) -> dict[str, Any]:
    path = Path(file_path)

    if not path.exists():
        raise ExecutionReportLoaderError(f"execution report file not found: {path}")

    if not path.is_file():
        raise ExecutionReportLoaderError(f"execution report path is not a file: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
    except json.JSONDecodeError as error:
        raise ExecutionReportLoaderError(
            f"invalid execution report JSON: {error}"
        ) from error

    if not isinstance(payload, dict):
        raise ExecutionReportLoaderError("execution report root must be a JSON object")

    return normalize_execution_report(payload)


def normalize_execution_report(payload: dict[str, Any]) -> dict[str, Any]:
    pipeline_id = payload.get("pipeline_id")
    status = payload.get("status", "unknown")
    generated_at = payload.get("generated_at")
    results = payload.get("results", [])
    summary = payload.get("summary", {})
    metadata = payload.get("metadata", {})

    if not pipeline_id:
        raise ExecutionReportLoaderError("execution report requires pipeline_id")

    if not generated_at:
        raise ExecutionReportLoaderError("execution report requires generated_at")

    if results is None:
        results = []

    if not isinstance(results, list):
        raise ExecutionReportLoaderError("execution report results must be a list")

    if not isinstance(summary, dict):
        raise ExecutionReportLoaderError("execution report summary must be an object")

    if not isinstance(metadata, dict):
        raise ExecutionReportLoaderError("execution report metadata must be an object")

    return {
        "pipeline_id": str(pipeline_id),
        "status": str(status),
        "generated_at": str(generated_at),
        "results": results,
        "summary": summary,
        "metadata": metadata,
    }
