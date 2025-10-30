#!/usr/bin/env python3
"""Linting wrapper (Ruff check) - Cross-OS compatible."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def lint_code(path: str, session_id: Optional[str] = None) -> int:
    """
    Lint code using Ruff.

    This function checks code quality using Ruff with automatic fixes enabled.
    It uses JSON output format for structured error reporting.

    Args:
        path: File or directory path to lint.
        session_id: Optional session ID for logging. If provided, logs are
                   written to logs/<session_id>/lint.json.

    Returns:
        Exit code (0 = success, non-zero = failure).

    Example:
        >>> lint_code("src/auth.py")
        0
        >>> lint_code("src/", session_id="abc123")
        0
    """
    path_obj = Path(path)

    if not path_obj.exists():
        print(f"[ERROR] Path does not exist: {path}")
        return 1

    # Initialize logging
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "script": "lint.py",
        "path": str(path_obj),
        "session_id": session_id,
        "violations": [],
        "auto_fixed": [],
    }

    print(f"[LINT] Running Ruff check on {path}...")
    start_time = datetime.utcnow()
    result = subprocess.run(
        ["ruff", "check", str(path_obj), "--fix", "--output-format=json"],
        capture_output=True,
        text=True,
    )
    duration = (datetime.utcnow() - start_time).total_seconds()

    log_entry["duration_seconds"] = duration
    log_entry["exit_code"] = result.returncode

    # Parse JSON output
    if result.stdout:
        try:
            violations = json.loads(result.stdout)
            log_entry["violations"] = violations
            if violations:
                print(f"Found {len(violations)} violations")
                for violation in violations[:5]:  # Show first 5
                    print(
                        f"  {violation.get('code', 'UNKNOWN')}: {violation.get('message', 'No message')}"
                    )
                if len(violations) > 5:
                    print(f"  ... and {len(violations) - 5} more")
        except json.JSONDecodeError:
            # If not JSON, print as-is
            print(result.stdout)

    if result.returncode != 0:
        print(f"[ERROR] Ruff check failed with issues")
        log_entry["status"] = "failed"
        _write_log(log_entry, session_id)
        return result.returncode

    print("[SUCCESS] Linting complete")
    log_entry["status"] = "success"
    _write_log(log_entry, session_id)
    return 0


def _write_log(log_entry: dict, session_id: Optional[str]) -> None:
    """
    Write structured log to session directory.

    Logs are appended to logs/<session_id>/lint.json. If the session_id
    is not provided, logging is skipped.

    Args:
        log_entry: Dictionary containing log information.
        session_id: Session ID for log organization.
    """
    if not session_id:
        return

    log_dir = Path("logs") / session_id
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "lint.json"

    # Append to existing log
    logs = []
    if log_file.exists():
        with open(log_file, "r") as f:
            logs = json.load(f)

    logs.append(log_entry)

    with open(log_file, "w") as f:
        json.dump(logs, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python lint.py <path> [--session SESSION_ID]")
        sys.exit(1)

    path = sys.argv[1]
    session_id = None

    if len(sys.argv) >= 4 and sys.argv[2] == "--session":
        session_id = sys.argv[3]

    exit_code = lint_code(path, session_id)
    sys.exit(exit_code)
