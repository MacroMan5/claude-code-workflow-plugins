# Quality Pipeline Scripts

Cross-platform Python wrappers for code quality tools in LAZY-DEV-FRAMEWORK.

## Overview

These scripts enforce code quality through a mandatory sequential pipeline:

```
Format (Black + Ruff) → Lint (Ruff) → Type (Mypy) → Test (Pytest)
```

All scripts are:
- **Cross-platform**: Work on Windows, macOS, and Linux
- **Observable**: Log operations to `logs/<session-id>/`
- **Fail-fast**: Stop on first error with clear reporting
- **Idempotent**: Safe to run multiple times

## Scripts

### 1. format.py - Code Beautification

Format code using Black and Ruff format.

**Usage:**
```bash
python scripts/format.py <path> [--session SESSION_ID]
```

**Examples:**
```bash
# Format single file
python scripts/format.py src/auth.py

# Format directory
python scripts/format.py src/

# Format with session logging
python scripts/format.py src/ --session abc123
```

**Performance:** 2-5 seconds for typical modules

**Tools Used:**
- `black <path>` - Code formatting
- `ruff format <path>` - Additional formatting

**Log Output:** `logs/<session-id>/format.json`

---

### 2. lint.py - Code Quality Checking

Check code quality using Ruff with automatic fixes.

**Usage:**
```bash
python scripts/lint.py <path> [--session SESSION_ID]
```

**Examples:**
```bash
# Lint single file
python scripts/lint.py src/auth.py

# Lint directory with auto-fix
python scripts/lint.py src/

# Lint with session logging
python scripts/lint.py src/ --session abc123
```

**Performance:** 3-8 seconds with auto-fixes

**Tools Used:**
- `ruff check <path> --fix --output-format=json`

**Log Output:** `logs/<session-id>/lint.json`

---

### 3. type_check.py - Type Safety Verification

Verify type correctness using Mypy in strict mode.

**Usage:**
```bash
python scripts/type_check.py <path> [--session SESSION_ID]
```

**Examples:**
```bash
# Type check single file
python scripts/type_check.py src/auth.py

# Type check directory
python scripts/type_check.py src/

# Type check with session logging
python scripts/type_check.py src/ --session abc123
```

**Performance:** 5-15 seconds depending on project size

**Tools Used:**
- `mypy <path> --strict`

**Log Output:** `logs/<session-id>/type_check.json`

**Note:** Type errors require manual fixes (no auto-fix available)

---

### 4. test_runner.py - Test Execution

Run tests using Pytest with coverage reporting.

**Usage:**
```bash
python scripts/test_runner.py [path] [--session SESSION_ID]
```

**Examples:**
```bash
# Run all tests
python scripts/test_runner.py

# Run specific test directory
python scripts/test_runner.py tests/unit/

# Run with session logging
python scripts/test_runner.py tests/ --session abc123
```

**Performance:** 10-30 seconds for small test suites

**Tools Used:**
- `pytest <path> -v --cov=src --cov-report=term --cov-report=json`

**Log Output:** `logs/<session-id>/test_runner.json`

**Coverage Threshold:** 80% minimum (configurable in pyproject.toml)

---

### 5. gh_wrapper.py - GitHub Integration

Create GitHub issues and pull requests using gh CLI.

**Usage:**
```bash
python scripts/gh_wrapper.py create-issue --title "..." --body "..." [--labels "..."]
python scripts/gh_wrapper.py create-pr --title "..." --body "..." --base main [--labels "..."]
```

**Examples:**
```bash
# Create issue
python scripts/gh_wrapper.py create-issue \
  --title "Setup OAuth2" \
  --body "Implement OAuth2 authentication" \
  --labels "task,authentication"

# Create PR
python scripts/gh_wrapper.py create-pr \
  --title "[FEATURE] Add OAuth2" \
  --body "Implements OAuth2 with Google provider" \
  --base main \
  --labels "feature,reviewed"
```

**Prerequisites:**
- Install gh CLI: https://cli.github.com
- Authenticate: `gh auth login`
- Verify: `gh auth status`

**Tools Used:**
- `gh issue create --title "..." --body "..." --label "..."`
- `gh pr create --title "..." --body "..." --base "..." --label "..."`

---

## Quality Pipeline

Run the complete quality pipeline sequentially:

