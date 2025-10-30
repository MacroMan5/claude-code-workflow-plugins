#!/usr/bin/env python3
"""
Lightweight status line for the LAZY framework.

Printed once, single line JSON suitable for Claude Code status bars.
Shows:
- enrichment model (from ENRICHMENT_MODEL when set)
- MCP memory configuration presence (workspace .mcp.json or template)
- basic runtime availability hints (npx present)
"""

from __future__ import annotations
import json
import os
import shutil
from pathlib import Path
from datetime import datetime


def detect_mcp_config() -> dict:
    cwd = Path.cwd()
    workspace_cfg = cwd / ".mcp.json"
    template_cfg = Path("LAZY_DEV/.claude/.mcp.json")
    configured = workspace_cfg.exists() or template_cfg.exists()
    npx_ok = shutil.which("npx") is not None
    has_memory = False
    for p in (workspace_cfg, template_cfg):
        try:
            if p.exists():
                data = json.loads(p.read_text())
                servers = (data or {}).get("mcpServers", {})
                has_memory = has_memory or ("memory" in servers)
        except Exception:
            pass
    return {"configured": configured, "has_memory": has_memory, "npx": npx_ok}


def main() -> None:
    model = os.getenv("ENRICHMENT_MODEL")
    mcp = detect_mcp_config()
    payload = {
        "lazy": "ok",
        "model": model or "default",
        "mcp": mcp,
        "time": datetime.now().strftime("%H:%M"),
    }
    print(json.dumps(payload, separators=(",", ":")))


if __name__ == "__main__":
    main()
