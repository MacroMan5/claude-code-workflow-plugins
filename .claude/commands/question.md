---
description: Answer questions about code or technical topics without creating artifacts
argument-hint: "<question>"
allowed-tools: Read, Glob, Grep, Bash, Task
---

# Question Command: Intelligent Q&A System

Answer questions about your codebase or general technical topics with zero artifacts.

## Core Philosophy

**Ask anything, get answers, create nothing.**

This command is for Q&A ONLY - no file creation, no documentation generation, no code changes.

## Usage Examples

```bash
# Codebase questions
/lazy question "where is user authentication handled?"
/lazy question "how does the payment processor work?"
/lazy question "what files implement the REST API?"

# General technical questions
/lazy question "what is the difference between REST and GraphQL?"
/lazy question "how to implement OAuth2 in Python?"
/lazy question "best practices for API versioning?"
```

## When to Use

**Use this command when:**
- You need to understand how something works in the codebase
- You want to locate specific functionality
- You have general technical questions
- You need quick documentation lookups

**Do NOT use for:**
- Creating documentation files
- Modifying code
- Generating new files
- Planning features (use `/lazy plan` instead)

## Requirements

**Input:**
- Single question string (clear and specific)
- Can be about codebase OR general knowledge

**Critical:**
- **NO file creation** - answers only
- **NO .md files** - inline responses only
- **NO code generation** - explanation only
- **NO documentation updates** - read-only operation

## Question Type Detection

### Decision Logic

```python
def should_use_codebase(question: str) -> bool:
    """Decide if question is about codebase or general knowledge."""

    codebase_indicators = [
        "in this", "this codebase", "this project", "this repo",
        "where is", "how does", "why does", "what does",
        "in our", "our codebase", "our project",
        "file", "function", "class", "module",
        "implemented", "defined", "located",
        "show me", "find", "which file"
    ]

    question_lower = question.lower()

    # If question mentions codebase-specific terms → use codebase
    if any(ind in question_lower for ind in codebase_indicators):
        return True

    # If question is general knowledge → use research agent
    general_indicators = [
        "what is", "how to", "difference between",
        "best practice", "tutorial", "documentation",
        "learn", "explain", "guide", "introduction"
    ]

    if any(ind in question_lower for ind in general_indicators):
        return False

    # Default: assume codebase question
    return True
```

### Examples by Type

**Codebase Questions (searches project):**
- "where is user authentication handled?"
- "how does this project structure payments?"
- "what files implement the API endpoints?"
- "in our codebase, how is logging configured?"
- "show me where database migrations are defined"
- "which function handles token validation?"

**General Questions (uses research agent):**
- "what is the difference between JWT and session tokens?"
- "how to implement OAuth2 in Python?"
- "best practices for API versioning?"
- "explain what GraphQL is"
- "tutorial on writing pytest fixtures"

## Execution Workflow

### Phase 1: Analyze Question

```python
question = "$ARGUMENTS".strip()

# Determine question type
is_codebase_question = should_use_codebase(question)

if is_codebase_question:
    approach = "codebase_search"
    tools = ["Grep", "Glob", "Read"]
else:
    approach = "research_agent"
    tools = ["Task (research agent)"]
```

### Phase 2a: Codebase Question Path

**If question is about the codebase:**

```python
# 1. Extract search terms from question
search_terms = extract_keywords(question)
# Example: "where is authentication handled?" → ["authentication", "auth", "login"]

# 2. Search codebase with Grep
for term in search_terms:
    # Search for term in code
    matches = grep(pattern=term, output_mode="files_with_matches")

    # Search for term in comments/docstrings
    doc_matches = grep(pattern=f"(#|//|\"\"\"|\"\"\").*{term}", output_mode="content", -n=True)

# 3. Prioritize results
relevant_files = prioritize_by_relevance(matches, question)
# Priority: src/ > tests/ > docs/

# 4. Read top relevant files
for file in relevant_files[:5]:  # Top 5 most relevant
    content = Read(file_path=file)
    # Extract relevant sections based on search terms

# 5. Analyze and answer
answer = """
Based on codebase analysis:

{synthesized answer from code}

**References:**
- {file1}:{line1}
- {file2}:{line2}
"""
```

**Search Strategy:**

