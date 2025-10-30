---
description: Execute task with quality pipeline
argument-hint: "[TASK-ID] [--user-story US-X] [--issue N] [--with-research] [--dry-run] [--continue-from STAGE] [--parallel MODE]"
allowed-tools: Read, Write, Edit, Bash, Task, Glob, Grep
---

# Task Execution Command

Execute single task or entire user story through full quality pipeline with complete git workflow.

## Agent Routing

This command uses automatic agent routing via `.claude/core/agent_registry.json`:
- **Research**: intent "research-topic" → research agent
- **Implementation**: intent "implement-code" → coder agent
- **Review**: intent "review-code" → reviewer agent

Agents are invoked automatically based on pipeline stage. No manual agent selection required.

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

## Memory Graph Usage (Auto)

When tasks surface durable facts (owners, endpoints, IDs) or new entities (services, people, repos), use the Memory MCP tools:
- `mcp__memory__search_nodes` before creation to avoid duplicates
- `mcp__memory__create_entities` for missing entities
- `mcp__memory__add_observations` for atomic facts (include dates when useful)
- `mcp__memory__create_relations` to connect entities (active voice: depends_on, owned_by, maintained_by)

See `.claude/skills/memory-graph/` for playbooks and I/O shapes. This is auto-hinted by the UserPromptSubmit hook; you can still invoke manually.

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

**Dry-Run Output for Phase 0 (Task Resolution)**:

If `$dry_run` is "true", output the plan without executing:

```
DRY RUN: Task and Story Resolution
===================================
Resolution Mode: directory

Would load story from:
  Story Dir: ./project-management/US-STORY/US-3.4-oauth2-authentication
  Story File: ./project-management/US-STORY/US-3.4-oauth2-authentication/US-story.md
  Tasks Dir: ./project-management/US-STORY/US-3.4-oauth2-authentication/TASKS

Would load tasks:
  - TASK-1.1: Setup OAuth2 Google provider
  - TASK-1.2: Add token validation
  - TASK-1.3: Implement refresh logic
  - TASK-1.4: Add error handling

Proceeding to git workflow setup...
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

# Verify remote tracking (if remote configured)
if git remote | grep -q "origin"; then
    if ! git rev-parse --abbrev-ref --symbolic-full-name @{u} >/dev/null 2>&1; then
        echo "Setting up remote tracking for: $branch_name"
        git branch --set-upstream-to=origin/$branch_name $branch_name 2>/dev/null || true
    fi
fi

# Display git state
echo "Git State:"
echo "  Branch: $(git branch --show-current)"
echo "  Commit: $(git log --oneline -1)"
echo "  Status: $(git status --porcelain | wc -l) uncommitted changes"
```

#### Step 3: Scan Existing Progress

Before starting work, identify what's already been done:

```bash
# List existing task tags
completed_tasks=$(git tag -l 'task/*-committed' | sed 's/task\///' | sed 's/-committed//')

if [[ -n "$completed_tasks" ]]; then
    echo "Found existing completed tasks:"
    echo "$completed_tasks"

    # If resuming, skip completed tasks
    if [[ "$task_id" == "all" ]]; then
        echo "Resuming from next pending task..."
    fi
fi

# Show all task-related tags
echo "Task tags:"
git tag -l 'task/*' | sort
```

**Dry-Run Output for Phase 0**:

If `$dry_run` is "true", output the plan without executing:

```
DRY RUN: Git Workflow Setup
============================
Would create/checkout branch: feat/US-3.4-oauth2-authentication
Would tag: story/US-3.4-start
Would set up remote tracking: origin/feat/US-3.4-oauth2-authentication

Existing progress:
  Completed tasks: None
  Remaining tasks: TASK-1.1, TASK-1.2, TASK-1.3, TASK-1.4
```

---

### Phase 2: Task Implementation

This phase handles single task or parallel task groups based on `$parallel` mode and dependency analysis.

#### Dependency Analysis (for "all" task execution)

When `$task_id` is "all", analyze task dependencies to group independent tasks:

```python
# Pseudo-code for dependency analysis
def analyze_dependencies(tasks_md_path):
    tasks = parse_tasks_md(tasks_md_path)
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

3. **Research Agent (Optional)**

   If `$with_research` is "true", the research agent is invoked automatically via the agent registry.

   ```markdown
   # Research agent invoked automatically (intent: "research-topic")
   # Agent registry routes to: .claude/agents/research.md

   You are the Research Agent for LAZY-DEV-FRAMEWORK.

   ## Task
   $task_description

   ## Research Goals
   - Identify best practices for this task
   - Find relevant libraries/frameworks
   - Note potential pitfalls
   - Gather code examples

   ## Output
   Create research-context.md with findings organized by:
   1. Recommended approach
   2. Code examples
   3. Dependencies needed
   4. Testing strategy
   ```

4. **Coder Agent**

   The coder agent is invoked automatically via the agent registry for implementation tasks.

   ```markdown
   # Coder agent invoked automatically (intent: "implement-code")
   # Agent registry routes to: .claude/agents/coder.md

   You are the Coder Agent for LAZY-DEV-FRAMEWORK.

   ## Task
   $task_content

   ## Research Context (if available)
   $research_context

   ## Acceptance Criteria
   $acceptance_criteria

   ## GitHub Issue
   $github_issue (if present)

   ## Instructions
   1. Implement the functionality described in the task
   2. Follow TDD: Write tests FIRST, then implementation
   3. Add comprehensive type hints
   4. Include docstrings for all functions/classes
   5. Handle edge cases and errors
   6. Ensure cross-OS compatibility

   ## Output
   - Implementation files (*.py)
   - Test files (test_*.py)
   - Updated documentation if needed
   ```

#### Parallel Task Execution

When `$parallel` is "auto" or "true" and multiple independent tasks exist:

1. **Group Independent Tasks**

   Analyze dependencies and create execution groups.

2. **Launch Parallel Coding Agents**

   For each group, launch multiple coder agents in parallel using a single message with multiple Task tool calls:

   ```markdown
   # Message with parallel Task tool invocations
   Launching Group 1: TASK-1.1 and TASK-1.2 in parallel

   [Task tool call 1: Coder agent for TASK-1.1]
   [Task tool call 2: Coder agent for TASK-1.2]
   ```

   Each agent receives:
   - Only its specific task (not entire story)
   - Focused, small-context prompt
   - Minimal token usage

3. **Wait for All Agents to Complete**

   All agents in the group must complete before proceeding to quality pipeline.

**Parallel Execution Benefits**:
- 3-4 independent tasks complete in ~same time as 1 task
- Each agent sees only its task context (lower token cost)
- Better quality through dedicated reviewers per task
- Scalable to 10+ task stories

**Parallel Modes**:
- `--parallel auto` (default): Automatically detect independent tasks and parallelize
- `--parallel true`: Force parallel execution (warns if dependencies detected)
- `--parallel false`: Sequential execution only (useful for debugging)

**Dry-Run Output for Parallel Execution**:

```
DRY RUN: Parallel Execution Plan
=================================
Group 1 (2 tasks in parallel):
  - TASK-1.1: Setup API client [Agent 1 + Reviewer 1]
  - TASK-1.2: Build authentication [Agent 2 + Reviewer 2]

Group 2 (2 tasks in parallel):
  - TASK-1.3: Add validation [Agent 3 + Reviewer 3] (depends on TASK-1.1)
  - TASK-1.4: Error handling [Agent 4 + Reviewer 4] (depends on TASK-1.2)

Would create 4 commits (1 per task)
Estimated time: ~93s (vs ~176s sequential)
Estimated speedup: 1.88x
```

---

### Phase 2: Quality Pipeline (MUST ALL PASS)

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

#### Continue from Failure

If `$continue_from` is set, skip to that stage:

```bash
case "$continue_from" in
    format)
        # Skip research, code gen; start from format
        ;;
    lint)
        # Skip research, code gen, format; start from lint
        ;;
    type)
        # Skip research, code gen, format, lint; start from type
        ;;
    test)
        # Skip research, code gen, format, lint, type; start from test
        ;;
