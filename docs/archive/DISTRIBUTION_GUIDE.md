# LAZY_DEV Distribution Guide

**Decision**: How to distribute LAZY_DEV as an open-source project?

**Options Analysis**: Plugin vs GitHub Template vs Both

---

## 🎯 Recommendation: **BOTH** (Plugin + GitHub Template)

### Why Both?

Different users have different needs:
- **Plugin**: Best for adding LAZY_DEV to existing projects
- **GitHub Template**: Best for starting new projects with LAZY_DEV pre-configured

**Maximum Reach** = Plugin + Template + npm package (optional)

---

## Option 1: Claude Code Plugin (Primary Distribution)

### ✅ Advantages

1. **Easy Installation**
   ```bash
   /plugin marketplace add therouxe/lazy-dev-marketplace
   /plugin install lazy-dev@therouxe
   ```

2. **Version Management** - Users can upgrade easily with `/plugin update`

3. **Team Collaboration** - Repository-level config ensures consistency

4. **Discoverability** - Users can browse plugins with `/plugin menu`

5. **Professional Distribution** - Official Claude Code ecosystem

6. **Selective Installation** - Users can enable/disable features

### ⚠️ Considerations

1. **Learning Curve** - Users need to understand plugin system

2. **Marketplace Setup** - Requires creating marketplace infrastructure

3. **Version Coordination** - Need to maintain `plugin.json` versions

4. **Documentation Overhead** - Must document plugin-specific installation

### 📁 Required Structure for Plugin

```
lazy-dev-marketplace/           # Your GitHub repo
├── .claude-plugin/
│   └── marketplace.json        # Marketplace catalog
│
└── lazy-dev/                   # The plugin
    ├── .claude-plugin/
    │   └── plugin.json         # Plugin manifest
    ├── commands/
    │   ├── create-feature.md
    │   ├── task-exec.md
    │   ├── story-review.md
    │   ├── story-fix-review.md
    │   ├── documentation.md
    │   ├── cleanup.md
    │   ├── memory-graph.md
    │   └── memory-check.md
    ├── agents/
    │   ├── project-manager.md
    │   ├── task-enhancer.md
    │   ├── coder.md
    │   ├── reviewer.md
    │   ├── reviewer-story.md
    │   ├── tester.md
    │   ├── research.md
    │   ├── refactor.md
    │   ├── documentation.md
    │   └── cleanup.md
    ├── skills/
    │   ├── ac-expander/
    │   ├── brainstorming/
    │   ├── code-review-request/
    │   ├── context-packer/
    │   ├── diff-scope-minimizer/
    │   ├── dispatching-parallel-agents/
    │   ├── finishing-a-development-branch/
    │   ├── gh-issue-sync/
    │   ├── git-worktrees/
    │   ├── memory-graph/
    │   ├── output-style-selector/
    │   ├── story-traceability/
    │   ├── subagent-driven-development/
    │   ├── task-slicer/
    │   ├── test-driven-development/
    │   └── writing-skills/
    ├── hooks/
    │   └── hooks.json           # Hook definitions
    ├── README.md                # Plugin documentation
    ├── CHANGELOG.md             # Version history
    └── LICENSE                  # MIT License
```

### 📄 Required Files

**`.claude-plugin/marketplace.json`**:
```json
{
  "name": "LAZY_DEV Marketplace",
  "description": "Command-first AI framework for Claude Code with automated workflows, quality enforcement, and persistent knowledge management",
  "author": "therouxe",
  "version": "2.0.0",
  "plugins": [
    {
      "name": "lazy-dev",
      "description": "Complete LAZY_DEV framework with 8 commands, 10 agents, 17 skills",
      "source": "./lazy-dev"
    }
  ]
}
```

**`lazy-dev/.claude-plugin/plugin.json`**:
```json
{
  "name": "lazy-dev",
  "description": "Command-first AI framework for Claude Code with automated workflows, quality enforcement, and persistent knowledge management",
  "version": "2.0.0",
  "author": "therouxe",
  "homepage": "https://github.com/therouxe/lazy-dev-marketplace",
  "repository": {
    "type": "git",
    "url": "https://github.com/therouxe/lazy-dev-marketplace.git"
  },
  "license": "MIT",
  "keywords": [
    "workflow",
    "automation",
    "quality",
    "tdd",
    "github",
    "mcp-memory",
    "agents",
    "commands"
  ],
  "requirements": {
    "claudeCode": ">=1.0.0",
    "python": ">=3.11",
    "tools": ["gh", "git", "uv"]
  },
  "config": {
    "envVars": {
      "ENRICHMENT_MODEL": {
        "description": "Model for pre-prompt enrichment (required)",
        "default": "claude-3-5-haiku",
        "required": true
      },
      "LAZYDEV_ENFORCE_TDD": {
        "description": "Enforce TDD in task execution",
        "default": "0",
        "required": false
      },
      "LAZYDEV_MIN_TESTS": {
        "description": "Minimum test count per task",
        "default": "3",
        "required": false
      }
    }
  }
}
```