```python
# Identify search terms based on question type
if "where" in question or "which file" in question:
    # Location question - find files
    search_mode = "files_with_matches"
    search_scope = "filenames and content"

elif "how does" in question or "how is" in question:
    # Implementation question - show code
    search_mode = "content"
    search_scope = "function definitions and logic"
    context_lines = 10  # Use -C flag

elif "what is" in question and is_codebase_question:
    # Definition question - find docstrings/comments
    search_mode = "content"
    search_scope = "docstrings, comments, README"
```

### Phase 2b: General Question Path

**If question is general knowledge:**

```python
Task(
    prompt=f"""
You are the Research Agent for LAZY-DEV-FRAMEWORK.

## Question to Answer

{question}

## Instructions

1. This is a GENERAL technical question (not codebase-specific)
2. Answer based on:
   - Your training knowledge
   - Industry best practices
   - Official documentation (if available)
   - Common patterns and conventions

3. Provide a clear, concise answer with:
   - Direct answer to the question
   - Key concepts explained
   - Code examples if relevant (generic, not project-specific)
   - Links to official docs/resources

4. Structure answer for readability:
   - Use bullet points for lists
   - Use code blocks for examples
   - Use clear section headers

## Output Format

**Answer:**
{direct answer}

**Key Concepts:**
- {concept 1}
- {concept 2}

**Example (if applicable):**
```language
{generic code example}
```

**Further Reading:**
- {resource 1}
- {resource 2}

**Critical Reminder:**
- Do NOT create any files
- Do NOT search the codebase
- Do NOT reference project-specific code
- This is general knowledge only
"""
)
```

## Output Format

### For Codebase Questions

```markdown
## Answer

Based on codebase analysis:

{synthesized answer from code analysis}

**Key Files:**
- `{file1}` - {purpose}
- `{file2}` - {purpose}

**Code References:**
- {file1}:{line1} - {what happens here}
- {file2}:{line2} - {what happens here}

**Flow:**
{if applicable, explain the flow through multiple files}
```

### For General Questions

```markdown
## Answer

{direct answer to question}

**Key Concepts:**
- {concept 1 with explanation}
- {concept 2 with explanation}

**Example:**
```language
{generic code example if relevant}
```

**Further Reading:**
- {official documentation link}
- {tutorial or guide link}
```

## Validation

**Success criteria:**
- Question answered clearly and accurately
- References provided (for codebase questions)
- No files created or modified
- No commits made
- Response is conversational, not a file

**Anti-patterns (MUST AVOID):**
- Creating documentation files
- Generating .md files
- Writing code to files
- Running git commands
- Creating pull requests

## Examples in Action

### Example 1: Codebase Location Question

```bash
$ /lazy question "where is user authentication handled?"

## Answer

Based on codebase analysis:

User authentication is handled primarily in the `src/auth/` module:

**Key Files:**
- `src/auth/login.py` - Main login endpoint and session management
- `src/auth/middleware.py` - Authentication middleware for protected routes
- `src/auth/jwt_handler.py` - JWT token generation and validation

**Code References:**
- src/auth/login.py:45 - `authenticate_user()` validates credentials
- src/auth/middleware.py:23 - `require_auth()` decorator protects endpoints
- src/auth/jwt_handler.py:67 - `generate_token()` creates JWT tokens

**Authentication Flow:**
1. User submits credentials → `login.py:authenticate_user()`
2. Credentials validated against database
3. JWT token generated → `jwt_handler.py:generate_token()`
4. Token returned to client
5. Protected routes checked by → `middleware.py:require_auth()`
```

### Example 2: Codebase Implementation Question

```bash
$ /lazy question "how does the payment processor work?"

## Answer

Based on codebase analysis:

The payment processor uses a strategy pattern with multiple payment providers:

**Key Files:**
- `src/payment/processor.py` - Main processor coordinator
- `src/payment/providers/stripe.py` - Stripe integration
- `src/payment/providers/paypal.py` - PayPal integration

**Processing Flow:**
1. Client initiates payment → `processor.py:process_payment()`
2. Processor selects provider based on payment method
3. Provider-specific handler called (Stripe/PayPal)
4. Payment validated and processed
5. Result logged and webhook sent

**Code References:**
- src/payment/processor.py:89 - Main `process_payment()` entry point
- src/payment/processor.py:145 - Provider selection logic
- src/payment/providers/stripe.py:34 - Stripe charge creation
- src/payment/webhook.py:23 - Payment confirmation webhook

**Error Handling:**
- Retries configured in processor.py:67 (3 attempts, exponential backoff)
- Failed payments logged to `payment_failures` table
- Customer notified via email on failure
```

