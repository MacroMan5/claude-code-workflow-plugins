#!/usr/bin/env python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Stop hook for LAZY-DEV-FRAMEWORK.

TDD enforcement gate - blocks completion until tests pass:
- Checks transcript for test execution
- Validates tests passed (RED → GREEN → REFACTOR)
- Blocks if tests not run or failed
- Allows if tests passed

Reference: PROJECT-MANAGEMENT-LAZY_DEV/docs/HOOKS.md (Stop/TDD Gate)
"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Configure logging to stderr with timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.

    Only allows alphanumeric, hyphens, and underscores.
    Prevents path traversal attacks.

    Args:
        session_id: Session identifier to validate

    Returns:
        True if valid format, False otherwise
    """
    return bool(re.match(r"^[a-zA-Z0-9_-]{1,64}$", session_id))


def parse_transcript(transcript_path: str) -> dict:
    """
    Parse transcript JSONL to check for test execution.

    Args:
        transcript_path: Path to transcript file

    Returns:
        Dictionary with test execution info
    """
    result = {
        "tests_run": False,
        "tests_passed": False,
        "test_failures": [],
        "test_count": 0,
        "coverage": None,
    }

    transcript_file = Path(transcript_path)

    if not transcript_file.exists():
        return result

    try:
        with open(transcript_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)

                    # Look for tool executions (Bash commands)
                    if entry.get("type") == "tool_use":
                        tool_name = entry.get("name")
                        if tool_name == "Bash":
                            tool_input = entry.get("input", {})
                            command = tool_input.get("command", "")

                            # Check for pytest execution
                            if "pytest" in command or "python -m pytest" in command:
                                result["tests_run"] = True

                    # Look for tool results
                    elif entry.get("type") == "tool_result":
                        content = entry.get("content", "")

                        if isinstance(content, list):
                            content = "\n".join(
                                (
                                    str(c.get("text", ""))
                                    if isinstance(c, dict)
                                    else str(c)
                                )
                                for c in content
                            )
                        elif not isinstance(content, str):
                            content = str(content)

                        # Parse pytest output
                        if "passed" in content.lower() or "failed" in content.lower():
                            result["tests_run"] = True

                            # Look for test summary
                            # Pattern: "5 passed in 2.3s" or "3 failed, 2 passed"
                            passed_match = re.search(r"(\d+)\s+passed", content)
                            failed_match = re.search(r"(\d+)\s+failed", content)

                            if passed_match:
                                passed_count = int(passed_match.group(1))
                                result["test_count"] += passed_count

                            if failed_match:
                                failed_count = int(failed_match.group(1))
                                result["test_count"] += failed_count

                                # Extract failure details
                                failure_lines = re.findall(
                                    r"FAILED\s+(.+?)\s+-", content
                                )
                                result["test_failures"].extend(failure_lines)

                            # Check overall pass/fail
                            if failed_match and int(failed_match.group(1)) > 0:
                                result["tests_passed"] = False
                            elif passed_match:
                                result["tests_passed"] = True

                            # Extract coverage if available
                            coverage_match = re.search(
                                r"TOTAL\s+\d+\s+\d+\s+(\d+)%", content
                            )
                            if coverage_match:
                                result["coverage"] = coverage_match.group(1) + "%"

                except json.JSONDecodeError:
                    # Skip malformed JSONL lines
                    continue

    except IOError as e:
        logger.warning(f"Failed to read transcript file: {type(e).__name__}")
    except Exception as e:
        logger.warning(f"Unexpected error parsing transcript: {type(e).__name__}")

    return result


def should_block_completion(
    test_info: dict, enforce_tdd: bool = False, min_tests: int | None = None
) -> tuple[bool, str]:
    """
    Determine if completion should be blocked based on test results.

    Args:
        test_info: Test execution information
        enforce_tdd: Whether to enforce TDD (default True)

    Returns:
        Tuple of (should_block, reason)
    """
    if not enforce_tdd:
        return False, "TDD enforcement disabled"

    # Block if no tests were run
    if not test_info["tests_run"]:
        return True, "No tests were executed. Write tests before marking work complete."

    # Block if tests failed
    if not test_info["tests_passed"]:
        failures = test_info["test_failures"]
        if failures:
            failure_list = "\n  - ".join(failures[:5])  # Show first 5 failures
            reason = f"Tests failed. Fix failing tests before completion:\n  - {failure_list}"
        else:
            reason = "Tests failed. Fix failing tests before completion."

        return True, reason

    # Enforce minimum tests if configured
    if min_tests is not None and test_info["test_count"] < min_tests:
        return True, f"Minimum tests not met: {test_info['test_count']}/{min_tests}"

    # Allow if tests passed
    return False, f"All tests passing ({test_info['test_count']} tests)"


def log_stop_event(
    session_id: str, input_data: dict, test_info: dict, blocked: bool, reason: str
) -> None:
    """
    Log stop event to logs/stop.json.

    Args:
        session_id: Session identifier
        input_data: Hook input data
        test_info: Test execution info
        blocked: Whether completion was blocked
        reason: Reason for block/allow
    """
    log_dir = Path(os.getenv("LAZYDEV_LOG_DIR", ".claude/data/logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "stop.json"

    # Read existing log or initialize
    if log_file.exists():
        try:
            with open(log_file, "r") as f:
                log_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            log_data = []
    else:
        log_data = []

    # Add stop entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "blocked": blocked,
        "reason": reason,
        "test_info": test_info,
    }

    log_data.append(log_entry)

    # Write back
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)


def main():
    """Hook entry point."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        session_id = input_data.get("session_id", "unknown")

        # Validate session_id
        if not validate_session_id(session_id):
            logger.error(f"Invalid session_id: {session_id}")
            sys.exit(0)  # Don't block, just skip

        transcript_path = input_data.get("transcript_path")

        # Parse transcript for test execution
        if transcript_path:
            test_info = parse_transcript(transcript_path)
        else:
            test_info = {
                "tests_run": False,
                "tests_passed": False,
                "test_failures": [],
                "test_count": 0,
                "coverage": None,
            }

        # Determine if we should block (opt-in via env)
        enforce = os.getenv("LAZYDEV_ENFORCE_TDD") in {"1", "true", "TRUE"}
        try:
            min_tests = int(os.getenv("LAZYDEV_MIN_TESTS", "").strip() or "0")
        except Exception:
            min_tests = 0
        min_tests_val = min_tests if min_tests > 0 else None
        should_block, reason = should_block_completion(
            test_info, enforce_tdd=enforce, min_tests=min_tests_val
        )

        # Log the stop event
        log_stop_event(session_id, input_data, test_info, should_block, reason)

        if should_block:
            # Output blocking response
            output = {
                "approved": False,
                "reason": reason,
                "test_status": "failed" if test_info["tests_run"] else "not_run",
                "failures": (
                    test_info["test_failures"][:5] if test_info["test_failures"] else []
                ),
                "action": "Fix failing tests and continue",
            }

            print(json.dumps(output))

            # Print to stderr for visibility
            print(f"\n❌ BLOCKED: {reason}\n", file=sys.stderr)

            # Exit code 2 blocks completion
            sys.exit(2)
        else:
            # Allow completion
            output = {
                "approved": True,
                "reason": reason,
                "test_status": "passed",
                "test_count": test_info["test_count"],
                "coverage": test_info["coverage"],
                "message": "✅ Ready for review",
            }

            print(json.dumps(output))

            # Print success message
            print(f"\n✅ All tests passing! Ready for review.\n", file=sys.stderr)

            sys.exit(0)

    except json.JSONDecodeError as e:
        # Handle JSON decode errors gracefully - don't block on hook errors
        logger.warning(f"JSON decode error in stop: {type(e).__name__}")
        sys.exit(0)
    except IOError as e:
        # Handle file I/O errors gracefully
        logger.warning(f"I/O error in stop: {type(e).__name__}")
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully - don't block on hook errors
        logger.warning(f"Unexpected error in stop: {type(e).__name__}")
        sys.exit(0)


if __name__ == "__main__":
    main()