**`lazy-dev/hooks/hooks.json`**:
```json
{
  "hooks": [
    {
      "name": "user_prompt_submit",
      "type": "UserPromptSubmit",
      "command": "python",
      "args": ["hooks/user_prompt_submit.py"],
      "description": "Pre-prompt enrichment and memory detection"
    },
    {
      "name": "pre_tool_use",
      "type": "PreToolUse",
      "command": "python",
      "args": ["hooks/pre_tool_use.py"],
      "description": "Safety checks before tool execution"
    },
    {
      "name": "post_tool_use_format",
      "type": "PostToolUse",
      "command": "python",
      "args": ["hooks/post_tool_use_format.py"],
      "description": "Auto-formatting after file operations"
    },
    {
      "name": "memory_suggestions",
      "type": "PostToolUse",
      "command": "python",
      "args": ["hooks/memory_suggestions.py"],
      "description": "Suggest memory persistence"
    },
    {
      "name": "stop",
      "type": "Stop",
      "command": "python",
      "args": ["hooks/stop.py"],
      "description": "Quality gate logging and metrics"
    }
  ]
}
```

### 🚀 Installation for Users

```bash
# Add marketplace
/plugin marketplace add therouxe/lazy-dev-marketplace

# Install plugin
/plugin install lazy-dev@therouxe

# Restart Claude Code
# Commands now available: /lazy create-feature, /lazy task-exec, etc.

# Set environment variable
export ENRICHMENT_MODEL=claude-3-5-haiku

# Enable MCP Memory (optional)
# Copy .mcp.json to project root
```

---

## Option 2: GitHub Template Repository (Secondary Distribution)

### ✅ Advantages

1. **One-Click Setup** - Click "Use this template" button

2. **Pre-configured Projects** - Everything works out-of-the-box

3. **Example Structure** - Users see working project layout

4. **No Plugin Knowledge Required** - Familiar GitHub workflow

5. **Instant Gratification** - Clone and start coding immediately

6. **Perfect for Tutorials** - "Here's a working example"

### ⚠️ Considerations

1. **No Automatic Updates** - Users must manually pull updates

2. **Per-Project Setup** - Must set up for each new project

3. **Git History Pollution** - Template includes framework commits

4. **Harder to Customize** - Users modify template directly

### 📁 Required Structure for Template

```
lazy-dev-template/              # Your GitHub template repo
├── .claude/
│   ├── commands/               # All 8 commands
│   ├── agents/                 # All 10 agents
│   ├── skills/                 # All 17+ skills
│   ├── hooks/                  # All hook Python files
│   ├── .mcp.json              # MCP Memory config
│   └── settings.json          # Claude Code settings
├── .github/
│   └── workflows/
│       └── quality-check.yml  # Optional CI/CD
├── scripts/
│   ├── format.py
│   ├── lint.py
│   ├── type_check.py
│   └── test_runner.py
├── project-management/
│   └── US-STORY/              # Example story structure
│       └── US-1.1-example/
│           ├── US-story.md
│           └── TASKS/
│               └── TASK-1.1.md
├── .gitignore
├── .mcp.json                  # Copy of MCP config
├── CLAUDE.md                  # Framework guide
├── README.md                  # Template-specific README
├── WORKFLOW.md                # Workflow documentation
├── MEMORY.md                  # Memory system docs
├── pyproject.toml             # Python dependencies
└── LICENSE                    # MIT License
```

### 📄 Template-Specific README.md

