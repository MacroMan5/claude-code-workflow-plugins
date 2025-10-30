# Agent Documentation for task-exec Command

## Agents Used in This Command

This command leverages automatic agent delegation. The following agents may be invoked:

### 1. Research Agent (`.claude/agents/research.md`) - OPTIONAL
- **When**: If `--with-research` flag is provided, before code implementation
- **Purpose**: Research unfamiliar technologies, patterns, or approaches
- **Invocation**: Automatic via agent descriptions

**What it does:**
- Researches best practices for the task
- Identifies relevant libraries and frameworks
- Notes potential pitfalls and gotchas
- Gathers code examples
- Recommends implementation approach

**Invocation pattern:**
Enabled with `--with-research` flag. Claude automatically delegates to research agent before implementation begins.

### 2. Coder Agent (`.claude/agents/coder.md`)
- **When**: Phase 2 - Implementation phase for all tasks
- **Purpose**: Implement the functionality described in the task
- **Invocation**: Automatic via agent descriptions

**What it does:**
- Writes implementation code following TDD approach
- Adds comprehensive type hints and docstrings
- Handles edge cases and errors
- Ensures cross-OS compatibility
- Creates test files alongside implementation

**Invocation pattern:**
Claude automatically routes to coder agent when implementation is needed. No manual selection required.

### 3. Reviewer Agent (`.claude/agents/reviewer.md`)
- **When**: Phase 3 - After quality pipeline passes
- **Purpose**: Review implementation for correctness and quality
- **Invocation**: Automatic via agent descriptions

**What it does:**
- Validates implementation matches acceptance criteria
- Checks test coverage is comprehensive
- Reviews error handling
- Verifies security best practices
- Approves or requests changes

**Invocation pattern:**
Claude automatically invokes reviewer after quality checks pass. Returns APPROVED or CHANGES_REQUESTED.

---

## Agent Invocation Flow

**Sequential (Single Task)**:
1. [Optional] Research Agent - if `--with-research` flag provided
2. Coder Agent - implements the task
3. Quality Pipeline - format → lint → type → test (not an agent)
4. Reviewer Agent - validates the implementation

**Parallel (Multiple Independent Tasks)**:
- Multiple Coder agents run in parallel (one per task)
- Each followed by its own Reviewer agent
- Quality pipeline runs for each task independently

---

## Key Principle: Automatic Delegation

**Claude automatically invokes the appropriate agent based on the pipeline stage.**

- Research stage → research agent
- Implementation stage → coder agent
- Review stage → reviewer agent

No manual agent selection or routing logic needed. Simply progress through the workflow and Claude delegates intelligently.

---

## Note: Manual Agent Registry Reference Removed

**Line 13-18 of the original command should be deleted:**

```markdown
## Agent Routing

This command uses automatic agent routing via `.claude/core/agent_registry.json`:
- **Research**: intent "research-topic" → research agent
- **Implementation**: intent "implement-code" → coder agent
- **Review**: intent "review-code" → reviewer agent
```

This manual reference is unnecessary. Claude's automatic delegation handles this without explicit registry lookups.
