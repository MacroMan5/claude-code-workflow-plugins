# LAZY_DEV Plugin - Implementation Checklist

**Last Updated:** 2025-10-29
**Status Tracking:** [Complete ✅] [In Progress ⏳] [Pending ⏱️]

---

## Phase 1: CRITICAL SECURITY FIXES (Week 1)

### Priority 1: Immediate (Days 1-2) - 8 hours

- [x] ✅ **Add directory scanning prevention** (pre_tool_use.py)
  - **Status:** COMPLETED 2025-10-29
  - **File:** `LAZY_DEV/.claude/hooks/pre_tool_use.py:171-260`
  - **Blocks:** node_modules, .git, __pycache__, dist, build, .venv, .next, .cache
  - **Impact:** Prevents 90% of performance issues

- [ ] ⏱️ **Fix API key exposure** (pre_prompt_enrichment.py:46)
  - **Task:** Sanitize api_key in f-strings and error messages
  - **Time:** 2 hours
  - **File:** `LAZY_DEV/.claude/hooks/pre_prompt_enrichment.py`
  - **Code:**
    ```python
    # Add at top of enrich_prompt function
    sanitized_key = api_key[:8] + "..." if api_key else "missing"
    # Use sanitized_key in any error messages or logs
    ```

- [ ] ⏱️ **Fix regex overmatch** (pre_tool_use.py:161)
  - **Task:** Make 'token' pattern more specific
  - **Time:** 1 hour
  - **File:** `LAZY_DEV/.claude/hooks/pre_tool_use.py`
  - **Code:**
    ```python
    # REPLACE line 161
    generic = [
        r'\.(pem|key|pfx|p12)\b',
        r'(?i)(api[_-]?key|access[_-]?token|secret[_-]?key)\s*=',
    ]
    ```

