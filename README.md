# LAZY_DEV Framework

> Command-first AI framework for Claude Code with automated workflows, quality enforcement, and persistent knowledge management.

**Version**: 2.0.0 | **License**: MIT | **Status**: Production-Ready

---

## Quick Start

**3-minute setup to first working feature:**

```bash
# 1. Copy LAZY_DEV to your project
cp -r LAZY_DEV/.claude/ .claude/

# 2. Set required environment variable
export ENRICHMENT_MODEL=claude-3-5-haiku

# 3. Create your first feature
/lazy create-feature "Add user authentication"

# 4. Execute first task
/lazy task-exec TASK-1.1

# 5. Review and create PR
/lazy story-review US-3.4
```

**What just happened?** PM agent created user stories, Coder agent implemented with TDD, quality pipeline validated code, PR was auto-created.

---

## What & Why

### The Problem

Modern AI-assisted development suffers from:
- Inconsistent quality (no format/lint/type/test enforcement)
- Lost context between sessions
- Manual repetitive tasks (stories, commits, reviews)
- Fragmented tools scattered across projects
- Constant re-prompting of the same context

### The Solution

LAZY_DEV provides a turnkey framework with:
- **Automatic quality pipeline**: format → lint → type → test (fail-fast)
- **Persistent knowledge**: MCP Memory graph across sessions
- **End-to-end automation**: voice → feature → tasks → code → PR
- **Protective hooks**: prevent dangerous operations (rm -rf, force-push to main)
- **Specialized agents**: intelligent delegation based on context

### Philosophy

**"Be lazy, but consistently excellent"**

Automate the mundane (formatting, commits, PRs) while enforcing discipline (quality gates, TDD, security checks).

---

## Core Features

**10 Commands**
- `/lazy create-feature <brief>` - Generate US-story + tasks
- `/lazy task-exec <id>` - Execute task with TDD
- `/lazy story-review <id>` - Review feature, create PR
- `/lazy story-fix-review <report>` - Apply review fixes
- `/lazy documentation <file>` - Generate/update docs
- `/lazy cleanup <path>` - Remove dead code
- `/lazy memory-graph <statement>` - Persist to MCP
- `/lazy memory-check` - Verify MCP connectivity

**10 Specialized Agents** (automatic delegation)
- project-manager, coder, reviewer, reviewer-story, tester
- research, documentation, refactor, cleanup, task-enhancer

**17 Skills** (reusable patterns)
- Planning: story-traceability, task-slicer, ac-expander
- Development: test-driven-development, diff-scope-minimizer
- Quality: code-review-checklist, security-scanner
- Documentation: readme-template, api-doc-generator
- Integration: gh-issue-sync, mcp-memory-router

**4 Hook Types** (10 implementations)
- UserPromptSubmit: context enrichment, memory detection, style selection
- PreToolUse: safety checks, audit logging, validation
- PostToolUse: auto-formatting, memory suggestions, cleanup
- Stop: quality gate logging, TDD enforcement, metrics

---

## Installation

### Prerequisites

- Python 3.11+
- Claude Code CLI (latest)
- uv package manager (`pip install uv`)
- git
- gh CLI (for PR creation)
- Node.js (for MCP Memory, optional)

### Step 1: Install Framework

```bash
# Copy LAZY_DEV to your project
cp -r LAZY_DEV/.claude/ .claude/
```

Or via plugin marketplace (when available):
```bash
/plugin marketplace add therouxe/lazy-marketplace
/plugin install lazy@lazy-marketplace
```

### Step 2: Set Environment Variables

```bash
# Required for pre-prompt enrichment
export ENRICHMENT_MODEL=claude-3-5-haiku

# Optional: Enable strict mode
export LAZYDEV_ENFORCE_TDD=1
export LAZYDEV_MIN_TESTS=3

# Optional: Disable features
export LAZYDEV_DISABLE_MEMORY_SKILL=1  # Disable auto-memory
export LAZYDEV_DISABLE_STYLE=1         # Disable output style
```

**Windows (PowerShell)**:
```powershell
$env:ENRICHMENT_MODEL = "claude-3-5-haiku"
```

### Step 3: Enable MCP Memory (Recommended)

```bash
# Copy config to workspace root
cp LAZY_DEV/.claude/.mcp.json .mcp.json

# Test MCP server
npx -y @modelcontextprotocol/server-memory
```

