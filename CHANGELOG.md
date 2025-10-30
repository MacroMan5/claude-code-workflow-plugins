# Changelog — LAZY_DEV

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.2.0] - 2025-10-30

### Major Release - Simplified Commands and Smart Orchestration

**Breaking Changes:**
- Simplified command names: `/lazy-dev:*` → `/lazy *`
- Plugin name changed to "lazy" for marketplace
- Restructured repository: moved from `LAZY_DEV/.claude/` to `.claude/` at root

### Added
- **Inline task management** in US-story.md files (no separate task files)
- **Debug report generation** when `/lazy review` finds issues
- **`/lazy fix` command** to apply fixes from review reports
- **Smart defaults** for test/review requirements based on project structure

### Changed
- Commands now use `/lazy` prefix instead of `/lazy-dev:`
- Plugin name: "lazy-dev" → "lazy"
- Repository structure: consolidated to root `.claude/` directory
- Review workflow: generates structured debug reports on failure

### Improved
- Command discoverability with simpler `/lazy` namespace
- Review error handling with machine-readable debug reports
- Automatic fix routing by issue severity
- Better marketplace compatibility

---

## [2.0.0] - 2025-10-29

### Production-Ready Plugin Release

**Breaking Changes:**
- Renamed project from "LAZY" to "LAZY_DEV Framework"
- Updated GitHub repository to MacroMan5/claude-code-workflow-plugins
- Restructured for Claude Code plugin marketplace distribution

### Added

**Commands (8 total):**
- `/lazy create-feature` - Generate US-story + tasks with PM agent
- `/lazy task-exec` - Execute task with TDD + quality pipeline
- `/lazy story-review` - Review complete story and create PR
- `/lazy story-fix-review` - Apply review fixes
- `/lazy documentation` - Generate/update documentation
- `/lazy cleanup` - Remove dead code
- `/lazy memory-graph` - Manual memory persistence
- `/lazy memory-check` - Verify MCP connectivity

**Agents (10 total):**
- project-manager - Creates user stories and tasks
- task-enhancer - Enriches task descriptions
- coder - Implements features with TDD
- tester - Writes comprehensive tests
- reviewer - Reviews code at task level
- reviewer-story - Reviews complete stories
- refactor - Improves code quality
- documentation - Generates/updates docs
- cleanup - Removes dead code
- research - Fetches documentation and examples

**Skills (17 total):**
- Planning: story-traceability, task-slicer, ac-expander, brainstorming
- Development: test-driven-development, diff-scope-minimizer, subagent-driven-development
- Quality: code-review-request, finishing-a-development-branch
- Documentation: writing-skills, example-skill
- Integration: gh-issue-sync, git-worktrees, memory-graph, output-style-selector, context-packer, dispatching-parallel-agents

**Hooks (8 implementations across 4 types):**
- UserPromptSubmit: user_prompt_submit.py (context enrichment + memory detection)
- PreToolUse: pre_tool_use.py (safety checks)
- PostToolUse: post_tool_use_format.py, memory_suggestions.py, memory_router.py, log_events.py
- SessionStart: session_start.py
- Stop: stop.py (quality gate logging)

**Documentation:**
- CREDITS.md - Attribution to PROJECT_INSPIRATION sources
- hooks.json - Hook registry for plugin system
- Comprehensive README.md with quick start
- WORKFLOW.md - Complete workflow guide
- MEMORY.md - MCP Memory integration guide
- SUB_AGENTS.md - Agent specifications
- CLAUDE.md - Framework guide for Claude Code

**Plugin Infrastructure:**
- .claude-plugin/plugin.json - Plugin manifest
- .claude-plugin/marketplace.json - Marketplace catalog
- hooks.json - Hook documentation

### Changed
- Plugin name: "lazy-dev-tools" → "lazy-dev"
- Version: 0.1.0 → 2.0.0
- Repository: therouxe/lazy → MacroMan5/claude-code-workflow-plugins
- Documentation restructured for production release
- Agent format: Updated to Anthropic's official YAML+Markdown pattern (context-based, no variable substitution)
- Memory system: Clarified as semi-automatic (AI-assisted suggestions, not fully automatic)

### Improved
- README.md: Added pros/cons, alignment with Anthropic best practices, troubleshooting
- Quality pipeline: Better cross-OS compatibility
- Hook system: Standardized JSON format
- Agent descriptions: Clearer action-oriented triggers

### Fixed
- Hook count documentation (4 types, 8 implementations)
- Agent delegation pattern (context-based, not variable substitution)
- Cross-platform path handling in scripts

---

## [0.1.0] - 2025-10-27

### Initial Release

**Features:**
- First public release
- Skills: memory-graph, writing-skills, TDD, diff-scope-minimizer, planning/brainstorming
- Hooks: UserPromptSubmit (context, style, memory auto-trigger), PreToolUse (safety), PostToolUse (formatter + memory suggestions), Stop (quality gate)
- Commands: memory-graph, memory-check, create-feature, task-exec, story-review, documentation
- MCP: `.mcp.json` template for `@modelcontextprotocol/server-memory`
- Docs: framework overview, memory setup/plan, skills catalog
- STT Prompt Enhancer: documented pipeline and behavior

---

## Release Notes

### v2.0.0 Highlights

This is a major production release with:

1. **Complete Plugin Infrastructure** - Ready for Claude Code marketplace
2. **Comprehensive Documentation** - 5 core docs + detailed guides
3. **Full Agent System** - 10 specialized agents with clear delegation
4. **Quality Pipeline** - Fail-fast enforcement (format→lint→type→test)
5. **MCP Memory Integration** - Semi-automatic persistence across sessions
6. **Proper Attribution** - Credits to all PROJECT_INSPIRATION sources

### Installation

```bash
# Add marketplace
/plugin marketplace add MacroMan5/claude-code-workflow-plugins

# Install plugin
/plugin install lazy-dev@MacroMan5

# Set environment
export ENRICHMENT_MODEL=claude-3-5-haiku

# Verify
/lazy memory-check
```

### Migration from 0.1.0

If you were using v0.1.0:
1. Backup your `.claude/` directory
2. Remove old installation
3. Install v2.0.0 via plugin system
4. Copy any custom configurations from backup

---

**Repository**: https://github.com/MacroMan5/claude-code-workflow-plugins
**License**: MIT
**Author**: MacroMan5 (Therouxe)

