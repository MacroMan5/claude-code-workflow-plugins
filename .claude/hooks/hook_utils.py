"""Common utilities for LAZY_DEV hooks."""

import re
import json

# Sensitive patterns to redact from logs
SENSITIVE_PATTERNS = [
    re.compile(r"(api_key|apikey|api-key)\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"(password|passwd)\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"(token|bearer)\s+\S+", re.IGNORECASE),
    re.compile(r"(secret|secret_key)\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"Authorization:\s*Bearer\s+\S+", re.IGNORECASE),
    re.compile(r"AWS_SECRET\s*[=:]\s*\S+", re.IGNORECASE),
    re.compile(r"PRIVATE_KEY\s*[=:]\s*\S+", re.IGNORECASE),
]


def sanitize_for_logging(text: str) -> str:
    """
    Remove sensitive data from text before logging.

    Args:
        text: The text to sanitize

    Returns:
        Sanitized text with secrets redacted
    """
    if not isinstance(text, str):
        return str(text)

    sanitized = text

    # Replace sensitive patterns
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(lambda m: m.group(1) + "=***REDACTED***", sanitized)

    return sanitized


def sanitize_dict_for_logging(data: dict) -> dict:
    """
    Deep sanitize a dictionary for logging.

    Args:
        data: The dictionary to sanitize

    Returns:
        New dictionary with sensitive values redacted
    """
    # Deep copy to avoid modifying original
    try:
        sanitized = json.loads(json.dumps(data))
    except (TypeError, ValueError):
        # Fallback for non-JSON-serializable data
        return {"error": "Unable to sanitize data"}

    # Sanitize string values recursively
    def sanitize_recursive(obj):
        if isinstance(obj, dict):
            return {k: sanitize_recursive(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [sanitize_recursive(item) for item in obj]
        elif isinstance(obj, str):
            return sanitize_for_logging(obj)
        else:
            return obj

    return sanitize_recursive(sanitized)