esac
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

### Phase 3: Review & Commit

**ONLY if quality pipeline passes**, proceed to review and commit.

#### Step 1: Reviewer Agent

The reviewer agent is invoked automatically via the agent registry to validate implementation:

```markdown
# Reviewer agent invoked automatically (intent: "review-code")
# Agent registry routes to: .claude/agents/reviewer.md

You are the Reviewer Agent for LAZY-DEV-FRAMEWORK.

## Task Being Reviewed
$task_description

## Code to Review
[All implementation files from coder agent]

## Acceptance Criteria
$acceptance_criteria

## Review Checklist
1. Code matches acceptance criteria
2. Tests cover all functionality
3. Error handling is comprehensive
4. Edge cases are addressed
5. Documentation is clear
6. Cross-OS compatibility maintained
7. Security best practices followed
8. Performance is acceptable

## Output Format
**APPROVED** or **CHANGES REQUESTED**

If APPROVED:
- Brief summary of implementation quality
- Highlight any notable strengths

If CHANGES REQUESTED:
- List specific changes needed
- Reference acceptance criteria not met
- Provide actionable feedback
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

🤖 Generated with [Claude Code](https://claude.com/claude-code)
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

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
fi

# Tag task completion
git tag "task/${task_id}-committed" -f -m "Task ${task_id} committed"
git tag "task/${task_id}-approved" -f -m "Task ${task_id} approved by reviewer"
```

**Commit Message Examples**:

```bash
# Feature implementation
feat(TASK-1.1): implement OAuth2 Google provider

- Add Google OAuth2 strategy with passport.js
- Configure client ID/secret handling via environment
- Implement token validation and refresh logic
- Add comprehensive error handling for auth failures

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

```bash
# Bug fix
fix(TASK-2.3): resolve race condition in cache invalidation

- Add mutex lock for cache write operations
- Implement retry logic for concurrent updates
- Add test coverage for race condition scenario

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

#### Step 3: Verify Git State After Commit

```bash
# Confirm clean working tree
if [[ -n $(git status --porcelain) ]]; then
    echo "WARNING: Uncommitted changes remain after commit"
    git status
fi

# Verify commit created
latest_commit=$(git log --oneline -1)
echo "Created commit: $latest_commit"

# Verify tags created
echo "Tags created:"
git tag -l "task/${task_id}-*"

# Show commit in context
echo "Branch status:"
git log --oneline --graph -5
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

### Phase 4: Final State (After All Tasks)

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

**Final Output (All Tasks - Sequential)**:

```
Story Execution Complete: US-3.4
================================
Branch: feat/US-3.4-oauth2-authentication
Tasks Completed: 4/4
  ✓ TASK-1.1: Setup API client
  ✓ TASK-1.2: Build authentication
  ✓ TASK-1.3: Add validation
  ✓ TASK-1.4: Error handling

Commits: 4
Files Changed: 12
Total Duration: ~176s

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
  ✓ TASK-1.1: Setup API client [Agent 1 + Reviewer 1]
  ✓ TASK-1.2: Build authentication [Agent 2 + Reviewer 2]

Group 2 (parallel): 2 tasks in 41s
  ✓ TASK-1.3: Add validation [Agent 3 + Reviewer 3]
  ✓ TASK-1.4: Error handling [Agent 4 + Reviewer 4]

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

## GitHub CLI Integration

This command supports two modes for task/story resolution: **Directory Structure** (default) and **GitHub Issues** (with `--use-gh` flag).

### Mode Comparison

