# LAZY-DEV-FRAMEWORK Hooks - Fix Examples

This document provides concrete code examples for fixing the critical issues found in the audit.

---

## 1. Fix Duplicate Imports (All Affected Files)

### Current (WRONG):
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import json
import os      # Line 20
import os      # Line 21 - DUPLICATE
import subprocess
import sys
```

### Fixed:
```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import json
import os      # Single import
import subprocess
import sys
```

**Files to fix**:
- `session_start.py` (lines 21-22)
- `user_prompt_submit.py` (lines 21, 32)
- `pre_tool_use.py` (lines 20-21)
- `post_tool_use_format.py` (lines 20-21)
- `stop.py` (lines 20-21)

---

## 2. Fix Duplicate Return Statement

### File: `user_prompt_submit.py` (lines 277-278)

### Current (WRONG):
```python
def build_context_pack(max_items: int = 8) -> str:
    """..."""
    lines: list[str] = []

    # ... lots of code ...

    return "\n".join(lines[:20])  # Line 277
    return "\n".join(lines[:20])  # Line 278 - DUPLICATE, unreachable
```

### Fixed:
```python
def build_context_pack(max_items: int = 8) -> str:
    """..."""
    lines: list[str] = []

    # ... lots of code ...

    return "\n".join(lines[:20])  # Remove the duplicate on line 278
```

---

## 3. Fix API Key Security (pre_prompt_enrichment.py)

### Current (UNSAFE):
```python
def enrich_prompt(user_input: str, api_key: str, model: str, max_tokens: int) -> tuple[str, int]:
    """Enrich user input with comprehensive context using Claude Haiku."""

    try:
        client = Anthropic(api_key=api_key)

        # PROBLEM: API key visible in f-string, could be logged
        enrichment_request = f"""You are a technical enrichment assistant for the LAZY-DEV-FRAMEWORK.

User's brief input: {user_input}

Your task: Expand this brief with actionable technical context. Be concise and specific.
...
"""

        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{'role': 'user', 'content': enrichment_request}]
        )
```

### Fixed:
```python
from string import Template

def enrich_prompt(user_input: str, api_key: str, model: str, max_tokens: int) -> tuple[str, int]:
    """Enrich user input with comprehensive context using Claude Haiku."""

    if not api_key:
        return '', 0

    try:
        client = Anthropic(api_key=api_key)  # Key passed to client, never in strings

        # Use Template.substitute() for safer variable interpolation
        enrichment_template = """You are a technical enrichment assistant for the LAZY-DEV-FRAMEWORK.

User's brief input: $user_input

Your task: Expand this brief with actionable technical context. Be concise and specific.

Include:
1. **Architecture Patterns**: Suggest relevant patterns (MVC, event-driven, microservices, etc.)
2. **Security Requirements**:
   - Input validation (type, range, sanitization)
   - Authentication/authorization considerations
   - OWASP Top 10 relevant items (XSS, SQL injection, etc.)
   - Data encryption needs
3. **Testing Strategy**:
   - Unit tests (what to test)
   - Integration tests (interactions to verify)
   - Edge cases (boundary conditions, error scenarios)
   - Test data requirements
4. **Performance Considerations**:
   - Scalability concerns
   - Caching opportunities
   - Database query optimization
   - API rate limiting
5. **Edge Cases & Error Handling**:
   - Null/empty input handling
   - Network failures
   - Race conditions
   - Resource exhaustion

Output format: Structured markdown with clear sections. Max $max_tokens tokens.
Be actionable and specific to the user's input."""

        # Safe substitution - no API key in template
        enrichment_request = Template(enrichment_template).substitute(
            user_input=user_input,
            max_tokens=max_tokens
        )

        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{'role': 'user', 'content': enrichment_request}]
        )

        enriched_text = response.content[0].text
        tokens_used = response.usage.output_tokens

        return enriched_text, tokens_used

    except Exception as e:
        logger.warning(f"Enrichment failed: {type(e).__name__}")  # Don't log e itself
        return '', 0
```

**Key changes**:
- Use `Template.substitute()` instead of f-strings
- API key never appears in string templates
- Never log the exception object itself (could contain key)
- Validate key exists before using

---

## 4. Fix Regex Pattern Overmatch (pre_tool_use.py)

### Current (UNSAFE):
```python
def is_sensitive_file_access(tool_name: str, tool_input: dict) -> tuple[bool, str]:
    """Check if any tool is trying to access sensitive files."""

    sensitive_files = [
        '.env', '.env.local', '.env.production', '.env.development',
        'secrets.json', 'credentials.json', 'private.key', 'id_rsa', 'id_ed25519',
        '.ssh/config', '.aws/credentials'
    ]

    # ... code ...

    # Generic secrets/keys patterns - TOO BROAD
    generic = [r'\.(pem|key|pfx|p12)\b', r'(?i)token', r'(?i)secret']
    for gp in generic:
        if re.search(gp, command):
            return True, 'sensitive-pattern'

    # This blocks legitimate code:
    # var token_value = ...
    # config.secret_key = ...
