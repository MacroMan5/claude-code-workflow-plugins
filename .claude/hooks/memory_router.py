#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Memory Router (stub)

Purpose: placeholder hook for future automation that routes session
context to MCP Memory tools. Safe no-op by default; controlled with
`LAZYDEV_ENABLE_MEMORY_ROUTER=1`.

Behavior when enabled:
- Reads JSON input from stdin
- Appends a lightweight record to `.claude/data/memory_router.jsonl`
- Does NOT call MCP tools directly (model should do tool use)

This allows incremental rollout without impacting normal workflows.
"""

import json
import logging
import os
import sys
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error in memory_router: {type(e).__name__}")
        data = {}
    except IOError as e:
        logger.warning(f"I/O error in memory_router: {type(e).__name__}")
        data = {}
    except Exception as e:
        logger.warning(f"Unexpected error in memory_router: {type(e).__name__}")
        data = {}

    if os.getenv("LAZYDEV_ENABLE_MEMORY_ROUTER") not in {"1", "true", "TRUE"}:
        # Disabled: exit quietly
        sys.exit(0)

    try:
        log_dir = Path(".claude/data")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "memory_router.jsonl"

        record = {
            "timestamp": datetime.now().isoformat(),
            "event": data.get("event_type") or data.get("event") or "unknown",
            "session_id": data.get("session_id") or "unknown",
            "note": "Router enabled (stub). Model should use mcp__memory__* tools per Skill.",
        }

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except IOError as e:
        logger.warning(f"Failed to write memory_router log: {type(e).__name__}")
    except Exception as e:
        logger.warning(f"Unexpected error in memory_router logging: {type(e).__name__}")

    # Always succeed
    sys.exit(0)


if __name__ == "__main__":
    main()

