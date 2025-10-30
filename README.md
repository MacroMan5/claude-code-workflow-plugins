# LAZY (Claude Code Plugin)

Give Claude Code pragmatic “lazy developer” automation with a cohesive framework: curated skills, protective hooks, MCP Memory Graph integration, documentation workflows, and a voice‑to‑prompt (STT) enhancer. This folder contains the template used by the plugin; see `CLAUDE-PLUGINS/lazy` for the packaged manifest and docs.

## What You Get

- Skills and Patterns
  - Test‑Driven Development, diff scope minimization, writing skills, planning/brainstorming
  - Memory Graph Skill (MCP): create/search/update/delete persistent knowledge
- Hooks and Safety
  - UserPromptSubmit context packer + output style selector + Memory auto‑trigger
  - PreToolUse safety checks (dangerous rm, force‑push to main, sensitive paths)
  - PostToolUse formatting + memory suggestions; Stop checks with quality gates
- Commands
  - `/lazy create-feature`, `/lazy task-exec`, `/lazy story-review`, `/lazy documentation`
  - `/lazy memory-graph` (persist knowledge), `/lazy memory-check` (connectivity)
- MCP Integration
  - `.mcp.json` template for `@modelcontextprotocol/server-memory`
  - Tooling pattern: search → create → add observations → relate → verify
- Voice → Prompt (STT) Enhancer
  - Hands‑free prompting pipeline (record → transcribe → enrich prompt)
  - Auto‑injected context and style guidance


## Installation

### Via Plugin Marketplace (Example)

```bash
# In Claude Code
/plugin marketplace add therouxe/lazy-marketplace
/plugin install lazy@lazy-marketplace
```

### Enable MCP Memory (Workspace)

```bash
# From the repo root, enable Memory MCP tools in this workspace
cp LAZY_DEV/.claude/.mcp.json .mcp.json
```

### Verify

```bash
# List commands
/help

# You should see
# /lazy memory-graph
# /lazy memory-check
# /lazy task-exec
# /lazy create-feature
# /lazy story-review
```

## Quick Start

- Persist durable facts with Memory Graph
  - “service:alpha owned_by person:alice; repo: org/alpha; endpoint: https://alpha.example.com”
  - LAZY will auto‑inject a Memory Graph block and use mcp__memory__ tools
- Execute a task with TDD guardrails
  - `/lazy task-exec TASK-1.1 --story US-X.Y`
- Create a feature package (story + tasks + issues)
  - `/lazy create-feature <brief>`

## End‑to‑End Flow (Voice → Plan → Build → Review → PR)

1) Speak your idea
   - The STT enhancer transcribes and an OpenAI system prompt refines it into a structured prompt (no manual typing needed)
2) Create the feature package
   - `/lazy create-feature generatedPrompt.md`
   - Produces US + TASKS and optionally syncs to GitHub (issue + sub‑issues)
3) Start development
   - `/lazy task-exec <TASK-ID | GH issue | local US/TASK file>`
   - Auto subagents, git worktrees, safe parallelization, TDD, auto review, auto commit
4) Review the story
   - `/lazy story-review US-X.Y` → Auto PR on approval, or a structured report
5) Fix review if needed
   - `/lazy story-fix-review <review-report.md>`

Other helpful commands: `/lazy documentation`, `/lazy cleanup`, `/lazy memory-graph`, `/lazy memory-check`.

## What’s Inside

- Skills: LAZY_DEV/.claude/skills/
- Hooks: LAZY_DEV/.claude/hooks/
- Commands: LAZY_DEV/.claude/commands/
- MCP config template: LAZY_DEV/.claude/.mcp.json

## Mermaid Overview

