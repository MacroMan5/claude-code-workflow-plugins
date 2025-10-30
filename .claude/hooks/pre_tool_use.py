#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Pre-tool-use hook for LAZY-DEV-FRAMEWORK.

Security gates - blocks dangerous operations before execution:
- rm -rf commands with recursive flags
- git push --force to main/master branches
- Edits to sensitive files (.env, secrets.json, credentials.json)
- Directory scanning prevention (node_modules, .git, __pycache__, dist, build)
- SQL injection patterns

Reference: PROJECT-MANAGEMENT-LAZY_DEV/docs/HOOKS.md (PreToolUse)
Inspired by: Reddit Claude Code community best practices
"""

import json
import logging
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from hook_utils import sanitize_for_logging, sanitize_dict_for_logging

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

# Directory scanning command patterns
SCAN_COMMAND_PATTERNS = [
    re.compile(r"\bfind\b"),
    re.compile(r"\bgrep\s+-[a-z]*r"),  # grep -r, grep -rn, etc.
    re.compile(r"\brg\b"),  # ripgrep
    re.compile(r"\bag\b"),  # ag (the silver searcher)
    re.compile(r"\bls\s+-[a-z]*R"),  # ls -R
    re.compile(r"\btree\b"),
]

# Check for rm with recursive flag
RM_RECURSIVE_PATTERN = re.compile(r"\brm\s+.*-[a-z]*r")

# Find current directory pattern
FIND_CWD_PATTERN = re.compile(r"\bfind\s+\.")

# Command injection patterns
COMMAND_INJECTION_PATTERNS = [
    re.compile(r"\bsh\s+-c\b"),  # sh -c
    re.compile(r"\bbash\s+-c\b"),  # bash -c
    re.compile(r"\beval\s+"),  # eval command
    re.compile(r"\bexec\s+"),  # exec command
    re.compile(r"\$\([^)]+\)"),  # $(command) substitution
    re.compile(r"`[^`]+`"),  # `command` substitution
    re.compile(r"\|\s*(sh|bash|zsh)\b"),  # | sh/bash/zsh pipes
]


def has_command_injection(command: str) -> bool:
    """
    Detect command injection patterns.

    Checks for:
    - Shell execution: sh -c, bash -c
    - Code evaluation: eval, exec
    - Command substitution: $(...), `...`
    - Pipe to shell: | sh, | bash

    Args:
        command: The bash command to analyze

    Returns:
        True if command injection pattern detected, False otherwise
    """
    normalized = command.lower()

    for pattern in COMMAND_INJECTION_PATTERNS:
        if pattern.search(normalized):
            return True

    return False


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


def is_directory_scan_blocked(command: str) -> tuple[bool, str]:
    """
    Detect and block scanning of restricted directories that cause slowdowns.

    Prevents Claude from scanning directories with large numbers of files:
    - node_modules/ (can have 100K+ files)
    - .git/ (contains repository history and secrets)
    - __pycache__/ (Python bytecode cache)
    - dist/, build/ (build artifacts)
    - .venv/, venv/ (virtual environments)
    - .next/ (Next.js build cache)
    - .cache/ (various caches)

    This prevents:
    1. Extreme performance degradation from scanning large directories
    2. Context pollution with irrelevant files
    3. Leaking sensitive data from .git and .env
    4. Wasting API tokens on build artifacts

    Based on Reddit best practices for Claude Code hooks.

    Args:
        command: The bash command to analyze

    Returns:
        Tuple of (is_blocked, blocked_directory)
    """
    # Blocked directory patterns
    blocked_dirs = [
        "node_modules",
        ".git",
        "__pycache__",
        "dist",
        "build",
        ".venv",
        "venv",
        ".next",
        ".cache",
        "target",  # Rust build directory
        "bin",  # Binary directories
        "obj",  # C# build artifacts
    ]

    # Normalize command
    normalized = " ".join(command.lower().split())

    # Check if command is a scanning command (use pre-compiled patterns)
    is_scan_command = any(
        pattern.search(normalized) for pattern in SCAN_COMMAND_PATTERNS
    )

    if not is_scan_command:
        return False, ""

    # Check if any blocked directory is referenced
    for blocked_dir in blocked_dirs:
        patterns = [
            rf"\b{re.escape(blocked_dir)}\b",  # Direct mention
            rf"[/\\]{re.escape(blocked_dir)}[/\\]",  # In path
            rf"\*[/\\]{re.escape(blocked_dir)}",  # With wildcard
            rf"{re.escape(blocked_dir)}[/\\]\*",  # Trailing wildcard
        ]

        for pattern in patterns:
            if re.search(pattern, normalized):
                return True, blocked_dir

    # Check for find with path patterns that would include blocked dirs (use pre-compiled pattern)
    if FIND_CWD_PATTERN.search(normalized):  # find . (current directory recursively)
        # Allow if explicitly excludes blocked directories
        excludes_blocked = any(
            f'-not -path "*/{blocked_dir}/*"' in command
            or f"-prune -name {blocked_dir}" in command
            for blocked_dir in blocked_dirs
        )

        if not excludes_blocked:
            # Check if command seems to be searching entire tree
            if not any(name in command for name in ["-name", "-type f", "-maxdepth"]):
                return True, "current_directory_without_filters"

    return False, ""


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

        # Security Check 1: Sensitive file access
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

        # Security Check 2: Dangerous rm commands
        if tool_name == "Bash":
            command = tool_input.get("command", "")
            normalized = " ".join(command.lower().split())
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

            if is_dangerous_rm_command(command):
                print(
                    "BLOCKED: Dangerous rm command detected and prevented",
                    file=sys.stderr,
                )
                print(f"Command: {command}", file=sys.stderr)
                sys.exit(2)

            # Security Check 3: Force push to main/master
            if is_force_push_to_main(command):
                print(
                    "BLOCKED: Force push to main/master branch is prohibited",
                    file=sys.stderr,
                )
                print("This prevents rewriting production history", file=sys.stderr)
                sys.exit(2)

            # Security Check 4: Directory scanning prevention
            is_blocked, blocked_dir = is_directory_scan_blocked(command)
            if is_blocked:
                print(
                    f"BLOCKED: Scanning '{blocked_dir}' directory is prohibited",
                    file=sys.stderr,
                )
                print(
                    "This prevents performance issues and context pollution.",
                    file=sys.stderr,
                )
                print(
                    f"Tip: Use Glob or Grep tools instead of bash find/grep for code search.",
                    file=sys.stderr,
                )
                sys.exit(2)

            # Security Check 5: Command injection detection
            if has_command_injection(command):
                print("BLOCKED: Command injection pattern detected", file=sys.stderr)
                logger.warning(f"Command injection attempt: {command[:100]}")
                sys.exit(2)

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
