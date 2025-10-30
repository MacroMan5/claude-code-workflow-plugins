# Command File Integration Guide

## Overview

This guide explains how to integrate agent documentation into each command file to make agent usage explicit while relying on automatic delegation.

## Files Created

Six agent documentation reference files have been created:

1. `_AGENT_DOCS_create-feature.md` - Documents project-manager and task-enhancer agents
2. `_AGENT_DOCS_task-exec.md` - Documents research, coder, and reviewer agents
3. `_AGENT_DOCS_story-review.md` - Documents reviewer-story agent
4. `_AGENT_DOCS_story-fix-review.md` - Documents coder, tester, refactor, documentation, and reviewer agents
5. `_AGENT_DOCS_cleanup.md` - Documents cleanup agent
6. `_AGENT_DOCS_documentation.md` - Documents documentation agent

## Integration Pattern

For each command file, add an "Agents Used" section that follows this pattern:

```markdown
## Agents Used in This Command

This command leverages automatic agent delegation. The following agents may be invoked:

### 1. [Agent Name] (`.claude/agents/filename.md`)
- **When**: [Trigger condition/workflow step]
- **Purpose**: [What the agent does]
- **Invocation**: Automatic via agent descriptions

**What it does:**
- [Capability 1]
- [Capability 2]
- [Capability 3]

**Invocation pattern:**
[Brief description of how Claude automatically routes to this agent]

---

## Key Principle: Automatic Delegation

**No manual agent selection is required.**

Claude automatically invokes the appropriate agent based on:
- Conversation context (what you're asking for)
- Agent descriptions (which agent specializes in what)
- Task requirements (what needs to be done)
```

---

## Specific Integration Instructions

### 1. create-feature.md

**Where to add**: After line 102 ("Deployment constraints")

**Section to add**: See `_AGENT_DOCS_create-feature.md`

**Key points:**
- Documents project-manager agent (Step 3)
- Documents task-enhancer agent (Step 4)
- Emphasizes automatic delegation
- No manual Task tool invocation needed

**Lines to modify:**
- Line 117: Remove "Use the Task tool with `subagent_type="project-manager"` to invoke the PM agent"
- Replace with: "Provide context in conversation and Claude will automatically delegate to project-manager agent"
- Line 172: Remove similar Task tool reference for task-enhancer

---

### 2. task-exec.md

**Where to modify/remove**: Lines 13-18 contain manual agent routing section

**Section to remove:**
```markdown
## Agent Routing

This command uses automatic agent routing via `.claude/core/agent_registry.json`:
- **Research**: intent "research-topic" → research agent
- **Implementation**: intent "implement-code" → coder agent
- **Review**: intent "review-code" → reviewer agent
```

**Section to add**: After line 5 (after "allowed-tools")

See `_AGENT_DOCS_task-exec.md` for full content.

**Key changes:**
- Remove manual registry reference (lines 13-18)
- Add comprehensive "Agents Used" section documenting:
  - Research agent (optional, with --with-research flag)
  - Coder agent (main implementation)
  - Reviewer agent (validation)
- Emphasize automatic delegation
- Note sequential vs parallel invocation patterns

---

### 3. story-review.md

**Where to add**: After line 48 (after Memory Graph Usage section)

**Section to add**: See `_AGENT_DOCS_story-review.md`

**Key points:**
- Documents reviewer-story agent
- Explains APPROVED vs CHANGES_NEEDED outcomes
- Emphasizes automatic delegation based on story context
- No manual agent selection needed

**No lines to remove** - this command doesn't have manual routing logic.

---

### 4. story-fix-review.md

**Major changes needed - both removal and addition**

**Section to REMOVE**: Lines 146-238 (entire `<agent_registry>` section)

This includes:
- Manual routing logic
- Registry JSON loading pseudo-code
- Category normalization rules
- Mapping tables
- Agent config examples
- Example routing flow

**Section to ADD**: After line 145 (before "### 3. Systematic Issue Resolution")

See `_AGENT_DOCS_story-fix-review.md` for full content.

**Key changes:**
- Remove all manual routing logic (lines 146-238)
- Add "Agents Used in This Command" section documenting:
  - Coder agent (security, code issues, bugs)
  - Tester agent (test gaps)
  - Refactor agent (architecture issues)
  - Documentation agent (missing docs)
  - Reviewer agent (validation)
- Emphasize automatic delegation based on issue category in conversation
- Simplify Step 3 to just "provide issue context, Claude routes automatically"

**Lines to modify in Step 3:**
- Line 307-350: Remove explicit agent invocation blocks with manual Task tool calls
- Replace with: "Provide issue details in conversation, Claude automatically delegates to appropriate agent"

---

### 5. cleanup.md

**Where to add**: After line 82 (after "Scanning for dead code..." line)

**Section to add**: See `_AGENT_DOCS_cleanup.md`

**Key points:**
- Documents cleanup agent
- Explains safety assessment (LOW/MEDIUM/HIGH risk)
- Shows structured output format
- Emphasizes automatic delegation based on scan scope

