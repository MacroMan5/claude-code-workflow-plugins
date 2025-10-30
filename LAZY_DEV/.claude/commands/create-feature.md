---
description: Create user story and tasks from feature brief
argument-hint: "[feature-description] [--file FILE] [--role pm|techlead] [--output-dir DIR]"
allowed-tools: Read, Write, Task, Bash, Grep, Glob
model: claude-haiku-4-5-20251001
---

# Create Feature: Transform Brief to User Story + Tasks

## Introduction

Transform a brief feature description into a complete user story with individual task files in a structured directory.

**Input Sources:**
1. **From STT Prompt Enhancer** (recommended): Enhanced, structured feature description from the STT_PROMPT_ENHANCER project
2. **Direct Input**: Brief text provided directly to command
3. **Pre-Prompt Enrichment Hook**: Automatically adds architecture, security, testing, and edge case considerations

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

## Usage Examples

```bash
# From direct input
/lazy create-feature "Add user authentication with OAuth2"

# From STT enhanced file
/lazy create-feature --file enhanced_prompt.md

# With specific role
/lazy create-feature "Build payment processing" --role techlead

# With custom output directory
/lazy create-feature "Add analytics dashboard" --output-dir ./docs/project-management/US-STORY
```

## Feature Description

<feature_description>
$ARGUMENTS
</feature_description>

## Main Tasks

### Step 1: Load Feature Brief

<thinking>
First, I need to load the feature brief from either the STT enhanced file, direct input, or the arguments. The brief may have already been enriched by the pre-prompt hook.
</thinking>

**Input Sources:**
1. **From STT Prompt Enhancer** (recommended):
   - Check if `--file` argument is provided
   - If yes, read enhanced prompt from file path
   - Contains: Enhanced, structured feature description
   - Location: Provided as argument or check default STT_PROMPT_ENHANCER output location

2. **Direct Input**:
   - Extract feature brief from `$ARGUMENTS` if no `--file` flag
   - Brief text provided directly to command

**Parse Arguments:**
- [ ] Check for `--file` flag and read enhanced prompt file if provided
- [ ] If no `--file`, extract feature brief from `$ARGUMENTS`
- [ ] Parse optional `--role` flag (pm|techlead) - defaults to "pm"
- [ ] Parse optional `--output-dir` flag - defaults to `./project-management/US-STORY/US-{ID}-{name}/`
- [ ] Verify the brief is not empty

**Error Handling:**
- If `--file` provided but file not found: Return error "Enhanced prompt file not found at: {path}"
- If no input provided: Return error "No feature brief provided. Use --file or provide description."
- If brief is empty: Return error "Feature brief is empty. Provide a valid description."

### Step 2: Pre-Prompt Enrichment

<thinking>
The pre-prompt enrichment hook should fire automatically via the user_prompt_submit hook. However, I should verify the enrichment has been applied and the brief contains the necessary context.
</thinking>

**Hook fires automatically** (user_prompt_submit):
- Adds architecture patterns relevant to the project
- Adds security requirements (OWASP considerations)
- Adds testing strategy (unit, integration, edge cases)
- Adds edge cases to consider
- Uses Claude Haiku for cost efficiency

**Verify Enrichment:**
- [ ] Check if brief contains security considerations
- [ ] Check if brief contains testing requirements
- [ ] Check if brief mentions architecture patterns
- [ ] If enrichment missing: Warn "Pre-prompt enrichment may not have fired. Check ANTHROPIC_API_KEY."

**Error Handling:**
- If enrichment failed (missing ANTHROPIC_API_KEY): Warn but continue "Pre-prompt enrichment failed. Story may lack security/testing context."
- Agent can still proceed with non-enriched brief (but quality may be lower)

### Step 3: Parse Arguments and Validate Context

<thinking>
Now I need to parse any remaining arguments and validate the environment is ready for story creation.
</thinking>

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
- If git not initialized: Warn "Not in git repository. Consider running `git init` for better tracking."
- If gh not installed: Return error "GitHub CLI not installed. Install with: brew install gh (or download from https://cli.github.com)"
- If gh not authenticated: Return error "GitHub CLI not authenticated. Run: gh auth login"
- If directory creation fails: Return error "Could not create directory structure. Check permissions."

### Step 4: Load Project Context

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

### Step 5: Invoke Project Manager Agent

<thinking>
Now I'll explicitly invoke the PM agent with the enriched brief and project context. The agent is defined at `.claude/agents/project-manager.md` and will create detailed US-story.md and individual TASK-*.md files following best practices.
</thinking>

**Agent Information:**
- **Agent File**: `.claude/agents/project-manager.md`
- **Agent Type**: project-manager
- **Model**: sonnet (Claude Sonnet 4.5)
- **Tools Available**: Read, Write, Grep, Glob
- **Invocation**: Automatic when user provides feature brief

**Prepare Context for Agent:**

The agent will receive context from the conversation, so prepare it clearly:

```markdown
FEATURE BRIEF (Enhanced):
{enriched_feature_brief_from_step_1_and_2}

ROLE: {pm|techlead}

PROJECT CONTEXT:
- Project Type: {identified_from_files}
- Architecture: {from_CLAUDE.md_or_README}
- Testing Framework: {pytest|jest|etc}
- Code Style: {Black|Prettier|etc}

TECHNICAL CONSTRAINTS:
- Programming Languages: {python|javascript|etc}
- Frameworks: {django|react|etc}
- Security Policies: {from_project_context}
- Performance Requirements: {if_any}

OUTPUT DIRECTORY: ./project-management/US-STORY/US-{ID}-{story-name}/
STORY ID: US-{generated_id}
```

**Invoke Agent Using Task Tool:**

Since the agent has `description: "Use PROACTIVELY when user provides a feature brief"`, it will be invoked automatically by Claude Code when the feature brief is detected in the conversation.

However, to ensure explicit invocation, you can invoke it via the Task tool:

```
Task tool will call the project-manager agent, which will:
1. Extract context from the conversation (above)
2. Create US-story.md with comprehensive details
3. Break down into individual TASK-X.Y.md files
4. Write files to the output directory
5. Return file locations and summary
```

**Agent Execution Steps:**
- [ ] Agent reads feature brief from conversation
- [ ] Agent identifies role (pm or techlead)
- [ ] Agent extracts technical constraints
- [ ] Agent analyzes project context
- [ ] Agent creates US-story.md with:
  - Story ID (US-{ID})
  - Title and description
  - Acceptance Criteria (specific, measurable, testable)
  - Security Considerations (OWASP, input validation, auth)
  - Testing Requirements (unit, integration, edge cases)
  - Technical Dependencies
  - Architecture Impact
  - Non-Functional Requirements
  - Definition of Done
- [ ] Agent breaks down into atomic tasks
- [ ] Agent creates individual TASK-X.Y.md files with:
  - Task ID (TASK-1.1, TASK-1.2, etc.)
  - Task description and implementation approach
  - Dependencies between tasks
  - Effort estimate (S/M/L, hours)
  - Acceptance criteria
  - Security checklist
  - Testing checklist
  - Quality gates
  - Skills required
- [ ] Agent validates all acceptance criteria are covered
- [ ] Agent ensures task dependencies are correct
- [ ] Agent writes all files to output directory

**Expected Output from Agent:**
1. **US-story.md** - Written to `./project-management/US-STORY/US-{ID}-{story-name}/`
2. **TASK-1.1.md, TASK-1.2.md, etc.** - Written to `./project-management/US-STORY/US-{ID}-{story-name}/TASKS/`
3. **Summary** - Number of tasks created, file locations

**Validation After Agent Completes:**
- [ ] Verify US-story.md exists and is valid
- [ ] Verify all TASK-*.md files exist in TASKS/ subdirectory
- [ ] Count task files
- [ ] Check US-story.md has all required sections
- [ ] Check each TASK-*.md has proper format
- [ ] Validate Story ID format: US-X.Y
- [ ] Validate Task ID format: TASK-X.Y
- [ ] Validate filename format: TASK-X.Y.md

**Error Handling:**
- If agent timeout (>5 minutes): Return error "PM agent exceeded time limit. Try breaking the feature into smaller pieces."
- If invalid output format: Return error "PM agent returned invalid format. Check agent template at .claude/agents/project-manager.md"
- If agent failure: Return error "PM agent failed: {error_message}"
- If missing required sections: Return error "PM agent output missing required sections: {list}"
- If no tasks created: Return error "PM agent created story but no tasks. Feature may be too vague - add more details."

### Step 6: Enhance Tasks with Codebase Context

<thinking>
The PM agent has created initial tasks, but they lack codebase-specific context. Now I'll invoke the task-enhancer agent to research the codebase and add technical details, relevant files, code patterns, and architectural guidance to each task. This makes tasks immediately actionable for developers.
</thinking>

**Agent Information:**
- **Agent File**: `.claude/agents/task-enhancer.md`
- **Agent Type**: task-enhancer
- **Purpose**: Add codebase-specific context to tasks
- **Tools Available**: Read, Write, Grep, Glob (for codebase research)

**Prepare Task Enhancement:**
- [ ] Identify output directory where TASK-*.md files were created
- [ ] Get story file path (US-story.md)
- [ ] Determine project root directory
- [ ] Identify codebase focus areas (if any)

**Invoke Task Enhancer Agent:**

The task-enhancer agent will research the codebase and enhance each task file with technical context.

**Context for Agent:**
```markdown
TASKS DIRECTORY: ./project-management/US-STORY/US-{ID}-{story-name}/TASKS/
STORY FILE: ./project-management/US-STORY/US-{ID}-{story-name}/US-story.md
PROJECT ROOT: {current_working_directory}
CODEBASE FOCUS: * (all directories)
```

**Agent Workflow:**
1. Agent scans TASKS/ directory for all TASK-*.md files
2. For each task:
   - Reads task description and acceptance criteria
   - Uses Grep to find relevant files in codebase
   - Uses Glob to find similar patterns
   - Identifies code examples to reference
   - Finds dependencies (imports, libraries)
   - Maps architecture integration points
   - Identifies testing patterns from test files
   - Extracts security patterns from existing code
