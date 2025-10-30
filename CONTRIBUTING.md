# Contributing to LAZY_DEV Framework

Thank you for your interest in contributing to the LAZY_DEV Framework! This document provides guidelines and instructions for contributing.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)

---

## Code of Conduct

This project adheres to a [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to etheroux5@gmail.com.

---

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs. **actual behavior**
- **Environment details** (OS, Python version, Claude Code version)
- **Relevant logs** from `.claude/data/logs/`

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Suggesting Enhancements

Enhancement suggestions are welcome! Please include:

- **Clear use case** - What problem does this solve?
- **Detailed description** of the proposed feature
- **Alternative solutions** you've considered
- **Examples** from other projects (if applicable)

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).

### Contributing Code

We welcome pull requests for:

- **Bug fixes**
- **New features** (discuss in an issue first)
- **Documentation improvements**
- **New agents** or **skills**
- **Quality improvements** (tests, type hints, etc.)

---

## Development Setup

### Prerequisites

1. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

2. **uv Package Manager**
   ```bash
   pip install uv
   ```

3. **Git**
   ```bash
   git --version
   ```

4. **Claude Code CLI**
   - Install from https://docs.claude.com/claude-code

### Clone and Install

```bash
# Fork the repository on GitHub first

# Clone your fork
git clone https://github.com/YOUR_USERNAME/claude-code-workflow-plugins.git
cd claude-code-workflow-plugins/LAZY_DEV

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install black ruff mypy pytest pytest-cov

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### Verify Installation

```bash
# Check Python tools
black --version
ruff --version
mypy --version
pytest --version

# Verify Claude Code commands
# (In Claude Code CLI)
/help
```

---

## Making Changes

### Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### Development Workflow

1. **Make your changes**
   - Follow [Style Guidelines](#style-guidelines)
   - Add/update tests as needed
   - Update documentation

2. **Run quality checks**
   ```bash
   # Format code
   black .
   ruff check --fix .

   # Type check
   mypy .claude/hooks/ --ignore-missing-imports

   # Run tests (if applicable)
   pytest tests/ -v
   ```

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   # Use conventional commits: feat:, fix:, docs:, refactor:, test:
   ```

---

## Submitting Changes

### Before Submitting

Ensure your PR:

- [ ] Passes all CI checks (lint, type check, tests)
- [ ] Includes tests for new functionality
- [ ] Updates relevant documentation
- [ ] Follows style guidelines
- [ ] Has descriptive commit messages
- [ ] References any related issues

### Create Pull Request

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub
   - Use the PR template
   - Link related issues
   - Provide clear description
   - Add screenshots/examples if applicable

3. **Respond to feedback**
   - Address review comments
   - Update your branch as needed
   - CI checks must pass before merge

### PR Review Process

1. Automated CI checks run on your PR
2. Maintainers review your code
3. You address any feedback
4. Once approved, a maintainer will merge

---

## Style Guidelines

### Python Code Style

We use **Black** for formatting and **Ruff** for linting:

```bash
# Format code
black .

# Lint code
ruff check .

# Fix linting issues automatically
ruff check --fix .
```

### Code Conventions

1. **Type Hints Required**
   ```python
   def process_task(task_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
       """Process a task with given options."""
       pass
   ```

2. **Docstrings Required (Google Style)**
   ```python
   def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
       """Execute command with provided arguments.

       Args:
           args: Command arguments dictionary containing task details

       Returns:
           Execution results with status and output

       Raises:
           ValueError: If required arguments are missing
       """
       pass
   ```

3. **Error Handling**
   ```python
   try:
       result = risky_operation()
   except SpecificError as e:
       logger.error(f"Operation failed: {e}")
       return {"status": "error", "message": str(e)}
   ```

4. **Cross-Platform Compatibility**
   ```python
   from pathlib import Path

   # Good: Works on all platforms
   path = Path(file_path)

   # Bad: Only works on Unix
   path = f"{file_path}".replace("\\", "/")
   ```

### Markdown Files

