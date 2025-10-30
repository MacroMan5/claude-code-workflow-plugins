# Agent Documentation for create-feature Command

## Agents Used in This Command

This command leverages automatic agent delegation. The following agents may be invoked:

### 1. Project Manager Agent (`.claude/agents/project-manager.md`)
- **When**: Step 3 - After gathering project context and enriched brief
- **Purpose**: Transform feature brief into complete user story with individual task files
- **Invocation**: Automatic via agent descriptions - Claude delegates based on conversation context

**What it does:**
- Creates US-story.md with story ID, title, description, acceptance criteria
- Generates individual TASK-*.md files in TASKS/ subdirectory
- Maps technical requirements to specific tasks
- Identifies dependencies between tasks

**Invocation pattern:**
Simply provide enriched brief, project context, and role in conversation. Claude automatically routes to this agent.

### 2. Task Enhancer Agent (`.claude/agents/task-enhancer.md`)
- **When**: Step 4 - After project-manager creates initial tasks
- **Purpose**: Research codebase and add technical context to each task
- **Invocation**: Automatic via agent descriptions - Claude delegates based on conversation context

**What it does:**
- Researches codebase for relevant patterns and files
- Adds "Technical Context" sections to each TASK-*.md
- Identifies relevant files to reference
- Suggests specific files to create/modify
- Extracts code patterns from existing implementations
- Notes architecture integration points
- Adds testing strategy based on project patterns

**Invocation pattern:**
Simply provide task directory path and story context. Claude automatically routes to this agent.

---

## Key Principle: Automatic Delegation

**No manual agent selection is required.** Claude will automatically invoke the appropriate agents based on:
- Conversation context (what you're asking for)
- Agent descriptions (which agent specializes in what)
- Task requirements (what needs to be done)

You simply provide the necessary context in the conversation, and Claude intelligently routes to the right agent.
