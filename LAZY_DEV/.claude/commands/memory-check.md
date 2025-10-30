---
description: Verify Memory MCP connectivity and list basic stats
argument-hint: [action]
allowed-tools: Read, Write, Grep, Glob, Bash, Task
---

# Memory Connectivity Check

ACTION: ${1:-status}

If the `memory` MCP server is available, call the following tools:

- `mcp__memory__read_graph` and report entity/relation counts
- `mcp__memory__search_nodes` with a sample query like `service:`

If any calls fail, print a clear remediation guide:
1) Ensure `.mcp.json` exists at workspace root (see LAZY_DEV/.claude/.mcp.json)
2) Ensure Node.js is installed and `npx -y @modelcontextprotocol/server-memory` works
3) Reload Claude Code for this workspace

Output a concise summary:
- Server reachable: yes/no
- Entities: N, Relations: M (or unknown)
- Sample search results: top 5 names