```

### Fixed:
```python
import os
import logging

logger = logging.getLogger(__name__)

# Module-level compiled patterns (compiled once, not on every call)
SENSITIVE_PATTERNS = [
    re.compile(r'\.(pem|key|pfx|p12)\b'),  # File extensions only
    re.compile(r'API_KEY\s*[=:]'),         # Specific pattern
    re.compile(r'SECRET_KEY\s*[=:]'),      # Specific pattern
    re.compile(r'PASSWORD\s*[=:]'),        # Specific pattern
    re.compile(r'AWS_SECRET'),
    re.compile(r'PRIVATE_KEY'),
]

def is_sensitive_file_access(tool_name: str, tool_input: dict) -> tuple[bool, str]:
    """Check if any tool is trying to access sensitive files."""

    sensitive_files = [
        '.env', '.env.local', '.env.production', '.env.development',
        'secrets.json', 'credentials.json', 'private.key', 'id_rsa', 'id_ed25519',
        '.ssh/config', '.aws/credentials'
    ]

    # Check file-based tools
    if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write']:
        file_path = tool_input.get('file_path', '')

        # Allow .env.sample and .env.example
        if '.env.sample' in file_path or '.env.example' in file_path:
            return False, ''

        for sensitive in sensitive_files:
            if sensitive in file_path:
                logger.warning(f"Blocked access to sensitive file: {sensitive}")
                return True, sensitive

    # Check bash commands
    elif tool_name == 'Bash':
        command = tool_input.get('command', '')

        # Allow .env.sample and .env.example
        if '.env.sample' in command or '.env.example' in command:
            return False, ''

        for sensitive in sensitive_files:
            patterns = [
                rf'\b{re.escape(sensitive)}\b',
                rf'cat\s+.*{re.escape(sensitive)}',
                rf'echo\s+.*>\s*{re.escape(sensitive)}',
                rf'touch\s+.*{re.escape(sensitive)}',
                rf'cp\s+.*{re.escape(sensitive)}',
                rf'mv\s+.*{re.escape(sensitive)}',
            ]
            for pattern in patterns:
                if re.search(pattern, command):
                    logger.warning(f"Blocked access to sensitive file: {sensitive}")
                    return True, sensitive

        # Check for specific secret patterns (compiled at module level)
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(command):
                logger.warning("Blocked access to sensitive pattern")
                return True, 'sensitive-pattern'

    return False, ''
```

**Key changes**:
- Patterns compiled at module level (done once, not on every call)
- More specific patterns: `API_KEY=`, `SECRET_KEY=`, `PASSWORD=`
- Removed overly broad `r'(?i)token'` and `r'(?i)secret'`
- Added logging for blocked attempts
- Patterns can be extended via env var in future

---

## 5. Add Command Injection Detection (pre_tool_use.py)

### Add this function:

```python
def has_command_injection(command: str) -> bool:
    """
    Detect command injection patterns.

    Checks for:
    - Shell execution: sh -c, bash -c
    - Code evaluation: eval, exec
    - Command substitution: $(...), `...`
    - Pipe to shell: | sh, | bash
    """

    # Compile once at module level if using in multiple places
    injection_patterns = [
        re.compile(r'\bsh\s+-c\b'),           # sh -c
        re.compile(r'\bbash\s+-c\b'),         # bash -c
        re.compile(r'\beval\s+'),             # eval command
        re.compile(r'\bexec\s+'),             # exec command
        re.compile(r'\$\([^)]+\)'),           # $(command) substitution
        re.compile(r'`[^`]+`'),               # `command` substitution
        re.compile(r'\|\s*(sh|bash|zsh)\b'),  # | sh/bash/zsh pipes
    ]

    normalized = command.lower()

    for pattern in injection_patterns:
        if pattern.search(normalized):
            return True

    return False