### Step 4: Authenticate GitHub

```bash
gh auth login
gh auth status
gh repo set-default
```

### Step 5: Verify

```bash
# List commands in Claude Code
/help

# Check MCP connectivity
/lazy memory-check
```

---

## Usage

### Complete Workflow Example

```bash
# 1. Create Feature
/lazy create-feature "Add payment processing with Stripe"
# → Creates USER-STORY.md + TASK-*.md files

# 2. Execute Tasks (iteratively)
/lazy task-exec TASK-1.1
# → TDD implementation → Quality pipeline → Review → Commit

/lazy task-exec TASK-1.2
# → Repeat for each task

# 3. Review Complete Story
/lazy story-review USER-STORY.md
# → Reviews all tasks together → Creates PR

# 4. Apply Fixes (if needed)
/lazy story-fix-review review-report.md
# → Fixes issues and re-reviews
```

**See [WORKFLOW.md](./WORKFLOW.md) for detailed workflow documentation.**

### Quality Pipeline

Every task enforces fail-fast quality checks:
```
Format → Lint → Type → Test → PASS → Commit
```

**Prerequisites**:
- Scripts: `scripts/format.py`, `scripts/lint.py`, `scripts/type_check.py`, `scripts/test_runner.py`
- Tools: `black`, `ruff`, `mypy`, `pytest` (installed via `uv`)

**See [WORKFLOW.md](./WORKFLOW.md) for pipeline details.**

### Agent Delegation

Agents are automatically invoked based on context (Anthropic pattern):
- **project-manager** → Creates stories/tasks
- **coder** → Implements with TDD
- **reviewer** → Reviews code quality
- **tester** → Writes comprehensive tests

**See [SUB_AGENTS.md](./SUB_AGENTS.md) for complete agent specifications.**

### Memory System

Semi-automatic persistence of durable facts (AI-assisted):
```bash
# Manual storage
/lazy memory-graph "service:api owned_by:alice"

# Automatic detection + suggestion
# Hooks detect entity mentions → suggest storage → Claude Code invokes MCP tools
# Context grows across sessions without manual re-prompting
```

**How it works**: Hooks detect durable facts (service owners, endpoints, repo links) and suggest MCP Memory storage. Claude Code decides when to invoke MCP tools based on context.

**See [MEMORY.md](./MEMORY.md) for complete memory system documentation.**

---

## Architecture

### Directory Structure

```
LAZY_DEV/
├── .claude/
│   ├── agents/          # 10 specialized agents
│   ├── commands/        # 8 commands
│   ├── hooks/           # 4 hooks (Python)
│   ├── skills/          # 17 skills
│   ├── status_lines/    # Status bar
│   ├── .mcp.json        # MCP config
│   └── settings.json    # Claude settings
├── scripts/             # Quality scripts (format, lint, test)
├── STT_PROMPT_ENHANCER/ # Voice-to-prompt pipeline
└── README.md            # This file
```

### Agent Format (Anthropic Standard)

YAML frontmatter + Markdown system prompt:

```yaml
---
name: coder
description: Implements features following TDD. Use after task-exec command.
tools: Read, Write, Edit, Grep, Glob, Bash
model: sonnet
---

You are the Coder Agent for LAZY-DEV-FRAMEWORK.

When invoked:
1. Review task description in conversation
2. Extract acceptance criteria
3. Implement following TDD: RED → GREEN → REFACTOR
```

**Key**: Context-based delegation (no variable substitution).

### High-Level Workflow

```
Voice/Text Input → Feature Creation → Task Execution → Story Review → PR
                                           ↓
                                    TDD + Quality + Review
```

**See [WORKFLOW.md](./WORKFLOW.md) for detailed workflow diagrams and state machines.**

---

## Pros and Cons

### Pros

**Consistent Quality**
- Mandatory pipeline enforces standards
- Auto-formatting on every save
- 80% test coverage minimum
- Security checklists built-in

**Automatic Delegation**
- Context-based agent routing (Anthropic pattern)
- No variable substitution code (simpler)
- Intelligent agent selection

**Complete Automation**
- Atomic commits (one per task)
- Auto-PR creation
- GitHub issue sync
- Voice input support

**Memory Persistence**
- MCP Memory graph for durable facts
- Persists across sessions
- Auto-triggers on durable knowledge

