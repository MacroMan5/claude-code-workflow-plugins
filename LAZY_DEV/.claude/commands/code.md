---
description: Implement feature from flexible input (story file, task ID, brief, or issue)
argument-hint: "<input>"
allowed-tools: Read, Write, Edit, Bash, Task, Glob, Grep
---

# Code Command: Flexible Feature Implementation

Transform any input into working code with intelligent orchestration.

## Core Philosophy

**Accept anything, infer everything, build intelligently.**

No flags, no ceremony - just provide context and get code.

## Usage Examples

```bash
# Quick feature from brief
/lazy code "add logout button to header"

# From user story file
/lazy code @US-3.4.md
/lazy code US-3.4.md

# From task ID (auto-finds story)
/lazy code TASK-003

# From GitHub issue
/lazy code #456
/lazy code 456
```

## Input Detection Logic

### Phase 0: Parse Input

**Detect input type:**

```python
input = "$ARGUMENTS".strip()

if input.startswith("@") or input.endswith(".md"):
    # User story file reference
    input_type = "story_file"
    story_file = input.lstrip("@")

elif input.startswith("TASK-") or input.startswith("task-"):
    # Task ID - need to find story
    input_type = "task_id"
    task_id = input.upper()

elif input.startswith("#") or input.isdigit():
    # GitHub issue
    input_type = "github_issue"
    issue_number = input.lstrip("#")

else:
    # Brief description
    input_type = "brief"
    feature_brief = input
```

### Phase 1: Load Context

**From User Story File:**
```bash
# If input is @US-3.4.md or US-3.4.md
story_path="./project-management/US-STORY/*/US-story.md"
story_path=$(find ./project-management/US-STORY -name "*${story_id}*" -type d -exec find {} -name "US-story.md" \; | head -1)

# Read full story content
story_content=$(cat "$story_path")

# Find next pending task or use all tasks
next_task=$(grep -E "^### TASK-[0-9]+" "$story_path" | head -1)
```

**From Task ID:**
```bash
# If input is TASK-003
# Find which story contains this task
story_path=$(grep -r "### ${task_id}:" ./project-management/US-STORY --include="US-story.md" -l | head -1)

# Extract story content
story_content=$(cat "$story_path")

# Extract specific task section
task_section=$(sed -n "/^### ${task_id}:/,/^### TASK-/p" "$story_path" | sed '$d')
```

**From GitHub Issue:**
```bash
# If input is #456 or 456
issue_content=$(gh issue view ${issue_number} --json title,body,labels --jq '{title, body, labels: [.labels[].name]}')

# Parse as story or task
# If issue has "user-story" label, treat as story
# Otherwise treat as single task
```

**From Brief Description:**
```bash
# If input is "add logout button to header"
# Create minimal context
feature_brief="$input"

# Generate inline task
task_section="
### TASK-1: ${feature_brief}

**Description:**
${feature_brief}

**Acceptance Criteria:**
- Implementation works as described
- Code follows project conventions
- Basic error handling included
"
```

## Smart Orchestration Logic

### Auto-Detection Rules

**1. Test Detection:**
```python
# Check if project uses tests
has_tests = any([
    exists("pytest.ini"),
    exists("tests/"),
    exists("__tests__/"),
    exists("*.test.js"),
    exists("*_test.py"),
])

# Check if TDD mentioned in docs
tdd_required = any([
    "TDD" in read("README.md"),
    "test-driven" in read("CLAUDE.md"),
    "LAZYDEV_ENFORCE_TDD" in env,
])

# Decision
run_tests = has_tests or tdd_required or "test" in task_section.lower()
```

**2. Complexity Detection:**
```python
# Analyze task complexity
complexity_indicators = [
    "security", "authentication", "auth", "payment",
    "database", "migration", "critical", "api",
]

# Check task content
is_complex = any(keyword in task_section.lower() for keyword in complexity_indicators)

# Check estimate
if "Estimate:" in task_section:
    estimate = extract_estimate(task_section)
    is_complex = is_complex or estimate in ["L", "Large"]

# Default to simple
complexity = "complex" if is_complex else "simple"
```

