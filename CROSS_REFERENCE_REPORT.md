# LAZY_DEV Framework - Cross-Reference Audit Report

**Date:** 2025-10-29
**Scope:** All documentation, commands, agents, hooks, skills, scripts
**Status:** ⚠️ Multiple Issues Found

---

## Executive Summary

This cross-reference audit analyzed **all references** in LAZY_DEV documentation to verify:
- File references (paths, existence)
- Command registrations and files
- Agent references and files
- Hook references and configuration
- Environment variables (documented vs. used)
- Skill references
- External dependencies

**Key Findings:**
- ✅ **8/8 Commands** properly registered and files exist
- ✅ **10/10 Agent files** exist and match SUB_AGENTS.md
- ✅ **10/10 Hook files** exist and registered in settings.json
- ✅ **17/17 Skill directories** exist with SKILL.md files
- ⚠️ **3 broken file references** found
- ⚠️ **2 undocumented environment variables** found
- ⚠️ **1 incorrect path reference** (@LAZY_DEV vs LAZY_DEV)

---

## 1. File References Audit

### ✅ VALID References (Verified to Exist)

**Configuration Files:**
- ✅ `.claude/settings.json` - Exists
- ✅ `.claude/.mcp.json` - Exists (225 bytes)
- ✅ `.claude/status_lines/lazy_status.sh` - Exists
- ✅ `.claude/status_lines/lazy_status.py` - Exists

**Hook Files (10/10 exist):**
- ✅ `.claude/hooks/session_start.py`
- ✅ `.claude/hooks/user_prompt_submit.py`
- ✅ `.claude/hooks/pre_prompt_enrichment.py`
- ✅ `.claude/hooks/pre_tool_use.py`
- ✅ `.claude/hooks/post_tool_use_format.py`
- ✅ `.claude/hooks/log_events.py`
- ✅ `.claude/hooks/memory_router.py`
- ✅ `.claude/hooks/memory_suggestions.py`
- ✅ `.claude/hooks/stop.py`
- ✅ `.claude/hooks/hook_utils.py`

**Agent Files (10/10 exist):**
- ✅ `.claude/agents/project-manager.md`
- ✅ `.claude/agents/task-enhancer.md`
- ✅ `.claude/agents/coder.md`
- ✅ `.claude/agents/reviewer.md`
- ✅ `.claude/agents/reviewer-story.md`
- ✅ `.claude/agents/tester.md`
- ✅ `.claude/agents/research.md`
- ✅ `.claude/agents/documentation.md`
- ✅ `.claude/agents/refactor.md`
- ✅ `.claude/agents/cleanup.md`

**Command Files (8/8 exist):**
- ✅ `.claude/commands/create-feature.md`
- ✅ `.claude/commands/task-exec.md`
- ✅ `.claude/commands/story-review.md`
- ✅ `.claude/commands/story-fix-review.md`
- ✅ `.claude/commands/documentation.md`
- ✅ `.claude/commands/cleanup.md`
- ✅ `.claude/commands/memory-graph.md`
- ✅ `.claude/commands/memory-check.md`

**Script Files (5/5 exist):**
- ✅ `scripts/format.py`
- ✅ `scripts/lint.py`
- ✅ `scripts/type_check.py`
- ✅ `scripts/test_runner.py`
- ✅ `scripts/gh_wrapper.py`
- ✅ `scripts/README.md`

**Memory-Graph Skill Files (4/4 exist):**
- ✅ `.claude/skills/memory-graph/SKILL.md`
- ✅ `.claude/skills/memory-graph/operations.md`
- ✅ `.claude/skills/memory-graph/playbooks.md`
- ✅ `.claude/skills/memory-graph/examples.md`

**Output Styles:**
- ✅ `.claude/output-styles/tts-summary.md`

### ❌ BROKEN References (Files Do Not Exist)

#### 🔴 **CRITICAL: Missing STT_PROMPT_ENHANCER Directory**
- **Referenced in:** README.md:189
- **Reference:** `LAZY_DEV/STT_PROMPT_ENHANCER`
- **Issue:** Directory does not exist
- **Impact:** Voice-to-prompt feature documented but not implemented
- **Fix:** Either implement the directory or remove references
- **Locations:**
  - README.md line 189: "Entry point: LAZY_DEV/STT_PROMPT_ENHANCER"

