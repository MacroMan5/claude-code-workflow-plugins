---
description: Create user story and tasks from feature brief
argument-hint: "[feature-description] [--role pm|techlead] [--output-dir DIR]"
allowed-tools: Read, Write, Task, Bash
model: claude-haiku-4-5-20251001
---

# Create Feature: Transform Brief to User Story + Tasks

## Introduction

Transform a brief feature description into a complete user story with individual task files in a structured directory. This command receives enriched input from the pre-prompt-enrichment hook, which adds architecture, security, testing, and edge case considerations automatically.

**Output Structure:**
```
./project-management/US-STORY/US-{STORY_ID}-{story-name}/
├── US-story.md              # Main user story (maps to GitHub issue)
└── TASKS/
    ├── TASK-1.1.md          # Individual task files (map to sub-issues)
    ├── TASK-1.2.md
    └── TASK-1.3.md
```

**GitHub Integration:**
After creating files, **ALWAYS** creates GitHub issues for the story and all tasks automatically.

## Memory Graph Usage (Auto)

When a feature introduces new entities (teams, services, APIs) or durable facts (owners, endpoints, repo links), use the Memory MCP tools to persist them for later discovery:
- Search first, then create entities and add observations; link related entities.
See `.claude/skills/memory-graph/` for playbooks. The UserPromptSubmit hook auto-hints this when signals are detected.

## Feature Description

<feature_description>
$ARGUMENTS
</feature_description>

## Main Tasks

### 1. Parse Arguments and Validate Context

<thinking>
First, I need to understand what the user wants to build and extract any optional parameters. The brief has already been enriched by the pre-prompt hook, so I should have comprehensive context.
</thinking>

**Parse Input:**
- [ ] Extract feature brief from `$ARGUMENTS`
- [ ] Parse optional `--role` flag (pm|techlead) - defaults to "pm"
- [ ] Parse optional `--output-dir` flag - defaults to `./project-management/US-STORY/US-{ID}-{name}/`
- [ ] Verify the enriched brief contains architecture/security/testing context

**Generate Story ID:**
- [ ] Scan `./project-management/US-STORY/` directory for existing US-* folders
- [ ] Extract all existing story IDs (format: US-X.Y)
- [ ] Find highest major.minor number (e.g., if US-3.2 exists, next is US-3.3)
- [ ] If no stories exist, start with US-1.1
- [ ] Generate new story ID: US-{next_number}

**Create Directory Structure:**
- [ ] Generate story name slug from feature brief (lowercase, alphanumeric, max 50 chars)
- [ ] Create directory: `./project-management/US-STORY/US-{ID}-{story-name}/`
- [ ] Create subdirectory: `./project-management/US-STORY/US-{ID}-{story-name}/TASKS/`
- [ ] Set proper permissions (755 for directories)

**Validate Context:**
- [ ] Check if in git repository: `git rev-parse --is-inside-work-tree`
- [ ] Get current project structure (if available): check for CLAUDE.md, README.md, package.json, etc.
- [ ] Identify project type (web app, API, library, etc.) from context
- [ ] Load any existing architecture documentation
- [ ] Check if `gh` CLI is installed: `which gh` (Unix) or `where gh` (Windows)
- [ ] Check if `gh` is authenticated: `gh auth status`

**Error Handling:**
- If enrichment failed (missing ANTHROPIC_API_KEY): Return error "Pre-prompt enrichment failed. Check ANTHROPIC_API_KEY in environment."
- If git not initialized: Warn "Not in git repository. Consider running `git init` for better tracking."
- If gh not installed: Return error "GitHub CLI not installed. Install with: brew install gh (or download from https://cli.github.com)"
- If gh not authenticated: Return error "GitHub CLI not authenticated. Run: gh auth login"
- If directory creation fails: Return error "Could not create directory structure. Check permissions."

### 2. Load Project Context

