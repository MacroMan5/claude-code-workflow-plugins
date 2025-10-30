#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Post-tool-use formatting hook for LAZY-DEV-FRAMEWORK.

Auto-format code after edits:
- Python (.py) -> Black + Ruff format
- JavaScript/TypeScript (.js, .ts, .tsx, .jsx) -> Prettier
- Rust (.rs) -> rustfmt
- Markdown (.md) -> Custom formatting

Reference: PROJECT-MANAGEMENT-LAZY_DEV/docs/HOOKS.md (PostToolUse)
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def get_file_path(tool_name: str, tool_input: dict) -> str | None:
    """
    Extract file path from tool input.

    Args:
        tool_name: Name of the tool used
        tool_input: Tool input parameters

    Returns:
        File path if available, None otherwise
    """
    if tool_name in ["Edit", "MultiEdit", "Write"]:
        return tool_input.get("file_path")

    return None


def format_python(file_path: Path) -> tuple[bool, str]:
    """
    Format Python file with Black and Ruff.

    Args:
        file_path: Path to Python file

    Returns:
        Tuple of (success, message)
    """
    try:
        # Try Black first
        result = subprocess.run(
            ["black", "--quiet", str(file_path)],
            capture_output=True,
            text=True,
            timeout=3,
        )

        black_success = result.returncode == 0

        # Try Ruff format
        result = subprocess.run(
            ["ruff", "format", str(file_path)],
            capture_output=True,
            text=True,
            timeout=3,
        )

        ruff_success = result.returncode == 0

        if black_success or ruff_success:
            tools = []
            if black_success:
                tools.append("Black")
            if ruff_success:
                tools.append("Ruff")

            return True, f"Formatted with {' + '.join(tools)}"

    except subprocess.TimeoutExpired:
        logger.warning("Python formatter timed out (3s)")
    except subprocess.SubprocessError as e:
        logger.warning(f"Formatter subprocess error: {type(e).__name__}")
    except FileNotFoundError:
        logger.debug("Black/Ruff not found in PATH")

    return False, "Formatters not available (Black/Ruff)"


def format_javascript(file_path: Path) -> tuple[bool, str]:
    """
    Format JavaScript/TypeScript file with Prettier.

    Args:
        file_path: Path to JS/TS file

    Returns:
        Tuple of (success, message)
    """
    try:
        result = subprocess.run(
            ["npx", "prettier", "--write", str(file_path)],
            capture_output=True,
            text=True,
            timeout=3,
        )

        if result.returncode == 0:
            return True, "Formatted with Prettier"

    except subprocess.TimeoutExpired:
        logger.warning("Prettier timed out (10s)")
    except subprocess.SubprocessError as e:
        logger.warning(f"Prettier subprocess error: {type(e).__name__}")
    except FileNotFoundError:
        logger.debug("Prettier not found (npx)")

    return False, "Prettier not available"


def format_rust(file_path: Path) -> tuple[bool, str]:
    """
    Format Rust file with rustfmt.

    Args:
        file_path: Path to Rust file

    Returns:
        Tuple of (success, message)
    """
    try:
        result = subprocess.run(
            ["rustfmt", str(file_path)], capture_output=True, text=True, timeout=3
        )

        if result.returncode == 0:
            return True, "Formatted with rustfmt"

    except subprocess.TimeoutExpired:
        logger.warning("rustfmt timed out (10s)")
    except subprocess.SubprocessError as e:
        logger.warning(f"rustfmt subprocess error: {type(e).__name__}")
    except FileNotFoundError:
        logger.debug("rustfmt not found in PATH")

    return False, "rustfmt not available"


def format_file(file_path: str) -> dict:
    """
    Format file based on extension.

    Args:
        file_path: Path to file to format

    Returns:
        Dictionary with formatting results
    """
    path = Path(file_path)

    if not path.exists():
        return {"formatted": False, "file": file_path, "reason": "File does not exist"}

    suffix = path.suffix.lower()

    # Skip documentation files (no formatting needed)
    if suffix in [".md", ".txt", ".rst", ".adoc", ".json"]:
        return {
            "formatted": False,
            "file": file_path,
            "type": "documentation",
            "message": "Skipped (documentation file)",
        }

    # Python files
    if suffix == ".py":
        success, message = format_python(path)
        return {
            "formatted": success,
            "file": file_path,
            "type": "python",
            "tool_used": "Black + Ruff" if success else None,
            "message": message,
        }

    # JavaScript/TypeScript files
    elif suffix in [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]:
        success, message = format_javascript(path)
        return {
            "formatted": success,
            "file": file_path,
            "type": "javascript",
            "tool_used": "Prettier" if success else None,
            "message": message,
        }

    # Rust files
    elif suffix == ".rs":
        success, message = format_rust(path)
        return {
            "formatted": success,
            "file": file_path,
            "type": "rust",
            "tool_used": "rustfmt" if success else None,
            "message": message,
        }

    # Unsupported file type
    else:
        return {
            "formatted": False,
            "file": file_path,
            "type": "unsupported",
            "message": f"No formatter for {suffix} files",
        }


def log_formatting(input_data: dict, format_result: dict) -> None:
    """
    Log formatting results to logs/post_tool_use_format.json.

    Args:
        input_data: Hook input data
        format_result: Formatting results
    """
    log_dir = Path(os.getenv("LAZYDEV_LOG_DIR", ".claude/data/logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "post_tool_use_format.json"

    # Read existing log data or initialize empty list
    if log_file.exists():
        try:
            with open(log_file, "r") as f:
                log_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            log_data = []
    else:
        log_data = []

    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": input_data.get("session_id", "unknown"),
        "tool_name": input_data.get("tool_name"),
        "format_result": format_result,
    }

    # Append new data
    log_data.append(log_entry)

    # Write back to file
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)


def main():
    """Hook entry point."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # Get file path
        file_path = get_file_path(tool_name, tool_input)

        if not file_path:
            # No file to format
            sys.exit(0)

        # Format the file
        format_result = format_file(file_path)

        # Log the formatting
        log_formatting(input_data, format_result)

        # Output result (optional feedback to Claude)
        if format_result["formatted"]:
            output = {
                "formatted": True,
                "file": file_path,
                "message": format_result["message"],
            }
            print(json.dumps(output))

        sys.exit(0)

    except json.JSONDecodeError as e:
        # Handle JSON decode errors gracefully
        logger.warning(f"JSON decode error in post_tool_use_format: {type(e).__name__}")
        sys.exit(0)
    except IOError as e:
        # Handle file I/O errors gracefully
        logger.warning(f"I/O error in post_tool_use_format: {type(e).__name__}")
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully - don't block
        logger.warning(f"Unexpected error in post_tool_use_format: {type(e).__name__}")
        sys.exit(0)


if __name__ == "__main__":
    main()
