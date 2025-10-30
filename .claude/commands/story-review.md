---
description: Review story and create PR with all committed tasks
argument-hint: "[STORY-ID or PATH]"
allowed-tools: Read, Bash, Task
model: claude-haiku-4-5-20251001
---

# Story Review Command

<command_purpose>
Review entire user story implementation and create single PR if all tasks are approved.
</command_purpose>

## Introduction

<role>Senior Story Review Architect with expertise in user story validation, acceptance criteria verification, and pull request automation</role>

## Prerequisites

<requirements>
- Git repository with story start tag (e.g., `story/US-3.4-start`)
- All tasks completed and tagged (e.g., `task/TASK-1.1-committed`)
- GitHub CLI (`gh`) installed and authenticated
- Story directory structure: `./project-management/US-STORY/US-X.Y-name/`
- Valid US-story.md file with all task references
- Clean working directory (no uncommitted changes)
</requirements>

## Input Variables

<story_file>$ARGUMENTS</story_file>

<base_branch>
Default: "main"
Can be overridden with: --base develop
</base_branch>

<draft_mode>
Default: "false"
Set to "true" with: --draft true
</draft_mode>

## Memory Graph Usage (Auto)

As you review a story, persist durable outcomes discovered in files and commit summaries:
- Use `mcp__memory__search_nodes` → `create_entities`/`add_observations` → `create_relations` to record owners, endpoints, repo links, and key decisions (dated).
The UserPromptSubmit and PostToolUse hooks auto-hint when these signals are detected. See `.claude/skills/memory-graph/`.

## Main Tasks

### Step 1: Load and Validate Story File

<critical_requirement>
MUST validate story file exists and contains all required sections before proceeding.
</critical_requirement>

<validation_tasks>
- [ ] Check USER-STORY.md exists at provided path
- [ ] Verify file contains required sections:
  - ## User Story
  - ## Acceptance Criteria
  - ## Technical Requirements
  - ## Tasks
- [ ] Parse all task references (TASK-X.Y format)
- [ ] Collect story metadata (ID, title, description)
</validation_tasks>

#### Load Story File

```bash
# Parse input - can be story ID (US-X.Y) or full path
story_input="$ARGUMENTS"

# Check if input is story ID format (US-X.Y)
if [[ "$story_input" =~ ^US-[0-9]+\.[0-9]+$ ]]; then
    # Find story directory
    story_dir=$(find ./project-management/US-STORY -name "${story_input}-*" -type d 2>/dev/null | head -1)

    if [[ -z "$story_dir" ]]; then
        echo "❌ Error: Story ${story_input} not found"
        echo ""
        echo "Available stories:"
        ls -1d ./project-management/US-STORY/US-*/ 2>/dev/null || echo "  (no stories found)"
        echo ""
        echo "Usage: /lazy story-review US-X.Y"
        echo "   or: /lazy story-review ./project-management/US-STORY/US-X.Y-name/US-story.md"
        exit 1
    fi

    story_file="${story_dir}/US-story.md"
    tasks_dir="${story_dir}/TASKS"
    story_id=$(basename "$story_dir" | grep -oP '^US-\d+\.\d+')
else
    # Assume it's a full path to US-story.md
    story_file="$story_input"

    # Validate story file exists
    if [ ! -f "$story_file" ]; then
        echo "❌ Error: Story file not found: $story_file"
        echo ""
        echo "Usage: /lazy story-review US-X.Y"
        echo "   or: /lazy story-review ./project-management/US-STORY/US-X.Y-name/US-story.md"
        exit 1
    fi

    story_dir=$(dirname "$story_file")
    tasks_dir="${story_dir}/TASKS"
    story_id=$(basename "$story_dir" | grep -oP '^US-\d+\.\d+')
fi

# Validate tasks directory exists
if [ ! -d "$tasks_dir" ]; then
    echo "❌ Error: Tasks directory not found: $tasks_dir"
    echo "Story directory may be corrupt"
    echo "Run /lazy create-feature to regenerate"
    exit 1
fi

# Read story content
story_content=$(cat "$story_file")
story_title=$(grep -m1 "^# " "$story_file" | sed 's/^# //')

# Extract GitHub issue number from story file
story_github_issue=$(grep "GitHub Issue: #" "$story_file" | sed 's/.*#//' | head -1)
```

