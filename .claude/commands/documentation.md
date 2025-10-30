---
description: Generate documentation for codebase, branch, commit, or file
argument-hint: [scope] [format]
allowed-tools: Read, Write, Bash, Glob, Grep, Edit, Task
model: claude-haiku-4-5-20251001
---

# Documentation Generator

Generate or update documentation for the specified scope with the selected format.

## Variables

SCOPE: $1
FORMAT: ${2:-docstrings}
PROJECT_ROOT: $(pwd)

## Instructions

You are the Documentation Command Handler for LAZY-DEV-FRAMEWORK.

Your task is to generate or update documentation based on the provided **SCOPE** and **FORMAT**.

### Step 1: Parse Scope and Identify Target Files

Analyze the **SCOPE** variable to determine which files need documentation:

- **`codebase`**: Document all Python files in the project
  - Use Glob to find: `**/*.py`
  - Exclude: `__pycache__`, `.venv`, `venv`, `node_modules`, `tests/`, `.git`

- **`current-branch`**: Document files changed in the current git branch
  - Run: `git diff --name-only main...HEAD` (or default branch)
  - Filter for relevant file extensions based on FORMAT

- **`last-commit`**: Document files in the most recent commit
  - Run: `git diff-tree --no-commit-id --name-only -r HEAD`
  - Filter for relevant file extensions

- **Specific file path** (e.g., `src/auth.py` or `.`): Document the specified file or directory
  - If directory: Use Glob to find relevant files
  - If file: Document that specific file
  - Validate the path exists before proceeding

### Step 2: Validate Format

Ensure **FORMAT** is one of the supported formats:
- `docstrings` - Add/update Google-style docstrings (default)
- `readme` - Generate or update README.md
- `api` - Generate API documentation
- `security` - Generate security considerations document
- `setup` - Generate setup/installation guide

If FORMAT is invalid, report an error and stop.

### Step 3: Prepare Agent Invocation

For each target file or module group, prepare to invoke the Documentation Agent with:

**Agent Call Structure**:
```markdown
You are the Documentation Agent. Generate documentation for the following scope:

## Scope
[List of files or description of scope]

## Format
$FORMAT

## Target
[Output directory based on format - docs/ for files, ./ for README]

## Instructions
[Format-specific instructions will be provided by the agent template]
```

**Use the Task tool** to invoke the Documentation Agent. The agent will:
1. Read the target files
2. Analyze code structure, functions, classes, and modules
3. Generate appropriate documentation based on FORMAT
4. Write updated files (for docstrings) or new documentation files (for readme/api/security/setup)

### Step 4: Track Coverage Changes

**Before Agent Invocation**:
- Count existing docstrings/documentation
- Calculate current documentation coverage percentage

**After Agent Invocation**:
- Count new/updated docstrings/documentation
- Calculate new documentation coverage percentage
- Report the improvement

### Step 5: Generate Summary Report

After all files are processed, generate a structured report in this format:

```
📖 Documentation Generated

[For docstrings format:]
Docstrings added: X files
  ✓ path/to/file1.py (Y functions/classes)
  ✓ path/to/file2.py (Z functions/classes)
  ✓ path/to/file3.py (W functions/classes)

Coverage: XX% → YY% ✅

[For readme/api/security/setup formats:]
Files created/updated:
  ✓ README.md
  ✓ docs/API.md
  ✓ docs/SECURITY.md
  ✓ docs/SETUP.md

Documentation status: Complete ✅
```

## Workflow

1. **Parse Arguments**
   - Extract SCOPE from $1
   - Extract FORMAT from $2 (default: docstrings)
   - Validate both parameters

2. **Identify Target Files**
   - Based on SCOPE, use Glob, Grep, or Bash (git commands) to locate files
   - Build a list of absolute file paths
   - Verify files exist and are readable

3. **Invoke Documentation Agent**
   - Use Task tool to invoke the Documentation Agent
   - Pass scope, format, and target directory
   - Agent reads files, generates documentation, writes output

4. **Calculate Coverage**
   - Compare before/after documentation metrics
   - Calculate coverage percentage improvement

5. **Generate Report**
   - List all files documented
   - Show coverage improvement
   - Confirm successful completion

## Error Handling

- If SCOPE is invalid or empty: Report error and ask user to specify scope
- If FORMAT is not supported: Report valid formats and ask user to choose
- If no files found for given SCOPE: Report no files found and suggest alternative scope
- If git commands fail (for branch/commit scopes): Report git error and suggest using file path
- If Documentation Agent fails: Report agent error and suggest manual review

## Examples

### Example 1: Document entire codebase with docstrings
```bash
/lazy documentation codebase docstrings
```

Expected flow:
1. Find all .py files in project
2. Invoke Documentation Agent for each module/file group
3. Agent adds Google-style docstrings to functions/classes
4. Report coverage improvement

### Example 2: Generate README for current branch changes
```bash
/lazy documentation current-branch readme
```

Expected flow:
1. Run git diff to find changed files
2. Invoke Documentation Agent with scope=changed files, format=readme
3. Agent generates comprehensive README.md
4. Report README created

### Example 3: Generate API docs for specific module
```bash
/lazy documentation src/auth.py api
```

Expected flow:
1. Validate src/auth.py exists
2. Invoke Documentation Agent with scope=src/auth.py, format=api
3. Agent generates docs/API.md with module documentation
4. Report API documentation created

### Example 4: Generate security documentation
```bash
/lazy documentation . security
```

Expected flow:
1. Find all relevant files in current directory
2. Invoke Documentation Agent with scope=current directory, format=security
3. Agent analyzes code for security patterns and generates docs/SECURITY.md
4. Report security documentation created

## Output Format Requirements

- Use emoji indicators for visual clarity (📖, ✓, ✅)
- Report absolute file paths in output
- Show clear before/after metrics for coverage
- List all files processed
- Indicate success/failure clearly
- Include actionable next steps if applicable

## Notes

- Documentation Agent is a sub-agent defined in `@LAZY_DEV/lazy_dev/subagents/documentation.md`
- Agent uses Haiku model for cost efficiency
- For large codebases (>50 files), process in batches of 10-15 files
- Coverage calculation counts docstrings/functions ratio for docstrings format
- For readme/api/security/setup formats, "coverage" means documentation completeness
- Always use absolute paths in reports
- Git commands are cross-platform compatible (Windows/Linux/macOS)