```mermaid
flowchart TD
    A[🎙️ Voice Input] --> B[STT Transcription\nVoice → Text]
    B --> C[🔧 OpenAI System Prompt\nRefactor the spoken idea into a structured prompt]
    C --> D[/lazy create-feature\nGenerate US + TASKS]
    D --> E{Sync to GitHub?}
    E -- yes --> E1[Create Issue + Sub-issues]
    E -- no --> E2[Local US/TASK Markdown]
    E1 --> F
    E2 --> F
    F[/lazy task-exec\nReference GH issue or local US/TASK]
    subgraph G[Execution Engine]
      G1[Subagents: PM/Coder/Reviewer/Tester]
      G2[Git worktrees + parallelization]
      G3[TDD: RED→GREEN→REFACTOR]
      G4[Auto review + auto commit]
      G5[MCP Memory Graph writes]
    end
    F --> G --> H[/lazy story-review]
    H --> I{Approved?}
    I -- yes --> J[Auto PR created]
    I -- no --> K[📄 Review report generated]
    K --> L[/lazy story-fix-review\nPass report to fix]
    L --> H

    %% Hooks
    classDef hook fill:#eef,stroke:#66f,color:#111
    X1[Hook: UserPromptSubmit\nContext pack + Style + Memory auto-trigger]:::hook
    X2[Hook: PreToolUse\nSafety checks + audit]:::hook
    X3[Hook: PostToolUse\nFormatter + Memory suggestions]:::hook
    X4[Hook: Stop\nQuality gate logging]:::hook

    A --> X1
    F --> X2
    G --> X3
    H --> X4

    %% Skills
    classDef skill fill:#efe,stroke:#3a3,color:#111
    S1[Skill: memory-graph]:::skill
    S2[Skill: test-driven-development]:::skill
    S3[Skill: diff-scope-minimizer]:::skill
    S4[Skill: writing-skills]:::skill
    B --> S4
    F --> S2
    G3 --> S3
    G5 --> S1
```

### Integration Hints (Skills + Hooks)

- Voice Input → STT → Prompt Refactor
  - Skill: writing-skills (structure and clarity)
  - Hook: UserPromptSubmit appends Context Pack and Output Style
  - Memory auto-trigger: injects MCP Memory Graph guidance when durable facts are detected

- /lazy create-feature
  - Agent: project-manager; produces US + TASKS and can sync to GitHub
  - Memory: persist owners/endpoints/repos discovered during planning

- /lazy task-exec
  - Skills: test-driven-development, diff-scope-minimizer, memory-graph
  - Hooks: PreToolUse (safety), PostToolUse (formatter + memory suggestions)
  - Parallelization: auto-detected; Git worktrees when helpful

- /lazy story-review → PR
  - Approved → auto PR; else structured report

- /lazy story-fix-review
  - Consumes the generated report and focuses the fixes

## Auto‑Triggers, Hooks, and Env Toggles

- Hooks
  - UserPromptSubmit: context pack + output style + Memory auto‑trigger
  - PreToolUse: safety checks (dangerous rm, force‑push to main), audit logging
  - PostToolUse: formatter (Black/Ruff/Prettier/rustfmt) + memory suggestions
  - Stop: quality gate logging
- Skills
  - memory-graph, test-driven-development, diff-scope-minimizer, writing-skills
- Env toggles
  - `LAZYDEV_DISABLE_MEMORY_SKILL=1` (disable memory auto block on submit)
  - `LAZYDEV_DISABLE_MEMORY_SUGGEST=1` (disable PostToolUse suggestions)
  - `LAZYDEV_ENABLE_MEMORY_ROUTER=1` (enable no‑op memory router logging)

## How It Works

1) SessionStart warms up environment (lightweight)
2) UserPromptSubmit adds context, selects output style, and auto‑triggers Memory Graph when signals are detected
3) PreToolUse enforces safety and logging
4) PostToolUse formats files and nudges Memory persistence
5) Commands and agents consistently reference the same skills and patterns

## STT Prompt Enhancer (Core)

A voice‑to‑prompt pipeline that captures speech, performs accurate transcription, and enriches the prompt with project context and output style hints.

- Entry point: LAZY_DEV/STT_PROMPT_ENHANCER
- Flow: record → transcribe → enhance → inject
- Benefits: speed, hands‑free workflows, consistent prompt structure

## MCP Memory Graph (Server “memory”)