### Step 2: Verify Story State with Git Tags

<critical_requirement>
Use git tags to track story and task completion state. All tasks must be committed before review.
</critical_requirement>

<state_verification>
Story review uses git tags for state management:

**Story Start Tag:**
```bash
# Created by /lazy create-feature
git tag story/oauth2-start
```

**Task Completion Tags:**
```bash
# Created by /lazy task-exec after each task
git tag task/TASK-1.1-committed
git tag task/TASK-1.2-committed
git tag task/TASK-1.3-committed
```

**Verification:**
```bash
# Get all task tags
task_tags=$(git tag -l 'task/*-committed')

# Get story start tag
story_start=$(git tag -l 'story/*-start' | tail -1)

# Verify story start exists
if [ -z "$story_start" ]; then
    echo "❌ Error: No story start tag found"
    echo "Expected: story/{story-id}-start"
    exit 1
fi
```
</state_verification>

#### Collect Task Tags

<task_collection>
- [ ] Get all task files from TASKS directory
- [ ] Get all task tags: `git tag -l 'task/*-committed'`
- [ ] Parse task IDs from tags (extract TASK-X.Y)
- [ ] Verify all tasks are committed
- [ ] Extract GitHub issue numbers from task files
- [ ] Block review if any task is incomplete
</task_collection>

```bash
# Collect all task files
task_files=$(ls ${tasks_dir}/TASK-*.md 2>/dev/null)

if [[ -z "$task_files" ]]; then
    echo "❌ Error: No task files found in ${tasks_dir}"
    echo "Story directory may be corrupt"
    exit 1
fi

# Collect committed and pending tasks
committed_tasks=()
pending_tasks=()
task_github_issues=()

for task_file in $task_files; do
    task_id=$(basename "$task_file" .md)  # e.g., TASK-1.1

    # Check if task is committed (git tag)
    if git tag | grep -q "task/${task_id}-committed"; then
        committed_tasks+=("$task_id")

        # Extract GitHub issue number if present
        github_issue=$(grep "GitHub Issue: #" "$task_file" | sed 's/.*#//' | head -1)
        if [[ -n "$github_issue" ]]; then
            task_github_issues+=("$task_id:$github_issue")
        fi
    else
        pending_tasks+=("$task_id")
    fi
done

# Verify all tasks are committed
if [[ ${#pending_tasks[@]} -gt 0 ]]; then
    echo "❌ Error: Not all tasks are committed"
    echo ""
    echo "Pending tasks:"
    for task in "${pending_tasks[@]}"; do
        echo "  - $task"
    done
    echo ""
    echo "Next steps:"
    echo "  1. Complete missing tasks: /lazy task-exec <TASK-ID>"
    echo "  2. Re-run story review: /lazy story-review ${story_id}"
    exit 1
fi

echo "✅ All ${#committed_tasks[@]} tasks are committed"
```

### Step 3: Collect All Commits Since Story Start

<commit_collection>
Get all commits between story start and current HEAD to include in PR.
</commit_collection>

```bash
# Get commits since story start
commits=$(git log "$story_start"..HEAD --oneline)
commit_count=$(echo "$commits" | wc -l)

# Verify there are commits
if [ $commit_count -eq 0 ]; then
    echo "❌ Error: No commits found since story start"
    echo "Story start: $story_start"
    exit 1
fi

echo "📊 Found $commit_count commits since $story_start"
```

### Step 4: Collect Task Implementations

<implementation_collection>
For each completed task, collect:
- Task file content from TASKS directory
- Implementation files (from git diff)
- Test results (if available)
- GitHub issue links
</implementation_collection>

```bash
# For each task, collect implementation details
all_tasks_summary=""
for task_file in $task_files; do
    task_id=$(basename "$task_file" .md)
    task_title=$(grep -m1 "^# " "$task_file" | sed 's/^# //')
    task_gh_issue=$(grep "GitHub Issue: #" "$task_file" | sed 's/.*#//' | head -1)

    # Get files changed in task commits (approximate by commit messages)
    task_commits=$(git log "$story_start"..HEAD --oneline --grep="$task_id")
    commit_count=$(echo "$task_commits" | wc -l)

    # Collect for review
    all_tasks_summary="${all_tasks_summary}\n${task_id}: ${task_title}"
    if [[ -n "$task_gh_issue" ]]; then
        all_tasks_summary="${all_tasks_summary} (GH Issue #${task_gh_issue})"
    fi
    all_tasks_summary="${all_tasks_summary}\n  Commits: ${commit_count}"
done

echo -e "📋 Task Summary:${all_tasks_summary}"
```