### Example 3: General Technical Question

```bash
$ /lazy question "what is the difference between REST and GraphQL?"

## Answer

REST and GraphQL are both API architectural patterns, but they differ in how clients request and receive data:

**Key Differences:**

1. **Data Fetching:**
   - REST: Multiple endpoints, each returns fixed data structure
   - GraphQL: Single endpoint, client specifies exact data needed

2. **Over/Under-fetching:**
   - REST: Often returns too much or too little data
   - GraphQL: Client gets exactly what they request

3. **Versioning:**
   - REST: Typically requires version in URL (v1, v2)
   - GraphQL: Schema evolution without versions

4. **Request Structure:**
   - REST: HTTP methods (GET, POST, PUT, DELETE)
   - GraphQL: All requests are POST with query body

**Example:**

REST - Multiple requests needed:
```bash
GET /api/users/123          # Get user
GET /api/users/123/posts    # Get user's posts
GET /api/posts/456/comments # Get post comments
```

GraphQL - Single request:
```graphql
query {
  user(id: 123) {
    name
    email
    posts {
      title
      comments {
        text
        author
      }
    }
  }
}
```

**Further Reading:**
- [GraphQL Official Docs](https://graphql.org/learn/)
- [REST API Best Practices](https://restfulapi.net/)
```

### Example 4: Edge Case - Ambiguous Question

```bash
$ /lazy question "how does authentication work?"

# Decision: Too ambiguous - clarify first

## Clarification Needed

Your question "how does authentication work?" could mean:

1. **Codebase-specific:** "How does authentication work in THIS project?"
   - Run: `/lazy question "how does authentication work in this codebase?"`

2. **General concept:** "How does authentication work as a concept?"
   - Run: `/lazy question "explain authentication concepts and best practices"`

Please rephrase your question to be more specific.
```

## Decision Tree

```
Parse question
      ↓
Contains codebase indicators? ──Yes──→ Codebase Search Path
      │                                      ↓
      No                              Extract keywords
      ↓                                      ↓
Contains general indicators? ──Yes──→  Grep/Glob codebase
      │                                      ↓
      No                              Read relevant files
      ↓                                      ↓
   Ambiguous                          Synthesize answer
      ↓                                      ↓
Ask for clarification               Format with references
                                            ↓
                                      Return answer
                                      (NO FILES CREATED)

Research Agent Path:
      ↓
Delegate to research agent
      ↓
Agent uses training knowledge
      ↓
Format answer with examples
      ↓
Return answer
(NO FILES CREATED)
```

## Key Principles

1. **Read-Only Operation**: Never create, modify, or delete files
2. **Zero Artifacts**: No .md files, no commits, no PRs
3. **Smart Detection**: Auto-determine codebase vs general question
4. **Cite Sources**: Always reference file:line for codebase answers
5. **Conversational**: Return inline answers, not documentation
6. **Focused Search**: Top 5 most relevant files only
7. **Context-Aware**: Use -C flag for code context when needed

## Integration Points

**With other commands:**
```bash
# Learn about codebase before implementing
/lazy question "where is user validation implemented?"
/lazy code "add email validation to user signup"

# Understand before documenting
/lazy question "how does the API rate limiting work?"
/lazy docs src/api/rate_limiter.py

# Research before planning
/lazy question "best practices for OAuth2 implementation"
/lazy plan "add OAuth2 authentication"
```

## Environment Variables

None required - this is a pure Q&A command.

## Troubleshooting

**Issue: "No results found"**
```
Try rephrasing your question:
- Use different keywords
- Be more specific about file types or modules
- Check if functionality exists in project
```

**Issue: "Too many results"**
```
Narrow your question:
- Specify module or component
- Add context about feature area
- Ask about specific file/function
```

**Issue: "Wrong type detected"**
```
Force codebase search:
- Add "in this codebase" to question

Force general search:
- Add "explain" or "what is" to question
```

## Anti-Patterns to Avoid

**DO NOT:**
- Create documentation files from answers
- Generate code files based on research
- Write .md files with Q&A content
- Make commits or PRs
- Modify existing files
- Create new directories

**DO:**
- Answer questions inline
- Provide file references
- Show code snippets in response
- Explain concepts clearly
- Link to external resources

---

**Version:** 2.2.0
**Status:** Production-Ready
**Philosophy:** Ask anything, get answers, create nothing.
