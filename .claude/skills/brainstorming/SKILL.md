---
name: brainstorming
description: Structured ideation for options, trade-offs, and a clear decision
version: 0.1.0
tags: [planning, design, options]
triggers:
  - brainstorm
  - options
  - approaches
  - design choices
---

# Brainstorming

## Purpose
Quickly generate several viable approaches with pros/cons and pick a default. Keep output compact and decision-oriented.

## When to Use
- Early feature shaping (before `/lazy create-feature`)
- Choosing patterns, libraries, or refactor strategies

## Behavior
1. Produce 3–5 options with one-sentence descriptions.
2. Table: Option | Pros | Cons | Effort | Risk.
3. Recommend one option with a 2–3 line rationale.
4. List immediate next steps (3–5 bullets).

## Output Style
- Prefer `table-based` for the options matrix + short bullets.

## Guardrails
- No long essays; keep to 1 table + short bullets.
- Avoid speculative claims; cite known repo facts when used.

## Integration
- Feed the selected option into `/lazy create-feature` and the Project Manager agent as context for story creation.

## Example Prompt
> Brainstorm approaches for adding rate limiting to the API.