**3. Review Detection:**
```python
# Always review complex tasks
needs_review = is_complex

# Review if multi-file changes expected
if not needs_review:
    # Check if task mentions multiple files/modules
    multi_file_keywords = [
        "refactor", "restructure", "multiple files",
        "across", "integration", "system-wide"
    ]
    needs_review = any(kw in task_section.lower() for kw in multi_file_keywords)

# Can skip for simple single-file changes
skip_review = not needs_review and complexity == "simple"
```

**4. User Story Detection:**
```python
# Check if we have a full story or single task
if input_type == "story_file":
    has_story = True
    # Work through tasks sequentially

elif input_type == "task_id":
    has_story = True
    # Story was found, implement specific task

elif input_type == "github_issue":
    # Check if issue is tagged as story
    has_story = "user-story" in issue_labels

else:  # brief
    has_story = False
    # Single task, quick implementation
```

## Execution Workflow

### Phase 2: Git Branch Setup

```bash
# Only create branch if working from story
if [ "$has_story" = true ]; then
    # Extract story ID from path or content
    story_id=$(extract_story_id)
    branch_name="feat/${story_id}-$(slugify_story_title)"

    # Create or checkout branch
    if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        git checkout "$branch_name"
    else
        git checkout -b "$branch_name"
    fi
else
    # Work on current branch for quick tasks
    current_branch=$(git branch --show-current)
    echo "Working on current branch: $current_branch"
fi
```

### Phase 3: Implementation

**Delegate to coder agent:**

```python
Task(
    prompt=f"""
You are the Coder Agent for LAZY-DEV-FRAMEWORK.

## Context Provided

{story_content if has_story else ""}

## Task to Implement

{task_section}

## Implementation Guidelines

1. **Read existing code first:**
   - Check README.md for project structure and conventions
   - Look for similar implementations in codebase
   - Identify existing patterns and styles

2. **Write clean, maintainable code:**
   - Type hints on all functions (if Python/TypeScript)
   - Docstrings for public APIs
   - Clear variable names
   - Error handling with specific exceptions

3. **Follow project conventions:**
   - Check for .editorconfig, .prettierrc, pyproject.toml
   - Match existing code style
   - Use project's logging/error patterns

4. **Tests (if required):**
   - TDD required: {run_tests}
   - Write tests if TDD enabled or "test" mentioned in task
   - Follow existing test patterns in repo
   - Aim for edge case coverage

5. **Security considerations:**
   - Input validation
   - No hardcoded secrets
   - Proper error messages (no sensitive data leaks)
   - Follow OWASP guidelines for web/API code

## Quality Standards

Code will be automatically checked by PostToolUse hook:
- Formatting (Black/Ruff/Prettier if configured)
- Linting (Ruff/ESLint if configured)
- Type checking (Mypy/TSC if configured)
- Tests (Pytest/Jest if TDD enabled)

Write quality code to pass these checks on first run.

## Output

Provide:
1. Implementation files (with full paths)
2. Test files (if TDD enabled)
3. Updated documentation (if API changes)
4. Brief summary of changes

DO NOT create a commit - that happens after review.
"""
)
```

### Phase 4: Quality Checks (Automatic)

**PostToolUse hook handles this automatically after Write/Edit operations:**

- Format: Auto-applied (Black/Ruff/Prettier)
- Lint: Auto-checked, warns if issues
- Type: Auto-checked, warns if issues
- Tests: Auto-run if TDD required

**No manual action needed** - hook runs after coder agent completes.

### Phase 5: Code Review (Conditional)

**Review decision:**

