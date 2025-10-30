# Memory Graph Playbooks

Use these routing patterns to decide which tools to call and in what order.

## 1) Persist a New Entity (+ facts)
1. `mcp__memory__search_nodes` with the proposed name
2. If not found → `mcp__memory__create_entities`
3. Then `mcp__memory__add_observations`
4. Optionally `mcp__memory__open_nodes` to verify

Example intent → tools
- Intent: “Remember service Alpha (owner: Alice, repo: org/alpha)”
- Tools:
  - `create_entities` → name: "service:alpha", type: "service"
  - `add_observations` → key facts (owner, repo URL, language, deploy URL)

## 2) Add Relations Between Known Entities
1. `mcp__memory__open_nodes` for both
2. If either missing → create it first
3. `mcp__memory__create_relations`

Relation guidance
- Use active voice `relationType`: `depends_on`, `owned_by`, `maintained_by`, `deployed_to`, `docs_at`
- Prefer directional relations; add reverse relation only if it has a different meaning

## 3) Correct or Update Facts
1. `mcp__memory__open_nodes`
2. `mcp__memory__delete_observations` to remove stale/incorrect facts
3. `mcp__memory__add_observations` to append correct facts

## 4) Remove Entities or Links
- `mcp__memory__delete_relations` for just the link
- `mcp__memory__delete_entities` for full removal (cascades relations)

## 5) Explore or Export
- `mcp__memory__read_graph` to dump entire graph
- `mcp__memory__search_nodes` to find relevant nodes by keyword
- For focused context, use `mcp__memory__open_nodes` with names

## 6) Session Rhythm
- Before deep work: `search_nodes` or `open_nodes` for today’s entities
- During work: add small observations at decision points
- After work: link new entities and summarize outcomes as observations

