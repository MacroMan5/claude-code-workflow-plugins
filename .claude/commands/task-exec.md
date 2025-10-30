---
description: Execute task with quality pipeline and explicit agent orchestration
argument-hint: "[TASK-ID] [--user-story US-X] [--issue N] [--with-research] [--dry-run] [--continue-from STAGE] [--parallel MODE]"
allowed-tools: Read, Write, Edit, Bash, Task, Glob, Grep
---

# Task Execution Command

Execute single task or entire user story through full quality pipeline with explicit agent invocation and parallelization.

**CRITICAL WORKFLOW RULES**:
1. Each completed task = **ONE COMMIT** (NOT PR)
2. PRs only at story level via `/lazy story-review`
3. Explicit agent invocation via **Task tool** (NOT automatic routing)
4. Parallel execution for independent tasks via **multiple Task tool calls in single message**

## Aliases

This command can be invoked as:
- `/lazy task-exec` - Traditional name (backward compatible)
- `/lazy issue-implementation` - When working from GitHub issues
- `/lazy us-development` - When implementing user stories

All aliases execute identical workflow with full git branch management.

## Input Variables

Parse arguments to extract named variables:

- `$task_id`: Task identifier (e.g., "TASK-1.1" or "43" for GitHub issue) or "all" for all pending tasks
- `$with_research`: "true" to invoke research agent (default: "false")
- `$dry_run`: "true" for preview only (default: "false")
- `$continue_from`: "format|lint|type|test" to resume from failure
- `$parallel`: "auto|true|false" for parallel execution (default: "auto")
- `$story_id`: User story ID (e.g., "US-3.4") - REQUIRED when not using --issue
- `$user_story_id`: DEPRECATED - use `$story_id` instead
- `$issue_number`: GitHub issue number (e.g., "42")
- `$use_gh`: "true" to fetch from GitHub instead of files (default: "false")

## Example Usage

```bash
# Single task execution from directory structure (default)
/lazy task-exec TASK-1.1 --story US-3.4

# With research for unfamiliar tech
/lazy task-exec TASK-1.2 --story US-3.4 --with-research

# Preview only (dry-run shows what would happen, no commits)
/lazy task-exec TASK-1.1 --story US-3.4 --dry-run

# Resume from quality check that failed
/lazy task-exec TASK-1.1 --story US-3.4 --continue-from type

# Execute entire user story from directory structure (default)
/lazy task-exec all --story US-3.4

# Execute task from GitHub issue
/lazy task-exec 43 --use-gh

# Execute all tasks in story from directory
/lazy task-exec all --story US-3.4 --parallel auto

# Execute all tasks from GitHub issue + sub-issues
/lazy issue-implementation all --issue 42 --use-gh

# Parallel execution with automatic parallelization
/lazy task-exec all --story US-3.4 --parallel auto

# Force sequential execution (useful for debugging)
/lazy task-exec all --story US-3.4 --parallel false

# Parallel with research for each task
/lazy task-exec all --story US-3.4 --parallel auto --with-research

# Dry-run parallel execution (preview execution plan)
/lazy task-exec all --story US-3.4 --parallel auto --dry-run
```

---

## Execution Workflow

### Phase 0: Task and Story Resolution (ALWAYS FIRST)

**CRITICAL**: This phase MUST complete before any git workflow or task implementation begins.

This phase handles locating and loading task and story files from either the directory structure or GitHub CLI.

#### Step 1: Determine Resolution Mode

Check which mode to use based on flags:

```bash
# Determine mode
if [[ "$use_gh" == "true" ]]; then
    resolution_mode="github"
    echo "Resolution Mode: GitHub CLI"
else
    resolution_mode="directory"
    echo "Resolution Mode: Directory Structure (default)"
fi
```

#### Step 2: Mode A - Directory-Based Resolution (Default)

When `$use_gh` is NOT "true", resolve from directory structure:

```bash
# Extract story ID from flags (prefer $story_id over deprecated $user_story_id)
if [[ -n "$story_id" ]]; then
    story_identifier="$story_id"
elif [[ -n "$user_story_id" ]]; then
    story_identifier="$user_story_id"
    echo "WARNING: --user-story flag is deprecated, use --story instead"
elif [[ -n "$issue_number" ]]; then
    story_identifier="issue-$issue_number"
else
    echo "ERROR: Story ID required. Use --story US-X.X or --issue N"
    exit 1
fi

# Find story directory
if [[ "$story_identifier" =~ ^US- ]]; then
    # Find matching US-STORY directory
    story_dir=$(find ./project-management/US-STORY -name "US-${story_identifier}-*" -type d | head -1)

    if [[ -z "$story_dir" ]]; then
        echo "ERROR: Story directory not found for ${story_identifier}"
        echo "Expected pattern: ./project-management/US-STORY/US-${story_identifier}-*/"
        echo ""
        echo "Available stories:"
        find ./project-management/US-STORY -maxdepth 1 -type d -name "US-*" | xargs -n1 basename | sort
        echo ""
        echo "Action: Run /lazy create-feature first to create story"
        exit 1
    fi

    # Load story file
    story_file="${story_dir}/US-story.md"
    if [[ ! -f "$story_file" ]]; then
        echo "ERROR: Story file not found: $story_file"
        exit 1
    fi

    tasks_dir="${story_dir}/TASKS"

    # Verify tasks directory exists
    if [[ ! -d "$tasks_dir" ]]; then
        echo "ERROR: Tasks directory not found: $tasks_dir"
        echo "Action: Ensure /lazy create-feature completed successfully"
        exit 1
    fi
else
    echo "ERROR: Invalid story identifier format: $story_identifier"
    echo "Expected: US-X.X (e.g., US-3.4)"
    exit 1
fi

# Load task file(s)
if [[ "$task_id" == "all" ]]; then
    # Load all TASK-*.md files from tasks_dir
    task_files=$(find "$tasks_dir" -name "TASK-*.md" -type f | sort)

    if [[ -z "$task_files" ]]; then
        echo "ERROR: No task files found in: $tasks_dir"
        echo "Action: Ensure /lazy create-feature generated task files"
        exit 1
    fi

    # Count tasks
    task_count=$(echo "$task_files" | wc -l)
    echo "Found $task_count tasks in story ${story_identifier}"

    # List tasks
    echo "Tasks to execute:"
    for task_file in $task_files; do
        task_name=$(basename "$task_file" .md)
        task_title=$(grep "^# " "$task_file" | head -1 | sed 's/^# //')
        echo "  - $task_name: $task_title"
    done
else
    # Load specific task
    task_file="${tasks_dir}/TASK-${task_id}.md"

    if [[ ! -f "$task_file" ]]; then
        echo "ERROR: Task file not found: $task_file"
        echo ""
        echo "Available tasks in ${story_identifier}:"
        find "$tasks_dir" -name "TASK-*.md" -type f | xargs -n1 basename | sed 's/.md$//' | sort
        echo ""
        echo "Action: Use one of the task IDs above (e.g., TASK-1.1)"
        exit 1
    fi

    task_files="$task_file"
    echo "Found task: $(basename "$task_file" .md)"
fi

# Export for later phases
export STORY_DIR="$story_dir"
export STORY_FILE="$story_file"
export TASKS_DIR="$tasks_dir"
export TASK_FILES="$task_files"
export STORY_IDENTIFIER="$story_identifier"
```

#### Step 3: Mode B - GitHub CLI Resolution

When `$use_gh` is "true", resolve from GitHub:

```bash
# Check gh CLI installed and authenticated
if ! command -v gh &> /dev/null; then
    echo "ERROR: GitHub CLI (gh) not found"
    echo "Action: Install with: brew install gh (macOS) or https://cli.github.com/"
    exit 1
fi

if ! gh auth status &> /dev/null; then
    echo "ERROR: GitHub CLI not authenticated"
    echo "Action: Run: gh auth login"
    exit 1
fi

# Determine issue number
if [[ -n "$issue_number" ]]; then
    story_issue_number="$issue_number"
elif [[ "$task_id" =~ ^[0-9]+$ ]]; then
    # Task ID is a number - treat as GitHub issue
    story_issue_number=$(gh issue view "$task_id" --json labels --jq '.labels[] | select(.name | startswith("parent:")) | .name' | sed 's/parent://')

    if [[ -z "$story_issue_number" ]]; then
        echo "ERROR: Cannot determine parent issue for task #$task_id"
        echo "Action: Add 'parent:N' label to issue or use --issue flag"
        exit 1
    fi
else
    echo "ERROR: GitHub mode requires --issue flag or numeric task ID"
    exit 1
fi

# Fetch story from GitHub
echo "Fetching story from GitHub issue #${story_issue_number}..."
story_issue=$(gh issue view "$story_issue_number" --json title,body,labels --jq '.')

if [[ -z "$story_issue" ]]; then
    echo "ERROR: GitHub issue #${story_issue_number} not found"
    echo "Action: Check issue number with: gh issue list"
    exit 1
fi

story_title=$(echo "$story_issue" | jq -r '.title')
story_body=$(echo "$story_issue" | jq -r '.body')

echo "Story: #${story_issue_number} - $story_title"

# Fetch sub-issues (tasks) with parent label
echo "Fetching tasks (sub-issues) with label 'parent:${story_issue_number}'..."
sub_issues=$(gh issue list --label "parent:${story_issue_number}" --json number,title,body,state --jq '.')

if [[ -z "$sub_issues" || "$sub_issues" == "[]" ]]; then
    echo "WARNING: No sub-issues found with label 'parent:${story_issue_number}'"

    if [[ "$task_id" == "all" ]]; then
        echo "ERROR: Cannot execute 'all' tasks - no sub-issues found"
        echo "Action: Add 'parent:${story_issue_number}' label to task issues"
        exit 1
    fi

    # Single task mode - treat task_id as issue number
    if [[ "$task_id" =~ ^[0-9]+$ ]]; then
        sub_issues="[{\"number\": $task_id}]"
        echo "Using task issue #${task_id}"
    else
        echo "ERROR: Task ID must be numeric for GitHub mode"
        exit 1
    fi
fi

# Create temporary directory for task files
temp_dir="/tmp/lazy-dev-gh-${story_issue_number}"
mkdir -p "$temp_dir"

# Write story to temp file
echo "$story_body" > "$temp_dir/STORY.md"

# Process sub-issues
task_count=$(echo "$sub_issues" | jq '. | length')
echo "Found $task_count task(s)"

if [[ "$task_id" == "all" ]]; then
    # Process all sub-issues
    task_files=""
    for i in $(seq 0 $((task_count - 1))); do
        task_issue=$(echo "$sub_issues" | jq -r ".[$i]")
        task_number=$(echo "$task_issue" | jq -r '.number')
        task_title=$(echo "$task_issue" | jq -r '.title')
        task_body=$(echo "$task_issue" | jq -r '.body')
        task_state=$(echo "$task_issue" | jq -r '.state')

        # Skip closed issues
        if [[ "$task_state" == "CLOSED" ]]; then
            echo "  - Skipping closed issue #${task_number}: $task_title"
            continue
        fi

        # Write to temp file
        task_temp_file="$temp_dir/TASK-${task_number}.md"
        echo "$task_body" > "$task_temp_file"

        # Add GitHub issue reference to task file
        echo "" >> "$task_temp_file"
        echo "---" >> "$task_temp_file"
        echo "GitHub Issue: #${task_number}" >> "$task_temp_file"

        task_files="$task_files$task_temp_file "
        echo "  - Task #${task_number}: $task_title"
    done

    if [[ -z "$task_files" ]]; then
        echo "ERROR: No open tasks found"
        exit 1
    fi
else
    # Process specific task
    task_issue=$(gh issue view "$task_id" --json number,title,body --jq '.')

    if [[ -z "$task_issue" ]]; then
        echo "ERROR: GitHub issue #${task_id} not found"
        echo "Action: Check issue number with: gh issue list"
        exit 1
    fi

    task_number=$(echo "$task_issue" | jq -r '.number')
    task_title=$(echo "$task_issue" | jq -r '.title')
    task_body=$(echo "$task_issue" | jq -r '.body')

    task_temp_file="$temp_dir/TASK-${task_number}.md"
    echo "$task_body" > "$task_temp_file"

    # Add GitHub issue reference
    echo "" >> "$task_temp_file"
    echo "---" >> "$task_temp_file"
    echo "GitHub Issue: #${task_number}" >> "$task_temp_file"

    task_files="$task_temp_file"
    echo "Task: #${task_number} - $task_title"
fi

# Export for later phases
export STORY_DIR="$temp_dir"
export STORY_FILE="$temp_dir/STORY.md"
export TASKS_DIR="$temp_dir"
export TASK_FILES="$task_files"
export STORY_IDENTIFIER="issue-${story_issue_number}"
```

#### Step 4: Validation Summary

After resolution, validate all required files are loaded:

```bash
echo ""
echo "Task Resolution Complete"
echo "========================"
echo "Mode: $resolution_mode"
echo "Story: $STORY_IDENTIFIER"
echo "Story File: $STORY_FILE"
echo "Tasks Dir: $TASKS_DIR"
echo "Task Count: $(echo $TASK_FILES | wc -w)"
echo ""

# Verify files exist
if [[ ! -f "$STORY_FILE" ]]; then
    echo "ERROR: Story file missing after resolution: $STORY_FILE"
    exit 1
fi

for task_file in $TASK_FILES; do
    if [[ ! -f "$task_file" ]]; then
        echo "ERROR: Task file missing after resolution: $task_file"
        exit 1
    fi
done

echo "All files validated ✓"
echo ""
```

---

### Phase 1: Git Workflow Setup

**CRITICAL**: This phase MUST complete before any task implementation begins.

#### Step 1: Validate Git State

Check if we're in a git repository and verify current state:

```bash
# Check if in git repository
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "ERROR: Not a git repository. Initialize with: git init"
    exit 1
fi

# Get current branch
current_branch=$(git branch --show-current)

# Verify clean working tree
if [[ -n $(git status --porcelain) ]]; then
    echo "WARNING: Uncommitted changes detected"
    git status
    echo "Action: Commit or stash changes before proceeding"
    exit 1
fi

# Check for detached HEAD
if [[ -z "$current_branch" ]]; then
    echo "ERROR: Detached HEAD state. Checkout a branch first"
    exit 1
fi
```

