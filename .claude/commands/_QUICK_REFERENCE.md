# Quick Reference: Agent Usage by Command

A quick lookup guide showing which agents are used in each command.

---

## create-feature

**Command**: `/lazy create-feature [description] [--role pm|techlead]`

**Agents**:
1. **project-manager** - Creates user story and task files
2. **task-enhancer** - Adds codebase context to tasks

**Flow**: Brief → project-manager → task files → task-enhancer → enhanced tasks

---

## task-exec

**Command**: `/lazy task-exec [TASK-ID] [--story US-X] [--with-research]`

**Agents**:
1. **research** (optional with --with-research) - Researches unfamiliar tech
2. **coder** - Implements the task
3. **reviewer** - Validates implementation

**Flow**: Research (optional) → coder → quality pipeline → reviewer → commit

**Parallel mode**: Multiple coder agents + reviewers run in parallel for independent tasks

---

## story-review

**Command**: `/lazy story-review [US-X.Y]`

**Agents**:
1. **reviewer-story** - Reviews complete story implementation

**Flow**: Collect tasks + commits → reviewer-story → APPROVED/CHANGES_NEEDED

---

## story-fix-review

**Command**: `/lazy story-fix-review [US-X.Y or REPORT-FILE]`

**Agents** (selected automatically based on issue type):
1. **coder** - Fixes security issues, code issues, bugs
2. **tester** - Adds missing tests
3. **refactor** - Fixes architecture issues
4. **documentation** - Adds missing documentation
5. **reviewer** - Validates each fix

**Flow**: Load report → for each issue: {appropriate agent} → quality pipeline → reviewer → commit → re-review

---

## cleanup

**Command**: `/lazy cleanup [codebase|current-branch|path]`

**Agents**:
1. **cleanup** - Identifies dead code safely

**Flow**: Scan code → cleanup agent → user approval → apply changes → quality pipeline → commit

---

## documentation

**Command**: `/lazy documentation [scope] [format]`

**Agents**:
1. **documentation** - Generates documentation

**Formats**: docstrings (default), readme, api, security, setup

**Flow**: Identify files → documentation agent → write output → report coverage

---

## Agent File Locations

All agents are located in: `.claude/agents/`

- `project-manager.md`
- `task-enhancer.md`
- `research.md`
- `coder.md`
- `reviewer.md`
- `reviewer-story.md`
- `tester.md`
- `refactor.md`
- `documentation.md`
- `cleanup.md`

---

## Key Principle

**All agent invocations are automatic.**

You don't need to manually call agents. Just:
1. Run the command
2. Provide necessary context
3. Claude automatically delegates to the right agent(s)

---

## Agent Specializations

| Agent | Specializes In |
|-------|----------------|
| project-manager | User story creation, task breakdown |
| task-enhancer | Codebase research, technical context |
| research | Technology research, best practices |
| coder | Code implementation, bug fixes, security |
| reviewer | Code review, validation |
| reviewer-story | Complete story validation |
| tester | Test writing, coverage improvement |
| refactor | Architecture improvements, refactoring |
| documentation | Docstrings, README, API docs |
| cleanup | Dead code identification |

---

## When Multiple Agents Run

### Sequential (One After Another)
- **create-feature**: project-manager → task-enhancer
- **task-exec** (single): research → coder → reviewer
- **story-fix-review**: appropriate agent → reviewer (per issue)

### Parallel (Simultaneously)
- **task-exec all**: Multiple coder agents + reviewers run in parallel for independent tasks
- **story-fix-review**: Independent issues can be fixed in parallel

---

## For More Details

- **Full documentation**: See `_AGENT_DOCS_[command-name].md`
- **Integration instructions**: See `_INTEGRATION_GUIDE.md`
- **Complete summary**: See `_SUMMARY_REPORT.md`

---

**Created**: 2025-10-29
**Purpose**: Quick reference for agent usage across commands
**Framework**: LAZY-DEV-FRAMEWORK
