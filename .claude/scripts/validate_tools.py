#!/usr/bin/env python3
"""Validate that all required tools are installed and working."""

import subprocess
import sys
from typing import List, Tuple


def check_tool(tool_name: str, command: List[str]) -> Tuple[bool, str]:
    """
    Check if a tool is installed and accessible.

    Args:
        tool_name: Display name of the tool.
        command: Command to run to check tool (e.g., ["black", "--version"]).

    Returns:
        Tuple of (success: bool, message: str).
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            # Extract version from output
            version = result.stdout.strip().split("\n")[0]
            return True, f"✅ {tool_name}: {version}"
        else:
            return False, f"❌ {tool_name}: Command failed (exit {result.returncode})"

    except FileNotFoundError:
        return False, f"❌ {tool_name}: Not installed"
    except subprocess.TimeoutExpired:
        return False, f"❌ {tool_name}: Timeout"
    except Exception as e:
        return False, f"❌ {tool_name}: Error - {str(e)}"


def main() -> None:
    """Main validation logic."""
    print("Validating Quality Pipeline Tools")
    print("=" * 60)

    # Define tools to check
    tools = [
        ("Python", ["python", "--version"]),
        ("Black", ["black", "--version"]),
        ("Ruff", ["ruff", "--version"]),
        ("Mypy", ["mypy", "--version"]),
        ("Pytest", ["pytest", "--version"]),
        ("Git", ["git", "--version"]),
        ("GitHub CLI", ["gh", "--version"]),
    ]

    results = []
    for tool_name, command in tools:
        success, message = check_tool(tool_name, command)
        results.append((success, message))
        print(message)

    print("=" * 60)

    # Summary
    passed = sum(1 for success, _ in results if success)
    total = len(results)

    print(f"\nSummary: {passed}/{total} tools available")

    if passed == total:
        print("All tools are installed and working")
        print("\nYou can now run the quality pipeline:")
        print("  python scripts/run_pipeline.py src/")
        sys.exit(0)
    else:
        print("Some tools are missing")
        print("\nInstallation instructions:")

        # Check which tools are missing
        failed = [
            (name, cmd)
            for (success, _), (name, cmd) in zip(results, tools)
            if not success
        ]

        if any(
            "Black" in name or "Ruff" in name or "Mypy" in name or "Pytest" in name
            for name, _ in failed
        ):
            print("\n  Install Python tools:")
            print("    pip install black ruff mypy pytest pytest-cov")
            print("  or:")
            print("    uv sync")

        if any("GitHub CLI" in name for name, _ in failed):
            print("\n  Install GitHub CLI:")
            print("    macOS:   brew install gh")
            print("    Windows: winget install GitHub.cli")
            print("    Linux:   See https://cli.github.com")
            print("\n  Then authenticate:")
            print("    gh auth login")

        if any("Git" in name for name, _ in failed):
            print("\n  Install Git:")
            print("    https://git-scm.com/downloads")

        sys.exit(1)


if __name__ == "__main__":
    main()