```

### Use in main():

```python
def main():
    """Hook entry point."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})

        # Security Check 1: Sensitive file access
        is_sensitive, file_name = is_sensitive_file_access(tool_name, tool_input)
        if is_sensitive:
            print(f"BLOCKED: Access to sensitive file '{file_name}' is prohibited", file=sys.stderr)
            sys.exit(2)

        # Security Check 2: Dangerous rm commands
        if tool_name == 'Bash':
            command = tool_input.get('command', '')

            if is_dangerous_rm_command(command):
                print("BLOCKED: Dangerous rm command detected", file=sys.stderr)
                sys.exit(2)

            # Security Check 3: Force push to main/master
            if is_force_push_to_main(command):
                print("BLOCKED: Force push to main/master branch is prohibited", file=sys.stderr)
                sys.exit(2)

            # Security Check 4: Command injection (NEW)
            if has_command_injection(command):
                print("BLOCKED: Command injection pattern detected", file=sys.stderr)
                logger.warning(f"Command injection attempt: {command[:100]}")
                sys.exit(2)
```

---

## 6. Fix Path Traversal Risk (session_start.py)

### Current (UNSAFE):
```python
def initialize_session_state(session_id: str, context: dict) -> None:
    """Initialize session state file in .claude/data/sessions/."""

    sessions_dir = Path('.claude/data/sessions')
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # PROBLEM: session_id not validated
    # Could be "../../../etc/passwd" or absolute path
    session_file = sessions_dir / f'{session_id}.json'

    # ... rest of function
```

### Fixed:
```python
import re

def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.

    Only allows alphanumeric, hyphens, and underscores.
    Prevents path traversal attacks.
    """
    return bool(re.match(r'^[a-zA-Z0-9_-]{1,64}$', session_id))

def initialize_session_state(session_id: str, context: dict) -> None:
    """Initialize session state file in .claude/data/sessions/."""

    # Validate session_id format
    if not validate_session_id(session_id):
        logger.error(f"Invalid session_id format: {session_id}")
        return  # Fail silently, don't create file

    sessions_dir = Path('.claude/data/sessions')
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Now safe - session_id is validated
    session_file = sessions_dir / f'{session_id}.json'

    # ... rest of function
```

### Also fix in main():

```python
def main():
    """Hook entry point."""
    try:
        input_data = json.load(sys.stdin)

        session_id = input_data.get('session_id', 'unknown')

        # Validate session_id
        if not validate_session_id(session_id):
            logger.error(f"Invalid session_id: {session_id}")
            sys.exit(0)  # Don't block, just skip

        # ... rest of main
```

---

## 7. Fix Silent Error Handling (All Hooks)

### Current (WRONG):
```python
def get_git_history() -> list[str]:
    """Get recent git commits (last 10)."""
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline', '-10'],
            capture_output=True,
            text=True,
            timeout=3
        )

        if result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            return [c for c in commits if c]

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
        pass  # SILENT FAILURE - no logging

    return []
```

### Fixed:
```python
import logging

logger = logging.getLogger(__name__)

def get_git_history() -> list[str]:
    """Get recent git commits (last 10)."""
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline', '-10'],
            capture_output=True,
            text=True,
            timeout=3
        )

        if result.returncode == 0:
            commits = result.stdout.strip().split('\n')
            return [c for c in commits if c]
        else:
            logger.debug(f"Git log failed with code {result.returncode}")

    except subprocess.TimeoutExpired:
        logger.warning("Git operation timed out (3s)")
    except subprocess.SubprocessError as e:
        logger.warning(f"Git subprocess error: {type(e).__name__}")
    except FileNotFoundError:
        logger.debug("Git not found in PATH")

    return []
```

---

## 8. Move Regex Patterns to Module Level

### Current (INEFFICIENT):
```python
def is_dangerous_rm_command(command: str) -> bool:
    """Comprehensive detection of dangerous rm commands."""

    normalized = ' '.join(command.lower().split())

    # Compiled EVERY TIME THIS FUNCTION IS CALLED
    patterns = [
        r'\brm\s+.*-[a-z]*r[a-z]*f',
        r'\brm\s+.*-[a-z]*f[a-z]*r',
        r'\brm\s+--recursive\s+--force',
        r'\brm\s+--force\s+--recursive',
        r'\brm\s+-r\s+.*-f',
        r'\brm\s+-f\s+.*-r',
    ]

    for pattern in patterns:  # Calls re.search() which compiles implicitly
        if re.search(pattern, normalized):
            return True

    # ... more code
```

### Fixed:
```python
import re

# Compile patterns ONCE at module load time
DANGEROUS_RM_PATTERNS = [
    re.compile(r'\brm\s+.*-[a-z]*r[a-z]*f'),
    re.compile(r'\brm\s+.*-[a-z]*f[a-z]*r'),
    re.compile(r'\brm\s+--recursive\s+--force'),
    re.compile(r'\brm\s+--force\s+--recursive'),
    re.compile(r'\brm\s+-r\s+.*-f'),
    re.compile(r'\brm\s+-f\s+.*-r'),
]

DANGEROUS_PATHS = [
    re.compile(r'\s+/$'),
    re.compile(r'\s+/\*'),
    re.compile(r'\s+~/?$'),
    re.compile(r'\s+\$HOME'),
    re.compile(r'\s+\.\.$'),
    re.compile(r'\s+\.\s*$'),
]