| Feature | Directory Mode | GitHub Mode |
|---------|---------------|-------------|
| **Story Source** | `./project-management/US-STORY/US-X.X-*/US-story.md` | GitHub issue (specified by `--issue N`) |
| **Task Source** | `./project-management/US-STORY/US-X.X-*/TASKS/TASK-*.md` | Sub-issues with label `parent:N` |
| **Task ID Format** | `TASK-1.1`, `TASK-1.2` | GitHub issue numbers: `43`, `44` |
| **Flag Required** | `--story US-X.X` | `--issue N --use-gh` |
| **Branch Naming** | `feat/US-3.4-oauth2-authentication` | `feat/issue-42-oauth2-authentication` |
| **Commit References** | Task ID only | `Closes #43` GitHub reference |
| **When to Use** | Local development workflow | Remote-first teams, existing GitHub workflows |

### How Tasks Are Fetched from GitHub

When `--use-gh` is enabled:

1. **Story Issue**: Fetched with `gh issue view $issue_number`
   - Title becomes branch name component
   - Body becomes story description

2. **Task Issues**: Fetched with `gh issue list --label "parent:$issue_number"`
   - Each sub-issue represents one task
   - Sub-issue body contains task description and acceptance criteria
   - Sub-issue number becomes task ID

3. **GitHub Issue References**: Extracted from task files
   - Written to task file footer as `GitHub Issue: #N`
   - Used in commit messages as `Closes #N`
   - Automatically closes GitHub issue on merge

### How Issue Numbers Are Extracted

From **Directory Mode** task files:

```markdown
# TASK-1.1: Setup OAuth2 Google provider

Description here...

## Acceptance Criteria
- Criteria here

---
GitHub Issue: #43
```

The footer `GitHub Issue: #43` is extracted and used in commit messages.

From **GitHub Mode** task files:

The issue number is the task ID itself (e.g., task ID `43` → issue `#43`).

### When to Use Each Mode

**Use Directory Mode (default) when:**
- Working locally before creating GitHub issues
- Prototyping features quickly
- Offline development
- Team prefers file-based workflow

**Use GitHub Mode (--use-gh) when:**
- GitHub issues are already created
- Team uses GitHub Projects for tracking
- Need automatic issue closure on PR merge
- Want integrated status updates

### Switching Between Modes

You can switch between modes at any time:

```bash
# Start with directory mode
/lazy create-feature "Add OAuth2"  # Creates US-STORY directory
/lazy task-exec TASK-1.1 --story US-3.4

# Later, create GitHub issues from US-STORY files
gh issue create --title "Setup OAuth2 provider" --body-file ./project-management/US-STORY/US-3.4-*/TASKS/TASK-1.1.md --label "parent:42"

# Continue with GitHub mode
/lazy task-exec 43 --use-gh  # Execute using GitHub issue #43
```

### GitHub CLI Requirements

To use GitHub mode, ensure:

1. **gh CLI installed**: `gh --version`
   - Install: `brew install gh` (macOS) or https://cli.github.com/

2. **Authenticated**: `gh auth status`
   - Login: `gh auth login`

3. **In git repository**: `git status`
   - Must be in repository with GitHub remote

4. **Parent labels configured**: Sub-issues must have `parent:N` label
   - Example: `gh issue edit 43 --add-label "parent:42"`

---

## Error Handling & Recovery

### Task Resolution Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| **Story directory not found** | US-STORY directory missing | Run: `/lazy create-feature` first to create story |
| **Task file not found** | Task doesn't exist in TASKS/ | Check available tasks with error output, use correct task ID |
| **No task files found** | TASKS/ directory empty | Ensure `/lazy create-feature` completed successfully |
| **Story ID required** | Missing --story or --issue flag | Add: `--story US-X.X` or `--issue N` |
| **Invalid story identifier** | Wrong format (not US-X.X) | Use format: `US-3.4` (not `3.4` or `US3.4`) |
| **GitHub issue not found** | Invalid issue number | Run: `gh issue list` to check issue numbers |
| **No sub-issues found** | Missing parent:N label | Add label: `gh issue edit 43 --add-label "parent:42"` |
| **Cannot determine parent issue** | Task missing parent label | Add parent label or use --issue flag |

