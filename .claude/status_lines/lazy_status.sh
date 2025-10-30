#!/usr/bin/env bash
set -euo pipefail
# Prefer uv, fall back to python3/python
if command -v uv >/dev/null 2>&1; then
  uv run .claude/status_lines/lazy_status.py && exit 0 || true
fi
if command -v python3 >/dev/null 2>&1; then
  python3 .claude/status_lines/lazy_status.py && exit 0 || true
fi
if command -v python >/dev/null 2>&1; then
  python .claude/status_lines/lazy_status.py && exit 0 || true
fi
# Last resort: print minimal default JSON
printf '{"lazy":"ok","model":"default","mcp":{"configured":false,"has_memory":false,"npx":%s}}
' "$([ -x "$(command -v npx 2>/dev/null || true)" ] && echo true || echo false)"
