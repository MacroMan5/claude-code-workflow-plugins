# CLAUDE.md

This file provides guidance to Claude Code when working with code in repositories using the **LAZY_DEV Framework**.

---

## Framework Overview

**LAZY_DEV** is a command-first AI framework for Claude Code CLI that enforces quality through automation while maintaining developer productivity.

### Core Philosophy

**"Be lazy, but consistently excellent"**

Automate mundane tasks (formatting, commits, PRs) while enforcing discipline (quality gates, TDD, security checks).

---

## Commands

Commands are your primary interface to LAZY_DEV. Think of them as orchestrators that coordinate agents, skills, and quality checks.

### Planning Commands

#### `/lazy plan`

**When to use:** Transform a feature idea into a structured user story with inline tasks.

**Input:** Brief feature description (text or file path).

**What it does:**
- Generates US-{ID}-{name} directory structure
- Creates US-story.md with acceptance criteria and inline tasks
- Optionally creates GitHub issues
- Sets `story/US-{ID}-start` git tag

**Examples:**
```bash
# From brief description
/lazy plan "Add user authentication with OAuth2"

# From enhanced prompt file
/lazy plan --file enhanced_prompt.md

# Skip GitHub issue creation
/lazy plan "Build payment processing" --no-issue
```

**Triggers:**
- `brainstorming` skill (automatic) - explores design options before story creation
- `project-manager` agent - structures the story and tasks

**Output:**
```
./project-management/US-STORY/US-{ID}-{name}/
└── US-story.md              # User story with inline tasks
```

---

### Development Commands

#### `/lazy code`

**When to use:** Implement anything - from quick fixes to full user stories.

**Input:** Flexible - accepts story files, task IDs, GitHub issues, or brief descriptions.

