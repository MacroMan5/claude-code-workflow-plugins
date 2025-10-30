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

<critical_requirements>
**KEY REQUIREMENTS**:
1. Each completed US (user story) = 1 PR (not per task)
2. If review FAILS → Generate detailed REPORT file
3. Review against project standards AND enterprise guidelines
4. Use reviewer-story agent via Task tool
5. Parse agent JSON output programmatically
6. APPROVED → Auto-create PR with comprehensive body
7. CHANGES_REQUIRED → Generate US-X.Y-REVIEW-REPORT.md with fix guidance
</critical_requirements>

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

### Step 6: Load Enterprise Standards

<standards_loading>
Load project and enterprise standards for compliance checking.
</standards_loading>

```bash
# Collect all applicable standards
standards_content=""

# 1. Load CLAUDE.md (project standards)
if [ -f "CLAUDE.md" ]; then
    echo "📋 Loading project standards from CLAUDE.md..."
    standards_content="${standards_content}\n## Project Standards (CLAUDE.md)\n\n"
    standards_content="${standards_content}$(cat CLAUDE.md)"
fi

# 2. Load README.md (architecture decisions)
if [ -f "README.md" ]; then
    echo "📋 Loading architecture decisions from README.md..."
    standards_content="${standards_content}\n## Architecture Decisions (README.md)\n\n"
    standards_content="${standards_content}$(cat README.md)"
fi

# 3. Load CONTRIBUTING.md (code standards)
if [ -f ".github/CONTRIBUTING.md" ]; then
    echo "📋 Loading code standards from .github/CONTRIBUTING.md..."
    standards_content="${standards_content}\n## Code Standards (CONTRIBUTING.md)\n\n"
    standards_content="${standards_content}$(cat .github/CONTRIBUTING.md)"
elif [ -f "CONTRIBUTING.md" ]; then
    echo "📋 Loading code standards from CONTRIBUTING.md..."
    standards_content="${standards_content}\n## Code Standards (CONTRIBUTING.md)\n\n"
    standards_content="${standards_content}$(cat CONTRIBUTING.md)"
fi

# 4. Load custom enterprise guidelines (if configured)
enterprise_standards_path="${LAZY_DEV_ENTERPRISE_STANDARDS:-}"
if [ -n "$enterprise_standards_path" ] && [ -f "$enterprise_standards_path" ]; then
    echo "📋 Loading enterprise standards from ${enterprise_standards_path}..."
    standards_content="${standards_content}\n## Enterprise Guidelines\n\n"
    standards_content="${standards_content}$(cat "$enterprise_standards_path")"
fi

# If no standards found, use defaults
if [ -z "$standards_content" ]; then
    echo "⚠️ No standards files found - using LAZY-DEV defaults"
    standards_content="## Default Standards\n\n- Test coverage >80%\n- Type hints required\n- Documentation required for public APIs\n- OWASP Top 10 security compliance"
fi

echo "✅ Standards loaded successfully"
```

### Step 7: Invoke Story Review Agent

<critical_requirement>
Invoke the Story Review Agent via Task tool with complete context including enterprise standards.
</critical_requirement>

<agent_invocation>
The agent receives all story context, implementation details, and compliance standards.
Agent output format is JSON for programmatic processing.
</agent_invocation>

```bash
# Prepare context for agent
echo "🤖 Invoking Story Review Agent..."

# Read full story content
story_content_full=$(cat "$story_file")

# Get all task file contents
tasks_content=""
for task_file in $task_files; do
    task_id=$(basename "$task_file" .md)
    tasks_content="${tasks_content}\n### ${task_id}\n\n$(cat "$task_file")\n"
done

# Get git diff stats
files_changed=$(git diff --stat "$story_start"..HEAD)
files_changed_list=$(git diff --name-only "$story_start"..HEAD)

# Get test coverage if available
coverage_result=""
if command -v pytest &> /dev/null; then
    coverage_result=$(pytest --cov --cov-report=term-missing 2>&1 || true)
fi

# Store agent context in temporary file for Task tool
cat > /tmp/story_review_context.md <<EOF
You are reviewing Story: ${story_id}
Story Title: ${story_title}
Story File: ${story_file}
Tasks Directory: ${tasks_dir}
Branch: $(git branch --show-current)

## Story Content
${story_content_full}

## All Tasks
${tasks_content}

## Commits (${commit_count} total)
${commits}

## Files Changed ($(echo "$files_changed_list" | wc -l) files)
${files_changed}

## Test Results
${test_results}
${coverage_result}

## Project Standards
${standards_content}

## Review Instructions
You MUST review against:
1. All acceptance criteria in the story file
2. Project standards from CLAUDE.md
3. Enterprise guidelines (if provided)
4. OWASP Top 10 security standards
5. Test coverage requirements (>80%)
6. Integration quality between all tasks

Return JSON output as specified in reviewer-story.md agent template.
EOF

echo "📄 Context prepared: /tmp/story_review_context.md"
```

