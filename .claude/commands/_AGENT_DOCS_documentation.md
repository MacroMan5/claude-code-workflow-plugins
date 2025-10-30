# Agent Documentation for documentation Command

## Agents Used in This Command

This command leverages automatic agent delegation. The following agent is invoked:

### 1. Documentation Agent (`.claude/agents/documentation.md`)
- **When**: Step 3 - After identifying target files and validating format
- **Purpose**: Generate or update documentation for specified scope and format
- **Invocation**: Automatic via agent descriptions

**What it does:**
- Reads target files and analyzes code structure
- Generates appropriate documentation based on format:
  - **docstrings**: Adds/updates Google-style docstrings to functions and classes
  - **readme**: Generates or updates comprehensive README.md
  - **api**: Creates API documentation in docs/API.md
  - **security**: Generates security considerations document
  - **setup**: Creates setup/installation guide
- Writes updated files (docstrings) or new documentation files (readme/api/security/setup)
- Maintains consistent style and formatting

**Context provided to agent:**
- List of files to document (scope)
- Desired documentation format
- Target output directory
- Project context (existing docs, conventions)

**Invocation pattern:**
Claude automatically delegates to documentation agent when you provide:
- Scope (codebase, current-branch, last-commit, or specific path)
- Format (docstrings, readme, api, security, or setup)

---

## Documentation Formats

The agent handles multiple documentation formats:

**docstrings** (default):
- Adds Google-style docstrings to Python functions/classes
- Updates existing docstrings to meet standards
- Improves coverage percentage

**readme**:
- Generates comprehensive README.md
- Includes project overview, installation, usage
- Based on codebase analysis

**api**:
- Creates API documentation
- Documents public interfaces, parameters, returns
- Generates examples

**security**:
- Analyzes code for security patterns
- Documents security considerations
- Notes potential vulnerabilities

**setup**:
- Creates installation and setup guide
- Documents dependencies and configuration
- Provides step-by-step instructions

---

## Key Principle: Automatic Delegation

**No manual agent selection is required.**

Claude automatically invokes the documentation agent when you provide:
- Documentation scope
- Desired format
- (Optional) Target directory

The agent reads code, generates appropriate documentation, and writes output files. Coverage metrics are calculated before/after to show improvement.