```python
if needs_review:
    # Invoke reviewer agent for complex/critical tasks
    Task(
        prompt=f"""
You are the Reviewer Agent for LAZY-DEV-FRAMEWORK.

## Task Being Reviewed

{task_section}

## Changes Made

{git_diff_output}

## Review Checklist

**Code Quality:**
- Readability and maintainability
- Follows project conventions
- Appropriate abstractions
- Clear naming

**Correctness:**
- Meets acceptance criteria
- Edge cases handled
- Error handling appropriate

**Security (if applicable):**
- Input validation
- No hardcoded secrets
- Proper authentication/authorization
- No SQL injection / XSS vulnerabilities

**Tests (if TDD required):**
- Tests cover main functionality
- Edge cases tested
- Tests are clear and maintainable

## Output

Return ONE of:
- **APPROVED**: Changes look good, ready to commit
- **REQUEST_CHANGES**: List specific issues to fix

Keep feedback concise and actionable.
"""
    )
else:
    echo "Review skipped: Simple task, single-file change"
fi
```

### Phase 6: Commit

**Only commit if approved or review skipped:**

```bash
# Prepare commit message
if [ "$has_story" = true ]; then
    commit_msg="feat(${task_id}): $(extract_task_title)

Implements ${task_id} from ${story_id}

$(summarize_changes)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
else
    commit_msg="feat: ${feature_brief}

Quick implementation from brief description.

$(summarize_changes)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
fi

# Create commit
git add .

git commit -m "$(cat <<'EOF'
$commit_msg
EOF
)"

# Tag if task completion
if [ "$input_type" = "task_id" ]; then
    git tag "task/${task_id}-done"
fi
```

### Phase 7: Output Summary

```
Task Complete
=============
Input: {input}
Type: {input_type}
{Story: {story_id}}
{Task: {task_id}}
Branch: {branch_name}
Complexity: {complexity}
Review: {skipped|passed}
Tests: {passed|skipped} {(n/n)}
Commit: {commit_hash}

Files Changed:
- {file1}
- {file2}

Next Steps:
{- Continue with next task: /lazy code TASK-{next}}
{- Review story and create PR: /lazy review {story_id}}
{- Work on new feature: /lazy code "description"}
```

## Intelligence Matrix

| Input | Detection | Story Lookup | Tests | Review | Branch |
|-------|-----------|--------------|-------|--------|--------|
| "brief" | Brief text | No | Auto | Simple=No | Current |
| @US-3.4.md | File reference | Yes (read file) | Auto | Smart | feat/US-3.4-* |
| TASK-003 | Task ID pattern | Yes (grep) | Auto | Smart | feat/US-* |
| #456 | Issue number | Yes (gh) | Auto | Smart | feat/issue-456 |

**Auto = Check project for test framework and TDD requirement**
**Smart = Complex/multi-file/security = Yes, Simple/single-file = No**

## Decision Trees

### Test Execution Decision

```
Has test framework in repo? ────No───→ Skip tests
         │
        Yes
         │
TDD in docs or LAZYDEV_ENFORCE_TDD? ──Yes──→ Run tests (required)
         │
         No
         │
"test" mentioned in task? ────Yes───→ Run tests (requested)
         │
         No
         │
      Skip tests
```

### Review Decision

```
Task complexity = complex? ───Yes───→ Review required
         │
         No
         │
Security/auth/payment related? ──Yes──→ Review required
         │
         No
         │
Multi-file refactor? ────Yes────→ Review required
         │
         No
         │
      Skip review (simple task)
```

### Branch Strategy

```
Input has story context? ───Yes───→ Create/use feat/{story-id}-* branch
         │
         No
         │
   Work on current branch
```

## Examples in Action

### Example 1: Quick Feature
```bash
$ /lazy code "add logout button to header"

Detected: Brief description
Complexity: Simple (single feature)
Tests: Auto-detected (pytest found in repo)
Review: Skipped (simple, single-file)
Branch: Current branch

Implementing...
✓ Added logout button to src/components/Header.tsx
✓ Added test in tests/components/Header.test.tsx
✓ Quality checks passed
✓ Committed: feat: add logout button to header

Complete! (1 file changed)
```