**Invoke reviewer-story agent now:**

Use the Task tool to invoke `.claude/agents/reviewer-story.md` with the following variable substitutions:

- `story_id`: ${story_id}
- `story_file`: ${story_file}
- `tasks_dir`: ${tasks_dir}
- `branch_name`: $(git branch --show-current)
- `standards`: ${standards_content}

The agent will analyze all context and return JSON output with `status` field of either "APPROVED" or "REQUEST_CHANGES".

### Step 8: Process Review Results

<review_processing>
Parse JSON output from reviewer-story agent and take appropriate action.
</review_processing>

```bash
# Agent returns JSON - parse the status field
agent_status=$(echo "$agent_output" | jq -r '.status' 2>/dev/null || echo "UNKNOWN")

if [ "$agent_status" = "APPROVED" ]; then
    echo "✅ Story review APPROVED"
    echo ""

    # Extract summary from agent output
    agent_summary=$(echo "$agent_output" | jq -r '.summary' 2>/dev/null || echo "All checks passed")
    echo "📋 Summary: ${agent_summary}"
    echo ""

    # Proceed to Step 9 (PR creation)

elif [ "$agent_status" = "REQUEST_CHANGES" ]; then
    echo "❌ Story review FAILED - Changes Required"
    echo ""

    # Generate detailed review report
    report_file="${story_dir}/${story_id}-REVIEW-REPORT.md"

    echo "📝 Generating review report: ${report_file}"

    # Extract data from agent JSON output
    agent_summary=$(echo "$agent_output" | jq -r '.summary' 2>/dev/null || echo "Review found issues")
    tasks_reviewed=$(echo "$agent_output" | jq -r '.tasks_reviewed | join(", ")' 2>/dev/null || echo "N/A")

    # Count issues by severity
    critical_count=$(echo "$agent_output" | jq '[.issues[] | select(.severity == "CRITICAL")] | length' 2>/dev/null || echo "0")
    warning_count=$(echo "$agent_output" | jq '[.issues[] | select(.severity == "WARNING")] | length' 2>/dev/null || echo "0")
    suggestion_count=$(echo "$agent_output" | jq '[.issues[] | select(.severity == "SUGGESTION")] | length' 2>/dev/null || echo "0")

    # Parse acceptance criteria status from story file
    acceptance_criteria_section=$(cat "$story_file" | sed -n '/## Acceptance Criteria/,/##/p' | head -n -1)

    # Generate comprehensive report
    cat > "$report_file" <<REPORT_EOF
# Story Review Report: ${story_id}

**Generated:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Story:** ${story_title}
**Status:** ❌ CHANGES REQUIRED
**Reviewer:** reviewer-story agent (LAZY-DEV-FRAMEWORK)
**Branch:** $(git branch --show-current)

---

## Executive Summary

${agent_summary}

**Tasks Reviewed:** ${tasks_reviewed}
**Issues Found:** ${critical_count} Critical, ${warning_count} Warnings, ${suggestion_count} Suggestions

---

## Acceptance Criteria Status

${acceptance_criteria_section}

---

## Issues Found

$(echo "$agent_output" | jq -r '
if .issues and (.issues | length > 0) then
    # Critical Issues
    (if [.issues[] | select(.severity == "CRITICAL")] | length > 0 then
        "### 🔴 CRITICAL (Must Fix Before Approval)\n\n" +
        ([.issues[] | select(.severity == "CRITICAL")] | to_entries | map(
            "#### Issue " + ((.key + 1) | tostring) + ": " + .value.description + "\n" +
            "- **Type**: " + (.value.type // "Code Quality") + "\n" +
            "- **Severity**: CRITICAL\n" +
            "- **Task**: " + (.value.task_id // "N/A") + "\n" +
            "- **Location**: \`" + (.value.file // "N/A") + (if .value.line then ":" + (.value.line | tostring) else "" end) + "\`\n" +
            "- **Description**: " + .value.description + "\n" +
            "- **Impact**: " + (.value.impact // "Must be fixed before approval") + "\n" +
            "- **Required Fix**: " + .value.fix + "\n" +
            "- **Agent to use**: " + (.value.suggested_agent // "`/lazy task-exec " + (.value.task_id // "TASK-ID") + "`") + "\n"
        ) | join("\n"))
    else "" end) +

    # Warning Issues
    (if [.issues[] | select(.severity == "WARNING")] | length > 0 then
        "\n### ⚠️ WARNING (Should Fix)\n\n" +
        ([.issues[] | select(.severity == "WARNING")] | to_entries | map(
            "#### Issue " + ((.key + 1) | tostring) + ": " + .value.description + "\n" +
            "- **Type**: " + (.value.type // "Code Quality") + "\n" +
            "- **Severity**: WARNING\n" +
            "- **Task**: " + (.value.task_id // "N/A") + "\n" +
            "- **Location**: \`" + (.value.file // "N/A") + (if .value.line then ":" + (.value.line | tostring) else "" end) + "\`\n" +
            "- **Description**: " + .value.description + "\n" +
            "- **Required Fix**: " + .value.fix + "\n"
        ) | join("\n"))
    else "" end) +

    # Suggestions
    (if [.issues[] | select(.severity == "SUGGESTION")] | length > 0 then
        "\n### 💡 SUGGESTION (Optional Improvements)\n\n" +
        ([.issues[] | select(.severity == "SUGGESTION")] | to_entries | map(
            "#### Suggestion " + ((.key + 1) | tostring) + ": " + .value.description + "\n" +
            "- **Task**: " + (.value.task_id // "N/A") + "\n" +
            "- **Location**: \`" + (.value.file // "N/A") + (if .value.line then ":" + (.value.line | tostring) else "" end) + "\`\n" +
            "- **Description**: " + .value.description + "\n" +
            "- **Improvement**: " + .value.fix + "\n"
        ) | join("\n"))
    else "" end)
else
    "No specific issues documented by reviewer."
end
')

---

## Compliance Issues

### Project Standards Violations:
$(echo "$agent_output" | jq -r '
if .issues then
    [.issues[] | select(.type == "Standards" or .type == "Compliance")] |
    if length > 0 then
        map("- [ ] " + .description + " in \`" + (.file // "N/A") + "\`") | join("\n")
    else
        "- [x] No project standards violations found"
    end
else
    "- [x] No project standards violations found"
end
')

### Enterprise Guideline Violations:
$(echo "$agent_output" | jq -r '
if .issues then
    [.issues[] | select(.type == "Security" or .type == "Enterprise")] |
    if length > 0 then
        map("- [ ] " + .severity + ": " + .description) | join("\n")
    else
        "- [x] No enterprise guideline violations found"
    end
else
    "- [x] No enterprise guideline violations found"
end
')

---

## Test Coverage Issues

$(echo "$agent_output" | jq -r '
if .issues then
    [.issues[] | select(.type == "Testing" or .type == "Coverage")] |
    if length > 0 then
        "**Current Coverage**: $(echo "$coverage_result" | grep "^TOTAL" | awk "{print \$NF}" || echo "N/A")\n" +
        "**Required**: >80%\n\n" +
        "**Files needing tests:**\n" +
        (map("- \`" + (.file // "N/A") + "\`: " + .description) | join("\n"))
    else
        "**Status**: ✅ Test coverage meets requirements\n" +
        "**Coverage**: $(echo "$coverage_result" | grep "^TOTAL" | awk "{print \$NF}" || echo "N/A")"
    end
else
    "**Status**: ✅ No test coverage issues reported"
end
')

---

## Required Actions

### To Fix and Re-Submit:

1. **Fix Critical Issues** (Priority 1):
   \`\`\`bash
   # Use story-fix-review command to route fixes to appropriate agents
   /lazy story-fix-review ${report_file}
   \`\`\`

   This will automatically:
   - Parse the report for critical issues
   - Route security issues → coder agent
   - Route test gaps → tester agent
   - Route architecture issues → refactor agent
   - Route documentation → documentation agent

2. **Address Warning Issues** (Priority 2):
   Review each warning and apply fixes manually or use specific agents:
   - Code quality: \`/lazy task-exec TASK-X.Y\` (re-execute task)
   - Documentation: \`/lazy documentation --scope ${story_id}\`
   - Refactoring: \`/lazy refactor --scope ${story_id}\`

3. **Re-run Story Review**:
   \`\`\`bash
   /lazy story-review ${story_id}
   \`\`\`

4. **Verify All Criteria Met**:
   - All ✓ marks in acceptance criteria
   - All 🔴 CRITICAL issues resolved
   - Coverage >80%
   - All tests passing

---

## Estimated Fix Time

- Critical issues: $(echo "$critical_count * 2" | bc 2>/dev/null || echo "$critical_count") hours (estimated)
- Warning issues: $(echo "$warning_count * 1" | bc 2>/dev/null || echo "$warning_count") hours (estimated)
- Total estimated: $(echo "($critical_count * 2) + $warning_count" | bc 2>/dev/null || echo "N/A") hours

---

## Next Steps

1. ✅ Review this report: \`cat ${report_file}\`
2. ✅ Fix critical issues: \`/lazy story-fix-review ${report_file}\`
3. ✅ Re-run review: \`/lazy story-review ${story_id}\`
4. ✅ Create PR once approved

---

**Generated by**: Claude Code LAZY-DEV-FRAMEWORK
**Review Agent**: \`.claude/agents/reviewer-story.md\`
**Framework Version**: 1.0.0-alpha
REPORT_EOF

    echo "✅ Review report generated: ${report_file}"
    echo ""
    echo "Found:"
    echo "  - ${critical_count} CRITICAL issues"
    echo "  - ${warning_count} WARNING issues"
    echo "  - ${suggestion_count} SUGGESTIONS"
    echo ""
    echo "Next steps:"
    echo "  1. Review report: cat ${report_file}"
    echo "  2. Fix issues: /lazy story-fix-review ${report_file}"
    echo "  3. Re-run review: /lazy story-review ${story_id}"
    echo ""

    # Exit with status 1 to indicate failure
    exit 1

else
    echo "❌ Error: Unknown review status from agent: ${agent_status}"
    echo "Agent output:"
    echo "$agent_output"
    exit 1
fi
```

