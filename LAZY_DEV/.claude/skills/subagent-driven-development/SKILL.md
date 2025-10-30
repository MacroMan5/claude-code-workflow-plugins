---
name: subagent-driven-development
description: Route subtasks to the best sub-agent (coder, reviewer, research, PM) with clear handoffs
version: 0.1.0
tags: [agents, orchestration]
triggers:
  - subagent
  - delegate
  - handoff
---

# Subagent-Driven Development

## Purpose
Decompose a problem and delegate each subtask to the appropriate agent with minimal ceremony.

## Behavior
1. Identify subtasks (≤5) and required outputs.
2. Map to agents:
   - Project Manager → story/tasks
   - Coder → implementation/tests
   - Reviewer → findings/patch plan
   - Research → docs/examples
3. For each handoff, specify: input, expected artifacts, and success criteria.
4. Summarize progress and next agent to call.

## Guardrails
- Keep subtasks atomic and ≤4 hours each.
- Avoid duplicate work; reuse artifacts across agents.

## Integration
- All agents under `LAZY_DEV/.claude/agents/`; `/lazy create-feature`, `/lazy task-exec`, `/lazy story-review`.

## Example Prompt
> Break this feature into subagent tasks and propose the call sequence.

