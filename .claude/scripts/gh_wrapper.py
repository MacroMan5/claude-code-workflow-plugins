#!/usr/bin/env python3
"""GitHub CLI wrapper - Cross-OS compatible."""

import subprocess
import sys
from typing import Dict, List, Optional


class GitHubWrapper:
    """Wrapper for GitHub CLI operations."""

    @staticmethod
    def create_issue(
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
        milestone: Optional[str] = None,
        assignee: Optional[str] = None,
        repo: Optional[str] = None
    ) -> str:
        """
        Create GitHub issue.

        This method creates a GitHub issue using the gh CLI. It supports
        labels, milestones, and assignees.

        Args:
            title: Issue title.
            body: Issue body (markdown formatted).
            labels: Optional list of label names.
            milestone: Optional milestone name.
            assignee: Optional username to assign.
            repo: Optional repo in format "owner/repo" (uses current by default).

        Returns:
            Issue URL as string.

        Raises:
            Exception: If issue creation fails.

        Example:
            >>> GitHubWrapper.create_issue("Bug Fix", "Description", labels=["bug"])
            'https://github.com/owner/repo/issues/123'
        """
        cmd = ["gh", "issue", "create", "--title", title, "--body", body]

        if labels:
            cmd.extend(["--label", ",".join(labels)])
        if milestone:
            cmd.extend(["--milestone", milestone])
        if assignee:
            cmd.extend(["--assignee", assignee])
        if repo:
            cmd.extend(["--repo", repo])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Failed to create issue: {result.stderr}")

        return result.stdout.strip()

    @staticmethod
    def create_pr(
        title: str,
        body: str,
        base: str = "main",
        head: Optional[str] = None,
        labels: Optional[List[str]] = None,
        repo: Optional[str] = None
    ) -> str:
        """
        Create GitHub pull request.

        This method creates a GitHub PR using the gh CLI. It supports
        custom base and head branches, labels, and repository selection.

        Args:
            title: PR title.
            body: PR body (markdown formatted).
            base: Base branch name. Defaults to "main".
            head: Head branch name. Uses current branch if not specified.
            labels: Optional list of label names.
            repo: Optional repo in format "owner/repo" (uses current by default).

        Returns:
            PR URL as string.

        Raises:
            Exception: If PR creation fails.

        Example:
            >>> GitHubWrapper.create_pr("Feature", "Description", base="main")
            'https://github.com/owner/repo/pull/456'
        """
        cmd = [
            "gh", "pr", "create",
            "--title", title,
            "--body", body,
            "--base", base
        ]

        if head:
            cmd.extend(["--head", head])
        if labels:
            cmd.extend(["--label", ",".join(labels)])
        if repo:
            cmd.extend(["--repo", repo])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Failed to create PR: {result.stderr}")

        return result.stdout.strip()

    @staticmethod
    def get_current_branch() -> str:
        """
        Get current git branch.

        Returns:
            Current branch name as string.

        Raises:
            Exception: If git command fails.

        Example:
            >>> GitHubWrapper.get_current_branch()
            'feature/new-feature'
        """
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Failed to get current branch: {result.stderr}")

        return result.stdout.strip()

    @staticmethod
    def list_issues(repo: str, state: str = "open") -> List[Dict]:
        """
        List GitHub issues.

        Args:
            repo: Repo in format "owner/repo".
            state: Issue state - "open", "closed", or "all". Defaults to "open".

        Returns:
            List of issue dictionaries.

        Raises:
            Exception: If listing issues fails.

        Example:
            >>> GitHubWrapper.list_issues("owner/repo")
            [{'number': 123, 'title': 'Bug', 'body': '...'}]
        """
        import json

        result = subprocess.run(
            ["gh", "issue", "list", "--repo", repo, "--state", state, "--json", "number,title,body"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Failed to list issues: {result.stderr}")

        return json.loads(result.stdout)


def main() -> None:
    """CLI interface for gh_wrapper.py."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python gh_wrapper.py create-issue --title '...' --body '...' [--labels '...']")
        print("  python gh_wrapper.py create-pr --title '...' --body '...' --base main")
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == "create-issue":
            title = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == "--title"), None)
            body = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == "--body"), None)
            labels_str = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == "--labels"), None)

            if not title or not body:
                print("[ERROR] Missing required: --title and --body")
                sys.exit(1)

            labels = labels_str.split(",") if labels_str else None

            issue_url = GitHubWrapper.create_issue(
                title=title,
                body=body,
                labels=labels
            )
            print(f"[SUCCESS] Issue created: {issue_url}")

        elif command == "create-pr":
            title = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == "--title"), None)
            body = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == "--body"), None)
            base = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == "--base"), "main")
            labels_str = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == "--labels"), None)

            if not title or not body:
                print("[ERROR] Missing required: --title and --body")
                sys.exit(1)

            labels = labels_str.split(",") if labels_str else None

            pr_url = GitHubWrapper.create_pr(
                title=title,
                body=body,
                base=base,
                labels=labels
            )
            print(f"[SUCCESS] PR created: {pr_url}")

        else:
            print(f"[ERROR] Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