<thinking>
To create relevant user stories and tasks, I need to understand the project's architecture, conventions, and existing patterns. This helps the PM agent generate context-aware deliverables.
</thinking>

**Gather Project Information:**
- [ ] Read CLAUDE.md (if exists) for project context and conventions
- [ ] Read README.md (if exists) for project overview
- [ ] Check for existing US-story.md files in ./project-management/US-STORY/ to understand format preferences
- [ ] Check for existing TASK-*.md files to understand task breakdown patterns
- [ ] Identify testing framework (pytest, jest, etc.) from project files
- [ ] Identify code style preferences (Black, Prettier, etc.)

**Extract Technical Constraints:**
- [ ] Programming languages used
- [ ] Frameworks and libraries
- [ ] Testing requirements
- [ ] Security policies
- [ ] Performance requirements
- [ ] Deployment constraints

### 3. Invoke Project Manager Agent

<thinking>
Now I'll call the PM agent with the enriched brief and project context. The agent will create detailed USER-STORY.md and TASKS.md files following best practices.
</thinking>

**Prepare Agent Input:**
- [ ] Combine enriched brief with project context
- [ ] Set role parameter (pm or techlead)
- [ ] Prepare constraints object with technical requirements
- [ ] Format input for agent consumption

**Call Agent via Task Tool:**

Use the Task tool with `subagent_type="project-manager"` to invoke the PM agent:

```markdown
Call @agent-project-manager with:

**Input Parameters:**
- $role: "{pm|techlead}"
- $description: "{enriched_feature_brief}"
- $constraints: "{technical_constraints_from_project}"
- $project_context: "{CLAUDE.md + README.md + existing_patterns}"

**Expected Deliverables:**
1. US-story.md with:
   - Story ID (US-{ID})
   - Title
   - Description
   - Acceptance Criteria
   - Security Considerations
   - Testing Requirements
   - Architecture Notes

2. Individual TASK-*.md files (one per task) with:
   - Task ID (TASK-1.1, TASK-1.2, etc.)
   - Task title and description
   - Dependencies between tasks
   - Estimated complexity
   - Required skills
   - Placeholder for GitHub issue number
```

**Agent Execution:**
- [ ] Invoke Task tool with project-manager subagent type
- [ ] Wait for agent completion (timeout: 5 minutes)
- [ ] Capture agent output (US-story.md content, individual TASK-*.md files content)
- [ ] Validate output format is correct
- [ ] Parse task count from agent output

**Error Handling:**
- If agent timeout: Return error "PM agent exceeded 5-minute limit. Simplify brief and retry."
- If invalid output format: Return error "PM agent returned invalid format. Please file bug report."
- If agent failure: Return error with agent's error message

### 4. Enhance Tasks with Codebase Context

<thinking>
The PM agent has created initial tasks, but they lack codebase-specific context. Now I'll invoke the task-enhancer agent to research the codebase and add technical details, relevant files, code patterns, and architectural guidance to each task. This makes tasks immediately actionable for developers.
</thinking>

**Prepare Task Enhancement:**
- [ ] Identify output directory where TASK-*.md files were created
- [ ] Get story file path (US-story.md)
- [ ] Determine project root directory
- [ ] Identify codebase focus areas (if any)

**Call Task Enhancer Agent via Task Tool:**

Use the Task tool with `subagent_type="task-enhancer"` to invoke the task enhancement agent:

```markdown
Call @agent-task-enhancer with:

**Input Parameters:**
- $tasks_dir: "{output_dir}/TASKS/"
- $story_file: "{output_dir}/US-story.md"
- $project_root: "{current_project_root}"
- $codebase_focus: "{specific_dirs_or_*_for_all}"

**Expected Enhancements:**
For each TASK-*.md file, add:
1. Technical Context - How task fits into architecture
2. Relevant Files - Existing files to reference
3. Files to Create/Modify - Specific file paths
4. Code Patterns - Examples from similar implementations
5. Dependencies - Libraries and internal modules
6. Architecture Integration - Component relationships
7. Testing Strategy - Based on existing test patterns
8. Security Considerations - Based on current patterns
9. Implementation Tips - Do's, Don'ts, Gotchas

**Output:**
Enhanced TASK-*.md files with rich technical context
```

