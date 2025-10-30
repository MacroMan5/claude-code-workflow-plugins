---
description: Remove dead code safely from codebase
argument-hint: [scope]
allowed-tools: Read, Write, Edit, Bash, Task, Glob, Grep
model: claude-haiku-4-5-20251001
---

# `/lazy cleanup` - Safe Dead Code Removal

You are the **Cleanup Command Handler** for LAZY-DEV-FRAMEWORK. Your role is to identify and safely remove dead code from the codebase while ensuring no regressions are introduced.

## Command Overview

**Purpose**: Remove dead code safely from codebase with comprehensive analysis and safety measures

**Scope Options**:
- `codebase` - Analyze entire project
- `current-branch` - Only files changed in current git branch
- `path/to/directory` - Specific directory or file path

**Safety Modes**:
- `--safe-mode true` (default) - Create git stash backup before changes
- `--safe-mode false` - Skip backup (not recommended)
- `--dry-run` - Preview changes without applying them

## Usage Examples

```bash
# Analyze and clean entire codebase (with safety backup)
/lazy cleanup codebase

# Clean specific directory
/lazy cleanup src/services

# Preview cleanup without applying changes
/lazy cleanup codebase --dry-run

# Clean current branch only
/lazy cleanup current-branch

# Clean without backup (use with caution)
/lazy cleanup src/legacy --safe-mode false
```

---

## Workflow

### Step 1: Parse Arguments and Validate Scope

**Extract parameters**:
```python
# Parse scope argument
scope = $1  # Required: codebase | current-branch | path/to/directory
safe_mode = $2 or "true"  # Optional: true | false
dry_run = $3  # Optional: --dry-run flag

# Validate scope
if scope == "codebase":
    target_paths = ["."]  # Entire project
elif scope == "current-branch":
    # Get changed files in current branch
    git diff --name-only main..HEAD
    target_paths = [list of changed files]
elif scope is a path:
    # Verify path exists
    if not os.path.exists(scope):
        ERROR: "Path not found: {scope}"
    target_paths = [scope]
```

**Display scan scope**:
```
🧹 Cleanup Analysis Starting...

Scope: {scope}
Target Paths: {target_paths}
Safe Mode: {safe_mode}
Dry Run: {dry_run}

Scanning for dead code...
```

---

### Step 2: Scan for Dead Code Patterns

**Use Glob and Grep tools to identify**:

#### A. Unused Imports
```bash
# Find imports that are never used
# Pattern: import statements not referenced in code
```

#### B. Unused Functions/Methods
```bash
# Find functions/methods defined but never called
# Pattern: def/async def with no references
```

#### C. Unused Variables
```bash
# Find variables assigned but never read
# Pattern: variable = value, but no subsequent usage
```

#### D. Unreachable Code
```bash
# Find code after return/break/continue statements
# Pattern: statements after control flow terminators
```

#### E. Commented-Out Code Blocks
```bash
# Find large blocks of commented code (>3 lines)
# Pattern: consecutive lines starting with #
```

#### F. Orphaned Files
```bash
# Find files with no imports from other modules
# Pattern: files not in any import statement across codebase
```

#### G. Deprecated Code
```bash
# Find code marked with @deprecated decorator or TODO: remove
# Pattern: @deprecated, # TODO: remove, # DEPRECATED
```

---

### Step 3: Invoke Cleanup Agent for Analysis

**Call Cleanup Agent with findings**:

```markdown
@agent-cleanup

You are the **Cleanup Agent** for LAZY-DEV-FRAMEWORK. Analyze code to identify dead code that can be safely removed.

## Scan Results

### Target Paths
$paths

### Dead Code Patterns to Identify
- Unused imports
- Unused functions/methods
- Unused variables
- Unreachable code
- Commented-out code blocks (>3 lines)
- Orphaned files (no references)
- Deprecated code (marked for removal)

### Analysis Mode
Safe Mode: $safe_mode
Dry Run: $dry_run

## Your Task

**Phase 1: Comprehensive Analysis**

For each target path, analyze and identify:

1. **Unused Imports**
   - List import statements not referenced in code
   - Provide: file, line number, import name

2. **Unused Functions/Methods**
   - Find functions/methods with zero call sites
   - Exclude: __init__, __main__, test fixtures, public API methods
   - Provide: file, line number, function name, reason safe to remove

3. **Unused Variables**
   - Find variables assigned but never read
   - Exclude: loop variables, configuration variables
   - Provide: file, line number, variable name

4. **Unreachable Code**
   - Find code after return/break/continue/raise
   - Provide: file, line number range, code snippet

5. **Commented-Out Code**
   - Find consecutive commented lines (>3 lines) containing code
   - Exclude: legitimate comments, docstrings
   - Provide: file, line number range, size (lines)

6. **Orphaned Files**
   - Find files not imported anywhere in codebase
   - Exclude: entry points, scripts, tests, __init__.py
   - Provide: file path, size (lines), last modified date

7. **Deprecated Code**
   - Find code marked @deprecated or TODO: remove
   - Provide: file, line number, deprecation reason

**Phase 2: Safety Assessment**

For each identified item, assess:
- **Risk Level**: LOW | MEDIUM | HIGH
- **Safe to Remove?**: YES | NO | MAYBE (requires review)
- **Reason**: Why it's safe (or not safe) to remove
- **Dependencies**: Any code that depends on this

**Phase 3: Removal Recommendations**

Categorize findings:

✅ **Safe to Remove (Low Risk)**
- Items with zero dependencies
- Clearly unused code with no side effects

⚠️ **Review Recommended (Medium Risk)**
- Items with unclear usage patterns
- Code that might be used via reflection/dynamic imports

❌ **Do Not Remove (High Risk)**
- Public API methods (even if unused internally)
- Code with external dependencies
- Configuration code
- Test fixtures

## Output Format

```yaml
dead_code_analysis:
  summary:
    total_items: N
    safe_to_remove: N
    review_recommended: N
    do_not_remove: N

  safe_removals:
    unused_imports:
      - file: "path/to/file.py"
        line: 5
        import: "from module import unused_function"
        reason: "No references to unused_function in file"

    unused_functions:
      - file: "path/to/file.py"
        line_start: 42
        line_end: 58
        function: "old_helper()"
        reason: "Zero call sites across entire codebase"

    commented_code:
      - file: "path/to/file.py"
        line_start: 100
        line_end: 125
        size_lines: 25
        reason: "Block comment contains old implementation"

    orphaned_files:
      - file: "src/old_utils.py"
        size_lines: 200
        reason: "No imports found across codebase"

  review_recommended:
    - file: "path/to/file.py"
      line: 78
      code: "def potentially_used()"
      reason: "Might be used via dynamic import or reflection"

  total_lines_to_remove: N
```
```

**Agent will return structured analysis for next step.**

---

### Step 4: Present Findings for User Approval

**Display findings summary**:

```
🧹 Cleanup Analysis Complete

Dead Code Found:

✅ SAFE TO REMOVE:
  ✓ {N} unused imports in {X} files
  ✓ {N} unused functions ({X} lines)
  ✓ {N} unused variables
  ✓ {N} unreachable code blocks ({X} lines)
  ✓ {N} lines of commented code
  ✓ {N} orphaned files ({file1.py, file2.py})

⚠️  REVIEW RECOMMENDED:
  ! {N} items need manual review:
    - {item1}: {reason}
    - {item2}: {reason}

📊 Impact:
  Total lines to remove: {N}
  Files affected: {X}
  Estimated time saved: {Y} minutes in future maintenance

🔒 Safety:
  Safe mode: {enabled/disabled}
  Dry run: {yes/no}
  Backup: {will be created/skipped}
```

**Ask user for approval**:

```
Apply cleanup?

Options:
  [y] Yes - Apply all safe removals
  [n] No - Cancel cleanup
  [p] Preview - Show detailed preview of each change
  [s] Selective - Review each item individually

Your choice:
```

---

### Step 5: Apply Cleanup (If Approved)

#### If user selects "Preview" (p):
```
📝 Detailed Preview:

1. UNUSED IMPORT: path/to/file.py:5
   Remove: from module import unused_function
   Reason: No references in file

2. UNUSED FUNCTION: path/to/file.py:42-58
   Remove: def old_helper(): ...
   Reason: Zero call sites
   Code preview:
   ```python
   def old_helper():
       # 16 lines
       ...
   ```

3. ORPHANED FILE: src/old_utils.py
   Remove: entire file (200 lines)
   Reason: No imports found
   Last modified: 2024-08-15

[Continue preview...]

Apply these changes? (y/n):
```

#### If user selects "Selective" (s):
```
Review each item:

1/15: UNUSED IMPORT: path/to/file.py:5
      Remove: from module import unused_function
      Apply? (y/n/q):
```

#### If user approves (y):

**Create safety backup** (if safe_mode=true):
```bash
# Create git stash with timestamp
git stash push -m "cleanup-backup-$(date +%Y%m%d-%H%M%S)" --include-untracked

# Output:
💾 Safety backup created: stash@{0}
   To restore: git stash apply stash@{0}
```

