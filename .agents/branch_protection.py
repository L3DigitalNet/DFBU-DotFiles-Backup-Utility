#!/usr/bin/env python3
"""
Branch Protection Checker for AI Agents
This script MUST be called before any AI agent makes file modifications.
"""
import subprocess
import sys
from pathlib import Path


def get_current_branch() -> str:
    """Get the current Git branch name."""
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout.strip()


def is_merge_in_progress() -> bool:
    """Check if a merge is currently in progress."""
    git_dir = Path(".git")
    return (git_dir / "MERGE_HEAD").exists()


def check_branch_protection() -> tuple[bool, str]:
    """
    Check if the current branch allows modifications.

    Returns:
        tuple: (is_allowed, message)
    """
    try:
        current_branch = get_current_branch()

        # Check if we're on main
        if current_branch == "main":
            # Only allow if we're in the middle of a merge
            if is_merge_in_progress():
                return True, "✓ Merge in progress on main branch - modifications allowed"
            else:
                return False, (
                    "❌ PROTECTION VIOLATION: Cannot modify files on 'main' branch!\n"
                    "\n"
                    "The 'main' branch is protected. AI agents must:\n"
                    "  1. Verify they are on 'testing' branch\n"
                    "  2. Make all modifications on 'testing' branch\n"
                    "  3. Only assist with merges when explicitly authorized by human\n"
                    "\n"
                    "Current branch: main\n"
                    "Required branch: testing\n"
                    "\n"
                    "To switch to testing branch, the human should run:\n"
                    "  git checkout testing"
                )

        # Allow modifications on other branches
        return True, f"✓ Branch protection check passed - modifications allowed on '{current_branch}'"

    except subprocess.CalledProcessError as e:
        return False, f"❌ Error checking Git branch: {e}"
    except Exception as e:
        return False, f"❌ Unexpected error: {e}"


def main():
    """Main entry point for branch protection check."""
    is_allowed, message = check_branch_protection()

    print(message)

    if not is_allowed:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
