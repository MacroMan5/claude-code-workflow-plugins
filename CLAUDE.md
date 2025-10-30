# CLAUDE.md

This file provides guidance to Claude Code when working with code in repositories using the **LAZY_DEV Framework**.

---

## Framework Overview

**LAZY_DEV** is a command-first AI framework for Claude Code CLI that enforces quality through automation while maintaining developer productivity.

**Core Philosophy:** "Be lazy, but consistently excellent" - Automate mundane tasks (formatting, commits, PRs) while enforcing discipline (quality gates, TDD, security checks).

### Comparison with Similar Plugins

| Feature | LAZY_DEV | claude-code-spec-workflow | agents | Built-in Claude Code |
|---------|----------|--------------------------|---------|----------------------|
| **Commands** | 10 workflow commands | 2 spec-driven commands | 5 agent commands | Basic /commit, /pr |
| **Skills** | 22 auto-invoked skills | None | None | Official skills marketplace |
| **Agents** | 10 specialized agents | 2 workflow agents | 8+ multi-agent orchestration | Task-based agents |
| **Quality Pipeline** | Auto format/lint/type/test | Manual spec validation | None | Manual |
| **MCP Integration** | Memory graph per project | None | None | Optional MCP servers |
| **Story Management** | Inline tasks with git tags | Separate requirements docs | None | None |
| **Review System** | Story-level + debug reports | Spec compliance check | None | Manual review |
| **TDD Support** | Optional with enforcement | None | None | None |

**Unique Value:** Comprehensive automation (planning → implementation → review → PR) with quality gates, memory persistence, and flexible TDD enforcement.

---

## Commands Reference

Commands orchestrate agents, skills, and quality checks. They are your primary interface to LAZY_DEV.

| Command | Purpose | Input | Output | Key Flags |
|---------|---------|-------|--------|-----------|
| `/lazy init-project` | Bootstrap new project docs | Description or `--file` | PROJECT-OVERVIEW.md, SPECIFICATIONS.md, TECH-STACK.md, ARCHITECTURE.md | `--minimal`, `--no-sync` |
| `/lazy plan` | Create user story with tasks | Feature description or `--file` | US-{ID}-{name}/US-story.md + GitHub issues | `--no-issue` |
| `/lazy code` | Implement features/fixes | @file, TASK-ID, #issue, or brief | Code + tests + commits + tags | Auto-detects scope |
| `/lazy review` | Validate story + create PR | US-ID or story path | PR (if approved) or debug report | `--base`, `--draft` |
| `/lazy fix` | Apply review fixes | Review report path | Fixed code + updated commits | None |
| `/lazy docs` | Generate documentation | File/directory path | Docstrings, README, API docs | `--format` |
| `/lazy clean` | Remove dead code | Path to clean | Removed unused code/imports | None |
| `/lazy question` | Answer codebase questions | Question string | Answer with file:line citations | None |
| `/lazy memory-graph` | Persist durable facts | Statement to persist | Knowledge graph entry | None |
| `/lazy memory-check` | Verify MCP Memory | Optional query | Connection status + facts | `--all` |

### Command Details

**`/lazy init-project`**
- **Triggers:** project-planner, tech-stack-architect skills
- **Creates:** project-management/ with 4 core docs
- **Use when:** Starting new projects from scratch

**`/lazy plan`**
- **Triggers:** brainstorming skill (auto), project-manager agent
- **Creates:** US-story.md with inline tasks, GitHub issues, git tag `story/US-{ID}-start`
- **Use when:** Planning features requiring 3+ tasks

**`/lazy code`**
- **Triggers:** coder, tester (if TDD), reviewer (complex), context-packer, quality pipeline
- **Smart Detection:** Tests (if framework exists), Review (complex tasks), Branch (auto-creates for stories)
- **Use when:** Implementing features, fixing bugs, iterating on tasks

**`/lazy review`**
- **Triggers:** reviewer-story agent, loads project standards
- **Validates:** All task tags exist, acceptance criteria met, test coverage >80%, integration works
- **Outcomes:** APPROVED → PR created | CHANGES_REQUIRED → `US-X.Y-review-report.md` with CRITICAL/WARNING/SUGGESTION issues
- **Use when:** All story tasks committed, ready for PR

**`/lazy fix`**
- **Triggers:** Routes to coder/tester/refactor/documentation agents by severity
- **Workflow:** `/lazy review` → report → `/lazy fix report.md` → `/lazy review` (re-check)
- **Use when:** Review report generated with issues

---

## Skills (22 Total)

Skills are reusable patterns that enhance commands and agents. **MODEL-INVOKED** - Claude autonomously decides when to use them based on descriptions.

### Planning & Design (4)
- **`brainstorming`**: Structured ideation for options, trade-offs, and clear decision
- **`task-slicer`**: Split features into atomic 2-4h tasks with independent tests
- **`ac-expander`**: Turn vague Acceptance Criteria into measurable checks
- **`story-traceability`**: Ensure Acceptance Criteria map to Tasks and Tests

