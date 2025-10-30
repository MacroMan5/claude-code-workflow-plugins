# Examples

All examples assume the Memory MCP server is connected under the name `memory`, so tool names are `mcp__memory__...`.

## Project/Service
Persist a service and its basics.

1) Prevent duplicates
```
tool: mcp__memory__search_nodes
input: {"query": "service:alpha"}
```

2) Create entity if missing
```
tool: mcp__memory__create_entities
input: {
  "entities": [
    {
      "name": "service:alpha",
      "entityType": "service",
      "observations": [
        "owner: alice",
        "repo: github.com/org/alpha",
        "primary_language: python",
        "deploy_url: https://alpha.example.com"
      ]
    }
  ]
}
```

3) Add relation to its owner
```
tool: mcp__memory__create_relations
input: {
  "relations": [
    {"from": "service:alpha", "to": "person:alice", "relationType": "owned_by"}
  ]
}
```

## People
Create or enrich people entities.

```
tool: mcp__memory__create_entities
input: {"entities": [{"name": "person:alice", "entityType": "person", "observations": ["email: alice@example.com"]}]}
```

Add title change
```
tool: mcp__memory__add_observations
input: {"observations": [{"entityName": "person:alice", "contents": ["title: Staff Engineer (2025-10-27)"]}]}
```

## Corrections
Remove stale owner, add new owner.

```
tool: mcp__memory__delete_observations
input: {"deletions": [{"entityName": "service:alpha", "observations": ["owner: alice"]}]}
```

```
tool: mcp__memory__add_observations
input: {"observations": [{"entityName": "service:alpha", "contents": ["owner: bob"]}]}
```

