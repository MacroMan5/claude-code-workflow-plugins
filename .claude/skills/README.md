# LAZY‑DEV Skills Index

Lightweight, Anthropic‑compatible Skills that Claude can load when relevant. Each skill is a folder with `SKILL.md` (frontmatter + concise instructions).

## Skills List

- `brainstorming/` — Structured ideation; options matrix + decision.
- `code-review-request/` — Focused review request; rubric + patch plan.
- `git-worktrees/` — Create/switch/remove Git worktrees safely.
- `subagent-driven-development/` — Delegate subtasks to coder/reviewer/research/PM.
- `test-driven-development/` — RED→GREEN→REFACTOR micro‑cycles; small diffs.
- `writing-skills/` — Generate new skills for claude codem using natural language prompts and anthropic documentation.
- `story-traceability/` — AC → Task → Test mapping for PR‑per‑story.
- `task-slicer/` — Split stories into 2–4h atomic tasks with tests.
- `gh-issue-sync/` — Draft GitHub issues/sub‑issues from local story/tasks.
- `ac-expander/` — Make AC measurable; add edge cases and test names.
- `output-style-selector/` — Auto‑pick best format (table, bullets, YAML, HTML, concise).
- `context-packer/` — Compact, high‑signal context instead of long pastes.
- `diff-scope-minimizer/` — Tiny patch plan, tight diffs, stop criteria.

## Suggested Pairings

- Project Manager → story-traceability, task-slicer, ac-expander, gh-issue-sync
- Coder → test-driven-development, diff-scope-minimizer, git-worktrees
- Reviewer / Story Reviewer → code-review-request
- Documentation →  output-style-selector
- Research → brainstorming, context-packer

## Overrides & Style

- Force/disable a style inline: `[style: table-based]`, `[style: off]`
- Manual skill hint in prompts: “Use skill ‘test-driven-development’ for this task.”

## Wiring (optional, not enabled yet)

- UserPromptSubmit: run `context-packer` + `output-style-selector`
- PreToolUse: nudge `test-driven-development` + `diff-scope-minimizer`
