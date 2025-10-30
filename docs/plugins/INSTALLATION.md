# LAZY_DEV Framework Installation Guide

## Quick Installation

### Method 1: Plugin Marketplace (Recommended)

```bash
# Add the marketplace
/plugin marketplace add MacroMan5/claude-code-workflow-plugins

# Install the plugin
/plugin install lazy-dev@MacroMan5

# Restart Claude Code CLI
exit
# Then restart your Claude Code session
```

### Method 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/MacroMan5/claude-code-workflow-plugins.git

# Copy to your project
cp -r claude-code-workflow-plugins/LAZY_DEV/.claude ~/.claude/
# Or for a specific project:
cp -r claude-code-workflow-plugins/LAZY_DEV/.claude /path/to/your/project/.claude/
```

---

## Configuration

### Required Environment Variables

```bash
# Set the enrichment model (required)
export ENRICHMENT_MODEL=claude-3-5-haiku
```

**Windows (PowerShell)**:
```powershell
$env:ENRICHMENT_MODEL = "claude-3-5-haiku"
```

### Optional Environment Variables

```bash
# Enforce strict TDD
export LAZYDEV_ENFORCE_TDD=1
export LAZYDEV_MIN_TESTS=3

# Disable features
export LAZYDEV_DISABLE_MEMORY_SKILL=1  # Disable auto-memory
export LAZYDEV_DISABLE_STYLE=1         # Disable output styling
```

---

## Prerequisites

### Required Tools

1. **Python 3.11+**
   ```bash
   python --version  # Should be 3.11 or higher
   ```

2. **uv Package Manager**
   ```bash
   pip install uv
   ```

3. **Git**
   ```bash
   git --version
   ```

4. **GitHub CLI** (for PR creation)
   ```bash
   # Install gh CLI
   # macOS:
   brew install gh

   # Windows:
   winget install --id GitHub.cli

   # Linux:
   # See https://github.com/cli/cli#installation

   # Authenticate
   gh auth login
   gh auth status
   ```

### Optional: MCP Memory Server

For persistent knowledge management across sessions:

1. **Node.js 18+**
   ```bash
   node --version  # Should be 18 or higher
   ```

2. **Install MCP Memory**
   ```bash
   # Copy MCP config to your project
   cp claude-code-workflow-plugins/LAZY_DEV/.claude/.mcp.json .mcp.json

   # Test the server
   npx -y @modelcontextprotocol/server-memory
   ```

### Python Dependencies

Install quality tools:

```bash
uv pip install black ruff mypy pytest pytest-cov
```

---

## Verification

### Check Installation

```bash
# In Claude Code CLI, verify commands are available
/help

# You should see:
# /lazy plan
# /lazy code
# /lazy review
# /lazy fix
# /lazy docs
# /lazy clean
# /lazy memory-graph
# /lazy memory-check
```

### Test MCP Memory (Optional)

```bash
# Check MCP connectivity
/lazy memory-check

# Should output: "✓ MCP Memory server is connected"
```

### Run First Command

```bash
# Create your first feature
/lazy plan "Add user authentication with OAuth2"

# This should:
# 1. Invoke the project-manager agent
# 2. Create USER-STORY.md
# 3. Create tasks with atomic breakdown
```

---

## Troubleshooting

### Common Issues

**1. ENRICHMENT_MODEL not set**

Error: `ENRICHMENT_MODEL environment variable not set`

Solution:
```bash
export ENRICHMENT_MODEL=claude-3-5-haiku
```

**2. Commands not showing in /help**

Solution:
- Restart Claude Code CLI
- Verify `.claude/commands/` directory exists
- Check file permissions (should be readable)

**3. MCP Memory not connecting**

Error: `MCP Memory server is not connected`

Solution:
```bash
# Check Node.js version
node --version  # Need 18+

# Test MCP server manually
npx -y @modelcontextprotocol/server-memory

# Verify .mcp.json exists in project root
cat .mcp.json
```

**4. GitHub CLI not authenticated**

Error: `gh: Not logged in`

Solution:
```bash
gh auth login
gh auth status
gh repo set-default
```

**5. Quality pipeline fails**

Error: `Format check failed` or `Lint errors found`

Solution:
```bash
# Auto-fix formatting
python scripts/format.py .

# Check linting
python scripts/lint.py .

# Type check
python scripts/type_check.py .
```

**6. Permission denied on hooks**

Error: `Permission denied: hooks/user_prompt_submit.py`

Solution:
```bash
# Make hooks executable
chmod +x .claude/hooks/*.py
```

---

## Next Steps

After installation:

1. **Read the documentation**:
   - [README.md](./README.md) - Framework overview
   - [WORKFLOW.md](./WORKFLOW.md) - Complete workflow guide
   - [MEMORY.md](./MEMORY.md) - Memory system documentation

2. **Try the quick start**:
   ```bash
   /lazy plan "Your first feature"
   /lazy code TASK-1.1
   /lazy review USER-STORY
   ```

3. **Customize for your project**:
   - Adjust environment variables
   - Configure quality scripts in `scripts/`
   - Customize agent prompts in `.claude/agents/`

4. **Join the community**:
   - Star the repo: https://github.com/MacroMan5/claude-code-workflow-plugins
   - Report issues: https://github.com/MacroMan5/claude-code-workflow-plugins/issues
   - Contribute: See [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## Uninstallation

### Plugin Method

```bash
/plugin uninstall lazy-dev@MacroMan5
```

### Manual Method

```bash
# Remove from global config
rm -rf ~/.claude/

# Or remove from project
rm -rf /path/to/project/.claude/
```

---

## Support

**Documentation**:
- [README.md](./README.md) - Main documentation
- [WORKFLOW.md](./WORKFLOW.md) - Workflow details
- [MEMORY.md](./MEMORY.md) - Memory system
- [SUB_AGENTS.md](./SUB_AGENTS.md) - Agent specifications
- [CLAUDE.md](./CLAUDE.md) - Framework guide

**Community**:
- GitHub Issues: https://github.com/MacroMan5/claude-code-workflow-plugins/issues
- Repository: https://github.com/MacroMan5/claude-code-workflow-plugins

**Credits**:
- See [CREDITS.md](./CREDITS.md) for attributions to inspiration projects

---

**LAZY_DEV Framework v2.0.0** - Production Ready
