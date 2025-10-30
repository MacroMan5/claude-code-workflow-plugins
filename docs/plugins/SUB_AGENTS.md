# LAZY_DEV Framework - Sub-Agent Registry

Central registry of all sub-agents with their purposes, tools, and usage patterns.

**Version**: 2.0.0
**Last Updated**: 2025-10-29
**Purpose**: Single source of truth for all sub-agent specifications

---

## Overview

LAZY_DEV uses 10 specialized sub-agents that operate on conversation context. Each agent extracts what it needs from the conversation naturally, following Anthropic's best practices for agent design.

**How Agents Work**:
- Agents are invoked via Claude Code's Task tool with `subagent_type="general-purpose"`
- Each agent is defined in a markdown file in `.claude/agents/`
- Agents extract context from the conversation (no explicit variable passing)
- Commands provide context through conversation, then spawn agents
- Agents read context naturally and produce results

**Key Principles**:
- No variable substitution - agents read conversation context
- Follows Anthropic best practices for Claude Code agents
- Each agent has a clear, focused purpose
- Agents use appropriate tools for their tasks
- Model selection based on task complexity (Haiku vs Sonnet)

---

## Table of Contents

1. [Project-Manager Agent](#1-project-manager-agent)
2. [Task-Enhancer Agent](#2-task-enhancer-agent)
3. [Coder Agent](#3-coder-agent)
4. [Reviewer Agent](#4-reviewer-agent)
5. [Reviewer-Story Agent](#5-reviewer-story-agent)
6. [Tester Agent](#6-tester-agent)
7. [Research Agent](#7-research-agent)
8. [Documentation Agent](#8-documentation-agent)
9. [Refactor Agent](#9-refactor-agent)
10. [Cleanup Agent](#10-cleanup-agent)

---

## Agent Invocation Pattern

All agents follow the same invocation pattern:

```python
# 1. Command provides context in conversation
# 2. Command spawns agent via Task tool
# 3. Agent reads context from conversation
# 4. Agent produces results
```

Example from a command:
```markdown
You are working with the following feature brief:

"Add OAuth2 authentication with Google provider"

Technical constraints:
- Python 3.11+
- FastAPI framework
- PostgreSQL database

Create a comprehensive USER-STORY.md and individual TASK files for this feature.
```

The agent prompt references the conversation context, and the agent extracts what it needs.

---

## 1. Project-Manager Agent

**Purpose**: Create comprehensive USER-STORY and individual TASK files from feature briefs.

**Location**: `.claude/agents/project-manager.md`

**Model**: Sonnet (requires complex reasoning for task breakdown)

**Tools**: Read, Write, Grep, Glob

**When to Use**:
- Start of new feature development
- Breaking down complex features into tasks
- Creating project structure and task files

**What It Does**:
1. Analyzes feature brief from conversation
2. Creates USER-STORY.md with:
   - Story ID (format: `US-YYYYMMDD-XXX`)
   - Description and acceptance criteria
   - Security considerations checklist
   - Testing requirements (unit, integration, edge cases)
   - Technical dependencies
   - Architecture impact
   - Definition of done
3. Creates multiple TASK-*.md files (one per task):
   - Task ID (format: `TASK-[StoryID]-[Number]`)
   - Description and acceptance criteria
   - Effort estimate (S/M/L)
   - Dependencies (blocked by, blocks)
   - Files to create/modify
   - Security checklist
   - Testing checklist
   - Quality gates

**Success Criteria**:
- USER-STORY.md exists with complete story structure
- Multiple TASK-*.md files created (one per atomic task)
- All acceptance criteria covered by tasks
- Dependencies clearly mapped
- Security and testing checklists comprehensive
- Each task is independently implementable

**Notes**:
- Creates separate files for each task (NOT a single TASKS.md)
- Tasks should be 2-4 hours each (atomic and testable)
- Story ID format: US-YYYYMMDD-XXX (e.g., US-20251026-001)
- Task ID format: TASK-[StoryID]-[Number] (e.g., TASK-US-20251026-001-1)
- File naming: TASK-US-YYYYMMDD-XXX-N.md

---

## 2. Task-Enhancer Agent

**Purpose**: Enhance task files with technical context by researching the codebase.

**Location**: `.claude/agents/task-enhancer.md`

**Model**: Sonnet (requires deep codebase analysis)

**Tools**: Read, Write, Edit, Grep, Glob

**When to Use**:
- After project-manager creates initial tasks
- Before starting implementation (to add context)
- When tasks need codebase-specific guidance

**What It Does**:
1. Reads existing TASK files from conversation context
2. Researches codebase for relevant patterns
3. Enhances each TASK file with:
   - Technical overview (how task fits into architecture)
   - Relevant files to reference
   - Files to create/modify (with line numbers)
   - Code patterns from codebase (10-30 line snippets)
   - Dependencies (existing + new)
   - Architecture integration
   - Testing strategy
   - Security considerations
   - Implementation tips (do's/don'ts, gotchas)

**Success Criteria**:
- Each task has actionable technical context
- At least 3 relevant files identified per task
- At least 2 code pattern examples with file paths
- Specific files to create/modify with line numbers
- Dependencies clearly listed (existing + new)
- Architecture integration clear
- Testing strategy aligned with project conventions

**Notes**:
- Runs AFTER project-manager creates initial tasks
- Reads codebase extensively but only writes/edits task files
- Provides concrete, actionable information (not vague suggestions)
- Code examples should be 10-30 lines (copy-pasteable)
- Handles edge cases: new projects, legacy codebases, microservices

---

## 3. Coder Agent

**Purpose**: Implement coding tasks with clean, tested, type-hinted code.

**Location**: `.claude/agents/coder.md`

**Model**: Sonnet (requires complex implementation logic)

**Tools**: Read, Write, Edit, Bash, Grep, Glob

**When to Use**:
- Implementing individual tasks
- Writing production code
- Creating tests alongside implementation

**What It Does**:
1. Reads task description and acceptance criteria from conversation
2. Optionally reads research context if provided
3. Implements code with:
   - Type hints on all functions (Python 3.11+)
   - Google-style docstrings (Args, Returns, Raises, Examples)
   - Comprehensive error handling
   - Input validation
   - Security best practices
4. Creates test files with:
   - Unit tests for all functions
   - Integration tests for workflows
   - Edge case coverage (null, empty, boundary)
   - Mocked external dependencies
   - Minimum 80% coverage

**Success Criteria**:
- All acceptance criteria met
- Code is clean, readable, and well-structured
- Type hints on all functions
- Comprehensive docstrings (Google style)
- Error handling with specific exceptions
- Security best practices followed (OWASP Top 10)
- Tests written with >= 80% coverage
- Tests pass (pytest succeeds)

**Notes**:
- Python 3.11+ type hints required
- Google-style docstrings mandatory
- Security is paramount (input validation, no secrets in code)
- Tests should follow Arrange-Act-Assert pattern
- Mock external dependencies (APIs, databases)

---

## 4. Reviewer Agent

**Purpose**: Review code implementation for quality, security, and testing.

**Location**: `.claude/agents/reviewer.md`

**Model**: Sonnet (requires deep code analysis)

**Tools**: Read, Grep, Glob, Bash (git diff, git log)

**When to Use**:
- After implementing a task
- Before committing code
- As part of quality pipeline

**What It Does**:
1. Reads code files and acceptance criteria from conversation
2. Reviews code against multiple dimensions:
   - Code quality (type hints, docstrings, naming, complexity)
   - Security (input validation, OWASP Top 10)
   - Testing (coverage, edge cases, test quality)
   - Functionality (meets acceptance criteria, edge cases)
   - Documentation (docstrings, README, API docs)
3. Returns structured JSON response:
   - Status: APPROVED or REQUEST_CHANGES
   - Issues list (severity, file, line, description, fix)
   - Summary of overall assessment

**Review Dimensions**:

**Code Quality**:
- Type hints on all functions
- Docstrings complete (Google style)
- Clean, readable code (no complex nesting)
- No code smells (duplication, long functions)
- Proper naming (descriptive, consistent)

**Security**:
- Input validation implemented
- No hardcoded secrets
- Error handling doesn't leak sensitive info
- OWASP Top 10 compliance

**Testing**:
- Unit tests present
- Tests pass
- Edge cases covered
- Good coverage (>= 80%)

**Functionality**:
- Meets all acceptance criteria
- Handles edge cases
- Performance acceptable
- No regressions

**Decision Criteria**:
- **APPROVED**: No critical issues, warnings are minor
- **REQUEST_CHANGES**: Critical issues OR multiple warnings

**Notes**:
- Reviews at task level (individual implementation)
- Focuses on code quality and security
- Returns structured JSON for automated processing
- Used in quality pipeline before commit

---

## 5. Reviewer-Story Agent

**Purpose**: Review all tasks in a story together for cohesion and completeness before PR creation.

**Location**: `.claude/agents/reviewer-story.md`

**Model**: Sonnet (requires holistic analysis)

**Tools**: Read, Grep, Glob, Bash

**When to Use**:
- After all tasks in a story are complete
- Before creating pull request
- To verify story-level integration

**What It Does**:
1. Reads story file, task files, and branch from conversation
2. Reviews entire story for:
   - Story completeness (all acceptance criteria met)
   - Code quality consistency across tasks
   - Integration (tasks work together cohesively)
   - Testing (all tests pass, adequate coverage)
   - Documentation (APIs documented, README updated)
   - Security (input validation, vulnerability prevention)
3. Returns JSON response with:
   - Status: APPROVED or REQUEST_CHANGES
   - Issues list (per task)
   - Summary of entire story
   - Tasks reviewed
   - Report path (if REQUEST_CHANGES)
4. If REQUEST_CHANGES, creates detailed US-{story_id}_REPORT.md

**Review Responsibilities**:

**Story Completeness**:
- All acceptance criteria from US-story.md met
- All tasks completed
- No missing functionality

**Code Quality**:
- Consistent code style across tasks
- No code duplication between tasks
- Proper error handling throughout
- Type hints consistent

**Integration**:
- All tasks work together cohesively
- No conflicts between task implementations
- Data flows correctly between components
- Consistent patterns

**Testing**:
- All tests pass
- Test coverage adequate
- Edge cases covered
- Integration tests for multi-task features

**Documentation**:
- Public APIs documented
- README updated
- Complex logic has comments
- Migration guides if needed

**Security**:
- Input validation throughout
- No SQL injection vulnerabilities
- No XSS vulnerabilities
- Sensitive data properly handled

**Decision Criteria**:

**APPROVED**:
- All checklist items pass
- All tests pass
- No CRITICAL issues
- At most minor SUGGESTIONS

**REQUEST_CHANGES**:
- Any CRITICAL issues
- Any tests fail
- Multiple WARNING issues
- Integration problems
- Missing acceptance criteria

**Notes**:
- Reviews at STORY level (all tasks together)
- Focuses on integration and cohesion
- Creates detailed report if requesting changes
- Used by `/lazy story-review` command
- Report format enables automated fix workflow

---

## 6. Tester Agent

**Purpose**: Generate comprehensive test suites with edge cases.

**Location**: `.claude/agents/tester.md`

**Model**: Haiku (testing is well-defined, doesn't require complex reasoning)

**Tools**: Read, Write, Bash (pytest, coverage)

**When to Use**:
- Generating tests for existing code
- Adding test coverage
- Creating test suites for new features

**What It Does**:
1. Reads code files from conversation context
2. Analyzes code structure and logic
3. Generates comprehensive test files with:
   - `tests/test_*.py` naming convention
   - pytest framework usage
   - Mocked external dependencies
   - Clear, descriptive test names
   - Arrange-Act-Assert pattern
   - Coverage >= target percentage
4. Tests cover:
   - Success cases
   - Edge cases (null, empty, boundary values)
   - Error cases (exceptions, invalid inputs)
   - Integration scenarios

**Test Requirements**:

**Coverage**:
- Unit tests for all functions
- Integration tests for workflows
- Edge cases: null, empty, boundary values
- Error handling: exceptions, invalid inputs

**Edge Cases to Cover**:
- Null/None inputs
- Empty strings/lists/dicts
- Boundary values (0, -1, MAX_INT)
- Invalid types
- Concurrent access (if applicable)
- Resource exhaustion

**Success Criteria**:
- Test files created in `tests/` directory
- Test naming follows `test_*` convention
- All tests use pytest framework
- External dependencies are mocked
- Coverage meets or exceeds target
- Tests follow Arrange-Act-Assert pattern
- Test names are clear and descriptive

**Notes**:
- Uses Haiku model (cost-efficient for well-defined task)
- Follows pytest conventions
- Mocks external dependencies (APIs, databases)
- Tests should be maintainable and clear
- Used by coder agent and in quality pipeline

---

## 7. Research Agent

**Purpose**: Research documentation and best practices for technologies.

**Location**: `.claude/agents/research.md`

**Model**: Haiku (research is retrieval-focused, doesn't require complex reasoning)

**Tools**: Read, WebSearch, WebFetch

**When to Use**:
- Implementing unfamiliar technologies
- Researching API documentation
- Finding best practices and patterns

**What It Does**:
1. Reads research keywords and depth from conversation
2. Searches official documentation and community resources
3. Produces markdown research document with:
   - Official documentation references
   - Key APIs/methods with examples
   - Best practices
   - Common pitfalls and solutions
   - Code examples (basic and advanced)
   - Recommendations based on findings

**Research Depth Levels**:

**Quick Research**:
- Official documentation only
- Key APIs/methods
- Basic usage examples
- Common gotchas

**Comprehensive Research**:
- Official documentation
- Community best practices
- Multiple code examples
- Common pitfalls
- Performance considerations
- Security implications
- Alternative approaches

**Success Criteria**:
- Official documentation sourced and cited
- Key APIs/methods documented with examples
- Best practices clearly listed
- Common pitfalls identified with solutions
- Code examples provided (basic and advanced)
- Recommendations made based on findings

**Notes**:
- Uses Haiku model (cost-efficient for research)
- WebSearch and WebFetch tools for documentation
- Provides concrete, actionable research
- Used by coder agent when implementing unfamiliar technologies
- Research results are provided to coder in conversation context

---

## 8. Documentation Agent

**Purpose**: Generate or update documentation, docstrings, and README files.

**Location**: `.claude/agents/documentation.md`

**Model**: Haiku (documentation generation is well-defined)

**Tools**: Read, Write, Grep, Glob

**When to Use**:
- Adding docstrings to code
- Generating README files
- Creating API documentation
- Writing security or setup guides

**What It Does**:
1. Reads scope and format from conversation
2. Generates or updates documentation based on format:
   - **docstrings**: Adds/updates Google-style docstrings in code
   - **readme**: Generates comprehensive README.md
   - **api**: Generates API reference documentation
   - **security**: Generates security documentation
   - **setup**: Generates setup/installation guide

**Documentation Formats**:

**Docstrings**:
- Google-style docstrings
- Args, Returns, Raises, Examples sections
- Clear, concise descriptions

**README**:
- Project overview
- Features list
- Installation instructions
- Quick start guide
- API reference link

**API Reference**:
- Module/class/method documentation
- Parameters, return values, exceptions
- Usage examples

**Security**:
- Authentication mechanisms
- Input validation rules
- Vulnerability prevention

**Setup**:
- Prerequisites
- Installation steps
- Configuration
- Troubleshooting

**Success Criteria**:
- Documentation generated in correct format
- All public APIs documented
- Examples provided where applicable
- Clear, concise language
- Proper markdown formatting
- Files created in target directory

**Notes**:
- Uses Haiku model (cost-efficient)
- Google-style docstrings for Python
- Markdown format for all docs
- Used by `/lazy documentation` command
- Can update existing docs or create new ones

---

## 9. Refactor Agent

**Purpose**: Simplify code while preserving functionality.

**Location**: `.claude/agents/refactor.md`

**Model**: Sonnet (requires complex code analysis)

**Tools**: Read, Edit

**When to Use**:
- Simplifying complex code
- Reducing cyclomatic complexity
- Removing code duplication
- Improving code maintainability

**What It Does**:
1. Reads code files and complexity threshold from conversation
2. Analyzes code for complexity, duplication, naming issues
3. Refactors code to:
   - Reduce cyclomatic complexity (≤ threshold)
   - Extract functions for complex logic
   - Remove code duplication (DRY principle)
   - Improve naming (clarity over brevity)
   - Add type hints (if missing)
   - Improve error handling
4. Provides:
   - Refactored code
   - Explanation of changes
   - Verification that tests still pass
   - Backward compatibility confirmation

**Refactoring Goals**:

**Reduce Complexity**:
- Cyclomatic complexity ≤ threshold
- Extract functions for complex logic
- Simplify conditional logic

**Remove Duplication**:
- DRY principle (Don't Repeat Yourself)
- Extract common logic
- Create reusable utilities

**Improve Naming**:
- Descriptive variable/function names
- Clear intent (clarity over brevity)

**Add Type Hints**:
- Type hints on all functions
- Type hints for complex data structures

**Improve Error Handling**:
- Specific exceptions
- Proper error messages
- Error recovery patterns

**Constraints**:
- DO NOT change functionality - behavior must be identical
- Maintain all tests - tests must still pass
- Preserve public APIs - no breaking changes
- Keep backward compatibility - existing callers unaffected

**Success Criteria**:
- Cyclomatic complexity reduced to ≤ threshold
- Code duplication eliminated
- All tests still pass
- No breaking changes
- Backward compatibility maintained
- Code is more readable and maintainable

**Notes**:
- Uses Sonnet model (requires complex analysis)
- Preserves functionality (no behavior changes)
- All tests must pass after refactoring
- Used by `/lazy story-fix-review` for architecture issues

---

## 10. Cleanup Agent

**Purpose**: Remove dead code, unused imports, and temporary files.

**Location**: `.claude/agents/cleanup.md`

**Model**: Haiku (cleanup is pattern-matching, doesn't require complex reasoning)

**Tools**: Read, Edit, Bash (git rm), Grep, Glob

**When to Use**:
- Removing dead code
- Cleaning up unused imports
- Deleting temporary files
- Preparing code for review

**What It Does**:
1. Reads paths and safe mode setting from conversation
2. Scans for:
   - Unused imports
   - Dead code (functions/classes with 0 references)
   - Commented-out code
   - Temporary files (`__pycache__/`, `*.pyc`, `.pytest_cache/`)
3. In safe mode (dry run):
   - Reports changes only
   - Lists candidates for deletion
   - Shows impact analysis
4. In execute mode:
   - Executes cleanup
   - Deletes dead code and files
   - Creates git commit with changes
5. Generates cleanup report with:
   - Unused imports removed
   - Dead code removed
   - Commented code removed
   - Temp files deleted
   - Impact analysis (lines removed, files modified, disk space freed)
   - Safety check (tests still pass)

**Cleanup Tasks**:

**Unused Imports**:
- Identify imports not referenced in file
- Remove import statements

**Dead Code**:
- Identify functions with 0 references
- Identify classes with 0 references
- Remove unreferenced code

**Commented Code**:
- Remove commented-out code
- Keep TODO comments
- Keep documentation comments

**Temp Files**:
- Remove `__pycache__/` directories
- Remove `*.pyc` files
- Remove `.pytest_cache/`
- Remove other temp files

**Success Criteria**:
- Unused imports removed
- Dead code identified and removed (or reported)
- Commented code removed
- Temp files deleted
- Impact analysis provided
- All tests still pass after cleanup

**Notes**:
- Uses Haiku model (cost-efficient)
- Safe mode recommended for first run
- Always verify tests pass after cleanup
- Used by `/lazy cleanup` command
- Creates git commit if safe_mode=false

---

## Model Selection Guide

### When to Use Sonnet

Use **Sonnet** model for agents requiring:
- Complex reasoning and analysis
- Deep codebase understanding
- Multi-file integration analysis
- Architectural decisions

**Agents using Sonnet**:
- Project-Manager (task breakdown)
- Task-Enhancer (codebase research)
- Coder (complex implementation)
- Reviewer (code analysis)
- Reviewer-Story (integration analysis)
- Refactor (code transformation)

### When to Use Haiku

Use **Haiku** model for agents with:
- Well-defined tasks
- Pattern-matching work
- Retrieval-focused work
- Cost-sensitive operations

**Agents using Haiku**:
- Tester (test generation)
- Research (documentation retrieval)
- Documentation (doc generation)
- Cleanup (dead code detection)

### Cost Considerations

**Sonnet**:
- Higher cost per token
- Better for complex reasoning
- Use for critical path (implementation, review)

**Haiku**:
- Lower cost per token (10-20x cheaper)
- Good for well-defined tasks
- Use for repetitive tasks (testing, docs, cleanup)

---

## Agent Summary Table

| Agent | Model | Tools | Primary Use Case |
|-------|-------|-------|------------------|
| Project-Manager | Sonnet | Read, Write, Grep, Glob | Break feature into story and tasks |
| Task-Enhancer | Sonnet | Read, Write, Edit, Grep, Glob | Add technical context to tasks |
| Coder | Sonnet | Read, Write, Edit, Bash, Grep, Glob | Implement coding tasks |
| Reviewer | Sonnet | Read, Grep, Glob, Bash | Review task implementation |
| Reviewer-Story | Sonnet | Read, Grep, Glob, Bash | Review entire story |
| Tester | Haiku | Read, Write, Bash | Generate test suites |
| Research | Haiku | Read, WebSearch, WebFetch | Research technologies |
| Documentation | Haiku | Read, Write, Grep, Glob | Generate/update docs |
| Refactor | Sonnet | Read, Edit | Simplify complex code |
| Cleanup | Haiku | Read, Edit, Bash, Grep, Glob | Remove dead code |

---

## File Locations

All agent templates are located in `.claude/agents/`:
- `project-manager.md`
- `task-enhancer.md`
- `coder.md`
- `reviewer.md`
- `reviewer-story.md`
- `tester.md`
- `research.md`
- `documentation.md`
- `refactor.md`
- `cleanup.md`

---

**End of Document**

For questions or contributions, see CONTRIBUTING.md or open an issue on GitHub.
