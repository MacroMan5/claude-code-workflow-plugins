# WORKFLOW.md

Complete workflow documentation for LAZY_DEV Framework - The commit-per-task, PR-per-story pattern.

---

## Table of Contents

1. [Workflow Overview](#workflow-overview)
2. [The Pattern: Commit Per Task, PR Per Story](#the-pattern-commit-per-task-pr-per-story)
3. [Complete Workflow Steps](#complete-workflow-steps)
4. [Quality Pipeline Details](#quality-pipeline-details)
5. [Agent Delegation Flow](#agent-delegation-flow)
6. [Git Operations](#git-operations)
7. [Failure Scenarios & Recovery](#failure-scenarios--recovery)
8. [Best Practices](#best-practices)
9. [Examples](#examples)

---

## Workflow Overview

LAZY_DEV implements a structured workflow that ensures:
- ✅ Consistent quality through mandatory pipeline
- ✅ Clear git history with atomic commits
- ✅ Cohesive PRs that represent complete features
- ✅ Automatic delegation to specialized agents
- ✅ Persistent knowledge across sessions

### The Big Picture

```
Voice/Text Input → Prompt Enhancement → Feature Creation
                                              ↓
                                    User Story + Tasks
                                              ↓
                                       Task Execution
                                       (TDD + Quality)
                                              ↓
                                         Git Commit
                                              ↓
                                    More Tasks? → Yes: Loop
                                              ↓ No
                                       Story Review
                                              ↓
                                    Approved? → Yes: PR
                                              ↓ No
                                       Fix & Re-review
```

---

## The Pattern: Commit Per Task, PR Per Story

### The Problem with Task-Level PRs

**Old Anti-Pattern:**
```
TASK-1.1 → Code → COMMIT → PR #1 ❌
TASK-1.2 → Code → COMMIT → PR #2 ❌
TASK-1.3 → Code → COMMIT → PR #3 ❌
```

**Issues:**
- Too many PRs
- Fragmented reviews
- Unclear feature boundaries
- Merge conflicts
- Lost context

### The LAZY_DEV Solution

**New Pattern:**
```
USER-STORY: Add Payment Processing
│
├── TASK-1.1: Setup Stripe API
│   └── Code → Quality → Review → COMMIT (no PR)
│
├── TASK-1.2: Implement payment processing
│   └── Code → Quality → Review → COMMIT (no PR)
│
├── TASK-1.3: Add validation
│   └── Code → Quality → Review → COMMIT (no PR)
│
└── STORY REVIEW
    └── All tasks reviewed together → PR #1 ✅
```

**Benefits:**
- One PR per feature
- Cohesive reviews
- Clear git history
- Atomic commits
- Complete context

---

## Complete Workflow Steps

### Phase 1: Feature Creation

**Command:**
```bash
/lazy create-feature "Add payment processing with Stripe"
```

**What Happens:**

1. **UserPromptSubmit Hook Fires:**
   - Enriches prompt with architecture patterns
   - Adds security considerations (OWASP)
   - Adds testing requirements
   - Adds edge cases

2. **Project Manager Agent Invoked:**
   - Creates `USER-STORY.md` with acceptance criteria
   - Creates `TASKS.md` with atomic task breakdown
   - Estimates effort
   - Identifies dependencies

3. **Optional: GitHub Issue Sync:**
   - Creates GitHub issue for story
   - Creates sub-issues for tasks
   - Links them together

**Output:**
```
✅ USER-STORY.md created
✅ TASKS.md created with 3 tasks
   - TASK-1.1: Setup Stripe API integration (2h)
   - TASK-1.2: Implement payment processing (4h)
   - TASK-1.3: Add validation (2h)
```

---

### Phase 2: Task Execution (Iterative)

**Command:**
```bash
/lazy task-exec TASK-1.1
```

**Workflow Steps:**

#### Step 1: Pre-Execution Validation
```
✓ Task exists in TASKS.md
✓ Dependencies satisfied
✓ Git working directory clean
✓ On correct branch
```

#### Step 2: Research (Optional)
```bash
/lazy task-exec TASK-1.1 --with-research
```
- Research agent fetches documentation
- Caches examples and patterns
- Returns context to coder

#### Step 3: Implementation (TDD)

**RED Phase:**
```python
# Coder agent writes failing tests first
def test_stripe_integration():
    """Test Stripe API integration."""
    client = StripeClient(api_key="test_key")
    assert client.create_payment(100) == "success"
```

**GREEN Phase:**
```python
# Minimal implementation to pass tests
class StripeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def create_payment(self, amount: int) -> str:
        # Minimal implementation
        return "success"
```

**REFACTOR Phase:**
```python
# Improve code quality
class StripeClient:
    """Client for Stripe API integration."""

    def __init__(self, api_key: str) -> None:
        """Initialize Stripe client.

        Args:
            api_key: Stripe API key
        """
        if not api_key:
            raise ValueError("API key required")
        self.api_key = api_key

    def create_payment(self, amount: int) -> str:
        """Create payment via Stripe.

        Args:
            amount: Payment amount in cents

        Returns:
            Payment status

        Raises:
            ValueError: If amount invalid
        """
        if amount <= 0:
            raise ValueError("Amount must be positive")
        # Implementation with error handling
        return "success"
```

#### Step 4: Quality Pipeline (Mandatory, Sequential)

```
Format (Black/Ruff) → PASS ✅
       ↓
Lint (Ruff) → PASS ✅
       ↓
Type (Mypy) → PASS ✅
       ↓
Test (Pytest) → PASS ✅ (Coverage: 95%)
       ↓
Proceed to Review
```

**Fail-Fast:**
- If any step fails, workflow stops
- Issues reported clearly
- Developer fixes before continuing

#### Step 5: Code Review

**Reviewer Agent Evaluates:**
- ✓ Readability
- ✓ Security (OWASP top 10)
- ✓ Performance
- ✓ Testing adequacy
- ✓ Edge cases
- ✓ Architectural consistency

**Review Results:**
- **APPROVED**: Proceed to commit
- **CHANGES REQUIRED**: Return to implementation

#### Step 6: Git Commit (NO PR YET)

```bash
# Automated by framework
git add <changed-files>
git commit -m "feat(payment): setup Stripe API integration

Implements TASK-1.1: Setup Stripe API integration

Changes:
- Add StripeClient class
- Implement payment creation
- Add input validation

Tests: Added test_stripe_integration.py
Coverage: 95%

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Output:**
```
✅ TASK-1.1 committed (commit: a1b2c3d4)
   Ready for next task or story review
```

---

### Phase 3: Continue Tasks

Repeat Phase 2 for each task:

```bash
/lazy task-exec TASK-1.2
# → Commit b5c6d7e8

/lazy task-exec TASK-1.3
# → Commit f9g0h1i2
```

**Git History:**
```
* f9g0h1i2 feat(payment): add validation
* b5c6d7e8 feat(payment): implement payment processing
* a1b2c3d4 feat(payment): setup Stripe API integration
```

---

### Phase 4: Story Review

**Command:**
```bash
/lazy story-review USER-STORY.md
```

**What Happens:**

#### Step 1: Context Collection
```
✓ Load USER-STORY.md
✓ Load all task commits
✓ Generate diff summary
✓ Collect test results
✓ Collect quality metrics
```

#### Step 2: Story Review Agent Evaluation

**Checks Against Acceptance Criteria:**
```
✓ Setup Stripe API integration
✓ Implement payment processing
✓ Add validation
✓ Handle errors
✓ Add tests
```

**Security Review:**
```
✓ No hardcoded secrets
✓ Input validation present
✓ Rate limiting implemented
✓ CSRF protection added
```

**Quality Review:**
```
✓ All tests passing
✓ Coverage: 92%
✓ No lint errors
✓ Type hints complete
```

#### Step 3: Decision

**If APPROVED:**
```bash
# Create PR automatically
gh pr create \
  --title "[FEATURE] Add Payment Processing" \
  --body "$(cat <<'EOF'
## User Story
Add payment processing with Stripe integration

## Acceptance Criteria
✓ Setup Stripe API
✓ Process payments
✓ Validate inputs
✓ Handle errors

## Tasks Completed
✓ TASK-1.1: Setup Stripe API integration
✓ TASK-1.2: Implement payment processing
✓ TASK-1.3: Add validation

## Commits
• f9g0h1i2 feat(payment): add validation
• b5c6d7e8 feat(payment): implement payment processing
• a1b2c3d4 feat(payment): setup Stripe API integration

## Testing
✓ 32 tests passing
✓ Coverage: 92%
✓ Integration tests included

## Quality Checks
✓ Format: PASS
✓ Lint: PASS
✓ Type: PASS
✓ Test: PASS

Generated with LAZY-DEV-FRAMEWORK
EOF
)" \
  --base main
```

**If CHANGES REQUIRED:**
```
❌ Story review: CHANGES REQUIRED

Issues:
🔴 CRITICAL: Missing webhook validation
   Required: Add TASK-1.4 for webhook handling

⚠️ WARNING: No rate limiting on payment endpoint
   Fix: Add rate limiting middleware

Required Actions:
1. Add TASK-1.4: Implement webhook handling
2. Add rate limiting to payment endpoint
3. Re-run story-review after fixes
```

---

### Phase 5: Fix Review (If Needed)

**Command:**
```bash
/lazy story-fix-review review-report.md
```

**What Happens:**
1. Parse review report
2. Create new task (TASK-1.4) if needed
3. Execute task: `/lazy task-exec TASK-1.4`
4. Fix existing tasks
5. Re-run story review

---

## Quality Pipeline Details

### Format Check (Black + Ruff)

**Purpose:** Ensure consistent code style

**Tools:**
- Black (opinionated formatter)
- Ruff (fast formatter)

**Script:**
```bash
python scripts/format.py .
```

**What it checks:**
- Line length (88 characters)
- Indentation consistency
- Import sorting
- Trailing whitespace
- Quote style

**Auto-fix:** Yes

---

### Lint Check (Ruff)

**Purpose:** Catch code quality issues

**Script:**
```bash
python scripts/lint.py .
```

**What it checks:**
- Unused imports
- Undefined variables
- Missing docstrings
- Complexity issues
- Style violations (PEP 8)

**Auto-fix:** Partial

---

### Type Check (Mypy)

**Purpose:** Validate type hints

**Script:**
```bash
python scripts/type_check.py .
```

**What it checks:**
- Type hint coverage
- Type compatibility
- Return type correctness
- Argument type correctness

**Auto-fix:** No (manual fixes required)

---

### Test Check (Pytest)

**Purpose:** Validate functionality and coverage

**Script:**
```bash
python scripts/test_runner.py .
```

**What it checks:**
- All tests passing
- Coverage ≥ 80%
- No test warnings
- Test isolation

**Auto-fix:** No (manual fixes required)

---

## Agent Delegation Flow

### Context-Based Delegation (Anthropic Pattern)

Agents are invoked automatically based on conversation context.

**Example: Task Execution**

```
User: /lazy task-exec TASK-1.1
           ↓
Command provides context in conversation:
  "Execute TASK-1.1: Setup Stripe API integration
   Acceptance Criteria: [...]
   Dependencies: None"
           ↓
Coder Agent reads context from conversation
           ↓
Coder implements with TDD
           ↓
Tester Agent adds comprehensive tests
           ↓
Reviewer Agent evaluates code
```

**No Variable Substitution:**
- Agents extract context naturally
- No `$variable` templates needed
- Cleaner, simpler implementation

---

## Git Operations

### Branch Strategy

**Recommended: Single Feature Branch**

```bash
# Create feature branch
git checkout -b feature/payment-processing

# All tasks commit to same branch
/lazy task-exec TASK-1.1  # → commit a1b2c3d4
/lazy task-exec TASK-1.2  # → commit b5c6d7e8
/lazy task-exec TASK-1.3  # → commit f9g0h1i2

# Story review creates PR from branch
/lazy story-review USER-STORY.md
# → PR: feature/payment-processing → main
```

**Git Log:**
```
* f9g0h1i2 (HEAD -> feature/payment-processing) feat(payment): add validation
* b5c6d7e8 feat(payment): implement payment processing
* a1b2c3d4 feat(payment): setup Stripe API integration
* m3n4o5p6 (main) Previous work
```

---

### Commit Message Format

**Convention:** Conventional Commits

```
<type>(<scope>): <description>

Implements TASK-<id>: <task title>

<detailed description>

Changes:
- <change 1>
- <change 2>

Tests: <test information>
Coverage: <percentage>%

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Test additions
- `docs`: Documentation
- `perf`: Performance improvement
- `chore`: Maintenance

---

## Failure Scenarios & Recovery

### Quality Pipeline Failure

**Scenario:** Tests fail during task execution

```
❌ Tests failed:
   FAILED tests/test_payment.py::test_invalid_amount
   Coverage: 65% (below 80% threshold)
```

**Recovery:**
```bash
# Fix failing tests
vim tests/test_payment.py

# Add missing tests for coverage
vim tests/test_payment_edge_cases.py

# Re-run quality pipeline
pytest tests/ -v --cov

# Continue task execution
/lazy task-exec TASK-1.1 --retry-from=test
```

---

### Code Review Failure

**Scenario:** Reviewer finds security issue

```
❌ Code review: CHANGES REQUIRED

🔴 CRITICAL: SQL Injection Vulnerability
   File: payment_processor.py:45
   Fix: Use parameterized queries
```

**Recovery:**
```bash
# Fix security issue
vim payment_processor.py

# Re-run quality pipeline
python scripts/format.py .
pytest tests/ -v

# Retry from review step
/lazy task-exec TASK-1.1 --retry-from=review
```

---

### Story Review Failure

**Scenario:** Story incomplete

```
❌ Story review: CHANGES REQUIRED

Missing Requirements:
1. Webhook validation not implemented
   → Add TASK-1.4: Implement webhook handling

2. No rate limiting
   → Add rate limiting middleware
```

**Recovery:**
```bash
# Add missing task
cat >> TASKS.md <<'EOF'

## TASK-1.4: Add webhook validation
**Status**: draft
**Estimate**: 2 hours
EOF

# Execute new task
/lazy task-exec TASK-1.4

# Fix existing code
vim payment_api.py  # Add rate limiting

# Commit fix
git add .
git commit -m "fix(payment): add rate limiting"

# Re-run story review
/lazy story-review USER-STORY.md
```

---

## Best Practices

### 1. Keep Tasks Atomic

**Good:**
```
TASK-1.1: Setup Stripe API client
TASK-1.2: Implement payment creation
TASK-1.3: Add payment validation
```

**Bad:**
```
TASK-1.1: Add complete payment system
```

---

### 2. Write Tests First (TDD)

**Correct Order:**
```
1. Write failing test
2. Implement minimal code to pass
3. Refactor for quality
```

**Avoid:**
```
1. Write implementation
2. Add tests after
```

---

### 3. Commit Messages Should Tell a Story

**Good:**
```
feat(payment): setup Stripe API integration

Implements TASK-1.1: Setup Stripe API integration

Added StripeClient class with payment creation support.
Includes input validation and error handling.

Changes:
- Add StripeClient class
- Implement create_payment method
- Add API key validation

Tests: Added test_stripe_integration.py
Coverage: 95%
```

**Bad:**
```
update code
```

---

### 4. Review at Both Levels

- ✅ **Task-level review:** Code quality, tests, security
- ✅ **Story-level review:** Complete feature, acceptance criteria

---

### 5. Use Memory for Persistent Facts

```bash
# Store team conventions
/lazy memory-graph "team:backend prefers:async-patterns"

# Store ownership
/lazy memory-graph "service:payment owned_by:alice"

# Store architecture decisions
/lazy memory-graph "repo:org/api uses:repository-pattern"
```

---

## Examples

### Example 1: Simple Feature (1 Task)

```bash
# Create feature
/lazy create-feature "Add API timeout configuration"

# Output:
# ✅ USER-STORY.md created
# ✅ TASK-1.1: Implement configurable timeout

# Execute task
/lazy task-exec TASK-1.1

# Output:
# ✅ TASK-1.1 committed (a1b2c3d4)

# Review story
/lazy story-review USER-STORY.md

# Output:
# ✅ PR created: https://github.com/org/repo/pull/42
```

---

### Example 2: Complex Feature (5 Tasks)

```bash
# Create feature
/lazy create-feature "Build user authentication system"

# Output:
# ✅ 5 tasks created (TASK-1.1 through TASK-1.5)

# Execute tasks sequentially
/lazy task-exec TASK-1.1 --with-research  # OAuth2 setup
/lazy task-exec TASK-1.2                  # JWT implementation
/lazy task-exec TASK-1.3                  # Session management
/lazy task-exec TASK-1.4                  # Auth middleware
/lazy task-exec TASK-1.5                  # RBAC

# Review complete story
/lazy story-review USER-STORY.md

# Output:
# ✅ PR created with 5 commits
```

---

### Example 3: Feature with Rework

```bash
# Create and execute
/lazy create-feature "Add data export"
/lazy task-exec TASK-1.1
/lazy task-exec TASK-1.2
/lazy task-exec TASK-1.3

# Review fails
/lazy story-review USER-STORY.md

# Output:
# ❌ CHANGES REQUIRED:
#    - Missing rate limiting
#    - No load test for large datasets

# Fix issues
/lazy task-exec TASK-1.3 --retry  # Add rate limiting
# (Manually add load test)

# Re-review
/lazy story-review USER-STORY.md

# Output:
# ✅ PR created
```

---

## Summary

### The LAZY_DEV Workflow

1. ✅ **Create Feature** → User story + tasks
2. ✅ **Execute Tasks** → TDD + quality + review + commit (no PR)
3. ✅ **Review Story** → All tasks together → PR
4. ✅ **Fix if Needed** → Iterate and re-review
5. ✅ **Merge** → Complete feature deployed

### Key Principles

- **Commit per task** - Atomic, reviewable commits
- **PR per story** - Cohesive, complete features
- **Quality mandatory** - Fail-fast pipeline blocks broken code
- **TDD required** - Tests before implementation
- **Context-based** - Agents extract from conversation
- **Memory-persistent** - Knowledge grows over time

---

**LAZY_DEV** - Be lazy, but consistently excellent.
