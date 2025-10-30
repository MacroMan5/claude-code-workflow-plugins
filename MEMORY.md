# MEMORY.md

Automatic Memory System - Persistent Knowledge Management with MCP Memory

---

## Table of Contents

1. [Overview](#overview)
2. [Implementation Status](#implementation-status)
3. [How Auto-Memory Works](#how-auto-memory-works)
4. [What Gets Stored](#what-gets-stored)
5. [Memory Graph Structure](#memory-graph-structure)
6. [Automatic Triggers](#automatic-triggers)
7. [Manual Memory Management](#manual-memory-management)
8. [Memory-Driven Context Injection](#memory-driven-context-injection)
9. [Configuration](#configuration)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Overview

LAZY_DEV integrates with **MCP (Model Context Protocol) Memory** to create a persistent knowledge graph that grows and evolves across sessions.

### The Problem

Traditional AI-assisted development suffers from:
- ❌ Lost context between sessions
- ❌ Constant re-prompting of team conventions
- ❌ Repeated explanations of architecture decisions
- ❌ No memory of service ownership or dependencies

### The LAZY_DEV Solution

```
Session 1: User mentions "service:payment owned_by:alice"
              ↓
           Hook detects durable fact
              ↓
           Suggests: Use mcp__memory__create_entities
              ↓
           You use MCP tools to store
              ↓
Session 2: Working on payment service
              ↓
           Hook injects memory skill guidance
              ↓
           You query: mcp__memory__search_nodes
              ↓
           Context retrieved: "Alice owns payment service"
```

---

## Implementation Status

### ✅ What's Implemented

**MCP Memory Server Integration:**
- ✅ `.claude/.mcp.json` configured for `@modelcontextprotocol/server-memory`
- ✅ All MCP memory tools available: `mcp__memory__*`

**Auto-Detection Hooks:**
- ✅ `user_prompt_submit.py` - Detects memory intents and entity mentions
- ✅ `memory_suggestions.py` (PostToolUse) - Suggests memory storage after tools

**Memory Graph Skill:**
- ✅ `.claude/skills/memory-graph/` - Complete skill documentation
- ✅ Operations guide, playbooks, examples

**What This Means:**
- Memory storage is **available** via MCP tools
- Hooks **detect** durable facts and **suggest** actions
- You must **manually invoke** MCP tools (Claude Code calls them for you when prompted)

### ⚠️ What's Semi-Automated

**Detection → Suggestion (Working):**
```python
# user_prompt_submit.py detects:
"service:payment owned_by:alice"
     ↓
Injects Memory Graph skill block with guidance
     ↓
Claude Code sees: "Use mcp__memory__create_entities"
```

**Manual Execution (Required):**
```python
# You (or Claude Code) must then actually call:
mcp__memory__create_entities({
    "entities": [{
        "name": "service:payment",
        "entityType": "service",
        "observations": ["Owned by Alice"]
    }]
})
```

### ❌ What's NOT Fully Automatic (Yet)

**Automatic Storage with Countdown:**
- ❌ No 5-second countdown auto-store (as documented)
- ❌ No "auto-store unless cancelled" feature
- ⚠️ This would require additional hook logic

**Automatic Context Injection:**
- ❌ No automatic retrieval based on keywords
- ❌ No auto-injection of related entities into prompts
- ✅ But: Skill guidance helps Claude Code query memory when relevant

**Why It Still Works:**
- Hook detects → Suggests → Claude Code invokes MCP tools
- It's **AI-assisted memory** rather than **fully automatic**
- Effective in practice, just requires Claude Code to execute

### Summary: How It Actually Works

**Current State:**
```
You: "service:payment owned_by:alice"
     ↓
Hook: [Detects entities, injects skill guidance]
     ↓
Claude Code: [Sees guidance, decides to store]
     ↓
Claude Code: mcp__memory__create_entities(...)
     ↓
MCP Memory: [Stores to graph]
     ✅ Persisted!

Next Session:
You: "Update payment service"
     ↓
Hook: [Detects entity mention, injects skill guidance]
     ↓
Claude Code: mcp__memory__search_nodes("payment")
     ↓
MCP Memory: [Returns: owned by Alice, uses Stripe API]
     ↓
Claude Code: [Uses context in implementation]
```

**It's Semi-Automatic:**
- ✅ Detection is automatic (hooks)
- ✅ Guidance is automatic (skill injection)
- ⚠️ Storage/retrieval requires Claude Code to invoke MCP tools
- ✅ Works well in practice (Claude Code is smart about using tools)

---

## How Auto-Memory Works

### The Three-Phase System (Current Implementation)

#### Phase 1: Detection (UserPromptSubmit Hook)

**Trigger:** Every user prompt

**Actual Detection Logic:**
```python
# From .claude/hooks/user_prompt_submit.py

# Hard triggers for explicit memory intents
hard_triggers = [
    "save to memory",
    "add to memory",
    "memory graph",
    "knowledge graph",
    "persist this",
    "remember this",
    "create entity",
    "link entities",
    "search memory",
]

# Entity mention detection (regex)
ENTITY_MENTION_PATTERN = re.compile(
    r"\b(person|service|repo|dataset|api|team):[\w\-/\.]+",
    re.IGNORECASE
)
```

**What Actually Happens:**
```
User: "service:payment owned_by:alice"
   ↓
Hook detects entity mentions
   ↓
Injects Memory Graph skill block into prompt
   ↓
Claude Code sees guidance to use mcp__memory__* tools
```

**Output (Injected into prompt):**
```markdown
[MEMORY GRAPH SKILL]

Detected potential memory entities:
- service:payment
- person:alice

Memory MCP Server available as `memory`.
Tools: mcp__memory__create_entities, mcp__memory__search_nodes, etc.

Suggested workflow:
1) mcp__memory__search_nodes to avoid duplicates
2) mcp__memory__create_entities (when missing)
3) mcp__memory__add_observations with small, dated facts
4) mcp__memory__create_relations to link entities
```

#### Phase 2: Assisted Storage (Not Fully Automatic)

**Current Behavior:**
```
Hook provides guidance
   ↓
Claude Code decides to store
   ↓
Claude Code calls: mcp__memory__create_entities
   ↓
MCP Memory server stores
   ↓
✅ Memory persisted
```

**Example Tool Call:**
```python
# Claude Code invokes (based on hook guidance):
mcp__memory__create_entities({
    "entities": [
        {
            "name": "service:payment",
            "entityType": "service",
            "observations": ["Payment processing service", "Owned by Alice"]
        },
        {
            "name": "person:alice",
            "entityType": "person",
            "observations": ["Team lead for backend", "Owns payment service"]
        }
    ]
})

mcp__memory__create_relations({
    "relations": [
        {
            "from": "service:payment",
            "to": "person:alice",
            "relationType": "owned_by"
        }
    ]
})
```

#### Phase 3: Assisted Retrieval (Skill-Guided)

**Current Behavior:**
```
User: "Update payment service"
   ↓
Hook detects entity mention
   ↓
Injects Memory Graph skill guidance
   ↓
Claude Code queries: mcp__memory__search_nodes
   ↓
MCP returns relevant entities
   ↓
Claude Code uses context in implementation
```

**Example Retrieval:**
```python
# Claude Code invokes:
mcp__memory__search_nodes({
    "query": "payment"
})

# MCP returns:
{
    "nodes": [
        {
            "name": "service:payment",
            "entityType": "service",
            "observations": ["Owned by Alice", "Uses Stripe API"],
            "relations": [
                {"to": "person:alice", "type": "owned_by"},
                {"to": "service:stripe-api", "type": "depends_on"}
            ]
        }
    ]
}

# Claude Code then knows:
# - Payment service owned by Alice
# - Depends on Stripe API
# - Can coordinate with Alice if needed
```

---

## What Gets Stored

### Entity Types

LAZY_DEV auto-detects and stores these entity types:

#### 1. Service Ownership
```bash
Pattern: "service:<name> owned_by:<owner>"

Examples:
- "service:payment owned_by:alice"
- "service:auth owned_by:bob"
- "service:api owned_by:team:backend"
```

#### 2. Repository Information
```bash
Pattern: "repo:<org/name> endpoint:<url>"

Examples:
- "repo:org/api endpoint:https://api.example.com"
- "repo:org/frontend uses:react"
- "repo:org/backend uses:fastapi"
```

#### 3. Architecture Patterns
```bash
Pattern: "project uses:<pattern>"

Examples:
- "project uses:repository-pattern"
- "project uses:event-driven-architecture"
- "api uses:rest"
```

#### 4. Team Conventions
```bash
Pattern: "team:<name> prefers:<convention>"

Examples:
- "team:backend prefers:async-patterns"
- "team:frontend prefers:functional-components"
- "team:all requires:type-hints"
```

#### 5. Dependency Relationships
```bash
Pattern: "<service> depends_on:<dependency>"

Examples:
- "payment depends_on:stripe-api"
- "checkout depends_on:payment"
- "billing depends_on:payment,checkout"
```

#### 6. Configuration Values
```bash
Pattern: "config:<key> value:<value>"

Examples:
- "config:api-timeout value:30s"
- "config:max-retries value:3"
- "config:cache-ttl value:3600"
```

---

## Memory Graph Structure

### Graph Model

MCP Memory uses a graph database model:

```
┌─────────────┐
│   ENTITY    │
├─────────────┤
│ name        │
│ entityType  │
│ observations│
└─────────────┘
       │
       │ RELATION
       ↓
┌─────────────┐
│   ENTITY    │
├─────────────┤
│ name        │
│ entityType  │
│ observations│
└─────────────┘
```

### Example Graph

```
service:payment (SERVICE)
  observations:
    - "Handles payment processing with Stripe"
    - "Owned by Alice"
    - "Uses async patterns"

  relations:
    - owned_by → person:alice
    - depends_on → service:stripe-api
    - uses → pattern:async
    - relates_to → service:billing

person:alice (PERSON)
  observations:
    - "Backend team lead"
    - "Owns payment and billing services"

  relations:
    - owns → service:payment
    - owns → service:billing

pattern:async (PATTERN)
  observations:
    - "Async/await pattern for I/O operations"
    - "Preferred by backend team"

  relations:
    - used_by → service:payment
```

---

## Automatic Triggers

### UserPromptSubmit Hook Logic

**Hook File:** `.claude/hooks/user_prompt_submit.py`

**Trigger Conditions:**

```python
def should_auto_store(prompt: str) -> bool:
    """Determine if prompt contains durable facts."""

    # Triggers:
    triggers = [
        # Ownership statements
        r"owned by",
        r"maintained by",
        r"belongs to",

        # Architecture decisions
        r"we use",
        r"pattern:",
        r"architecture:",

        # Configuration
        r"config:",
        r"setting:",
        r"endpoint:",

        # Dependencies
        r"depends on",
        r"requires",
        r"integrates with",
    ]

    return any(re.search(trigger, prompt, re.IGNORECASE) for trigger in triggers)
```

**Auto-Store Workflow:**

```
User Prompt
    ↓
UserPromptSubmit Hook
    ↓
Detect durable facts?
    ↓ Yes
Show suggestion + countdown
    ↓
5 seconds elapsed
    ↓
Store to MCP Memory
    ↓
Continue with command
```

---

## Manual Memory Management

### Store Memory Manually

```bash
# Basic syntax
/lazy memory-graph "<statement>"

# Examples
/lazy memory-graph "service:payment owned_by:alice"
/lazy memory-graph "repo:org/api endpoint:https://api.example.com"
/lazy memory-graph "team:backend prefers:async-patterns"
```

**Complex Statements:**

```bash
# Multiple relations
/lazy memory-graph "service:payment owned_by:alice depends_on:stripe-api uses:async-pattern"

# With observations
/lazy memory-graph "service:payment owned_by:alice observation:'Handles all payment processing with Stripe API integration'"
```

---

### Query Memory

```bash
# Check what's stored
/lazy memory-check

# Output:
✅ MCP Memory Connected

Entities: 15
Relations: 23

Recent entries:
  - service:payment → person:alice (owned_by)
  - service:payment → service:stripe-api (depends_on)
  - team:backend → pattern:async (prefers)
```

**Search Memory:**

```bash
# Via MCP tools (automatic during prompts)
# Memory auto-queried when relevant keywords detected

# Manual query via skill
Use mcp-memory-router skill to search graph
```

---

### Update Memory

```bash
# Add new observation to existing entity
/lazy memory-graph "service:payment observation:'Now supports PayPal integration'"

# Add new relation
/lazy memory-graph "service:payment depends_on:paypal-api"
```

---

### Delete Memory

**Currently:** No direct delete command (MCP Memory limitation)

**Workaround:** Update observations to mark as deprecated

```bash
/lazy memory-graph "service:legacy observation:'DEPRECATED - No longer in use'"
```

---

## Memory-Driven Context Injection

### How Context Injection Works

#### Step 1: Keyword Detection

```python
# User: "Update payment service"
prompt_keywords = extract_keywords(prompt)
# → ["payment", "service", "update"]
```

#### Step 2: Graph Query

```python
# Query MCP Memory for related entities
results = mcp_memory_search(keywords=["payment", "service"])

# Results:
# - service:payment (direct match)
# - person:alice (related via owned_by)
# - service:stripe-api (related via depends_on)
# - pattern:async (related via uses)
```

#### Step 3: Context Building

```python
context = build_context(results)

# Context:
"""
[MEMORY CONTEXT]
Service: payment
- Owner: Alice (team:backend)
- Dependencies: stripe-api, database
- Patterns: async, repository-pattern
- Endpoint: https://api.payment.example.com
- Recent changes: Added PayPal integration (2024-10-15)
"""
```

#### Step 4: Prompt Enhancement

```python
enhanced_prompt = f"{original_prompt}\n\n{context}"

# Final Prompt:
"""
Update payment service

[MEMORY CONTEXT]
Service: payment
- Owner: Alice (team:backend)
- Dependencies: stripe-api, database
- Patterns: async, repository-pattern
...
"""
```

---

## Configuration

### MCP Memory Server Setup

**Configuration File:** `.claude/.mcp.json`

```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

**Install Node.js (Required):**

```bash
# Check installation
node --version  # Should be v18+

# Install if missing
# Windows: Download from nodejs.org
# macOS: brew install node
# Linux: sudo apt install nodejs npm
```

**Test MCP Server:**

```bash
# Manual test
npx -y @modelcontextprotocol/server-memory

# Should start without errors
```

---

### Environment Variables

```bash
# Optional: Disable auto-memory
export LAZYDEV_DISABLE_MEMORY_SKILL=1

# Optional: Adjust auto-store countdown
export LAZYDEV_MEMORY_COUNTDOWN=10  # seconds (default: 5)
```

---

### Skills Configuration

**Memory Router Skill:** `.claude/skills/mcp-memory-router.md`

Controls how memory is queried and injected.

**Key Settings:**
- `search_depth`: How many relation hops to traverse (default: 2)
- `max_results`: Maximum entities to return (default: 10)
- `relevance_threshold`: Minimum relevance score (default: 0.5)

---

## Best Practices

### 1. Be Specific with Entity Names

**Good:**
```bash
/lazy memory-graph "service:payment-api owned_by:alice"
/lazy memory-graph "repo:org/payment-service endpoint:https://api.payment.com"
```

**Bad:**
```bash
/lazy memory-graph "api owned_by:alice"  # Too vague
/lazy memory-graph "service endpoint:url"  # Not descriptive
```

---

### 2. Use Consistent Naming Conventions

**Good:**
```bash
service:payment-api     # kebab-case
service:billing-api
service:user-auth
```

**Bad:**
```bash
service:PaymentAPI      # Mixed case
service:billing_api     # Mixed conventions
service:UserAuth
```

---

### 3. Add Rich Observations

**Good:**
```bash
/lazy memory-graph "service:payment observation:'Handles payment processing with Stripe and PayPal. Supports subscriptions and one-time payments. Rate limited at 1000 req/min.'"
```

**Bad:**
```bash
/lazy memory-graph "service:payment observation:'payment stuff'"
```

---

### 4. Model Dependencies Explicitly

**Good:**
```bash
/lazy memory-graph "service:checkout depends_on:payment,inventory,shipping"
```

**Better:**
```bash
/lazy memory-graph "service:checkout depends_on:payment"
/lazy memory-graph "service:checkout depends_on:inventory"
/lazy memory-graph "service:checkout depends_on:shipping"
```

---

### 5. Update Memory as Project Evolves

```bash
# When ownership changes
/lazy memory-graph "service:payment owned_by:bob"  # Updates relation

# When architecture changes
/lazy memory-graph "service:payment uses:event-sourcing"  # Adds pattern

# When deprecating
/lazy memory-graph "service:legacy observation:'DEPRECATED - Replaced by service:payment-v2'"
```

---

## Troubleshooting

### Memory Not Auto-Storing

**Symptoms:** No auto-store suggestions appear

**Checks:**

```bash
# 1. Verify MCP server running
npx -y @modelcontextprotocol/server-memory

# 2. Check MCP configuration
cat .claude/.mcp.json

# 3. Verify hook exists and is executable
ls -la .claude/hooks/user_prompt_submit.py
chmod +x .claude/hooks/user_prompt_submit.py

# 4. Check if disabled
echo $LAZYDEV_DISABLE_MEMORY_SKILL
```

---

### Memory Not Injecting Context

**Symptoms:** Stored memories not appearing in prompts

**Checks:**

```bash
# 1. Verify memory stored
/lazy memory-check

# 2. Check search keywords
# Ensure prompt contains relevant keywords

# 3. Test manual query
# Use mcp-memory-router skill explicitly

# 4. Check search_depth setting
# May need to increase relation hops
```

---

### MCP Server Connection Failed

**Symptoms:** Error: "MCP Memory server not responding"

**Solutions:**

```bash
# 1. Check Node.js version
node --version  # Need v18+

# 2. Reinstall MCP memory server
npm install -g @modelcontextprotocol/server-memory

# 3. Test direct connection
npx -y @modelcontextprotocol/server-memory

# 4. Check firewall/antivirus
# May block local server connections

# 5. Try alternative port
# Edit .claude/.mcp.json if port conflicts
```

---

### Memory Growing Too Large

**Symptoms:** Slow queries, context overload

**Solutions:**

```bash
# 1. Audit stored entities
/lazy memory-check

# 2. Mark deprecated entities
/lazy memory-graph "service:old observation:'DEPRECATED'"

# 3. Reduce search_depth
# Edit .claude/skills/mcp-memory-router.md

# 4. Clear and rebuild (last resort)
# Backup, delete MCP data, rebuild
```

---

## Advanced Usage

### Multi-Project Memory

**Scenario:** Work on multiple projects with shared context

**Solution: Project Namespacing**

```bash
# Project A
/lazy memory-graph "project:acme service:payment owned_by:alice"

# Project B
/lazy memory-graph "project:widgets service:payment owned_by:bob"

# Query specific project
# Memory auto-filters by current project context
```

---

### Team Shared Memory

**Scenario:** Team needs shared knowledge graph

**Solution: Git-Tracked Memory**

```bash
# Export memory to JSON
/lazy memory-export > .claude/memory-snapshot.json

# Commit to git
git add .claude/memory-snapshot.json
git commit -m "docs: update team memory snapshot"

# Other team members import
/lazy memory-import .claude/memory-snapshot.json
```

---

### Memory-Driven Code Generation

**Scenario:** Use memory to guide implementation

**Example:**

```bash
# User: "Create new payment endpoint"

# Auto-injected context from memory:
# - service:payment uses:fastapi
# - service:payment requires:authentication
# - team:backend prefers:async-patterns
# - config:api-timeout value:30s

# Generated code automatically follows conventions:
@router.post("/payment", dependencies=[Depends(require_auth)])
async def create_payment(request: PaymentRequest, timeout: int = 30):
    """Create payment (async per team convention)."""
    # Implementation follows team patterns
```

---

## Summary

### Memory System Workflow

1. ✅ **Auto-Detection** → UserPromptSubmit hook detects durable facts
2. ✅ **Auto-Storage** → 5-second countdown, stores to MCP Memory
3. ✅ **Auto-Retrieval** → Relevant memories queried on keywords
4. ✅ **Auto-Injection** → Context injected into prompts
5. ✅ **No Re-Prompting** → Knowledge persists across sessions

### Key Benefits

- **Persistent Context** - Never lose important facts
- **Zero Overhead** - Automatic detection and storage
- **Smart Retrieval** - Only relevant context injected
- **Team Shared** - Knowledge shared via git
- **Growing Intelligence** - System gets smarter over time

---

**LAZY_DEV Memory** - Knowledge that persists, context that grows.