#### Step 2: Create/Checkout Feature Branch

**Branch Naming Convention**: `{type}/{story-id}-{short-title}`

**Components**:
- `{type}`: One of: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
- `{story-id}`: User story ID (e.g., "US-3.4") or issue number (e.g., "issue-42")
- `{short-title}`: Kebab-case summary (max 50 chars)

**Branch Creation Logic**:

```bash
# Determine branch type from story file or task context
branch_type="feat"  # Default to feature

# Extract story ID (already set in Phase 0)
if [[ -n "$STORY_IDENTIFIER" ]]; then
    story_id="$STORY_IDENTIFIER"
else
    echo "ERROR: Story identifier not set from Phase 0"
    exit 1
fi

# Generate short title from story directory or GitHub issue
if [[ "$resolution_mode" == "directory" ]]; then
    # Extract short title from directory name
    # Directory pattern: US-{story_id}-{short-title}
    short_title=$(basename "$STORY_DIR" | sed "s/US-${story_id}-//")

    # Sanitize to kebab-case
    short_title=$(echo "$short_title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//' | cut -c1-50)
elif [[ "$resolution_mode" == "github" ]]; then
    # Fetch issue title from GitHub
    if [[ "$story_id" =~ ^issue- ]]; then
        issue_num=$(echo "$story_id" | sed 's/issue-//')
        issue_title=$(gh issue view "$issue_num" --json title --jq '.title')

        # Sanitize to kebab-case
        short_title=$(echo "$issue_title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//' | cut -c1-50)
    else
        short_title="implementation"
    fi
else
    short_title="implementation"
fi

# Create branch name: feat/US-3.4-oauth2-authentication or feat/issue-42-oauth2-authentication
branch_name="${branch_type}/${story_id}-${short_title}"

# Check if on protected branch
if [[ "$current_branch" == "main" || "$current_branch" == "master" || "$current_branch" == "develop" ]]; then
    echo "WARNING: Currently on protected branch: $current_branch"
    echo "Creating feature branch: $branch_name"

    # Check if branch exists
    if git show-ref --verify --quiet "refs/heads/$branch_name"; then
        echo "Branch already exists: $branch_name"
        git checkout "$branch_name"
    else
        echo "Creating new branch: $branch_name"
        git checkout -b "$branch_name"
    fi
else
    # Verify current branch name matches story/issue
    if [[ ! "$current_branch" =~ $story_id ]]; then
        echo "WARNING: Current branch ($current_branch) doesn't match story ID ($story_id)"
        echo "Action: Checkout correct branch or create new one: $branch_name"

        # Offer to checkout/create correct branch
        if git show-ref --verify --quiet "refs/heads/$branch_name"; then
            echo "Checking out existing branch: $branch_name"
            git checkout "$branch_name"
        else
            echo "Creating new branch: $branch_name"
            git checkout -b "$branch_name"
        fi
    else
        echo "Already on correct branch: $current_branch"
    fi
fi

# Create story start tag
git tag "story/${story_id}-start" -f -m "Start of user story ${story_id}"

# Display git state
echo "Git State:"
echo "  Branch: $(git branch --show-current)"
echo "  Commit: $(git log --oneline -1)"
echo "  Status: $(git status --porcelain | wc -l) uncommitted changes"
```

---

### Phase 2: Task Implementation with Explicit Agent Invocation

**CRITICAL**: All agents are invoked explicitly via **Task tool**, NOT automatic routing.

This phase handles single task or parallel task groups based on `$parallel` mode and dependency analysis.

#### Single Task Execution

For a single task (when `$task_id` is not "all"):

1. **Load Task from File**

   ```bash
   # Task file was loaded in Phase 0 and stored in $TASK_FILES
   task_file="$TASK_FILES"

   # Read task content
   task_content=$(cat "$task_file")

   # Extract task title
   task_title=$(grep "^# " "$task_file" | head -1 | sed 's/^# //')

   # Extract acceptance criteria (section after "## Acceptance Criteria")
   acceptance_criteria=$(sed -n '/^## Acceptance Criteria/,/^## /p' "$task_file" | sed '$d')

   # Extract GitHub issue number if present
   github_issue=$(grep "^GitHub Issue: #" "$task_file" | sed 's/.*#//')

   if [[ -n "$github_issue" ]]; then
       echo "Task linked to GitHub issue: #${github_issue}"
   fi
   ```

2. **Tag Task Start**

   ```bash
   git tag "task/$task_id-start" -f -m "Start implementation of $task_id"
   ```

