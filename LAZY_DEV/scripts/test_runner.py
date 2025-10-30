#!/usr/bin/env python3
"""Test runner wrapper (Pytest) for LAZY-DEV-FRAMEWORK."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Final, Optional


LOG_FILE_NAME: Final[str] = "test_runner.json"
DEFAULT_TARGET: Final[str] = "tests/"
DEFAULT_COV_TARGET: Final[str] = "src"
PYTEST_COVERAGE_JSON: Final[str] = "coverage.json"


def run_pytest(target: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "pytest",
            target,
            "-v",
            f"--cov={DEFAULT_COV_TARGET}",
            "--cov-report=term",
            "--cov-report=json",
        ],
        capture_output=True,
        text=True,
    )


def read_coverage() -> dict | None:
    coverage_file = Path(PYTEST_COVERAGE_JSON)
    if not coverage_file.exists():
        return None
    try:
        return json.loads(coverage_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def write_log(
    session_id: Optional[str],
    target: str,
    result: subprocess.CompletedProcess[str],
    duration: float,
    coverage: dict | None,
) -> None:
    if not session_id:
        return

    log_dir = Path("logs") / session_id
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / LOG_FILE_NAME

    entry = {
        "path": target,
        "session_id": session_id,
        "status": "success" if result.returncode == 0 else "failed",
        "duration_seconds": duration,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    if coverage:
        entry["coverage"] = {
            "total_coverage": coverage.get("totals", {}).get("percent_covered"),
            "files": coverage.get("files"),
        }

    existing: list[dict] = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = []

    existing.append(entry)
    log_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def run_tests(target: str, session_id: Optional[str]) -> int:
    path_obj = Path(target)
    if not path_obj.exists():
        print(f"⚠️ Path '{target}' does not exist. Pytest will still be invoked.", file=sys.stderr)

    print(f"🧪 Running Pytest on {target}...")
    start = time.perf_counter()
    result = run_pytest(target)
    duration = time.perf_counter() - start

    # Always relay stdout/stderr for investigator visibility
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    coverage = read_coverage()

    if result.returncode != 0:
        print("❌ Tests failed", file=sys.stderr)
        write_log(session_id, target, result, duration, coverage)
        return result.returncode

    print("✅ All tests passed")
    write_log(session_id, target, result, duration, coverage)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run pytest with coverage.")
    parser.add_argument(
        "path",
        nargs="?",
        default=DEFAULT_TARGET,
        help=f"Path to tests (default: {DEFAULT_TARGET})",
    )
    parser.add_argument(
        "--session",
        dest="session_id",
        help="Optional session identifier for logging",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        return run_tests(args.path, args.session_id)
    except KeyboardInterrupt:
        print("⚠️ Test run interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
