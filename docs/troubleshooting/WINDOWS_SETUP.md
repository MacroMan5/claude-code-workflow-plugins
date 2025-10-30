# Windows Setup Guide for LAZY_DEV Framework

This guide covers Windows-specific setup and troubleshooting for the LAZY_DEV Framework.

## Prerequisites Verification

### 1. Python 3.11+
```powershell
python --version
# Should show: Python 3.11.x or higher
```

### 2. Node.js (for MCP Memory)
```powershell
node --version
# Should show: v18.x or higher
npx --version
# Should show npx version
```

### 3. Git Bash or WSL
The framework uses bash scripts for some operations. You need either:
- Git Bash (comes with Git for Windows)
- WSL (Windows Subsystem for Linux)

Test:
```bash
bash --version
```

## Installation Steps

### Step 1: Copy Framework Files
```powershell
# From the LAZY_DEV repository
Copy-Item -Recurse LAZY_DEV\.claude .claude
```

### Step 2: Fix Hook Paths (IMPORTANT for Windows)

The `.claude/settings.json` file needs to use relative paths instead of `$CLAUDE_PROJECT_DIR`.

**Correct format:**
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python .claude/hooks/user_prompt_submit.py"
          }
        ]
      }
    ]
  }
}
```

**Incorrect format (will fail on Windows):**
```json
{
  "command": "python $CLAUDE_PROJECT_DIR/.claude/hooks/user_prompt_submit.py"
}
```

### Step 3: Set Environment Variables

**PowerShell (current session):**
```powershell
$env:ENRICHMENT_MODEL = "claude-3-5-haiku"
$env:MEMORY_FILE_PATH = ".claude/memory/memory.jsonl"
```

**PowerShell (persistent):**
```powershell
[System.Environment]::SetEnvironmentVariable('ENRICHMENT_MODEL', 'claude-3-5-haiku', 'User')
[System.Environment]::SetEnvironmentVariable('MEMORY_FILE_PATH', '.claude/memory/memory.jsonl', 'User')
```

**Command Prompt:**
```cmd
set ENRICHMENT_MODEL=claude-3-5-haiku
set MEMORY_FILE_PATH=.claude/memory/memory.jsonl
```

### Step 4: Create Memory Directory
```powershell
New-Item -ItemType Directory -Force -Path .claude\memory
```

Or in bash:
```bash
mkdir -p .claude/memory
```

### Step 5: Verify Installation

Test all components:

**1. Test Hooks:**
```powershell
python .claude/hooks/user_prompt_submit.py
# Should show: JSON decode error (expected when run manually)

