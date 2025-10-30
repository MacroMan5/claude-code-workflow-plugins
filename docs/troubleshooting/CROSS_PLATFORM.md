# Cross-Platform Compatibility Guide

**LAZY_DEV Framework** is designed to work seamlessly across **Linux, macOS, and Windows**.

## Platform Support Matrix

| Component | Linux | macOS | Windows | Notes |
|-----------|-------|-------|---------|-------|
| **Python Hooks** | ✅ | ✅ | ✅ | Uses pathlib.Path (cross-platform) |
| **Quality Scripts** | ✅ | ✅ | ✅ | Python-based, platform-agnostic |
| **MCP Memory** | ✅ | ✅ | ✅ | Node.js-based |
| **Git Operations** | ✅ | ✅ | ✅ | Standard git commands |
| **Bash Scripts** | ✅ | ✅ | ⚠️ | Windows requires Git Bash/WSL |
| **Commands** | ✅ | ✅ | ✅ | Claude Code CLI |
| **Skills** | ✅ | ✅ | ✅ | Markdown-based |
| **Agents** | ✅ | ✅ | ✅ | Markdown-based |

## Key Design Principles

### 1. Path Handling ✅

**All paths use cross-platform methods:**

- **Python**: Uses `pathlib.Path` (not `os.path`)
  ```python
  from pathlib import Path
  project_root = Path.cwd()
  hook_path = project_root / ".claude" / "hooks" / "session_start.py"
  ```

- **Settings**: Uses relative paths (work on all platforms)
  ```json
  {
    "command": "python .claude/hooks/session_start.py"
  }
  ```

- **Forward slashes**: Work on all platforms in Python and most shells
  ```bash
  python .claude/hooks/session_start.py  # Works everywhere
  ```

### 2. No Platform-Specific Code ✅

**Verified**: No `sys.platform`, `os.name`, or platform checks in hooks or scripts.

All functionality works identically across platforms without conditional logic.

### 3. Standard Tools ✅

**Only standard cross-platform tools:**
- Python 3.11+ (available on all platforms)
- Node.js (available on all platforms)
- Git (available on all platforms)
- npm/npx (comes with Node.js)

### 4. Shell Script Fallbacks ⚠️

**Bash scripts** (used for status line) require:
- **Linux/macOS**: Native bash (already installed)
- **Windows**: Git Bash (comes with Git for Windows) or WSL

Alternative: The status line will fall back to minimal JSON if bash is unavailable.

## Installation by Platform

### Linux (Ubuntu/Debian)

```bash
# Install prerequisites
sudo apt update
sudo apt install python3.11 python3-pip git nodejs npm

# Install framework
cp -r LAZY_DEV/.claude/ .claude/

# Set environment variables
export ENRICHMENT_MODEL=claude-3-5-haiku
export MEMORY_FILE_PATH=.claude/memory/memory.jsonl

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export ENRICHMENT_MODEL=claude-3-5-haiku' >> ~/.bashrc
```

### macOS

```bash
# Install prerequisites (using Homebrew)
brew install python@3.11 git node

# Install framework
cp -r LAZY_DEV/.claude/ .claude/

# Set environment variables
export ENRICHMENT_MODEL=claude-3-5-haiku
export MEMORY_FILE_PATH=.claude/memory/memory.jsonl

# Add to ~/.zshrc or ~/.bash_profile for persistence
echo 'export ENRICHMENT_MODEL=claude-3-5-haiku' >> ~/.zshrc
```

### Windows

```powershell
# Install prerequisites
# - Python 3.11+ from python.org
# - Git for Windows from git-scm.com
# - Node.js from nodejs.org

# Install framework
Copy-Item -Recurse LAZY_DEV\.claude .claude

# Set environment variables (persistent)
[System.Environment]::SetEnvironmentVariable('ENRICHMENT_MODEL', 'claude-3-5-haiku', 'User')

# Or for current session only
$env:ENRICHMENT_MODEL = "claude-3-5-haiku"
```

**See [WINDOWS_SETUP.md](./WINDOWS_SETUP.md) for detailed Windows instructions.**

## Platform-Specific Considerations

### Path Separators

| Platform | Native | Python Handles | Settings.json |
|----------|--------|----------------|---------------|
| Linux    | `/`    | `/` and `\`    | Use `/` or `.` |
| macOS    | `/`    | `/` and `\`    | Use `/` or `.` |
| Windows  | `\`    | `/` and `\`    | Use `/` or `.` |

**Recommendation**: Always use forward slashes `/` or relative paths with `.`

### Environment Variables

| Platform | Set (Session) | Set (Persistent) |
|----------|---------------|------------------|
| **Linux/macOS** | `export VAR=value` | Add to `~/.bashrc` or `~/.zshrc` |
| **Windows (PowerShell)** | `$env:VAR = "value"` | `[System.Environment]::SetEnvironmentVariable()` |
| **Windows (CMD)** | `set VAR=value` | Use System Properties GUI |

### Line Endings

**Not an issue**: Python handles both `\n` (Unix) and `\r\n` (Windows) automatically.

Git should be configured to handle line endings:
```bash
# Set once per machine
git config --global core.autocrlf input  # Linux/macOS
git config --global core.autocrlf true   # Windows
```

### Shell Scripts

**Status line** (`.claude/status_lines/lazy_status.sh`) requires bash:

| Platform | Bash Availability |
|----------|-------------------|
| Linux | ✅ Built-in |
| macOS | ✅ Built-in |
| Windows | ⚠️ Requires Git Bash or WSL |

**Fallback**: If bash is unavailable, status line returns minimal JSON.

## Testing Cross-Platform

### Quick Test (All Platforms)

```bash
# 1. Test Python hooks
python .claude/hooks/session_start.py
# Expected: JSON decode error (normal when run manually)

