# Memory Graph Operations (I/O)

Use the fully-qualified tool names with the MCP prefix: `mcp__memory__<tool>`.

All tools below belong to the server `memory`.

## create_entities
Create multiple new entities. Skips any entity whose `name` already exists.

Input
```
{
  "entities": [
    {
      "name": "string",
      "entityType": "string",
      "observations": ["string", "string"]
    }
  ]
}
```

## create_relations
Create multiple relations. Skips duplicates.

Input
```
{
  "relations": [
    {
      "from": "string",
      "to": "string",
      "relationType": "string"  // active voice, e.g. "depends_on", "owned_by"
    }
  ]
}
```

## add_observations
Add observations to existing entities. Fails if `entityName` doesn’t exist.

Input
```
{
  "observations": [
    {
      "entityName": "string",
      "contents": ["string", "string"]
    }
  ]
}
```

## delete_entities
Remove entities and cascade their relations. No-op if missing.

Input
```
{ "entityNames": ["string", "string"] }
```

## delete_observations
Remove specific observations from entities. No-op if missing.

Input
```
{
  "deletions": [
    {
      "entityName": "string",
      "observations": ["string", "string"]
    }
  ]
}
```

## delete_relations
Remove specific relations. No-op if missing.

Input
```
{
  "relations": [
    {
      "from": "string",
      "to": "string",
      "relationType": "string"
    }
  ]
}
```

## read_graph
Return the entire graph.

Input: none

## search_nodes
Fuzzy search across entity names, types, and observations.

Input
```
{ "query": "string" }
```

## open_nodes
Return specific nodes and relations connecting them. Skips non-existent names.

Input
```
{ "names": ["string", "string"] }
```