**Lines to modify:**
- Line 139: Remove "Use the Task tool with `subagent_type="cleanup"` to invoke the Cleanup Agent"
- Replace with: "Claude automatically delegates to cleanup agent when you provide scan scope and context"

---

### 6. documentation.md

**Where to add**: After line 52 (after "If FORMAT is invalid..." line)

**Section to add**: See `_AGENT_DOCS_documentation.md`

**Key points:**
- Documents documentation agent
- Lists all supported formats (docstrings, readme, api, security, setup)
- Explains what each format produces
- Emphasizes automatic delegation based on scope and format

**Lines to modify:**
- Line 60-82: Simplify agent invocation section
- Remove explicit Task tool reference
- Replace with: "Provide scope and format in conversation, Claude automatically delegates"

---

## General Principles for All Updates

### 1. Consistent Structure

Every "Agents Used" section should have:
- Clear heading: "## Agents Used in This Command"
- Introduction: "This command leverages automatic agent delegation..."
- Per-agent subsections with: When, Purpose, Invocation
- "What it does" bullet list
- "Invocation pattern" explanation
- Footer: "## Key Principle: Automatic Delegation"

### 2. Remove Manual Invocation Language

Replace phrases like:
- "Use the Task tool with `subagent_type=...`"
- "Call @agent-name with..."
- "Invoke Task tool..."
- "Manual agent selection..."

With phrases like:
- "Claude automatically delegates..."
- "Provide context in conversation..."
- "No manual agent selection required..."
- "Simply provide [context], Claude routes intelligently..."

### 3. Emphasize Context Over Explicit Calls

Instead of:
```markdown
Task: @agent-coder
Input:
  - $task: "..."
  - $context: "..."
```

Use:
```markdown
Provide task details in conversation:
- Task description
- Relevant context
- Constraints

Claude automatically routes to coder agent.
```

### 4. Keep Agent Descriptions Informative

Each agent section should clearly explain:
- **When** it's invoked (which workflow step or condition)
- **Why** it's needed (what problem it solves)
- **What** it produces (deliverables/output)
- **How** it's invoked (automatic based on context)

### 5. Maintain Existing Workflow Logic

The agent documentation sections are **additions** (or replacements of manual routing logic).

They should **not** change:
- The overall command workflow steps
- Quality pipeline requirements
- Git operations
- Error handling
- Success criteria
- Example usage

Only change:
- How agents are described and documented
- Manual Task tool invocation language
- Agent selection/routing logic (remove manual, emphasize automatic)

---

## Testing the Updates

After integrating agent documentation into each command:

1. **Read each command file** - ensure it flows naturally
2. **Check for consistency** - all "Agents Used" sections follow the same pattern
3. **Verify removals** - manual routing logic is gone (especially story-fix-review.md)
4. **Test commands** - run `/lazy create-feature`, `/lazy task-exec`, etc. to ensure they work as expected
5. **Validate documentation** - ensure agent descriptions are accurate and helpful

---

## Summary of Changes

### create-feature.md
- **Add**: "Agents Used" sections for project-manager and task-enhancer agents
- **Modify**: Remove explicit Task tool invocation language (2 places)
- **Impact**: Makes automatic delegation clear

### task-exec.md
- **Remove**: Lines 13-18 (manual agent routing section)
- **Add**: Comprehensive "Agents Used" section for research, coder, reviewer agents
- **Impact**: Removes manual registry reference, emphasizes automatic delegation

### story-review.md
- **Add**: "Agents Used" section for reviewer-story agent
- **Impact**: Documents agent usage clearly

### story-fix-review.md
- **Remove**: Lines 146-238 (entire manual routing logic)
- **Add**: "Agents Used" section for all 5 agents (coder, tester, refactor, documentation, reviewer)
- **Modify**: Step 3 to remove manual agent selection logic
- **Impact**: Massive simplification, removes ~90 lines of manual routing code

### cleanup.md
- **Add**: "Agents Used" section for cleanup agent
- **Modify**: Remove explicit Task tool reference
- **Impact**: Makes automatic delegation clear

### documentation.md
- **Add**: "Agents Used" section for documentation agent
- **Modify**: Simplify agent invocation section
- **Impact**: Makes automatic delegation clear

---

## Next Steps

1. Review this integration guide
2. Integrate agent documentation into each command file
3. Test each command to ensure functionality is unchanged
4. Update any related documentation (README, IMPLEMENTATION-PLAN.md) if needed
5. Commit changes with message: "docs(commands): add explicit agent usage documentation with automatic delegation"

---

## Benefits of These Changes

1. **Clarity**: Users know which agents are involved in each command
2. **Simplicity**: Removes complex manual routing logic
3. **Trust**: Emphasizes Claude's intelligent automatic delegation
4. **Maintainability**: Less code to maintain, easier to add new agents
5. **Consistency**: All commands document agents the same way
6. **User Experience**: Users understand the workflow without needing to read agent files

---

**Version**: 1.0
**Created**: 2025-10-29
**Purpose**: Guide integration of agent documentation into command files
