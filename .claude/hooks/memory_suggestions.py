#!/usr/bin/env python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
PostToolUse heuristic suggester for Memory Graph.

If the last tool result appears to include durable facts, emit a small
hint to the model suggesting MCP memory actions. This does not mutate
state or call tools; it only suggests next steps. Disable via
LAZYDEV_DISABLE_MEMORY_SUGGEST=1.
"""

import json
import logging
import os
import sys

# Configure logging to stderr with timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


KEY_MARKERS = (
    "owner:",
    "maintainer:",
    "repo:",
    "endpoint:",
    "base url:",
    "service:",
    "person:",
    "dataset:",
    "api:",
    "team:",
)


def likely_durable(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in KEY_MARKERS)


def main() -> None:
    if os.getenv("LAZYDEV_DISABLE_MEMORY_SUGGEST") in {"1", "true", "TRUE"}:
        sys.exit(0)

    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    # Expect optional keys like 'result' or 'tool_result'
    result = data.get("result") or data.get("tool_result") or ""
    if not isinstance(result, str) or not result.strip():
        # Some tools return structured; consider 'stdout' if present
        if isinstance(result, dict):
            result = json.dumps(result)
        else:
            result = str(result)

    if not likely_durable(result):
        sys.exit(0)

    suggestion = {
        "memory_suggestion": True,
        "hint": "Consider persisting durable facts using Memory MCP.",
        "next_steps": [
            "mcp__memory__search_nodes to find/avoid duplicates",
            "mcp__memory__create_entities for new items",
            "mcp__memory__add_observations with small facts (include dates)",
            "mcp__memory__create_relations to connect entities",
        ],
    }
    print(json.dumps(suggestion))
    sys.exit(0)


if __name__ == "__main__":
    main()
