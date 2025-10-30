---
name: security-audit
description: Triggers for authentication, payments, user input, and API endpoints to check OWASP risks. Auto-evaluates security need and provides actionable fixes, not checklists.
---

# Security Audit Skill

**Purpose**: Catch security vulnerabilities early with targeted checks, not generic checklists.

**Trigger Words**: auth, login, password, payment, credit card, token, API endpoint, user input, SQL, database query, session, cookie, upload

---

## Quick Decision: When to Audit?

```python
def needs_security_audit(code_context: dict) -> bool:
    """Fast security risk evaluation."""

    # ALWAYS audit these (high risk)
    critical_patterns = [
        "authentication", "authorization", "login", "password",
        "payment", "credit card", "billing", "stripe", "paypal",
        "admin", "sudo", "privilege", "role",
        "token", "jwt", "session", "cookie",
        "sql", "database", "query", "exec", "eval",
        "upload", "file", "download", "path traversal"
    ]

    # Check if any critical pattern in code
    if any(p in code_context.get("description", "").lower() for p in critical_patterns):
        return True

    # Skip for: docs, tests, config, low-risk utils
    skip_patterns = ["test_", "docs/", "README", "config", "utils"]
    if any(p in code_context.get("files", []) for p in skip_patterns):
        return False

    return False
```

---

## Security Checks (Targeted, Not Exhaustive)

### 1. **Input Validation** (Most Common)
```python
# ❌ BAD - No validation
def get_user(user_id):
    return db.query(f"SELECT * FROM users WHERE id = {user_id}")

# ✅ GOOD - Validated + parameterized
def get_user(user_id: int):
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("Invalid user_id")
    return db.query("SELECT * FROM users WHERE id = ?", [user_id])
```

**Quick Fix**: Add type hints + validation at entry points.

---

### 2. **SQL Injection** (Critical)
```python
# ❌ BAD - String interpolation
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ GOOD - Parameterized queries
query = "SELECT * FROM users WHERE email = ?"
db.execute(query, [email])
```

**Quick Fix**: Never use f-strings for SQL. Use ORM or parameterized queries.

---

### 3. **Authentication & Secrets** (Critical)
```python
# ❌ BAD - Hardcoded secrets
API_KEY = "sk_live_abc123"
password = "admin123"

# ✅ GOOD - Environment variables
API_KEY = os.getenv("STRIPE_API_KEY")
# Passwords: bcrypt hashed, never plaintext

# ❌ BAD - Weak session
session["user_id"] = user_id  # No expiry, no signing

# ✅ GOOD - Secure session
session.permanent = False
session["user_id"] = user_id
session["expires"] = time.time() + 3600  # 1 hour
```

**Quick Fix**: Extract secrets to .env, hash passwords, add session expiry.

---

### 4. **Authorization** (Often Forgotten)
```python
# ❌ BAD - Missing authorization check
@app.route("/admin/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    User.delete(user_id)  # Anyone can delete!

# ✅ GOOD - Check permissions
@app.route("/admin/users/<user_id>", methods=["DELETE"])
@require_role("admin")
def delete_user(user_id):
    if not current_user.can_delete(user_id):
        abort(403)
    User.delete(user_id)
```

**Quick Fix**: Add permission checks before destructive operations.

---

### 5. **Rate Limiting** (API Endpoints)
```python
# ❌ BAD - No rate limit
@app.route("/api/login", methods=["POST"])
def login():
    # Brute force possible
    return authenticate(request.json)

# ✅ GOOD - Rate limited
@app.route("/api/login", methods=["POST"])
@rate_limit("5 per minute")
def login():
    return authenticate(request.json)
```

**Quick Fix**: Add rate limiting to login, payment, sensitive endpoints.

---

### 6. **XSS Prevention** (Frontend/Templates)
```python
# ❌ BAD - Unescaped user input
return f"<div>Welcome {username}</div>"  # XSS if username = "<script>alert('XSS')</script>"

# ✅ GOOD - Escaped output
from html import escape
return f"<div>Welcome {escape(username)}</div>"

# Or use framework escaping (Jinja2, React auto-escapes)
```

**Quick Fix**: Escape user input in HTML. Use framework defaults.

---

### 7. **File Upload Safety**
```python
# ❌ BAD - No validation
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    file.save(f"uploads/{file.filename}")  # Path traversal! Overwrite!

# ✅ GOOD - Validated
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "pdf"}

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    if not file or "." not in file.filename:
        abort(400, "Invalid file")

    ext = file.filename.rsplit(".", 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        abort(400, "File type not allowed")

    filename = secure_filename(file.filename)
    file.save(os.path.join("uploads", filename))
```

**Quick Fix**: Whitelist extensions, sanitize filenames, limit size.

---

## Output Format (Actionable Only)

```markdown
## Security Audit Results

**Risk Level**: [CRITICAL | HIGH | MEDIUM | LOW]

### Issues Found: X

1. **[CRITICAL] SQL Injection in get_user() (auth.py:45)**
   - Issue: f-string used for SQL query
   - Fix: Use parameterized query
   - Code:
     ```python
     # Change this:
     query = f"SELECT * FROM users WHERE id = {user_id}"
     # To this:
     query = "SELECT * FROM users WHERE id = ?"
     db.execute(query, [user_id])
     ```

2. **[HIGH] Missing rate limiting on /api/login**
   - Issue: Brute force attacks possible
   - Fix: Add @rate_limit("5 per minute") decorator

3. **[MEDIUM] Hardcoded API key in config.py:12**
   - Issue: Secret in code
   - Fix: Move to environment variable

---

**Next Steps**:
1. Fix CRITICAL issues first (SQL injection)
2. Add rate limiting (5 min fix)
3. Extract secrets to .env
4. Re-run security audit after fixes
```

---

## Integration with Workflow

```bash
# Automatic trigger
/lazy code "add user login endpoint"

→ security-audit triggers
→ Checks: password handling, session, rate limiting
→ Finds: Missing bcrypt hash, no rate limit
→ Suggests fixes with code examples
→ Developer applies fixes
→ Re-audit confirms: ✅ Secure

# Manual trigger
Skill(command="security-audit")
```

---

## What This Skill Does NOT Do

❌ Generate 50-item security checklists (not actionable)
❌ Flag every minor issue (noise)
❌ Require penetration testing (that's a different tool)
❌ Cover infrastructure security (AWS, Docker, etc.)

✅ **DOES**: Catch common code-level vulnerabilities with fast, practical fixes.

---

## Configuration

```bash
# Strict mode: audit everything (slower)
export LAZYDEV_SECURITY_STRICT=1

# Disable security skill
export LAZYDEV_DISABLE_SECURITY=1

# Focus on specific risks only
export LAZYDEV_SECURITY_FOCUS="sql,auth,xss"
```

---

**Version**: 1.0.0
**OWASP Coverage**: SQL Injection, XSS, Broken Auth, Insecure Design, Security Misconfiguration
**Speed**: <5 seconds for typical file
