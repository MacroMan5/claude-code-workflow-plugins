# LAZY-DEV-FRAMEWORK Hooks Audit Checklist

## Quick Reference for Developers

---

## Critical Security Fixes (MUST DO)

- [ ] **API Key Exposure** - `pre_prompt_enrichment.py`
  - Remove API key from f-strings
  - Use Template.substitute() instead
  - Test: Verify key doesn't appear in logs

- [ ] **Regex Overmatch** - `pre_tool_use.py`
  - Replace `r'(?i)token'` with specific patterns
  - Replace `r'(?i)secret'` with specific patterns
  - Test: Verify legitimate code not blocked

- [ ] **Command Injection** - `pre_tool_use.py`
  - Add detection: `sh -c`, `bash -c`, `eval`, `$(...)`, backticks
  - Add detection: `| sh`, `| bash` pipes
  - Test: Verify injection attempts blocked

- [ ] **Path Traversal** - `session_start.py`, `stop.py`
  - Validate session_id format: `^[a-zA-Z0-9_-]{1,64}$`
  - Validate transcript_path within `.claude/data/`
  - Test: Verify `../../../etc/passwd` blocked

- [ ] **Log Secret Exposure** - `log_events.py`
  - Sanitize commands before logging
  - Redact API keys, tokens, passwords
  - Test: Verify secrets not in logs

---

## High Priority Code Quality (SHOULD DO - Week 1)

- [ ] **Remove Duplicate Imports**
  - [ ] `session_start.py` (line 22)
  - [ ] `user_prompt_submit.py` (line 32)
  - [ ] `pre_tool_use.py` (line 21)
  - [ ] `post_tool_use_format.py` (line 21)
  - [ ] `stop.py` (line 21)

- [ ] **Fix Duplicate Return** - `user_prompt_submit.py` (line 278)
  - Remove duplicate return statement

- [ ] **Move Regex Patterns to Module Level**
  - [ ] `pre_tool_use.py`: Compile patterns once
  - [ ] `user_prompt_submit.py`: Compile patterns once
  - [ ] `stop.py`: Compile patterns once
  - Performance improvement: 10-100x faster

- [ ] **Add Logging** (Replace silent `except` blocks)
  - [ ] `session_start.py`: Add logger for failures
  - [ ] `user_prompt_submit.py`: Add logger for git/task failures
  - [ ] `pre_tool_use.py`: Add logger for blocked commands
  - [ ] `post_tool_use_format.py`: Add logger for format failures
  - [ ] `stop.py`: Add logger for parse errors
  - [ ] All hooks: Use `logging` module consistently

---

## Medium Priority Performance (SHOULD DO - Week 2)

- [ ] **Reduce Subprocess Timeouts** - `post_tool_use_format.py`
  - Change from 10s to 3-5s maximum
  - Test: Verify formatting still works

- [ ] **Implement Log Rotation** - All logging hooks
  - Add max file size limit (100MB)
  - Add backup count (5 files)
  - Test: Verify old logs archived

- [ ] **Add Caching** - `pre_prompt_enrichment.py`
  - Cache enrichment results by prompt hash
  - Reduce API calls
  - Test: Verify repeated prompts don't re-enrich

- [ ] **Optimize Context Pack** - `user_prompt_submit.py`
  - Respect .gitignore patterns
  - Limit walk with better heuristics
  - Test: Verify no slowdown on large repos

---

## Configuration & Documentation (NICE TO HAVE - Week 3)

- [ ] **Document Environment Variables**
  - [ ] Create `HOOKS_CONFIG.md`
  - [ ] List all LAZYDEV_* variables
  - [ ] Include defaults and examples

- [ ] **Fix Hook Execution Order** - `settings.json`
  - Log BEFORE security checks
  - Document hook dependencies
  - Test: Verify proper execution order

- [ ] **Add Configuration Validation**
  - [ ] Validate ANTHROPIC_API_KEY format (not content)
  - [ ] Validate required env vars at startup
  - [ ] Warn on deprecated configurations

- [ ] **Create Troubleshooting Guide**
  - [ ] Common hook failures
  - [ ] How to debug issues
  - [ ] Performance tuning tips

---

## Testing Requirements

### Unit Tests (Each Hook)
- [ ] `session_start.py`
  - [ ] Test PRD loading
  - [ ] Test TASKS loading
  - [ ] Test git history retrieval
  - [ ] Test session state file creation

- [ ] `user_prompt_submit.py`
  - [ ] Test git context detection
  - [ ] Test task detection
  - [ ] Test style selection (multiple prompt types)
  - [ ] Test context pack generation
  - [ ] Test memory intent detection

- [ ] `pre_prompt_enrichment.py`
  - [ ] Test with valid API key
  - [ ] Test with missing API key (should skip gracefully)
  - [ ] Test enrichment result
  - [ ] Test logging

- [ ] `pre_tool_use.py`
  - [ ] Test rm command detection (various forms)
  - [ ] Test force push detection
  - [ ] Test sensitive file detection
  - [ ] Test new command injection patterns
  - [ ] Test path validation