3. **Research Agent (Optional - Explicit Invocation via Task tool)**

   If `$with_research` is "true", invoke research agent explicitly:

   ```markdown
   # EXPLICIT AGENT INVOCATION using Task tool
   # Launch research agent with substituted context

   Use Task tool to invoke research agent:
   ```

   **Agent Invocation Pattern**:

   ```python
   # Invoke research agent explicitly via Task tool
   Task(
       prompt=f"""
You are the Research Agent for LAZY-DEV-FRAMEWORK.

## Task Context
**Task**: {task_title}
**Description**: {task_description}
**Technologies**: {extracted_technologies_from_task}

## Research Goals
- Official documentation for: {extracted_technologies}
- Find relevant libraries/frameworks
- Note potential pitfalls
- Gather code examples
- Identify best practices

## Research Depth
quick (or comprehensive if complex)

## Output Format
Create research findings with:
1. Official Documentation (URLs, versions)
2. Key APIs/methods
3. Code examples
4. Best practices
5. Common pitfalls
6. Recommendations
"""
   )
   ```

   **Expected Output**: Research context stored for coder agent

4. **Coder Agent (Explicit Invocation via Task tool)**

   Invoke coder agent explicitly for implementation:

   ```markdown
   # EXPLICIT AGENT INVOCATION using Task tool
   # Launch coder agent with substituted context
   ```

   **Agent Invocation Pattern**:

   ```python
   # Invoke coder agent explicitly via Task tool
   Task(
       prompt=f"""
You are the Coder Agent for LAZY-DEV-FRAMEWORK.

## Task
{task_content}

## Research Context (if available)
{research_context if with_research else "No research requested"}

## Acceptance Criteria
{acceptance_criteria}

## GitHub Issue
{f"Closes #{github_issue}" if github_issue else "N/A"}

## Instructions
1. **Follow TDD**: Write tests FIRST, then implementation
2. Add comprehensive type hints (Python 3.11+)
3. Include docstrings (Google style) for all functions/classes
4. Handle edge cases and errors
5. Ensure cross-OS compatibility (Windows/Linux/macOS)
6. Security best practices (input validation, no hardcoded secrets)

## Code Quality Requirements
- Type hints on all functions
- Docstrings with Args, Returns, Raises
- Error handling with specific exceptions
- Input validation
- Minimum 80% test coverage

## Output
Create:
1. Implementation files (*.py)
2. Test files (test_*.py)
3. Update relevant documentation
"""
   )
   ```

   **Expected Output**: Implementation files, test files, updated docs

#### Parallel Task Execution

When `$parallel` is "auto" or "true" and multiple independent tasks exist:

1. **Group Independent Tasks**

   Analyze dependencies and create execution groups:

   ```python
   # Pseudo-code for dependency analysis
   def analyze_dependencies(task_files):
       tasks = parse_task_files(task_files)
       groups = []
       current_group = []

       for task in tasks:
           if task.has_dependencies():
               # Start new group if current has tasks
               if current_group:
                   groups.append(current_group)
                   current_group = []
               # Check if dependencies are satisfied
               if all_dependencies_completed(task.dependencies):
                   current_group.append(task)
           else:
               # No dependencies - add to current group
               current_group.append(task)

       # Add final group
       if current_group:
           groups.append(current_group)

       return groups
   ```

   **Example Dependency Groups**:

   ```
   TASKS.md:
   - TASK-1.1: Setup API client (no dependencies)
   - TASK-1.2: Build authentication (no dependencies)
   - TASK-1.3: Add validation (depends on TASK-1.1)
   - TASK-1.4: Error handling (depends on TASK-1.2)

   Execution Plan:
     Group 1 (parallel): TASK-1.1, TASK-1.2
     Group 2 (parallel): TASK-1.3, TASK-1.4
   ```

2. **Launch Parallel Agents (Multiple Task Tool Calls in Single Message)**

   **CRITICAL PATTERN**: For each group, launch multiple agents in parallel using **a single message with multiple Task tool calls**:

   ```markdown
   # PARALLEL EXECUTION PATTERN
   # Launch multiple coder agents in parallel for independent tasks

   ## Group 1: 2 independent tasks

   # Message with multiple Task tool invocations (in single message):

   Task Call 1 - TASK-1.1:
   Task(
       prompt="""
You are the Coder Agent for LAZY-DEV-FRAMEWORK.

## Task
TASK-1.1: Setup API client

[Task-specific context only - NOT full story]

## Instructions
[Same as single task mode]
"""
   )

   Task Call 2 - TASK-1.2:
   Task(
       prompt="""
You are the Coder Agent for LAZY-DEV-FRAMEWORK.

## Task
TASK-1.2: Build authentication

[Task-specific context only - NOT full story]

## Instructions
[Same as single task mode]
"""
   )

   # Both agents run independently in parallel
   # Each agent sees only its specific task context (minimal tokens)
   ```

   **Key Benefits**:
   - 3-4 independent tasks complete in ~same time as 1 task
   - Each agent has minimal context (only its task, not full story)
   - Lower total token usage vs sequential with full story context
   - Scalable to 10+ task stories

