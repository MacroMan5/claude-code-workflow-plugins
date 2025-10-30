---
name: regression-testing
description: Evaluates and implements regression tests after bug fixes based on severity, code complexity, and coverage. Use when bugs are fixed to prevent future regressions.
---

# Regression Testing Skill

**Purpose**: Automatically evaluate and implement regression tests after bug fixes to prevent future regressions.

**When to Trigger**: This skill activates after bug fixes are implemented, allowing Claude (the orchestrator) to decide if regression tests would be valuable based on context.

---

## Decision Criteria (Orchestrator Evaluation)

Before implementing regression tests, evaluate these factors:

### High Value Scenarios (Implement Regression Tests)
- **Critical Bugs**: Security, data loss, or production-impacting issues
- **Subtle Bugs**: Edge cases, race conditions, timing issues that are easy to miss
- **Complex Logic**: Multi-step workflows, state machines, intricate business rules
- **Low Coverage Areas**: Bug occurred in under-tested code (<70% coverage)
- **Recurring Patterns**: Similar bugs fixed before in related code
- **Integration Points**: Bugs at module/service boundaries

### Lower Value Scenarios (Skip or Defer)
- **Trivial Fixes**: Typos, obvious logic errors with existing tests
- **Already Well-Tested**: Bug area has >90% coverage with comprehensive tests
- **One-Time Anomalies**: Environmental issues, config errors (not code bugs)
- **Rapid Prototyping**: Early-stage features expected to change significantly
- **UI-Only Changes**: Purely cosmetic fixes with no logic impact

---

## Regression Test Strategy

### 1. Bug Analysis Phase

**Understand the Bug:**
```markdown
## Bug Context
- **What broke**: [Symptom/error]
- **Root cause**: [Why it happened]
- **Fix applied**: [What changed]
- **Failure scenario**: [Steps to reproduce original bug]
```

**Evaluate Test Value:**
```python
def should_add_regression_test(bug_context: dict) -> tuple[bool, str]:
    """
    Decide if regression test is valuable.

    Returns:
        (add_test: bool, reason: str)
    """
    severity = bug_context.get("severity")  # critical, high, medium, low
    complexity = bug_context.get("complexity")  # high, medium, low
    coverage = bug_context.get("coverage_pct", 0)

    # Critical bugs always get regression tests
    if severity == "critical":
        return True, "Critical bug requires regression test"

    # Complex bugs with low coverage
    if complexity == "high" and coverage < 70:
        return True, "Complex logic with insufficient coverage"

    # Already well-tested
    if coverage > 90:
        return False, "Area already has comprehensive tests"

    # Default: add test for medium+ severity
    if severity in {"high", "medium"}:
        return True, f"Bug severity {severity} warrants regression test"

    return False, "Low-value regression test, skipping"
```

### 2. Regression Test Implementation

**Test Structure:**
```python
# test_<module>_regression.py

import pytest
from datetime import datetime

class TestRegressions:
    """Regression tests for fixed bugs."""

    def test_regression_issue_123_null_pointer_in_payment(self):
        """
        Regression test for GitHub issue #123.

        Bug: NullPointerException when processing payment with missing user email.
        Fixed: 2025-10-30
        Root cause: Missing null check in payment processor

        This test ensures the fix remains in place and prevents regression.
        """
        # Arrange: Setup scenario that caused original bug
        payment = Payment(amount=100.0, user=User(email=None))
        processor = PaymentProcessor()

        # Act: Execute the previously failing code path
        result = processor.process(payment)

        # Assert: Verify fix works (no exception, proper error handling)
        assert result.status == "failed"
        assert "invalid user email" in result.error_message.lower()

    def test_regression_pr_456_race_condition_in_cache(self):
        """
        Regression test for PR #456.

        Bug: Race condition in cache invalidation caused stale reads
        Fixed: 2025-10-30
        Root cause: Non-atomic read-modify-write operation

        This test simulates concurrent cache access to verify thread safety.
        """
        # Arrange: Setup concurrent scenario
        cache = ThreadSafeCache()
        cache.set("key", "value1")

        # Act: Simulate race condition with threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(cache.update, "key", f"value{i}")
                for i in range(100)
            ]
            wait(futures)

        # Assert: Verify no stale reads or corruption
        final_value = cache.get("key")
        assert final_value.startswith("value")
        assert cache.consistency_check()  # Internal consistency
```

