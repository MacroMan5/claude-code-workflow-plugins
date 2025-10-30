#!/usr/bin/env python3
"""Code formatting wrapper (Black + Ruff format) for LAZY-DEV-FRAMEWORK.

This script normalises execution of formatting tools so commands and hooks can
invoke a single entry point regardless of platform. It follows the guidance in
`PROJECT-MANAGEMENT-LAZY_DEV/docs/TOOLS.md` and logs structured output that
other automation can consume.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable, Optional


LOG_FILE_NAME: Final[str] = "format.json"


@dataclass
class StepResult:
    """Represents a single formatter execution."""

    tool: str
    duration_seconds: float
    exit_code: int
    stdout: str
    stderr: str

    def as_dict(self) -> dict:
        return {
            "tool": self.tool,
            "duration_seconds": self.duration_seconds,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


def run_subprocess(command: Iterable[str]) -> StepResult:
    """Run a subprocess command and capture execution metadata."""
    cmd = list(command)
    start = time.perf_counter()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    duration = time.perf_counter() - start
    return StepResult(
        tool=" ".join(cmd[:2]) if len(cmd) > 1 else cmd[0],
        duration_seconds=duration,
        exit_code=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def ensure_path(path: Path) -> None:
    """Validate the provided path exists."""
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")


def write_log(
    step_results: list[StepResult], target: Path, session_id: Optional[str]
) -> None:
    """Persist formatter run metadata into logs/<session_id>/format.json."""
    if not session_id:
        return

    log_dir = Path("logs") / session_id
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / LOG_FILE_NAME

    entry = {
        "path": str(target),
        "session_id": session_id,
        "steps": [result.as_dict() for result in step_results],
    }

    if all(result.exit_code == 0 for result in step_results):
        entry["status"] = "success"
    else:
        entry["status"] = "failed"

    existing: list[dict] = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = []

    existing.append(entry)
    log_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def format_path(target: Path, session_id: Optional[str]) -> int:
    """Run Black and Ruff format against the provided path."""
    ensure_path(target)
    step_results: list[StepResult] = []

    print(f"📝 Running Black on {target}...")
    black_result = run_subprocess(["black", str(target)])
    step_results.append(black_result)
    if black_result.exit_code != 0:
        print(f"❌ Black failed:\n{black_result.stderr}", file=sys.stderr)
        write_log(step_results, target, session_id)
        return black_result.exit_code

    print(f"📝 Running Ruff format on {target}...")
    ruff_result = run_subprocess(["ruff", "format", str(target)])
    step_results.append(ruff_result)
    if ruff_result.exit_code != 0:
        print(f"❌ Ruff format failed:\n{ruff_result.stderr}", file=sys.stderr)
        write_log(step_results, target, session_id)
        return ruff_result.exit_code

    print("✅ Formatting complete")
    write_log(step_results, target, session_id)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Black and Ruff format.")
    parser.add_argument(
        "path",
        help="File or directory to format",
    )
    parser.add_argument(
        "--session",
        dest="session_id",
        help="Optional session identifier for logging",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    target = Path(args.path)
    try:
        return format_path(target, args.session_id)
    except FileNotFoundError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("⚠️ Formatting interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