### Step 5: Run Test Suite (if tests exist)

<test_execution>
Run project tests if test runner is available.
</test_execution>

```bash
# Detect test framework and run tests
test_results=""
if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ]; then
    echo "🧪 Running pytest..."
    test_results=$(pytest --tb=short 2>&1 || true)
elif [ -f "package.json" ]; then
    if grep -q '"test"' package.json; then
        echo "🧪 Running npm test..."
        test_results=$(npm test 2>&1 || true)
    fi
fi
```

### Step 6: Invoke Story Review Agent

<critical_requirement>
Invoke the Story Review Agent with complete story context to validate implementation.
</critical_requirement>

<agent_invocation>
Call the Story Review Agent via Task tool with all collected context.
</agent_invocation>

```markdown
You are the **Story Review Agent** for LAZY-DEV-FRAMEWORK.

## Your Role

Review the complete user story implementation and validate that all acceptance criteria are met.

## Story Context

### User Story
$user_story_content

### Acceptance Criteria
$acceptance_criteria

### Technical Requirements
$technical_requirements

## Implementation Context

### Tasks Completed
$all_tasks_list

### Commits Summary
$commits_summary

### Test Results
$test_results

### Files Changed
$files_changed_summary

## Review Checklist

Validate the following:

### 1. Requirements Validation
- [ ] Does implementation match the user story description?
- [ ] Are all acceptance criteria satisfied?
- [ ] Are technical requirements met?
- [ ] Are edge cases handled appropriately?

### 2. Architecture Review
- [ ] Is the architecture sound across all tasks?
- [ ] Are components properly integrated?
- [ ] Is separation of concerns maintained?
- [ ] Are there any architectural smells?

### 3. Security Review
- [ ] Are security requirements satisfied?
- [ ] Is input validation comprehensive?
- [ ] Are authentication/authorization correct?
- [ ] Are there any security vulnerabilities?

### 4. Testing Review
- [ ] Is test coverage comprehensive?
- [ ] Do all tests pass?
- [ ] Are edge cases tested?
- [ ] Is error handling tested?

### 5. Code Quality
- [ ] Is code readable and maintainable?
- [ ] Are naming conventions followed?
- [ ] Is documentation adequate?
- [ ] Are there any code smells?

### 6. Integration Validation
- [ ] Do all tasks work together cohesively?
- [ ] Are there any integration issues?
- [ ] Is the feature complete end-to-end?

## Output Format

Provide your review in this format:

### Review Decision
**[APPROVED / CHANGES_NEEDED]**

### Summary
[2-3 sentence summary of implementation quality]

### Strengths
- [What was done well]
- [Positive aspects]

### Issues Found (if CHANGES_NEEDED)
#### Critical Issues (Must Fix)
- [Issue 1]: [Description, location, impact]
- [Issue 2]: [Description, location, impact]

#### Important Issues (Should Fix)
- [Issue 1]: [Description, location, impact]

#### Minor Issues (Nice to Fix)
- [Issue 1]: [Description, location, impact]

### Recommendations
[Specific recommendations for improvement or next steps]

### Next Steps (if CHANGES_NEEDED)
1. Fix [specific issue]
2. Re-run /lazy task-exec [TASK-ID] to address [issue]
3. Re-run /lazy story-review $story_file

---
End of Review
```

### Step 7: Process Review Results

<review_processing>
Parse review agent output and determine next action.
</review_processing>

```bash
# Parse review decision from agent output
review_decision=$(echo "$agent_output" | grep -A1 "### Review Decision" | tail -1)

if echo "$review_decision" | grep -q "APPROVED"; then
    echo "✅ Story review APPROVED"
    echo "🎯 All acceptance criteria met"
    # Proceed to PR creation
else
    echo "⚠️ Story review needs changes"
    echo ""
    echo "$agent_output"
    exit 0
fi
```

