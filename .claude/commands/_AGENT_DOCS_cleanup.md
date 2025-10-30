# Agent Documentation for cleanup Command

## Agents Used in This Command

This command leverages automatic agent delegation. The following agent is invoked:

### 1. Cleanup Agent (`.claude/agents/cleanup.md`)
- **When**: Step 3 - After scanning codebase for dead code patterns
- **Purpose**: Analyze code to identify dead code that can be safely removed
- **Invocation**: Automatic via agent descriptions

**What it does:**
- Identifies unused imports, functions, variables
- Finds unreachable code blocks
- Locates commented-out code (>3 lines)
- Detects orphaned files (no imports)
- Finds deprecated code marked for removal
- Assesses safety level for each item (LOW/MEDIUM/HIGH risk)
- Categorizes findings: Safe to Remove, Review Recommended, Do Not Remove

**Context provided to agent:**
- Target paths to analyze
- Dead code patterns to look for
- Safe mode setting
- Dry run flag

**Invocation pattern:**
Claude automatically delegates to cleanup agent when you provide scan scope and dead code findings. The agent performs comprehensive analysis and returns structured recommendations.

---

## Agent Output Format

The agent returns structured analysis:

```yaml
dead_code_analysis:
  summary:
    total_items: N
    safe_to_remove: N
    review_recommended: N
    do_not_remove: N

  safe_removals:
    unused_imports: [...]
    unused_functions: [...]
    commented_code: [...]
    orphaned_files: [...]

  review_recommended: [...]

  total_lines_to_remove: N
```

This structured output drives the cleanup workflow (user approval → apply changes → quality pipeline → commit).

---

## Key Principle: Automatic Delegation

**No manual agent selection is required.**

Claude automatically invokes the cleanup agent when you provide:
- Scan scope (codebase, current-branch, or specific path)
- Dead code patterns detected (or request to detect them)
- Safety preferences

The agent performs thorough analysis and returns safe removal recommendations. You review and approve before changes are applied.
