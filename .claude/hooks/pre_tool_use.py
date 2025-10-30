#!/usr/bin/env python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Pre-tool-use hook for LAZY-DEV-FRAMEWORK.

Context-aware security and productivity gates:

CRITICAL BLOCKS (Security):
- Edits to sensitive files (.env, credentials, private keys)
- git push --force to main/master branches
- Dangerous rm -rf on critical paths (/, ~, system dirs)

SMART WARNINGS (Productivity):
- Large file edits (>100KB)
- Binary file modifications
- Protected branch operations
- Dependency chain awareness (package.json → lock files)

Philosophy: Guide developers, don't frustrate them.
Block only truly dangerous operations, warn on potentially problematic ones.
"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from hook_utils import sanitize_dict_for_logging

# Configure logging to stderr with timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Module-level compiled regex patterns for performance (10-100x faster)
# Compiled once at import time, not on every function call

# Dangerous rm command patterns
DANGEROUS_RM_PATTERNS = [
    re.compile(r"\brm\s+.*-[a-z]*r[a-z]*f"),  # rm -rf, rm -fr, rm -Rf, etc.
    re.compile(r"\brm\s+.*-[a-z]*f[a-z]*r"),  # rm -fr variations
    re.compile(r"\brm\s+--recursive\s+--force"),  # rm --recursive --force
    re.compile(r"\brm\s+--force\s+--recursive"),  # rm --force --recursive
    re.compile(r"\brm\s+-r\s+.*-f"),  # rm -r ... -f
    re.compile(r"\brm\s+-f\s+.*-r"),  # rm -f ... -r
]

# Dangerous path patterns
DANGEROUS_PATHS = [
    re.compile(r"\s+/$"),  # Root directory at end
    re.compile(r"\s+/\*"),  # Root with wildcard
    re.compile(r"\s+~/?$"),  # Home directory
    re.compile(r"\s+\$HOME"),  # Home environment variable
    re.compile(r"\s+\.\.$"),  # Parent directory
    re.compile(r"\s+\.\s*$"),  # Current directory at end
]

# Git force push patterns
FORCE_PUSH_PATTERNS = [
    re.compile(r"git\s+push\s+.*--force"),
    re.compile(r"git\s+push\s+.*-f\b"),
]

# Main/master branch patterns
MAIN_BRANCH_PATTERNS = [
    re.compile(r"\bmain\b"),
    re.compile(r"\bmaster\b"),
    re.compile(r"origin\s+main\b"),
    re.compile(r"origin\s+master\b"),
]

# Sensitive file patterns (specific patterns only)
SENSITIVE_PATTERNS = [
    re.compile(r"\.(pem|key|pfx|p12)\b"),  # File extensions only
    re.compile(r"API_KEY\s*[=:]"),  # Specific pattern
    re.compile(r"SECRET_KEY\s*[=:]"),  # Specific pattern
    re.compile(r"PASSWORD\s*[=:]"),  # Specific pattern
    re.compile(r"AWS_SECRET"),
    re.compile(r"PRIVATE_KEY"),
]

# Check for rm with recursive flag
RM_RECURSIVE_PATTERN = re.compile(r"\brm\s+.*-[a-z]*r")

# Binary file extensions (warn on edits)
BINARY_EXTENSIONS = {
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".bin",
    ".dat",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".rar",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".wav",
    ".pyc",
    ".pyo",
    ".class",
    ".o",
    ".a",
}

# Large file threshold (bytes)
LARGE_FILE_THRESHOLD = 100 * 1024  # 100KB

# Dependency file pairs (editing one should check the other)
DEPENDENCY_PAIRS = {
    "package.json": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
    "Cargo.toml": ["Cargo.lock"],
    "pyproject.toml": ["poetry.lock", "Pipfile.lock"],
    "composer.json": ["composer.lock"],
    "Gemfile": ["Gemfile.lock"],
}


def is_binary_file(file_path: str) -> bool:
    """
    Check if file is likely binary based on extension.

    Args:
        file_path: Path to check

    Returns:
        True if file appears to be binary
    """
    from pathlib import Path

    ext = Path(file_path).suffix.lower()
    return ext in BINARY_EXTENSIONS


def is_large_file(file_path: str) -> tuple[bool, int]:
    """
    Check if file exceeds size threshold.

    Args:
        file_path: Path to check

    Returns:
        Tuple of (is_large, size_in_bytes)
    """
    try:
        size = os.path.getsize(file_path)
        return size > LARGE_FILE_THRESHOLD, size
    except (OSError, FileNotFoundError):
        return False, 0