### Step 8: Create Pull Request (if approved)

<pr_creation>
If review is approved, create a single PR containing all story commits.
</pr_creation>

#### Prepare PR Body

```bash
# Generate PR body
cat > pr_body.md <<EOF
# [STORY] ${story_title}

**Story ID**: ${story_id}
**Directory**: \`${story_dir}\`
**GitHub Issue**: #${story_github_issue}

## User Story

$(cat "${story_file}" | grep -A 10 "## User Story" | tail -9)

## Tasks Completed

$(for task_file in ${tasks_dir}/TASK-*.md; do
    task_id=$(basename "$task_file" .md)
    task_title=$(grep "^# " "$task_file" | head -1 | sed 's/^# //')
    task_gh_issue=$(grep "GitHub Issue: #" "$task_file" | sed 's/.*#//' | head -1)

    if [[ -n "$task_gh_issue" ]]; then
        echo "- ✅ [${task_id}] ${task_title} - Closes #${task_gh_issue}"
    else
        echo "- ✅ [${task_id}] ${task_title}"
    fi
done)

## Commits

$(git log --oneline ${story_start}..HEAD)

## Quality Metrics

- **Total Commits**: $commit_count
- **Files Changed**: $(git diff --name-only "$story_start"..HEAD | wc -l)
- **Lines Added**: $(git diff --stat "$story_start"..HEAD | tail -1 | grep -oP '\d+(?= insertion)' || echo "0")
- **Lines Removed**: $(git diff --stat "$story_start"..HEAD | tail -1 | grep -oP '\d+(?= deletion)' || echo "0")
- **Test Coverage**: ${coverage:-N/A}%

## Test Results

\`\`\`
${test_results:-No tests run}
\`\`\`

## Review Status

All validations passed:
- ✅ Requirements met
- ✅ Architecture sound
- ✅ Security validated
- ✅ Tests comprehensive
- ✅ Code quality approved

---
🤖 Generated with [Claude Code](https://claude.com/claude-code)
Story: ${story_id}
Directory: ${story_dir}
EOF
```

#### Create PR with gh CLI

```bash
# Determine if draft mode
draft_flag=""
if [ "$draft_mode" = "true" ]; then
    draft_flag="--draft"
fi

# Create PR
echo "📦 Creating pull request..."
pr_url=$(gh pr create \
  --title "[STORY] $story_title" \
  --body-file pr_body.md \
  --base "$base_branch" \
  --label "automated-pr,reviewed,story:$story_id" \
  $draft_flag)

# Verify PR creation
if [ $? -eq 0 ]; then
    # Get PR number
    pr_number=$(gh pr list --head "$(git branch --show-current)" --json number --jq '.[0].number')

    echo "✅ PR Created: $pr_url"
    echo ""
    echo "📁 Story: ${story_id}"
    echo "   Directory: ${story_dir}"
    echo ""
    echo "📦 PR Details:"
    echo "   Number: #${pr_number}"
    echo "   Title: [STORY] $story_title"
    echo "   Base: $base_branch"
    echo "   Commits: $commit_count"
    echo ""

    # Close GitHub issues
    echo "🔗 Closing GitHub Issues:"

    # Close main story issue
    if [[ -n "$story_github_issue" ]]; then
        gh issue close $story_github_issue --reason completed \
            --comment "Completed in PR #${pr_number}" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "   ✅ #${story_github_issue} - [STORY] ${story_title}"
        fi
    fi

    # Close all task issues
    for task_file in ${tasks_dir}/TASK-*.md; do
        task_id=$(basename "$task_file" .md)
        task_title=$(grep "^# " "$task_file" | head -1 | sed 's/^# //')
        task_gh_issue=$(grep "GitHub Issue: #" "$task_file" | sed 's/.*#//' | head -1)

        if [[ -n "$task_gh_issue" ]]; then
            gh issue close $task_gh_issue --reason completed \
                --comment "Completed in PR #${pr_number}" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "   ✅ #${task_gh_issue} - [${task_id}] ${task_title}"
            fi
        fi
    done

    echo ""
    echo "✅ All related issues closed"
    echo "✅ Ready for merge"
else
    echo "❌ Error: Failed to create PR"
    echo "Check: gh auth status"
    exit 1
fi
```

