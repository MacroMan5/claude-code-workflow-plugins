---
name: breaking-change-detector
description: Detects backward-incompatible changes to public APIs, function signatures, endpoints, and data schemas before they break production. Suggests migration paths.
---

# Breaking Change Detector Skill

**Purpose**: Catch breaking changes early, not after customers complain.

**Trigger Words**: API, endpoint, route, public, schema, model, interface, contract, signature, rename, remove, delete

---

## Quick Decision: Is This Breaking?

```python
def is_breaking_change(change: dict) -> tuple[bool, str]:
    """Fast breaking change evaluation."""

    breaking_patterns = {
        # Method signatures
        "removed_parameter": True,
        "renamed_parameter": True,
        "changed_parameter_type": True,
        "removed_method": True,
        "renamed_method": True,

        # API endpoints
        "removed_endpoint": True,
        "renamed_endpoint": True,
        "changed_response_format": True,
        "removed_response_field": True,

        # Data models
        "removed_field": True,
        "renamed_field": True,
        "changed_field_type": True,
        "made_required": True,

        # Return types
        "changed_return_type": True,
    }

    # Safe changes (backward compatible)
    safe_patterns = {
        "added_parameter_with_default": False,
        "added_optional_field": False,
        "added_endpoint": False,
        "added_response_field": False,
        "deprecated_but_kept": False,
    }

    change_type = change.get("type")
    return breaking_patterns.get(change_type, False), change_type
```

---

## Common Breaking Changes (With Fixes)

### 1. **Removed Function Parameter** ❌ BREAKING
```python
# BEFORE (v1.0)
def process_payment(amount, currency, user_id):
    pass

# AFTER (v2.0) - BREAKS EXISTING CODE
def process_payment(amount, user_id):  # Removed currency!
    pass

# ✅ FIX: Keep parameter with default
def process_payment(amount, user_id, currency="USD"):
    """
    Args:
        currency: Deprecated in v2.0, always uses USD
    """
    pass
```

**Migration Path**: Add default value, deprecate, document.

---

### 2. **Renamed Function/Method** ❌ BREAKING
```python
# BEFORE
def getUserProfile(user_id):
    pass

# AFTER - BREAKS CALLS
def get_user_profile(user_id):  # Renamed!
    pass

# ✅ FIX: Keep both, deprecate old
def get_user_profile(user_id):
    """Get user profile (v2.0+ naming)."""
    pass

def getUserProfile(user_id):
    """Deprecated: Use get_user_profile() instead."""
    warnings.warn("getUserProfile is deprecated, use get_user_profile", DeprecationWarning)
    return get_user_profile(user_id)
```

**Migration Path**: Alias old name → new name, add deprecation warning.

---

### 3. **Changed Response Format** ❌ BREAKING
```python
# BEFORE - Returns dict
@app.route("/api/user/<id>")
def get_user(id):
    return {"id": id, "name": "Alice", "email": "alice@example.com"}

# AFTER - Returns list - BREAKS CLIENTS!
@app.route("/api/user/<id>")
def get_user(id):
    return [{"id": id, "name": "Alice", "email": "alice@example.com"}]

# ✅ FIX: Keep format, add new endpoint
@app.route("/api/v2/user/<id>")  # New version
def get_user_v2(id):
    return [{"id": id, "name": "Alice"}]

@app.route("/api/user/<id>")  # Keep v1
def get_user(id):
    return {"id": id, "name": "Alice", "email": "alice@example.com"}
```

**Migration Path**: Version the API (v1, v2), keep old version alive.

---

### 4. **Removed Endpoint** ❌ BREAKING
```python
# BEFORE
@app.route("/users")
def get_users():
    pass

# AFTER - REMOVED! Breaks clients.
# (endpoint deleted)

# ✅ FIX: Redirect to new endpoint
@app.route("/users")
def get_users():
    """Deprecated: Use /api/v2/accounts instead."""
    return redirect("/api/v2/accounts", code=301)  # Permanent redirect
```

**Migration Path**: Keep endpoint, redirect with 301, document deprecation.

---

### 5. **Changed Required Fields** ❌ BREAKING
```python
# BEFORE - email optional
class User:
    def __init__(self, name, email=None):
        self.name = name
        self.email = email

# AFTER - email required! Breaks existing code.
class User:
    def __init__(self, name, email):  # No default!
        self.name = name
        self.email = email

# ✅ FIX: Keep optional, validate separately
class User:
    def __init__(self, name, email=None):
        self.name = name
        self.email = email

    def validate(self):
        """Validate required fields."""
        if not self.email:
            raise ValueError("Email is required (new in v2.0)")
```

**Migration Path**: Keep optional in constructor, add validation method.

---

