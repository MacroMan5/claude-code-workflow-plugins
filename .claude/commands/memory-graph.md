---
description: Manage persistent knowledge via MCP Memory Graph
argument-hint: [intent]
allowed-tools: Read, Write, Grep, Glob, Bash, Task
---

# Memory Graph Command

This command activates the Memory Graph Skill and guides you to use the MCP Memory server tools to persist, update, search, and prune knowledge.

## Inputs

INTENT: ${1:-auto}

## Skill

Include the Memory Graph Skill files:
- .claude/skills/memory-graph/SKILL.md
- .claude/skills/memory-graph/operations.md
- .claude/skills/memory-graph/playbooks.md
- .claude/skills/memory-graph/examples.md

If any file is missing, read the repo to locate them under `.claude/skills/memory-graph/`.

## Behavior

- Detect entities, relations, and observations in the current context
- Use MCP tool names prefixed with `mcp__memory__`
- Avoid duplicates by searching before creating
- Keep observations small and factual, include dates when relevant
- Verify writes with `open_nodes` when helpful

## Planner

1. If INTENT == `auto`, infer one of: `persist-new`, `enrich`, `link`, `correct`, `prune`, `explore`
2. Route per `playbooks.md`
3. Execute the needed MCP tool calls
4. Print a short summary of what changed
5. When appropriate, suggest next relations or entities

## MCP Tooling

Target server name: `memory` (tools appear as `mcp__memory__<tool>`)

Core tools:
- create_entities, add_observations, create_relations
- delete_entities, delete_observations, delete_relations
- read_graph, search_nodes, open_nodes

## Examples

Persist a new service and owner
```
/lazy memory-graph "persist-new service:alpha (owner: alice, repo: org/alpha)"
```

Explore existing graph
```
/lazy memory-graph explore
```

Correct a stale fact
```
/lazy memory-graph "correct owner for service:alpha -> bob"
```

