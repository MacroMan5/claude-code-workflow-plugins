#!/usr/bin/env python3
"""Code formatting wrapper (Black + Ruff format) - Cross-OS compatible."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def format_code(path: str, session_id: Optional[str] = None) -> int:
    """
    Format code with Black and Ruff.

    This function formats Python code using Black for code style and Ruff
    for additional formatting rules. It executes sequentially: Black first,
    then Ruff format. If Black fails, Ruff is not executed.

    Args:
        path: File or directory path to format.
        session_id: Optional session ID for logging. If provided, logs are
                   written to logs/<session_id>/format.json.

    Returns:
        Exit code (0 = success, non-zero = failure).

    Example:
        >>> format_code("src/auth.py")
        0
        >>> format_code("src/", session_id="abc123")
        0
    """
    path_obj = Path(path)

    if not path_obj.exists():
        print(f"[ERROR] Path does not exist: {path}")
        return 1

    # Initialize logging
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "script": "format.py",
        "path": str(path_obj),
        "session_id": session_id,
        "steps": [],
    }

    print(f"[FORMAT] Running Black on {path}...")
    start_time = datetime.utcnow()
    black_result = subprocess.run(
        ["black", str(path_obj)], capture_output=True, text=True
    )
    black_duration = (datetime.utcnow() - start_time).total_seconds()

    log_entry["steps"].append(
        {
            "tool": "black",
            "duration_seconds": black_duration,
            "exit_code": black_result.returncode,
            "stdout": black_result.stdout,
            "stderr": black_result.stderr,
        }
    )

    if black_result.returncode != 0:
        print(f"[ERROR] Black failed:\n{black_result.stderr}")
        _write_log(log_entry, session_id)
        return black_result.returncode

    print(f"[FORMAT] Running Ruff format on {path}...")
    start_time = datetime.utcnow()
    ruff_result = subprocess.run(
        ["ruff", "format", str(path_obj)], capture_output=True, text=True
    )
    ruff_duration = (datetime.utcnow() - start_time).total_seconds()

    log_entry["steps"].append(
        {
            "tool": "ruff",
            "duration_seconds": ruff_duration,
            "exit_code": ruff_result.returncode,
            "stdout": ruff_result.stdout,
            "stderr": ruff_result.stderr,
        }
    )

    if ruff_result.returncode != 0:
        print(f"[ERROR] Ruff format failed:\n{ruff_result.stderr}")
        _write_log(log_entry, session_id)
        return ruff_result.returncode

    print("[SUCCESS] Formatting complete")
    log_entry["status"] = "success"
    _write_log(log_entry, session_id)
    return 0


def _write_log(log_entry: dict, session_id: Optional[str]) -> None:
    """
    Write structured log to session directory.

    Logs are appended to logs/<session_id>/format.json. If the session_id
    is not provided, logging is skipped.

    Args:
        log_entry: Dictionary containing log information.
        session_id: Session ID for log organization.
    """
    if not session_id:
        return

    log_dir = Path("logs") / session_id
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "format.json"

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
        print("Usage: python format.py <path> [--session SESSION_ID]")
        sys.exit(1)

    path = sys.argv[1]
    session_id = None

    if len(sys.argv) >= 4 and sys.argv[2] == "--session":
        session_id = sys.argv[3]

    exit_code = format_code(path, session_id)
    sys.exit(exit_code)