### Cons

**Learning Curve**
- 8 commands with various options
- Complex workflow chain
- MCP setup requires Node.js
- Mitigation: Comprehensive docs, examples

**Discipline Required**
- Quality gates block progress (by design)
- No bypass for format/lint/type/test failures
- Can be frustrating initially
- Mitigation: Auto-formatting reduces friction

**Dependencies**
- Python 3.11+ required
- Haiku API costs for enrichment (~$0.001-0.005 per prompt)
- Cross-platform path handling complexity
- Mitigation: Modern Python widely available, low costs

---

## Alignment with Anthropic Best Practices

### ✅ Conversation Context (Not Variables)
Agents extract from conversation naturally, no `$variable` Template substitution. Matches official examples exactly.

### ✅ Automatic Delegation
Clear agent descriptions with action-oriented triggers. Claude routes intelligently.

### ✅ Hook-Based Automation
PostToolUse for auto-formatting, PreToolUse for safety, UserPromptSubmit for enrichment, Stop for quality gates.

### ✅ Standard YAML+Markdown Format
All agents use official pattern:
```yaml
---
name: agent-name
description: Clear description
tools: Tool1, Tool2
model: sonnet
---
System prompt in markdown...
```

---

## Troubleshooting

### Common Issues

**ENRICHMENT_MODEL not set:**
```bash
export ENRICHMENT_MODEL=claude-3-5-haiku
```

**MCP Memory not connecting:**
```bash
node --version  # Need v18+
npx -y @modelcontextprotocol/server-memory
```

**Quality pipeline fails:**
```bash
python scripts/format.py .  # Auto-fix formatting
python scripts/lint.py .    # Check linting
```

**GitHub auth issues:**
```bash
gh auth login && gh auth status
```

**Detailed Troubleshooting:**
- **Workflow Issues** → See [WORKFLOW.md](./WORKFLOW.md#failure-scenarios--recovery)
- **Memory Issues** → See [MEMORY.md](./MEMORY.md#troubleshooting)
- **Agent Issues** → See [SUB_AGENTS.md](./SUB_AGENTS.md)
- **Framework Issues** → See [CLAUDE.md](./CLAUDE.md#troubleshooting)

---

## Contributing

### Add New Agent

1. Create `.claude/agents/my-agent.md`
2. Use YAML frontmatter + Markdown prompt
3. Test with relevant command
4. Document in SUB_AGENTS.md

### Add New Command

1. Create `.claude/commands/my-command.md`
2. Follow 5-section structure: When/Requirements/Execution/Validation/Examples
3. Test: `/lazy my-command`
4. Document in README

### Quality Standards

- Type hints on all Python code
- 80% test coverage minimum
- Cross-OS compatible (Windows/Linux/macOS)
- Black/Ruff formatted
- Google-style docstrings

---

## Documentation

### Getting Started
- **[README.md](./README.md)** (this file) - Overview and quick start
- **[CLAUDE.md](./CLAUDE.md)** - Guide for Claude Code when working with this framework

### Core Documentation
- **[WORKFLOW.md](./WORKFLOW.md)** - Complete workflow guide (commit-per-task, PR-per-story pattern)
- **[MEMORY.md](./MEMORY.md)** - Automatic memory system with MCP Memory
- **[SUB_AGENTS.md](./SUB_AGENTS.md)** - Agent registry and specifications

### Reference
- **[CHANGELOG.md](./CHANGELOG.md)** - Version history and release notes
- **[WORKFLOW_COHERENCE_REPORT.md](./WORKFLOW_COHERENCE_REPORT.md)** - Framework coherence analysis

### Logs & Debugging
- `.claude/data/logs/` - Hook execution logs
- `.claude/data/metrics/` - Quality metrics

---

## Resources

**Official Documentation**
- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [MCP Memory Protocol](https://github.com/modelcontextprotocol/servers/tree/main/src/memory)

**Credits**
- Anthropic Claude Code (official patterns)
- Model Context Protocol (MCP Memory)
- obra/superpowers (automation inspiration)
- KoljaB/RealtimeSTT (STT pipeline)
- disler/claude-code-hooks-* (multi-agent patterns)

---

## License

MIT License - See LICENSE file for details.

---

**LAZY_DEV** - Be lazy, but consistently excellent.
