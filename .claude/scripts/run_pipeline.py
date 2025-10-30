#!/usr/bin/env python3
"""Run complete quality pipeline with fail-fast behavior - Cross-OS compatible."""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple


def run_pipeline(path: str, session_id: str = None) -> int:
    """
    Run quality pipeline with fail-fast behavior.

    Executes the complete quality pipeline: Format → Lint → Type → Test.
    Stops at the first failure and reports the error.

    Args:
        path: File or directory path to check.
        session_id: Optional session ID for logging. If not provided,
                   generates timestamp-based session ID.

    Returns:
        Exit code (0 = all passed, non-zero = failed).

    Example:
        >>> run_pipeline("src/")
        0
        >>> run_pipeline("src/", session_id="pipeline_123")
        0
    """
    # Generate session ID if not provided
    if not session_id:
        session_id = f"pipeline_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    print(f"Running Quality Pipeline on {path}")
    print(f"Session ID: {session_id}")
    print("=" * 60)

    scripts_dir = Path(__file__).parent

    # Define pipeline stages
    stages = [
        ("Format", "format.py", "[FORMAT]"),
        ("Lint", "lint.py", "[LINT]"),
        ("Type Check", "type_check.py", "[TYPE]"),
        ("Tests", "test_runner.py", "[TEST]"),
    ]

    total_start = datetime.utcnow()

    # Run each stage sequentially
    for name, script, prefix in stages:
        print(f"\n{prefix} Running {name}...")
        print("-" * 60)

        stage_start = datetime.utcnow()
        result = subprocess.run(
            ["python", str(scripts_dir / script), path, "--session", session_id],
            capture_output=True,
            text=True,
        )
        stage_duration = (datetime.utcnow() - stage_start).total_seconds()

        # Print output
        if result.stdout:
            print(result.stdout)

        if result.returncode != 0:
            print(f"\n[FAIL] {name} failed after {stage_duration:.2f}s")
            if result.stderr:
                print(f"Error: {result.stderr}")
            print("\n" + "=" * 60)
            print(f"[FAIL] Pipeline failed at {name} stage")
            print(f"View logs: logs/{session_id}/")
            print("=" * 60)
            return result.returncode

        print(f"[PASS] {name} passed in {stage_duration:.2f}s")

    total_duration = (datetime.utcnow() - total_start).total_seconds()

    # All stages passed
    print("\n" + "=" * 60)
    print(f"[SUCCESS] All quality checks passed in {total_duration:.2f}s")
    print(f"View logs: logs/{session_id}/")
    print("=" * 60)

    return 0


def main() -> None:
    """CLI interface for pipeline runner."""
    if len(sys.argv) < 2:
        print("Usage: python run_pipeline.py <path> [--session SESSION_ID]")
        print("\nExamples:")
        print("  python run_pipeline.py src/")
        print("  python run_pipeline.py src/ --session my_session")
        sys.exit(1)

    path = sys.argv[1]
    session_id = None

    if len(sys.argv) >= 4 and sys.argv[2] == "--session":
        session_id = sys.argv[3]

    exit_code = run_pipeline(path, session_id)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
