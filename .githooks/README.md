# Git Hooks for LAZY-DEV Framework

This directory contains custom git hooks for the LAZY-DEV framework.

## Setup

After cloning the repository, run:

```bash
git config core.hooksPath .githooks
```

This tells git to use hooks from this directory instead of `.git/hooks/`.

## Available Hooks

### pre-commit

**Purpose**: Automatically format all staged files before commit.

**What it does**:
- Formats Python files with Black + Ruff
- Formats JS/TS/JSON/YAML/Markdown with Prettier
- Re-stages formatted files automatically
- Prevents unformatted code from being committed

**Languages supported**:
- Python (.py) → Black + Ruff
- JavaScript/TypeScript (.js, .jsx, .ts, .tsx) → Prettier
- JSON (.json) → Prettier
- YAML (.yml, .yaml) → Prettier
- Markdown (.md) → Prettier

**Requirements**:
- Python 3.11+
- Black (`pip install black`)
- Ruff (`pip install ruff`)
- Node.js (for Prettier via npx)

**Behavior**:
1. Gets list of staged files
2. Formats each file type with appropriate formatter
3. Re-adds formatted files to staging area
4. Commit proceeds with formatted code

**Skip the hook** (if needed):
```bash
git commit --no-verify -m "message"
```

**Manual test**:
```bash
# Stage a file
git add some_file.py

# Run hook manually
.githooks/pre-commit

# Check if file was formatted
git diff --cached some_file.py
```

## Why Version-Controlled Hooks?

**Benefits**:
- ✅ Shared across entire team
- ✅ Version controlled (changes tracked)
- ✅ No manual setup per developer (just `git config`)
- ✅ Consistent formatting enforcement

**Traditional `.git/hooks/`**:
- ❌ Not version controlled
- ❌ Each developer must install manually
- ❌ Easy to forget or skip

## Adding New Hooks

1. Create hook script in `.githooks/`
2. Make it executable: `chmod +x .githooks/<hook-name>`
3. Document in this README
4. Commit to repository

## Troubleshooting

**Hook not running?**
```bash
# Verify hooks path is configured
git config core.hooksPath
# Should output: .githooks

# If not set:
git config core.hooksPath .githooks
```

**Hook failing?**
```bash
# Check hook is executable
ls -la .githooks/pre-commit

# Make executable if needed
chmod +x .githooks/pre-commit

# Test hook manually
.githooks/pre-commit
```

**Formatters not found?**
```bash
# Install Python formatters
pip install black ruff

# Prettier is installed via npx (auto-downloads)
npx -y prettier --version
```

## Integration with CI

The pre-commit hook provides **local enforcement**. CI provides **final enforcement**:

- **Local** (pre-commit): Fast feedback, prevents most issues
- **CI** (GitHub Actions): Safety net, catches anything that bypassed local checks

Both use the same formatters, ensuring consistency.