**Test Naming Convention:**
- `test_regression_<issue_id>_<short_description>`
- Include issue/PR number for traceability
- Short description of what broke

**Test Documentation:**
- **Bug description**: What failed
- **Date fixed**: When fix was applied
- **Root cause**: Why it happened
- **Test purpose**: What regression is prevented

### 3. Regression Test Coverage

**What to Test:**
1. **Exact Failure Scenario**: Reproduce original bug conditions
2. **Edge Cases Around Fix**: Test boundaries near the bug
3. **Integration Impact**: Test how fix affects dependent code
4. **Performance**: If bug was performance-related, add benchmark

**What NOT to Test:**
- Don't duplicate existing unit tests
- Don't test obvious behavior already covered
- Don't over-specify implementation details (brittle tests)

---

## Workflow Integration

### Standard Bug Fix Flow

```bash
# 1. Fix the bug
/lazy code "fix: null pointer in payment processor"

# ✓ Bug fixed and committed

# 2. Regression testing skill evaluates
# (Automatic trigger after bug fix commit)

## Decision: Add regression test?
- Severity: HIGH (production crash)
- Coverage: 65% (medium)
- Complexity: MEDIUM
→ **YES, add regression test**

# 3. Implement regression test
# ✓ test_regression_issue_123_null_pointer_in_payment() added
# ✓ Coverage increased to 78%
# ✓ Test passes (bug is fixed)

# 4. Commit regression test
git add tests/test_payment_regression.py
git commit -m "test: add regression test for issue #123 null pointer"
```

### Quick Bug Fix (Skip Regression)

```bash
# 1. Fix trivial bug
/lazy code "fix: typo in error message"

# ✓ Bug fixed

# 2. Regression testing skill evaluates
## Decision: Add regression test?
- Severity: LOW (cosmetic)
- Coverage: 95% (excellent)
- Complexity: LOW (trivial)
→ **NO, skip regression test** (low value, already well-tested)

# 3. Commit fix only
# No additional test needed
```

---

## Regression Test Suite Management

### Organization

```
tests/
├── test_module.py              # Regular unit tests
├── test_module_integration.py  # Integration tests
└── test_module_regression.py   # Regression tests (this skill)
```

**Separate regression tests** to:
- Track historical bug fixes
- Easy to identify which tests prevent regressions
- Can be run as separate CI job for faster feedback

### CI/CD Integration

```yaml
# .github/workflows/ci.yml

jobs:
  regression-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run regression test suite
        run: pytest tests/*_regression.py -v --tb=short

      # Fast feedback: regression tests run first
      # If they fail, likely a regression occurred
```

### Regression Test Metrics

**Track Over Time:**
- Total regression tests count
- Bug recurrence rate (0% is goal)
- Coverage increase from regression tests
- Time to detect regression (should be in CI, not production)

---

## Examples

### Example 1: Critical Bug (Add Regression Test)

**Bug**: Authentication bypass when session token is malformed
**Fix**: Added token validation
**Decision**: ✅ **Add regression test** (security critical)

```python
def test_regression_issue_789_auth_bypass_malformed_token():
    """
    Regression test for security issue #789.

    Bug: Malformed session tokens bypassed authentication
    Fixed: 2025-10-30
    Severity: CRITICAL (security)
    Root cause: Missing token format validation
    """
    # Arrange: Malformed token that bypassed auth
    malformed_token = "invalid||format||token"

    # Act: Attempt authentication
    result = AuthService.validate_token(malformed_token)

    # Assert: Should reject malformed token
    assert result.is_valid is False
    assert result.error == "invalid_token_format"
```

### Example 2: Complex Bug (Add Regression Test)