- [ ] ⏱️ **Add command injection detection** (pre_tool_use.py)
  - **Task:** Create is_command_injection() function
  - **Time:** 3 hours
  - **Insert after:** Line 260 (after is_directory_scan_blocked)
  - **Code:**
    ```python
    def is_command_injection(command: str) -> bool:
        """Detect command injection patterns."""
        patterns = [
            r'\beval\s+', r'\bexec\s+',
            r'sh\s+-c', r'bash\s+-c',
            r'\$\(', r'`[^`]+`',
        ]
        return any(re.search(pattern, command) for pattern in patterns)
    ```
  - **Integration:** Add check in main() after line 366

- [ ] ⏱️ **Sanitize logs** (log_events.py)
  - **Task:** Remove secrets from logged commands
  - **Time:** 2 hours
  - **File:** `LAZY_DEV/.claude/hooks/log_events.py`

### Priority 2: Critical (Days 3-5) - 9 hours

- [ ] ⏱️ **Add system directory protection** (settings.json)
  - **Task:** Add deny rules for /sys, /proc, /dev, /var, /usr
  - **Time:** 2 hours
  - **File:** `LAZY_DEV/.claude/settings.json:26-37`
  - **Add to deny list:**
    ```json
    "Bash(find:.*/sys/*)",
    "Bash(find:.*/proc/*)",
    "Bash(find:.*/dev/*)",
    "Bash(rm:-rf:/var)",
    "Bash(rm:-rf:/usr)",
    "Bash(rm:-rf:/home)"
    ```

- [ ] ⏱️ **Add dangerous find flag detection** (pre_tool_use.py)
  - **Task:** Block find -exec, find -delete
  - **Time:** 2 hours
  - **New function:** is_dangerous_find_flags()

- [ ] ⏱️ **Add code injection pattern detection** (pre_tool_use.py)
  - **Task:** Block python -c eval, node eval
  - **Time:** 2 hours
  - **New function:** is_code_injection_pattern()

- [ ] ⏱️ **Fix model inconsistency** (story-fix-review.md)
  - **Task:** Change Sonnet to Haiku
  - **Time:** 1 hour
  - **File:** `LAZY_DEV/.claude/commands/story-fix-review.md`
  - **Find and replace:** `claude-sonnet-*` → `claude-haiku-4-5-20251001`

- [ ] ⏱️ **Remove duplicate imports** (5 files)
  - **Task:** Remove duplicate `import os`
  - **Time:** 30 minutes
  - **Files:** session_start.py, user_prompt_submit.py, pre_tool_use.py, post_tool_use_format.py, stop.py
  - **Fix:** Delete one of the duplicate `import os` lines (lines 20-21)

- [ ] ⏱️ **Fix duplicate return** (user_prompt_submit.py:277-278)
  - **Task:** Remove duplicate return statement
  - **Time:** 10 minutes
  - **File:** `LAZY_DEV/.claude/hooks/user_prompt_submit.py`

---

## Phase 2: PERFORMANCE OPTIMIZATION (Week 2)

### Code Quality - 18 hours

- [ ] ⏱️ **Compile regex patterns at module level** (all hooks)
  - **Task:** Move patterns to module level, use re.compile()
  - **Time:** 6 hours
  - **Impact:** 10-100x faster regex matching
  - **Files:** pre_tool_use.py, user_prompt_submit.py, post_tool_use_format.py
  - **Pattern:**
    ```python
    # At module level
    DANGEROUS_RM_PATTERN = re.compile(r'\brm\s+.*-[a-z]*r[a-z]*f')

    # In function
    if DANGEROUS_RM_PATTERN.search(normalized):
        return True
    ```

- [ ] ⏱️ **Implement API response caching** (pre_prompt_enrichment.py)
  - **Task:** Add LRU cache for enrichment results
  - **Time:** 8 hours
  - **File:** `LAZY_DEV/.claude/hooks/pre_prompt_enrichment.py`
  - **Strategy:** Cache enriched prompts with 15-min TTL

- [ ] ⏱️ **Reduce subprocess timeouts** (multiple hooks)
  - **Task:** Change 10s timeouts to 3-5s
  - **Time:** 1 hour
  - **Files:** Search for `timeout=10` in all hooks

- [ ] ⏱️ **Add log rotation** (log_events.py, pre_tool_use.py)
  - **Task:** Implement max file size (10MB) and rotation
  - **Time:** 4 hours
  - **Strategy:** Use Python logging.handlers.RotatingFileHandler

### Commands - 13 hours

- [ ] ⏱️ **Expand documentation.md command**
  - **Task:** Add full workflow or document skill locations
  - **Time:** 8 hours
  - **File:** `LAZY_DEV/.claude/commands/documentation.md`
  - **Verify:** Skill files exist, add error handling

- [ ] ⏱️ **Create central sub-agent definitions**
  - **Task:** Create `LAZY_DEV/SUB_AGENTS.md` with all agent specs
  - **Time:** 5 hours
  - **Include:** Input/output formats, variable names, examples

---

## Phase 3: PERMISSIONS HARDENING (Week 3)

### Permission Matrix - 18 hours

- [ ] ⏱️ **Replace bash wildcards with specific constraints**
  - **Task:** Replace `Bash(find:*)` with `Bash(find:-type:f:*)`
  - **Time:** 8 hours
  - **File:** `LAZY_DEV/.claude/settings.json:3-25`
  - **Update:**
    ```json
    "Bash(find:-type:f:*)",
    "Bash(grep:-r:--exclude-dir=node_modules:*)",
    "Bash(npm:install:*)",
    "Bash(npm:run:*)",
    "Bash(python:-m:*)",
    "Bash(docker:ps:*)",
    "Bash(docker:logs:*)"
    ```

- [ ] ⏱️ **Add comprehensive deny rules**
  - **Task:** Add 18 missing deny patterns
  - **Time:** 6 hours
  - **File:** `LAZY_DEV/.claude/settings.json:26-37`
  - **See:** AUDIT_REPORT.md Section 3.1

- [ ] ⏱️ **Document permission rationale**
  - **Task:** Create PERMISSIONS.md with explanations
  - **Time:** 4 hours

### Testing - 12 hours

- [ ] ⏱️ **Create permission testing suite**
  - **Task:** Automated tests for all permission rules
  - **Time:** 8 hours
  - **File:** `LAZY_DEV/tests/test_permissions.py`

- [ ] ⏱️ **Add resource exhaustion prevention**
  - **Task:** Limit recursive operations depth
  - **Time:** 4 hours
  - **New function:** check_recursion_depth()

---

## Phase 4: FINAL REVIEW & TESTING (Week 4)

### Testing - 10 hours

- [ ] ⏱️ **Hook integration tests**
  - **Task:** Test all hooks with real scenarios
  - **Time:** 6 hours
  - **File:** `LAZY_DEV/tests/test_hooks.py`
  - **Coverage:** All blocking scenarios, edge cases

- [ ] ⏱️ **Command workflow tests**
  - **Task:** End-to-end command testing
  - **Time:** 4 hours
  - **File:** `LAZY_DEV/tests/test_commands.py`

### Security - 3 hours

- [ ] ⏱️ **Security penetration testing**
  - **Task:** Attempt to bypass all security controls
  - **Time:** 3 hours
  - **Document:** Any bypasses found

### Documentation - 2 hours

- [ ] ⏱️ **Update all documentation**
  - **Task:** Reflect all changes in CLAUDE.md, README.md
  - **Time:** 2 hours
  - **Files:** CLAUDE.md, README.md, IMPLEMENTATION-PLAN.md

---

## Quick Reference

### Files Modified

**Hooks (9 files):**
- [x] ✅ pre_tool_use.py (directory scanning added)
- [ ] ⏱️ pre_prompt_enrichment.py (API key sanitization)
- [ ] ⏱️ log_events.py (log sanitization)
- [ ] ⏱️ user_prompt_submit.py (duplicate return)
- [ ] ⏱️ session_start.py (duplicate import)
- [ ] ⏱️ post_tool_use_format.py (duplicate import)
- [ ] ⏱️ stop.py (duplicate import)
- [ ] ⏱️ memory_router.py (review)
- [ ] ⏱️ memory_suggestions.py (review)

**Commands (8 files):**
- [ ] ⏱️ story-fix-review.md (model change)
- [ ] ⏱️ documentation.md (expand)
- [ ] ⏱️ (others - review only)

**Configuration:**
- [ ] ⏱️ settings.json (permissions update)
- [x] ✅ .mcp.json (review complete, no changes needed)

### Time Tracking

| Phase | Hours | Status |
|-------|-------|--------|
| Phase 1 | 40 | ⏳ 8h complete, 32h pending |
| Phase 2 | 35 | ⏱️ Not started |
| Phase 3 | 30 | ⏱️ Not started |
| Phase 4 | 15 | ⏱️ Not started |
| **Total** | **120** | **~7% complete** |

### Test Commands

**Verify Directory Scanning Block:**
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"find . -name node_modules"}}' | \
  uv run LAZY_DEV/.claude/hooks/pre_tool_use.py
# Expected: Exit code 2, BLOCKED message
```

**Verify API Key Sanitization (after fix):**
```bash
# Check logs don't contain full API keys
grep -r "sk-[a-zA-Z0-9]{32,}" LAZY_DEV/.claude/data/logs/
# Expected: No matches
```

**Verify Model Consistency (after fix):**
```bash
grep -r "claude-sonnet" LAZY_DEV/.claude/commands/
# Expected: No matches
```

---

## Sign-Off

### Phase 1 Complete
- [ ] Security lead reviewed and approved
- [ ] All critical issues resolved
- [ ] Tests passing

### Phase 2 Complete
- [ ] Performance benchmarks met
- [ ] Code quality checks pass
- [ ] Documentation updated

### Phase 3 Complete
- [ ] Permission matrix validated
- [ ] Security testing passed
- [ ] Compliance verified

### Phase 4 Complete
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Ready for production

---

**Next Steps:**
1. Start with Phase 1, Priority 1 items (API key, regex, command injection)
2. Run test commands after each fix
3. Update this checklist as items complete
4. Review AUDIT_REPORT.md for detailed guidance on each item

**Questions?** Refer to AUDIT_REPORT.md Section 6 (Implementation Roadmap)