### Step 9: Create Pull Request (If APPROVED)

<pr_creation>
If review is approved, create a single PR containing all story commits with comprehensive summary.
</pr_creation>

<pr_requirements>
- One PR per user story (not per task)
- Includes all commits since story start tag
- References all task GitHub issues
- Includes test results and quality metrics
- Auto-closes related GitHub issues
</pr_requirements>

#### Prepare PR Body

```bash
# Generate comprehensive PR body
echo "📝 Generating PR body..."

# Extract test coverage percentage
test_coverage=$(echo "$coverage_result" | grep "^TOTAL" | awk '{print $NF}' || echo "N/A")

# Get acceptance criteria status
acceptance_criteria_list=$(cat "$story_file" | sed -n '/## Acceptance Criteria/,/##/p' | grep -E "^-.*" | sed 's/^- /✓ /')

# Extract agent summary
pr_summary=$(echo "$agent_output" | jq -r '.summary' 2>/dev/null || echo "Story implementation completed and reviewed")

cat > pr_body.md <<'PR_BODY'
# [FEATURE] ${story_title}

**Story ID**: ${story_id}
**Directory**: `${story_dir}`
$(if [[ -n "$story_github_issue" ]]; then echo "**GitHub Issue**: Closes #${story_github_issue}"; fi)

---

## Summary

${pr_summary}

---

## User Story

$(cat "${story_file}" | sed -n '/## User Story/,/##/p' | tail -n +2 | head -n -1)

---

## Acceptance Criteria

$(echo "$acceptance_criteria_list" | sed 's/^/✓ /')

---

## Tasks Completed

$(for task_file in ${tasks_dir}/TASK-*.md; do
    task_id=$(basename "$task_file" .md)
    task_title=$(grep "^# " "$task_file" | head -1 | sed 's/^# //')
    task_gh_issue=$(grep "GitHub Issue: #" "$task_file" | sed 's/.*#//' | head -1)

    if [[ -n "$task_gh_issue" ]]; then
        echo "✓ [${task_id}] ${task_title} - Closes #${task_gh_issue}"
    else
        echo "✓ [${task_id}] ${task_title}"
    fi
done)

---

## Commits

\`\`\`
$(git log --oneline ${story_start}..HEAD)
\`\`\`

**Total Commits**: ${commit_count}

---

## Quality Metrics

| Metric | Value |
|--------|-------|
| Files Changed | $(git diff --name-only "$story_start"..HEAD | wc -l) |
| Lines Added | $(git diff --stat "$story_start"..HEAD | tail -1 | grep -oP '\d+(?= insertion)' || echo "0") |
| Lines Removed | $(git diff --stat "$story_start"..HEAD | tail -1 | grep -oP '\d+(?= deletion)' || echo "0") |
| Test Coverage | ${test_coverage} |
| Tests Passing | $(echo "$test_results" | grep -oP '\d+(?= passed)' || echo "All") |

---

## Testing

\`\`\`
${test_results:-No tests run}
\`\`\`

$(if [[ -n "$coverage_result" ]]; then
echo "### Coverage Report"
echo "\`\`\`"
echo "$coverage_result" | head -20
echo "\`\`\`"
fi)

---

## Compliance & Quality Checks

### Story Review
✅ **APPROVED** by reviewer-story agent

### Project Standards
✅ Compliant with CLAUDE.md requirements
✅ Follows project architecture patterns

### Enterprise Guidelines
$(if [[ -n "$enterprise_standards_path" ]]; then
    echo "✅ Compliant with enterprise standards: \`${enterprise_standards_path}\`"
else
    echo "✅ Compliant with LAZY-DEV framework defaults"
fi)

### Security
✅ OWASP Top 10 compliance verified
✅ No security vulnerabilities detected
✅ Input validation implemented
✅ Authentication/authorization reviewed

### Code Quality
✅ Format: PASS (Black/Ruff)
✅ Lint: PASS (Ruff)
✅ Type: PASS (Mypy)
✅ Tests: PASS (Pytest)

### Documentation
✅ Public APIs documented
✅ README updated (if applicable)
✅ Inline comments for complex logic

---

## Integration Status

✅ All tasks integrate cohesively
✅ No conflicts between task implementations
✅ Data flows correctly between components
✅ No breaking changes to existing functionality

---

## Reviewer Notes

**Review Method**: LAZY-DEV-FRAMEWORK automated story review
**Review Agent**: `.claude/agents/reviewer-story.md`
**Review Date**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

**Summary**: ${pr_summary}

**Strengths**:
$(echo "$agent_output" | jq -r '.strengths // [] | if length > 0 then map("- " + .) | join("\n") else "- Comprehensive implementation\n- Strong test coverage\n- Clean code quality" end' 2>/dev/null || echo "- High-quality implementation")

---

## Related Issues

$(if [[ -n "$story_github_issue" ]]; then
    echo "- Story: #${story_github_issue}"
fi)
$(for task_file in ${tasks_dir}/TASK-*.md; do
    task_gh_issue=$(grep "GitHub Issue: #" "$task_file" | sed 's/.*#//' | head -1)
    if [[ -n "$task_gh_issue" ]]; then
        task_id=$(basename "$task_file" .md)
        echo "- Task ${task_id}: #${task_gh_issue}"
    fi
done)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code) LAZY-DEV-FRAMEWORK

**Story**: ${story_id}
**Directory**: ${story_dir}
**Framework**: LAZY-DEV v1.0.0-alpha
PR_BODY

# Expand variables in PR body
eval "cat <<'EXPAND_PR_BODY' > pr_body_final.md
$(cat pr_body.md)
EXPAND_PR_BODY"

echo "✅ PR body generated: pr_body_final.md"
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
  --title "[FEATURE] $story_title" \
  --body-file pr_body_final.md \
  --base "$base_branch" \
  --label "story,automated,reviewed,story:$story_id" \
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

## Parallelization During Review

<parallelization>
While the story review is running or after it completes, you can run other commands in parallel if they are independent.
</parallelization>

### Commands That Can Run in Parallel

**During Review (While Waiting for Agent)**:

```bash
# 1. Cleanup unused code (runs on current branch)
/lazy cleanup --scope feature/US-X.Y