### Development (4)
- **`test-driven-development`**: Enforce RED→GREEN→REFACTOR micro-cycles
- **`diff-scope-minimizer`**: Keep changes narrowly scoped with patch plan
- **`code-review-request`**: Request code review with rubric and patch plan
- **`regression-testing`**: Evaluate need for regression tests after bug fixes

### Quality & Review (4)
- **`security-audit`**: Check OWASP risks for auth, payments, user input, APIs
- **`breaking-change-detector`**: Detect backward-incompatible API changes
- **`error-handling-completeness`**: Evaluate try-catch coverage, logging, retry logic
- **`performance-budget-checker`**: Detect N+1 queries, nested loops, inefficient algorithms

### Context & Optimization (2)
- **`context-packer`**: Build compact context brief instead of large code blocks
- **`output-style-selector`**: Auto-choose best output style for scanability

### Integration & Workflow (4)
- **`gh-issue-sync`**: Create/update GitHub issues for stories and tasks
- **`git-worktrees`**: Isolate tasks with git worktrees for parallelization
- **`memory-graph`**: Persist knowledge graph via MCP Memory (disable: `LAZYDEV_DISABLE_MEMORY_SKILL=1`)
- **`finishing-a-development-branch`**: Present options for merge, PR, or cleanup

### Project Initialization (4)
- **`project-planner`**: Generate PROJECT-OVERVIEW.md and SPECIFICATIONS.md
- **`tech-stack-architect`**: Select tech stack and design architecture with diagrams
- **`project-docs-sync`**: Auto-sync docs when tech/architecture/requirements change
- **`agent-selector`**: Recommend best agent for task (auto-triggers on UserPromptSubmit)

### Skill Configuration

**File Organization:** `~/.claude/skills/skill-name/` (personal) or `.claude/skills/skill-name/` (project)