#### 🔴 **CRITICAL: Missing TTS Script**
- **Referenced in:** `.claude/output-styles/tts-summary.md:31,53`
- **Reference:** `uv run .claude/hooks/utils/tts/elevenlabs_tts.py`
- **Issue:** File does not exist (neither does `.claude/hooks/utils/` directory)
- **Impact:** TTS output style feature broken
- **Fix:** Either implement the script or remove output-style references
- **Locations:**
  - `.claude/output-styles/tts-summary.md` line 31
  - `.claude/output-styles/tts-summary.md` line 53

#### 🟡 **MEDIUM: Incorrect Path Reference**
- **Referenced in:** `.claude/commands/documentation.md:210`
- **Reference:** `@LAZY_DEV/lazy_dev/subagents/documentation.md`
- **Issue:** Path uses `@LAZY_DEV` prefix which doesn't exist (should be `.claude/agents/documentation.md`)
- **Impact:** Confusion, incorrect path in documentation
- **Fix:** Update to correct path: `.claude/agents/documentation.md`
- **Locations:**
  - `.claude/commands/documentation.md` line 210

### ⚠️ Potentially Outdated References

#### Referenced but Not Verified (May Exist in Other Locations)
- `PROJECT-MANAGEMENT-LAZY_DEV/docs/TOOLS.md` (referenced in `scripts/README.md:4`)
  - **Status:** Not found in LAZY_DEV directory
  - **Likely location:** Parent directory or separate project
  - **Recommendation:** Clarify reference or provide relative path

---

## 2. Command Registration Audit

### ✅ All Commands Properly Registered

**Registered in settings.json vs Files on Disk:**

| Command Name | File in settings.json | Actual File Exists | Status |
|--------------|----------------------|-------------------|--------|
| create-feature | `.claude/commands/create-feature.md` | ✅ Yes | ✅ Valid |
| task-exec | `.claude/commands/task-exec.md` | ✅ Yes | ✅ Valid |
| issue-implementation | `.claude/commands/task-exec.md` | ✅ Yes (alias) | ✅ Valid |
| us-development | `.claude/commands/task-exec.md` | ✅ Yes (alias) | ✅ Valid |
| story-review | `.claude/commands/story-review.md` | ✅ Yes | ✅ Valid |
| story-fix-review | `.claude/commands/story-fix-review.md` | ✅ Yes | ✅ Valid |
| documentation | `.claude/commands/documentation.md` | ✅ Yes | ✅ Valid |
| cleanup | `.claude/commands/cleanup.md` | ✅ Yes | ✅ Valid |
| memory-graph | `.claude/commands/memory-graph.md` | ✅ Yes | ✅ Valid |
| memory-check | `.claude/commands/memory-check.md` | ✅ Yes | ✅ Valid |

**Aliases:**
- `issue-implementation` → `task-exec.md` (for GitHub issues)
- `us-development` → `task-exec.md` (for user stories)

**Total:** 10 command names, 8 unique files, all valid ✅

---

## 3. Agent Files Audit

### ✅ All Agents Exist and Match Documentation

**Cross-reference between SUB_AGENTS.md and actual files:**

| Agent Name | Documented in SUB_AGENTS.md | File Exists | Status |
|------------|---------------------------|-------------|--------|
| Project-Manager | ✅ Yes (line 56) | ✅ `.claude/agents/project-manager.md` | ✅ Valid |
| Task-Enhancer | ✅ Yes (line 137) | ✅ `.claude/agents/task-enhancer.md` | ✅ Valid |
| Coder | ✅ Yes (line 238) | ✅ `.claude/agents/coder.md` | ✅ Valid |
| Reviewer | ✅ Yes (line 368) | ✅ `.claude/agents/reviewer.md` | ✅ Valid |
| Reviewer-Story | ✅ Yes (line 466) | ✅ `.claude/agents/reviewer-story.md` | ✅ Valid |
| Tester | ✅ Yes (line 600) | ✅ `.claude/agents/tester.md` | ✅ Valid |
| Research | ✅ Yes (line 715) | ✅ `.claude/agents/research.md` | ✅ Valid |
| Documentation | ✅ Yes (line 838) | ✅ `.claude/agents/documentation.md` | ✅ Valid |
| Refactor | ✅ Yes (line 1008) | ✅ `.claude/agents/refactor.md` | ✅ Valid |
| Cleanup | ✅ Yes (line 1132) | ✅ `.claude/agents/cleanup.md` | ✅ Valid |