**Apply removals using Edit tool**:
```python
# For each safe removal:
# 1. Use Edit tool to remove unused imports
# 2. Use Edit tool to remove unused functions
# 3. Use Edit tool to remove commented blocks
# 4. Use Bash tool to remove orphaned files

# Track changes
changes_applied = []
```

**Display progress**:
```
🧹 Applying cleanup...

✅ Removed unused imports (5 files)
✅ Removed unused functions (3 files)
✅ Removed commented code (8 files)
✅ Removed orphaned files (2 files)

Total: 250 lines removed from 12 files
```

---

### Step 6: Run Quality Pipeline

**CRITICAL: Must pass quality gates before commit**

```bash
# Run quality checks
1. Format: python scripts/format.py {changed_files}
2. Lint: python scripts/lint.py {changed_files}
3. Type: python scripts/type_check.py {changed_files}
4. Test: python scripts/test_runner.py

# If ANY check fails:
  - Restore from backup: git stash apply
  - Report error to user
  - Return: "Cleanup failed quality checks, changes reverted"
```

**Display quality results**:
```
📊 Quality Pipeline: RUNNING...

✅ Format (Black/Ruff): PASS
✅ Lint (Ruff): PASS
✅ Type Check (Mypy): PASS
✅ Tests (Pytest): PASS
   - 124/124 tests passing
   - Coverage: 87% (unchanged)

All quality checks passed! ✅
```

---

### Step 7: Commit Changes

**Create commit** (if quality passes):

```bash
git add {changed_files}

git commit -m "$(cat <<'EOF'
chore(cleanup): remove dead code

Cleanup scope: {scope}
Files affected: {N}
Lines removed: {M}

Items removed:
- {N} unused imports
- {N} unused functions
- {N} commented code blocks
- {N} orphaned files

Quality pipeline: PASSED
All tests passing: ✅

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

---

### Step 8: Return Summary

**Final output**:

```
✅ Cleanup Complete

📊 Summary:
  Scope: {scope}
  Files modified: {N}
  Files deleted: {N}
  Lines removed: {M}

  Items removed:
  ✓ {N} unused imports
  ✓ {N} unused functions
  ✓ {N} unused variables
  ✓ {N} unreachable code blocks
  ✓ {N} lines of commented code
  ✓ {N} orphaned files

📊 Quality Pipeline: PASS
  ✅ Format (Black/Ruff)
  ✅ Lint (Ruff)
  ✅ Type Check (Mypy)
  ✅ Tests (Pytest)

💾 Committed: {commit_sha}
  Message: "chore(cleanup): remove dead code"

💾 Safety Backup: {stash_id}
  To restore if needed: git stash apply {stash_id}

🎯 Impact:
  Code reduction: {M} lines
  Maintainability: Improved
  Future time saved: ~{X} minutes
```

---

## Error Handling

### Git Issues

| Error | Cause | Recovery |
|-------|-------|----------|
| **Not a git repository** | No .git directory | Initialize: `git init`, retry |
| **Dirty working tree** | Uncommitted changes | Commit or stash changes first |
| **Stash creation failed** | No changes to stash | Disable safe mode, retry |

### Cleanup Issues

| Error | Cause | Recovery |
|-------|-------|----------|
| **No dead code found** | Clean codebase | Return: "No dead code detected" |
| **Agent timeout** | Large codebase | Reduce scope, retry with specific path |
| **Path not found** | Invalid scope argument | Verify path exists, retry |

### Quality Pipeline Failures

| Error | Cause | Recovery |
|-------|-------|----------|
| **Format failed** | Syntax errors introduced | Restore from stash: `git stash apply`, report issue |
| **Lint failed** | Code quality regressions | Restore from stash, report issue |
| **Type check failed** | Type errors introduced | Restore from stash, report issue |
| **Tests failed** | Removed code was not actually dead | Restore from stash, mark as unsafe removal |

**Failure recovery pattern**:
```bash
# If quality pipeline fails:
echo "❌ Cleanup failed at: {stage}"
echo "🔄 Restoring from backup..."
git stash apply {stash_id}
echo "✅ Changes reverted"
echo ""
echo "Issue: {error_details}"
echo "Action: Review removals manually or report issue"
```

---

## Safety Constraints

**DO NOT REMOVE**:
- Public API methods (even if unused internally)
- Test fixtures and test utilities
- Configuration variables
- __init__.py files
- __main__.py entry points
- Code marked with # KEEP or # DO_NOT_REMOVE comments
- Callbacks registered via decorators
- Code used via reflection/dynamic imports

**ALWAYS**:
- Create backup before changes (unless --safe-mode false)
- Run full quality pipeline before commit
- Ask for user approval before applying changes
- Show detailed preview if requested
- Provide restoration instructions

**NEVER**:
- Remove code without analysis
- Skip quality checks
- Commit failing tests
- Remove files without verifying zero references

---

## Best Practices

### 1. Conservative Approach
- When in doubt, mark for review (don't auto-remove)
- Prefer false negatives (keep code) over false positives (remove needed code)

### 2. Thorough Analysis
- Check entire codebase for references, not just local file
- Consider reflection, dynamic imports, getattr() usage
- Exclude public APIs from unused function detection

### 3. Quality First
- ALWAYS run quality pipeline
- NEVER commit with failing tests
- Verify type checking passes

### 4. User Communication
- Show clear preview before changes
- Provide detailed removal reasons
- Offer selective approval option
- Display impact metrics

### 5. Safety Nets
- Default to safe mode (backup)
- Provide restoration instructions
- Auto-revert on quality failures
- Log all removals for audit

---

## Example Execution

### Command
```bash
/lazy cleanup src/services
```

### Output
```
🧹 Cleanup Analysis Starting...