**YAML Frontmatter:** See [Anthropic Skills Guide](https://docs.claude.com/en/docs/claude-code/skills) - requires `name` (lowercase, hyphens, max 64 chars) and `description` (max 1024 chars)

**Manual Testing:** `Skill(command="skill-name")`

---

## Quality Pipeline (Automated)

Quality checks run automatically via PostToolUse hook after Write/Edit operations.

| Stage | Tools | Behavior |
|-------|-------|----------|
| **1. Format** | Black/Ruff (Python), Prettier (JS/TS), gofmt (Go) | Auto-applied |
| **2. Lint** | Ruff (Python), ESLint (JS/TS), golangci-lint (Go) | Warns only |
| **3. Type** | Mypy (Python), TSC (TypeScript) | Warns only |
| **4. Tests** | Pytest (Python), Jest (JS/TS), Go test (Go) | If TDD enabled |

**Characteristics:**
- Hook-driven (fires after Write/Edit, no manual execution)
- Non-blocking (allows progress with warnings except critical failures)
- Language-aware (detects project type automatically)

---

## Agent System

LAZY_DEV follows Anthropic's context-based delegation pattern. Agents extract context from conversation naturally.

| Category | Agents | Purpose |
|----------|--------|---------|
| **Planning & Management** | project-manager | Create user stories with inline tasks from briefs |
| **Development** | coder, tester, refactor | Implement features, write tests, improve code quality |
| **Quality & Review** | reviewer, reviewer-story | Review complex tasks (reviewer) or entire stories (reviewer-story) |
| **Documentation & Cleanup** | documentation, cleanup, research | Generate docs, remove dead code, fetch examples |

**Delegation:** Automatic based on command context and agent descriptions. See [SUB_AGENTS.md](./SUB_AGENTS.md) for specifications.

### Agent Color Configuration

Each agent has visual identity settings for better UI/terminal distinction:

| Agent | Color | Hex Code | ANSI | Purpose |
|-------|-------|----------|------|---------|
| **coder** | Blue | `#3B82F6` | 34 | Implementation & building |
| **reviewer** | Amber | `#F59E0B` | 33 | Code review & validation |
| **reviewer-story** | Orange | `#F97316` | 33 | Story-level review |
| **tester** | Green | `#10B981` | 32 | Testing & validation |
| **refactor** | Purple | `#8B5CF6` | 35 | Optimization & improvement |
| **documentation** | Gray | `#6B7280` | 37 | Documentation writing |
| **cleanup** | Red | `#EF4444` | 31 | Code removal & cleanup |
| **research** | Pink | `#EC4899` | 95 | Research & exploration |
| **project-manager** | Cyan | `#06B6D4` | 36 | Planning & organization |

**Usage in Agent YAML Frontmatter:**
```yaml
---
name: coder
color: "#3B82F6"
color_name: blue
ansi_color: "34"
---
```

**Benefits:**
- Visual distinction in logs and output
- Easier debugging when multiple agents run
- Better UX in terminal and web interfaces
- Consistent branding across tools

---

## Hook System

LAZY_DEV uses 3 hooks at strategic automation points:

| Hook | Fires | Purpose |
|------|-------|---------|
| **UserPromptSubmit** | Before every command | Inject context pack, select output style, trigger memory auto-persistence |
| **PostToolUse** | After Write/Edit operations | Auto-format code, run quality checks, suggest memory persistence, collect metrics |
| **Stop** | Session end or task completion | Log quality gates, validate TDD enforcement, summarize metrics |

---

## MCP Memory Integration

LAZY_DEV integrates with MCP Memory to persist project-specific knowledge graph.

**Stored Data:** Service ownership, repository info, architecture decisions, dependency relationships, team conventions

**Storage:** `<PROJECT_ROOT>/.claude/memory/memory.jsonl` (project-isolated)

**Workflow:**
1. Auto-Detection: UserPromptSubmit hook persists durable facts automatically
2. Manual Persistence: `/lazy memory-graph "statement"`
3. Context Injection: Relevant memories injected into prompts

**Configuration:** See `.claude/.mcp.json` for MCP server setup

**Verify:** `/lazy memory-check`

---

## Development Guidelines

### Adding New Code
1. **TDD (if required):** RED → GREEN → REFACTOR
2. **Type Hints:** All functions require type annotations
3. **Docstrings:** Google-style for public functions
4. **Quality:** Automated via PostToolUse hook

### Creating New Agents
1. Create in `.claude/agents/my-agent.md`
2. Use YAML frontmatter (name, description, tools, model) + Markdown prompt
3. Clear action-oriented description for auto-delegation
4. Document in [SUB_AGENTS.md](./SUB_AGENTS.md)

**Template:** See existing agents in `.claude/agents/` directory

### Creating New Commands
1. Create in `.claude/commands/my-command.md`
2. Follow 5-section structure: When to Use, Requirements, Execution, Validation, Examples
3. Test thoroughly, document in README.md

---

## Environment Variables

**Required:**
```bash
export ENRICHMENT_MODEL=claude-3-5-haiku
```

**Optional:**
```bash
# TDD enforcement
export LAZYDEV_ENFORCE_TDD=1
export LAZYDEV_MIN_TESTS=3

# Memory storage
export MEMORY_FILE_PATH=.claude/memory/memory.jsonl

# Disable features
export LAZYDEV_DISABLE_MEMORY_SKILL=1  # No auto-memory
export LAZYDEV_DISABLE_STYLE=1         # No output styling
```

**Windows:** Use `$env:VARIABLE_NAME = "value"` in PowerShell

---

## File Organization

```
project-root/
├── .claude/
│   ├── agents/          # 10 specialized agents
│   ├── commands/        # 10 commands
│   ├── hooks/           # 3 hooks (Python)
│   ├── skills/          # 22 skills
│   ├── memory/
│   │   └── memory.jsonl # Knowledge graph
│   ├── .mcp.json        # MCP config
│   └── settings.json
├── project-management/
│   └── US-STORY/
│       └── US-X.Y-name/
│           └── US-story.md
└── US-X.Y-review-report.md  # If review finds issues
```

---

## Key Principles

1. **Command-First**: Use commands, not ad-hoc prompts
2. **Quality-First**: Pipeline enforces standards automatically
3. **Context-Based**: Agents extract from conversation naturally
4. **Commit-Per-Task**: One commit per task, one PR per story
5. **TDD-Optional**: Tests required only if project uses TDD
6. **Memory-Persistent**: Durable facts stored in MCP (project-isolated)
7. **Auto-Formatting**: Code formatted automatically via hook
8. **Security-Aware**: OWASP checks built-in for sensitive code
9. **Smart-Defaults**: Infer tests, reviews, complexity from context
10. **Flexible-Input**: Accept stories, tasks, briefs, or issues

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Quality pipeline fails | Run `python scripts/format.py .` then `python scripts/lint.py .` |
| Agent not delegating | Check agent description clarity, verify YAML frontmatter, review `.claude/data/logs/` |
| MCP Memory not working | Verify Node.js installed, test with `npx -y @modelcontextprotocol/server-memory`, check `.claude/.mcp.json` |
| GitHub PR fails | Run `gh auth login`, then `gh repo set-default` |
| Task not found | Check `ls -la ./project-management/US-STORY/*/US-story.md` or `grep -r "TASK-ID" ./project-management/` |
| Tests not running | Verify test framework installed, check CLAUDE.md for TDD config, verify `$LAZYDEV_ENFORCE_TDD` |

---

## Additional Resources

- [SUB_AGENTS.md](./SUB_AGENTS.md) - Agent specifications
- [MEMORY.md](./MEMORY.md) - MCP Memory documentation
- [CHANGELOG.md](./CHANGELOG.md) - Version history
- [Anthropic Skills Guide](https://docs.claude.com/en/docs/claude-code/skills) - Official skill documentation
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - Official best practices

---

## Version

**Framework Version:** 2.2.2
**Last Updated:** 2025-10-30
**Status:** Production-Ready

---

**LAZY_DEV** - Be lazy, but consistently excellent.