def check_dependency_chain(file_path: str) -> list[str]:
    """
    Check if editing this file should trigger warnings about related files.

    Args:
        file_path: File being edited

    Returns:
        List of related files that might need updating
    """
    from pathlib import Path

    file_name = Path(file_path).name
    warnings = []

    if file_name in DEPENDENCY_PAIRS:
        dir_path = Path(file_path).parent
        for related_file in DEPENDENCY_PAIRS[file_name]:
            related_path = dir_path / related_file
            if related_path.exists():
                warnings.append(str(related_path))

    return warnings


def get_current_branch() -> str:
    """
    Get current git branch name.

    Returns:
        Branch name or empty string if not in git repo
    """
    try:
        import subprocess

        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def is_dangerous_rm_command(command: str) -> bool:
    """
    Comprehensive detection of dangerous rm commands.

    Matches various forms of rm -rf and similar destructive patterns.

    Args:
        command: The bash command to analyze

    Returns:
        True if dangerous rm pattern detected, False otherwise
    """
    # Normalize command by removing extra spaces and converting to lowercase
    normalized = " ".join(command.lower().split())

    # Pattern 1: Standard rm -rf variations (use pre-compiled patterns)
    for pattern in DANGEROUS_RM_PATTERNS:
        if pattern.search(normalized):
            return True

    # Pattern 2: Check for rm with recursive flag targeting dangerous paths
    if RM_RECURSIVE_PATTERN.search(normalized):  # If rm has recursive flag
        for path_pattern in DANGEROUS_PATHS:
            if path_pattern.search(normalized):
                return True

    return False


def is_force_push_to_main(command: str) -> bool:
    """
    Detect git push --force to main or master branches.

    Args:
        command: The bash command to analyze

    Returns:
        True if force push to main/master detected, False otherwise
    """
    normalized = " ".join(command.lower().split())

    # Check for force push patterns (use pre-compiled patterns)
    has_force = any(pattern.search(normalized) for pattern in FORCE_PUSH_PATTERNS)

    if not has_force:
        return False

    # Check if targeting main/master (use pre-compiled patterns)
    return any(pattern.search(normalized) for pattern in MAIN_BRANCH_PATTERNS)


def is_sensitive_file_access(tool_name: str, tool_input: dict) -> tuple[bool, str]:
    """
    Check if any tool is trying to access sensitive files.

    Args:
        tool_name: Name of the tool being used
        tool_input: Input parameters for the tool

    Returns:
        Tuple of (is_sensitive, file_name)
    """
    sensitive_files = [
        ".env",
        ".env.local",
        ".env.production",
        ".env.development",
        "secrets.json",
        "credentials.json",
        "private.key",
        "id_rsa",
        "id_ed25519",
        ".ssh/config",
        ".aws/credentials",
    ]

    # Check file-based tools
    if tool_name in ["Read", "Edit", "MultiEdit", "Write"]:
        file_path = tool_input.get("file_path", "")

        # Allow .env.sample and .env.example
        if ".env.sample" in file_path or ".env.example" in file_path:
            return False, ""

        for sensitive in sensitive_files:
            if sensitive in file_path:
                logger.warning(f"Blocked access to sensitive file: {sensitive}")
                return True, sensitive

    # Check bash commands
    elif tool_name == "Bash":
        command = tool_input.get("command", "")

        # Allow .env.sample and .env.example
        if ".env.sample" in command or ".env.example" in command:
            return False, ""

        for sensitive in sensitive_files:
            # Note: These patterns must be compiled dynamically due to variable 'sensitive'
            patterns = [
                rf"\b{re.escape(sensitive)}\b",
                rf"cat\s+.*{re.escape(sensitive)}",
                rf"echo\s+.*>\s*{re.escape(sensitive)}",
                rf"touch\s+.*{re.escape(sensitive)}",
                rf"cp\s+.*{re.escape(sensitive)}",
                rf"mv\s+.*{re.escape(sensitive)}",
            ]
            for pattern in patterns:
                if re.search(pattern, command):
                    logger.warning(f"Blocked access to sensitive file: {sensitive}")
                    return True, sensitive

        # Check for specific secret patterns (use pre-compiled patterns)
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(command):
                logger.warning("Blocked access to sensitive pattern")
                return True, "sensitive-pattern"

    return False, ""