### 6. **Removed Response Field** ❌ BREAKING
```python
# BEFORE
{
    "id": 123,
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com"
}

# AFTER - Removed age! Breaks clients expecting it.
{
    "id": 123,
    "name": "Alice",
    "email": "alice@example.com"
}

# ✅ FIX: Keep field with null/default
{
    "id": 123,
    "name": "Alice",
    "age": null,  # Deprecated, always null in v2.0
    "email": "alice@example.com"
}
```

**Migration Path**: Keep field with null, document deprecation.

---

## Non-Breaking Changes ✅ (Safe)

### 1. **Added Optional Parameter**
```python
# BEFORE
def process_payment(amount):
    pass

# AFTER - Safe! Has default
def process_payment(amount, currency="USD"):
    pass

# Old calls still work:
process_payment(100)  # ✅ Works
```

---

### 2. **Added Response Field**
```python
# BEFORE
{"id": 123, "name": "Alice"}

# AFTER - Safe! Added field
{"id": 123, "name": "Alice", "created_at": "2025-10-30"}

# Old clients ignore new field: ✅ Works
```

---

### 3. **Added New Endpoint**
```python
# New endpoint added
@app.route("/api/v2/users")
def get_users_v2():
    pass

# Old endpoint unchanged: ✅ Safe
```

---

## Detection Strategy

### Automatic Checks
1. **Function signatures**: Compare old vs new parameters, types, names
2. **API routes**: Check for removed/renamed endpoints
3. **Data schemas**: Validate field additions/removals/renames
4. **Return types**: Detect type changes

### When to Run
- ✅ Before committing changes to public APIs
- ✅ During code review
- ✅ Before releasing new version

---

## Output Format

```markdown
## Breaking Change Report

**Status**: [✅ NO BREAKING CHANGES | ⚠️ BREAKING CHANGES DETECTED]

---

### Breaking Changes: 2

1. **[CRITICAL] Removed endpoint: GET /users**
   - **Impact**: External API clients will get 404
   - **File**: api/routes.py:45
   - **Fix**:
     ```python
     # Keep endpoint, redirect to new one
     @app.route("/users")
     def get_users():
         return redirect("/api/v2/accounts", code=301)
     ```
   - **Migration**: Add to CHANGELOG.md, notify users

2. **[HIGH] Renamed parameter: currency → currency_code**
   - **Impact**: Existing function calls will fail
   - **File**: payments.py:23
   - **Fix**:
     ```python
     # Accept both, deprecate old name
     def process_payment(amount, currency_code=None, currency=None):
         # Support old name temporarily
         if currency is not None:
             warnings.warn("currency is deprecated, use currency_code")
             currency_code = currency
     ```

---

### Safe Changes: 1

1. **[SAFE] Added optional parameter: timeout (default=30)**
   - **File**: api_client.py:12
   - **Impact**: None, backward compatible

---

**Recommendation**:
1. Fix 2 breaking changes before merge
2. Document breaking changes in CHANGELOG.md
3. Bump major version (v1.x → v2.0) per semver
4. Notify API consumers 2 weeks before release
```

---

## Integration with Workflow

```bash
# Automatic trigger when modifying APIs
/lazy code "rename /users endpoint to /accounts"

→ breaking-change-detector triggers
→ Detects: Endpoint rename is breaking
→ Suggests: Keep /users, redirect to /accounts
→ Developer applies fix
→ Re-check: ✅ Backward compatible

# Before PR
/lazy review US-3.4

→ breaking-change-detector runs
→ Checks all API changes in PR
→ Reports breaking changes
→ PR blocked if breaking without migration plan
```

---

## Version Bumping Guide

```bash
# Semantic versioning
Given version: MAJOR.MINOR.PATCH

# Breaking change detected → Bump MAJOR
1.2.3 → 2.0.0

# New feature (backward compatible) → Bump MINOR
1.2.3 → 1.3.0

# Bug fix (backward compatible) → Bump PATCH
1.2.3 → 1.2.4
```

---

## What This Skill Does NOT Do

❌ Catch internal/private API changes (only public APIs)
❌ Test runtime compatibility (use integration tests)
❌ Manage database migrations (separate tool)
❌ Generate full migration scripts

✅ **DOES**: Detect public API breaking changes, suggest fixes, enforce versioning.

---

## Configuration

```bash
# Strict mode: flag all changes (even safe ones)
export LAZYDEV_BREAKING_STRICT=1

# Disable breaking change detection
export LAZYDEV_DISABLE_BREAKING_DETECTOR=1

# Check only specific types
export LAZYDEV_BREAKING_CHECK="endpoints,schemas"
```

---

**Version**: 1.0.0
**Follows**: Semantic Versioning 2.0.0
**Speed**: <3 seconds for typical PR