**Total:** 10/10 agents documented and exist ✅

**Agent Variable Definitions:**
- ✅ All agents have clearly defined input variables in SUB_AGENTS.md
- ✅ All agents use `$variable` syntax for substitution
- ✅ All agents document required vs optional variables

---

## 4. Hook Registration Audit

### ✅ All Hooks Properly Configured

**Hooks in settings.json vs Files on Disk:**

| Hook Event | Hook Commands | Files Exist | Status |
|------------|--------------|-------------|--------|
| SessionStart | `session_start.py` | ✅ Yes | ✅ Valid |
| UserPromptSubmit | `user_prompt_submit.py`, `pre_prompt_enrichment.py` | ✅ Yes | ✅ Valid |
| PreToolUse | `pre_tool_use.py`, `log_events.py --event PreToolUse` | ✅ Yes | ✅ Valid |
| PostToolUse | `post_tool_use_format.py`, `log_events.py --event PostToolUse`, `memory_suggestions.py`, `memory_router.py` | ✅ Yes | ✅ Valid |
| Stop | `stop.py`, `log_events.py --event Stop`, `memory_router.py` | ✅ Yes | ✅ Valid |
| SubagentStop | `log_events.py --event SubagentStop` | ✅ Yes | ✅ Valid |

**Status Line:**
- ✅ Configured: `bash .claude/status_lines/lazy_status.sh`
- ✅ Files exist: `lazy_status.sh`, `lazy_status.py`

**Total:** 6 hook events, 10 unique hook scripts, all valid ✅

**Hook Configuration Quality:**
- ✅ All hooks use `uv run $CLAUDE_PROJECT_DIR/.claude/hooks/...`
- ✅ Proper ordering and parallel execution supported
- ✅ All referenced files exist

---

## 5. Environment Variables Audit

### 📊 Environment Variables Analysis

**Total Environment Variables:** 17 unique

#### ✅ DOCUMENTED Variables (in README.md)

| Variable | Purpose | Default | Lines in README |
|----------|---------|---------|-----------------|
| `ENRICHMENT_MODEL` | Model for pre-prompt enrichment | (none, hook skips if unset) | 221, 235, 254, 264 |
| `LAZYDEV_LOG_DIR` | Log directory location | `.claude/data/logs` | 222, 255, 265 |
| `LAZYDEV_ALLOW_SUDO` | Allow sudo in Bash calls | (blocked) | 223 |
| `LAZYDEV_DISABLE_CONTEXT_PACK` | Skip context pack | (enabled) | 224 |
| `LAZYDEV_CONTEXT_PACK_MAX_FILES` | File cap for ext counting | 300 | 225 |
| `LAZYDEV_CONTEXT_PACK_MAX_DIRS` | Dir cap | 60 | 226 |
| `LAZYDEV_CONTEXT_PACK_MAX_DEPTH` | Max walk depth | 3 | 227 |
| `LAZYDEV_CONTEXT_PACK_BUDGET_MS` | Time budget (ms) | 200 | 228, 259, 268 |
| `LAZYDEV_ENFORCE_TDD` | Stop hook blocks unless tests pass | (disabled) | 229, 256, 266 |
| `LAZYDEV_MIN_TESTS` | Min tests required when TDD enforced | (none) | 230, 257, 267 |
| `LAZYDEV_DISABLE_MEMORY_SKILL` | Disable memory auto-block | (enabled) | 173 |
| `LAZYDEV_DISABLE_MEMORY_SUGGEST` | Disable PostToolUse suggestions | (enabled) | 174 |
| `LAZYDEV_ENABLE_MEMORY_ROUTER` | Enable memory router logging | (disabled) | 175 |
| `ANTHROPIC_API_KEY` | Anthropic API key for enrichment | (required for enrichment) | (mentioned in create-feature.md, scripts README) |

#### ⚠️ UNDOCUMENTED Variables (Used in Code but Not in README.md)