### Git Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| **Not a git repository** | No .git directory | Run: `git init`, configure remote, retry |
| **Dirty working tree** | Uncommitted changes | Run: `git status`, commit/stash changes, retry |
| **On protected branch** | Currently on main/master/develop | Command auto-creates feature branch |
| **Branch already exists** | Previous work on story | Command checks out existing branch, continues |
| **Detached HEAD** | Not on any branch | Run: `git checkout main`, retry |
| **Commit failed** | Pre-commit hook failed | Fix hook issues, retry commit |
| **Tag already exists** | Task previously attempted | Command overwrites tag with `-f` flag |
| **Remote push rejected** | Upstream changes | Run: `git pull --rebase`, resolve conflicts, retry |

### GitHub CLI Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| **gh CLI not found** | GitHub CLI not installed | Install: `brew install gh` (macOS) or https://cli.github.com/ |
| **Not authenticated** | GitHub CLI not logged in | Run: `gh auth login` |
| **GitHub not configured** | No GitHub remote | Add remote: `git remote add origin <url>` |
| **Issue not found** | Invalid issue number | Check: `gh issue list` for valid issue numbers |
| **Rate limit exceeded** | Too many API requests | Wait ~1 hour or authenticate with: `gh auth login` |

### Quality Pipeline Errors

| Stage | Error | Cause | Recovery |
|-------|-------|-------|----------|
| **Research** | Research timeout | Complex topic | Simplify keywords, retry with `--with-research` |
| **Code Gen** | Agent failed | Invalid acceptance criteria | Fix TASKS.md, retry task-exec |
| **Format** | Black/Ruff mismatch | Code style issues | Auto-fixed, run: `/lazy task-exec TASK-X --continue-from format` |
| **Lint** | Ruff violations | Code quality issues | Review output, fix, retry with `--continue-from lint` |
| **Type Check** | Mypy errors | Missing type hints | Add hints manually, retry with `--continue-from type` |
| **Tests** | Pytest failures | Broken tests | Review failure, fix test or code, retry with `--continue-from test` |
| **Review** | Changes requested | Doesn't meet criteria | Fix issues, re-run `task-exec` from start |

### Parallel Execution Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| **Parallel Group Failure** | One task in group fails quality pipeline | Failed task is retried; other tasks in group continue; group completes when all pass |
| **Dependency Violation** | Task depends on failed task | Block dependent group, fix failing task first, then retry dependent group |

---

## Session Logging

All task execution is logged to `logs/<session-id>/task-exec.json` for tracking and debugging.

### Single Task Log

```json
{
  "task_id": "TASK-1.1",
  "execution_mode": "single",
  "timestamp": "2025-10-25T14:30:00Z",
  "stages": [
    {"stage": "research", "status": "skipped"},
    {"stage": "code_gen", "status": "completed", "duration": 45},
    {"stage": "format", "status": "completed", "changes": 3},
    {"stage": "lint", "status": "completed", "issues": 0},
    {"stage": "type_check", "status": "completed", "errors": 0},
    {"stage": "tests", "status": "completed", "passed": 24, "failed": 0, "coverage": 87},
    {"stage": "review", "status": "approved"},
    {"stage": "commit", "status": "completed", "sha": "abc123"}
  ]
}
```

### Parallel Execution Log

