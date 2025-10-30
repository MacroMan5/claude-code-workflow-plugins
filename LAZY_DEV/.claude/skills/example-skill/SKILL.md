---
name: example-skill
description: Starter template for a Claude Agent Skill used in LAZY-DEV projects
version: 0.1.0
authors:
  - your-name-here
tags:
  - template
  - documentation
  - automation
---

# Example Skill (Starter)

## Purpose
Provide a minimal, well-structured Skill that Claude can load when tasks match this capability. Duplicate this folder, rename it, and edit the frontmatter and sections to fit your domain.

## When To Use
- The user asks for [your domain task]
- Files or prompts include keywords: [add keywords]
- The task benefits from consistent structure, steps, or formatting

## Non‑Goals
- Don’t override core agent behavior unrelated to this domain
- Don’t run destructive commands or write outside the project unless explicitly requested

## Behaviors (What This Skill Adds)
1. Style: Prefer concise, structured responses with clear steps
2. Files: Reference files with absolute or project‑relative paths using backticks
3. Quality: Include brief validation or a checklist when relevant

## Guardrails
- Confirm before making destructive changes
- Surface assumptions and ask for missing inputs
- Respect repository conventions (CLAUDE.md, settings, linters)

## Inputs (Examples)
- User prompt context and goals
- Optional flags or parameters the user provides
- Project files discovered during the task

## Outputs (Examples)
- A short plan and next actions
- Edited or created files, listed explicitly
- Summary of changes and verification steps

## Quick Usage Examples

Prompt examples that should activate this skill naturally:

> “Generate a structured checklist for migrating the API.”

> “Create a concise rollout plan with validation steps.”

## Implementation Notes
- If your skill needs helper scripts, add them under `scripts/` and reference exact commands
- Keep instructions decisive; avoid long narrative
- Prefer reusable patterns and small sections over large blocks of text

## Test Prompts (for validation)
1. “Give me a 5‑step plan with risks and mitigations.”
2. “List files to change and commands to run.”
3. “Summarize completion criteria in bullets.”

## Changelog
- 0.1.0 — Initial starter template

