#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Event logging hook for LAZY-DEV-FRAMEWORK.

Structured logging & observability - records all agent actions:
- Creates session directory: logs/{session_id}/
- Appends events to JSONL: logs/{session_id}/events.jsonl
- Structured event format with timestamp, event type, tool info

Reference: PROJECT-MANAGEMENT-LAZY_DEV/docs/HOOKS.md (Event Logging)
"""

import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from hook_utils import sanitize_for_logging, sanitize_dict_for_logging

logger = logging.getLogger(__name__)


def parse_args(argv: list[str]) -> str | None:
    """
    Parse optional CLI arguments.

    Supports: log_events.py --event EVENT_NAME
    """
    if "--event" in argv:
        idx = argv.index("--event")
        if idx + 1 < len(argv):
            return argv[idx + 1]
    return None


def create_event_entry(input_data: dict, override_event: str | None) -> dict:
    """
    Create structured event entry.

    Args:
        input_data: Hook input data

    Returns:
        Structured event dictionary
    """
    # Extract core event data
    event = {
        "timestamp": datetime.now().isoformat(),
        "session_id": input_data.get("session_id", "unknown"),
        "event_type": override_event
        or input_data.get("event_type")
        or input_data.get("hook_event")
        or "Unknown",
    }

    # Add tool-specific data
    tool_name = input_data.get("tool_name")
    if tool_name:
        event["tool"] = tool_name

    tool_input = input_data.get("tool_input")
    if tool_input:
        # Sanitize tool input - don't log full file contents OR sensitive data
        sanitized_input = {}

        if "command" in tool_input:
            # Sanitize command to remove secrets
            sanitized_input["command"] = sanitize_for_logging(tool_input["command"])

        if "description" in tool_input:
            sanitized_input["description"] = tool_input["description"]

        if "file_path" in tool_input:
            sanitized_input["file_path"] = tool_input["file_path"]

        if "pattern" in tool_input:
            sanitized_input["pattern"] = tool_input["pattern"]

        if sanitized_input:
            event["tool_input"] = sanitized_input

    # Add result if available
    result = input_data.get("result")
    if result:
        # Truncate long results
        if isinstance(result, str) and len(result) > 500:
            event["result"] = result[:500] + "... (truncated)"
        else:
            event["result"] = result

    # Add error info if available
    error = input_data.get("error")
    if error:
        event["error"] = error

    return event


def log_to_jsonl(session_id: str, event: dict) -> None:
    """
    Append event to session JSONL log file.

    Args:
        session_id: Session identifier
        event: Event dictionary to log
    """
    # Create session directory
    base_dir = Path(os.getenv("LAZYDEV_LOG_DIR", ".claude/data/logs"))
    session_dir = base_dir / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    # JSONL log file
    log_file = session_dir / "events.jsonl"

    # Append event as single JSON line
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def log_to_master(event: dict) -> None:
    """
    Also log to master log file for all sessions.

    Args:
        event: Event dictionary to log
    """
    log_dir = Path(os.getenv("LAZYDEV_LOG_DIR", ".claude/data/logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    master_log = log_dir / "all_events.jsonl"

    # Append to master JSONL
    with open(master_log, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def main():
    """Hook entry point."""
    try:
        override_event = parse_args(sys.argv[1:])

        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        session_id = input_data.get("session_id", "unknown")

        # Create structured event
        event = create_event_entry(input_data, override_event)

        # Log to session-specific JSONL
        log_to_jsonl(session_id, event)

        # Also log to master log
        log_to_master(event)

        # Output confirmation
        output = {
            "logged": True,
            "session_id": session_id,
            "log_file": str(
                (
                    Path(os.getenv("LAZYDEV_LOG_DIR", ".claude/data/logs"))
                    / session_id
                    / "events.jsonl"
                )
            ),
            "event_type": event.get("event_type"),
        }

        print(json.dumps(output))

        sys.exit(0)

    except json.JSONDecodeError as e:
        # Handle JSON decode errors gracefully
        logger.warning(f"JSON decode error in log_events: {type(e).__name__}")
        sys.exit(0)
    except IOError as e:
        # Handle file I/O errors gracefully
        logger.warning(f"I/O error in log_events: {type(e).__name__}")
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully - logging should never block
        logger.warning(f"Unexpected error in log_events: {type(e).__name__}")
        sys.exit(0)


if __name__ == '__main__':
    main()