```markdown
# Project Name

> Built with [LAZY_DEV Framework](https://github.com/therouxe/lazy-dev-marketplace) v2.0.0

## Quick Start

1. **Clone this repository** (it's a template)
   ```bash
   # Use "Use this template" button on GitHub
   # Or clone directly:
   git clone https://github.com/your-username/your-project.git
   cd your-project
   ```

2. **Set environment variables**
   ```bash
   export ENRICHMENT_MODEL=claude-3-5-haiku
   ```

3. **Install dependencies**
   ```bash
   uv venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   uv pip install black ruff mypy pytest pytest-cov
   ```

4. **Start building**
   ```bash
   /lazy create-feature "Your feature description"
   ```

## What's Included

- ✅ Complete LAZY_DEV framework (v2.0.0)
- ✅ 8 commands for workflow automation
- ✅ 10 specialized agents
- ✅ 17+ reusable skills
- ✅ Quality pipeline (format→lint→type→test)
- ✅ MCP Memory integration
- ✅ Example user story structure

## Documentation

- [CLAUDE.md](./CLAUDE.md) - Framework guide
- [WORKFLOW.md](./WORKFLOW.md) - Workflow details
- [MEMORY.md](./MEMORY.md) - Memory system

## Updating LAZY_DEV

This template includes LAZY_DEV v2.0.0. To get updates:

**Option 1**: Install as plugin (recommended)
```bash
/plugin marketplace add therouxe/lazy-dev-marketplace
/plugin install lazy-dev@therouxe
```

**Option 2**: Manual update
1. Download latest release from [lazy-dev-marketplace](https://github.com/therouxe/lazy-dev-marketplace)
2. Copy `.claude/` directory to your project

## License

MIT License - See [LICENSE](./LICENSE)
```

### 🚀 Installation for Users

```bash
# On GitHub: Click "Use this template" button
# Or clone:
git clone https://github.com/therouxe/lazy-dev-template.git my-new-project
cd my-new-project

# Set environment
export ENRICHMENT_MODEL=claude-3-5-haiku

# Install tools
uv pip install black ruff mypy pytest pytest-cov

# Start using
/lazy create-feature "Add authentication"
```

---

## Option 3: npm Package (Optional, Advanced)

### ✅ Advantages

1. **Professional Distribution** - npm is the standard for Node.js ecosystem

2. **Version Management** - `npm install -g @therouxe/lazy-dev`

3. **Dependency Management** - Specify Claude Code version requirements

4. **Automatic Updates** - `npm update -g @therouxe/lazy-dev`

### 📦 Package Structure

```json
{
  "name": "@therouxe/lazy-dev",
  "version": "2.0.0",
  "description": "Command-first AI framework for Claude Code",
  "main": "install.js",
  "bin": {
    "lazy-dev-install": "./bin/install.js"
  },
  "scripts": {
    "postinstall": "node install.js"
  },
  "files": [
    ".claude/",
    "scripts/",
    "install.js",
    "README.md",
    "LICENSE"
  ],
  "repository": {
    "type": "git",
    "url": "https://github.com/therouxe/lazy-dev-marketplace.git"
  },
  "keywords": [
    "claude-code",
    "ai",
    "automation",
    "workflow",
    "tdd"
  ],
  "author": "therouxe",
  "license": "MIT"
}
```

---

## 🏆 RECOMMENDED STRATEGY: Triple Distribution

### Phase 1: Foundation (Week 1)

1. **Create Plugin Marketplace** ⭐ PRIMARY
   - Repo: `github.com/therouxe/lazy-dev-marketplace`
   - Structure: Plugin format with proper manifests
   - Users: `/plugin marketplace add therouxe/lazy-dev-marketplace`

2. **Create GitHub Template** ⭐ SECONDARY
   - Repo: `github.com/therouxe/lazy-dev-template`
   - Mark as template on GitHub
   - Users: Click "Use this template" button

### Phase 2: Documentation (Week 2)

3. **Create Documentation Site**
   - Use GitHub Pages or docs.rs
   - Host: `lazy-dev.github.io` or similar
   - Content: Tutorials, examples, API reference

4. **Create Example Projects**
   - Repo: `github.com/therouxe/lazy-dev-examples`
   - Real-world use cases
   - Different tech stacks (Python, Node.js, etc.)

### Phase 3: Community (Week 3+)

5. **Optional: npm Package**
   - For users who prefer npm ecosystem
   - `npm install -g @therouxe/lazy-dev-cli`

6. **Create Community Resources**
   - Discord server or GitHub Discussions
   - Contributing guide
   - Issue templates

---

## 📋 Implementation Checklist

### For Plugin Distribution

- [ ] Create `lazy-dev-marketplace` repository
- [ ] Structure as plugin (`.claude-plugin/` directories)
- [ ] Create `marketplace.json` with plugin catalog
- [ ] Create `plugin.json` with metadata
- [ ] Convert hooks to `hooks.json` format
- [ ] Test plugin installation locally
- [ ] Add comprehensive README.md
- [ ] Create CHANGELOG.md
- [ ] Tag v2.0.0 release
- [ ] Publish to GitHub
- [ ] Test installation: `/plugin marketplace add therouxe/lazy-dev-marketplace`