# 2. Test scripts
python scripts/format.py --help
python scripts/lint.py --help

# 3. Test MCP Memory
npx -y @modelcontextprotocol/server-memory
# Expected: "Knowledge Graph MCP Server running on stdio"
# Press Ctrl+C to stop

# 4. Count skills
find .claude/skills -name "SKILL.md" | wc -l
# Expected: 17

# 5. Test in Claude Code
/help
# Should list lazy commands
```

### Platform-Specific Tests

**Linux/macOS**:
```bash
# Test bash status line
bash .claude/status_lines/lazy_status.sh
# Should output JSON with status
```

**Windows** (PowerShell):
```powershell
# Test paths work with backslashes
Test-Path .claude\hooks\session_start.py
# Should return: True

# Test environment variable
echo $env:ENRICHMENT_MODEL
# Should show: claude-3-5-haiku
```

## CI/CD Recommendations

### GitHub Actions Matrix

```yaml
name: Cross-Platform Tests

on: [push, pull_request]

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ['3.11', '3.12', '3.13']

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Test hooks execute
        run: python .claude/hooks/session_start.py || true

      - name: Test scripts have help
        run: |
          python scripts/format.py --help
          python scripts/lint.py --help

      - name: Test MCP Memory
        run: npx -y @modelcontextprotocol/server-memory &
        timeout-minutes: 1

      - name: Count skills
        shell: bash
        run: |
          count=$(find .claude/skills -name "SKILL.md" | wc -l)
          if [ $count -ne 17 ]; then exit 1; fi
```

## Common Cross-Platform Issues

### Issue 1: Bash Not Found (Windows)

**Symptom**: Status line doesn't work on Windows.

**Solution**: Install Git for Windows (includes Git Bash).

**Workaround**: Status line falls back to minimal JSON automatically.

### Issue 2: Path Separators

**Symptom**: Paths with backslashes don't work in settings.json.

**Solution**: Use forward slashes or relative paths with `.`
```json
✅ "command": "python .claude/hooks/session_start.py"
❌ "command": "python .claude\\hooks\\session_start.py"
```

### Issue 3: Python Not in PATH

**Symptom**: `python: command not found`

**Solution by Platform**:
- **Linux**: Use `python3` or create symlink
- **macOS**: Use `python3` or install via Homebrew
- **Windows**: Check "Add to PATH" during Python installation

### Issue 4: Different Python Command

Some platforms use `python3` instead of `python`.

**Fix**: Create alias or use `python3` explicitly in settings.json:
```json
{
  "command": "python3 .claude/hooks/session_start.py"
}
```

## Benefits of Cross-Platform Design

✅ **Consistent Experience**: Same commands, same behavior across platforms
✅ **Team Collaboration**: Team members can use different OSes
✅ **CI/CD**: Run tests on all platforms with GitHub Actions
✅ **Maintainability**: No platform-specific code branches
✅ **Portability**: Move projects between machines easily

## Verification Checklist

After installation, verify cross-platform compatibility:

- [ ] Python executes: `python --version` or `python3 --version`
- [ ] Node.js works: `node --version`
- [ ] Hooks execute: `python .claude/hooks/session_start.py`
- [ ] Scripts work: `python scripts/format.py --help`
- [ ] MCP starts: `npx -y @modelcontextprotocol/server-memory`
- [ ] All 17 skills present: `find .claude/skills -name "SKILL.md" | wc -l`
- [ ] Environment variable set: Check `ENRICHMENT_MODEL`
- [ ] Commands listed: `/help` in Claude Code

## Platform-Specific Guides

- **Windows**: See [WINDOWS_SETUP.md](./WINDOWS_SETUP.md)
- **Linux**: Standard installation works out of the box
- **macOS**: Standard installation works out of the box

## Contributing Cross-Platform Code

When contributing, ensure:

1. **Use pathlib.Path** for all path operations (not `os.path`)
2. **Test on multiple platforms** (use GitHub Actions)
3. **Avoid platform checks** (no `if sys.platform == "win32"`)
4. **Use forward slashes** in example paths
5. **Document platform-specific requirements** clearly

## Version

**Document Version**: 1.0.0
**Last Updated**: 2025-10-30
**Framework Version**: 2.2.0
**Tested Platforms**: Linux (Ubuntu 22.04), macOS (Sonoma 14.x), Windows (10/11)

---

**LAZY_DEV Framework** - Write once, run everywhere! 🌍
