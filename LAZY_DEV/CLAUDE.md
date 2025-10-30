# CLAUDE.md

This file provides guidance to Claude Code when working with code in repositories using the **LAZY_DEV Framework**.

---

## Framework Overview

**LAZY_DEV** is a command-first AI framework for Claude Code CLI that enforces quality through automation while maintaining developer productivity.

### Core Philosophy

**"Be lazy, but consistently excellent"**

Automate mundane tasks (formatting, commits, PRs) while enforcing discipline (quality gates, TDD, security checks).

---

## Quick Command Reference

### Primary Workflow Commands

```bash
# 1. Create feature with inline tasks
/lazy create-feature "<brief description>"

# 2. Execute task with flexible quality checks
/lazy task-exec <TASK-ID> --story US-X

# 3. Review story and create PR
/lazy story-review <US-ID>

# 4. Apply review fixes
/lazy story-fix-review <review-report.md>
```

### Utility Commands

```bash
# Documentation
/lazy documentation <file>

# Cleanup dead code
/lazy cleanup <path>

# Memory management
/lazy memory-graph "<statement>"
/lazy memory-check
```

---

## Workflow Adherence

### The Commit-Per-Task, PR-Per-Story Pattern

LAZY_DEV workflow structure:

```
USER-STORY (single file with inline tasks)
├── TASK-1 → Code → Quality (flexible) → Review (if complex) → COMMIT
├── TASK-2 → Code → Quality (flexible) → Review (if complex) → COMMIT
├── TASK-3 → Code → Quality (flexible) → Review (if complex) → COMMIT
│
└── STORY REVIEW → Single PR (all tasks together)
```

**Key Points:**
- ✅ One commit per task
- ✅ One PR per user story
- ✅ Tasks are inline sections in US-story.md (not separate files)
- ✅ Quality checks adapt to project (TDD optional)
- ✅ Code review only for complex/critical tasks
- ❌ Never create PRs for individual tasks

### Quality Pipeline (Flexible)

Task execution applies quality checks based on project configuration:

```
Format (if configured) → Lint (if configured) → Type (if configured) → Test (if TDD required)
      ↓                     ↓                      ↓                      ↓
    PASS/SKIP            PASS/SKIP              PASS/SKIP              PASS/SKIP
                                                                          ↓
                                                                    Git Commit Allowed
```

**Flexibility:**
- **TDD**: Only enforced if mentioned in README/CLAUDE.md
- **Tests**: Skip with `--skip-tests` if not required
- **Review**: Skip with `--skip-review` for simple tasks
- **Type checking**: Only runs if mypy/tsc configured
- **Linting**: Only runs if ruff/eslint configured

---

## Agent System (Anthropic Best Practices)

### Context-Based Delegation (Not Variables)

LAZY_DEV follows Anthropic's official pattern: agents extract context from conversation naturally.

**How it works:**
1. Command provides context in conversation
2. Claude reads agent description
3. Agent extracts needed information from conversation history
4. No variable substitution needed

**Example Agent Format:**

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

### Available Agents (Auto-Delegated)

**Planning & Management:**
- `project-manager` - Creates user stories with inline tasks

**Development:**
- `coder` - Implements features (TDD optional)
- `tester` - Writes comprehensive tests
- `refactor` - Improves code quality

**Quality & Review:**
- `reviewer` - Reviews code for complex tasks only
- `reviewer-story` - Reviews complete stories

**Documentation & Cleanup:**
- `documentation` - Generates/updates docs
- `cleanup` - Removes dead code
- `research` - Fetches documentation and examples

---

## Hook System

LAZY_DEV uses 3 hooks at strategic automation points:

### 1. UserPromptSubmit Hook

**Fires:** Before EVERY command execution

**Purpose:**
- Inject context pack (architecture patterns, team conventions)
- Select output style
- Trigger memory auto-persistence for durable facts

**Example:**
```
User types: /lazy create-feature "Add payments"
     ↓
Hook enriches with:
  - Architecture: adapter pattern, repository pattern
  - Security: OWASP top 10 considerations
  - Testing: Optional TDD (if project uses it)
  - Performance: async patterns
     ↓
Enriched prompt passed to command
```

### 2. PostToolUse Hook

**Fires:** After tool operations complete

**Purpose:**
- Auto-formatting (Black/Ruff)
- Memory persistence suggestions
- Metric collection

