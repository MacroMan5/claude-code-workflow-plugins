---
description: Create user story with inline tasks from feature brief
argument-hint: "[feature-description] [--file FILE] [--output-dir DIR]"
allowed-tools: Read, Write, Task, Bash, Grep, Glob
model: claude-haiku-4-5-20251001
---

# Create Feature: Transform Brief to User Story

## Introduction

Transform a brief feature description into a single user story file with tasks included inline.

**Input Sources:**
1. **From STT Prompt Enhancer** (recommended): Enhanced, structured feature description from the STT_PROMPT_ENHANCER project
2. **Direct Input**: Brief text provided directly to command

**Output Structure:**
```
./project-management/US-STORY/US-{STORY_ID}-{story-name}/
└── US-story.md              # User story with inline tasks
```

**GitHub Integration:**
Optionally creates a GitHub issue for the story (can be disabled with --no-issue flag).

## Usage Examples

```bash
# From direct input
/lazy create-feature "Add user authentication with OAuth2"

# From STT enhanced file
/lazy create-feature --file enhanced_prompt.md

# With custom output directory
/lazy create-feature "Add analytics dashboard" --output-dir ./docs/project-management/US-STORY

# Skip GitHub issue creation
/lazy create-feature "Build payment processing" --no-issue
```

## Feature Description

<feature_description>
$ARGUMENTS
</feature_description>

## Instructions

### Step 1: Parse Arguments and Load Brief

**Parse Arguments:**
- Check for `--file` flag and read file if provided, otherwise use $ARGUMENTS
- Parse optional `--output-dir` flag (default: `./project-management/US-STORY/`)
- Parse optional `--no-issue` flag (skip GitHub issue creation)
- Verify the brief is not empty

**Error Handling:**
- If `--file` provided but file not found: Return error "File not found at: {path}"
- If no input provided: Return error "No feature brief provided"

### Step 2: Generate Story ID and Create Directory

- Scan `./project-management/US-STORY/` for existing US-* folders
- Generate next story ID (e.g., if US-3.2 exists, next is US-3.3; if none exist, start with US-1.1)
- Create directory: `./project-management/US-STORY/US-{ID}-{story-name}/`

### Step 3: Invoke Project Manager Agent

**Agent**: `project-manager` (at `.claude/agents/project-manager.md`)

The agent will:
1. Read feature brief from conversation
2. Create single US-story.md file with:
   - Story description and acceptance criteria
   - Tasks listed inline (TASK-1, TASK-2, etc.)
   - Security and testing requirements
3. Write file to output directory

### Step 4: Optionally Create GitHub Issue

If `--no-issue` flag NOT provided:
- Create GitHub issue with story content
- Update US-story.md with issue number

### Step 5: Git Add (if in repository)

- Add story file to git: `git add ./project-management/US-STORY/US-{ID}-{name}/`
- Do NOT commit (user commits when ready)

### Step 6: Output Summary

Display:
- Story location
- GitHub issue number (if created)
- Next steps: review story and start implementation
