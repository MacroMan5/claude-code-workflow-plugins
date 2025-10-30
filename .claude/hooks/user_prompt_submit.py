#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
User-prompt-submit hook for LAZY-DEV-FRAMEWORK.

Smart context injection - auto-adds git, task, and project context:
- Current git branch
- Recent commits (last 5)
- Current task from TASKS.md (if exists)
- Project structure context

Lightweight skill wiring (enabled by default):
- context-packer: adds a compact 10–20 line Context Pack (file map, langs, recent commits)
- output-style-selector: infers a best-fit output style and emits a tiny Style Block

Disable via env:
- LAZYDEV_DISABLE_STYLE=1 → skip style selection
- LAZYDEV_DISABLE_CONTEXT_PACK=1 → skip context pack

Reference: PROJECT-MANAGEMENT-LAZY_DEV/docs/HOOKS.md (UserPromptSubmit)
"""

import json
import logging
import subprocess
import sys
from pathlib import Path
import re
import os
import time
from datetime import datetime

logger = logging.getLogger(__name__)

# Module-level compiled regex patterns for performance (10-100x faster)
# Compiled once at import time, not on every function call

# Style override pattern
STYLE_OVERRIDE_PATTERN = re.compile(r"\[style:\s*([^\]]+)\]")

# Entity mention pattern (case-insensitive for search, preserve case for display)
ENTITY_MENTION_PATTERN = re.compile(r"\b(person|service|repo|dataset|api|team):[\w\-/\.]+", re.IGNORECASE)


def get_git_context() -> dict:
    """
    Get current git branch and recent commits.

    Returns:
        Dictionary with branch and commits list
    """
    context = {
        'branch': None,
        'commits': []
    }

    try:
        # Get current branch
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            context['branch'] = result.stdout.strip()

        # Get recent commits (last 5)
        result = subprocess.run(
            ['git', 'log', '--oneline', '-5'],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            context['commits'] = [c for c in commits if c]

    except subprocess.TimeoutExpired:
        logger.warning("Git operations timed out (2s)")
    except subprocess.SubprocessError as e:
        logger.warning(f"Git subprocess error: {type(e).__name__}")
    except FileNotFoundError:
        logger.debug("Git not found in PATH")

    return context


def get_current_task() -> str | None:
    """
    Get current task from TASKS.md if it exists.

    Returns:
        Task identifier (e.g., "TASK-1.1: Setup OAuth2") or None
    """
    tasks_path = Path('TASKS.md')

    if not tasks_path.exists():
        return None

    try:
        content = tasks_path.read_text(encoding='utf-8')

        # Look for tasks marked as "in progress" or "current"
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Match patterns like "- [ ] TASK-1.1:" or "### TASK-1.1:"
            if '[ ]' in line or 'TASK-' in line:
                # Check if marked as current/in-progress
                if any(marker in line.lower() for marker in ['current', 'in progress', 'active', '🔄']):
                    return line.strip()

                # First uncompleted task
                if '[ ]' in line and 'TASK-' in line:
                    return line.strip()

    except IOError as e:
        logger.warning(f"Failed to load TASKS.md: {type(e).__name__}")
    except Exception as e:
        logger.warning(f"Unexpected error loading TASKS.md: {type(e).__name__}")

    return None


def choose_output_style(prompt: str) -> tuple[str, float, str]:
    """
    Heuristic output-style selector. Returns (style_name, confidence, reason).

    Respects inline override markers like "[style: table-based]" or "[style: off]".
    """
    text = prompt.lower()

    # Inline overrides (use pre-compiled pattern)
    m = STYLE_OVERRIDE_PATTERN.search(text)
    if m:
        val = m.group(1).strip()
        if val in {"off", "none", "disable"}:
            return ("off", 1.0, "explicit override: off")
        return (val, 1.0, "explicit override")

    patterns: list[tuple[str, list[str], str]] = [
        ("table-based", ["compare", "comparison", "matrix", "pros and cons", "contrast"],
         "comparison/matrix keywords"),
        ("yaml-structured", ["yaml", "yml", "config", "manifest", "schema", "spec"],
         "yaml/config/schema keywords"),
        ("genui", ["html page", "open in browser", "ui preview", "full html"],
         "full HTML page intent"),
        ("html-structured", ["html", "tag", "<html", "<section", "semantic html"],
         "HTML fragment intent"),
        ("bullet-points", ["summary", "bullets", "quick scan", "checklist"],
         "summary/bullets intent"),
        ("ultra-concise", ["concise", "short", "tl;dr", "one-liner", "one line", "minimal"],
         "ultra concise intent"),
        ("markdown-focused", ["readme", "docs", "documentation", "markdown"],
         "markdown/doc intent"),
        ("tts-summary", ["tts", "audio", "voice"],
         "tts/audio intent"),
    ]

    for style, keys, reason in patterns:
        if any(k in text for k in keys):
            return (style, 0.85, reason)

    # Default
    return ("markdown-focused", 0.55, "fallback default")


def build_style_block(style_name: str) -> str:
    """Return a compact 1–2 line Style Block description."""
    templates = {
        "table-based": "Style: Table Based. Use a brief summary, then tables for comparisons and actions.",
        "yaml-structured": "Style: YAML Structured. Output valid YAML with clear keys and lists only.",
        "genui": "Style: GenUI. Produce a complete HTML page with embedded CSS; save/open as needed.",
        "html-structured": "Style: HTML Structured. Output semantic HTML fragments with article/section tags.",
        "bullet-points": "Style: Bullet Points. Use hierarchical bullets; keep each line concise.",
        "ultra-concise": "Style: Ultra Concise. Minimal words, commands first, one-line summaries.",
        "markdown-focused": "Style: Markdown Focused. Clear headings, code blocks, and task lists.",
        "tts-summary": "Style: TTS Summary. Add a brief end-of-response TTS announcement.",
    }
    return templates.get(style_name, f"Style: {style_name}.")


def build_context_pack(max_items: int = 8) -> str:
    """
    Create a compact 10–20 line context brief, optimized for speed.
    - Top-level dirs (exclude heavy/hidden)
    - File counts by extension (pruned walk with small caps + time budget)
    - Last 3 commit subjects

    Tunables via env:
      LAZYDEV_CONTEXT_PACK_MAX_FILES (default 300)
      LAZYDEV_CONTEXT_PACK_MAX_DIRS  (default 60)
      LAZYDEV_CONTEXT_PACK_MAX_DEPTH (default 3)
      LAZYDEV_CONTEXT_PACK_BUDGET_MS (default 200)
      LAZYDEV_CONTEXT_PACK_EXTS      (e.g., ".py,.js,.ts,.tsx,.md")
    """
    lines: list[str] = []

    EXCLUDE = {
        '.git', '.hg', '.svn', '.bzr',
        'node_modules', 'dist', 'build', 'out', 'coverage', 'target', 'vendor',
        '.next', '.nuxt', '.cache', '.ruff_cache', '.mypy_cache', '.pytest_cache', '.tox',
        '.idea', '.vscode', '.gradle', '.yarn', '.pnpm-store', '.parcel-cache',
        'tmp', 'temp', '__pycache__', '.venv', 'venv', '.claude', 'LAZY_DEV'
    }

    # Top-level directories (filtered)
    try:
        top = [
            p.name for p in Path('.').iterdir()
            if p.is_dir() and p.name not in EXCLUDE and not p.name.startswith('.')
        ]
        top.sort()
        if top:
            lines.append("Dirs: " + ", ".join(top[:max_items]))
    except Exception:
        pass

    # Language/extension counts with aggressive limits
    exts_env = os.getenv('LAZYDEV_CONTEXT_PACK_EXTS')
    if exts_env:
        exts = {e.strip().lower(): 0 for e in exts_env.split(',') if e.strip().startswith('.')}
        if not exts:
            exts = {".py": 0, ".js": 0, ".ts": 0, ".tsx": 0, ".md": 0}
    else:
        exts = {".py": 0, ".js": 0, ".ts": 0, ".tsx": 0, ".md": 0}

    max_files = int(os.getenv('LAZYDEV_CONTEXT_PACK_MAX_FILES', '300'))
    max_dirs  = int(os.getenv('LAZYDEV_CONTEXT_PACK_MAX_DIRS',  '60'))
    max_depth = int(os.getenv('LAZYDEV_CONTEXT_PACK_MAX_DEPTH', '3'))
    budget_ms = int(os.getenv('LAZYDEV_CONTEXT_PACK_BUDGET_MS','200'))
    deadline  = time.perf_counter() + (budget_ms / 1000.0)

    try:
        import os as _os
        counted_files = 0
        visited_dirs = 0
        timed_out = False

        for root, dirs, files in _os.walk('.', topdown=True):
            # Time budget
            if time.perf_counter() > deadline:
                timed_out = True
                break

            # Compute depth and prune
            rel = _os.path.relpath(root, '.')
            depth = 0 if rel == '.' else len(rel.split(_os.sep))
            if depth >= max_depth:
                dirs[:] = []
            # Exclude heavy/hidden dirs
            dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.startswith('.')]

            visited_dirs += 1
            if visited_dirs > max_dirs:
                break

            # Files in this dir
            for f in files:
                if f.startswith('.'):
                    continue
                sfx = _os.path.splitext(f)[1].lower()
                if sfx in exts:
                    exts[sfx] += 1
                counted_files += 1
                if counted_files >= max_files or time.perf_counter() > deadline:
                    timed_out = True
                    break
            if counted_files >= max_files or timed_out:
                break

        langs = [f"{k}:{v}" for k, v in exts.items() if v > 0]
        if langs:
            lines.append("Files: " + ", ".join(langs))
    except Exception:
        pass

    # Last 3 commit subjects (short timeout)
    try:
        result = subprocess.run(['git', 'log', '--oneline', '-3'], capture_output=True, text=True, timeout=1)
        if result.returncode == 0:
            commits = [c.strip() for c in result.stdout.strip().split('\n') if c.strip()]
            for c in commits:
                lines.append(f"Commit: {c}")
    except Exception:
        pass

    return "\n".join(lines[:20])


def detect_memory_intent(prompt: str) -> dict:
    """Detect whether we should auto-activate the Memory Graph skill.

    Heuristics favor precision over recall to avoid noisy triggers.
    Returns a dict with keys: enabled (bool), intents (set[str]), mentions (list[str]).
    """
    text = (prompt or "").lower()

    hard_triggers = [
        "save to memory",
        "add to memory",
        "memory graph",
        "knowledge graph",
        "persist this",
        "remember this",
        "create entity",
        "link entities",
        "create relation",
        "add observation",
        "delete entity",
        "delete relation",
        "delete observation",
        "search memory",
        "search nodes",
        "open nodes",
    ]

    intents = set()
    if any(p in text for p in hard_triggers):
        intents.add("explicit")

    # Soft hints for durable facts
    soft_markers = [
        "owner:", "maintainer:", "repo:", "endpoint:", "base url:", "email:",
        "service:", "person:", "dataset:", "api:", "team:", "depends on", "owned by",
    ]
    if any(p in text for p in soft_markers):
        intents.add("durable")

    # Entity-like tokens: type:name (use pre-compiled pattern)
    mentions = []
    m = ENTITY_MENTION_PATTERN.findall(text)
    if m:
        intents.add("entities")
        # keep original case snippets for better UX (search in original prompt)
        for match in ENTITY_MENTION_PATTERN.finditer(prompt):
            mentions.append(match.group(0))

    enabled = bool(intents)
    return {"enabled": enabled, "intents": intents, "mentions": mentions}


def build_memory_skill_block(intents: set[str], mentions: list[str]) -> str:
    """Return a compact Memory Graph activation block instructing MCP tool use."""
    mention_line = f"Mentions: {', '.join(mentions)}\n" if mentions else ""
    return (
        "\n\n## Memory Graph (Auto)\n\n"
        "If durable facts or entities are present, use the MCP Memory tools.\n\n"
        "Server: `memory` — prefix all tools as `mcp__memory__<tool>`.\n\n"
        f"{mention_line}"
        "Flow:\n"
        "1) `mcp__memory__search_nodes` to avoid duplicates\n"
        "2) `mcp__memory__create_entities` (when missing)\n"
        "3) `mcp__memory__add_observations` with small, dated facts\n"
        "4) `mcp__memory__create_relations` to link entities (active voice types: depends_on, owned_by, maintained_by)\n"
        "5) Verify with `mcp__memory__open_nodes`\n\n"
        "I/O shapes overview (see .claude/skills/memory-graph/operations.md for full):\n"
        "- create_entities: {entities:[{name, entityType, observations[]}]}\n"
        "- add_observations: {observations:[{entityName, contents[]}]}\n"
        "- create_relations: {relations:[{from,to,relationType}]}\n"
        "- delete_* variants accept names/relations/observations and are safe on missing items\n"
    )
def format_context_injection(git_context: dict, current_task: str | None) -> str:
    """
    Format context as markdown to inject into prompt.

    Args:
        git_context: Git branch and commits
        current_task: Current task identifier

    Returns:
        Formatted markdown string
    """
    parts = []

    # Git context
    if git_context['branch'] or git_context['commits']:
        parts.append('## Git Context')

        if git_context['branch']:
            parts.append(f"Branch: `{git_context['branch']}`")

        if git_context['commits']:
            parts.append('\nRecent commits:')
            for commit in git_context['commits']:
                parts.append(f"- {commit}")

    # Task context
    if current_task:
        parts.append('\n## Current Task')
        parts.append(current_task)

    if parts:
        return '\n\n---\n\n' + '\n'.join(parts) + '\n\n---'

    return ''


def log_prompt(session_id: str, input_data: dict) -> None:
    """
    Log user prompt to logs/user_prompt_submit.json.

    Args:
        session_id: Session identifier
        input_data: Full hook input data
    """
    log_dir = Path('logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'user_prompt_submit.json'

    # Read existing log data or initialize empty list
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            log_data = []
    else:
        log_data = []

    # Add timestamp
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        **input_data
    }

    # Append new data
    log_data.append(log_entry)

    # Write back to file
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)


def manage_session_data(session_id: str, prompt: str) -> None:
    """
    Store session data in .claude/data/sessions/{session_id}.json.

    Args:
        session_id: Session identifier
        prompt: User prompt
    """
    sessions_dir = Path('.claude/data/sessions')
    sessions_dir.mkdir(parents=True, exist_ok=True)

    session_file = sessions_dir / f'{session_id}.json'

    # Load or create session file
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            session_data = {'session_id': session_id, 'prompts': []}
    else:
        session_data = {'session_id': session_id, 'prompts': []}

    # Add timestamp to prompt
    prompt_entry = {
        'timestamp': datetime.now().isoformat(),
        'prompt': prompt
    }

    # Add the new prompt
    session_data['prompts'].append(prompt_entry)

    # Save the updated session data
    try:
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
    except IOError as e:
        logger.warning(f"Failed to write session file: {type(e).__name__}")
    except Exception as e:
        logger.warning(f"Unexpected error writing session file: {type(e).__name__}")


def main():
    """Hook entry point."""
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        # Extract session_id and prompt
        session_id = input_data.get('session_id', 'unknown')
        original_prompt = input_data.get('prompt', '')

        # Get context
        git_context = get_git_context()
        current_task = get_current_task()

        # Format base context injection (git + current task)
        context_injection = format_context_injection(git_context, current_task)

        # Lightweight output-style selection
        style_name = None
        style_conf = 0.0
        style_reason = ''
        if os.getenv('LAZYDEV_DISABLE_STYLE') not in {'1', 'true', 'TRUE'}:
            sel, conf, reason = choose_output_style(original_prompt)
            if sel != 'off':
                style_name, style_conf, style_reason = sel, conf, reason
                style_block = f"\n\n## Output Style (Auto)\n\n{build_style_block(sel)}\n"
            else:
                style_block = ''
        else:
            style_block = ''

        # Lightweight context pack
        context_pack_block = ''
        if os.getenv('LAZYDEV_DISABLE_CONTEXT_PACK') not in {'1', 'true', 'TRUE'}:
            pack = build_context_pack()
            if pack:
                context_pack_block = f"\n\n## Context Pack (Auto)\n\n{pack}\n"

        # Build additional context only (per Anthropic hooks reference):
        # For UserPromptSubmit, stdout JSON with hookSpecificOutput.additionalContext
        # is appended to the model context without replacing the original prompt.
        additional_parts = []
        if context_injection:
            additional_parts.append(context_injection)
        if style_block:
            additional_parts.append(style_block)
        if context_pack_block:
            additional_parts.append(context_pack_block)

        # Auto-activate Memory Graph skill when appropriate (opt-out with env)
        if os.getenv('LAZYDEV_DISABLE_MEMORY_SKILL') not in {'1','true','TRUE'}:
            mi = detect_memory_intent(original_prompt)
            if mi.get('enabled'):
                additional_parts.append(build_memory_skill_block(mi['intents'], mi['mentions']))

        additional_context = ''.join(additional_parts)

        # Log the prompt
        log_prompt(session_id, input_data)

        # Manage session data
        manage_session_data(session_id, original_prompt)

        # Output JSON per hooks reference to append context
        hook_output = {
            "decision": None,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": additional_context
            },
            # Optional diagnostic metadata for transcript/debugging
            "suppressOutput": False,
            "systemMessage": None
        }

        print(json.dumps(hook_output))

        sys.exit(0)

    except json.JSONDecodeError as e:
        # Handle JSON decode errors gracefully
        logger.warning(f"JSON decode error in user_prompt_submit: {type(e).__name__}")
        sys.exit(0)
    except IOError as e:
        # Handle file I/O errors gracefully
        logger.warning(f"I/O error in user_prompt_submit: {type(e).__name__}")
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully
        logger.warning(f"Unexpected error in user_prompt_submit: {type(e).__name__}")
        sys.exit(0)


if __name__ == '__main__':
    main()
