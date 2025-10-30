#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anthropic>=0.18.0",
#     "python-dotenv>=1.0.0"
# ]
# ///

"""
Pre-prompt enrichment hook for LAZY-DEV-FRAMEWORK - CRITICAL COMPONENT.

Automatically enriches user input with:
- Architecture patterns
- Security requirements (OWASP Top 10)
- Testing strategy
- Edge cases
- Performance considerations

Uses Claude Haiku for cost efficiency (max 1000 tokens).

References:
- PROJECT-MANAGEMENT-LAZY_DEV/docs/HOOKS.md (Pre-Prompt Enrichment section)
- PROJECT-MANAGEMENT-LAZY_DEV/IMPLEMENTATION-PLAN.md (enrichment prompt design)
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from string import Template

logger = logging.getLogger(__name__)

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def enrich_prompt(user_input: str, api_key: str, model: str, max_tokens: int) -> tuple[str, int]:
    """
    Enrich user input with comprehensive context using Claude Haiku.

    Args:
        user_input: Original user prompt
        api_key: Anthropic API key
        model: Claude model to use (Haiku)
        max_tokens: Maximum tokens for enrichment

    Returns:
        Tuple of (enriched_text, tokens_used)
    """
    if not ANTHROPIC_AVAILABLE:
        return '', 0

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


def log_enrichment(session_id: str, original: str, enriched: str, tokens: int) -> None:
    """
    Log enrichment to logs/pre_prompt_enrichment.json.

    Args:
        session_id: Session identifier
        original: Original prompt
        enriched: Enriched text
        tokens: Tokens used
    """
    log_dir = Path(os.getenv('LAZYDEV_LOG_DIR', '.claude/data/logs'))
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / 'pre_prompt_enrichment.json'

    # Read existing log or initialize
    if log_file.exists():
        try:
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            log_data = []
    else:
        log_data = []

    # Add enrichment entry
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'session_id': session_id,
        'original_length': len(original),
        'enriched_length': len(enriched),
        'tokens_used': tokens,
        'original_prompt': original[:200] + '...' if len(original) > 200 else original
    }

    log_data.append(log_entry)

    # Write back
    with open(log_file, 'w') as f:
        json.dump(log_data, f, indent=2)


def main():
    """Hook entry point."""
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        session_id = input_data.get('session_id', 'unknown')
        user_prompt = input_data.get('prompt', '')

        # Get configuration from environment
        api_key = os.getenv('ANTHROPIC_API_KEY')
        model = os.getenv('ENRICHMENT_MODEL')
        max_tokens = int(os.getenv('ENRICHMENT_MAX_TOKENS', '1000'))

        # Check if enrichment is enabled and API key is available
        if not api_key or not model:
            # No API key - skip enrichment but don't block
            print(json.dumps({'prompt': user_prompt, 'enriched': False}))
            sys.exit(0)

        if not ANTHROPIC_AVAILABLE:
            # Anthropic library not available - skip enrichment
            print(json.dumps({'prompt': user_prompt, 'enriched': False}))
            sys.exit(0)

        # Enrich the prompt
        enriched_text, tokens_used = enrich_prompt(user_prompt, api_key, model, max_tokens)

        # Build final enriched prompt
        if enriched_text:
            enriched_prompt = f"""{user_prompt}

---

## Auto-Enrichment (LAZY-DEV-FRAMEWORK)

{enriched_text}

---
"""
        else:
            # Enrichment failed - use original prompt
            enriched_prompt = user_prompt

        # Log enrichment
        log_enrichment(session_id, user_prompt, enriched_text, tokens_used)

        # Output enriched prompt
        output = {
            'prompt': enriched_prompt,
            'enriched': bool(enriched_text),
            'tokens_used': tokens_used
        }

        print(json.dumps(output))

        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully - don't block on enrichment failure
        print(f'Hook error: {e}', file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    main()
