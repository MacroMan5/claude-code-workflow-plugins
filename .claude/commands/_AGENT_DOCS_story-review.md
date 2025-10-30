# Agent Documentation for story-review Command

## Agents Used in This Command

This command leverages automatic agent delegation. The following agent is invoked:

### 1. Story Reviewer Agent (`.claude/agents/reviewer-story.md`)
- **When**: Step 6 - After collecting all tasks, commits, and test results
- **Purpose**: Review complete user story implementation and validate acceptance criteria
- **Invocation**: Automatic via agent descriptions

**What it does:**
- Validates all acceptance criteria are met
- Reviews architecture across all tasks
- Checks security requirements are satisfied
- Validates test coverage is comprehensive
- Ensures all tasks work together cohesively
- Returns APPROVED or CHANGES_NEEDED with detailed feedback

**Context provided to agent:**
- Complete user story content
- All task implementations
- Commit history summary
- Test results
- Files changed summary

**Invocation pattern:**
Claude automatically delegates to story reviewer when story validation is needed. Simply provide the story context and implementation details.

---

## Review Output

The agent returns one of two decisions:

**APPROVED**:
- All acceptance criteria met
- All tasks integrated successfully
- Quality metrics satisfactory
- Ready for PR creation

**CHANGES_NEEDED**:
- Lists specific issues found (Critical/Important/Minor)
- Provides actionable feedback
- References which tasks need fixes
- Returns control to user for fixes

---

## Key Principle: Automatic Delegation

**No manual agent selection is required.**

Claude automatically invokes the reviewer-story agent when you provide:
- Story file content
- Task completion status
- Implementation artifacts
- Test results

The agent extracts all necessary context from the conversation and performs comprehensive validation.