3. **Wait for All Agents to Complete**

   All agents in the group must complete before proceeding to quality pipeline.

4. **Repeat for Next Group**

   After Group 1 completes and passes quality pipeline, launch Group 2 in parallel.

**Parallel Modes**:
- `--parallel auto` (default): Automatically detect independent tasks and parallelize
- `--parallel true`: Force parallel execution (warns if dependencies detected)
- `--parallel false`: Sequential execution only (useful for debugging)

**Dry-Run Output for Parallel Execution**:

```
DRY RUN: Parallel Execution Plan
=================================
Group 1 (2 tasks in parallel):
  - TASK-1.1: Setup API client [Coder Agent 1 + Reviewer Agent 1]
  - TASK-1.2: Build authentication [Coder Agent 2 + Reviewer Agent 2]

Group 2 (2 tasks in parallel):
  - TASK-1.3: Add validation [Coder Agent 3 + Reviewer Agent 3] (depends on TASK-1.1)
  - TASK-1.4: Error handling [Coder Agent 4 + Reviewer Agent 4] (depends on TASK-1.2)

Would create 4 commits (1 per task)
Estimated time: ~93s (vs ~176s sequential)
Estimated speedup: 1.88x
```

---

### Phase 3: Quality Pipeline (MUST ALL PASS)

**CRITICAL**: Every task MUST pass all quality gates sequentially. FAIL-FAST on any error.

The quality pipeline enforces strict code quality before any review or commit:

```
Format → Lint → Type → Test
  ↓       ↓      ↓      ↓
Pass   Pass   Pass   Pass  → Proceed to Review
Fail   Fail   Fail   Fail  → STOP, Report Error
```

#### Step 1: Format (Black + Ruff)

```bash
# Run Black formatter
python scripts/format.py <files>

# Verify no formatting issues
if [[ $? -ne 0 ]]; then
    echo "ERROR: Format check failed"
    echo "Action: Review format output and fix issues"
    echo "Resume with: /lazy task-exec $task_id --continue-from format"
    exit 1
fi
```

#### Step 2: Lint (Ruff)

```bash
# Run Ruff linter
python scripts/lint.py <files>

# Check for violations
if [[ $? -ne 0 ]]; then
    echo "ERROR: Lint check failed"
    echo "Action: Fix linting violations"
    echo "Resume with: /lazy task-exec $task_id --continue-from lint"
    exit 1
fi
```

#### Step 3: Type Check (Mypy)

```bash
# Run Mypy type checker
python scripts/type_check.py <files>

# Check for type errors
if [[ $? -ne 0 ]]; then
    echo "ERROR: Type check failed"
    echo "Action: Add missing type hints or fix type errors"
    echo "Resume with: /lazy task-exec $task_id --continue-from type"
    exit 1
fi
```

#### Step 4: Test (Pytest)

```bash
# Run Pytest with coverage
python scripts/test_runner.py tests/

# Verify tests pass and coverage >= 80%
if [[ $? -ne 0 ]]; then
    echo "ERROR: Tests failed"
    echo "Action: Fix failing tests or implementation"
    echo "Resume with: /lazy task-exec $task_id --continue-from test"
    exit 1
fi

# Check coverage threshold
coverage=$(pytest --cov --cov-report=term-missing | grep "TOTAL" | awk '{print $4}' | sed 's/%//')
if [[ $coverage -lt 80 ]]; then
    echo "ERROR: Coverage below 80% (current: ${coverage}%)"
    echo "Action: Add more tests to reach 80% coverage"
    exit 1
fi
```

**Quality Pipeline Output**:

```
Quality Pipeline: TASK-1.1
==========================
Format (Black + Ruff): PASS (3 files formatted)
Lint (Ruff): PASS (0 violations)
Type (Mypy): PASS (0 errors)
Test (Pytest): PASS (24/24 tests, 87% coverage)

Quality Gates: ALL PASSED
Proceeding to code review...
```

---

### Phase 4: Review & Commit

**ONLY if quality pipeline passes**, proceed to review and commit.

#### Step 1: Reviewer Agent (Explicit Invocation via Task tool)

Invoke reviewer agent explicitly to validate implementation:

```markdown
# EXPLICIT AGENT INVOCATION using Task tool
# Launch reviewer agent with code changes and acceptance criteria
```

**Agent Invocation Pattern**:

```python
# Invoke reviewer agent explicitly via Task tool
Task(
    prompt=f"""
You are the Reviewer Agent for LAZY-DEV-FRAMEWORK.

## Task Being Reviewed
{task_description}

## Code Changes
{git_diff_output}

## Acceptance Criteria
{acceptance_criteria}

## Review Checklist
1. Code Quality: Type hints, docstrings, clean code, no code smells
2. Security: Input validation, no secrets, error handling, OWASP Top 10
3. Testing: Unit tests present, tests pass, edge cases covered, >= 80% coverage
4. Functionality: Meets acceptance criteria, handles edge cases, performance acceptable
5. Documentation: Docstrings updated, README updated if needed

## Output Format
Return JSON:
{{
  "status": "APPROVED" | "REQUEST_CHANGES",
  "issues": [
    {{
      "severity": "CRITICAL" | "WARNING" | "SUGGESTION",
      "file": "path/to/file.py",
      "line": 42,
      "description": "What's wrong",
      "fix": "How to fix it"
    }}
  ],
  "summary": "Overall assessment"
}}

## Decision Criteria
- APPROVED: No critical issues, warnings are minor
- REQUEST_CHANGES: Critical issues OR multiple warnings
"""
)
```

**If Review NOT Approved**:

```
Code Review: CHANGES REQUESTED
==============================
Changes needed:
1. Missing error handling for network timeouts
2. Test coverage for edge case: empty response
3. Add type hints for callback parameter

Action: Fix issues and re-run task-exec
```

**STOP** execution and return for fixes.

#### Step 2: Git Commit (Only if Review Approved)

**CRITICAL**: Each completed task = **ONE COMMIT** (NOT PR)

Create conventional commit with strict message format:

```bash
# Stage all changes
git add .

# Verify clean staging
if [[ -z $(git diff --cached --name-only) ]]; then
    echo "ERROR: No changes to commit"
    exit 1
fi

# Create commit message
commit_type="feat"  # or fix, refactor, etc.
commit_scope="$task_id"
commit_description="<short description of what was implemented>"

# Extract GitHub issue number from task file (if present)
github_issue_ref=""
if [[ -n "$github_issue" ]]; then
    github_issue_ref="Closes #${github_issue}"
fi

# Commit with conventional format
if [[ -n "$github_issue_ref" ]]; then
    # Include GitHub issue reference
    git commit -m "$(cat <<EOF
${commit_type}(${commit_scope}): ${commit_description}

Implements ${task_id}: ${task_title}

${github_issue_ref}

Changes:
- Bullet point summary of changes
- Additional context about implementation
- Notable decisions or trade-offs

Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
else
    # Standard commit without GitHub reference
    git commit -m "$(cat <<EOF
${commit_type}(${commit_scope}): ${commit_description}

- Bullet point summary of changes
- Additional context about implementation
- Notable decisions or trade-offs

Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
fi

# Tag task completion
git tag "task/${task_id}-committed" -f -m "Task ${task_id} committed"
git tag "task/${task_id}-approved" -f -m "Task ${task_id} approved by reviewer"
```

**Commit Output**:

```
Commit Created: TASK-1.1
========================
Commit: abc123def456 - feat(TASK-1.1): implement OAuth2 Google provider
Tags:
  - task/TASK-1.1-start
  - task/TASK-1.1-committed
  - task/TASK-1.1-approved

Working tree: CLEAN
Branch: feat/US-3.4-oauth2-authentication
Status: Awaiting story review for PR creation
```

---

### Phase 5: Parallelization Opportunities (While Tasks in Review)

**CRITICAL**: While current task/group is being reviewed, can run parallel tasks if independent.

**Parallelization Decision Logic**:

```python
if task_has_no_dependencies(next_task) and current_task_in_review:
    # Can run in parallel
    spawn_parallel_task_exec(next_task)

if documentation_needed and code_stable:
    # Run documentation agent in parallel
    Task(prompt="Documentation Agent prompt...")

if cleanup_opportunities_detected:
    # Run cleanup agent in parallel
    Task(prompt="Cleanup Agent prompt...")
```

**Parallel Agents Available**:

1. **Documentation Agent** (if code is stable):
   - Invoke `.claude/agents/documentation.md` via Task tool
   - Generate/update docs for new code
   - Can run while other tasks are in review

2. **Cleanup Agent** (if refactoring identified):
   - Invoke `.claude/agents/cleanup.md` via Task tool
   - Remove dead code, unused imports
   - Can run while other tasks are in review

3. **Next Independent Task** (if available):
   - Check TASKS.md for tasks with satisfied dependencies
   - Start next task-exec in parallel
   - Each task runs in isolated context

**Example Parallel Execution**:

```bash
# Task 1.1 in review → Start Task 1.2 (independent)
/lazy task-exec TASK-1.1
# While reviewing, automatically start:
/lazy task-exec TASK-1.2  # (if independent)

# Or launch documentation agent in parallel:
Task(prompt="""
You are the Documentation Agent for LAZY-DEV-FRAMEWORK.
Generate API documentation for newly implemented OAuth2 module.
""")
```

---

### Phase 6: Final State (After All Tasks)

After all tasks complete (single task or all tasks in story), provide summary report.

#### Summary Report