- Configure via `.mcp.json` (template provided here)
- Tools appear as `mcp__memory__<tool>` (e.g., `mcp__memory__create_entities`)
- Typical flow: `search_nodes` → `create_entities` → `add_observations` → `create_relations` → `open_nodes`

## Credits and Inspirations

This plugin synthesizes patterns and ideas from:
- Anthropic Claude Code skills and hooks guidance
- Model Context Protocol (MCP) Memory server
- List of inspirations from various open-source projects and research papers
- [obra/superpowers](https://github.com/obra/superpowers) - Superpowers for developers
- [KoljaB/RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) - Real-time speech-to-text transcription
- [disler/claude-code-hooks-multi-agent-observability](https://github.com/disler/claude-code-hooks-multi-agent-observability) - Multi-agent observability patterns for Claude Code
- [disler/always-on-ai-assistant](https://github.com/disler/always-on-ai-assistant) - Always-on AI assistant workflows
- [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) - Advanced Claude Code hooks patterns

## License

MIT — see LICENSE

## Changelog

See CHANGELOG.md

## Configuration

- `ENRICHMENT_MODEL`: Model used by pre-prompt enrichment. If unset, the hook skips enrichment.
- `LAZYDEV_LOG_DIR`: Where hooks write logs (default: `.claude/data/logs`).
- `LAZYDEV_ALLOW_SUDO`: Set to `1` to allow `sudo` in Bash tool calls (blocked by default).
- `LAZYDEV_DISABLE_CONTEXT_PACK`: Set to `1` to skip context pack.
- `LAZYDEV_CONTEXT_PACK_MAX_FILES`: File cap for extension counting (default 300).
- `LAZYDEV_CONTEXT_PACK_MAX_DIRS`: Dir cap (default 60).
- `LAZYDEV_CONTEXT_PACK_MAX_DEPTH`: Max walk depth (default 3).
- `LAZYDEV_CONTEXT_PACK_BUDGET_MS`: Time budget in ms (default 200).
- `LAZYDEV_ENFORCE_TDD`: When `1` (or `true`), the Stop hook blocks completion unless tests ran and passed.
- `LAZYDEV_MIN_TESTS`: Optional minimum number of tests required when TDD is enforced (e.g., `3`).

## Status Line

- The status bar uses `bash .claude/status_lines/lazy_status.sh` (configured in `.claude/settings.json`).
- It reads `ENRICHMENT_MODEL` and reports MCP status by checking `.mcp.json` at the workspace root (falls back to the template in `LAZY_DEV/.claude/.mcp.json`).
- It also reports whether `npx` is available for MCP servers.

Example output (single-line JSON):
```
{"lazy":"ok","model":"default","mcp":{"configured":true,"has_memory":true,"npx":true},"time":"12:34"}
```

To enable Memory MCP in this workspace:
- Copy the template: `cp LAZY_DEV/.claude/.mcp.json .mcp.json`
- Ensure Node.js is installed so `npx -y @modelcontextprotocol/server-memory` works.

## Recommended Workspace Settings (Optional Strict Mode)

- Use environment variables for hook behavior; this follows Anthropic’s Claude Code configuration model (project `.claude/settings.json` + env vars).
- Suggested stricter defaults:

bash/zsh:
```bash
export ENRICHMENT_MODEL=claude-3-5-haiku  # or your preferred model alias
export LAZYDEV_LOG_DIR=.claude/data/logs
export LAZYDEV_ENFORCE_TDD=1
export LAZYDEV_MIN_TESTS=3
# Optional: faster context pack
export LAZYDEV_CONTEXT_PACK_BUDGET_MS=150
```

PowerShell:
```powershell
$env:ENRICHMENT_MODEL = "claude-3-5-haiku"
$env:LAZYDEV_LOG_DIR = ".claude/data/logs"
$env:LAZYDEV_ENFORCE_TDD = "1"
$env:LAZYDEV_MIN_TESTS = "3"
$env:LAZYDEV_CONTEXT_PACK_BUDGET_MS = "150"
```

Note: Do not commit workspace-specific env settings. `.claude/settings.local.json` (if used) is ignored by `.gitignore`.