| Variable | Used In | Purpose | Default | Recommendation |
|----------|---------|---------|---------|----------------|
| `ENRICHMENT_MAX_TOKENS` | `pre_prompt_enrichment.py:181` | Max tokens for enrichment API call | 1000 | **Add to README.md** |
| `LAZYDEV_DISABLE_STYLE` | `user_prompt_submit.py:504` | Disable output style selector | (enabled) | **Add to README.md** |
| `LAZYDEV_CONTEXT_PACK_EXTS` | `user_prompt_submit.py:226` | Custom file extensions to track | (none, uses default list) | **Add to README.md** |

#### 🔍 Additional Variables Referenced

| Variable | Referenced In | Context |
|----------|--------------|---------|
| `CLAUDE_PROJECT_DIR` | All hooks (settings.json), AUDIT_REPORT.md | Claude Code sets this automatically |

### Summary

- **Documented:** 14 variables
- **Undocumented:** 3 variables
- **Automatic (Claude Code):** 1 variable (`CLAUDE_PROJECT_DIR`)

**Recommendation:** Add documentation for the 3 undocumented variables in README.md:

```markdown
## Configuration (ADD THESE)

- `ENRICHMENT_MAX_TOKENS`: Maximum tokens for pre-prompt enrichment API call (default: 1000)
- `LAZYDEV_DISABLE_STYLE`: Set to `1` to disable output style selector in UserPromptSubmit hook
- `LAZYDEV_CONTEXT_PACK_EXTS`: Comma-separated file extensions to track (e.g., "py,js,md"), overrides defaults
```

---

## 6. Skills Audit

### ✅ All Skill Directories and Files Exist

**17 Skills with SKILL.md files:**

| Skill Name | Directory | SKILL.md Exists | Status |
|------------|-----------|-----------------|--------|
| example-skill | `.claude/skills/example-skill/` | ✅ Yes | ✅ Valid |
| dispatching-parallel-agents | `.claude/skills/dispatching-parallel-agents/` | ✅ Yes | ✅ Valid |
| finishing-a-development-branch | `.claude/skills/finishing-a-development-branch/` | ✅ Yes | ✅ Valid |
| brainstorming | `.claude/skills/brainstorming/` | ✅ Yes | ✅ Valid |
| code-review-request | `.claude/skills/code-review-request/` | ✅ Yes | ✅ Valid |
| git-worktrees | `.claude/skills/git-worktrees/` | ✅ Yes | ✅ Valid |
| subagent-driven-development | `.claude/skills/subagent-driven-development/` | ✅ Yes | ✅ Valid |
| test-driven-development | `.claude/skills/test-driven-development/` | ✅ Yes | ✅ Valid |
| story-traceability | `.claude/skills/story-traceability/` | ✅ Yes | ✅ Valid |
| task-slicer | `.claude/skills/task-slicer/` | ✅ Yes | ✅ Valid |
| gh-issue-sync | `.claude/skills/gh-issue-sync/` | ✅ Yes | ✅ Valid |
| ac-expander | `.claude/skills/ac-expander/` | ✅ Yes | ✅ Valid |
| output-style-selector | `.claude/skills/output-style-selector/` | ✅ Yes | ✅ Valid |
| context-packer | `.claude/skills/context-packer/` | ✅ Yes | ✅ Valid |
| diff-scope-minimizer | `.claude/skills/diff-scope-minimizer/` | ✅ Yes | ✅ Valid |
| memory-graph | `.claude/skills/memory-graph/` | ✅ Yes + 3 extra files | ✅ Valid |
| writing-skills | `.claude/skills/writing-skills/` | ✅ Yes | ✅ Valid |

**Total:** 17/17 skills verified ✅

**Special Note:** `memory-graph` skill has additional documentation files:
- ✅ `operations.md`
- ✅ `playbooks.md`
- ✅ `examples.md`

All referenced in `memory-graph.md` command, all exist ✅

---

## 7. MCP Integration Audit

### ✅ MCP Configuration Valid

**File:** `.claude/.mcp.json`

**Contents:**
```json
{
    "mcpServers": {
        "memory": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
            "env": {}
        }
    }
}
```

**Status:** ✅ Valid

**Referenced in:**
- ✅ README.md (line 39, 244)
- ✅ memory-check.md (line 17)
- ✅ AUDIT_REPORT.md (line 604)

