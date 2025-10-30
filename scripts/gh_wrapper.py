#!/usr/bin/env python3
"""GitHub CLI wrapper utilities for LAZY-DEV-FRAMEWORK."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Optional


class GitHubError(RuntimeError):
    """Base error for GitHub CLI failures."""


def run_command(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise GitHubError(result.stderr.strip() or "Unknown GitHub CLI error")
    return result.stdout.strip()


def create_issue(
    title: str,
    body: str,
    *,
    labels: Optional[list[str]] = None,
    milestone: Optional[str] = None,
    assignee: Optional[str] = None,
    repo: Optional[str] = None,
) -> str:
    command = ["gh", "issue", "create", "--title", title, "--body", body]
    if labels:
        command.extend(["--label", ",".join(labels)])
    if milestone:
        command.extend(["--milestone", milestone])
    if assignee:
        command.extend(["--assignee", assignee])
    if repo:
        command.extend(["--repo", repo])
    return run_command(command)


def create_pr(
    title: str,
    body: str,
    *,
    base: str = "main",
    head: Optional[str] = None,
    labels: Optional[list[str]] = None,
    repo: Optional[str] = None,
) -> str:
    command = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base]
    if head:
        command.extend(["--head", head])
    if labels:
        command.extend(["--label", ",".join(labels)])
    if repo:
        command.extend(["--repo", repo])
    return run_command(command)


def list_issues(repo: str, *, state: str = "open") -> list[dict]:
    command = [
        "gh",
        "issue",
        "list",
        "--repo",
        repo,
        "--state",
        state,
        "--json",
        "number,title,body,url",
    ]
    output = run_command(command)
    return json.loads(output)


def get_current_branch() -> str:
    return run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GitHub CLI wrapper.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    issue_parser = subparsers.add_parser("create-issue", help="Create a GitHub issue")
    issue_parser.add_argument("--title", required=True)
    issue_parser.add_argument("--body", required=True)
    issue_parser.add_argument("--labels")
    issue_parser.add_argument("--milestone")
    issue_parser.add_argument("--assignee")
    issue_parser.add_argument("--repo")

    pr_parser = subparsers.add_parser("create-pr", help="Create a GitHub pull request")
    pr_parser.add_argument("--title", required=True)
    pr_parser.add_argument("--body", required=True)
    pr_parser.add_argument("--base", default="main")
    pr_parser.add_argument("--head")
    pr_parser.add_argument("--labels")
    pr_parser.add_argument("--repo")

    list_parser = subparsers.add_parser("list-issues", help="List GitHub issues")
    list_parser.add_argument("--repo", required=True)
    list_parser.add_argument(
        "--state", default="open", choices=["open", "closed", "all"]
    )

    subparsers.add_parser("current-branch", help="Print the current git branch")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "create-issue":
            labels = args.labels.split(",") if args.labels else None
            issue_url = create_issue(
                args.title,
                args.body,
                labels=labels,
                milestone=args.milestone,
                assignee=args.assignee,
                repo=args.repo,
            )
            print(f"✅ Issue created: {issue_url}")
            return 0
        if args.command == "create-pr":
            labels = args.labels.split(",") if args.labels else None
            pr_url = create_pr(
                args.title,
                args.body,
                base=args.base,
                head=args.head,
                labels=labels,
                repo=args.repo,
            )
            print(f"✅ PR created: {pr_url}")
            return 0
        if args.command == "list-issues":
            issues = list_issues(args.repo, state=args.state)
            print(json.dumps(issues, indent=2))
            return 0
        if args.command == "current-branch":
            print(get_current_branch())
            return 0
    except GitHubError as exc:
        print(f"❌ Error: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