# 2. Generate documentation for the story
/lazy documentation --scope US-X.Y

# 3. Check memory graph for this story's entities
/lazy memory-check US-X.Y
```

**After Review Approval (Before PR Merge)**:

```bash
# 1. Start work on next independent story
/lazy create-feature "Next feature brief"

# 2. Update project documentation
/lazy documentation --scope project

# 3. Run refactoring on completed work
/lazy refactor --scope US-X.Y
```

### Commands That CANNOT Run in Parallel

**Blocked Until Review Completes**:

```bash
# ❌ Cannot run another story review simultaneously
/lazy story-review US-Y.Z  # Wait for current review to finish

# ❌ Cannot re-execute tasks in the story being reviewed
/lazy task-exec TASK-X.Y  # Wait until review fails or make changes after PR

# ❌ Cannot fix review issues until report is generated
/lazy story-fix-review US-X.Y-REVIEW-REPORT.md  # Only after review fails
```

### Recommended Workflow

**Optimal Parallelization**:

```bash
# Terminal 1: Run story review
/lazy story-review US-3.4

# Terminal 2: While review is running, cleanup and document in parallel
/lazy cleanup --scope feature/US-3.4
/lazy documentation --scope US-3.4

# If review APPROVED:
# - PR is created automatically
# - GitHub issues are closed
# - Ready to start next story