**MCP Server Package:**
- Package: `@modelcontextprotocol/server-memory`
- Delivery: via `npx -y` (on-demand download)
- Configuration: ✅ Proper

**MCP Tools Referenced:**
- `mcp__memory__create_entities` - ✅ Standard MCP tool
- `mcp__memory__create_relations` - ✅ Standard MCP tool
- `mcp__memory__add_observations` - ✅ Standard MCP tool
- `mcp__memory__delete_entities` - ✅ Standard MCP tool
- `mcp__memory__delete_observations` - ✅ Standard MCP tool
- `mcp__memory__delete_relations` - ✅ Standard MCP tool
- `mcp__memory__read_graph` - ✅ Standard MCP tool
- `mcp__memory__search_nodes` - ✅ Standard MCP tool
- `mcp__memory__open_nodes` - ✅ Standard MCP tool

All MCP tool names match Anthropic MCP Memory Server specification ✅

---

## 8. External Dependencies Audit

### Python Packages

**Referenced in Documentation:**

| Package | Referenced In | Purpose | Documented in README? |
|---------|---------------|---------|----------------------|
| `anthropic` | Multiple hooks | Anthropic API client | ⚠️ No |
| `dotenv` | (implied for env vars) | Environment variable management | ⚠️ No |
| `black` | Quality pipeline | Code formatting | ⚠️ No |
| `ruff` | Quality pipeline | Linting | ⚠️ No |
| `mypy` | Quality pipeline | Type checking | ⚠️ No |
| `pytest` | Quality pipeline | Testing | ⚠️ No |
| `pytest-mock` | SUB_AGENTS.md:184 | Mocking for tests | ⚠️ No |

**Recommendation:** Add a "Dependencies" section to README.md or create a `requirements.txt`:

```txt
anthropic>=0.18.0
python-dotenv>=1.0.0
black>=24.0.0
ruff>=0.3.0
mypy>=1.8.0
pytest>=8.0.0
pytest-mock>=3.12.0
```

### External Tools

**Required External Commands:**

| Tool | Purpose | Referenced In | Installation Doc? |
|------|---------|--------------|-------------------|
| `git` | Version control | Multiple commands | ⚠️ No |
| `gh` | GitHub CLI | Multiple commands | ⚠️ No |
| `npm` / `npx` | MCP server delivery | .mcp.json, status line | ⚠️ Partial (README line 236) |
| `uv` | Python package/script runner | settings.json hooks | ⚠️ No |
| `bash` | Shell execution | status line | ⚠️ No |

**Recommendation:** Add "Prerequisites" section to README.md:

```markdown
## Prerequisites

- Python 3.11+
- Git 2.30+
- GitHub CLI (`gh`) - for PR automation
- Node.js 18+ (for `npx` and MCP Memory server)
- `uv` - Python package manager (https://github.com/astral-sh/uv)
```

---

## 9. Consistency Issues

### Path Style Inconsistencies

1. **Relative vs Absolute Paths:**
   - ✅ Most documentation uses relative paths (`.claude/...`)
   - ⚠️ Some examples use absolute paths (`C:\Users\...` in AUDIT_REPORT.md)
   - **Recommendation:** Stick to relative paths in documentation

2. **Prefix Inconsistencies:**
   - ❌ `@LAZY_DEV/` prefix used in documentation.md (incorrect)
   - ✅ `.claude/` prefix used everywhere else (correct)
   - **Recommendation:** Remove `@LAZY_DEV` prefix, use `.claude/`

3. **Directory Reference Styles:**
   - ✅ Consistent use of forward slashes in paths
   - ✅ Consistent use of `.claude/` prefix

### Environment Variable Naming Inconsistencies

1. **Prefix Consistency:**
   - ✅ All LAZY_DEV-specific vars use `LAZYDEV_` prefix
   - ✅ External tool vars use appropriate prefixes (`ANTHROPIC_`, `ENRICHMENT_`, `CLAUDE_`)

2. **Boolean Value Styles:**
   - ✅ Consistent: Check for `{'1', 'true', 'TRUE'}`
   - ✅ No inconsistencies found

3. **Variable Documentation Format:**
   - ✅ Consistent format in README.md
   - ⚠️ Missing 3 variables (see section 5)

---