**Agent Execution:**
- [ ] Invoke Task tool with task-enhancer subagent type
- [ ] Wait for agent completion (timeout: 10 minutes - needs time to research codebase)
- [ ] Verify each TASK-*.md file now has "Technical Context" section
- [ ] Validate enhancement quality (relevant files found, code patterns included)

**Enhancement Validation:**
- [ ] Check each enhanced task includes:
  - At least 3 relevant files identified
  - At least 2 code pattern examples
  - Specific files to create/modify
  - Dependencies listed
  - Architecture integration notes
  - Testing strategy
- [ ] If validation fails: Warn but continue (enhancement is optional, don't block feature creation)

**Error Handling:**
- If agent timeout: Warn "Task enhancement took too long. Tasks created but not enhanced. You can manually add context later."
- If agent failure: Warn "Task enhancement failed: {error}. Tasks created but not enhanced."
- If no relevant files found: This is OK (might be a new pattern) - agent will note this in tasks
- If enhancement incomplete: Warn which tasks were not enhanced, continue with available enhancements

**Benefits of Enhancement:**
- ✅ Developers know exactly which files to reference
- ✅ Code patterns are provided (copy-paste ready)
- ✅ Dependencies are clear (no hunting for libraries)
- ✅ Architecture guidance prevents misalignment
- ✅ Testing patterns follow project conventions
- ✅ Security considerations are project-specific
- ✅ Implementation tips prevent common mistakes

### 5. Generate and Write Output Files

<thinking>
The PM agent has provided the initial content, and the task-enhancer has added codebase context. Files have already been written by the agents. Now I verify they exist and are valid.
</thinking>

**File Generation:**
- [ ] Format US-story.md content with proper markdown structure
- [ ] Include Story ID (US-{ID}) at the top of US-story.md
- [ ] Format each TASK-*.md file with proper task structure
- [ ] Add metadata headers (creation date, generated by Claude Code, story ID)
- [ ] Ensure consistent formatting (line breaks, spacing)
- [ ] Add placeholder for GitHub issue numbers in each file

**File Writing:**
- [ ] Determine output directory: `./project-management/US-STORY/US-{ID}-{story-name}/`
- [ ] Write US-story.md to output directory
- [ ] Write each TASK-{ID}.md to `{output_directory}/TASKS/` subdirectory
- [ ] Set appropriate file permissions (644 for files)

**Validation:**
- [ ] Verify US-story.md exists
- [ ] Verify all TASK-*.md files exist in TASKS/ subdirectory
- [ ] Count task files to ensure all were written
- [ ] Verify files are valid Markdown
- [ ] Check US-story.md contains all required sections (Title, Description, Acceptance Criteria, Security, Testing)
- [ ] Check each TASK-*.md has proper format (ID, Title, Description, Dependencies, Complexity)

**Error Handling:**
- If write fails (no disk space): Return error "File write failed. Check disk space."
- If write fails (permission denied): Return error "Permission denied. Check write permissions for directory."
- If validation fails: Return error with specific validation issue

### 6. Create GitHub Issues (MANDATORY)

<thinking>
Now that files are created, I must create GitHub issues for the main story and all tasks. This is a mandatory step that always executes.
</thinking>

**GitHub Integration:**

This section ALWAYS executes (not optional). Prerequisites already validated in step 1.

**Create Main Story Issue:**
- [ ] Read US-story.md content
- [ ] Extract story title from US-story.md
- [ ] Create main GitHub issue:
  ```bash
  gh issue create \
    --title "[STORY] {story-title}" \
    --body-file "./project-management/US-STORY/US-{ID}-{name}/US-story.md" \
    --label "user-story,story:US-{ID}" \
    --assignee "@me"
  ```
- [ ] Capture main issue number: `STORY_ISSUE=$(gh issue list --label "story:US-{ID}" --json number --jq '.[0].number')`
- [ ] Store story issue number for sub-issue creation

**Create Sub-Issues for Tasks:**
- [ ] For each TASK-*.md file in TASKS/ directory:
  - [ ] Extract task ID (e.g., TASK-1.1)
  - [ ] Extract task title from file
  - [ ] Create GitHub sub-issue:
    ```bash
    gh issue create \
      --title "[TASK-{ID}] {task-title}" \
      --body-file "./project-management/US-STORY/US-{ID}-{name}/TASKS/TASK-{ID}.md" \
      --label "task,story:US-{ID},parent:${STORY_ISSUE}" \
      --assignee "@me"
    ```
  - [ ] Capture issue number
  - [ ] Store task ID -> issue number mapping

**Update Files with Issue Numbers:**
- [ ] Append to US-story.md: `\n\n---\n**GitHub Issue:** #{issue_number}`
- [ ] For each TASK-*.md file:
  - [ ] Append: `\n\n---\n**GitHub Issue:** #{issue_number}`
  - [ ] Append: `**Parent Story:** #{story_issue_number}`

**Collect Results:**
- [ ] Create summary of all created issues (story + tasks)
- [ ] Store issue URLs for output

**Error Handling:**
- If issue creation fails: Return error "GitHub issue creation failed. Manual fallback: You can create issues manually from the generated files"
- If issue number capture fails: Warn but continue "Could not capture issue number. Check GitHub directly."
- If file update fails: Warn "Could not update files with issue numbers. Issues created but not linked in files."

### 7. Git Operations

<thinking>
If we're in a git repository, we should add the new files for tracking but NOT commit them. The user will commit when ready.
</thinking>

**Git Status Check:**
- [ ] Verify we're in git repository (already checked in step 1)
- [ ] Get current git status: `git status --porcelain`

**Git Add (if in repository):**
- [ ] Add entire story directory: `git add ./project-management/US-STORY/US-{ID}-{name}/`
- [ ] Show status: `git status --short`

**DO NOT:**
- ❌ Create commits (user will commit when ready)
- ❌ Create branches (that happens in task-exec)
- ❌ Push to remote

**Error Handling:**
- If git add fails: Warn but continue "Could not add files to git. Add manually with: git add ./project-management/US-STORY/US-{ID}-{name}/"

### 8. Final Summary and Output

<thinking>
Provide clear, actionable summary of what was created and next steps.
</thinking>

**Success Output:**

```markdown
✅ Story created: US-{ID}-{story-name}

📁 Directory structure:
   ./project-management/US-STORY/US-{ID}-{story-name}/
   ├── US-story.md ........................ GitHub Issue #{story_issue}
   └── TASKS/
       ├── TASK-1.1.md ..................... GitHub Issue #{task_issue_1} ✨ Enhanced
       ├── TASK-1.2.md ..................... GitHub Issue #{task_issue_2} ✨ Enhanced
       └── TASK-1.3.md ..................... GitHub Issue #{task_issue_3} ✨ Enhanced

🔗 GitHub Issues:
   Main Story: #{story_issue} - [STORY] {story_title}
   Tasks:
     #{task_issue_1} - [TASK-1.1] {task_1_title}
     #{task_issue_2} - [TASK-1.2] {task_2_title}
     #{task_issue_3} - [TASK-1.3] {task_3_title}

✨ Task Enhancement Applied:
   Each task includes:
   • Relevant files from codebase to reference
   • Code patterns and examples to follow
   • Specific files to create/modify with paths
   • Dependencies (libraries + internal modules)
   • Architecture integration guidance
   • Testing strategy based on project patterns
   • Security considerations
   • Implementation tips (do's, don'ts, gotchas)

📋 Next Steps:
   1. Review story: cat ./project-management/US-STORY/US-{ID}-{story-name}/US-story.md
   2. Review enhanced task: cat ./project-management/US-STORY/US-{ID}-{story-name}/TASKS/TASK-1.1.md
   3. Start implementation: /lazy task-exec TASK-1.1 --story US-{ID}
   4. View issues: gh issue view {story_issue}

💡 Tip: Use '/lazy task-exec all --story US-{ID}' to execute all tasks for this story
```

**Failure Output:**

If any critical error occurred:

```markdown
❌ Feature creation failed

Error: {error_message}

Cause: {error_cause}

Recovery:
{specific_recovery_steps}

Next Steps:
{what_user_should_do}
```

## Error Handling Reference

| Error | Cause | Recovery |
|-------|-------|----------|
| **Enrichment failed** | API key missing or quota exceeded | Check ANTHROPIC_API_KEY, retry after cool-down |
| **Agent timeout** | PM agent exceeded 5-min limit | Simplify brief, reduce scope, retry |
| **File write failed** | No disk space or permission denied | Check filesystem, verify write permissions |
| **Directory creation failed** | Permission denied or path issues | Check permissions, verify parent directory exists |
| **Git context missing** | Not in git repository | Run `git init` and retry (optional) |
| **Malformed output** | PM agent returned invalid format | File bug with Claude, provide example brief |
| **gh CLI missing** | GitHub CLI not installed | Install with: brew install gh (or download from https://cli.github.com) |
| **gh auth failed** | Not authenticated to GitHub | Run: `gh auth login` |
| **Issue creation failed** | API errors or network issues | Manual fallback: create issues manually from generated files |

## Success Indicators

All of these must be true for successful execution:

- ✅ Story directory created: `./project-management/US-STORY/US-{ID}-{name}/`
- ✅ TASKS subdirectory created: `./project-management/US-STORY/US-{ID}-{name}/TASKS/`
- ✅ US-story.md exists and is valid Markdown
- ✅ All TASK-*.md files exist in TASKS/ subdirectory
- ✅ All required sections present in US-story.md:
  - Story ID (US-{ID})
  - Title
  - Description
  - Acceptance Criteria
  - Security Considerations (from enrichment)
  - Testing Requirements (from enrichment)
  - GitHub issue number
- ✅ Each TASK-*.md has proper format:
  - Task ID (TASK-1.1, TASK-1.2, etc.)
  - Task title and description
  - Dependencies noted
  - Complexity estimate
  - GitHub issue number
  - Parent story reference
- ✅ GitHub issues created for story and all tasks
- ✅ Files are tracked in git (if in repository)
- ✅ No uncommitted changes to existing files

## Example Usage

**Basic usage (creates US-3.4 automatically):**
```bash
/lazy create-feature "Add OAuth2 authentication with Google, GitHub"
```

**With PM role:**
```bash
/lazy create-feature "Build payment processing with Stripe" --role pm
```

**With techlead role (more technical depth):**
```bash
/lazy create-feature "Implement WebSocket real-time updates" --role techlead
```

**With custom output base directory (still creates US-{ID} subdirectory inside):**
```bash
/lazy create-feature "Add analytics dashboard" --output-dir ./docs/project-management/US-STORY
```

**With specific role:**
```bash
/lazy create-feature "Refactor database layer" --role techlead
```

## Real-World Example Output

After running `/lazy create-feature "Add OAuth2 authentication with Google and GitHub"`:

**Directory Structure Created:**
```
./project-management/US-STORY/US-3.4-oauth2-authentication/
├── US-story.md
└── TASKS/
    ├── TASK-1.1.md
    ├── TASK-1.2.md
    ├── TASK-1.3.md
    └── TASK-1.4.md
```

**US-story.md:**
```markdown
# Story US-3.4: Build OAuth2 Authentication System

## Description
Add OAuth2 authentication with Google and GitHub providers to allow users to sign in securely.

## Acceptance Criteria
- [ ] Users can authenticate via Google OAuth2
- [ ] Users can authenticate via GitHub OAuth2
- [ ] Session tokens are securely stored
- [ ] CSRF protection implemented
- [ ] Rate limiting on auth endpoints

## Security Considerations
- OAuth2 token refresh mechanism
- Secure state parameter handling
- PKCE support for mobile clients
- No plain text secrets in logs
- Token expiration and rotation policy

## Testing Requirements
- [ ] Unit tests for OAuth2 providers
- [ ] Integration tests for auth flow
- [ ] Security tests for CSRF protection
- [ ] Load tests for rate limiting
- [ ] E2E tests for complete auth flow

---
**GitHub Issue:** #42
```

**TASKS/TASK-1.1.md:**
```markdown
# TASK-1.1: Setup OAuth2 Configuration

**Description:** Configure OAuth2 providers (Google, GitHub) with client IDs and secrets

**Dependencies:** None

**Complexity:** Low

**Skills:** Configuration management, environment variables

---
**GitHub Issue:** #43
**Parent Story:** #42
```

**TASKS/TASK-1.2.md:**
```markdown
# TASK-1.2: Implement Google OAuth2 Provider

**Description:** Build Google OAuth2 authentication strategy

**Dependencies:** TASK-1.1

**Complexity:** Medium

**Skills:** OAuth2 protocol, Google APIs

---
**GitHub Issue:** #44
**Parent Story:** #42
```

**Command Output:**
```
✅ Story created: US-3.4-oauth2-authentication

📁 Directory structure:
   ./project-management/US-STORY/US-3.4-oauth2-authentication/
   ├── US-story.md ........................ GitHub Issue #42
   └── TASKS/
       ├── TASK-1.1.md ..................... GitHub Issue #43
       ├── TASK-1.2.md ..................... GitHub Issue #44
       ├── TASK-1.3.md ..................... GitHub Issue #45
       └── TASK-1.4.md ..................... GitHub Issue #46

🔗 GitHub Issues:
   Main Story: #42 - [STORY] Build OAuth2 Authentication System
   Tasks:
     #43 - [TASK-1.1] Setup OAuth2 Configuration
     #44 - [TASK-1.2] Implement Google OAuth2 Provider
     #45 - [TASK-1.3] Implement GitHub OAuth2 Provider
     #46 - [TASK-1.4] Add OAuth2 Security Validation

📋 Next Steps:
   1. Review story: cat ./project-management/US-STORY/US-3.4-oauth2-authentication/US-story.md
   2. Start implementation: /lazy task-exec TASK-1.1 --story US-3.4
   3. View issues: gh issue view 42

💡 Tip: Use '/lazy task-exec all --story US-3.4' to execute all tasks for this story
```

## Notes

- This command receives **enriched input** from the pre-prompt-enrichment hook automatically
- The enrichment adds architecture, security, testing, and edge case context
- The PM agent uses this enrichment to create comprehensive user stories and tasks
- **NEW: Task-enhancer agent** researches codebase and adds technical context to each task:
  - Relevant files to reference (existing similar implementations)
  - Code patterns and examples from the codebase
  - Specific files to create/modify with paths
  - Dependencies (libraries + internal modules)
  - Architecture integration guidance
  - Testing strategy based on project patterns
  - Implementation tips (do's, don'ts, gotchas from codebase)
- **Story ID is auto-generated** by scanning existing stories and incrementing
- **Directory structure is standardized**: `./project-management/US-STORY/US-{ID}-{name}/`
- **GitHub issue creation is MANDATORY** - always creates issues for story and all tasks (with enhanced content)
- **Each task gets its own file** in the TASKS/ subdirectory
- Files are added to git but **not committed** - user controls when to commit
- Use `/lazy task-exec` after this command to implement the tasks
- The `gh` CLI must be installed and authenticated before running this command