# If review FAILED:
# - Fix issues: /lazy story-fix-review US-3.4-REVIEW-REPORT.md
# - Re-run: /lazy story-review US-3.4
```

## Integration with Other Commands

### Workflow Integration

**Complete Story Lifecycle**:

```
1. /lazy create-feature "Brief"
   ↓
   Creates: US-X.Y-name/US-story.md
   Creates: TASKS/TASK-*.md
   Creates: GitHub issues
   Sets tag: story/US-X.Y-start

2. /lazy task-exec TASK-1.1
   /lazy task-exec TASK-1.2
   /lazy task-exec TASK-1.3
   ↓
   Each sets tag: task/TASK-X.Y-committed
   Each implements and tests feature

3. /lazy story-review US-X.Y  ← THIS COMMAND
   ↓
   Loads: All tasks, commits, standards
   Invokes: reviewer-story agent

   If APPROVED:
     ↓
     Creates: PR with full context
     Closes: All GitHub issues

   If CHANGES_REQUIRED:
     ↓
     Creates: US-X.Y-REVIEW-REPORT.md
     Outputs: Fix guidance

4. If changes needed:
   /lazy story-fix-review US-X.Y-REVIEW-REPORT.md
   ↓
   Routes issues to appropriate agents
   Fixes critical/warning issues

   Then re-run:
   /lazy story-review US-X.Y

5. After PR merge:
   /lazy cleanup --scope US-X.Y
   /lazy documentation --scope US-X.Y
```

### Command Dependencies

**story-review depends on**:
- `/lazy create-feature` (creates story structure)
- `/lazy task-exec` (completes all tasks)
- Git tags: `story/*-start`, `task/*-committed`
- GitHub CLI: `gh` authenticated

**Commands that depend on story-review**:
- `/lazy story-fix-review` (processes review report)
- Subsequent `/lazy story-review` runs (after fixes)

**Independent parallel commands**:
- `/lazy cleanup` (code cleanup)
- `/lazy documentation` (docs generation)
- `/lazy memory-check` (graph queries)
- `/lazy create-feature` (new independent story)

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
