# LAZY_DEV Framework

> A comprehensive Claude Code framework for pragmatic developers who want automated workflows, quality enforcement, and persistent knowledge management.

**Version**: 2.0.0
**License**: MIT
**Status**: Production-Ready

---

## Table of Contents

1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Core Features](#core-features)
4. [Installation & Setup](#installation--setup)
5. [Usage Guide](#usage-guide)
6. [Architecture](#architecture)
7. [Pros and Cons](#pros-and-cons)
8. [Alignment with Anthropic Best Practices](#alignment-with-anthropic-best-practices)
9. [Contributing & Development](#contributing--development)
10. [Troubleshooting](#troubleshooting)

---

## Overview

### What is LAZY_DEV?

LAZY_DEV is a **command-first AI framework** for Claude Code that automates the entire software development lifecycle: from voice-driven feature planning to automated PR creation. It combines **curated skills**, **protective hooks**, **specialized agents**, and **MCP Memory integration** into a cohesive workflow that enforces quality while minimizing manual work.

### What Problem Does It Solve?

Modern AI-assisted development suffers from:
- **Inconsistent quality** - No enforcement of format, lint, type, test standards
- **Lost context** - Important project knowledge forgotten between sessions
- **Manual workflow** - Repetitive tasks like creating stories, committing, reviewing
- **Fragmented tools** - Hooks, agents, skills scattered across multiple projects
- **Re-prompting fatigue** - Constantly explaining the same context

LAZY_DEV solves these by providing a **turnkey framework** with:
- Automatic quality pipeline (format → lint → type → test)
- Persistent knowledge graph via MCP Memory
- End-to-end automation (voice → feature → tasks → code → PR)
- Protective hooks that prevent dangerous operations
- Specialized agents that delegate work intelligently

### Key Philosophy

**"Be lazy, but consistently excellent"**

LAZY_DEV automates the mundane so you focus on the creative. It enforces discipline (quality gates, TDD, security checks) while removing friction (auto-formatting, auto-commits, auto-PRs).

---

## How It Works

### Command-First Architecture

Everything in LAZY_DEV is triggered by simple commands:

```bash
/lazy create-feature "Add OAuth2 authentication"
/lazy task-exec TASK-1.1
/lazy story-review US-3.4
/lazy memory-graph "service:api owned_by person:alice"
```

**No complex configuration files.** No YAML orchestration. Just commands that do what they say.

### Automatic Agent Delegation

LAZY_DEV includes 10 specialized agents (project-manager, coder, reviewer, tester, etc.) that are **automatically invoked based on context**:

- **Project Manager** - Creates US-stories and tasks from feature briefs
- **Coder** - Implements features following TDD principles
- **Reviewer** - Evaluates code for security, readability, performance
- **Tester** - Generates comprehensive test suites
- **Research** - Fetches documentation and examples
- **Documentation** - Creates/updates project docs
- **Refactor** - Improves code quality systematically
- **Cleanup** - Removes dead code and optimizes
- **Task Enhancer** - Enriches task descriptions with context
- **Story Reviewer** - Evaluates complete feature implementations

**You don't manually invoke agents.** Commands orchestrate them automatically based on workflow stage.

### Quality Pipeline

Every code change goes through mandatory quality gates:

```
Format (Black/Ruff) → Lint (Ruff) → Type (Mypy) → Test (Pytest)
        ↓                  ↓             ↓            ↓
      PASS              PASS          PASS         PASS
        ↓                  ↓             ↓            ↓
                    Git Commit Allowed
```

**Fail-fast enforcement**: If any stage fails, the workflow stops. No broken code reaches your repository.

### Hook System Integration

LAZY_DEV uses 4 strategic hooks for automation:

1. **UserPromptSubmit** - Adds context pack, selects output style, auto-triggers Memory
2. **PreToolUse** - Safety checks (blocks dangerous rm, force-push to main)
3. **PostToolUse** - Auto-formatting, memory suggestions
4. **Stop** - Quality gate logging, TDD enforcement

### Workflow: Feature → Tasks → Implementation → Review → PR

```mermaid
flowchart TD
    A[Voice Input] --> B[STT Transcription]
    B --> C[Prompt Enhancement]
    C --> D[/lazy create-feature]
    D --> E{Sync to GitHub?}
    E -->|yes| E1[Create Issue + Sub-issues]
    E -->|no| E2[Local US/TASK Files]
    E1 --> F
    E2 --> F
    F[/lazy task-exec]
    F --> G[TDD: RED → GREEN → REFACTOR]
    G --> H[Quality Pipeline]
    H --> I[Code Review]
    I --> J{Approved?}
    J -->|yes| K[Git Commit]
    J -->|no| G
    K --> L[More Tasks?]
    L -->|yes| F
    L -->|no| M[/lazy story-review]
    M --> N{Story Approved?}
    N -->|yes| O[Auto PR Created]
    N -->|no| P[Fix Review Report]
    P --> F
```

**Key Points**:
- One commit per task (atomic changes)
- One PR per user-story (cohesive feature)
- Automatic review and quality checks at each stage
- MCP Memory persistence throughout

---

## Core Features

### 10 Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `/lazy create-feature` | Generate US-story + tasks from brief | `create-feature "Add payment processing"` |
| `/lazy task-exec` | Execute a single task with TDD | `task-exec TASK-1.1` |
| `/lazy story-review` | Review entire story, create PR | `story-review US-3.4` |
| `/lazy story-fix-review` | Apply fixes from review report | `story-fix-review report.md` |
| `/lazy documentation` | Generate/update docs | `documentation README.md` |
| `/lazy cleanup` | Remove dead code, optimize | `cleanup src/` |
| `/lazy memory-graph` | Persist knowledge to MCP | `memory-graph "endpoint:api.example.com"` |
| `/lazy memory-check` | Verify MCP connectivity | `memory-check` |

### 10 Specialized Agents

All agents use **automatic delegation** - Claude invokes them based on context.

1. **project-manager** - Creates comprehensive US-stories and tasks
2. **task-enhancer** - Enriches tasks with security, testing, edge cases
3. **coder** - Implements features following TDD (RED → GREEN → REFACTOR)
4. **reviewer** - Code review with security, performance, readability checks
5. **reviewer-story** - Evaluates complete story implementation
6. **tester** - Generates unit, integration, and edge case tests
7. **research** - Fetches docs, patterns, examples from web/codebase
8. **documentation** - Creates/updates README, API docs, guides
9. **refactor** - Improves code quality systematically
10. **cleanup** - Removes dead code, optimizes imports, fixes warnings

**Format**: YAML frontmatter + Markdown system prompt (Anthropic standard)

### 17 Skills

Skills provide reusable patterns and guidance:

| Category | Skills |
|----------|--------|
| **Planning** | story-traceability, task-slicer, ac-expander |
| **Development** | test-driven-development, diff-scope-minimizer, semantic-release |
| **Quality** | code-review-checklist, refactoring-pipeline, security-scanner |
| **Documentation** | readme-template, api-doc-generator, changelog-builder |
| **Integration** | gh-issue-sync, mcp-memory-router, output-style-selector |
| **Testing** | test-coverage-enforcer, edge-case-generator |

**Usage**: Referenced in agent prompts and command instructions

### 4 Hooks for Automation

| Hook | Event | Purpose | Can Block? |
|------|-------|---------|------------|
| **UserPromptSubmit** | Before Claude processes input | Context pack + style selector + memory trigger | Yes |
| **PreToolUse** | Before tool execution | Safety checks, audit logging | Yes |
| **PostToolUse** | After tool completion | Auto-formatting, memory suggestions | No |
| **Stop** | When Claude finishes | Quality gate logging, TDD enforcement | Yes |

**Safety Features**:
- Blocks `sudo` commands (unless `LAZYDEV_ALLOW_SUDO=1`)
- Blocks `rm -rf /` and similar dangerous operations
- Blocks force-push to main/master branches
- Blocks operations on sensitive paths (`.git`, `.env`)

### MCP Memory Integration

Persistent knowledge graph for durable facts:

```bash
# Store entities and relationships
/lazy memory-graph "service:api owned_by person:alice; repo: org/api; endpoint: https://api.example.com"

# Check connectivity
/lazy memory-check
```

**Auto-triggers**:
- UserPromptSubmit hook detects durable facts in prompts
- Automatically injects Memory Graph guidance
- Suggests persisting knowledge after tool use
- Maintains project knowledge across sessions

**MCP Tools** (9 total):
- `mcp__memory__create_entities` / `delete_entities`
- `mcp__memory__create_relations` / `delete_relations`
- `mcp__memory__add_observations` / `delete_observations`
- `mcp__memory__read_graph` / `search_nodes` / `open_nodes`

---

## Installation & Setup

### Prerequisites

- **Python 3.11+** - `python --version`
- **Claude Code CLI** - Latest version
- **uv** package manager - `pip install uv` or [install script](https://astral.sh/uv/install.sh)
- **git** - For version control
- **gh CLI** - For GitHub integration (`winget install GitHub.cli` or `brew install gh`)
- **Node.js** - For MCP Memory server (optional but recommended)

### Step 1: Install LAZY_DEV

**Option A: Via Plugin Marketplace** (when available)
```bash
# In Claude Code
/plugin marketplace add therouxe/lazy-marketplace
/plugin install lazy@lazy-marketplace
```

**Option B: Manual Installation**
```bash
# Clone or copy LAZY_DEV directory to your project
cp -r LAZY_DEV/.claude/ .claude/
```

### Step 2: Configure Environment Variables

Create `.env` or set environment variables:

```bash
# Required for pre-prompt enrichment
export ENRICHMENT_MODEL=claude-3-5-haiku

# Optional: Hook behavior
export LAZYDEV_LOG_DIR=.claude/data/logs
export LAZYDEV_ENFORCE_TDD=1  # Enforce TDD workflow
export LAZYDEV_MIN_TESTS=3    # Minimum tests per task

# Optional: Context pack optimization
export LAZYDEV_CONTEXT_PACK_BUDGET_MS=200

# Optional: Disable features
export LAZYDEV_DISABLE_MEMORY_SKILL=1  # Disable auto-memory
export LAZYDEV_DISABLE_STYLE=1         # Disable output style
```

**PowerShell** (Windows):
```powershell
$env:ENRICHMENT_MODEL = "claude-3-5-haiku"
$env:LAZYDEV_ENFORCE_TDD = "1"
```

### Step 3: Enable MCP Memory (Recommended)

```bash
# Copy MCP config template to workspace root
cp LAZY_DEV/.claude/.mcp.json .mcp.json

# Verify Node.js is installed
node --version

# Test MCP server
npx -y @modelcontextprotocol/server-memory
```

### Step 4: Authenticate with GitHub (For PR creation)

```bash
# Authenticate gh CLI
gh auth login

# Verify authentication
gh auth status

# Set default repository
gh repo set-default
```

### Step 5: Verify Installation

```bash
# In Claude Code, list commands
/help

# Should show:
# /lazy create-feature
# /lazy task-exec
# /lazy story-review
# /lazy memory-check
# ... etc

# Check MCP connectivity
/lazy memory-check

# Should output: ✓ MCP Memory server is connected
```

### First-Time Setup Complete!

You're ready to use LAZY_DEV. Try:
```bash
/lazy create-feature "Add user authentication with email and password"
```

---

## Usage Guide

### Basic Workflow Example

Let's build a complete feature from voice input to merged PR.

#### 1. Voice Input (Optional STT Enhancement)

```bash
# Speak: "I need to add payment processing with Stripe integration"
# STT transcribes and OpenAI system prompt structures it
```

#### 2. Create Feature Package

```bash
/lazy create-feature "Add payment processing with Stripe integration"
```

**What happens**:
- Pre-prompt enrichment adds architecture, security, testing context
- Project-Manager agent creates:
  - `US-story.md` with Story ID, acceptance criteria, security checklist
  - `TASK-1.1.md`, `TASK-1.2.md`, etc. (individual task files)
- Optionally syncs to GitHub as issue + sub-issues

**Output**:
```
✓ Created US-story.md (Story ID: US-3.4)
✓ Created TASK-1.1.md - Setup Stripe SDK
✓ Created TASK-1.2.md - Implement payment endpoint
✓ Created TASK-1.3.md - Add webhook handler
✓ Created TASK-1.4.md - Create integration tests

Total: 4 tasks, estimated 12 hours
```

#### 3. Execute Tasks (One at a Time)

```bash
/lazy task-exec TASK-1.1
```

**What happens**:
1. **Research** (if needed): Fetches Stripe docs, code examples
2. **TDD Cycle**:
   - RED: Coder writes failing tests
   - GREEN: Coder implements minimal code to pass
   - REFACTOR: Coder improves code quality
3. **Quality Pipeline**:
   - Format check (Black + Ruff) → Auto-fix
   - Lint check (Ruff) → Report issues
   - Type check (Mypy) → Validate types
   - Test suite (Pytest) → Run all tests
4. **Code Review**: Reviewer checks security, readability, performance
5. **Git Commit** (if approved): Atomic commit with conventional format

**Output**:
```
🔍 Researching Stripe SDK integration...
✓ Documentation cached

🤖 TDD Cycle:
  ✓ RED: Created tests/test_stripe.py (3 failing tests)
  ✓ GREEN: Implemented stripe_client.py (tests pass)
  ✓ REFACTOR: Extracted config, improved error handling

📊 Quality Pipeline:
  ✓ Format: PASS (auto-fixed 2 files)
  ✓ Lint: PASS
  ✓ Type: PASS
  ✓ Test: PASS (Coverage: 92%)

🔍 Code Review:
  ✓ Security: API key handling secure
  ✓ Readability: Clear naming, good comments
  ✓ Performance: No issues

  Review: APPROVED

💾 Git Commit:
  ✓ Committed: feat(payment): setup Stripe SDK (a1b2c3d4)

✅ TASK-1.1 complete - Ready for next task
```

#### 4. Continue with Remaining Tasks

```bash
/lazy task-exec TASK-1.2
/lazy task-exec TASK-1.3
/lazy task-exec TASK-1.4
```

Each task follows the same cycle: TDD → Quality → Review → Commit

#### 5. Review Entire Story

```bash
/lazy story-review US-3.4
```

**What happens**:
- Story Reviewer evaluates all tasks against acceptance criteria
- Checks security checklist completion
- Verifies test coverage across all tasks
- Either approves (creates PR) or provides fix report

**Output (if approved)**:
```
📖 Loading story: Add Payment Processing (US-3.4)
✓ 4 tasks completed

🔍 Evaluating against acceptance criteria:
  ✓ Stripe SDK integrated
  ✓ Payment endpoint functional
  ✓ Webhook handler implemented
  ✓ Integration tests passing

📊 Quality Summary:
  ✓ Test coverage: 94%
  ✓ Security checklist: 100% complete
  ✓ All quality gates passed

🚀 Creating Pull Request...
  ✓ PR #42: [FEATURE] Add Payment Processing

  Reviewers: @teammate1, @teammate2
  Labels: feature, payment, needs-review

  URL: https://github.com/org/repo/pull/42

✅ Story complete!
```

#### 6. Fix Review (If Needed)

If story review finds issues:

```bash
/lazy story-fix-review review-report.md
```

Applies targeted fixes and re-runs story-review.

---

### Command Reference

#### `/lazy create-feature <brief>`

**Purpose**: Generate comprehensive US-story and individual task files

**Arguments**:
- `<brief>`: Feature description (string or file path)

**Options**:
- `--no-github`: Skip GitHub issue creation
- `--model <name>`: Override default model (default: sonnet)

**Example**:
```bash
/lazy create-feature "Add OAuth2 authentication with Google provider"
/lazy create-feature feature-brief.md
/lazy create-feature "Add search functionality" --no-github
```

**Output**:
- `US-story.md` - Complete user story
- `TASK-*.md` - Individual task files

---

#### `/lazy task-exec <task-id>`

**Purpose**: Execute a single task following TDD workflow

**Arguments**:
- `<task-id>`: Task ID (e.g., TASK-1.1) or GitHub issue number

**Options**:
- `--story <story-id>`: Specify story context
- `--with-research`: Enable research phase
- `--no-commit`: Skip auto-commit (review only)

**Example**:
```bash
/lazy task-exec TASK-1.1
/lazy task-exec TASK-1.2 --with-research
/lazy task-exec #42  # GitHub issue number
```

**Output**:
- Code implementation
- Test files
- Git commit (if approved)

---

#### `/lazy story-review <story-id>`

**Purpose**: Review complete story implementation, create PR

**Arguments**:
- `<story-id>`: Story ID (e.g., US-3.4) or file path

**Options**:
- `--no-pr`: Skip PR creation (review only)
- `--base <branch>`: PR base branch (default: main)

**Example**:
```bash
/lazy story-review US-3.4
/lazy story-review US-story.md --no-pr
/lazy story-review US-3.4 --base develop
```

**Output**:
- Pull Request (if approved)
- OR Review report with required fixes

---

#### `/lazy memory-graph <statement>`

**Purpose**: Persist knowledge to MCP Memory Graph

**Arguments**:
- `<statement>`: Entity and relationship statements

**Example**:
```bash
/lazy memory-graph "service:api owned_by person:alice"
/lazy memory-graph "repo:org/api endpoint:https://api.example.com"
/lazy memory-graph "team:backend responsible_for service:api"
```

**Output**:
- Entities created/updated in Memory Graph
- Relationships established

---

### Agent Delegation Explanation

**You don't manually invoke agents.** LAZY_DEV uses **automatic delegation** based on Anthropic best practices:

1. **Command provides context** in conversation
2. **Command description triggers** appropriate agent
3. **Agent extracts context** from conversation naturally
4. **Agent produces results** using its tools

**Example**: When you run `/lazy task-exec TASK-1.1`, the command:
1. Loads TASK-1.1.md content
2. Provides task context in conversation
3. Automatically invokes:
   - Research agent (if `--with-research` flag)
   - Coder agent (for implementation)
   - Tester agent (for test generation)
   - Reviewer agent (for code review)

**No variable substitution.** No explicit agent invocation. Just natural delegation based on context.

---

### Quality Pipeline Usage

#### Automatic Formatting (PostToolUse Hook)

Every time you edit or write a file:

```python
# .py files → Black + Ruff
# .ts/.tsx files → Prettier
# .rs files → rustfmt
# .go files → gofmt
```

**No manual formatting needed.** Happens automatically on save.

#### Quality Gates (Task-Exec)

Every task execution enforces:

```
1. Format Check → Auto-fix if possible
2. Lint Check → Report issues, block if critical
3. Type Check → Validate all type hints
4. Test Suite → Run all tests, check coverage
```

**Fail-fast**: Pipeline stops at first failure.

#### TDD Enforcement (Optional)

Set `LAZYDEV_ENFORCE_TDD=1` to require:
- Tests written BEFORE implementation
- Minimum test count (`LAZYDEV_MIN_TESTS`)
- Tests pass before commit

**Stop hook blocks** completion unless TDD requirements met.

---

## Architecture

### Directory Structure

```
LAZY_DEV/
├── .claude/
│   ├── agents/                    # 10 specialized agents
│   │   ├── project-manager.md
│   │   ├── coder.md
│   │   ├── reviewer.md
│   │   └── ... (7 more)
│   │
│   ├── commands/                  # 8 commands
│   │   ├── create-feature.md
│   │   ├── task-exec.md
│   │   ├── story-review.md
│   │   └── ... (5 more)
│   │
│   ├── hooks/                     # 4 hooks
│   │   ├── user_prompt_submit.py
│   │   ├── pre_tool_use.py
│   │   ├── post_tool_use.py
│   │   └── stop.py
│   │
│   ├── skills/                    # 17 skills
│   │   ├── test-driven-development.md
│   │   ├── memory-graph.md
│   │   ├── story-traceability.md
│   │   └── ... (14 more)
│   │
│   ├── status_lines/              # Status bar integration
│   │   └── lazy_status.sh
│   │
│   ├── .mcp.json                  # MCP Memory config template
│   └── settings.json              # Claude Code settings
│
├── scripts/                       # Utility scripts
│   ├── format.py
│   ├── lint.py
│   ├── test_runner.py
│   └── gh_wrapper.py
│
├── STT_PROMPT_ENHANCER/           # Voice-to-prompt pipeline
│   ├── main.py
│   ├── whisper_stt.py
│   └── prompt_enhancer.py
│
├── README.md                      # This file
├── SUB_AGENTS.md                  # Agent registry
├── WORKFLOW.md                    # Detailed workflow guide
├── CHANGELOG.md                   # Version history
└── LICENSE                        # MIT License
```

---

### Agent Automatic Delegation Pattern

LAZY_DEV follows **Anthropic's official pattern** for agent delegation:

**YAML Frontmatter** defines agent metadata:
```yaml
---
name: coder
description: Implements features following TDD. Use immediately after task-exec command.
tools: Read, Write, Edit, Grep, Glob, Bash
model: sonnet
---
```

**Markdown System Prompt** provides instructions:
```markdown
You are the Coder Agent for LAZY-DEV-FRAMEWORK.

When invoked:
1. Review the task description in the conversation
2. Extract acceptance criteria and technical details
3. Implement following TDD: RED → GREEN → REFACTOR
4. Create comprehensive tests
```

**Context-Based** - Agents extract information from conversation:
- No `$variable` substitution
- No explicit parameter passing
- Natural context extraction
- Tool restrictions control access

**Benefits**:
- Simpler codebase (no Template code)
- More flexible (agents search for context)
- Aligns with official best practices
- Easier to maintain and extend

---

### Hook Integration Points

```
User Input
    ↓
┌───────────────────────────────────────┐
│ UserPromptSubmit Hook                 │
│ - Context pack (file stats, git info) │
│ - Output style selector               │
│ - Memory auto-trigger                 │
└───────────────────────────────────────┘
    ↓
Command Execution
    ↓
┌───────────────────────────────────────┐
│ PreToolUse Hook                        │
│ - Safety checks (dangerous commands)   │
│ - Audit logging                        │
│ - Block if unsafe                      │
└───────────────────────────────────────┘
    ↓
Tool Execution (Edit, Write, Bash, etc.)
    ↓
┌───────────────────────────────────────┐
│ PostToolUse Hook                       │
│ - Auto-format files (Black/Prettier)   │
│ - Memory suggestions                   │
│ - Cannot block                         │
└───────────────────────────────────────┘
    ↓
Claude Finishes
    ↓
┌───────────────────────────────────────┐
│ Stop Hook                              │
│ - Quality gate logging                 │
│ - TDD enforcement (optional)           │
│ - Can force continue if needed         │
└───────────────────────────────────────┘
```

---

### Command Execution Flow

Example: `/lazy task-exec TASK-1.1`

```
1. Command Parsing
   ↓
2. UserPromptSubmit Hook
   - Adds context pack
   - Detects TDD signals
   ↓
3. Load Task File (TASK-1.1.md)
   ↓
4. PreToolUse Hook (if tools used)
   - Check safety
   ↓
5. Research Agent (optional)
   - Fetch docs/examples
   ↓
6. Coder Agent
   - TDD: RED → GREEN → REFACTOR
   ↓
7. Quality Pipeline
   a. Format (PostToolUse hook + scripts)
   b. Lint (scripts)
   c. Type (scripts)
   d. Test (scripts)
   ↓
8. Reviewer Agent
   - Security, readability, performance
   ↓
9. Git Commit (if approved)
   - Conventional commit format
   ↓
10. Stop Hook
    - Log completion
    - Enforce TDD if enabled
```

---

## Pros and Cons

### Pros

#### Consistent Quality Enforcement
- **Mandatory pipeline**: Format → Lint → Type → Test (no shortcuts)
- **Fail-fast**: Stops at first failure, clear error reporting
- **Auto-formatting**: PostToolUse hook formats on every save
- **TDD enforcement**: Optional but powerful for test discipline
- **Security checklists**: Built into every task and story

#### Automatic Agent Delegation (Anthropic Pattern)
- **Context-based**: Agents extract from conversation (no variables)
- **Intelligent routing**: Claude selects agents based on descriptions
- **Simpler codebase**: No Template substitution code (500+ lines saved)
- **More flexible**: Agents search for context they need
- **Official standard**: Matches Anthropic best practices exactly

#### Comprehensive Testing Requirements
- **80% coverage minimum** enforced
- **Unit + integration + edge case** tests required
- **TDD workflow**: RED → GREEN → REFACTOR cycle
- **Test-first culture**: Tests written before implementation

#### Git Workflow Automation
- **Atomic commits**: One commit per task
- **Conventional format**: Standardized commit messages
- **Auto-PR creation**: Story review creates PRs automatically
- **GitHub integration**: Syncs issues and sub-issues

#### Prompt Enrichment for Better Results
- **Pre-prompt hook**: Adds architecture, security, testing context
- **Model**: Uses Haiku for cost efficiency
- **Voice input**: Optional STT pipeline for hands-free prompting
- **Context pack**: Automatic file stats, git info, project structure

#### Memory Persistence via MCP
- **Durable facts**: Persists across sessions
- **Graph relationships**: Entities and relations
- **Auto-triggers**: Detects knowledge to persist
- **Search and query**: Find information quickly

### Cons

#### Learning Curve for New Users
- **Many commands**: 8 commands with various options
- **Complex workflow**: Create-feature → task-exec → story-review chain
- **Hook behavior**: Understanding when hooks fire and what they do
- **MCP setup**: Requires Node.js and MCP server configuration
- **Mitigation**: Comprehensive docs (this README, WORKFLOW.md), examples

#### Requires Discipline (Quality Gates Block Progress)
- **Can be frustrating**: Blocked by format/lint/type/test failures
- **Time investment**: Quality checks add overhead to each task
- **No bypass**: Quality gates are mandatory (by design)
- **Mitigation**: Auto-formatting reduces friction, clear error messages guide fixes

#### Python 3.11+ Only
- **Version constraint**: Older Python versions not supported
- **Type hints required**: Mypy validation needs proper typing
- **Mitigation**: Python 3.11+ widely available, easy to install with pyenv/conda

#### Haiku API Costs for Enrichment
- **Per-prompt cost**: Pre-prompt enrichment calls Haiku API
- **Cost estimate**: ~$0.001-0.005 per prompt (cheap but adds up)
- **Mitigation**: Can disable with `unset ENRICHMENT_MODEL`, or use sparingly

#### Windows Path Handling Complexity
- **Cross-OS scripts**: Hooks and scripts must work on Windows/Linux/macOS
- **Path separators**: Backslash vs forward slash handling
- **Line endings**: CRLF vs LF differences
- **Mitigation**: Use `pathlib.Path` for cross-OS compatibility, test on all platforms

---

## Alignment with Anthropic Best Practices

LAZY_DEV closely aligns with official Anthropic guidance for Claude Code workflows:

### ✅ Conversation Context (Not Variable Substitution)

**Anthropic Pattern**:
> "Subagents operate on conversation context. System prompts are static instructions. Variables passed through conversation flow."

**LAZY_DEV Implementation**:
- Agents extract context from conversation naturally
- No `$variable` Template substitution
- Commands provide context, agents read it
- Matches official examples exactly

**Example**:
```markdown
# Agent prompt (official pattern)
When invoked:
1. Review the task description in the conversation above
2. Extract acceptance criteria
3. Implement the solution
```

### ✅ Automatic Delegation via Agent Descriptions

**Anthropic Pattern**:
> "Use clear, action-oriented descriptions. Include 'Use PROACTIVELY' triggers."

**LAZY_DEV Implementation**:
```yaml
---
description: Implements features following TDD. Use immediately after task-exec command.
---
```

Claude intelligently routes based on these descriptions.

### ✅ Hook-Based Automation

**Anthropic Pattern**:
> "Use hooks for automatic formatting, safety checks, and logging. PostToolUse for non-blocking automation."

**LAZY_DEV Implementation**:
- PostToolUse: Auto-formatting (Black, Ruff, Prettier)
- PreToolUse: Safety checks (dangerous commands blocked)
- UserPromptSubmit: Context enrichment
- Stop: Quality gate logging

### ✅ Standard YAML+Markdown Agent Format

**Anthropic Pattern**:
```yaml
---
name: agent-name
description: Clear description
tools: Tool1, Tool2
model: sonnet
---

System prompt in markdown...
```

**LAZY_DEV Implementation**: Exact match for all 10 agents

### ✅ Context-Aware Agent Selection

**Anthropic Pattern**:
> "Claude decides which agent to use based on context and agent descriptions."

**LAZY_DEV Implementation**:
- Commands describe intent clearly
- Agents self-identify via descriptions
- No hardcoded agent selection in code
- Natural delegation based on conversation

---

## Contributing & Development

### How to Add New Agents

1. **Create agent file** in `.claude/agents/`:
```markdown
---
name: my-agent
description: Does something specific. Use when [trigger].
tools: Read, Write
model: sonnet
---

You are the My-Agent for LAZY-DEV-FRAMEWORK.

When invoked:
1. Extract context from conversation
2. Do the thing
3. Produce results
```

2. **Reference in commands** (if needed):
```markdown
The my-agent will be automatically invoked based on context.
```

3. **Test agent** by invoking relevant command

4. **Document in SUB_AGENTS.md**

### How to Add New Commands

1. **Create command file** in `.claude/commands/`:
```markdown
# /lazy my-command

Brief description of what this command does.

## When to Use
[Context and triggers]

## Requirements
[Prerequisites]

## Execution
Step-by-step instructions for Claude.

## Validation
How to verify success.

## Examples
Concrete usage examples.
```

2. **Test command** in Claude Code:
```bash
/lazy my-command
```

3. **Document in README** (this file)

### Testing Guidelines

**Quality Standards**:
- All Python code: Type hints, docstrings, formatted with Black/Ruff
- Test coverage: Minimum 80%
- Cross-OS: Test on Windows, Linux, macOS
- Error handling: Graceful failures, clear messages

**Test Structure**:
```python
# tests/test_feature.py
def test_feature():
    # Arrange
    input_data = {...}

    # Act
    result = execute(input_data)

    # Assert
    assert result["status"] == "success"
    assert result["output"] is not None
```

**Run tests**:
```bash
pytest tests/ -v --cov
```

### Documentation Standards

**CLAUDE.md** (if creating):
- Keep under 200 lines
- Essentials only (quick reference)
- Link to detailed docs

**Agent documentation**:
- Include in agent file itself (YAML frontmatter)
- Document in SUB_AGENTS.md registry

**Command documentation**:
- Follow 5-section structure (When/Requirements/Execution/Validation/Examples)
- Include concrete examples

---

## Troubleshooting

### Common Issues and Fixes

#### Problem: ENRICHMENT_MODEL not set

**Symptoms**:
```
⚠ Pre-prompt enrichment skipped: ENRICHMENT_MODEL not set
```

**Solution**:
```bash
export ENRICHMENT_MODEL=claude-3-5-haiku
# Or disable enrichment entirely
unset ENRICHMENT_MODEL
```

---

#### Problem: MCP Memory server not connecting

**Symptoms**:
```
❌ MCP Memory server is NOT connected
```

**Solution**:
```bash
# Check Node.js installed
node --version

# Test MCP server manually
npx -y @modelcontextprotocol/server-memory

# Verify .mcp.json exists
ls -la .mcp.json

# Copy template if missing
cp LAZY_DEV/.claude/.mcp.json .mcp.json
```

---

#### Problem: Quality pipeline fails (format/lint/type)

**Symptoms**:
```
❌ Format check failed: Line too long
❌ Lint check failed: Unused import
❌ Type check failed: Missing type hint
```

**Solution**:
```bash
# Auto-fix formatting
python scripts/format.py lazy_dev/

# Fix lint issues manually
python scripts/lint.py lazy_dev/

# Add type hints
python scripts/type_check.py lazy_dev/

# Re-run task-exec
/lazy task-exec TASK-1.1
```

---

#### Problem: Agent delegation not working

**Symptoms**:
- Agents not invoked automatically
- Context not extracted correctly

**Solution**:
1. **Check agent description** - Must be clear and action-oriented
2. **Verify agent file** - Correct YAML frontmatter format
3. **Provide context** - Ensure command provides context in conversation
4. **Review logs** - Check `.claude/data/logs/` for errors

---

#### Problem: Tests not enforced (TDD mode)

**Symptoms**:
- Task commits without tests
- Stop hook doesn't block

**Solution**:
```bash
# Enable TDD enforcement
export LAZYDEV_ENFORCE_TDD=1
export LAZYDEV_MIN_TESTS=3

# Verify in command output
# Should see: "TDD enforcement: ENABLED"
```

---

#### Problem: GitHub PR creation fails

**Symptoms**:
```
❌ gh: authentication required
❌ gh: command not found
```

**Solution**:
```bash
# Install gh CLI
# Windows:
winget install GitHub.cli
# macOS:
brew install gh
# Linux:
sudo apt install gh

# Authenticate
gh auth login

# Verify
gh auth status

# Set default repo
gh repo set-default
```

---

#### Problem: Git conflicts during story review

**Symptoms**:
```
❌ Story review failed: Git conflict detected
```

**Solution**:
```bash
# Fetch latest main
git fetch origin main

# Rebase feature branch
git rebase origin/main

# Resolve conflicts manually
# Edit conflicted files, then:
git add <files>
git rebase --continue

# Re-run quality pipeline
pytest tests/ -v

# Retry story review
/lazy story-review US-3.4
```

---

### Environment Setup Problems

#### Problem: Python version too old

**Symptoms**:
```
Error: Python 3.11+ required
```

**Solution**:
```bash
# Install Python 3.11+ with pyenv
pyenv install 3.11
pyenv local 3.11

# Or with conda
conda create -n lazy python=3.11
conda activate lazy

# Verify
python --version
```

---

#### Problem: uv not installed

**Symptoms**:
```
bash: uv: command not found
```

**Solution**:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip
pip install uv

# Verify
uv --version
```

---

### Getting Help

1. **Check documentation**:
   - README.md (this file) - Overview and setup
   - WORKFLOW.md - Detailed workflow guide
   - SUB_AGENTS.md - Agent registry and specs

2. **Review logs**:
   - `.claude/data/logs/` - Hook execution logs
   - Check timestamps and error messages

3. **Test components**:
   - Test hooks manually: `echo '{"test": true}' | python .claude/hooks/hook.py`
   - Test MCP: `npx -y @modelcontextprotocol/server-memory`
   - Test gh CLI: `gh auth status`

4. **Ask for help**:
   - GitHub Issues: Report bugs or request features
   - Discussions: Ask questions, share workflows

---

## Next Steps

Now that you understand LAZY_DEV:

1. **Try the basic workflow**:
   ```bash
   /lazy create-feature "Add user authentication"
   /lazy task-exec TASK-1.1
   /lazy story-review US-3.4
   ```

2. **Enable strict mode** (recommended):
   ```bash
   export LAZYDEV_ENFORCE_TDD=1
   export LAZYDEV_MIN_TESTS=3
   ```

3. **Explore advanced features**:
   - Voice input with STT enhancer
   - MCP Memory persistence
   - Parallel task execution (git worktrees)

4. **Read detailed guides**:
   - WORKFLOW.md - Complete workflow reference
   - SUB_AGENTS.md - Agent details and patterns

---

## Credits

LAZY_DEV synthesizes patterns from:
- **Anthropic Claude Code** - Official hooks, agents, skills guidance
- **Model Context Protocol (MCP)** - Memory server integration
- **obra/superpowers** - Developer automation inspiration
- **KoljaB/RealtimeSTT** - Speech-to-text pipeline
- **disler/claude-code-hooks-****** - Multi-agent patterns, observability

Special thanks to the Claude Code community for sharing workflows and best practices.

---

## License

MIT License - See LICENSE file for details.

---

## Changelog

See CHANGELOG.md for version history and release notes.

---

**LAZY_DEV** - Be lazy, but consistently excellent. 🚀
