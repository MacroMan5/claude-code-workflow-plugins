#!/usr/bin/env python3
"""Linting wrapper (Ruff check) for LAZY-DEV-FRAMEWORK."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Optional


LOG_FILE_NAME: Final[str] = "lint.json"


@dataclass
class LintResult:
    exit_code: int
    duration_seconds: float
    stdout: str
    stderr: str

    def as_dict(self) -> dict:
        return {
            "duration_seconds": self.duration_seconds,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


def run_ruff_check(target: Path) -> LintResult:
    start = time.perf_counter()
    result = subprocess.run(
        ["ruff", "check", str(target), "--fix", "--output-format=json"],
        capture_output=True,
        text=True,
    )
    duration = time.perf_counter() - start
    return LintResult(
        exit_code=result.returncode,
        duration_seconds=duration,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def write_log(
    target: Path,
    session_id: Optional[str],
    lint_result: LintResult,
    violations: list | None,
) -> None:
    if not session_id:
        return

    log_dir = Path("logs") / session_id
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / LOG_FILE_NAME

    entry = {
        "path": str(target),
        "session_id": session_id,
        "status": "success" if lint_result.exit_code == 0 else "failed",
        "result": lint_result.as_dict(),
    }
    if violations is not None:
        entry["violations"] = violations

    existing: list[dict] = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = []

    existing.append(entry)
    log_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def lint_path(target: Path, session_id: Optional[str]) -> int:
    if not target.exists():
        raise FileNotFoundError(f"Path does not exist: {target}")

    print(f"🔍 Running Ruff check on {target}...")
    lint_result = run_ruff_check(target)

    violations: list | None = None
    if lint_result.stdout:
        try:
            violations = json.loads(lint_result.stdout)
            if violations:
                print(json.dumps(violations, indent=2))
        except json.JSONDecodeError:
            print(lint_result.stdout)

    if lint_result.exit_code != 0:
        print("❌ Ruff check reported issues", file=sys.stderr)
        write_log(target, session_id, lint_result, violations)
        return lint_result.exit_code

    print("✅ Linting complete")
    write_log(target, session_id, lint_result, violations)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Ruff lint checks.")
    parser.add_argument("path", help="File or directory to lint")
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
        return lint_path(target, args.session_id)
    except FileNotFoundError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("⚠️ Lint interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