## Error Handling & Recovery

### Error: Story file not found

```
❌ Error: Story US-3.4 not found

Available stories:
  ./project-management/US-STORY/US-1.1-user-authentication/
  ./project-management/US-STORY/US-2.3-payment-integration/

Usage: /lazy story-review US-X.Y
   or: /lazy story-review ./project-management/US-STORY/US-X.Y-name/US-story.md

Recovery:
  1. Check story ID: ls ./project-management/US-STORY/
  2. Use correct story ID: /lazy story-review US-1.1
  3. Or use full path to US-story.md
```

### Error: Task tags missing

```
❌ Error: Not all tasks are committed

Pending tasks:
  - TASK-1.2
  - TASK-1.3

Next steps:
  1. Run git tag -l 'task/*' to see completed tasks
  2. Execute missing tasks: /lazy task-exec TASK-1.2
  3. Retry: /lazy story-review US-3.4
```

### Error: Story start tag missing

```
❌ Error: No story start tag found
Expected: story/US-X.Y-start

Recovery:
  1. Check if create-feature was run: git tag -l 'story/*'
  2. Create tag manually: git tag story/US-3.4-start $(git log --reverse --oneline | head -1 | cut -d' ' -f1)
  3. Retry: /lazy story-review US-3.4
```

### Error: No commits found

```
❌ Error: No commits found since story start
Story start: story/oauth2-start

Recovery:
  1. Verify story tag: git log story/oauth2-start
  2. Check current branch: git branch --show-current
  3. Ensure tasks were committed (not just completed)
```

### Error: Review changes needed

```
⚠️ Story review needs changes:

Critical Issues:
- TASK-1.3 validation: Missing edge case for declined cards
  Location: src/payments/validator.py:45
  Impact: Invalid cards may be processed

Next steps:
  1. Fix validation in TASK-1.3
  2. Re-run: /lazy task-exec TASK-1.3
  3. Re-review: /lazy story-review US-3.4
```

### Error: Tasks directory not found

```
❌ Error: Tasks directory not found: ./project-management/US-STORY/US-3.4-oauth2/TASKS
Story directory may be corrupt
Run /lazy create-feature to regenerate

Recovery:
  1. Verify story structure: ls -la ./project-management/US-STORY/US-3.4-*/
  2. Check if TASKS directory exists
  3. If missing, regenerate with /lazy create-feature
```

### Error: GitHub issue numbers missing

```
⚠️ Warning: Some task files don't have GitHub issue numbers
This may happen with older stories

Recovery:
  1. Manually add GitHub issues
  2. Or regenerate story with /lazy create-feature (includes gh issue creation)
  3. Issues without numbers won't be auto-closed
```

### Error: gh CLI not found

```
❌ Error: gh command not found

Recovery:
  1. Install GitHub CLI: https://cli.github.com
  2. Authenticate: gh auth login
  3. Verify: gh auth status
  4. Retry: /lazy story-review US-3.4
```

### Error: gh auth failed

```
❌ Error: Not authenticated to GitHub

Recovery:
  1. Run: gh auth login
  2. Follow prompts to authorize
  3. Verify: gh auth status
  4. Retry: /lazy story-review US-3.4
```

### Error: Base branch doesn't exist

```
❌ Error: Base branch 'develop' not found

Recovery:
  1. Check branches: git branch -a
  2. Use correct base: /lazy story-review US-3.4 --base main
  3. Or create branch: git branch develop
```

## Success Criteria

Story review is successful when:

- ✅ Story file is valid with all required sections
- ✅ Story directory structure is correct: `./project-management/US-STORY/US-X.Y-name/`
- ✅ All task files found in TASKS directory
- ✅ All task tags present: `git tag -l 'task/TASK-*-committed'`
- ✅ All commits collected since story start
- ✅ Review agent approved entire implementation
- ✅ All acceptance criteria validated
- ✅ Architecture, security, and testing validated
- ✅ PR created with title `[STORY] {story-name}`
- ✅ PR body contains full story + all tasks + test results + GitHub issues
- ✅ All commits included in PR history
- ✅ PR is on correct base branch
- ✅ All related GitHub issues closed (story + tasks)

