#!/usr/bin/env python
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
PostToolUse hook for quality checks in LAZY-DEV-FRAMEWORK.

Runs quality checks automatically after Write/Edit operations:
- Lint: Ruff/ESLint (if configured)
- Type: Mypy/TSC (if configured)
- Tests: Pytest/Jest (only if TDD required in project)

Note: Formatting is handled by separate post_tool_use_format.py hook
"""

import json
import logging
import os
import sys
import subprocess

# Configure logging to stderr with timestamp
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def check_tdd_required() -> bool:
    """Check if TDD is required in project."""
    check_files = ["README.md", "CLAUDE.md", ".github/workflows"]
    keywords = ["TDD", "test-driven", "pytest", "jest"]

    for file_path in check_files:
        if os.path.exists(file_path):
            try:
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if any(keyword in content for keyword in keywords):
                            return True
            except Exception:
                pass

    return False


def run_lint() -> tuple[bool, str]:
    """Run linting if configured."""
    # Check for Python (Ruff)
    if os.path.exists(".ruff.toml") or os.path.exists("pyproject.toml"):
        if os.path.exists("scripts/lint.py"):
            result = subprocess.run(
                ["python", "scripts/lint.py", "."], capture_output=True, text=True
            )
        else:
            result = subprocess.run(
                ["ruff", "check", "."], capture_output=True, text=True
            )

        if result.returncode != 0:
            return False, f"Ruff linting failed:\n{result.stdout}\n{result.stderr}"

    # Check for JavaScript (ESLint)
    if os.path.exists(".eslintrc.json") or os.path.exists(".eslintrc.js"):
        result = subprocess.run(["npx", "eslint", "."], capture_output=True, text=True)

        if result.returncode != 0:
            return False, f"ESLint failed:\n{result.stdout}\n{result.stderr}"

    return True, "Linting passed"


def run_type_check() -> tuple[bool, str]:
    """Run type checking if configured."""
    # Check for Python (Mypy)
    if os.path.exists("mypy.ini") or os.path.exists("pyproject.toml"):
        if os.path.exists("scripts/type_check.py"):
            result = subprocess.run(
                ["python", "scripts/type_check.py", "."], capture_output=True, text=True
            )
        else:
            result = subprocess.run(["mypy", "."], capture_output=True, text=True)

        if result.returncode != 0:
            return (
                False,
                f"Mypy type checking failed:\n{result.stdout}\n{result.stderr}",
            )

    # Check for TypeScript (tsc)
    if os.path.exists("tsconfig.json"):
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"], capture_output=True, text=True
        )

        if result.returncode != 0:
            return (
                False,
                f"TypeScript type checking failed:\n{result.stdout}\n{result.stderr}",
            )

    return True, "Type checking passed"


def run_tests() -> tuple[bool, str]:
    """Run tests only if TDD is required."""
    if not check_tdd_required():
        return True, "Tests skipped (TDD not required in project)"

    # Check for Python (Pytest)
    if os.path.exists("pytest.ini") or os.path.exists("tests/"):
        if os.path.exists("scripts/test_runner.py"):
            result = subprocess.run(
                ["python", "scripts/test_runner.py", "tests/"],
                capture_output=True,
                text=True,
            )
        else:
            result = subprocess.run(
                ["pytest", "tests/", "-v"], capture_output=True, text=True
            )

        if result.returncode != 0:
            return False, f"Pytest failed:\n{result.stdout}\n{result.stderr}"

    # Check for JavaScript (Jest/npm test)
    if os.path.exists("package.json"):
        result = subprocess.run(["npm", "test"], capture_output=True, text=True)

        if result.returncode != 0:
            return False, f"Tests failed:\n{result.stdout}\n{result.stderr}"

    return True, "Tests passed"


def main():
    """Hook entry point."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get("tool_name", "")

        # Only run quality checks after Write/Edit operations
        if tool_name not in ["Write", "Edit"]:
            print(
                json.dumps(
                    {"status": "skipped", "reason": "Not a Write/Edit operation"}
                )
            )
            sys.exit(0)

        results = {
            "lint": {"status": "skipped"},
            "type": {"status": "skipped"},
            "tests": {"status": "skipped"},
        }

        # Run lint
        lint_success, lint_msg = run_lint()
        results["lint"] = {
            "status": "pass" if lint_success else "fail",
            "message": lint_msg,
        }

        if not lint_success:
            print(json.dumps(results), file=sys.stderr)
            sys.exit(0)  # Don't block, just warn

        # Run type check
        type_success, type_msg = run_type_check()
        results["type"] = {
            "status": "pass" if type_success else "fail",
            "message": type_msg,
        }

        if not type_success:
            print(json.dumps(results), file=sys.stderr)
            sys.exit(0)  # Don't block, just warn

        # Run tests
        test_success, test_msg = run_tests()
        results["tests"] = {
            "status": "pass" if test_success else "fail",
            "message": test_msg,
        }

        if not test_success:
            print(json.dumps(results), file=sys.stderr)
            sys.exit(0)  # Don't block, just warn

        # All passed
        print(json.dumps(results))
        sys.exit(0)

    except Exception as e:
        # Don't block on hook errors
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
