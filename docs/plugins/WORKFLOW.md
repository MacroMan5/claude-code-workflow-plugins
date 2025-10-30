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
8. [Review Failure Scenario: Debug Report and Fix](#review-failure-scenario-debug-report-and-fix)
9. [Best Practices](#best-practices)
10. [Examples](#examples)

---

## Workflow Overview

LAZY_DEV implements a structured workflow that ensures:
- ✅ Consistent quality through mandatory pipeline
- ✅ Clear git history with atomic commits
- ✅ Cohesive PRs that represent complete features
- ✅ Automatic delegation to specialized agents
- ✅ Persistent knowledge across sessions
- ✅ Structured debugging with report-driven fixes

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
                                      Report → Fix → Re-review
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
/lazy plan "Add payment processing with Stripe"
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
/lazy code TASK-1.1
# Or: /lazy code @US-3.4.md  (implements next pending task)
# Or: /lazy code "quick feature brief"
# Or: /lazy code #456  (from GitHub issue)
```

**Workflow Steps:**

#### Step 1: Auto-Detection & Context Loading
```
✓ Detects input type (task ID, story file, brief, or issue)
✓ Loads story context automatically (if task ID provided)
✓ Analyzes complexity (simple vs complex)
✓ Determines if tests needed (checks project config)
✓ Determines if review needed (based on complexity)
```

#### Step 2: Git Branch Setup
- Creates or checks out feature branch (if working from story)
- Uses current branch for quick tasks/briefs

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
/lazy code TASK-1.2
# → Commit b5c6d7e8

/lazy code TASK-1.3
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
/lazy review USER-STORY.md
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

**If CHANGES_REQUIRED:**
```
❌ Story review: CHANGES_REQUIRED

Generated: US-3.4-review-report.md

Report contains:
- Summary of issues
- Per-issue details
- Per-task status
- Next steps

Run: /lazy fix US-3.4-review-report.md
```

---

### Phase 5: Review Failure, Debug Report, and Fixes

**Scenario:** Story review finds issues that need fixing using the new debug report feature.

#### Step 1: Initial Review Fails

```bash
/lazy review US-3.4
```

**Output:**
```
❌ CHANGES_REQUIRED

Generated Debug Report: US-3.4-review-report.md

Issues Summary:
- 2 CRITICAL issues
- 3 WARNING issues
- 1 SUGGESTION issue
```

#### Step 2: Read the Debug Report

**File: US-3.4-review-report.md**

```markdown
# US-3.4 Review Report

## Summary
Story review incomplete - 2 CRITICAL, 3 WARNING, 1 SUGGESTION issues found.

Review Date: 2025-10-30
Story: US-3.4 Add Payment Processing
Commits: 3 (all completed)

## Issues

### CRITICAL (Must fix before PR)

1. Missing input validation
   File: src/auth/oauth.py
   Line: 45
   Description: Payment amount not validated for negative values
   Fix: Add validation to reject amounts <= 0
   Estimated Time: 15 minutes

2. Test coverage below threshold
   File: tests/test_payment.py
   Current: 65%
   Required: >80%
   Description: Missing edge case tests
   Fix: Add tests for invalid amounts, network failures
   Estimated Time: 30 minutes

### WARNING (Should fix)

1. Missing docstrings
   File: src/payment_processor.py
   Lines: 23, 45, 67
   Description: Public methods lack documentation
   Fix: Add Google-style docstrings
   Estimated Time: 10 minutes

2. No rate limiting
   File: src/payment_api.py
   Description: Payment endpoint has no rate limiting
   Fix: Add middleware for rate limiting (10 req/min per user)
   Estimated Time: 20 minutes

3. Incomplete error handling
   File: src/stripe_client.py
   Lines: 78-95
   Description: Network errors not properly caught
   Fix: Add try-catch for timeout errors
   Estimated Time: 15 minutes

### SUGGESTION (Nice to have)

1. Refactor duplicate code
   File: src/payment_processor.py
   Lines: 34, 56
   Description: Same validation logic duplicated twice
   Fix: Extract to shared _validate_payment() method
   Estimated Time: 10 minutes

## Task Status

- TASK-3.4.1: COMPLETE
  Commit: a1b2c3d4
  Coverage: 95%
  Status: Committed

- TASK-3.4.2: COMPLETE
  Commit: b5c6d7e8
  Coverage: 88%
  Status: Committed

- TASK-3.4.3: COMPLETE
  Commit: f9g0h1i2
  Coverage: 72% (BELOW THRESHOLD)
  Status: Committed

## Next Steps

1. Fix CRITICAL issues immediately:
   ```bash
   /lazy fix US-3.4-review-report.md
   ```

2. This will:
   - Route issues to appropriate agents
   - Add missing validation code
   - Add missing tests
   - Improve coverage to >80%

3. Re-run story review:
   ```bash
   /lazy review US-3.4
   ```

4. If still issues, repeat steps 2-3

## Estimated Total Fix Time
- CRITICAL: 45 minutes
- WARNING: 55 minutes
- SUGGESTION: 10 minutes
- Total: ~2 hours (with re-review)

---

Generated by LAZY-DEV-FRAMEWORK v2.2.0
Report Format: Machine-readable for `/lazy fix` command
```

#### Step 3: Understanding the Report

The debug report provides:

**Machine-Readable Format:**
- Clear severity levels (CRITICAL/WARNING/SUGGESTION)
- File paths and line numbers
- Specific descriptions of each issue
- Estimated fix time
- Per-task completion status

**Actionable Structure:**
- Issues organized by severity
- Clear next steps
- Integration with `/lazy fix` command

**Status Information:**
- Which tasks are complete
- Coverage statistics
- Quality metrics

#### Step 4: Apply Fixes Automatically

```bash
/lazy fix US-3.4-review-report.md
```

**What Happens:**

1. **Parse Report:**
   - Identifies all issues
   - Groups by severity

2. **Route to Agents:**
   - CRITICAL security issues → Coder agent
   - Coverage gaps → Tester agent
   - Documentation → Documentation agent
   - Code quality → Refactor agent

3. **Apply Fixes:**
   ```bash
   # Coder agent adds validation
   # File: src/auth/oauth.py
   if amount <= 0:
       raise ValueError("Amount must be positive")

   # Tester agent adds missing tests
   # File: tests/test_payment.py
   def test_invalid_amount():
       with pytest.raises(ValueError):
           process_payment(-10)

   # Documentation agent adds docstrings
   # File: src/payment_processor.py
   def process_payment(amount: int) -> dict:
       """Process payment.

       Args:
           amount: Payment amount in cents

       Returns:
           Payment result
       """
   ```

4. **Quality Pipeline:**
   - Format code automatically
   - Run linter
   - Run type checker
   - Run tests

5. **Coverage Improvement:**
   - Tests now at 85% (above 80% threshold)
   - All CRITICAL issues fixed

6. **Commits:**
   - New commits with fixes
   - Commits added to feature branch

**Output:**
```
✅ Fixes applied:
   - Added input validation (1 commit)
   - Added missing tests (1 commit)
   - Added docstrings (1 commit)
   - Added rate limiting (1 commit)

✅ Quality checks:
   - Format: PASS
   - Lint: PASS
   - Type: PASS
   - Test: PASS (Coverage: 85%)

✅ Ready for re-review
   Run: /lazy review US-3.4
```

#### Step 5: Re-Review After Fixes

```bash
/lazy review US-3.4
```

**Output:**
```
✅ APPROVED

All issues resolved:
- CRITICAL: 2/2 fixed
- WARNING: 3/3 fixed
- SUGGESTION: 1/1 addressed

Creating PR...

✅ PR created: https://github.com/org/repo/pull/123
   All GitHub issues closed automatically
```

#### Complete Failure → Report → Fix → Re-Review Cycle

```
Initial Review
    ↓
/lazy review US-3.4
    ↓
❌ CHANGES_REQUIRED
    ↓
US-3.4-review-report.md generated
    ↓
Read report (2 CRITICAL, 3 WARNING)
    ↓
Apply fixes
    ↓
/lazy fix US-3.4-review-report.md
    ↓
✓ Routes to coder (validation)
✓ Routes to tester (coverage)
✓ Routes to documentation (docstrings)
    ↓
Quality pipeline runs
    ↓
Coverage: 65% → 85% (PASS)
    ↓
Re-Review
    ↓
/lazy review US-3.4
    ↓
✅ APPROVED
    ↓
PR created (#123)
```

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
User: /lazy code TASK-1.1
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
/lazy code TASK-1.1  # → commit a1b2c3d4
/lazy code TASK-1.2  # → commit b5c6d7e8
/lazy code TASK-1.3  # → commit f9g0h1i2

# Story review creates PR from branch
/lazy review USER-STORY.md
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
/lazy code TASK-1.1 --retry-from=test
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
/lazy code TASK-1.1 --retry-from=review
```

---

### Story Review Failure

**Scenario:** Story incomplete with debug report generated

```
❌ Story review: CHANGES_REQUIRED

Generated: US-3.4-review-report.md

Issues found:
- 2 CRITICAL
- 3 WARNING
- 1 SUGGESTION

Next Steps:
1. Read: cat US-3.4-review-report.md
2. Apply: /lazy fix US-3.4-review-report.md
3. Re-review: /lazy review US-3.4
```

**Recovery:**
```bash
# Review the debug report
cat US-3.4-review-report.md

# Apply fixes automatically
/lazy fix US-3.4-review-report.md

# Fixes are applied and committed
# Quality pipeline runs automatically

# Re-review
/lazy review US-3.4

# Should now be APPROVED
```

---

## Review Failure Scenario: Debug Report and Fix

**Complete Example: From Failure to PR**

### Initial State

Story has 3 tasks, all committed:
- TASK-3.4.1: Setup Stripe API (95% coverage)
- TASK-3.4.2: Implement processing (88% coverage)
- TASK-3.4.3: Add validation (72% coverage) ← Below threshold

### Step 1: Review Fails

```bash
$ /lazy review US-3.4

❌ CHANGES_REQUIRED

Generated: US-3.4-review-report.md
```

### Step 2: Examine Report

```bash
$ cat US-3.4-review-report.md

# US-3.4 Review Report

## Summary
Story review incomplete - 2 CRITICAL, 3 WARNING, 1 SUGGESTION

## Issues

### CRITICAL
1. Missing input validation
   File: src/auth/oauth.py:45
   Fix: Add amount validation
   Estimated Time: 15 minutes

2. Test coverage 65% (required >80%)
   File: tests/test_payment.py
   Fix: Add edge case tests
   Estimated Time: 30 minutes

### WARNING
1. Missing docstrings
   File: src/payment_processor.py
   Lines: 23, 45, 67
   Estimated Time: 10 minutes

2. No rate limiting
   File: src/payment_api.py
   Estimated Time: 20 minutes

3. Incomplete error handling
   File: src/stripe_client.py
   Lines: 78-95
   Estimated Time: 15 minutes

### SUGGESTION
1. Refactor duplicate code
   Estimated Time: 10 minutes

## Task Status
- TASK-3.4.1: COMPLETE (95% coverage)
- TASK-3.4.2: COMPLETE (88% coverage)
- TASK-3.4.3: COMPLETE (72% coverage - BELOW THRESHOLD)

## Next Steps
1. /lazy fix US-3.4-review-report.md
2. Wait for fixes to apply
3. /lazy review US-3.4
```

### Step 3: Apply Fixes

```bash
$ /lazy fix US-3.4-review-report.md

Processing issues...

✓ Routing CRITICAL issues to coder agent
  - Adding validation to oauth.py

✓ Routing coverage gap to tester agent
  - Adding edge case tests

✓ Routing documentation to documentation agent
  - Adding docstrings

✓ Routing quality issues to refactor agent
  - Adding rate limiting
  - Improving error handling
  - Extracting duplicate code

Running quality pipeline...

✓ Format: PASS
✓ Lint: PASS
✓ Type: PASS
✓ Test: PASS (Coverage: 85%)

Creating commits...

✓ commit 1: fix: add input validation to payment processing
✓ commit 2: test: add edge case tests for payment validation
✓ commit 3: docs: add docstrings to payment processor
✓ commit 4: perf: add rate limiting to payment API
✓ commit 5: fix: improve stripe client error handling

Ready for re-review!
```

### Step 4: Re-Review

```bash
$ /lazy review US-3.4

Reviewing story...

✓ All CRITICAL issues fixed (2/2)
✓ All WARNING issues fixed (3/3)
✓ SUGGESTION addressed (1/1)
✓ All tests passing
✓ Coverage: 85% (above 80%)
✓ Quality checks: ALL PASS

✅ APPROVED

Creating PR...

✅ PR created: https://github.com/org/repo/pull/123
   Title: [FEATURE] Add Payment Processing
   Branch: feature/payment-processing → main

All GitHub issues closed automatically.
```

### Git History After Fixes

```
* g2h3i4j5 fix: improve stripe client error handling
* f1g2h3i4 perf: add rate limiting to payment API
* e0f1g2h3 docs: add docstrings to payment processor
* d9e0f1g2 test: add edge case tests for payment validation
* c8d9e0f1 fix: add input validation to payment processing
* f9g0h1i2 feat(payment): add validation (original TASK-3.4.3)
* b5c6d7e8 feat(payment): implement payment processing (original TASK-3.4.2)
* a1b2c3d4 feat(payment): setup Stripe API integration (original TASK-3.4.1)
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

### 6. Read Debug Reports Thoroughly

```bash
# When review fails
/lazy review US-3.4
# → Check if US-{ID}-review-report.md generated

# Read the entire report
cat US-{ID}-review-report.md
# → Understand all issues before fixing

# Fix strategically
# → CRITICAL first (blocks PR)
# → Then WARNING (should fix)
# → Then SUGGESTION (nice to have)
```

---

## Examples

### Example 1: Simple Feature (1 Task)

```bash
# Create feature
/lazy plan "Add API timeout configuration"

# Output:
# ✅ USER-STORY.md created
# ✅ TASK-1.1: Implement configurable timeout

# Execute task
/lazy code TASK-1.1

# Output:
# ✅ TASK-1.1 committed (a1b2c3d4)

# Review story
/lazy review USER-STORY.md

# Output:
# ✅ PR created: https://github.com/org/repo/pull/42
```

---

### Example 2: Complex Feature (5 Tasks)

```bash
# Create feature
/lazy plan "Build user authentication system"

# Output:
# ✅ 5 tasks created (TASK-1.1 through TASK-1.5)

# Execute tasks sequentially
/lazy code TASK-1.1 --with-research  # OAuth2 setup
/lazy code TASK-1.2                  # JWT implementation
/lazy code TASK-1.3                  # Session management
/lazy code TASK-1.4                  # Auth middleware
/lazy code TASK-1.5                  # RBAC

# Review complete story
/lazy review USER-STORY.md

# Output:
# ✅ PR created with 5 commits
```

---

### Example 3: Feature with Rework (Using Debug Report)

```bash
# Create and execute
/lazy plan "Add data export"
/lazy code TASK-1.1
/lazy code TASK-1.2
/lazy code TASK-1.3

# Review fails with debug report
/lazy review USER-STORY.md

# Output:
# ❌ CHANGES_REQUIRED
# Generated: US-3.4-review-report.md
# Issues: 2 CRITICAL, 1 WARNING

# Read report
cat US-3.4-review-report.md
# Shows: Missing rate limiting, Test coverage 65%

# Apply fixes automatically
/lazy fix US-3.4-review-report.md

# Output:
# ✓ Added rate limiting
# ✓ Added missing tests (coverage now 85%)
# ✓ Quality checks: PASS

# Re-review
/lazy review USER-STORY.md

# Output:
# ✅ APPROVED
# ✅ PR created
```

---

## Summary

### The LAZY_DEV Workflow

1. ✅ **Create Feature** → User story + tasks
2. ✅ **Execute Tasks** → TDD + quality + review + commit (no PR)
3. ✅ **Review Story** → All tasks together → PR or debug report
4. ✅ **Fix if Needed** → Read report → Apply fixes → Re-review
5. ✅ **Merge** → Complete feature deployed

### Key Principles

- **Commit per task** - Atomic, reviewable commits
- **PR per story** - Cohesive, complete features
- **Quality mandatory** - Fail-fast pipeline blocks broken code
- **TDD required** - Tests before implementation
- **Context-based** - Agents extract from conversation
- **Memory-persistent** - Knowledge grows over time
- **Report-driven fixes** - Machine-readable debug reports guide fixes

### New in v2.2.0

- **Debug reports on review failure** - Structured `US-{ID}-review-report.md`
- **Per-issue details** - File paths, line numbers, fix descriptions
- **Per-task status** - See which tasks contributed to failures
- **Automatic fix routing** - `/lazy fix` routes to appropriate agents
- **Clear next steps** - Report tells you exactly what to do next

---

**LAZY_DEV** - Be lazy, but consistently excellent.