**Bug**: Race condition in distributed lock causes duplicate job execution
**Fix**: Atomic compare-and-swap operation
**Decision**: ✅ **Add regression test** (complex concurrency issue)

```python
def test_regression_pr_234_race_condition_duplicate_jobs():
    """
    Regression test for PR #234.

    Bug: Race condition allowed duplicate job execution
    Fixed: 2025-10-30
    Complexity: HIGH (concurrency)
    Root cause: Non-atomic lock acquisition
    """
    # Arrange: Simulate concurrent job submissions
    job_queue = DistributedJobQueue()
    job_id = "test-job-123"

    # Act: 100 threads try to acquire same job
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [
            executor.submit(job_queue.try_acquire_job, job_id)
            for _ in range(100)
        ]
        results = [f.result() for f in futures]

    # Assert: Only ONE thread should acquire the job
    acquired = [r for r in results if r.acquired]
    assert len(acquired) == 1, "Race condition: multiple threads acquired same job"
```

### Example 3: Trivial Bug (Skip Regression Test)

**Bug**: Typo in log message "Usre authenticated" → "User authenticated"
**Fix**: Corrected spelling
**Decision**: ❌ **Skip regression test** (cosmetic, no logic impact)

```
No test needed. Fix is obvious and has no functional impact.
Existing tests already cover authentication logic.
```

### Example 4: Well-Tested Area (Skip Regression Test)

**Bug**: Off-by-one error in pagination (page 1 showed 0 results)
**Fix**: Changed `offset = page * size` to `offset = (page - 1) * size`
**Coverage**: 95% (pagination thoroughly tested)
**Decision**: ❌ **Skip regression test** (area already has comprehensive tests)

```python
# Existing test already covers this:
def test_pagination_first_page_shows_results():
    results = api.get_users(page=1, size=10)
    assert len(results) == 10  # This test would have caught the bug
```

---

## Best Practices

### DO:
✅ Add regression tests for **critical and complex bugs**
✅ Include **issue/PR number** in test name for traceability
✅ Document **what broke, why, and when** in test docstring
✅ Test the **exact failure scenario** that caused the bug
✅ Keep regression tests **separate** from unit tests (easier tracking)
✅ Run regression tests in **CI/CD** for early detection

### DON'T:
❌ Add regression tests for **trivial or cosmetic bugs**
❌ Duplicate **existing comprehensive tests**
❌ Write **brittle tests** that test implementation details
❌ Skip **root cause analysis** (understand why it broke)
❌ Forget to **verify test fails** before fix (should reproduce bug)

---

## Output Format

When this skill triggers, provide:

```markdown
## Regression Test Evaluation

**Bug Fixed**: [Brief description]
**Issue/PR**: #[number]
**Severity**: [critical/high/medium/low]
**Complexity**: [high/medium/low]
**Current Coverage**: [X%]

**Decision**: [✅ Add Regression Test | ❌ Skip Regression Test]

**Reason**: [Why regression test is/isn't valuable]

---

[If adding test]
## Regression Test Implementation

**File**: `tests/test_<module>_regression.py`

```python
def test_regression_<issue>_<description>():
    """
    [Docstring with bug context]
    """
    # Test implementation
```

**Coverage Impact**: +X% (before: Y%, after: Z%)
```

---

## Integration with Other Skills

- **Works with**: `test-driven-development` (adds tests post-fix)
- **Complements**: `code-review-request` (reviewer checks for regression tests)
- **Used by**: `/lazy fix` command (auto-evaluates regression test need)

---

## Configuration

**Environment Variables:**
```bash
# Force regression tests for all bugs (strict mode)
export LAZYDEV_FORCE_REGRESSION_TESTS=1

# Disable regression test skill
export LAZYDEV_DISABLE_REGRESSION_SKILL=1

# Minimum coverage threshold to skip regression test (default: 90)
export LAZYDEV_REGRESSION_SKIP_COVERAGE_THRESHOLD=90
```

---

**Version**: 1.0.0
**Created**: 2025-10-30
**Anthropic Best Practice**: Model-invoked, autonomous trigger after bug fixes