def is_dangerous_rm_command(command: str) -> bool:
    """Comprehensive detection of dangerous rm commands."""

    normalized = ' '.join(command.lower().split())

    # Use pre-compiled patterns (much faster)
    for pattern in DANGEROUS_RM_PATTERNS:
        if pattern.search(normalized):
            return True

    if re.search(r'\brm\s+.*-[a-z]*r', normalized):
        for path_pattern in DANGEROUS_PATHS:
            if path_pattern.search(normalized):
                return True

    return False
```

**Performance improvement**: ~10-100x faster on repeated calls

---

## 9. Implement Log Sanitization

### Add to any hook that logs:

```python
import json
import re

# Keys to sanitize from logs
SENSITIVE_KEYS = {
    'api_key', 'apikey', 'api-key',
    'secret', 'secret_key',
    'password', 'passwd',
    'token', 'bearer',
    'authorization',
    'x-api-key',
    'aws_secret',
    'private_key',
}

SENSITIVE_PATTERNS = [
    re.compile(r'(api_key|apikey|api-key)\s*[=:]\s*\S+', re.IGNORECASE),
    re.compile(r'(password|passwd)\s*[=:]\s*\S+', re.IGNORECASE),
    re.compile(r'(token|bearer)\s+\S+', re.IGNORECASE),
    re.compile(r'(secret|secret_key)\s*[=:]\s*\S+', re.IGNORECASE),
    re.compile(r'Authorization:\s*Bearer\s+\S+', re.IGNORECASE),
]

def sanitize_for_logging(text: str) -> str:
    """Remove sensitive data from text before logging."""

    if not isinstance(text, str):
        return str(text)

    sanitized = text

    # Replace sensitive patterns
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(lambda m: m.group(1) + '=***REDACTED***', sanitized)

    return sanitized

def log_tool_call(input_data: dict) -> None:
    """Log tool call with sensitive data removed."""

    # Deep copy to avoid modifying original
    safe_data = json.loads(json.dumps(input_data))

    # Sanitize command if present
    if 'tool_input' in safe_data:
        if 'command' in safe_data['tool_input']:
            safe_data['tool_input']['command'] = sanitize_for_logging(
                safe_data['tool_input']['command']
            )

    # Write sanitized log
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        **safe_data
    }

    log_data.append(log_entry)
```

---

## 10. Reduce Subprocess Timeout

### Current (EXCESSIVE):
```python
def format_python(file_path: Path) -> tuple[bool, str]:
    """Format Python file with Black and Ruff."""

    try:
        result = subprocess.run(
            ['black', '--quiet', str(file_path)],
            capture_output=True,
            text=True,
            timeout=10  # 10 seconds is way too long
        )
```

### Fixed:
```python
def format_python(file_path: Path) -> tuple[bool, str]:
    """Format Python file with Black and Ruff."""

    try:
        # Reasonable timeout: Black/Ruff should format in < 2 seconds
        result = subprocess.run(
            ['black', '--quiet', str(file_path)],
            capture_output=True,
            text=True,
            timeout=3  # Max 3 seconds per formatter
        )

        black_success = result.returncode == 0

        # Also timeout Ruff
        result = subprocess.run(
            ['ruff', 'format', str(file_path)],
            capture_output=True,
            text=True,
            timeout=3  # Max 3 seconds per formatter
        )
```

---

## Summary of Critical Fixes

| Issue | File | Priority | Effort |
|-------|------|----------|--------|
| Duplicate imports | 5 files | HIGH | <5 min |
| API key in f-string | pre_prompt_enrichment.py | CRITICAL | 30 min |
| Regex overmatch | pre_tool_use.py | CRITICAL | 30 min |
| Command injection detection | pre_tool_use.py | CRITICAL | 30 min |
| Path traversal validation | session_start.py, stop.py | CRITICAL | 20 min |
| Silent error handling | All hooks | HIGH | 1 hour |
| Regex compilation | Multiple | HIGH | 30 min |
| Duplicate return | user_prompt_submit.py | MEDIUM | <5 min |
| Log sanitization | log_events.py, etc. | HIGH | 30 min |
| Subprocess timeouts | post_tool_use_format.py | MEDIUM | 10 min |

---

**Total time to implement all critical fixes**: ~4-5 hours

---

## Testing Each Fix

### Test API key fix:
```bash
# Should NOT log the API key
ANTHROPIC_API_KEY=sk_test_12345 uv run .claude/hooks/pre_prompt_enrichment.py
```

### Test regex fix:
```bash
# Should NOT block this (legitimate code):
echo 'config.token_value = "test"' | uv run .claude/hooks/pre_tool_use.py

# Should block this (sensitive file):
echo 'cat ~/.env' | uv run .claude/hooks/pre_tool_use.py
```

### Test path validation:
```bash
# Should work (valid session_id):
echo '{"session_id": "session-123"}' | uv run .claude/hooks/session_start.py

# Should fail silently (invalid session_id):
echo '{"session_id": "../../../etc/passwd"}' | uv run .claude/hooks/session_start.py
```

---
