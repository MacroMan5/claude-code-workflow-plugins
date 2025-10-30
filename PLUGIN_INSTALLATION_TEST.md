# Testing Your Claude Code Plugin Installation

## 🎉 Your Plugin is LIVE on GitHub Marketplace!

**Repository**: https://github.com/MacroMan5/claude-code-workflow-plugins

---

## Quick Test (Do This Now!)

### Step 1: Open Claude Code CLI

Make sure you have Claude Code installed. If not:
```bash
# Install Claude Code CLI
# Visit: https://docs.claude.com/claude-code
```

### Step 2: Install Your Plugin

In Claude Code CLI, run these commands:

```bash
# Add your marketplace
/plugin marketplace add MacroMan5/claude-code-workflow-plugins

# List available plugins in your marketplace
/plugin list MacroMan5

# Install LAZY_DEV plugin
/plugin install lazy-dev@MacroMan5
```

### Step 3: Verify Installation

```bash
# Check if commands are available
/help

# You should see:
# /lazy create-feature
# /lazy task-exec
# /lazy story-review
# /lazy story-fix-review
# /lazy documentation
# /lazy cleanup
# /lazy memory-graph
# /lazy memory-check
```

### Step 4: Test a Command

```bash
# Set required environment variable
export ENRICHMENT_MODEL=claude-3-5-haiku

# Test memory check (doesn't require MCP setup)
/lazy memory-check

# Create a test feature
/lazy create-feature "Add user authentication with OAuth2"
```

---

## What Just Happened?

When you ran `/plugin install lazy-dev@MacroMan5`, Claude Code:

1. ✅ Fetched `marketplace.json` from your GitHub repo
2. ✅ Found the `lazy-dev` plugin entry
3. ✅ Downloaded the entire `.claude/` directory
4. ✅ Installed:
   - 8 commands in `.claude/commands/`
   - 10 agents in `.claude/agents/`
   - 17 skills in `.claude/skills/`
   - 8 hooks in `.claude/hooks/`
5. ✅ Made commands available via `/lazy` prefix

---

## Full Installation Test Checklist

### Prerequisites ✅
- [ ] Claude Code CLI installed
- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] GitHub CLI installed (optional, for PR features)

### Installation ✅
- [ ] Marketplace added successfully
- [ ] Plugin listed in `/plugin list MacroMan5`
- [ ] Plugin installed without errors
- [ ] `/help` shows `/lazy` commands

### Commands Test ✅
```bash
# Test each command
- [ ] /lazy memory-check
- [ ] /lazy create-feature "Test feature"
- [ ] /lazy documentation README.md
- [ ] /lazy cleanup .
```

### Environment Setup ✅
```bash
# Required
export ENRICHMENT_MODEL=claude-3-5-haiku

# Optional
export LAZYDEV_ENFORCE_TDD=1
export LAZYDEV_MIN_TESTS=3
```

### Advanced Testing ✅

**Test with Real Workflow:**
```bash
# 1. Create feature
/lazy create-feature "Add payment processing"

# 2. Check generated files
ls -la
# Should see: USER-STORY.md, TASKS.md

# 3. Execute first task
/lazy task-exec TASK-1.1

# 4. Review (if tasks completed)
/lazy story-review USER-STORY.md
```

---

## Troubleshooting

### Issue: "Marketplace not found"
```bash
# Make sure GitHub repo is public
# Verify URL: https://github.com/MacroMan5/claude-code-workflow-plugins

# Check internet connection
ping github.com

# Retry with full URL
/plugin marketplace add https://github.com/MacroMan5/claude-code-workflow-plugins
```

### Issue: "Plugin not found"
```bash
# Check marketplace.json exists
curl https://raw.githubusercontent.com/MacroMan5/claude-code-workflow-plugins/main/LAZY_DEV/.claude-plugin/marketplace.json

# Should return JSON with "lazy-dev" plugin
```

### Issue: "Commands not showing"
```bash
# Restart Claude Code CLI
exit
# Then restart

# Check installation location
ls -la .claude/commands/

# Should see create-feature.md, task-exec.md, etc.
```

### Issue: "ENRICHMENT_MODEL not set"
```bash
# Set environment variable
export ENRICHMENT_MODEL=claude-3-5-haiku

# Windows (PowerShell)
$env:ENRICHMENT_MODEL = "claude-3-5-haiku"

# Verify
echo $ENRICHMENT_MODEL
```

---

## Sharing Your Plugin

Now that it works, share it with the world!

### 1. Tweet About It

```
🚀 Just published LAZY_DEV Framework v2.0.0 for @AnthropicAI Claude Code!

✨ 8 commands for full dev workflow
🤖 10 specialized agents
🔒 TDD-enforced quality
📝 MCP Memory integration

Install in 30 seconds:
/plugin marketplace add MacroMan5/claude-code-workflow-plugins
/plugin install lazy-dev@MacroMan5

https://github.com/MacroMan5/claude-code-workflow-plugins

#ClaudeCode #AI #DevTools #Automation
```