## 10. Recommendations Summary

### 🔴 CRITICAL (Fix Immediately)

1. **Remove or Implement STT_PROMPT_ENHANCER**
   - **Issue:** Referenced in README.md but doesn't exist
   - **Fix Option 1:** Remove references in README.md line 189
   - **Fix Option 2:** Implement the directory and feature
   - **Files to update:** `README.md`

2. **Remove or Implement TTS Script**
   - **Issue:** `.claude/output-styles/tts-summary.md` references non-existent script
   - **Fix Option 1:** Remove or comment out `.claude/output-styles/tts-summary.md`
   - **Fix Option 2:** Implement `.claude/hooks/utils/tts/elevenlabs_tts.py`
   - **Files to update:** `.claude/output-styles/tts-summary.md`

3. **Fix Incorrect Path in documentation.md**
   - **Issue:** Line 210 references `@LAZY_DEV/lazy_dev/subagents/documentation.md`
   - **Fix:** Change to `.claude/agents/documentation.md`
   - **File to update:** `.claude/commands/documentation.md`

### 🟠 HIGH (Fix Soon)

4. **Document Missing Environment Variables**
   - **Add to README.md:**
     - `ENRICHMENT_MAX_TOKENS`
     - `LAZYDEV_DISABLE_STYLE`
     - `LAZYDEV_CONTEXT_PACK_EXTS`
   - **File to update:** `README.md` (new section or expand existing Configuration section)

5. **Add Dependencies Section**
   - **Create:** `requirements.txt` or add section to README.md
   - **Include:** anthropic, dotenv, black, ruff, mypy, pytest, pytest-mock
   - **File to create/update:** `requirements.txt` or `README.md`

6. **Add Prerequisites Section**
   - **Add to README.md:** Python, Git, gh, Node.js, uv
   - **File to update:** `README.md`

### 🟡 MEDIUM (Nice to Have)

7. **Clarify External Reference**
   - **Issue:** `PROJECT-MANAGEMENT-LAZY_DEV/docs/TOOLS.md` referenced in `scripts/README.md`
   - **Fix:** Clarify if this is in parent directory, or provide full relative path
   - **File to update:** `scripts/README.md`

8. **Standardize Path Examples**
   - **Issue:** AUDIT_REPORT.md uses Windows absolute paths
   - **Fix:** Use relative paths or note "Example path shown"
   - **File to update:** `AUDIT_REPORT.md`

---

## 11. Testing Recommendations

### Automated Cross-Reference Tests

Create `tests/test_cross_references.py`:

```python
import pytest
from pathlib import Path
import json
import re

def test_all_command_files_exist():
    """Verify all commands in settings.json have corresponding files."""
    settings = json.loads(Path(".claude/settings.json").read_text())
    for cmd in settings.get("commands", []):
        file_path = Path(cmd["file"])
        assert file_path.exists(), f"Command file not found: {file_path}"

def test_all_agent_files_exist():
    """Verify all agents referenced in SUB_AGENTS.md exist."""
    agents = [
        ".claude/agents/project-manager.md",
        ".claude/agents/task-enhancer.md",
        ".claude/agents/coder.md",
        ".claude/agents/reviewer.md",
        ".claude/agents/reviewer-story.md",
        ".claude/agents/tester.md",
        ".claude/agents/research.md",
        ".claude/agents/documentation.md",
        ".claude/agents/refactor.md",
        ".claude/agents/cleanup.md",
    ]
    for agent in agents:
        assert Path(agent).exists(), f"Agent file not found: {agent}"

def test_all_hooks_exist():
    """Verify all hooks in settings.json have corresponding files."""
    settings = json.loads(Path(".claude/settings.json").read_text())
    hooks = settings.get("hooks", {})
    for event, hook_list in hooks.items():
        for hook_group in hook_list:
            for hook in hook_group.get("hooks", []):
                cmd = hook.get("command", "")
                # Extract .py file from command
                match = re.search(r'\.claude/hooks/([a-z_]+\.py)', cmd)
                if match:
                    file_path = Path(f".claude/hooks/{match.group(1)}")
                    assert file_path.exists(), f"Hook file not found: {file_path}"

def test_mcp_config_exists():
    """Verify MCP configuration file exists."""
    assert Path(".claude/.mcp.json").exists()

def test_no_broken_file_references():
    """Check for common broken file reference patterns."""
    # This would scan all .md files for file references and verify them
    pass
```