def generate_warnings(tool_name: str, tool_input: dict) -> list[str]:
    """
    Generate non-blocking warnings for potentially problematic operations.

    Args:
        tool_name: Name of the tool being used
        tool_input: Input parameters for the tool

    Returns:
        List of warning messages (empty if no warnings)
    """
    warnings = []

    # Check file-based tools for potential issues
    if tool_name in ["Write", "Edit"]:
        file_path = tool_input.get("file_path", "")

        if file_path:
            # Warning 1: Binary file modification
            if is_binary_file(file_path):
                warnings.append(
                    f"⚠ WARNING: Attempting to edit binary file: {file_path}\n"
                    "  Binary files should not be edited as text."
                )

            # Warning 2: Large file modification
            is_large, size = is_large_file(file_path)
            if is_large:
                size_kb = size / 1024
                warnings.append(
                    f"⚠ WARNING: Editing large file ({size_kb:.1f}KB): {file_path}\n"
                    "  Consider editing in smaller chunks to avoid context overflow."
                )

            # Warning 3: Dependency chain awareness
            related_files = check_dependency_chain(file_path)
            if related_files:
                warnings.append(
                    f"ℹ INFO: Editing {file_path} may require updating:\n"
                    + "\n".join(f"  - {f}" for f in related_files)
                )

            # Warning 4: Protected branch operation
            branch = get_current_branch()
            if branch in ["main", "master"]:
                warnings.append(
                    f"⚠ WARNING: Editing on protected branch '{branch}'\n"
                    "  Consider creating a feature branch instead."
                )

    return warnings


def log_tool_call(input_data: dict) -> None:
    """
    Log tool call to pre_tool_use.json for audit trail with sanitization.

    Args:
        input_data: The hook input data
    """
    log_dir = Path(os.getenv("LAZYDEV_LOG_DIR", ".claude/data/logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "pre_tool_use.json"

    # Read existing log data or initialize empty list
    if log_path.exists():
        try:
            with open(log_path, "r") as f:
                log_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            log_data = []
    else:
        log_data = []

    # Sanitize input data before logging (removes sensitive information)
    sanitized_data = sanitize_dict_for_logging(input_data)

    # Add timestamp
    log_entry = {"timestamp": datetime.now().isoformat(), **sanitized_data}

    # Append new data
    log_data.append(log_entry)

    # Write back to file with formatting
    try:
        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=2)
    except IOError as e:
        logger.warning(f"Failed to write log file: {type(e).__name__}")


def main():
    """Hook entry point."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        # === CRITICAL SECURITY BLOCKS (Non-negotiable) ===

        # Block 1: Sensitive file access
        is_sensitive, file_name = is_sensitive_file_access(tool_name, tool_input)
        if is_sensitive:
            print(
                f"BLOCKED: Access to sensitive file '{file_name}' is prohibited",
                file=sys.stderr,
            )
            print(
                "Use .env.sample or .env.example for template files instead",
                file=sys.stderr,
            )
            sys.exit(2)  # Exit code 2 blocks tool call

        # Bash command security checks
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            normalized = " ".join(command.lower().split())

            # Block 2: sudo commands (unless explicitly allowed)
            if "sudo " in normalized and os.getenv("LAZYDEV_ALLOW_SUDO") not in {
                "1",
                "true",
                "TRUE",
            }:
                print(
                    "BLOCKED: sudo is disabled for safety (set LAZYDEV_ALLOW_SUDO=1 to allow)",
                    file=sys.stderr,
                )
                sys.exit(2)

            # Block 3: Dangerous rm commands
            if is_dangerous_rm_command(command):
                print(
                    "BLOCKED: Dangerous rm command detected and prevented",
                    file=sys.stderr,
                )
                print(f"Command: {command}", file=sys.stderr)
                sys.exit(2)

            # Block 4: Force push to main/master
            if is_force_push_to_main(command):
                print(
                    "BLOCKED: Force push to main/master branch is prohibited",
                    file=sys.stderr,
                )
                print("This prevents rewriting production history", file=sys.stderr)
                sys.exit(2)

        # === SMART WARNINGS (Productivity helpers, non-blocking) ===

        warnings = generate_warnings(tool_name, tool_input)
        if warnings:
            # Print warnings to stderr but don't block
            for warning in warnings:
                print(warning, file=sys.stderr)

        # Log all tool calls for audit trail
        log_tool_call(input_data)

        # Output success JSON
        output = {
            "approved": True,
            "logged": True,
            "tool": tool_name,
            "session_id": input_data.get("session_id", "unknown"),
        }
        print(json.dumps(output))

        sys.exit(0)

    except json.JSONDecodeError as e:
        # Gracefully handle JSON decode errors
        logger.warning(f"JSON decode error in pre_tool_use: {type(e).__name__}")
        sys.exit(0)
    except IOError as e:
        # Handle file I/O errors gracefully
        logger.warning(f"I/O error in pre_tool_use: {type(e).__name__}")
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully - don't block on hook failures
        logger.warning(f"Unexpected error in pre_tool_use: {type(e).__name__}")
        sys.exit(0)


if __name__ == "__main__":
    main()
