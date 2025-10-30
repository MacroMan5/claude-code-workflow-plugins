# Agent Documentation for story-fix-review Command

## Agents Used in This Command

This command leverages automatic agent delegation. The following agents may be invoked based on issue type:

### 1. Coder Agent (`.claude/agents/coder.md`)
- **When**: Fixing security issues, code issues, or bugs
- **Purpose**: Implement code fixes for security vulnerabilities and code quality issues
- **Invocation**: Automatic via agent descriptions

**Triggered by issue types:**
- Security vulnerabilities (SQL injection, XSS, etc.)
- Code quality issues (complexity, readability)
- Bug fixes
- Performance problems

### 2. Tester Agent (`.claude/agents/tester.md`)
- **When**: Fixing test gaps or missing test coverage
- **Purpose**: Write comprehensive tests for uncovered scenarios
- **Invocation**: Automatic via agent descriptions

**Triggered by issue types:**
- Missing test coverage
- Untested edge cases
- Test gaps in critical paths
- Missing integration tests

### 3. Refactor Agent (`.claude/agents/refactor.md`)
- **When**: Fixing architecture issues or code structure problems
- **Purpose**: Refactor code to improve architecture and design
- **Invocation**: Automatic via agent descriptions

**Triggered by issue types:**
- Architecture concerns
- Design pattern violations
- Code structure issues
- Separation of concerns problems

### 4. Documentation Agent (`.claude/agents/documentation.md`)
- **When**: Fixing missing or inadequate documentation
- **Purpose**: Add or improve documentation (docstrings, README, API docs)
- **Invocation**: Automatic via agent descriptions

**Triggered by issue types:**
- Missing docstrings
- Inadequate README
- Missing API documentation
- Unclear code comments

### 5. Reviewer Agent (`.claude/agents/reviewer.md`)
- **When**: After each fix is applied and quality pipeline passes
- **Purpose**: Validate the fix resolves the issue correctly
- **Invocation**: Automatic via agent descriptions

**Review criteria:**
- Original issue is resolved
- No new issues introduced
- Quality metrics maintained
- Implementation meets standards

---

## Automatic Agent Routing

**Manual routing logic (lines 146-238 in original command) should be REMOVED.**

The command currently contains manual if/else logic for agent selection:

```markdown
**Routing Logic:**

1. **Load agent registry**: Read `.claude/core/agent_registry.json`

2. **Parse issue category**: Extract category from report issue (security, code_issue, test_gap, architecture, documentation, etc.)

3. **Normalize category**: Convert to lowercase with underscores
   - "Code Issue" → "code_issue"
   ...
```

**This entire section (lines 146-238) should be deleted.**

---

## Simplified Approach: Context-Based Delegation

**Instead of manual routing, use conversation context:**

1. Load issue from report
2. Provide issue details in conversation:
   - Issue category (security, test gap, etc.)
   - Problem description
   - Affected files
   - Proposed solution
3. Claude automatically delegates to the appropriate agent

**Example:**

```markdown
Issue from report:
- Category: Security
- Problem: SQL injection in auth.py line 45
- Solution needed: Use parameterized queries

Claude reads this context and automatically routes to the coder agent specializing in security fixes.
```

---

## Key Principle: Automatic Delegation

**No manual agent selection or registry lookups needed.**

Claude automatically invokes the appropriate agent based on:
- Issue category in the conversation
- Problem description context
- Agent specialization descriptions

Simply provide the issue details clearly, and Claude handles routing intelligently.

---

## What to Remove from story-fix-review.md

**Delete lines 146-238:**
- Entire `<agent_registry>` section
- Manual routing logic
- Registry JSON examples
- Mapping tables

**Replace with:**
- Simple statement: "Claude automatically delegates to appropriate agent based on issue type"
- List which agents handle which categories (as shown above)
- Note that invocation is automatic via agent descriptions