## Example Usage

### Basic story review with story ID

```bash
/lazy story-review US-3.4
```

### Review with full path (backward compatible)

```bash
/lazy story-review ./project-management/US-STORY/US-3.4-oauth2-authentication/US-story.md
```

### Review on specific base branch

```bash
/lazy story-review US-3.4 --base develop
```

### Create as draft PR

```bash
/lazy story-review US-3.4 --draft true
```

### Verify story state before review

```bash
# List available stories
ls -1d ./project-management/US-STORY/US-*/

# Check what tasks are completed
git tag -l 'task/*'

# Check story commits
git log story/US-3.4-start..HEAD --oneline

# Then run review
/lazy story-review US-3.4
```

## Session Logging

All activities logged to `logs/<session-id>/story-review.json`:

```json
{
  "story_file": "USER-STORY.md",
  "story_id": "oauth2-auth",
  "base_branch": "main",
  "draft_mode": false,
  "timestamp": "2025-10-25T15:45:00Z",
  "stages": [
    {
      "stage": "load_story",
      "status": "completed",
      "story_title": "Build OAuth2 Authentication"
    },
    {
      "stage": "verify_tags",
      "status": "completed",
      "all_present": true,
      "task_count": 4
    },
    {
      "stage": "collect_commits",
      "status": "completed",
      "commit_count": 7
    },
    {
      "stage": "collect_implementations",
      "status": "completed",
      "files_changed": 15
    },
    {
      "stage": "run_tests",
      "status": "completed",
      "test_result": "passed"
    },
    {
      "stage": "review",
      "status": "approved",
      "agent": "story-review-agent"
    },
    {
      "stage": "pr_creation",
      "status": "completed",
      "pr_url": "https://github.com/org/repo/pull/42",
      "pr_number": 42
    }
  ],
  "result": {
    "approved": true,
    "pr_url": "https://github.com/org/repo/pull/42",
    "tasks_included": ["TASK-1.1", "TASK-1.2", "TASK-1.3", "TASK-1.4"],
    "commits_included": 7,
    "files_changed": 15
  }
}
```

## Integration with Other Commands

### After /lazy create-feature

```bash
# create-feature creates story directory and sets start tag
/lazy create-feature "Add OAuth2 authentication"
# Creates: ./project-management/US-STORY/US-3.4-oauth2-authentication/
#          US-story.md, TASKS/TASK-*.md files
#          GitHub issues for story and tasks
# Sets tag: story/US-3.4-start

# Execute all tasks
/lazy task-exec TASK-1.1
/lazy task-exec TASK-1.2
/lazy task-exec TASK-1.3

# Review and create PR (using story ID)
/lazy story-review US-3.4
```

### After /lazy task-exec

```bash
# Each task-exec sets a completion tag
/lazy task-exec TASK-1.1
# Sets tag: task/TASK-1.1-committed

# story-review uses these tags to verify completion
/lazy story-review US-3.4
```

### Workflow Summary

```
/lazy create-feature
      ↓
  Creates ./project-management/US-STORY/US-X.Y-name/
  story/US-X.Y-start tag created
  GitHub issues created
      ↓
/lazy task-exec TASK-1.1 → task/TASK-1.1-committed
/lazy task-exec TASK-1.2 → task/TASK-1.2-committed
/lazy task-exec TASK-1.3 → task/TASK-1.3-committed
      ↓
/lazy story-review US-X.Y
      ↓
  Verify all tags present
      ↓
  Collect all commits
      ↓
  Review Agent validation
      ↓
  Create PR (if approved)
      ↓
  Close GitHub issues (story + tasks)
```

## Notes

- Story review is **read-only** - no file modifications during review
- All validation happens through git tags (immutable markers)
- Review agent has complete context (story + tasks + implementations + tests)
- PR creation is automatic only if review is approved
- Draft mode allows additional manual review before merge
- Story state tracking enables iterative review (fix tasks, re-review)
- Accepts both story ID (US-X.Y) and full path for backward compatibility
- Automatically closes all related GitHub issues (story + all tasks)
- Works with new directory structure: `./project-management/US-STORY/US-X.Y-name/`
- Task files are individual TASK-*.md files in TASKS subdirectory
- GitHub issue numbers extracted from story and task files