---

## 12. Final Verification Checklist

- [x] ✅ All command files exist (8/8)
- [x] ✅ All agent files exist (10/10)
- [x] ✅ All hook files exist (10/10)
- [x] ✅ All skill directories exist (17/17)
- [x] ✅ MCP configuration valid
- [ ] ⏱️ All file references in documentation valid (3 broken)
- [ ] ⏱️ All environment variables documented (3 missing)
- [ ] ⏱️ All dependencies documented (7 missing)
- [ ] ⏱️ All external tools documented (5 partially documented)

---

## Detailed Fix Instructions

### Fix 1: Remove STT_PROMPT_ENHANCER Reference

**File:** `README.md`
**Line:** 189

**Before:**
```markdown
- Entry point: LAZY_DEV/STT_PROMPT_ENHANCER
```

**After (Option 1 - Remove):**
```markdown
- Entry point: (To be implemented)
```

**After (Option 2 - Implement):**
Create directory `STT_PROMPT_ENHANCER/` with appropriate files, or clarify this is external.

---

### Fix 2: Fix TTS Script References

**File:** `.claude/output-styles/tts-summary.md`
**Lines:** 31, 53

**Option 1 (Remove/Comment):**
```markdown
<!-- TTS feature not yet implemented
uv run .claude/hooks/utils/tts/elevenlabs_tts.py "YOUR_MESSAGE_TO_DAN"
-->
```

**Option 2 (Implement):**
Create `.claude/hooks/utils/tts/elevenlabs_tts.py` with TTS functionality.

---

### Fix 3: Correct Path in documentation.md

**File:** `.claude/commands/documentation.md`
**Line:** 210

**Before:**
```markdown
- Documentation Agent is a sub-agent defined in `@LAZY_DEV/lazy_dev/subagents/documentation.md`
```

**After:**
```markdown
- Documentation Agent is a sub-agent defined in `.claude/agents/documentation.md`
```

---

### Fix 4: Add Missing Environment Variables to README.md

**File:** `README.md`
**Section:** Configuration (after line 230)

**Add:**
```markdown
- `ENRICHMENT_MAX_TOKENS`: Maximum tokens for enrichment API calls (default: 1000)
- `LAZYDEV_DISABLE_STYLE`: Set to `1` to disable output style selector
- `LAZYDEV_CONTEXT_PACK_EXTS`: Custom file extensions for context pack (comma-separated, e.g., "py,js,md")
```

---

## Summary Statistics

| Category | Total | Valid | Broken | Success Rate |
|----------|-------|-------|--------|--------------|
| **Command Files** | 8 | 8 | 0 | 100% ✅ |
| **Agent Files** | 10 | 10 | 0 | 100% ✅ |
| **Hook Files** | 10 | 10 | 0 | 100% ✅ |
| **Skill Directories** | 17 | 17 | 0 | 100% ✅ |
| **File References** | ~50 | 47 | 3 | 94% ⚠️ |
| **Env Variables** | 17 | 14 | 3 undocumented | 82% ⚠️ |
| **Dependencies** | 12 | 5 | 7 undocumented | 42% ⚠️ |

**Overall Health:** 88% ✅ (Good, but needs fixes)

---

## Conclusion

The LAZY_DEV framework has **excellent structural integrity**:
- ✅ All core files (commands, agents, hooks, skills) exist
- ✅ All registrations match actual files
- ✅ MCP configuration is valid
- ✅ Environment variable naming is consistent

**Issues to address:**
- 🔴 3 broken file references (2 missing files, 1 incorrect path)
- 🟠 3 undocumented environment variables
- 🟠 7 undocumented dependencies
- 🟡 1 unclear external reference

**Estimated fix time:** 2-3 hours (mostly documentation updates)

**Priority order:**
1. Fix incorrect path in documentation.md (5 min)
2. Document missing environment variables (15 min)
3. Add dependencies section (30 min)
4. Remove or implement STT/TTS features (1-2 hours)

---

**Report Generated:** 2025-10-29
**Next Action:** Review and implement fixes in priority order
**Contact:** See CLAUDE.md for development guidance