### 2. Post on Reddit

**r/ClaudeAI**
```
Title: [Plugin] LAZY_DEV Framework - Full workflow automation for Claude Code

Just released a comprehensive framework that automates the entire development workflow:

🎯 Features:
- 8 commands (create-feature, task-exec, story-review, etc.)
- 10 agents (PM, coder, reviewer, tester, etc.)
- TDD-enforced quality pipeline (format→lint→type→test)
- MCP Memory for persistent knowledge
- GitHub PR automation

📦 Installation (30 seconds):
/plugin marketplace add MacroMan5/claude-code-workflow-plugins
/plugin install lazy-dev@MacroMan5

🔗 GitHub: https://github.com/MacroMan5/claude-code-workflow-plugins

[Add screenshots here]

Happy to answer questions!
```

### 3. Create Demo GIF

Record these workflows:
1. Installation (30 seconds)
2. `/lazy create-feature` → Shows USER-STORY.md
3. `/lazy task-exec` → Shows quality pipeline
4. `/lazy story-review` → Creates PR

Tools:
- **LICEcap** (free, cross-platform)
- **ScreenToGif** (Windows)
- **Kap** (macOS)
- **Peek** (Linux)

### 4. Update README.md

Add a prominent installation section:

```markdown
## 🚀 Quick Install

### Via Claude Code Marketplace

```bash
# 1. Add marketplace
/plugin marketplace add MacroMan5/claude-code-workflow-plugins

# 2. Install plugin
/plugin install lazy-dev@MacroMan5

# 3. Set environment
export ENRICHMENT_MODEL=claude-3-5-haiku

# 4. Verify
/lazy memory-check
```

### What You Get

- ✨ 8 automated commands
- 🤖 10 specialized agents
- 🎯 17 reusable skills
- 🔒 TDD-enforced quality
- 📝 Persistent memory
- 🚀 GitHub PR automation

[See demo GIF]
```

---

## Plugin Update Process

When you make changes and want to release an update:

### 1. Update Version

```bash
# Edit .claude-plugin/plugin.json
{
  "version": "2.0.1",  # Increment version
  ...
}

# Edit .claude-plugin/marketplace.json
{
  "version": "2.0.1",  # Keep in sync
  ...
}
```

### 2. Update CHANGELOG.md

```markdown
## [2.0.1] - 2025-10-31

### Fixed
- Bug fix description

### Added
- New feature description
```

### 3. Commit, Tag, and Push

```bash
# Commit changes
git add .
git commit -m "release: v2.0.1 - Bug fixes and improvements"

# Tag release
git tag v2.0.1

# Push everything
git push origin main --tags
```

### 4. Users Update

Users get updates automatically or manually:

```bash
# Manual update
/plugin update lazy-dev@MacroMan5

# Or reinstall
/plugin uninstall lazy-dev@MacroMan5
/plugin install lazy-dev@MacroMan5
```

---

## Analytics & Feedback

### Track Usage

Watch these metrics:

1. **GitHub Stars** - Interest level
2. **GitHub Forks** - Customization/contributions
3. **Issues** - User engagement
4. **Pull Requests** - Community contributions
5. **Clones** (GitHub Insights) - Installation count

### Gather Feedback

Add to README.md:

```markdown
## 💬 Feedback

Love LAZY_DEV? Let us know!

- ⭐ Star this repo
- 🐛 [Report bugs](https://github.com/MacroMan5/claude-code-workflow-plugins/issues)
- 💡 [Request features](https://github.com/MacroMan5/claude-code-workflow-plugins/issues)
- 💬 [Ask questions](https://github.com/MacroMan5/claude-code-workflow-plugins/discussions)
```

---

## Success! 🎉

Your plugin is now:

✅ **Live on GitHub Marketplace**
- Anyone can install it
- No approval needed
- You control updates

✅ **Production Ready**
- CI/CD pipeline active
- Security scanning enabled
- Documentation complete

✅ **Community Ready**
- Contributing guidelines
- Code of conduct
- Issue/PR templates

**Installation Command:**
```bash
/plugin marketplace add MacroMan5/claude-code-workflow-plugins
/plugin install lazy-dev@MacroMan5
```

**Next Steps:**
1. Test it yourself (follow this guide)
2. Create demo GIF/video
3. Share on social media
4. Gather user feedback
5. Iterate and improve

---

## Support

- **Installation Issues**: See [INSTALLATION.md](docs/INSTALLATION.md)
- **Usage Questions**: See [WORKFLOW.md](docs/plugins/WORKFLOW.md)
- **Bug Reports**: [GitHub Issues](https://github.com/MacroMan5/claude-code-workflow-plugins/issues)
- **Security**: Email etheroux5@gmail.com

---

**Congratulations! Your Claude Code plugin is LIVE!** 🚀🎉
