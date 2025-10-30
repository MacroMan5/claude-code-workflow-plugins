---
description: Execute task from US-Story with flexible quality checks
argument-hint: "[TASK-ID] --story US-X or --issue N [--skip-review] [--skip-tests]"
allowed-tools: Read, Write, Edit, Bash, Task, Glob, Grep
---

# Task Execution Command

Execute a task from US-Story file or GitHub issue with pragmatic quality pipeline.

## Core Principles

1. **Simple by default**: No over-engineering for simple tasks
2. **TDD optional**: Only enforce tests if mentioned in repo/story
3. **Smart reviews**: Skip reviewer for trivial tasks, require for complex/critical ones
4. **Story-centric**: Reference US-Story file, not individual TASK files

## Usage

```bash
# Execute task from US-Story file
/lazy task-exec TASK-1 --story US-3.4

# Execute from GitHub issue
/lazy task-exec 43

# Skip review for simple tasks
/lazy task-exec TASK-1 --story US-3.4 --skip-review

# Skip tests (if TDD not required)
/lazy task-exec TASK-1 --story US-3.4 --skip-tests

# Preview execution plan
/lazy task-exec TASK-1 --story US-3.4 --dry-run
```

## Workflow

### Phase 1: Load Task Context

**From US-Story File** (default):
```bash
# Find story file
story_file=$(find ./project-management/US-STORY -name "*US-${story_id}*" -type f -name "US-story.md" | head -1)

# Read story content
story_content=$(cat "$story_file")

# Extract specific task section
task_section=$(sed -n "/^### TASK-${task_id}:/,/^### TASK-/p" "$story_file" | sed '$d')
```

**From GitHub Issue**:
```bash
# Fetch issue content
gh issue view ${issue_number} --json body --jq '.body'

# Extract task section (same format as US-Story)
```

**Task Complexity Detection**:
```bash
# Analyze task to determine complexity
complexity="simple"  # default

# Check for complexity indicators
if grep -q "critical\|security\|database\|authentication\|payment" "$task_section"; then
    complexity="complex"
fi

# Check task estimate
if grep -q "Estimate.*L\|Estimate.*Large" "$task_section"; then
    complexity="complex"
fi
```

### Phase 2: Git Branch Setup

```bash
# Create/checkout feature branch
branch_name="feat/${story_id}-$(extract_story_slug)"

if git show-ref --verify --quiet "refs/heads/$branch_name"; then
    git checkout "$branch_name"
else
    git checkout -b "$branch_name"
fi
```

### Phase 3: Implementation (Coder Agent)

**Invoke coder agent with story context**:

```python
Task(
    prompt=f"""
You are the Coder Agent for LAZY-DEV-FRAMEWORK.

## User Story
{story_content}

## Current Task
{task_section}

## Implementation Guidelines
1. Write clean, readable code
2. Add type hints if project uses them
3. Include docstrings for public APIs
4. Handle errors gracefully
5. Write tests if project requires TDD (check for pytest/jest in repo)

## Project Context
- Check README.md for coding standards
- Check for existing test patterns
- Follow existing code style

## Output
- Implementation files
- Test files (if TDD required in project)
- Updated docs (if needed)
"""
)
```

### Phase 4: Quality Checks (Automated via Hook)

**Quality checks run automatically via PostToolUse hook**:
- Format: Black/Ruff/Prettier (if configured)
- Lint: Ruff/ESLint (if configured)
- Type: Mypy/TSC (if configured)
- Tests: Pytest/Jest (if TDD required in project)

**No manual execution needed** - hooks handle this automatically after Write/Edit operations.

### Phase 5: Review (Conditional)

**Skip review if**:
- Task complexity is "simple" AND
- `--skip-review` flag provided OR
- Task estimate is S (small)

**Require review if**:
- Task complexity is "complex" OR
- Task involves security/database/authentication OR
- Task estimate is L (large)

```bash
needs_review=false

# Always review complex tasks
if [ "$complexity" = "complex" ]; then
    needs_review=true
fi

# Allow skip for simple tasks
if [ "$complexity" = "simple" ] && [ "$skip_review" = "true" ]; then
    needs_review=false
fi

if [ "$needs_review" = true ]; then
    # Invoke reviewer agent
    Task(
        prompt=f"""
You are the Reviewer Agent for LAZY-DEV-FRAMEWORK.

## Task
{task_section}

## Changes
{git_diff_output}

## Review Focus
- Code quality and readability
- Security issues (if applicable)
- Error handling
- Tests (if TDD required)

## Output
Return: APPROVED or REQUEST_CHANGES with specific issues
"""
    )
fi
```

### Phase 6: Commit

```bash
# Create conventional commit
git add .

commit_msg="feat(${task_id}): $(extract_task_title)

Implements ${task_id} from ${story_id}

$(list_changes)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git commit -m "$commit_msg"

# Tag task completion
git tag "task/${task_id}-done"
```

## Output

```
Task Complete: TASK-1
=====================
Story: US-3.4
Branch: feat/US-3.4-oauth2-authentication
Complexity: simple
Review: skipped (simple task)
Tests: passed (10/10)
Commit: abc123d

Next: Continue with next task or run /lazy story-review
```

## Flags

- `--story US-X`: Story ID (required if not using --issue)
- `--issue N`: GitHub issue number
- `--skip-review`: Skip code review (for simple tasks)
- `--skip-tests`: Skip test execution (if TDD not required)
- `--dry-run`: Preview execution plan without running

## Decision Logic

**When to skip tests**:
- No pytest/jest/testing framework in repo
- No TDD mentioned in README/CLAUDE.md
- `--skip-tests` flag provided

**When to skip review**:
- Task complexity is "simple"
- Task estimate is S (small)
- `--skip-review` flag provided
- NOT security/auth/database related

**When tests are required**:
- TDD mentioned in repo documentation
- Existing test suite with >50 tests
- Task involves critical functionality

**When review is required**:
- Task complexity is "complex"
- Task estimate is L (large)
- Security/auth/database/payment related
- Changes to critical code paths
