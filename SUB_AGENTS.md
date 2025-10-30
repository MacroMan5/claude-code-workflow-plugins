# LAZY_DEV Framework - Sub-Agent Definitions

Central registry of all sub-agents with their input/output formats, variable names, and invocation patterns.

**Version**: 1.0.0
**Last Updated**: 2025-10-29
**Purpose**: Single source of truth for all sub-agent specifications

---

## Overview

All sub-agents are invoked via Claude Code's Task tool with `subagent_type="general-purpose"`. Each agent is defined in a markdown file in `.claude/agents/` with parametric variables using `$variable` syntax.

**Variable Substitution Pattern**:
```python
from string import Template
from pathlib import Path

# Load template
template_text = Path(".claude/agents/agent-name.md").read_text()

# Substitute variables
prompt = Template(template_text).substitute({
    "variable1": "value1",
    "variable2": "value2"
})

# Invoke via Task tool
# Task(subagent_type="general-purpose", prompt=prompt)
```

**Key Principles**:
- Use `Template.substitute()` for required variables (raises KeyError if missing)
- Use `Template.safe_substitute()` for optional variables (leaves $var unchanged if missing)
- Always validate variable values before substitution
- Document all variables with types and examples

---

## Table of Contents

1. [Project-Manager Agent](#1-project-manager-agent)
2. [Task-Enhancer Agent](#2-task-enhancer-agent)
3. [Coder Agent](#3-coder-agent)
4. [Reviewer Agent](#4-reviewer-agent)
5. [Reviewer-Story Agent](#5-reviewer-story-agent)
6. [Tester Agent](#6-tester-agent)
7. [Research Agent](#7-research-agent)
8. [Documentation Agent](#8-documentation-agent)
9. [Refactor Agent](#9-refactor-agent)
10. [Cleanup Agent](#10-cleanup-agent)

---

## 1. Project-Manager Agent

**Purpose**: Create comprehensive USER-STORY and individual TASK files from feature briefs.

**Location**: `.claude/agents/project-manager.md`

**Model**: Sonnet (requires complex reasoning for task breakdown)

**Tools**: Read, Write, Grep, Glob

### Input Variables

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `$role` | string | Yes | Target developer role | "full-stack developer" |
| `$description` | string | Yes | Feature brief (enriched by pre-prompt hook) | "Add OAuth2 authentication with Google provider" |
| `$constraints` | string | Yes | Technical constraints and requirements | "Python 3.11+, FastAPI, PostgreSQL, JWT tokens" |
| `$project_context` | string | No | Additional project context | "Existing auth system uses JWT, new OAuth should integrate with it" |

### Output Format

**Files Created**:
1. `USER-STORY.md` - Comprehensive user story with:
   - Story ID (format: `US-YYYYMMDD-XXX`)
   - Description and acceptance criteria
   - Security considerations checklist
   - Testing requirements (unit, integration, edge cases)
   - Technical dependencies
   - Architecture impact
   - Definition of done

2. Multiple `TASK-*.md` files (one per task):
   - Task ID (format: `TASK-[StoryID]-[Number]`)
   - Description and acceptance criteria
   - Effort estimate (S/M/L)
   - Dependencies (blocked by, blocks)
   - Files to create/modify
   - Security checklist
   - Testing checklist
   - Quality gates

### Example Invocation

```python
from string import Template
from pathlib import Path

# Load template
template = Path(".claude/agents/project-manager.md").read_text()

# Substitute variables
prompt = Template(template).substitute(
    role="full-stack developer",
    description=enriched_user_input,  # Already enriched by pre-prompt hook
    constraints="Python 3.11+, FastAPI, PostgreSQL, pytest",
    project_context="Existing auth system uses JWT tokens"
)

# Invoke via Task tool
# Task invocation would happen here with the substituted prompt
```

### Success Criteria

- USER-STORY.md exists with complete story structure
- Multiple TASK-*.md files created (one per atomic task)
- All acceptance criteria covered by tasks
- Dependencies clearly mapped
- Security and testing checklists comprehensive
- Each task is independently implementable

### Notes

- Creates separate files for each task (NOT a single TASKS.md)
- Tasks should be 2-4 hours each (atomic and testable)
- Story ID format: US-YYYYMMDD-XXX (e.g., US-20251026-001)
- Task ID format: TASK-[StoryID]-[Number] (e.g., TASK-US-20251026-001-1)
- File naming: TASK-US-YYYYMMDD-XXX-N.md

---

## 2. Task-Enhancer Agent

**Purpose**: Enhance task files with technical context by researching the codebase.

**Location**: `.claude/agents/task-enhancer.md`

**Model**: Sonnet (requires deep codebase analysis)

**Tools**: Read, Write, Edit, Grep, Glob

### Input Variables

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `$tasks_dir` | string | Yes | Directory containing TASK-*.md files | "./project-management/US-STORY/US-3.4-oauth2/TASKS" |
| `$story_file` | string | Yes | Path to US-story.md | "./project-management/US-STORY/US-3.4-oauth2/US-story.md" |
| `$project_root` | string | Yes | Root directory of project | "." |
| `$codebase_focus` | string | No | Specific directories to focus on | "src/auth" (default: "*") |

### Output Format

**Files Modified**: Each TASK-*.md file in `$tasks_dir` gets enhanced with:

```markdown
---

## Technical Context (Added by Task Enhancer)

### Overview
[2-3 sentence summary of how this task fits into codebase architecture]

### Relevant Files to Reference
- `path/to/similar_feature.py` - [What to learn from this]
- `path/to/base_class.py` - [Base class to inherit from]

### Files to Create/Modify
**New Files:**
- `src/features/new_feature.py` - [Main implementation]

**Files to Modify:**
- `src/main.py:45` - [Add import and initialization]

### Code Patterns from Codebase
[10-30 line code snippets with file paths]

### Dependencies
- `requests==2.31.0` - HTTP client (already in requirements.txt)
- `NEW: pytest-mock==3.12.0` - Mocking for tests (ADD)

### Architecture Integration
[Component relationship diagram]

### Testing Strategy
[Existing test patterns to follow]

### Security Considerations
[Codebase-specific security patterns]

### Implementation Tips
- Do's and Don'ts
- Common gotchas
```

### Example Invocation

```python
from string import Template
from pathlib import Path

template = Path(".claude/agents/task-enhancer.md").read_text()

prompt = Template(template).substitute(
    tasks_dir="./project-management/US-STORY/US-3.4-oauth2/TASKS",
    story_file="./project-management/US-STORY/US-3.4-oauth2/US-story.md",
    project_root=".",
    codebase_focus="src/auth"  # Optional
)

# Invoke via Task tool
```

### Success Criteria

- Each task has actionable technical context
- At least 3 relevant files identified per task
- At least 2 code pattern examples with file paths
- Specific files to create/modify with line numbers
- Dependencies clearly listed (existing + new)
- Architecture integration clear
- Testing strategy aligned with project conventions

### Notes

- Runs AFTER project-manager creates initial tasks
- Reads codebase extensively but only writes/edits task files
- Provides concrete, actionable information (not vague suggestions)
- Code examples should be 10-30 lines (copy-pasteable)
- Handles edge cases: new projects, legacy codebases, microservices

---

## 3. Coder Agent

**Purpose**: Implement coding tasks with clean, tested, type-hinted code.

**Location**: `.claude/agents/coder.md`

**Model**: Sonnet (requires complex implementation logic)

**Tools**: Read, Write, Edit, Bash, Grep, Glob

### Input Variables

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `$task` | string | Yes | Task description and requirements | "Implement Google OAuth2 provider inheriting from OAuthProvider base class" |
| `$research` | string | No | Research context from research agent | "Google OAuth endpoints: authorization URL, token URL, user info URL" (default: "No research provided") |
| `$acceptance_criteria` | string | Yes | Acceptance criteria from task file | "- [ ] Implements OAuthProvider interface\n- [ ] Handles errors\n- [ ] 80% test coverage" |

### Output Format

**Files Created/Modified**:
1. Implementation file(s) with:
   - Type hints on all functions (Python 3.11+)
   - Google-style docstrings (Args, Returns, Raises, Examples)
   - Comprehensive error handling
   - Input validation
   - Security best practices

2. Test file(s) with:
   - `test_` prefix
   - Unit tests for all functions
   - Integration tests for workflows
   - Edge case coverage (null, empty, boundary)
   - Mocked external dependencies
   - Minimum 80% coverage

3. Updated documentation (if applicable)

### Example Invocation

```python
from string import Template
from pathlib import Path

template = Path(".claude/agents/coder.md").read_text()

# With research context
prompt = Template(template).substitute(
    task="Implement Google OAuth2 provider",
    research="Google OAuth endpoints: https://accounts.google.com/o/oauth2/v2/auth for authorization",
    acceptance_criteria="- [ ] Implements OAuthProvider interface\n- [ ] Returns access token"
)

# Without research (optional variable)
prompt = Template(template).safe_substitute(
    task="Implement Google OAuth2 provider",
    acceptance_criteria="- [ ] Implements OAuthProvider interface"
    # research will remain as "$research" or be omitted
)
```

### Success Criteria

- All acceptance criteria met
- Code is clean, readable, and well-structured
- Type hints on all functions
- Comprehensive docstrings (Google style)
- Error handling with specific exceptions
- Security best practices followed (OWASP Top 10)
- Tests written with >= 80% coverage
- Tests pass (pytest succeeds)

### Code Quality Requirements

```python
# Example of expected code quality
from typing import Optional

def authenticate_user(username: str, password: str) -> Optional[str]:
    """
    Authenticate user and return JWT token.

    Args:
        username: User's username
        password: User's password (will be hashed)

    Returns:
        JWT token if auth succeeds, None otherwise

    Raises:
        ValueError: If username or password empty

    Examples:
        >>> authenticate_user("user", "pass123")
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    """
    if not username or not password:
        raise ValueError("Username and password required")

    # Implementation...
```

### Testing Requirements

```python
# Example test structure
import pytest
from module import function_to_test

def test_function_success():
    """Test successful execution."""
    result = function_to_test("valid input")
    assert result is not None

def test_function_empty_input():
    """Test with empty input."""
    with pytest.raises(ValueError):
        function_to_test("")
```

### Notes

- Python 3.11+ type hints required
- Google-style docstrings mandatory
- Security is paramount (input validation, no secrets in code)
- Tests should follow Arrange-Act-Assert pattern
- Mock external dependencies (APIs, databases)

---

## 4. Reviewer Agent

**Purpose**: Review code implementation for quality, security, and testing.

**Location**: `.claude/agents/reviewer.md`

**Model**: Sonnet (requires deep code analysis)

**Tools**: Read, Grep, Glob, Bash (git diff, git log)

### Input Variables

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `$code` | string | Yes | Code to review (file paths or diffs) | "src/auth/google_provider.py\ntests/test_google_provider.py" |
| `$criteria` | string | Yes | Acceptance criteria to verify | "- [ ] Implements OAuthProvider\n- [ ] Handles errors" |
| `$standards` | string | No | Coding standards to enforce | "PEP 8, Type hints, 80% coverage" (default: standard) |

### Output Format

**JSON Response**:
```json
{
  "status": "APPROVED" | "REQUEST_CHANGES",
  "issues": [
    {
      "severity": "CRITICAL" | "WARNING" | "SUGGESTION",
      "file": "path/to/file.py",
      "line": 42,
      "description": "What's wrong",
      "fix": "How to fix it"
    }
  ],
  "summary": "Overall assessment"
}
```

### Example Invocation

```python
from string import Template
from pathlib import Path

template = Path(".claude/agents/reviewer.md").read_text()

prompt = Template(template).safe_substitute(
    code="src/auth/google_provider.py\ntests/test_google_provider.py",
    criteria="- [ ] Implements OAuthProvider interface\n- [ ] Handles token exchange errors\n- [ ] 80% test coverage",
    standards="PEP 8, Type hints, Google docstrings, 80% coverage"
)
```

### Review Checklist

**Code Quality**:
- Type hints on all functions
- Docstrings complete (Google style)
- Clean, readable code (no complex nesting)
- No code smells (duplication, long functions)
- Proper naming (descriptive, consistent)

**Security**:
- Input validation implemented
- No hardcoded secrets
- Error handling doesn't leak sensitive info
- OWASP Top 10 compliance

**Testing**:
- Unit tests present
- Tests pass
- Edge cases covered
- Good coverage (>= 80%)

**Functionality**:
- Meets all acceptance criteria
- Handles edge cases
- Performance acceptable
- No regressions

**Documentation**:
- Docstrings updated
- README updated if needed
- API changes documented

### Decision Criteria

- **APPROVED**: No critical issues, warnings are minor
- **REQUEST_CHANGES**: Critical issues OR multiple warnings

### Notes

- Reviews at task level (individual implementation)
- Focuses on code quality and security
- Returns structured JSON for automated processing
- Used in quality pipeline before commit

---

## 5. Reviewer-Story Agent

**Purpose**: Review all tasks in a story together for cohesion and completeness before PR creation.

**Location**: `.claude/agents/reviewer-story.md`

**Model**: Sonnet (requires holistic analysis)

**Tools**: Read, Grep, Glob, Bash

### Input Variables

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `$story_id` | string | Yes | Story identifier | "US-3.4" or "US-20251026-001" |
| `$story_file` | string | Yes | Path to US-story.md | "./project-management/US-STORY/US-3.4-oauth2/US-story.md" |
| `$tasks_dir` | string | Yes | Directory containing completed tasks | "./project-management/US-STORY/US-3.4-oauth2/TASKS" |
| `$branch_name` | string | Yes | Git branch name | "feat/US-3.4-oauth2-authentication" |
| `$standards` | string | No | Coding standards | "PEP 8, Type hints, 80% coverage, Google docstrings" |

### Output Format

**JSON Response**:
```json
{
  "status": "APPROVED" | "REQUEST_CHANGES",
  "issues": [
    {
      "severity": "CRITICAL" | "WARNING" | "SUGGESTION",
      "task_id": "TASK-1.1",
      "file": "path/to/file.py",
      "line": 42,
      "description": "Clear description of what's wrong",
      "fix": "Specific guidance on how to fix it"
    }
  ],
  "summary": "Overall assessment of entire story",
  "tasks_reviewed": ["TASK-1.1", "TASK-1.2", "TASK-1.3"],
  "report_path": "US-3.4_REPORT.md"
}
```

**If REQUEST_CHANGES**: Creates detailed report file `US-{story_id}_REPORT.md` with:
- Executive summary
- Acceptance criteria status (checklist)
- Tasks reviewed (status per task)
- Critical issues (MUST FIX)
- Warnings (SHOULD FIX)
- Suggestions (CONSIDER)
- Integration analysis
- Test results
- Documentation review
- Security review
- Recommendations

### Example Invocation

```python
from string import Template
from pathlib import Path

template = Path(".claude/agents/reviewer-story.md").read_text()

prompt = Template(template).safe_substitute(
    story_id="US-3.4",
    story_file="./project-management/US-STORY/US-3.4-oauth2/US-story.md",
    tasks_dir="./project-management/US-STORY/US-3.4-oauth2/TASKS",
    branch_name="feat/US-3.4-oauth2-authentication",
    standards="PEP 8, Type hints, 80% coverage, Google docstrings"
)
```

### Review Responsibilities

**Story Completeness**:
- All acceptance criteria from US-story.md met
- All tasks completed
- No missing functionality

**Code Quality**:
- Consistent code style across tasks
- No code duplication between tasks
- Proper error handling throughout
- Type hints consistent

**Integration**:
- All tasks work together cohesively
- No conflicts between task implementations
- Data flows correctly between components
- Consistent patterns

**Testing**:
- All tests pass
- Test coverage adequate
- Edge cases covered
- Integration tests for multi-task features

**Documentation**:
- Public APIs documented
- README updated
- Complex logic has comments
- Migration guides if needed

**Security**:
- Input validation throughout
- No SQL injection vulnerabilities
- No XSS vulnerabilities
- Sensitive data properly handled

### Decision Criteria

**APPROVED**:
- All checklist items pass
- All tests pass
- No CRITICAL issues
- At most minor SUGGESTIONS

**REQUEST_CHANGES**:
- Any CRITICAL issues
- Any tests fail
- Multiple WARNING issues
- Integration problems
- Missing acceptance criteria

### Notes

- Reviews at STORY level (all tasks together)
- Focuses on integration and cohesion
- Creates detailed report if requesting changes
- Used by `/lazy story-review` command
- Report format enables automated fix workflow

---

## 6. Tester Agent

**Purpose**: Generate comprehensive test suites with edge cases.

**Location**: `.claude/agents/tester.md`

**Model**: Haiku (testing is well-defined, doesn't require complex reasoning)

**Tools**: Read, Write, Bash (pytest, coverage)

### Input Variables

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `$code` | string | Yes | Code to test (file paths) | "src/auth/google_provider.py" |
| `$coverage_target` | number | Yes | Minimum coverage percentage | 80 |

### Output Format

**Files Created**: Test files with:
- `tests/test_*.py` naming convention
- pytest framework usage
- Mocked external dependencies
- Clear, descriptive test names
- Arrange-Act-Assert pattern
- Coverage >= `$coverage_target%`

**Test Structure**:
```python
import pytest
from unittest.mock import Mock, patch
from module import function_to_test

class TestFunctionName:
    """Tests for function_to_test."""

    def test_success_case(self):
        """Test successful execution."""
        # Arrange
        input_data = "valid input"

        # Act
        result = function_to_test(input_data)

        # Assert
        assert result == expected_output

    def test_empty_input(self):
        """Test with empty input."""
        with pytest.raises(ValueError):
            function_to_test("")

    def test_null_input(self):
        """Test with None input."""
        with pytest.raises(TypeError):
            function_to_test(None)

    @patch('module.external_api')
    def test_with_mocked_dependency(self, mock_api):
        """Test with mocked external API."""
        mock_api.return_value = {"status": "ok"}
        result = function_to_test("input")
        assert result is not None
```

### Example Invocation

```python
from string import Template
from pathlib import Path

template = Path(".claude/agents/tester.md").read_text()

prompt = Template(template).substitute(
    code="src/auth/google_provider.py",
    coverage_target=80
)
```

### Test Requirements

**Coverage**:
- Unit tests for all functions
- Integration tests for workflows
- Edge cases: null, empty, boundary values
- Error handling: exceptions, invalid inputs

**Edge Cases to Cover**:
- Null/None inputs
- Empty strings/lists/dicts
- Boundary values (0, -1, MAX_INT)
- Invalid types
- Concurrent access (if applicable)
- Resource exhaustion

### Success Criteria

- Test files created in `tests/` directory
- Test naming follows `test_*` convention
- All tests use pytest framework
- External dependencies are mocked
- Coverage meets or exceeds `$coverage_target%`
- Tests follow Arrange-Act-Assert pattern
- Test names are clear and descriptive

### Notes

- Uses Haiku model (cost-efficient for well-defined task)
- Follows pytest conventions
- Mocks external dependencies (APIs, databases)
- Tests should be maintainable and clear
- Used by coder agent and in quality pipeline

---

## 7. Research Agent

**Purpose**: Research documentation and best practices for technologies.

**Location**: `.claude/agents/research.md`

**Model**: Haiku (research is retrieval-focused, doesn't require complex reasoning)

**Tools**: Read, WebSearch, WebFetch

### Input Variables

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `$keywords` | string | Yes | Research keywords/topics | "Google OAuth2 API Python implementation" |
| `$depth` | string | Yes | Research depth level | "quick" or "comprehensive" |

### Output Format

**Markdown Research Document**:
```markdown
# Research: $keywords

## Official Documentation
- Source: [URL]
- Version: [Version number]
- Last updated: [Date]

## Key Points
- Point 1
- Point 2

## API Reference
### Class/Function Name
- Purpose: ...
- Parameters: ...
- Returns: ...
- Example:
```code
...
```

## Best Practices
1. Practice 1
2. Practice 2

## Common Pitfalls
- Pitfall 1: Description and how to avoid
- Pitfall 2: Description and how to avoid

## Code Examples
```code
# Example 1: Basic usage
...

# Example 2: Advanced usage
...
```

## Recommendations
Based on research, recommend:
- Approach A vs Approach B
- Libraries to use
- Patterns to follow
```

### Example Invocation

```python
from string import Template
from pathlib import Path

template = Path(".claude/agents/research.md").read_text()

# Quick research
prompt = Template(template).substitute(
    keywords="Google OAuth2 API Python",
    depth="quick"
)

# Comprehensive research
prompt = Template(template).substitute(
    keywords="FastAPI OAuth2 implementation best practices",
    depth="comprehensive"
)
```

### Research Depth Levels

**Quick Research** (`depth="quick"`):
- Official documentation only
- Key APIs/methods
- Basic usage examples
- Common gotchas

**Comprehensive Research** (`depth="comprehensive"`):
- Official documentation
- Community best practices
- Multiple code examples
- Common pitfalls
- Performance considerations
- Security implications
- Alternative approaches

### Success Criteria

- Official documentation sourced and cited
- Key APIs/methods documented with examples
- Best practices clearly listed
- Common pitfalls identified with solutions
- Code examples provided (basic and advanced)
- Recommendations made based on findings

### Notes

- Uses Haiku model (cost-efficient for research)
- WebSearch and WebFetch tools for documentation
- Provides concrete, actionable research
- Used by coder agent when implementing unfamiliar technologies
- Research is passed to coder via `$research` variable

---

## 8. Documentation Agent

**Purpose**: Generate or update documentation, docstrings, and README files.

**Location**: `.claude/agents/documentation.md`

**Model**: Haiku (documentation generation is well-defined)

**Tools**: Read, Write, Grep, Glob

### Input Variables

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `$scope` | string | Yes | What to document | "src/auth/google_provider.py" or "codebase" |
| `$format` | string | Yes | Documentation format | "docstrings", "readme", "api", "security", "setup" |
| `$target` | string | No | Target directory for docs | "docs/" (default: "docs/") |

### Output Format

**Depends on `$format`**:

#### Format: docstrings
Adds/updates Google-style docstrings in code:
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Longer description if needed. Explain what the function does,
    not how it does it.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer

    Examples:
        >>> function_name("test", 42)
        True
    """
```

#### Format: readme
Generates comprehensive README.md:
```markdown
# Project Name

Brief description

## Features
- Feature 1
- Feature 2

## Installation
```bash
pip install package-name
```

## Quick Start
[Usage examples]

## API Reference
[Link to API docs]
```

#### Format: api
Generates API reference documentation:
```markdown
# API Reference

## Module: module_name

### Class: ClassName

#### Methods

##### `method_name(param1: str) -> bool`

[Description, parameters, returns, raises, examples]
```

#### Format: security
Generates security documentation:
```markdown
# Security Considerations

## Authentication
[How authentication works]

## Input Validation
[Validation rules]

## Common Vulnerabilities
[How prevented]
```

#### Format: setup
Generates setup/installation guide:
```markdown
# Setup Guide

## Prerequisites
[Requirements]

## Installation
[Step-by-step]

## Configuration
[Environment variables]

## Troubleshooting
[Common issues]
```

### Example Invocation

```python
from string import Template
from pathlib import Path

template = Path(".claude/agents/documentation.md").read_text()

# Document with docstrings
prompt = Template(template).safe_substitute(
    scope="src/auth/google_provider.py",
    format="docstrings",
    target="docs/"
)

# Generate README
prompt = Template(template).safe_substitute(
    scope="codebase",
    format="readme",
    target="."
)

# Generate API docs
prompt = Template(template).safe_substitute(
    scope="src/auth",
    format="api",
    target="docs/api"
)
```

### Success Criteria

- Documentation generated in correct format
- All public APIs documented
- Examples provided where applicable
- Clear, concise language
- Proper markdown formatting
- Files created in `$target` directory

### Notes

- Uses Haiku model (cost-efficient)
- Google-style docstrings for Python
- Markdown format for all docs
- Used by `/lazy documentation` command
- Can update existing docs or create new ones

---

## 9. Refactor Agent

**Purpose**: Simplify code while preserving functionality.

**Location**: `.claude/agents/refactor.md`

**Model**: Sonnet (requires complex code analysis)

**Tools**: Read, Edit

### Input Variables

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `$code` | string | Yes | Code to refactor (file paths) | "src/auth/legacy_auth.py" |
| `$complexity_threshold` | number | No | Max cyclomatic complexity | 10 (default: 10) |

### Output Format

**Refactored Code** with:
1. Reduced cyclomatic complexity (≤ `$complexity_threshold`)
2. Extracted functions for complex logic
3. Removed code duplication (DRY principle)
4. Improved naming (clarity over brevity)
5. Added type hints (if missing)
6. Improved error handling

**Plus**:
- Explanation of changes
- Verification that tests still pass
- Backward compatibility preserved

### Example Invocation

```python
from string import Template
from pathlib import Path

template = Path(".claude/agents/refactor.md").read_text()

prompt = Template(template).safe_substitute(
    code="src/auth/legacy_auth.py",
    complexity_threshold=10
)
```

### Refactoring Goals

**Reduce Complexity**:
- Cyclomatic complexity ≤ `$complexity_threshold`
- Extract functions for complex logic
- Simplify conditional logic

**Remove Duplication**:
- DRY principle (Don't Repeat Yourself)
- Extract common logic
- Create reusable utilities

**Improve Naming**:
- Descriptive variable/function names
- Clear intent (clarity over brevity)

**Add Type Hints**:
- Type hints on all functions
- Type hints for complex data structures

**Improve Error Handling**:
- Specific exceptions
- Proper error messages
- Error recovery patterns

### Constraints

- **DO NOT change functionality** - behavior must be identical
- **Maintain all tests** - tests must still pass
- **Preserve public APIs** - no breaking changes
- **Keep backward compatibility** - existing callers unaffected

### Refactoring Patterns

**Extract Function**:
```python
# Before: Complex function
def process_data(data):
    # 50 lines of logic...

# After: Extracted helper functions
def process_data(data):
    validated = _validate_data(data)
    transformed = _transform_data(validated)
    return _save_data(transformed)
```

**Remove Duplication**:
```python
# Before: Duplicated code in save_user and save_product

# After: Extracted common logic
def save_user(user):
    _execute_insert("users", user)

def _execute_insert(table, data):
    with get_db_connection() as conn:
        # Common insert logic
```

### Success Criteria

- Cyclomatic complexity reduced to ≤ threshold
- Code duplication eliminated
- All tests still pass
- No breaking changes
- Backward compatibility maintained
- Code is more readable and maintainable

### Notes

- Uses Sonnet model (requires complex analysis)
- Preserves functionality (no behavior changes)
- All tests must pass after refactoring
- Used by `/lazy story-fix-review` for architecture issues

---

## 10. Cleanup Agent

**Purpose**: Remove dead code, unused imports, and temporary files.

**Location**: `.claude/agents/cleanup.md`

**Model**: Haiku (cleanup is pattern-matching, doesn't require complex reasoning)

**Tools**: Read, Edit, Bash (git rm), Grep, Glob

### Input Variables

| Variable | Type | Required | Description | Example |
|----------|------|----------|-------------|---------|
| `$paths` | string | Yes | Paths to clean | "src/" or "src/auth src/utils" |
| `$safe_mode` | string | Yes | Enable safe mode | "true" or "false" |

### Output Format

**Cleanup Report**:
```markdown
# Cleanup Report

## Unused Imports Removed
- `file.py`: removed `import unused_module`

## Dead Code Removed
- `utils.py`: removed function `old_helper()` (0 references)

## Commented Code Removed
- `service.py`: lines 45-60 (commented out debug code)

## Temp Files Deleted
- `__pycache__/` (entire directory)
- `*.pyc` (15 files)

## Impact Analysis
- Total lines removed: 234
- Files modified: 8
- Files deleted: 0
- Estimated disk space freed: 45 KB

## Safety Check
✓ All tests still pass
✓ No breaking changes detected
```

### Example Invocation

```python
from string import Template
from pathlib import Path

template = Path(".claude/agents/cleanup.md").read_text()

# Safe mode (dry run)
prompt = Template(template).substitute(
    paths="src/auth src/utils",
    safe_mode="true"
)

# Execute cleanup
prompt = Template(template).substitute(
    paths="src/",
    safe_mode="false"
)
```

### Safe Mode Behavior

**Safe Mode = "true"** (Dry Run):
- Report changes only
- Do NOT delete files
- List candidates for deletion
- Show impact analysis

**Safe Mode = "false"** (Execute):
- Execute cleanup
- Delete dead code
- Remove unused files
- Create git commit with changes

### Cleanup Tasks

**Unused Imports**:
- Identify imports not referenced in file
- Remove import statements

**Dead Code**:
- Identify functions with 0 references
- Identify classes with 0 references
- Remove unreferenced code

**Commented Code**:
- Remove commented-out code
- Keep TODO comments
- Keep documentation comments

**Temp Files**:
- Remove `__pycache__/` directories
- Remove `*.pyc` files
- Remove `.pytest_cache/`
- Remove other temp files

### Success Criteria

- Unused imports removed
- Dead code identified and removed (or reported)
- Commented code removed
- Temp files deleted
- Impact analysis provided
- All tests still pass after cleanup

### Notes

- Uses Haiku model (cost-efficient)
- Safe mode recommended for first run
- Always verify tests pass after cleanup
- Used by `/lazy cleanup` command
- Creates git commit if `safe_mode="false"`

---

## Variable Substitution Best Practices

### Required vs Optional Variables

**Use `Template.substitute()` for required variables**:
```python
from string import Template

template = Template("$required_var")
try:
    result = template.substitute(required_var="value")
except KeyError as e:
    print(f"Missing required variable: {e}")
```

**Use `Template.safe_substitute()` for optional variables**:
```python
from string import Template

template = Template("$optional_var or default")
result = template.safe_substitute(optional_var="value")
# If optional_var not provided, "$optional_var" remains in string
```

### Default Values in Templates

Use `${variable:-default}` syntax in agent templates:
```markdown
## Research Context
${research:-No research provided}
```

This allows safe_substitute to work without the variable.

### Validation Before Substitution

Always validate variable values:
```python
def validate_story_id(story_id: str) -> str:
    """Validate story ID format."""
    if not re.match(r'^US-\d{8}-\d{3}$', story_id):
        raise ValueError(f"Invalid story ID format: {story_id}")
    return story_id

story_id = validate_story_id(user_input)
prompt = Template(template).substitute(story_id=story_id)
```

### Multi-line Variables

Use triple-quoted strings for multi-line variables:
```python
acceptance_criteria = """
- [ ] Implements OAuth2 provider
- [ ] Handles token exchange
- [ ] Validates state parameter
- [ ] 80% test coverage
"""

prompt = Template(template).substitute(
    task="Implement OAuth2",
    acceptance_criteria=acceptance_criteria
)
```

---

## Common Invocation Patterns

### Pattern 1: Sequential Agent Pipeline

```python
# Step 1: Project-Manager creates story and tasks
pm_prompt = Template(pm_template).substitute(
    role="developer",
    description=enriched_brief,
    constraints="Python 3.11+",
    project_context=""
)
# Invoke PM agent -> creates USER-STORY.md and TASK-*.md files

# Step 2: Task-Enhancer adds technical context
te_prompt = Template(te_template).substitute(
    tasks_dir="./project-management/US-STORY/US-3.4/TASKS",
    story_file="./project-management/US-STORY/US-3.4/US-story.md",
    project_root="."
)
# Invoke TE agent -> enhances TASK-*.md files

# Step 3: Coder implements each task
for task_file in task_files:
    coder_prompt = Template(coder_template).substitute(
        task=task_description,
        acceptance_criteria=criteria,
        research=research_results
    )
    # Invoke Coder agent -> implements task

# Step 4: Reviewer reviews each implementation
for implementation in implementations:
    reviewer_prompt = Template(reviewer_template).substitute(
        code=code_files,
        criteria=acceptance_criteria
    )
    # Invoke Reviewer agent -> reviews code

# Step 5: Story-Reviewer reviews entire story
story_review_prompt = Template(sr_template).substitute(
    story_id="US-3.4",
    story_file="./project-management/US-STORY/US-3.4/US-story.md",
    tasks_dir="./project-management/US-STORY/US-3.4/TASKS",
    branch_name="feat/US-3.4"
)
# Invoke Story-Reviewer -> reviews entire story
```

### Pattern 2: Parallel Agent Invocation

```python
# Invoke multiple agents in parallel for independent tasks
from concurrent.futures import ThreadPoolExecutor

def invoke_coder(task):
    prompt = Template(coder_template).substitute(
        task=task.description,
        acceptance_criteria=task.criteria
    )
    # Invoke agent and return result

# Execute in parallel
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(invoke_coder, independent_tasks)
```

### Pattern 3: Research + Implementation

```python
# Step 1: Research if needed
if requires_research:
    research_prompt = Template(research_template).substitute(
        keywords="Google OAuth2 Python",
        depth="comprehensive"
    )
    research_results = invoke_research_agent(research_prompt)
else:
    research_results = "No research provided"

# Step 2: Implement with research context
coder_prompt = Template(coder_template).safe_substitute(
    task=task_description,
    research=research_results,
    acceptance_criteria=criteria
)
```

### Pattern 4: Refactor + Test + Review

```python
# Step 1: Refactor complex code
refactor_prompt = Template(refactor_template).substitute(
    code="src/legacy/complex_logic.py",
    complexity_threshold=10
)
refactored_code = invoke_refactor_agent(refactor_prompt)

# Step 2: Generate new tests
tester_prompt = Template(tester_template).substitute(
    code="src/legacy/complex_logic.py",
    coverage_target=80
)
tests = invoke_tester_agent(tester_prompt)

# Step 3: Review refactored code
reviewer_prompt = Template(reviewer_template).substitute(
    code="src/legacy/complex_logic.py",
    criteria="- [ ] Complexity < 10\n- [ ] Tests pass\n- [ ] Coverage >= 80%"
)
review = invoke_reviewer_agent(reviewer_prompt)
```

---

## Agent Model Selection Guide

### When to Use Sonnet

Use **Sonnet** model for agents requiring:
- Complex reasoning and analysis
- Deep codebase understanding
- Multi-file integration analysis
- Architectural decisions

**Agents using Sonnet**:
- Project-Manager (task breakdown)
- Task-Enhancer (codebase research)
- Coder (complex implementation)
- Reviewer (code analysis)
- Reviewer-Story (integration analysis)
- Refactor (code transformation)

### When to Use Haiku

Use **Haiku** model for agents with:
- Well-defined tasks
- Pattern-matching work
- Retrieval-focused work
- Cost-sensitive operations

**Agents using Haiku**:
- Tester (test generation)
- Research (documentation retrieval)
- Documentation (doc generation)
- Cleanup (dead code detection)

### Cost Considerations

**Sonnet**:
- Higher cost per token
- Better for complex reasoning
- Use for critical path (implementation, review)

**Haiku**:
- Lower cost per token (10-20x cheaper)
- Good for well-defined tasks
- Use for repetitive tasks (testing, docs, cleanup)

---

## Error Handling Patterns

### Missing Required Variables

```python
from string import Template

template = Template(agent_template)
try:
    prompt = template.substitute(**variables)
except KeyError as e:
    print(f"Missing required variable: {e}")
    print(f"Required variables: {extract_variables(agent_template)}")
    raise
```

### Invalid Variable Values

```python
def validate_variables(variables: dict) -> dict:
    """Validate all variable values before substitution."""
    validators = {
        "story_id": lambda x: re.match(r'^US-\d{8}-\d{3}$', x),
        "coverage_target": lambda x: 0 <= int(x) <= 100,
        "safe_mode": lambda x: x in ["true", "false"]
    }

    for key, validator in validators.items():
        if key in variables:
            if not validator(variables[key]):
                raise ValueError(f"Invalid value for {key}: {variables[key]}")

    return variables
```

### Agent Timeout Handling

```python
import asyncio

async def invoke_agent_with_timeout(prompt: str, timeout: int = 300):
    """Invoke agent with timeout."""
    try:
        result = await asyncio.wait_for(
            invoke_agent(prompt),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        print(f"Agent timed out after {timeout}s")
        raise
```

---

## Testing Agent Invocations

### Unit Test Example

```python
import pytest
from string import Template
from pathlib import Path

def test_project_manager_agent_invocation():
    """Test project-manager agent variable substitution."""
    template = Path(".claude/agents/project-manager.md").read_text()

    prompt = Template(template).substitute(
        role="full-stack developer",
        description="Add OAuth2 authentication",
        constraints="Python 3.11+, FastAPI",
        project_context="Existing JWT auth"
    )

    # Verify substitution
    assert "$role" not in prompt
    assert "$description" not in prompt
    assert "full-stack developer" in prompt
    assert "Add OAuth2 authentication" in prompt

def test_missing_required_variable():
    """Test error when required variable missing."""
    template = Template("$required_var")

    with pytest.raises(KeyError):
        template.substitute()  # Missing required_var

def test_optional_variable():
    """Test safe_substitute with optional variable."""
    template = Template("${optional:-default}")

    # With variable
    result = template.safe_substitute(optional="value")
    assert "value" in result

    # Without variable
    result = template.safe_substitute()
    assert "${optional:-default}" in result
```

---

## Appendix: Quick Reference

### Agent Summary Table

| Agent | Model | Input Variables | Output | Primary Use Case |
|-------|-------|----------------|--------|------------------|
| Project-Manager | Sonnet | role, description, constraints, project_context | USER-STORY.md + TASK-*.md | Break feature into story and tasks |
| Task-Enhancer | Sonnet | tasks_dir, story_file, project_root, codebase_focus | Enhanced TASK-*.md | Add technical context to tasks |
| Coder | Sonnet | task, research, acceptance_criteria | Implementation + tests | Implement coding tasks |
| Reviewer | Sonnet | code, criteria, standards | JSON review | Review task implementation |
| Reviewer-Story | Sonnet | story_id, story_file, tasks_dir, branch_name, standards | JSON review + report | Review entire story |
| Tester | Haiku | code, coverage_target | Test files | Generate test suites |
| Research | Haiku | keywords, depth | Research doc | Research technologies |
| Documentation | Haiku | scope, format, target | Documentation files | Generate/update docs |
| Refactor | Sonnet | code, complexity_threshold | Refactored code | Simplify complex code |
| Cleanup | Haiku | paths, safe_mode | Cleanup report | Remove dead code |

### Variable Naming Conventions

- Use lowercase with underscores: `$story_id`, `$tasks_dir`
- Use descriptive names: `$acceptance_criteria` not `$ac`
- Use defaults for optional variables: `${research:-No research provided}`
- Validate before substitution
- Document all variables with types and examples

### File Locations

All agent templates: `.claude/agents/`
- project-manager.md
- task-enhancer.md
- coder.md
- reviewer.md
- reviewer-story.md
- tester.md
- research.md
- documentation.md
- refactor.md
- cleanup.md

---

**End of Document**

For questions or contributions, see CONTRIBUTING.md or open an issue on GitHub.
