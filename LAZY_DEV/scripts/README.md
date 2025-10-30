# LAZY-DEV-FRAMEWORK Scripts

Supporting utilities that implement the quality pipeline described in
`PROJECT-MANAGEMENT-LAZY_DEV/docs/TOOLS.md`. Each script is cross-platform and
logs into `logs/<session-id>/` when a session identifier is provided.

- `format.py` &mdash; run Black followed by Ruff format against a file or directory.
- `lint.py` &mdash; execute `ruff check --fix` and surface structured violation data.
- `type_check.py` &mdash; invoke mypy in strict mode and capture parsed errors.
- `test_runner.py` &mdash; run pytest with coverage reports (`coverage.json`).
- `gh_wrapper.py` &mdash; thin wrapper around the GitHub CLI for issues/PR interaction.

Example usage:

```bash
python scripts/format.py src/ --session task_123
python scripts/lint.py src/ --session task_123
python scripts/type_check.py src/ --session task_123
python scripts/test_runner.py tests/ --session task_123
python scripts/gh_wrapper.py create-pr --title "WIP" --body "Summary"
```