**What it does:**
- Detects input type (story/@file/TASK-ID/#issue/brief)
- Loads context and determines scope
- Auto-detects complexity, test requirements, and review needs
- Implements code with appropriate quality checks
- Creates atomic commits with proper messages

**Examples:**
```bash
# Quick feature from brief
/lazy code "add logout button to header"

# From user story file
/lazy code @US-3.4.md

# From task ID (auto-finds story)
/lazy code TASK-003

# From GitHub issue
/lazy code #456
```

**Smart Detection:**
- **Tests:** Runs if project has test framework OR TDD mentioned in docs
- **Review:** Triggers for complex/security/multi-file tasks only
- **Branch:** Creates feature branch for stories, uses current for quick tasks

**Triggers:**
- `coder` agent - implements the feature
- `tester` agent - writes tests (if TDD required)
- `reviewer` agent - reviews complex tasks
- `context-packer` skill (automatic) - loads relevant context
- Quality pipeline (automatic via PostToolUse hook)

**Integration with plan:**
```bash
/lazy plan "feature description"  # Creates US-story.md
/lazy code @US-story.md          # Implements first task
/lazy code TASK-002              # Continues with next task
```

---

### Quality Commands

#### `/lazy review`

**When to use:** Review entire story implementation and create PR after all tasks are committed.

**Input:** Story ID (US-X.Y) or path to US-story.md.

**What it does:**
- Validates all tasks are committed (checks git tags)
- Reviews against acceptance criteria and project standards
- Runs full test suite with coverage analysis
- Either creates PR (if approved) or generates structured debug report on failure

**Examples:**
```bash
# Review by story ID
/lazy review US-3.4

# Review with full path
/lazy review ./project-management/US-STORY/US-3.4-oauth2/US-story.md

# Review on different base branch
/lazy review US-3.4 --base develop

# Create as draft PR
/lazy review US-3.4 --draft
```

**Prerequisites:**
- All tasks committed with `task/TASK-X.Y-committed` tags
- Story start tag exists: `story/US-X.Y-start`
- Clean working directory

**Outcomes:**

**If APPROVED:**
- Creates single PR with all commits
- Comprehensive PR body with story context, tests, metrics
- Auto-closes all related GitHub issues (story + tasks)

**If CHANGES_REQUIRED:**
- Generates structured debug report: `US-X.Y-review-report.md`
- Contains: summary, issues (critical/warning/suggestion), per-task status, next steps
- Machine-readable format for `/lazy fix` command
- Provides fix commands and estimated time

**Debug Report Format:**
```markdown
# US-3.4 Review Report

## Summary
Story review incomplete - 2 CRITICAL, 3 WARNING, 1 SUGGESTION issues found.

## Issues

### CRITICAL
1. Missing input validation (src/auth/oauth.py:45)
2. Test coverage 65% (required >80%)

### WARNING
1. Missing docstrings in payment processor
2. No rate limiting on API endpoint
3. Incomplete error handling

### SUGGESTION
1. Refactor duplicate code in handlers

## Task Status
- TASK-3.4.1: COMPLETE (committed)
- TASK-3.4.2: COMPLETE (committed)
- TASK-3.4.3: COMPLETE (committed)

## Next Steps
1. Run: /lazy fix US-3.4-review-report.md
2. Address CRITICAL security issue
3. Add missing tests for coverage
4. Re-run: /lazy review US-3.4
```

**Triggers:**
- `reviewer-story` agent - comprehensive story review
- Loads project standards (CLAUDE.md, README.md, CONTRIBUTING.md)
- Loads enterprise guidelines (if configured)

---

#### `/lazy fix`

**When to use:** Apply fixes from a review report.

**Input:** Path to review report file (format: `US-{ID}-review-report.md`).

**What it does:**
- Parses review report for issues by severity
- Routes fixes to appropriate agents (coder/tester/refactor/documentation)
- Applies fixes and re-runs quality checks
- Updates commits with fixes

**Examples:**
```bash
# Fix issues from review report
/lazy fix US-3.4-review-report.md
```

**Integration with review:**
```bash
/lazy code TASK-001             # Implementation
/lazy code TASK-002             # Implementation
/lazy review US-3.4             # Generates review report (if issues)
# Output: US-3.4-review-report.md
/lazy fix US-3.4-review-report.md  # Apply fixes
/lazy review US-3.4             # Re-review (should pass now)
```

**Report Consumption Cycle:**
```
/lazy review → CHANGES_REQUIRED
   ↓
   Generates US-{ID}-review-report.md
   ↓
   Read report (summary, issues, status)
   ↓
/lazy fix US-{ID}-review-report.md
   ↓
   Routes to agents by severity
   ↓
   Adds missing tests, validation, docs
   ↓
   Re-runs quality pipeline
   ↓
/lazy review → APPROVED
   ↓
   PR created
```

---

### Documentation Commands

#### `/lazy docs`

**When to use:** Generate or update documentation for code, APIs, or features.

**Input:** File path or scope to document.

**What it does:**
- Analyzes code structure and APIs
- Generates Google-style docstrings (Python)
- Creates README sections, API docs, or setup guides
- Updates existing documentation

**Examples:**
```bash
# Document specific file
/lazy docs src/auth/oauth.py

# Document entire module
/lazy docs src/auth/

# Generate API documentation
/lazy docs --format api src/api/

# Generate README
/lazy docs --format readme
```

**Formats:**
- `docstrings` - Add/update inline documentation
- `readme` - Generate README.md sections
- `api` - API reference documentation
- `security` - Security considerations
- `setup` - Installation and setup guide

**Triggers:**
- `documentation` agent - generates documentation

---

### Utility Commands

#### `/lazy clean`

**When to use:** Remove dead code, unused imports, and orphaned files.

**Input:** Path to clean (file or directory).

**What it does:**
- Identifies unused imports, functions, and classes
- Finds orphaned test files
- Removes commented-out code blocks
- Reports what can be safely removed

**Examples:**
```bash
# Clean specific directory
/lazy clean src/legacy/

# Clean entire project
/lazy clean .
```

**Triggers:**
- `cleanup` agent - analyzes and removes dead code

---

#### `/lazy memory-graph`

**When to use:** Manually persist durable facts to the project's knowledge graph.

**Input:** Statement describing the fact to persist.

**What it does:**
- Creates entities (person, team, service, repository)
- Adds observations (facts, decisions)
- Creates relationships between entities
- Stores in project-specific `.claude/memory/memory.jsonl`

**Examples:**
```bash
# Record service ownership
/lazy memory-graph "service:payment owned_by team:backend"

# Record API endpoint
/lazy memory-graph "repo:api endpoint:https://api.example.com"

# Record architecture decision
/lazy memory-graph "decision:use-postgres rationale:better transaction support date:2025-10-30"
```

**Note:** Memory graph is also auto-triggered during commands when durable facts are detected (via UserPromptSubmit hook).

---

#### `/lazy memory-check`

**When to use:** Verify MCP Memory connectivity and query stored knowledge.

**Input:** Optional query string.

**What it does:**
- Verifies MCP Memory server is connected
- Shows stored entities and relationships
- Searches for specific facts if query provided

**Examples:**
```bash
# Check connectivity
/lazy memory-check

# Search for specific entity
/lazy memory-check "service:payment"

# List all stored facts
/lazy memory-check --all
```

---

## Skills

Skills are reusable patterns that enhance commands and agents. They're automatically injected or manually invoked based on context.

### Auto-Triggered Skills

These activate automatically during command execution:

#### `brainstorming`

**Triggers:** During `/lazy plan` when multiple design approaches exist.

**What it does:** Generates 3-5 implementation options with pros/cons, recommends one with rationale.

**Output:** Table with Option | Pros | Cons | Effort | Risk

---

#### `memory-graph`

**Triggers:** When UserPromptSubmit hook detects durable facts (ownership, decisions, endpoints).

**What it does:** Persists facts to project's knowledge graph via MCP Memory.

**Disable:** Set `LAZYDEV_DISABLE_MEMORY_SKILL=1`

**Examples of auto-detection:**
- "service:api owned by Alice"
- "repo:backend endpoint:https://api.example.com"
- "decision: use Postgres for better transactions"

---

#### `output-style-selector`

**Triggers:** During UserPromptSubmit hook on every command.

**What it does:** Selects appropriate output format (table, list, code, prose) based on command context.

**Styles:**
- `table-based` - For comparisons and matrices
- `list-based` - For action items and steps
- `code-first` - For technical implementations
- `prose` - For explanations and reports

---

#### `context-packer`

**Triggers:** Before sub-agent calls and during UserPromptSubmit enrichment.

**What it does:** Summarizes relevant context (files, symbols, commits) to reduce token usage.

**Output:** 10-20 line brief with:
- Key file paths
- Important symbols/functions
- Last 3 relevant commits
- Pointers to exact lines (not full files)

---

### Manual-Triggered Skills

These are invoked explicitly by commands or when specific patterns are detected:

#### `story-traceability`

**When to use:** Map acceptance criteria to tasks to tests.

**Used by:** `project-manager` agent during story creation, `reviewer-story` agent during review.

**What it does:** Ensures every AC has corresponding tasks, every task has tests, creates traceability matrix.

---

#### `task-slicer`

**When to use:** Break large features into atomic, estimable tasks.

**Used by:** `project-manager` agent during story creation.

**What it does:**
- Analyzes feature scope
- Creates tasks of 2-4 hours each
- Ensures tasks are independent and testable
- Assigns estimates (S/M/L)

---

#### `git-worktrees`

**When to use:** Work on multiple stories in parallel with isolated environments.

**Used by:** Manually when needed.

**What it does:**
- Creates separate working directories for each story
- Maintains isolated dependencies
- Prevents branch switching conflicts

**Example:**
```bash
# Create worktree for new story
git worktree add ../project-US-3.4 feat/US-3.4-oauth2

# Work in isolation
cd ../project-US-3.4
/lazy code TASK-001

# Cleanup when done
git worktree remove ../project-US-3.4
```

---

#### `test-driven-development`

**When to use:** TDD workflow enforcement.

**Used by:** `coder` agent when tests are required.

**What it does:** Enforces RED → GREEN → REFACTOR cycle:
1. Write failing test (RED)
2. Minimal implementation (GREEN)
3. Improve code quality (REFACTOR)

**Enabled when:**
- Project has test framework (pytest.ini, jest.config.js)
- TDD mentioned in CLAUDE.md or README
- `LAZYDEV_ENFORCE_TDD=1` environment variable set

---

#### `code-review-checklist`

**When to use:** Comprehensive review criteria.

**Used by:** `reviewer` and `reviewer-story` agents.

**Checks:**
- Code quality (readability, maintainability)
- Correctness (meets ACs, edge cases)
- Security (OWASP Top 10)
- Testing (coverage, edge cases)
- Documentation (public APIs)

---

#### `security-scanner`

**When to use:** OWASP Top 10 validation.

**Used by:** Review agents for security-sensitive code (auth, payment, data handling).

**Checks:**
- Input validation
- SQL injection prevention
- XSS prevention
- Authentication/authorization
- Secrets management (no hardcoded keys)
- Proper error messages (no data leaks)

---

## Workflows

Complete end-to-end workflows showing how commands, skills, and agents work together.

### Feature Development Workflow

**Scenario:** Build a new feature from idea to merged PR.

```bash
# 1. Planning Phase
/lazy plan "Add OAuth2 authentication with Google and GitHub providers"
# ✓ Brainstorming skill explores OAuth2 implementation options
# ✓ Project-manager agent creates US-3.4-oauth2-authentication/
# ✓ Story file with 5 tasks (TASK-001 to TASK-005)
# ✓ GitHub issues created for story and tasks
# ✓ Git tag: story/US-3.4-start

# 2. Implementation Phase (task by task)
/lazy code @US-3.4.md
# ✓ Implements TASK-001: Set up OAuth2 configuration
# ✓ Context-packer loads relevant files
# ✓ Coder agent implements with tests
# ✓ PostToolUse hook: format → lint → type → test
# ✓ Commit: feat(TASK-001): set up OAuth2 configuration
# ✓ Git tag: task/TASK-001-committed

/lazy code TASK-002
# ✓ Implements TASK-002: Add Google OAuth2 provider
# ✓ Reviewer agent reviews (complex/security task)
# ✓ Commit after approval
# ✓ Git tag: task/TASK-002-committed

/lazy code TASK-003
/lazy code TASK-004
/lazy code TASK-005
# ... similar flow for remaining tasks

# 3. Review Phase
/lazy review US-3.4
# ✓ Reviewer-story agent checks:
#   - All 5 tasks committed
#   - All acceptance criteria met
#   - Security validated (OWASP)
#   - Test coverage >80%
#   - Integration between tasks
# ✓ PR created with comprehensive body
# ✓ GitHub issues closed (story + all tasks)

# 4. PR Merge (manual)
# Review PR on GitHub → Approve → Merge

# 5. Cleanup
/lazy clean src/auth/  # Remove any dead code
/lazy docs src/auth/   # Update documentation
```

**Timeline:** ~2-4 hours for 5 tasks

**Artifacts:**
- 1 user story file
- 5 commits (one per task)
- 1 PR (all tasks together)
- Closed GitHub issues
- Updated documentation

---

### Bug Fix Workflow

**Scenario:** Fix a reported bug quickly.

```bash
# 1. Quick Implementation (no story needed)
/lazy code "#456"
# ✓ Fetches GitHub issue #456: "Validation error in signup form"
# ✓ Coder agent implements fix
# ✓ Tester agent adds regression test
# ✓ Quality checks pass
# ✓ Commit: fix: validation error in signup form (closes #456)

# Alternative: From brief description
/lazy code "fix null pointer exception in payment processing"
# ✓ Quick fix on current branch
# ✓ Tests added
# ✓ Committed

# 2. Create PR (if not already in feature branch)
# Manual: create PR from current branch
```

**Timeline:** ~15-30 minutes

**Artifacts:**
- 1 commit
- 1 PR (if needed)
- Closed issue

---

### Documentation Update Workflow

**Scenario:** Document a new API module.

```bash
# 1. Generate API documentation
/lazy docs --format api src/api/

# ✓ Documentation agent analyzes module
# ✓ Generates API reference in docs/api/
# ✓ Creates endpoint documentation
# ✓ Adds usage examples

# 2. Update README
/lazy docs --format readme

# ✓ Adds API section to README
# ✓ Links to detailed docs
# ✓ Updates table of contents

# 3. Commit and PR
git add docs/ README.md
git commit -m "docs: add API documentation for new module"
# Create PR manually or as part of feature story
```

**Timeline:** ~30 minutes

**Artifacts:**
- Updated API docs
- Updated README
- Usage examples

---

### Parallel Development Workflow

**Scenario:** Work on multiple stories simultaneously using git worktrees.

```bash
# 1. Set up worktrees for parallel stories
git worktree add ../project-US-3.4 feat/US-3.4-oauth2
git worktree add ../project-US-3.5 feat/US-3.5-payments

# 2. Work on Story 1 (Terminal 1)
cd ../project-US-3.4
/lazy code TASK-001
/lazy code TASK-002
# ... continue with story

# 3. Work on Story 2 (Terminal 2, parallel)
cd ../project-US-3.5
/lazy code TASK-001
/lazy code TASK-002
# ... continue with story

# 4. Review both stories
cd ../project-US-3.4
/lazy review US-3.4
# ✓ PR created for US-3.4

cd ../project-US-3.5
/lazy review US-3.5
# ✓ PR created for US-3.5

# 5. Cleanup worktrees after merge
cd ../project
git worktree remove ../project-US-3.4
git worktree remove ../project-US-3.5
```

**Benefits:**
- No branch switching
- Isolated dependencies
- True parallel development
- No merge conflicts during work

---

### Review Failure and Fix Workflow

**Scenario:** Story review finds issues that need fixing with new debug report feature.

```bash
# 1. Initial review fails
/lazy review US-3.4
# ❌ CHANGES_REQUIRED
# ✓ Generated: US-3.4-review-report.md
# Issues found:
#   - 2 CRITICAL (security validation missing, test coverage <80%)
#   - 3 WARNING (missing docstrings)
#   - 1 SUGGESTION (refactor duplicate code)

# 2. Review the debug report
cat US-3.4-review-report.md
# Shows:
# ## Summary
# Story review incomplete - 2 CRITICAL, 3 WARNING, 1 SUGGESTION issues found.
#
# ## Issues
# ### CRITICAL
# 1. Missing input validation in src/auth/oauth.py:45
# 2. Test coverage 65% (required >80%)
#
# ## Task Status
# - TASK-3.4.1: COMPLETE (committed)
# - TASK-3.4.2: COMPLETE (committed)
# - TASK-3.4.3: COMPLETE (committed)
#
# ## Next Steps
# 1. Run: /lazy fix US-3.4-review-report.md
# 2. Address CRITICAL security issue
# 3. Add missing tests for coverage
# 4. Re-run: /lazy review US-3.4

# 3. Apply fixes automatically
/lazy fix US-3.4-review-report.md
# ✓ Routes security issue to coder agent
# ✓ Routes test gap to tester agent
# ✓ Adds input validation
# ✓ Adds missing tests
# ✓ Coverage now 85%
# ✓ New commits with fixes

# 4. Re-review
/lazy review US-3.4
# ✅ APPROVED
# ✓ PR created successfully

# 5. PR merge (manual)
```

**Timeline:** ~1-2 hours for fixes

**Key Benefits:**
- Structured debug information in machine-readable format
- Clear per-task status
- Actionable next steps
- Automatic routing in `/lazy fix`

---

## Quality Pipeline (Automated)

Quality checks run automatically via PostToolUse hook after Write/Edit operations. No manual execution needed.

### Pipeline Stages

```
Write/Edit Code
      ↓
PostToolUse Hook Fires
      ↓
┌─────────────────────────────────────┐
│  Stage 1: Format (Auto-applied)     │
│  ✓ Black/Ruff (Python)              │
│  ✓ Prettier (JS/TS)                 │
│  ✓ gofmt (Go)                       │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│  Stage 2: Lint (Warns)              │
│  ⚠ Ruff (Python)                    │
│  ⚠ ESLint (JS/TS)                   │
│  ⚠ golangci-lint (Go)               │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│  Stage 3: Type Check (Warns)        │
│  ⚠ Mypy (Python)                    │
│  ⚠ TSC (TypeScript)                 │
└─────────────────────────────────────┘
      ↓
┌─────────────────────────────────────┐
│  Stage 4: Tests (If TDD)            │
│  ⚠ Pytest (Python)                  │
│  ⚠ Jest (JS/TS)                     │
│  ⚠ Go test (Go)                     │
└─────────────────────────────────────┘
      ↓
Ready for Commit
```

### Auto-Behavior

- **Format:** Always applied automatically
- **Lint/Type/Tests:** Check and warn, but don't block (except critical failures)
- **Hook-driven:** Fires after Write/Edit tools, no manual commands needed
- **Non-blocking:** Allows progress with warnings for developer review

### Manual Quality Checks

For pre-commit verification (optional):

```bash
# Format code
python scripts/format.py .

# Check linting
python scripts/lint.py .

# Check types
python scripts/type_check.py .

# Run tests
pytest tests/ -v --cov
```

---

## Agent System

LAZY_DEV follows Anthropic's context-based delegation pattern. Agents extract context from conversation naturally.

### How It Works

1. Command provides context in conversation
2. Claude reads agent description
3. Agent extracts needed information from conversation history
4. No variable substitution needed

### Available Agents

**Planning & Management:**
- `project-manager` - Creates user stories with inline tasks from briefs

**Development:**
- `coder` - Implements features (TDD optional based on project)
- `tester` - Writes comprehensive tests
- `refactor` - Improves code quality

**Quality & Review:**
- `reviewer` - Reviews code for complex tasks only
- `reviewer-story` - Reviews complete stories with full context

**Documentation & Cleanup:**
- `documentation` - Generates/updates docs in multiple formats
- `cleanup` - Removes dead code and unused imports
- `research` - Fetches documentation and examples

**Agent Delegation:** Automatic based on command context and agent descriptions.

---

## Hook System

LAZY_DEV uses 3 hooks at strategic automation points:

### 1. UserPromptSubmit Hook

**Fires:** Before EVERY command execution

**Purpose:**
- Inject context pack (architecture patterns, team conventions)
- Select output style (table/list/code/prose)
- Trigger memory auto-persistence for durable facts

**Example:**
```
User: /lazy plan "Add payments"
  ↓
Hook enriches with:
  - Architecture: adapter pattern, repository pattern
  - Security: OWASP considerations
  - Testing: Optional TDD (if project uses it)
  - Performance: async patterns
  ↓
Enriched prompt → command
```

### 2. PostToolUse Hook

**Fires:** After Write/Edit tool operations

**Purpose:**
- Auto-formatting (Black/Ruff/Prettier if configured)
- Quality checks (lint, type, tests if TDD)
- Memory persistence suggestions
- Metric collection

**Example:**
```
After Write/Edit:
  ↓
Format code (Black/Ruff)
  ↓
Run quality checks (lint → type → tests)
  ↓
Code validated, warnings shown
```

### 3. Stop Hook

**Fires:** When session ends or task completes

**Purpose:**
- Quality gate logging
- TDD enforcement validation
- Metrics summary

---

## MCP Memory Integration

### Project-Specific Memory Storage

LAZY_DEV integrates with MCP Memory to persist knowledge graph per project.

**What Gets Persisted:**
- Service ownership (`service:api owned_by person:alice`)
- Repository information (`repo:org/api endpoint:https://api.example.com`)
- Architecture decisions
- Dependency relationships
- Team conventions

**Storage Location:**
- `<PROJECT_ROOT>/.claude/memory/memory.jsonl`
- Each project has isolated knowledge graph
- Persists across sessions within same project

**How It Works:**

1. **Auto-Detection:** UserPromptSubmit hook detects durable facts and persists automatically
2. **Manual Persistence:** Use `/lazy memory-graph "statement"`
3. **Context Injection:** Relevant memories injected into prompts automatically

**Configuration:**

```json
// .claude/.mcp.json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "env": {
        "MEMORY_FILE_PATH": ".claude/memory/memory.jsonl"
      }
    }
  }
}
```

**Verify Connectivity:**
```bash
/lazy memory-check
```

See [MEMORY.md](./MEMORY.md) for detailed documentation.

---

## Development Guidelines

### When Adding New Code

1. **Follow TDD (if required):**
   - RED: Write failing test
   - GREEN: Minimal implementation
   - REFACTOR: Improve code quality

2. **Type Hints Required:**
   ```python
   def process_task(task_id: str, options: Dict[str, Any]) -> Dict[str, Any]:
       """Process a task with given options."""
       pass
   ```

3. **Docstrings Required (Google Style):**
   ```python
   def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
       """Execute command with provided arguments.

       Args:
           args: Command arguments dictionary

       Returns:
           Execution results with status and output

       Raises:
           ValueError: If required arguments missing
       """
   ```

4. **Quality Checks (Automated via PostToolUse hook):**
   - Format: Auto-applied
   - Lint: Auto-checked, warns if issues
   - Type: Auto-checked, warns if issues
   - Tests: Auto-run if TDD enabled

### When Creating New Agents

1. Create in `.claude/agents/my-agent.md`
2. Use YAML frontmatter + Markdown prompt
3. Clear description for auto-delegation
4. Specify required tools
5. Document in SUB_AGENTS.md

**Template:**
```yaml
---
name: my-agent
description: Clear, action-oriented description. Use when [context].
tools: Read, Write, Edit
model: sonnet
---

You are the [Role] Agent for LAZY-DEV-FRAMEWORK.

When invoked:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Output Format:
[Expected deliverables]
```

### When Creating New Commands

1. Create in `.claude/commands/my-command.md`
2. Follow 5-section structure:
   - **When to Use**: Clear usage criteria
   - **Requirements**: Prerequisites
   - **Execution**: Step-by-step process
   - **Validation**: Success criteria
   - **Examples**: Usage examples

3. Test thoroughly
4. Document in README.md

---

## Environment Variables

### Required

```bash
# Model for prompt enrichment
export ENRICHMENT_MODEL=claude-3-5-haiku
```

### Optional

```bash
# Strict TDD enforcement
export LAZYDEV_ENFORCE_TDD=1
export LAZYDEV_MIN_TESTS=3

# Project-specific memory storage
export MEMORY_FILE_PATH=.claude/memory/memory.jsonl

# Disable features
export LAZYDEV_DISABLE_MEMORY_SKILL=1  # No auto-memory
export LAZYDEV_DISABLE_STYLE=1         # No output styling
```

**Windows (PowerShell):**
```powershell
$env:ENRICHMENT_MODEL = "claude-3-5-haiku"
$env:MEMORY_FILE_PATH = ".claude/memory/memory.jsonl"
```

---

## Troubleshooting

### Common Issues

**1. Quality Pipeline Fails**
```bash
# Auto-fix formatting
python scripts/format.py .

# Check specific issues
python scripts/lint.py .      # Linting
python scripts/type_check.py . # Type errors
pytest tests/ -v               # Test failures
```

**2. Agent Not Delegating**
- Check agent description is clear and action-oriented
- Verify YAML frontmatter format
- Ensure conversation provides context
- Review `.claude/data/logs/` for errors

**3. MCP Memory Not Working**
```bash
# Verify Node.js installed
node --version

# Test MCP server
npx -y @modelcontextprotocol/server-memory

# Check configuration
cat .claude/.mcp.json

# Verify memory storage directory exists
ls -la .claude/memory/
```

**4. GitHub PR Creation Fails**
```bash
# Authenticate
gh auth login
gh auth status

# Set default repo
gh repo set-default
```

**5. Task Not Found**
```bash
# Check story files exist
ls -la ./project-management/US-STORY/*/US-story.md

# Search for task manually
grep -r "TASK-003" ./project-management/US-STORY
```

**6. Tests Not Running**
```bash
# Check test framework installed
pytest --version  # or: npm test

# Check TDD configuration
cat CLAUDE.md | grep -i tdd
echo $LAZYDEV_ENFORCE_TDD
```

---

## Tips & Best Practices

### Command Selection

**Use `/lazy plan` when:**
- Starting a new feature (more than 1 hour of work)
- Need structured approach with multiple tasks
- Want GitHub issue tracking
- Team collaboration required

**Use `/lazy code` when:**
- Quick fixes or small features (<1 hour)
- Already have a story/task to implement
- Working from GitHub issues
- Iterating on existing code

**Use `/lazy review` when:**
- All story tasks are complete
- Ready to create PR
- Want comprehensive story validation
- Need quality assurance before merge

**Use `/lazy docs` when:**
- Adding new public APIs
- Feature is complete but undocumented
- Onboarding new team members
- Compliance requires documentation

### Workflow Optimization

**Commit Strategy:**
- One commit per task (atomic, revertable)
- One PR per story (cohesive, reviewable)
- Never commit incomplete work

**Branch Strategy:**
- Feature branches for stories (`feat/US-X.Y-name`)
- Current branch for quick fixes
- Use worktrees for parallel development

**Quality Strategy:**
- Let PostToolUse hook handle quality (automatic)
- Fix issues incrementally (not all at once)
- Review complex tasks during implementation
- Review entire story before PR

**Memory Strategy:**
- Let auto-detection handle most facts
- Manually persist critical decisions
- Query memory before starting related work
- Keep memory entries atomic and dated

**Review & Fix Strategy:**
- Read the debug report completely
- Fix CRITICAL issues first
- Then WARNING, then SUGGESTION
- Use `/lazy fix` for automatic routing
- Re-review to confirm all issues resolved

### Performance Tips

**Token Optimization:**
- `context-packer` skill reduces token usage automatically
- Link to files/lines instead of pasting large blocks
- Use memory graph for persistent context (no re-prompting)

**Parallel Work:**
- Use git worktrees for simultaneous stories
- Run `/lazy clean` and `/lazy docs` during reviews
- Start next story planning while current story is in review

**Review Optimization:**
- Read debug report to prioritize fixes
- Use `/lazy fix` to route fixes automatically
- Re-review only after all criticals are fixed

---

## File Organization

```
project-root/
├── .claude/                    # Framework installation
│   ├── agents/                 # 10 specialized agents
│   ├── commands/               # 8 commands
│   ├── hooks/                  # 3 hooks (Python)
│   ├── skills/                 # 20+ skills
│   ├── memory/                 # Project-specific memory
│   │   └── memory.jsonl        # Knowledge graph storage
│   ├── .mcp.json              # MCP Memory config
│   └── settings.json          # Claude Code settings
│
├── project-management/
│   └── US-STORY/
│       └── US-X.Y-name/
│           └── US-story.md    # User story with inline tasks
│
└── US-X.Y-review-report.md    # Generated by review command (if issues)
```

---

## Key Principles

1. ✅ **Command-First**: Use commands, not ad-hoc prompts
2. ✅ **Quality-First**: Pipeline enforces standards automatically
3. ✅ **Context-Based**: Agents extract from conversation naturally
4. ✅ **Commit-Per-Task**: One commit per task, one PR per story
5. ✅ **TDD-Optional**: Tests required only if project uses TDD
6. ✅ **Memory-Persistent**: Durable facts stored in MCP (project-isolated)
7. ✅ **Auto-Formatting**: Code formatted automatically via hook
8. ✅ **Security-Aware**: OWASP checks built-in for sensitive code
9. ✅ **Smart-Defaults**: Infer tests, reviews, complexity from context
10. ✅ **Flexible-Input**: Accept stories, tasks, briefs, or issues

---

## Additional Resources

- [SUB_AGENTS.md](./SUB_AGENTS.md) - Agent specifications
- [MEMORY.md](./MEMORY.md) - MCP Memory documentation
- [CHANGELOG.md](./CHANGELOG.md) - Version history

---

## Version

**Framework Version:** 2.2.0
**Last Updated:** 2025-10-30
**Status:** Production-Ready

---

**LAZY_DEV** - Be lazy, but consistently excellent.
