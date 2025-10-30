#!/usr/bin/env python3
"""Type checking wrapper (Mypy) for LAZY-DEV-FRAMEWORK."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Optional


LOG_FILE_NAME: Final[str] = "type_check.json"


@dataclass
class TypeCheckResult:
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


def run_mypy(target: Path) -> TypeCheckResult:
    start = time.perf_counter()
    result = subprocess.run(
        ["mypy", str(target), "--strict"],
        capture_output=True,
        text=True,
    )
    duration = time.perf_counter() - start
    return TypeCheckResult(
        exit_code=result.returncode,
        duration_seconds=duration,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def parse_mypy_stdout(stdout: str) -> list[dict]:
    errors: list[dict] = []
    for line in stdout.splitlines():
        if "error:" not in line:
            continue
        parts = line.split(":", 3)
        if len(parts) < 4:
            continue
        file_path, line_no, col, message = parts
        errors.append(
            {
                "file": file_path.strip(),
                "line": line_no.strip(),
                "column": col.strip() if col.strip().isdigit() else None,
                "message": message.replace("error:", "").strip(),
            }
        )
    return errors


def write_log(
    target: Path,
    session_id: Optional[str],
    result: TypeCheckResult,
    errors: list[dict] | None,
) -> None:
    if not session_id:
        return

    log_dir = Path("logs") / session_id
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / LOG_FILE_NAME

    entry = {
        "path": str(target),
        "session_id": session_id,
        "status": "success" if result.exit_code == 0 else "failed",
        "result": result.as_dict(),
    }
    if errors:
        entry["errors"] = errors

    existing: list[dict] = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = []

    existing.append(entry)
    log_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")


def type_check_path(target: Path, session_id: Optional[str]) -> int:
    if not target.exists():
        raise FileNotFoundError(f"Path does not exist: {target}")

    print(f"🔎 Running Mypy on {target}...")
    result = run_mypy(target)

    if result.stdout:
        print(result.stdout)

    errors = parse_mypy_stdout(result.stdout) if result.exit_code != 0 else []

    if result.exit_code != 0:
        print("\n❌ Type checking failed", file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        write_log(target, session_id, result, errors)
        return result.exit_code

    print("✅ Type checking complete")
    write_log(target, session_id, result, errors)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Mypy type checks.")
    parser.add_argument("path", help="File or directory to type check")
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
        return type_check_path(target, args.session_id)
    except FileNotFoundError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("⚠️ Type checking interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