python .claude/hooks/post_tool_use_format.py
# Should show: JSON decode error (expected when run manually)
```

**2. Test Scripts:**
```powershell
python scripts/format.py --help
python scripts/lint.py --help
python scripts/type_check.py --help
python scripts/test_runner.py --help
```

**3. Test MCP Memory:**
```bash
cd .claude/memory
npx -y @modelcontextprotocol/server-memory
# Should show: "Knowledge Graph MCP Server running on stdio"
# Press Ctrl+C to stop
```

**4. List Skills:**
```bash
find .claude/skills -name "SKILL.md" | wc -l
# Should show: 17
```

**5. Test in Claude Code:**
```
/help
# Should list lazy commands
```

## Common Issues and Solutions

### Issue 1: Environment Variable Not Expanding

**Symptom:**
```
python: can't open file 'C:\path\$CLAUDE_PROJECT_DIR\.claude\hooks\...'
```

**Solution:**
Replace all `$CLAUDE_PROJECT_DIR` with relative paths in `.claude/settings.json`:
- Change: `python $CLAUDE_PROJECT_DIR/.claude/hooks/session_start.py`
- To: `python .claude/hooks/session_start.py`

### Issue 2: Python Not Found

**Symptom:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
1. Install Python 3.11+ from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Restart terminal
4. Verify: `python --version`

### Issue 3: Node.js/NPX Not Found

**Symptom:**
```
'node' is not recognized as an internal or external command
```

**Solution:**
1. Install Node.js v18+ from [nodejs.org](https://nodejs.org/)
2. Restart terminal
3. Verify: `node --version` and `npx --version`

### Issue 4: Bash Scripts Not Running

**Symptom:**
```
bash: command not found
```

**Solution:**
Install Git for Windows (includes Git Bash):
1. Download from [git-scm.com](https://git-scm.com/download/win)
2. During installation, select "Use Git and optional Unix tools from Command Prompt"
3. Restart terminal

### Issue 5: Memory Directory Missing

**Symptom:**
```
ls: cannot access '.claude/memory/': No such file or directory
```

**Solution:**
```powershell
New-Item -ItemType Directory -Force -Path .claude\memory
```

### Issue 6: Hooks Not Executing in Claude Code

**Symptom:**
Hooks don't seem to run when using Claude Code commands.

**Solution:**
1. Verify hooks are enabled: `/hooks list`
2. Check Claude Code logs for errors
3. Ensure Python is in PATH: `python --version`
4. Restart Claude Code CLI

## Path Handling Notes

### Forward Slashes vs Backslashes

- Python scripts: Use forward slashes `/` or `os.path.join()`
- PowerShell: Backslashes `\` work, but forward slashes `/` also work
- Bash scripts: Always use forward slashes `/`

### Relative Paths

All hook commands should use relative paths from the project root:
- ✅ `python .claude/hooks/session_start.py`
- ❌ `python $CLAUDE_PROJECT_DIR/.claude/hooks/session_start.py`
- ❌ `python C:\absolute\path\.claude\hooks\session_start.py`

### Git Bash Path Translation

Git Bash automatically translates Windows paths:
- Windows: `C:\Users\username\project`
- Git Bash: `/c/Users/username/project`

This is handled automatically, no action needed.

## Testing Checklist

After installation, verify:

- [ ] Python 3.11+ installed: `python --version`
- [ ] Node.js installed: `node --version`
- [ ] Git Bash or WSL available: `bash --version`
- [ ] Environment variables set: `echo $env:ENRICHMENT_MODEL`
- [ ] Memory directory created: `Test-Path .claude\memory`
- [ ] Hooks use relative paths in `.claude/settings.json`
- [ ] Hooks execute without Python errors: `python .claude/hooks/session_start.py`
- [ ] Scripts have help text: `python scripts/format.py --help`
- [ ] MCP Memory server runs: `npx -y @modelcontextprotocol/server-memory`
- [ ] 17 skills present: `find .claude/skills -name "SKILL.md" | wc -l`
- [ ] Commands listed in Claude Code: `/help`

## Performance Tips

### Use PowerShell 7+

PowerShell 7 (Core) is faster and more Unix-like than Windows PowerShell 5.1:

```powershell
# Install PowerShell 7
winget install Microsoft.PowerShell
```

### Use WSL2 for Better Performance

WSL2 provides better performance for bash operations:

```powershell
# Enable WSL2
wsl --install
```

Then run Claude Code from within WSL2.

## Additional Resources

- [LAZY_DEV Framework README](./README.md)
- [CLAUDE.md Guide](./CLAUDE.md)
- [Workflow Documentation](./docs/plugins/WORKFLOW.md)
- [Memory System](./docs/plugins/MEMORY.md)

## Tested Environment

This guide was verified on:
- **OS**: Windows 10/11
- **Python**: 3.13
- **Node.js**: v22.15.0
- **Git**: Git Bash 2.x
- **Terminal**: PowerShell, Git Bash

## Version

**Document Version**: 1.0.0
**Last Updated**: 2025-10-30
**Framework Version**: 2.2.0

---

**Need help?** Open an issue at [github.com/MacroMan5/claude-code-workflow-plugins](https://github.com/MacroMan5/claude-code-workflow-plugins/issues)