- Use **ATX-style headers** (`# Header`)
- Include **table of contents** for long documents
- Use **code fences** with language specifiers
- Keep lines under 120 characters when possible

### Agent and Command Files

**Agent Format** (`.claude/agents/*.md`):
```yaml
---
name: agent-name
description: Clear, action-oriented description. Use when [context].
tools: Read, Write, Edit, Grep, Glob, Bash
model: sonnet
---

You are the [Role] Agent for LAZY-DEV-FRAMEWORK.

When invoked:
1. [Step 1]
2. [Step 2]

Output Format:
[Expected deliverables]
```

**Command Format** (`.claude/commands/*.md`):
```markdown
# Command Name

## When to Use
[Clear usage criteria]

## Requirements
[Prerequisites]

## Execution
[Step-by-step process]

## Validation
[Success criteria]

## Examples
[Usage examples]
```

---

## Testing Guidelines

### Writing Tests

```python
import pytest
from pathlib import Path

def test_feature_basic():
    """Test basic feature functionality."""
    # Arrange
    input_data = {"key": "value"}

    # Act
    result = process_feature(input_data)

    # Assert
    assert result["status"] == "success"
    assert "output" in result
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=.claude --cov-report=html

# Run specific test
pytest tests/test_hooks.py::test_user_prompt_submit -v
```

### Test Coverage

- Aim for **80% coverage** minimum
- Test edge cases and error conditions
- Mock external dependencies (API calls, file I/O)

---

## Documentation Guidelines

### What to Document

- **New features** - Add to README.md, CHANGELOG.md
- **New commands** - Create command file, update README.md
- **New agents** - Create agent file, update SUB_AGENTS.md
- **New skills** - Add skill directory, update skills README
- **Breaking changes** - Document in CHANGELOG.md

### Documentation Structure

```
LAZY_DEV/
├── README.md              # Main documentation
├── INSTALLATION.md        # Setup guide
├── WORKFLOW.md            # Workflow details
├── MEMORY.md              # Memory system
├── SUB_AGENTS.md          # Agent specifications
├── CLAUDE.md              # Framework guide
└── CHANGELOG.md           # Version history
```

### Changelog Format

Follow [Keep a Changelog](https://keepachangelog.com/):

```markdown
## [2.1.0] - 2025-10-31

### Added
- New feature description

### Changed
- Modified feature description

### Fixed
- Bug fix description

### Deprecated
- Deprecated feature description
```

---

## Common Tasks

### Adding a New Command

1. Create `.claude/commands/my-command.md`
2. Follow command format (see Style Guidelines)
3. Update README.md command list
4. Add tests (if applicable)
5. Update CHANGELOG.md

### Adding a New Agent

1. Create `.claude/agents/my-agent.md`
2. Use YAML frontmatter + Markdown prompt
3. Update SUB_AGENTS.md agent registry
4. Test agent invocation
5. Update CHANGELOG.md

### Adding a New Skill

1. Create `.claude/skills/my-skill/` directory
2. Add `skill.md` with skill definition
3. Add examples in `examples/` subdirectory
4. Update `.claude/skills/README.md`
5. Update CHANGELOG.md

### Fixing a Bug

1. Create issue if one doesn't exist
2. Write test that reproduces the bug
3. Fix the bug
4. Verify test passes
5. Update CHANGELOG.md

---

## Questions?

- **General questions** - Open a [Discussion](https://github.com/MacroMan5/claude-code-workflow-plugins/discussions)
- **Bug reports** - Open an [Issue](https://github.com/MacroMan5/claude-code-workflow-plugins/issues)
- **Security issues** - Email etheroux5@gmail.com (see [SECURITY.md](./SECURITY.md))

---

## Recognition

Contributors are recognized in:
- GitHub contributors page
- CHANGELOG.md for significant contributions
- CREDITS.md for major architectural contributions

Thank you for contributing to LAZY_DEV Framework! 🚀

---

**Repository**: https://github.com/MacroMan5/claude-code-workflow-plugins
**License**: MIT
**Maintainer**: MacroMan5 (Therouxe)