3. Agent enhances each TASK-*.md with:
   - **Technical Context** - How task fits into architecture
   - **Relevant Files** - Existing files to reference with paths
   - **Files to Create/Modify** - Specific file paths
   - **Code Patterns** - Examples from similar implementations
   - **Dependencies** - Libraries and internal modules
   - **Architecture Integration** - Component relationships
   - **Testing Strategy** - Based on existing test patterns
   - **Security Considerations** - Based on current patterns
   - **Implementation Tips** - Do's, Don'ts, Gotchas
4. Agent writes enhanced content back to each TASK-*.md file
5. Agent returns summary of enhancements

**Agent Execution:**
- [ ] Invoke task-enhancer agent (automatic or explicit via Task tool)
- [ ] Wait for agent completion (timeout: 10 minutes - needs time to research codebase)
- [ ] Verify each TASK-*.md file now has enhanced sections
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

### Step 7: Verify Output Files

<thinking>
The PM agent and task-enhancer agent have written all files. Now I verify they exist, are valid, and contain all required sections.
</thinking>

**File Verification (agents have already written files):**
- [ ] Confirm output directory exists: `./project-management/US-STORY/US-{ID}-{story-name}/`
- [ ] Confirm TASKS subdirectory exists: `./project-management/US-STORY/US-{ID}-{story-name}/TASKS/`

**Content Validation:**
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

### Step 8: Create GitHub Issues (MANDATORY)

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

### Step 9: Git Operations

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

### Step 10: Final Summary and Output

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

## Workflow Summary

This command orchestrates multiple agents to create a complete feature specification:

### Step-by-Step Agent Workflow

1. **Load Feature Brief**
   - From STT Prompt Enhancer file (`--file` flag)
   - From direct input (command arguments)
   - Parse role and output directory options

2. **Pre-Prompt Enrichment** (Automatic Hook)
   - Hook: `user_prompt_submit`
   - Adds: Architecture patterns, security requirements, testing strategy, edge cases
   - Model: Claude Haiku (cost efficient)

3. **Parse Arguments and Validate Context**
   - Generate Story ID (auto-increment from existing stories)
   - Create directory structure
   - Validate git repository and GitHub CLI setup

4. **Load Project Context**
   - Read CLAUDE.md, README.md
   - Identify project type, frameworks, testing patterns
   - Extract technical constraints

5. **Invoke Project Manager Agent** (Explicit)
   - Agent: `.claude/agents/project-manager.md`
   - Creates: US-story.md with comprehensive details
   - Creates: Individual TASK-X.Y.md files (atomic, testable tasks)
   - Validates: All acceptance criteria covered, dependencies mapped

6. **Invoke Task Enhancer Agent** (Explicit)
   - Agent: `.claude/agents/task-enhancer.md`
   - Researches: Codebase for relevant files, patterns, examples
   - Enhances: Each TASK-*.md with technical context
   - Adds: Relevant files, code patterns, dependencies, architecture integration

7. **Verify Output Files**
   - Confirm US-story.md exists and is valid
   - Confirm all TASK-*.md files exist
   - Validate format and required sections

8. **Create GitHub Issues** (MANDATORY)
   - Create main story issue
   - Create sub-issues for each task
   - Link tasks to story
   - Update files with issue numbers

9. **Git Operations**
   - Add files to git (but do NOT commit)
   - User controls when to commit

10. **Final Summary**
    - Display created files and issue numbers
    - Show next steps

## Key Features

- **Input Flexibility**: Accepts STT enhanced files or direct input
- **Automatic Enrichment**: Pre-prompt hook adds comprehensive context
- **Explicit Agent Invocation**: Clear project-manager and task-enhancer agent workflow
- **Codebase-Aware Tasks**: Tasks include relevant files, patterns, and examples
- **Auto Story ID**: Scans existing stories and auto-increments
- **GitHub Integration**: Mandatory issue creation for traceability
- **Quality Standards**: Each task has security, testing, and quality checklists

## Important Notes

- **Story ID is auto-generated**: Scans `./project-management/US-STORY/` and increments
- **Directory structure is standardized**: `./project-management/US-STORY/US-{ID}-{name}/`
- **Each task gets its own file**: TASK-1.1.md, TASK-1.2.md, etc. in TASKS/ subdirectory
- **GitHub CLI required**: Must have `gh` installed and authenticated
- **Files added to git but NOT committed**: User controls when to commit
- **Use `/lazy task-exec TASK-X.Y` after this command to implement tasks**

## Agent Details

### Project Manager Agent
- **File**: `.claude/agents/project-manager.md`
- **Model**: Claude Sonnet 4.5
- **Tools**: Read, Write, Grep, Glob
- **Output**: US-story.md + multiple TASK-X.Y.md files
- **Automatic Invocation**: Yes (when feature brief detected)

### Task Enhancer Agent
- **File**: `.claude/agents/task-enhancer.md`
- **Purpose**: Add codebase-specific context to tasks
- **Research**: Uses Grep/Glob to find relevant files and patterns
- **Enhancements**: Technical context, code examples, architecture integration
- **Timeout**: 10 minutes (needs time to research codebase)
