# Installation Guide

## ✅ Fixed Installation

The plugin structure has been corrected and should now install properly!

---

## Quick Install (3 commands)

```bash
# 1. Add the marketplace
/plugin marketplace add MacroMan5/claude-code-workflow-plugins

# 2. Install the plugin
/plugin install lazy-dev@lazy-dev-marketplace

# 3. Verify installation
/help
```

You should now see `/lazy` commands available!

---

## Setup Environment

```bash
# Required: Set the enrichment model
export ENRICHMENT_MODEL=claude-3-5-haiku

# Windows PowerShell:
$env:ENRICHMENT_MODEL = "claude-3-5-haiku"
```

---

## Test It Works

```bash
# Test a simple command
/lazy memory-check

# Create your first feature
/lazy create-feature "Add user authentication"
```

---

## What Gets Installed

When you run the install command, Claude Code copies:

- ✅ 8 commands → `.claude/commands/`
- ✅ 10 agents → `.claude/agents/`
- ✅ 17 skills → `.claude/skills/`
- ✅ 8 hooks → `.claude/hooks/`

---

## Troubleshooting

### "Marketplace not found"
Wait 1-2 minutes for GitHub to update, then retry.

### "Plugin not found"
Make sure to use the correct marketplace name:
```bash
/plugin install lazy-dev@lazy-dev-marketplace
```

### Commands not showing after restart
Check that `.claude/commands/` exists in your project and contains the command files.

---

## Full Documentation

- **README.md** - Overview and features
- **docs/INSTALLATION.md** - Detailed setup guide
- **docs/plugins/WORKFLOW.md** - Complete workflow documentation
- **MARKETPLACE_PUBLISHING.md** - Publishing guide

---

## Support

- **Issues**: https://github.com/MacroMan5/claude-code-workflow-plugins/issues
- **Discussions**: https://github.com/MacroMan5/claude-code-workflow-plugins/discussions
- **Email**: etheroux5@gmail.com

---

**Repository**: https://github.com/MacroMan5/claude-code-workflow-plugins