```json
{
  "execution_mode": "parallel",
  "timestamp": "2025-10-25T14:30:00Z",
  "git_state": {
    "repository": "my-project",
    "base_branch": "main",
    "feature_branch": "feat/US-3.4-oauth2-authentication",
    "branch_created": true,
    "story_tag": "story/US-3.4-start",
    "initial_commit": "abc0000",
    "remote_tracking": "origin/feat/US-3.4-oauth2-authentication"
  },
  "dependency_groups": [
    {
      "group_id": 1,
      "parallel_tasks": ["TASK-1.1", "TASK-1.2"],
      "start_time": "2025-10-25T14:30:00Z",
      "end_time": "2025-10-25T14:31:32Z",
      "duration": 92,
      "tasks": [
        {
          "task_id": "TASK-1.1",
          "agent_id": "coder-1",
          "reviewer_id": "reviewer-1",
          "stages": [
            {"stage": "code_gen", "status": "completed", "duration": 45},
            {"stage": "quality_pipeline", "status": "passed", "duration": 28},
            {"stage": "review", "status": "approved", "duration": 12}
          ],
          "commit_sha": "abc123"
        },
        {
          "task_id": "TASK-1.2",
          "agent_id": "coder-2",
          "reviewer_id": "reviewer-2",
          "stages": [
            {"stage": "code_gen", "status": "completed", "duration": 52},
            {"stage": "quality_pipeline", "status": "passed", "duration": 31},
            {"stage": "review", "status": "approved", "duration": 9}
          ],
          "commit_sha": "def456"
        }
      ]
    },
    {
      "group_id": 2,
      "parallel_tasks": ["TASK-1.3", "TASK-1.4"],
      "dependencies": ["TASK-1.1", "TASK-1.2"],
      "start_time": "2025-10-25T14:31:32Z",
      "end_time": "2025-10-25T14:32:45Z",
      "duration": 73,
      "tasks": [
        {
          "task_id": "TASK-1.3",
          "agent_id": "coder-3",
          "reviewer_id": "reviewer-3",
          "commit_sha": "ghi789"
        },
        {
          "task_id": "TASK-1.4",
          "agent_id": "coder-4",
          "reviewer_id": "reviewer-4",
          "commit_sha": "jkl012"
        }
      ]
    }
  ],
  "summary": {
    "total_tasks": 4,
    "total_duration": 165,
    "sequential_estimate": 310,
    "time_saved": 145,
    "speedup_factor": 1.88
  }
}
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
- ✅ Code review approved by reviewer agent
- ✅ Session log created in `logs/<session-id>/task-exec.json`

---

## Implementation Notes

### Agent Invocation Pattern

**Single Task Mode**:
```markdown
# Sequential agent invocations
1. Research Agent (if --with-research)
2. Coder Agent (with research context)
3. Reviewer Agent (with code + criteria)
```

**Parallel Mode**:
```markdown
# Launch multiple agents in parallel using single message with multiple Task tool calls

# Example: 3 independent tasks
Message with parallel Task tool invocations:
  [Task 1: @agent-coder (task=TASK-1.1, context=...)]
  [Task 2: @agent-coder (task=TASK-1.2, context=...)]
  [Task 3: @agent-coder (task=TASK-1.3, context=...)]

# Each coder agent runs independently in parallel
# After all complete, launch reviewers in parallel:

Message with parallel Task tool invocations:
  [Task 1: @agent-reviewer (code=TASK-1.1-impl, criteria=...)]
  [Task 2: @agent-reviewer (code=TASK-1.2-impl, criteria=...)]
  [Task 3: @agent-reviewer (code=TASK-1.3-impl, criteria=...)]

# Benefits:
# - 3 tasks complete in ~time of 1 task
# - Each agent has minimal context (only its task)
# - Lower total token usage vs sequential with full story context
```

### Cross-OS Compatibility

All bash commands must work on Windows (Git Bash), Linux, and macOS:

```bash
# Good: Works on all platforms
git status
git branch --show-current

# Good: Portable path handling
file_path="path/to/file.py"  # Use forward slashes

# Avoid: Platform-specific commands
# ls -la  # Use git commands instead for cross-platform compatibility
```

### Tool Scoping

This command has access to:
- ✅ **Read** - Read source files, test files, configuration
- ✅ **Write** - Create new implementation/test files
- ✅ **Edit** - Modify existing files
- ✅ **Bash** - Run git commands, quality scripts, tests
- ✅ **Task** - Invoke sub-agents (research, coder, reviewer)
- ✅ **Glob** - Find files by pattern
- ✅ **Grep** - Search file contents

Blocked operations:
- ❌ File deletion (filtered by pre_tool_use hook)
- ❌ Destructive git operations (git reset --hard, git push --force)

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
