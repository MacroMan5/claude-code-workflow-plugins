#!/usr/bin/env python3
"""Test runner wrapper (Pytest) - Cross-OS compatible."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def run_tests(path: str = "tests/", session_id: Optional[str] = None) -> int:
    """
    Run tests using Pytest.

    This function executes tests with coverage reporting enabled. It uses
    pytest with verbose output and generates coverage reports in multiple
    formats (terminal, JSON).

    Args:
        path: File or directory path containing tests. Defaults to "tests/".
        session_id: Optional session ID for logging. If provided, logs are
                   written to logs/<session_id>/test_runner.json.

    Returns:
        Exit code (0 = success, non-zero = failure).

    Example:
        >>> run_tests("tests/")
        0
        >>> run_tests("tests/test_auth.py", session_id="abc123")
        0
    """
    path_obj = Path(path)

    if not path_obj.exists():
        print(f"[ERROR] Path does not exist: {path}")
        return 1

    # Initialize logging
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "script": "test_runner.py",
        "path": str(path_obj),
        "session_id": session_id,
        "test_results": {},
    }

    print(f"[TEST] Running Pytest on {path}...")
    start_time = datetime.utcnow()
    result = subprocess.run(
        [
            "pytest",
            str(path_obj),
            "-v",
            "--cov=src",
            "--cov-report=term",
            "--cov-report=json",
        ],
        capture_output=True,
        text=True,
    )
    duration = (datetime.utcnow() - start_time).total_seconds()

    log_entry["duration_seconds"] = duration
    log_entry["exit_code"] = result.returncode

    # Always display output
    print(result.stdout)

    # Parse coverage JSON if available
    coverage_file = Path("coverage.json")
    if coverage_file.exists():
        try:
            with open(coverage_file, "r") as f:
                coverage_data = json.load(f)
                log_entry["coverage"] = {
                    "total_coverage": coverage_data.get("totals", {}).get(
                        "percent_covered", 0
                    ),
                    "files": coverage_data.get("files", {}),
                }
        except (json.JSONDecodeError, FileNotFoundError):
            # Coverage file may not exist or be malformed
            pass

    if result.returncode != 0:
        print(f"\n[ERROR] Tests failed")
        if result.stderr:
            print(f"Error details: {result.stderr}")
        log_entry["status"] = "failed"
        log_entry["stderr"] = result.stderr
        _write_log(log_entry, session_id)
        return result.returncode

    print("[SUCCESS] All tests passed")
    log_entry["status"] = "success"
    _write_log(log_entry, session_id)
    return 0


def _write_log(log_entry: dict, session_id: Optional[str]) -> None:
    """
    Write structured log to session directory.

    Logs are appended to logs/<session_id>/test_runner.json. If the session_id
    is not provided, logging is skipped.

    Args:
        log_entry: Dictionary containing log information.
        session_id: Session ID for log organization.
    """
    if not session_id:
        return

    log_dir = Path("logs") / session_id
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "test_runner.json"

    # Append to existing log
    logs = []
    if log_file.exists():
        with open(log_file, "r") as f:
            logs = json.load(f)

    logs.append(log_entry)

    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "tests/"
    session_id = None

    if len(sys.argv) >= 4 and sys.argv[2] == "--session":
        session_id = sys.argv[3]

    exit_code = run_tests(path, session_id)
    sys.exit(exit_code)