```bash
# Run all quality checks
python scripts/format.py src/ --session pipeline_123
python scripts/lint.py src/ --session pipeline_123
python scripts/type_check.py src/ --session pipeline_123
python scripts/test_runner.py tests/ --session pipeline_123
```

**Pipeline Behavior:**
- Each step must pass before proceeding
- Logs are collected under a single session ID
- Fail-fast: stops at first failure
- Exit code 0 = all passed, non-zero = failed

---

## Session Logging

All scripts support session-based logging for audit trails.

**Log Directory Structure:**
```
logs/
└── <session-id>/
    ├── format.json
    ├── lint.json
    ├── type_check.json
    └── test_runner.json
```

**Log Entry Format:**
```json
{
  "timestamp": "2025-01-20T15:30:45.123Z",
  "script": "format.py",
  "path": "src/auth.py",
  "session_id": "abc123",
  "status": "success",
  "duration_seconds": 3.45,
  "steps": [...]
}
```

**Benefits:**
- Audit trail for compliance
- Performance analysis
- Debugging failed runs
- Retrospective analysis

---

## Cross-Platform Compatibility

All scripts use `pathlib.Path` for cross-platform path handling:

**Good:**
```python
from pathlib import Path
path = Path("src") / "auth.py"
subprocess.run(["black", str(path)])
```

**Bad:**
```python
path = "src/auth.py"  # Only works on Unix
```

**Environment Variables:**
- `ANTHROPIC_API_KEY` - For AI-powered features
- `LOG_DIR` - Override log directory (default: `logs/`)

---

## Error Handling

All scripts follow these error handling patterns:

1. **Nonexistent Path:** Returns exit code 1 with clear error message
2. **Tool Failure:** Returns tool's exit code with stderr/stdout
3. **Permission Error:** Returns exit code 1 with permission error details
4. **Missing Tool:** Returns exit code 1 with installation instructions

**Example Error Output:**
```
❌ Path does not exist: /tmp/nonexistent.py
```

---

## Testing

Run script tests:

```bash
# Test all scripts
pytest tests/test_scripts/

# Test specific script
pytest tests/test_scripts/test_integration.py

# Test with coverage
pytest tests/test_scripts/ --cov=scripts
```

---

## Dependencies

Add to `pyproject.toml`:

```toml
[project]
dependencies = [
    "black>=24.0.0",
    "ruff>=0.2.0",
    "mypy>=1.8.0",
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
]
```

Install with:
```bash
pip install black ruff mypy pytest pytest-cov
# or
uv sync
```

---

## Performance Expectations

| Script | Small Project | Medium Project | Large Project |
|--------|---------------|----------------|---------------|
| format.py | 2-5s | 5-10s | 10-20s |
| lint.py | 3-8s | 8-15s | 15-30s |
| type_check.py | 5-15s | 15-30s | 30-60s |
| test_runner.py | 10-30s | 30-90s | 90-300s |

- **Small:** <1000 LOC, <100 tests
- **Medium:** 1000-10000 LOC, 100-1000 tests
- **Large:** >10000 LOC, >1000 tests

---

## Troubleshooting

### "Command not found: black"

Install formatting tools:
```bash
pip install black ruff
```

### "Command not found: mypy"

Install type checker:
```bash
pip install mypy
```

### "Command not found: pytest"

Install test runner:
```bash
pip install pytest pytest-cov
```

### "Command not found: gh"

Install GitHub CLI:
- **macOS:** `brew install gh`
- **Windows:** `winget install GitHub.cli`
- **Linux:** See https://cli.github.com

Then authenticate:
```bash
gh auth login
```

### Session logs not created

Ensure you have write permissions in the current directory:
```bash
ls -la logs/
```

If permission denied, run with appropriate permissions or change log directory.

---

## Integration with Commands

Scripts are called from LAZY-DEV commands:

```python
# In task-exec.md command
import subprocess

session_id = "task_exec_123"

# Format
result = subprocess.run([
    "python", "scripts/format.py", "src/", "--session", session_id
])
if result.returncode != 0:
    print("❌ Format failed")
    sys.exit(1)

# Lint
result = subprocess.run([
    "python", "scripts/lint.py", "src/", "--session", session_id
])
# ... continue pipeline
```

---

## Contributing

When adding new scripts:

1. Follow existing patterns (pathlib, type hints, docstrings)
2. Add comprehensive tests
3. Update this README
4. Ensure cross-platform compatibility
5. Add session logging support

---

## License

Part of LAZY-DEV-FRAMEWORK. See main project LICENSE.