- [ ] `post_tool_use_format.py`
  - [ ] Test Python formatting
  - [ ] Test JavaScript formatting
  - [ ] Test Rust formatting
  - [ ] Test unsupported file types

- [ ] `log_events.py`
  - [ ] Test JSONL writing
  - [ ] Test master log
  - [ ] Test session directory creation
  - [ ] Test sanitization

- [ ] `stop.py`
  - [ ] Test test detection
  - [ ] Test failure detection
  - [ ] Test pass/fail output
  - [ ] Test blocking behavior

### Integration Tests
- [ ] Full hook chain execution
- [ ] Error propagation
- [ ] Log file creation
- [ ] Concurrent execution

### Security Tests
- [ ] Path traversal attempts (various forms)
- [ ] Command injection attempts
- [ ] Secret exposure in logs
- [ ] API key in error messages

### Performance Tests
- [ ] Large directory trees (10k+ files)
- [ ] Large log files (1GB+)
- [ ] Regex performance on long commands
- [ ] Concurrent hook execution

---

## Files to Audit/Update

### Current Hook Files
- [x] `session_start.py` - 246 lines
- [x] `user_prompt_submit.py` - 555 lines
- [x] `pre_prompt_enrichment.py` - 225 lines
- [x] `pre_tool_use.py` - 280 lines
- [x] `post_tool_use_format.py` - 290 lines
- [x] `log_events.py` - 176 lines
- [x] `memory_router.py` - 64 lines
- [x] `memory_suggestions.py` - 70 lines
- [x] `stop.py` - 282 lines

### Configuration Files
- [x] `.claude/settings.json` - Lines 44-132 (hooks configuration)

### Documentation Files
- [ ] Create `HOOKS_CONFIG.md`
- [ ] Create `HOOKS_TROUBLESHOOTING.md`
- [ ] Update `CLAUDE.md` with hook documentation
- [ ] Create `.claude/HOOKS_README.md`

---

## Audit Results Summary

| Category | Status | Issues Found |
|----------|--------|--------------|
| Security | REVIEW | 9 issues (4 critical) |
| Performance | REVIEW | 6 issues |
| Error Handling | NEEDS WORK | 5 issues |
| Code Quality | NEEDS WORK | 8 issues |
| Documentation | NEEDS IMPROVEMENT | 5 gaps |
| Testing | NOT STARTED | 0 tests found |

---

## Implementation Timeline

### Week 1: Security & Critical Fixes
- Days 1-2: API key, regex, path validation fixes
- Days 3-4: Command injection detection, log sanitization
- Days 4-5: Code cleanup (imports, returns)

### Week 2: Code Quality & Performance
- Days 1-2: Add logging throughout
- Days 3-4: Move regex patterns, reduce timeouts
- Days 4-5: Implement log rotation

### Week 3: Configuration & Testing
- Days 1-2: Write unit tests for each hook
- Days 3: Write integration tests
- Days 4: Documentation and troubleshooting guide
- Days 5: Performance and security tests

### Week 4: Documentation & Cleanup
- Days 1-2: API documentation
- Days 3-4: Create configuration guide
- Days 5: Final review and cleanup

---

## Sign-Off Checklist

Before marking audit as complete:

- [ ] All critical security issues documented
- [ ] High priority items prioritized
- [ ] Code examples provided for each fix
- [ ] Testing requirements specified
- [ ] Implementation timeline created
- [ ] File paths documented
- [ ] Next steps clear
- [ ] Team notified of findings
- [ ] Issues created in tracker
- [ ] Audit report signed off

---

## Resources

### Audit Documents
- Detailed Report: `/LAZY_DEV/.claude/HOOKS_AUDIT_REPORT.json`
- Summary: `/LAZY_DEV/.claude/AUDIT_SUMMARY.md`
- Code Examples: `/LAZY_DEV/.claude/HOOKS_FIX_EXAMPLES.md`
- This Checklist: `/LAZY_DEV/.claude/HOOKS_CHECKLIST.md`

### Reference Documentation
- Framework Guide: `/CLAUDE.md`
- Implementation Plan: `/IMPLEMENTATION-PLAN.md`
- PRD: `/PRD.md`

### Related Directories
- Hooks: `/LAZY_DEV/.claude/hooks/`
- Scripts: `/LAZY_DEV/scripts/`
- Reference Projects: `/@PROJECT_INSPIRATION/`

---

## Quick Commands

```bash
# Check hook syntax
python -m py_compile .claude/hooks/*.py

# Run linter
ruff check .claude/hooks/

# Check types
mypy .claude/hooks/

# Run tests (when created)
pytest tests/hooks/

# Audit trail
tail -f .claude/data/logs/all_events.jsonl

# Check log sizes
du -sh .claude/data/logs/*
```

---

**Audit Date**: 2025-10-29
**Status**: Ready for Implementation
**Next Review**: After Phase 1 completion