```bash
# List all commits in this story
echo "Commits Created:"
base_branch="main"  # or extract from git config
git log --oneline ${base_branch}..HEAD

# List all task tags
echo "Task Tags:"
git tag -l 'task/*-committed'

# Show branch state
echo "Branch State:"
git branch -vv

# Compare with base branch
echo "Changes vs ${base_branch}:"
git diff ${base_branch}...HEAD --stat

# Count files changed
files_changed=$(git diff ${base_branch}...HEAD --name-only | wc -l)
echo "Files changed: $files_changed"

# DO NOT CREATE PR
echo "Ready for story review"
echo "Next step: Run /lazy story-review to create PR"
```

**Final Output (Single Task)**:

```
Task Execution Complete: TASK-1.1
==================================
Quality Pipeline: PASS (format ✓ lint ✓ type ✓ test ✓)
Code Review: APPROVED
Commit: abc123def456

Status: Awaiting story review for PR creation
Next: /lazy story-review
```

**Final Output (All Tasks - Parallel)**:

```
Story Execution Complete: US-3.4 (Parallel)
===========================================
Branch: feat/US-3.4-oauth2-authentication
Execution Mode: Parallel (auto)

Group 1 (parallel): 2 tasks in 52s
  ✓ TASK-1.1: Setup API client [Coder Agent 1 + Reviewer Agent 1]
  ✓ TASK-1.2: Build authentication [Coder Agent 2 + Reviewer Agent 2]

Group 2 (parallel): 2 tasks in 41s
  ✓ TASK-1.3: Add validation [Coder Agent 3 + Reviewer Agent 3]
  ✓ TASK-1.4: Error handling [Coder Agent 4 + Reviewer Agent 4]

Tasks Completed: 4/4
Commits: 4
Files Changed: 12
Total Duration: 93s (vs ~176s sequential)
Time Saved: 83s
Speedup Factor: 1.88x

Status: Awaiting story review for PR creation
Next: /lazy story-review
```

---

## Success Criteria

A task is considered successfully completed when:

- ✅ Task git tags created: `git tag task/TASK-X-start` and `git tag task/TASK-X-committed`
- ✅ Commit message follows conventional format: `{type}(TASK-X): {description}`
- ✅ Commit is on current feature branch, not pushed to remote
- ✅ No uncommitted changes remaining (clean working tree)
- ✅ All tests pass with ≥80% coverage
- ✅ Type checking passes with strict mode (Mypy)
- ✅ Code formatting passes (Black + Ruff)
- ✅ Linting passes with 0 violations (Ruff)
- ✅ Code review approved by reviewer agent (invoked via Task tool)
- ✅ Each agent explicitly invoked via Task tool (NOT automatic routing)

---

## Agent Invocation Summary

**CRITICAL**: All agents are invoked explicitly via Task tool with substituted context.

### Research Agent Invocation (Optional)

```python
Task(
    prompt=f"""
You are the Research Agent for LAZY-DEV-FRAMEWORK.

## Task Context
{task_context}

## Research Goals
{research_goals}

## Output Format
{output_format}
"""
)
```

### Coder Agent Invocation (Required)

```python
Task(
    prompt=f"""
You are the Coder Agent for LAZY-DEV-FRAMEWORK.

## Task
{task_content}

## Research Context (if available)
{research_context}

## Acceptance Criteria
{acceptance_criteria}

## Instructions
{implementation_instructions}
"""
)
```

### Reviewer Agent Invocation (Required)

```python
Task(
    prompt=f"""
You are the Reviewer Agent for LAZY-DEV-FRAMEWORK.

## Task Being Reviewed
{task_description}

## Code Changes
{git_diff}

## Acceptance Criteria
{acceptance_criteria}

## Review Checklist
{review_checklist}

## Output Format
{json_output_format}
"""
)
```

### Documentation Agent Invocation (Parallel - Optional)

```python
Task(
    prompt=f"""
You are the Documentation Agent for LAZY-DEV-FRAMEWORK.

## Context
{documentation_context}

## Instructions
{documentation_instructions}

## Output Format
{output_format}
"""
)
```

### Cleanup Agent Invocation (Parallel - Optional)

```python
Task(
    prompt=f"""
You are the Cleanup Agent for LAZY-DEV-FRAMEWORK.

## Context
{cleanup_context}

## Instructions
{cleanup_instructions}

## Safe Mode
{safe_mode_enabled}
"""
)
```

---

## Next Steps After Task Execution

After all tasks are committed and tagged, the story is ready for review:

```bash
# Run story review to create PR
/lazy story-review

# This will:
# 1. Validate all tasks committed (check for task/*-committed tags)
# 2. Run final quality checks across entire story
# 3. Generate comprehensive PR description
# 4. Create GitHub PR with gh CLI
# 5. Link tasks and commits in PR body
```

**DO NOT** create PR in this command. That responsibility belongs to `/lazy story-review`.