Scope: src/services
Target Paths: ['src/services']
Safe Mode: enabled
Dry Run: no

Scanning for dead code...

🔍 Analyzing: src/services/auth.py
🔍 Analyzing: src/services/payment.py
🔍 Analyzing: src/services/notification.py

🧹 Cleanup Analysis Complete

Dead Code Found:

✅ SAFE TO REMOVE:
  ✓ 5 unused imports in 3 files
  ✓ 2 unused functions (35 lines)
  ✓ 3 unused variables
  ✓ 1 unreachable code block (8 lines)
  ✓ 50 lines of commented code
  ✓ 1 orphaned file (old_utils.py, 200 lines)

📊 Impact:
  Total lines to remove: 293
  Files affected: 4
  Estimated time saved: 15 minutes in future maintenance

🔒 Safety:
  Safe mode: enabled
  Dry run: no
  Backup: will be created

Apply cleanup? (y/n/p/s): y

💾 Safety backup created: stash@{0}
   To restore: git stash apply stash@{0}

🧹 Applying cleanup...

✅ Removed unused imports (3 files)
✅ Removed unused functions (2 files)
✅ Removed commented code (3 files)
✅ Removed orphaned file: src/services/old_utils.py

Total: 293 lines removed from 4 files

📊 Quality Pipeline: RUNNING...

✅ Format (Black/Ruff): PASS
✅ Lint (Ruff): PASS
✅ Type Check (Mypy): PASS
✅ Tests (Pytest): PASS
   - 124/124 tests passing
   - Coverage: 87% (unchanged)

All quality checks passed! ✅

💾 Committing changes...

✅ Cleanup Complete

📊 Summary:
  Scope: src/services
  Files modified: 3
  Files deleted: 1
  Lines removed: 293

  Items removed:
  ✓ 5 unused imports
  ✓ 2 unused functions
  ✓ 3 unused variables
  ✓ 1 unreachable code block
  ✓ 50 lines of commented code
  ✓ 1 orphaned file

📊 Quality Pipeline: PASS

💾 Committed: abc123def
  Message: "chore(cleanup): remove dead code"

💾 Safety Backup: stash@{0}
  To restore if needed: git stash apply stash@{0}

🎯 Impact:
  Code reduction: 293 lines
  Maintainability: Improved
  Future time saved: ~15 minutes
```

---

## Session Logging

All cleanup activities logged to `logs/<session-id>/cleanup.json`:

```json
{
  "command": "/lazy cleanup",
  "scope": "src/services",
  "safe_mode": true,
  "dry_run": false,
  "timestamp": "2025-10-26T10:30:00Z",
  "analysis": {
    "total_items_found": 15,
    "safe_to_remove": 12,
    "review_recommended": 3,
    "do_not_remove": 0
  },
  "removals": {
    "unused_imports": 5,
    "unused_functions": 2,
    "unused_variables": 3,
    "unreachable_code": 1,
    "commented_code": 1,
    "orphaned_files": 1
  },
  "impact": {
    "files_modified": 3,
    "files_deleted": 1,
    "lines_removed": 293
  },
  "quality_pipeline": {
    "format": "pass",
    "lint": "pass",
    "type_check": "pass",
    "tests": "pass"
  },
  "commit": {
    "sha": "abc123def",
    "message": "chore(cleanup): remove dead code"
  },
  "backup": {
    "stash_id": "stash@{0}",
    "created": true
  }
}
```

---

**Version**: 1.0
**Last Updated**: 2025-10-26
**Framework**: LAZY-DEV-FRAMEWORK