### Example 2: From Story File
```bash
$ /lazy code @US-3.4.md

Detected: User story file
Story: US-3.4 - OAuth2 Authentication
Next pending: TASK-002 - Implement token refresh
Complexity: Complex (auth + security)
Tests: Required (TDD in CLAUDE.md)
Review: Required (complex task)
Branch: feat/US-3.4-oauth2-authentication

Implementing...
✓ Implemented token refresh in src/auth/refresh.py
✓ Added tests in tests/auth/test_refresh.py
✓ Quality checks passed
✓ Code review: APPROVED
✓ Committed: feat(TASK-002): implement token refresh

Complete! Continue with: /lazy code TASK-003
```

### Example 3: From Task ID
```bash
$ /lazy code TASK-007

Detected: Task ID
Finding story... Found in US-2.1-payment-processing
Task: TASK-007 - Add retry logic to payment API
Complexity: Complex (payment + API)
Tests: Required (pytest found)
Review: Required (payment-related)
Branch: feat/US-2.1-payment-processing

Implementing...
✓ Added retry logic to src/payment/api.py
✓ Added retry tests in tests/payment/test_api.py
✓ Quality checks passed
✓ Code review: APPROVED
✓ Committed: feat(TASK-007): add retry logic to payment API
✓ Tagged: task/TASK-007-done

Complete! Continue with: /lazy code TASK-008
```

### Example 4: From GitHub Issue
```bash
$ /lazy code #456

Detected: GitHub issue
Fetching issue #456...
Issue: "Fix validation error in user signup form"
Labels: bug, frontend
Complexity: Simple (bug fix)
Tests: Required (jest found in repo)
Review: Skipped (simple bug fix)
Branch: Current branch

Implementing...
✓ Fixed validation in src/components/SignupForm.tsx
✓ Added regression test in tests/components/SignupForm.test.tsx
✓ Quality checks passed
✓ Committed: fix: validation error in user signup form (closes #456)

Complete! Issue #456 will be closed on PR merge.
```

## Key Principles

1. **Zero Configuration**: No flags, no setup - just provide input
2. **Smart Defaults**: Infer tests, review, complexity from context
3. **Flexible Input**: Accept stories, tasks, briefs, issues
4. **Auto Quality**: PostToolUse hook handles formatting/linting/tests
5. **Contextual Branching**: Stories get branches, briefs work on current
6. **Progressive Enhancement**: More context = smarter orchestration

## Integration Points

**With plan command:**
```bash
/lazy plan "feature description"  # Creates US-story.md
/lazy code @US-story.md          # Implements first task
/lazy code TASK-002              # Continues with next task
```

**With review command:**
```bash
/lazy code TASK-001  # Commit 1
/lazy code TASK-002  # Commit 2
/lazy code TASK-003  # Commit 3
/lazy review US-3.4  # Review all tasks, create PR
```

**With fix command:**
```bash
/lazy code TASK-001       # Implementation
/lazy review US-3.4       # Generates review-report.md
/lazy fix review-report.md  # Apply fixes
```

## Environment Variables

```bash
# Force TDD for all tasks
export LAZYDEV_ENFORCE_TDD=1

# Minimum test count
export LAZYDEV_MIN_TESTS=3

# Skip review for all tasks (not recommended)
export LAZYDEV_SKIP_REVIEW=1
```

## Troubleshooting

**Issue: Task ID not found**
```bash
# Check story files exist
ls -la ./project-management/US-STORY/*/US-story.md

# Search for task manually
grep -r "TASK-003" ./project-management/US-STORY
```

**Issue: Tests not running**
```bash
# Check test framework installed
pytest --version  # or: npm test

# Check TDD configuration
cat CLAUDE.md | grep -i tdd
echo $LAZYDEV_ENFORCE_TDD
```

**Issue: Review not triggering**
```bash
# Reviews trigger automatically for:
# - Complex tasks (security/auth/database)
# - Multi-file changes
# - Large estimates

# To force review, set in task:
### TASK-X: ... [REVIEW_REQUIRED]
```

---

**Version:** 2.2.0
**Status:** Production-Ready
**Philosophy:** Accept anything, infer everything, build intelligently.
