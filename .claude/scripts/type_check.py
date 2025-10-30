#!/usr/bin/env python3
"""Type checking wrapper (Mypy) - Cross-OS compatible."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def type_check(path: str, session_id: Optional[str] = None) -> int:
    """
    Type check code using Mypy.

    This function performs static type checking using Mypy in strict mode.
    It parses error output into structured format for better reporting.

    Args:
        path: File or directory path to type check.
        session_id: Optional session ID for logging. If provided, logs are
                   written to logs/<session_id>/type_check.json.

    Returns:
        Exit code (0 = success, non-zero = failure).

    Example:
        >>> type_check("src/auth.py")
        0
        >>> type_check("src/", session_id="abc123")
        0
    """
    path_obj = Path(path)

    if not path_obj.exists():
        print(f"[ERROR] Path does not exist: {path}")
        return 1

    # Initialize logging
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "script": "type_check.py",
        "path": str(path_obj),
        "session_id": session_id,
        "errors": [],
    }

    print(f"[TYPE] Running Mypy on {path}...")
    start_time = datetime.utcnow()
    result = subprocess.run(
        ["mypy", str(path_obj), "--strict"], capture_output=True, text=True
    )
    duration = (datetime.utcnow() - start_time).total_seconds()

    log_entry["duration_seconds"] = duration
    log_entry["exit_code"] = result.returncode
    log_entry["stdout"] = result.stdout
    log_entry["stderr"] = result.stderr

    if result.stdout:
        print(result.stdout)

    if result.returncode != 0:
        print("\n[ERROR] Type checking failed")
        print("[INFO] Fix type errors and re-run")
        log_entry["status"] = "failed"

        # Parse errors for structured logging
        errors = _parse_mypy_errors(result.stdout)
        log_entry["errors"] = errors

        _write_log(log_entry, session_id)
        return result.returncode

    print("[SUCCESS] Type checking complete")
    log_entry["status"] = "success"
    _write_log(log_entry, session_id)
    return 0


def _parse_mypy_errors(output: str) -> List[dict]:
    """
    Parse Mypy output into structured error list.

    Args:
        output: Raw Mypy output string.

    Returns:
        List of error dictionaries with file, line, column, and message.

    Example:
        >>> _parse_mypy_errors("src/auth.py:42:12: error: ...")
        [{'file': 'src/auth.py', 'line': '42', 'column': '12', 'message': '...'}]
    """
    errors = []
    for line in output.split("\n"):
        if ":" in line and "error:" in line:
            parts = line.split(":")
            if len(parts) >= 4:
                errors.append(
                    {
                        "file": parts[0].strip(),
                        "line": parts[1].strip(),
                        "column": (
                            parts[2].strip() if parts[2].strip().isdigit() else None
                        ),
                        "message": ":".join(parts[3:]).replace("error:", "").strip(),
                    }
                )
    return errors


def _write_log(log_entry: dict, session_id: Optional[str]) -> None:
    """
    Write structured log to session directory.

    Logs are appended to logs/<session_id>/type_check.json. If the session_id
    is not provided, logging is skipped.

    Args:
        log_entry: Dictionary containing log information.
        session_id: Session ID for log organization.
    """
    if not session_id:
        return

    log_dir = Path("logs") / session_id
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "type_check.json"

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
        print("Usage: python type_check.py <path> [--session SESSION_ID]")
        sys.exit(1)

    path = sys.argv[1]
    session_id = None

    if len(sys.argv) >= 4 and sys.argv[2] == "--session":
        session_id = sys.argv[3]

    exit_code = type_check(path, session_id)
    sys.exit(exit_code)