### For Template Distribution

- [ ] Create `lazy-dev-template` repository
- [ ] Copy complete `.claude/` directory
- [ ] Add example project structure
- [ ] Create template-specific README.md
- [ ] Add `.github/workflows/` for CI/CD examples
- [ ] Mark repository as template on GitHub
- [ ] Add "Use this template" button
- [ ] Test template generation
- [ ] Tag v2.0.0 release

### For Both

- [ ] Create detailed documentation
- [ ] Add screenshots/GIFs to README
- [ ] Create quickstart video
- [ ] Write blog post announcement
- [ ] Share on social media (Twitter, Reddit, HackerNews)
- [ ] Submit to awesome-claude-code lists
- [ ] Create contributing guidelines
- [ ] Set up issue templates
- [ ] Create security policy
- [ ] Add code of conduct

---

## 🎯 Best Practices for Open Source Distribution

### 1. Clear Documentation

```
README.md structure:
├── Hero section (what it is, why it matters)
├── Features (bullet points with emojis)
├── Quick Start (3-minute setup)
├── Installation (multiple options)
├── Usage (examples with GIFs)
├── Documentation (links to detailed docs)
├── Contributing (how to help)
├── License (MIT recommended)
└── Support (Discord, issues, sponsorship)
```

### 2. Semantic Versioning

```
v2.0.0 - Initial plugin release
v2.0.1 - Bug fixes
v2.1.0 - New features (backward compatible)
v3.0.0 - Breaking changes
```

### 3. Changelog Maintenance

Keep `CHANGELOG.md` updated with each release:
```markdown
## [2.0.0] - 2025-10-29
### Added
- Plugin marketplace distribution
- GitHub template repository
- 8 commands for workflow automation
- 10 specialized agents
- 17+ reusable skills
- MCP Memory integration

### Changed
- Documentation structure (now comprehensive)
- Memory system (clarified as semi-automatic)

### Fixed
- Hook count clarification (4 types, 10 implementations)
```

### 4. Community Building

- **GitHub Discussions** - Q&A, feature requests
- **Discord Server** - Real-time support
- **Twitter/X** - Updates and showcases
- **Blog Posts** - Deep dives and tutorials
- **YouTube Videos** - Walkthroughs

### 5. License Choice

**MIT License** (recommended for maximum adoption):
- ✅ Permissive (commercial use allowed)
- ✅ Simple and well-understood
- ✅ Widely adopted in Claude Code ecosystem

---

## 🚀 Launch Strategy

### Week 1: Soft Launch
1. Publish plugin marketplace repository
2. Publish template repository
3. Test with small group of beta users
4. Gather feedback and fix issues

### Week 2: Public Announcement
1. Publish blog post on dev.to
2. Post on Reddit (r/ClaudeAI, r/opensource)
3. Tweet about launch with demo GIF
4. Submit to awesome-claude-code lists

### Week 3: Community Growth
1. Set up Discord server
2. Create first tutorial video
3. Write detailed documentation site
4. Engage with early adopters

### Ongoing: Maintenance
1. Respond to issues promptly
2. Review and merge pull requests
3. Release updates monthly
4. Share user success stories

---

## 📊 Success Metrics

### Plugin Metrics
- GitHub stars (target: 100+ in first month)
- Plugin installs (track via GitHub traffic)
- GitHub issues (engagement)
- Pull requests (community contributions)

### Template Metrics
- Template uses (GitHub insights)
- Forks and stars
- Community projects using template

### Community Metrics
- Discord members
- GitHub discussions activity
- Social media mentions
- Blog post views

---

## 🤔 Decision Matrix

| Factor | Plugin | Template | Both |
|--------|--------|----------|------|
| **Ease of Installation** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Ease of Updates** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **New Project Setup** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Existing Project** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Discoverability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Maintenance** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **User Reach** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Winner**: ✅ **BOTH** (Plugin as primary, Template as secondary)

---

## 🎁 Bonus: Marketing Copy

### For README.md Hero Section

```markdown
# 🚀 LAZY_DEV Framework

> Command-first AI framework for Claude Code with automated workflows, quality enforcement, and persistent knowledge management

**Be lazy, but consistently excellent** ✨

[![GitHub stars](https://img.shields.io/github/stars/therouxe/lazy-dev-marketplace?style=social)](https://github.com/therouxe/lazy-dev-marketplace)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/therouxe/lazy-dev-marketplace/releases)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Plugin-blueviolet.svg)](https://docs.claude.com/en/docs/claude-code)

**3-minute setup to first working feature** 🎯

