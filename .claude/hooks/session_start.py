#!/usr/bin/env python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Session start hook for LAZY-DEV-FRAMEWORK.

Loads repository context at session initialization:
- Load PRD.md if exists
- Load TASKS.md if exists
- Get recent git commits
- Initialize session state file
- Log session start event

Reference: PROJECT-MANAGEMENT-LAZY_DEV/docs/HOOKS.md (SessionStart)
"""

import json
import logging
import os
import re
import subprocess
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


def load_prd() -> str | None:
    """
    Load PRD.md if it exists.

    Returns:
        PRD content or None
    """
    prd_path = Path("PRD.md")

    if prd_path.exists():
        try:
            return prd_path.read_text(encoding="utf-8")
        except IOError as e:
            logger.warning(f"Failed to load PRD.md: {type(e).__name__}")
        except Exception as e:
            logger.warning(f"Unexpected error loading PRD.md: {type(e).__name__}")

    return None


def load_tasks() -> str | None:
    """
    Load TASKS.md if it exists.

    Returns:
        TASKS content or None
    """
    tasks_path = Path("TASKS.md")

    if tasks_path.exists():
        try:
            return tasks_path.read_text(encoding="utf-8")
        except IOError as e:
            logger.warning(f"Failed to load TASKS.md: {type(e).__name__}")
        except Exception as e:
            logger.warning(f"Unexpected error loading TASKS.md: {type(e).__name__}")

    return None


def get_git_history() -> list[str]:
    """
    Get recent git commits (last 10).

    Returns:
        List of commit messages
    """
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            capture_output=True,
            text=True,
            timeout=3,
        )

        if result.returncode == 0:
            commits = result.stdout.strip().split("\n")
            return [c for c in commits if c]
        else:
            logger.debug(f"Git log failed with code {result.returncode}")

    except subprocess.TimeoutExpired:
        logger.warning("Git log operation timed out (3s)")
    except subprocess.SubprocessError as e:
        logger.warning(f"Git subprocess error: {type(e).__name__}")
    except FileNotFoundError:
        logger.debug("Git not found in PATH")

    return []


def get_current_branch() -> str | None:
    """
    Get current git branch.

    Returns:
        Branch name or None
    """
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=2,
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            logger.debug(f"Git branch command failed with code {result.returncode}")

    except subprocess.TimeoutExpired:
        logger.warning("Git branch operation timed out (2s)")
    except subprocess.SubprocessError as e:
        logger.warning(f"Git subprocess error: {type(e).__name__}")
    except FileNotFoundError:
        logger.debug("Git not found in PATH")

    return None


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


def initialize_session_state(session_id: str, context: dict) -> None:
    """
    Initialize session state file in .claude/data/sessions/.

    Args:
        session_id: Session identifier
        context: Loaded context data
    """
    # Validate session_id format
    if not validate_session_id(session_id):
        logger.error(f"Invalid session_id format: {session_id}")
        return  # Fail silently, don't create file

    sessions_dir = Path(".claude/data/sessions")
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Now safe - session_id is validated
    session_file = sessions_dir / f"{session_id}.json"

    session_data = {
        "session_id": session_id,
        "started_at": datetime.now().isoformat(),
        "context": {
            "prd_loaded": context["prd"] is not None,
            "tasks_loaded": context["tasks"] is not None,
            "git_history_loaded": len(context["git_history"]) > 0,
            "branch": context["branch"],
        },
        "prompts": [],
    }

    try:
        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2)
    except IOError as e:
        logger.warning(f"Failed to write session file: {type(e).__name__}")
    except Exception as e:
        logger.warning(f"Unexpected error writing session file: {type(e).__name__}")


def log_session_start(session_id: str, context: dict) -> None:
    """
    Log session start event.

    Args:
        session_id: Session identifier
        context: Loaded context
    """
    log_dir = Path(os.getenv("LAZYDEV_LOG_DIR", ".claude/data/logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "session_start.json"

    # Read existing log or initialize
    if log_file.exists():
        try:
            with open(log_file, "r") as f:
                log_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            log_data = []
    else:
        log_data = []

    # Add session start entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "context_loaded": {
            "prd": context["prd"] is not None,
            "tasks": context["tasks"] is not None,
            "git_history": len(context["git_history"]),
            "branch": context["branch"],
        },
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

        # Load repository context
        context = {
            "prd": load_prd(),
            "tasks": load_tasks(),
            "git_history": get_git_history(),
            "branch": get_current_branch(),
        }

        # Initialize session state file
        initialize_session_state(session_id, context)

        # Log session start
        log_session_start(session_id, context)

        # Output summary
        output = {
            "session_id": session_id,
            "context_loaded": {
                "prd": context["prd"] is not None,
                "tasks": context["tasks"] is not None,
                "git_history": len(context["git_history"]) > 0,
                "branch": context["branch"],
            },
            "message": "Session context loaded successfully",
        }

        print(json.dumps(output))

        # Also print user-friendly message to stderr (visible in console)
        print("\n=== LAZY-DEV-FRAMEWORK Session Started ===", file=sys.stderr)
        print(f"Session ID: {session_id}", file=sys.stderr)
        print(f'PRD loaded: {"✓" if context["prd"] else "✗"}', file=sys.stderr)
        print(f'TASKS loaded: {"✓" if context["tasks"] else "✗"}', file=sys.stderr)
        print(f'Git branch: {context["branch"] or "N/A"}', file=sys.stderr)
        print(f'Git history: {len(context["git_history"])} commits', file=sys.stderr)
        print("==========================================\n", file=sys.stderr)

        sys.exit(0)

    except json.JSONDecodeError as e:
        # Handle JSON decode errors gracefully
        logger.warning(f"JSON decode error in session_start: {type(e).__name__}")
        sys.exit(0)
    except IOError as e:
        # Handle file I/O errors gracefully
        logger.warning(f"I/O error in session_start: {type(e).__name__}")
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully
        logger.warning(f"Unexpected error in session_start: {type(e).__name__}")
        sys.exit(0)


if __name__ == "__main__":
    main()