**Example:**
```
After Write/Edit tool:
     ↓
Hook runs Black/Ruff formatter (if configured)
     ↓
Code is auto-formatted
```

### 3. Stop Hook

**Fires:** When session ends or task completes

**Purpose:**
- Quality gate logging
- TDD enforcement validation
- Metrics summary

---

## Skills System

LAZY_DEV provides 17 reusable skills organized by category:

### Planning Skills
- `story-traceability` - Link stories to requirements
- `task-slicer` - Break features into atomic tasks
- `ac-expander` - Generate acceptance criteria

### Development Skills
- `test-driven-development` - TDD workflow (RED→GREEN→REFACTOR)
- `diff-scope-minimizer` - Keep changes focused

### Quality Skills
- `code-review-checklist` - Comprehensive review criteria
- `security-scanner` - OWASP top 10 validation

### Documentation Skills
- `readme-template` - Generate README sections
- `api-doc-generator` - Create API documentation

### Integration Skills
- `gh-issue-sync` - Sync with GitHub issues
- `mcp-memory-router` - Persist to MCP Memory

**Using Skills:**

Skills are invoked automatically by agents or explicitly via commands. They provide reusable patterns that ensure consistency.

---

## MCP Memory Integration

### Automatic Memory Persistence

LAZY_DEV integrates with MCP Memory to persist knowledge across sessions.

**What Gets Persisted:**
- Service ownership (`service:api owned_by person:alice`)
- Repository information (`repo:org/api endpoint:https://api.example.com`)
- Architecture decisions
- Dependency relationships
- Team conventions

**How It Works:**

1. **UserPromptSubmit Hook Detection:**
   - Detects durable facts in user input
   - Suggests memory persistence

2. **Manual Persistence:**
   ```bash
   /lazy memory-graph "service:payment owned_by team:backend"
   ```

3. **Automatic Context Injection:**
   - Relevant memories injected into prompts
   - Context grows over time
   - No manual re-prompting needed

**Configuration:**

```json
// .claude/.mcp.json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
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

1. **Follow TDD:**
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

4. **Quality Checks Before Commit:**
   ```bash
   python scripts/format.py .     # Auto-fix formatting
   python scripts/lint.py .       # Check linting
   python scripts/type_check.py . # Type validation
   pytest tests/ -v --cov        # Tests + coverage
   ```

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

# Disable features
export LAZYDEV_DISABLE_MEMORY_SKILL=1  # No auto-memory
export LAZYDEV_DISABLE_STYLE=1         # No output styling
```

**Windows (PowerShell):**
```powershell
$env:ENRICHMENT_MODEL = "claude-3-5-haiku"
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
```

**4. GitHub PR Creation Fails**
```bash
# Authenticate
gh auth login
gh auth status

# Set default repo
gh repo set-default
```

---

## File Organization

```
project-root/
├── .claude/                    # Framework installation
│   ├── agents/                 # 10 specialized agents
│   ├── commands/               # 8 commands
│   ├── hooks/                  # 4 hooks (Python)
│   ├── skills/                 # 17 skills
│   ├── .mcp.json              # MCP Memory config
│   └── settings.json          # Claude Code settings
│
├── USER-STORY.md              # Generated by create-feature
├── TASKS.md                   # Generated task breakdown
├── TASK-*.md                  # Individual task files
└── review-report.md           # Generated by story-review
```

---

## Key Principles

1. ✅ **Command-First**: Use commands, not ad-hoc prompts
2. ✅ **Quality-First**: Pipeline blocks incomplete work
3. ✅ **Context-Based**: Agents extract from conversation
4. ✅ **Commit-Per-Task**: One commit per task, one PR per story
5. ✅ **TDD-Required**: Tests before implementation
6. ✅ **Memory-Persistent**: Durable facts stored in MCP
7. ✅ **Auto-Formatting**: Code formatted automatically
8. ✅ **Security-Aware**: OWASP checks built-in

---

## Additional Resources

- [WORKFLOW.md](./WORKFLOW.md) - Complete workflow guide
- [MEMORY.md](./MEMORY.md) - MCP Memory documentation
- [SUB_AGENTS.md](./SUB_AGENTS.md) - Agent specifications
- [CHANGELOG.md](./CHANGELOG.md) - Version history

---

## Version

**Framework Version:** 2.0.0
**Last Updated:** 2025-10-29
**Status:** Production-Ready

---

**LAZY_DEV** - Be lazy, but consistently excellent.
