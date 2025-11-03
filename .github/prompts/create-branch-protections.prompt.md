# Create Branch Protections - Setup Prompt

## Overview

This prompt sets up comprehensive branch protection for a Git repository to prevent accidental modifications to the `main` branch by both humans and AI agents. The protection system enforces a workflow where all development happens on a `testing` branch, with `main` reserved exclusively for receiving tested, approved merges.

## Protection Components to Create

### 1. Git Hooks (Human Protection)

Create three Git hooks in `.git/hooks/` directory:

#### Pre-Commit Hook (`.git/hooks/pre-commit`)

```bash
#!/bin/bash
# Pre-commit hook to prevent direct commits to main branch

BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Allow commits during merge operations
if [ -f .git/MERGE_HEAD ]; then
    exit 0
fi

# Block commits to main branch
if [ "$BRANCH" = "main" ]; then
    echo ""
    echo "❌ ERROR: Direct commits to 'main' branch are not allowed!"
    echo ""
    echo "The main branch is protected. You should:"
    echo "  1. Switch to the testing branch: git checkout testing"
    echo "  2. Make your changes and commit them there"
    echo "  3. Merge to main only when ready: git checkout main && git merge testing"
    echo "  4. Switch back immediately: git checkout testing"
    echo ""
    echo "Current branch: $BRANCH"
    echo "Required branch: testing"
    echo ""
    exit 1
fi

exit 0
```

#### Post-Checkout Hook (`.git/hooks/post-checkout`)

```bash
#!/bin/bash
# Post-checkout hook to warn when switching to main branch

PREVIOUS_HEAD=$1
NEW_HEAD=$2
BRANCH_SWITCH=$3

# Only run for branch checkouts (not file checkouts)
if [ "$BRANCH_SWITCH" = "1" ]; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

    if [ "$CURRENT_BRANCH" = "main" ]; then
        echo ""
        echo "⚠️  WARNING: You are now on the PROTECTED 'main' branch!"
        echo ""
        echo "The main branch is reserved for merges only. Please:"
        echo "  • Do NOT make changes directly on this branch"
        echo "  • Use 'git checkout testing' to return to development"
        echo "  • Only stay on main for merging from testing"
        echo ""
        echo "Press Enter to acknowledge this warning..."
        read -r
    fi
fi

exit 0
```

#### Post-Merge Hook (`.git/hooks/post-merge`)

```bash
#!/bin/bash
# Post-merge hook to remind switching back to testing after merge

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" = "main" ]; then
    echo ""
    echo "✅ Merge completed on main branch"
    echo ""
    echo "🔄 IMPORTANT: Switch back to testing branch now!"
    echo ""
    echo "Run this command to continue development:"
    echo "  git checkout testing"
    echo ""
    echo "Remember: main branch is only for receiving merges."
    echo "All development should happen on testing branch."
    echo ""
fi

exit 0
```

**After creating hooks, make them executable:**

```bash
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-checkout
chmod +x .git/hooks/post-merge
```

### 2. AI Agent Protection Script

Create or verify `.agents/branch_protection.py` exists with proper functionality:

```python
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
```

**Make the script executable:**

```bash
chmod +x .agents/branch_protection.py
```

### 3. Testing Branch Creation

Ensure the `testing` branch exists and is set up:

```bash
# Create testing branch if it doesn't exist
git checkout -b testing 2>/dev/null || git checkout testing

# Push testing branch to remote (if remote exists)
git push -u origin testing 2>/dev/null || true

# Switch back to main to verify protection
git checkout main
```

### 4. AI Agent Memory Update

Ensure `.agents/memory.instruction.md` contains proper branch protection rules. If the file doesn't exist, create it. If it exists, ensure it contains the branch protection section:

```markdown
# ⚠️ CRITICAL: Branch Protection Rules (MANDATORY FOR ALL AI AGENTS)

**BEFORE ANY FILE MODIFICATIONS, AI AGENTS MUST:**

1. **Check current Git branch** using: `git branch --show-current`
2. **Verify branch is NOT 'main'** (unless explicitly authorized for merge assistance)
3. **Run branch protection check**: `python .agents/branch_protection.py`

## Branch Usage Rules

- **testing branch**: All development, modifications, and commits happen here
- **main branch**: PROTECTED - Only for merges from testing (human-approved only)

## AI Agent Restrictions

❌ **NEVER** make file changes on the 'main' branch
❌ **NEVER** commit to the 'main' branch
❌ **NEVER** suggest changes to files when on 'main' branch
✅ **ALWAYS** verify branch before any file operations
✅ **ONLY** assist with merges when human gives explicit permission

## Exception: Merge Assistance

When human explicitly requests merge assistance:

1. Human must be on 'main' branch
2. Human must explicitly say "help me merge" or similar authorization
3. AI can guide through: `git merge testing`
4. After merge, AI must remind human to switch back: `git checkout testing`

## Enforcement

The following protections are in place:

- Git pre-commit hook: Blocks commits to main
- Git post-checkout hook: Warns when switching to main
- Git post-merge hook: Reminds to switch back to testing
- Python script: `.agents/branch_protection.py` - AI agents should check this before modifications

**If AI agent detects it's on 'main' branch without explicit merge authorization, it must:**

1. Refuse to make any file changes
2. Inform human of the protection violation
3. Suggest switching to testing: `git checkout testing`
```

### 5. Documentation Updates

Update the main documentation files to reference the new protection system:

#### README.md Updates

Add to the "Branch Protection" section:

```markdown
## Branch Protection Setup

To set up branch protection on this repository, run the setup process:

1. **Automated Setup**: Run the branch protection setup script (if available)
2. **Manual Setup**: Follow the instructions in `create-branch-protections.prompt.md`

The protection system includes:

- **Git Hooks**: Prevent human mistakes (pre-commit, post-checkout, post-merge)
- **AI Agent Script**: Blocks AI modifications to main (`.agents/branch_protection.py`)
- **Documentation**: Clear rules and workflows for all contributors
```

#### New Quick Setup Script (Optional)

Create `setup-branch-protection.sh`:

```bash
#!/bin/bash
# Setup script for branch protection system

echo "Setting up branch protection system..."

# Create .agents directory if it doesn't exist
mkdir -p .agents

# Create Git hooks directory
mkdir -p .git/hooks

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to prevent direct commits to main branch

BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Allow commits during merge operations
if [ -f .git/MERGE_HEAD ]; then
    exit 0
fi

# Block commits to main branch
if [ "$BRANCH" = "main" ]; then
    echo ""
    echo "❌ ERROR: Direct commits to 'main' branch are not allowed!"
    echo ""
    echo "The main branch is protected. You should:"
    echo "  1. Switch to the testing branch: git checkout testing"
    echo "  2. Make your changes and commit them there"
    echo "  3. Merge to main only when ready: git checkout main && git merge testing"
    echo "  4. Switch back immediately: git checkout testing"
    echo ""
    echo "Current branch: $BRANCH"
    echo "Required branch: testing"
    echo ""
    exit 1
fi

exit 0
EOF

# Create post-checkout hook
cat > .git/hooks/post-checkout << 'EOF'
#!/bin/bash
# Post-checkout hook to warn when switching to main branch

PREVIOUS_HEAD=$1
NEW_HEAD=$2
BRANCH_SWITCH=$3

# Only run for branch checkouts (not file checkouts)
if [ "$BRANCH_SWITCH" = "1" ]; then
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

    if [ "$CURRENT_BRANCH" = "main" ]; then
        echo ""
        echo "⚠️  WARNING: You are now on the PROTECTED 'main' branch!"
        echo ""
        echo "The main branch is reserved for merges only. Please:"
        echo "  • Do NOT make changes directly on this branch"
        echo "  • Use 'git checkout testing' to return to development"
        echo "  • Only stay on main for merging from testing"
        echo ""
        echo "Press Enter to acknowledge this warning..."
        read -r
    fi
fi

exit 0
EOF

# Create post-merge hook
cat > .git/hooks/post-merge << 'EOF'
#!/bin/bash
# Post-merge hook to remind switching back to testing after merge

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$CURRENT_BRANCH" = "main" ]; then
    echo ""
    echo "✅ Merge completed on main branch"
    echo ""
    echo "🔄 IMPORTANT: Switch back to testing branch now!"
    echo ""
    echo "Run this command to continue development:"
    echo "  git checkout testing"
    echo ""
    echo "Remember: main branch is only for receiving merges."
    echo "All development should happen on testing branch."
    echo ""
fi

exit 0
EOF

# Make hooks executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-checkout
chmod +x .git/hooks/post-merge

# Ensure branch protection script exists and is executable
if [ -f .agents/branch_protection.py ]; then
    chmod +x .agents/branch_protection.py
    echo "✓ Made .agents/branch_protection.py executable"
else
    echo "⚠️  Warning: .agents/branch_protection.py not found"
    echo "   Please ensure this file exists for AI agent protection"
fi

# Create testing branch if it doesn't exist
git checkout -b testing 2>/dev/null || git checkout testing
echo "✓ Ensured testing branch exists and is current"

echo ""
echo "✅ Branch protection setup completed!"
echo ""
echo "Protection components installed:"
echo "  • Pre-commit hook (prevents commits to main)"
echo "  • Post-checkout hook (warns when on main)"
echo "  • Post-merge hook (reminds to switch back)"
echo "  • Testing branch (ready for development)"
echo ""
echo "Next steps:"
echo "  1. Verify .agents/branch_protection.py exists"
echo "  2. Test protection: 'git checkout main && touch test && git add test && git commit -m test'"
echo "  3. Start development: 'git checkout testing'"
echo ""
```

Make the setup script executable:

```bash
chmod +x setup-branch-protection.sh
```

## Testing the Protection System

After setup, test each component:

### Test 1: Git Hook Protection

```bash
# Switch to main and try to commit (should be blocked)
git checkout main
echo "test" > test.txt
git add test.txt
git commit -m "test commit"
# Expected: Error message blocking the commit

# Clean up
rm test.txt
git checkout testing
```

### Test 2: Checkout Warning

```bash
# Switch to main (should show warning)
git checkout main
# Expected: Warning message and prompt

# Switch back
git checkout testing
```

### Test 3: AI Agent Protection

```bash
# Test from main branch
git checkout main
python .agents/branch_protection.py
# Expected: Exit code 1 with error message

# Test from testing branch
git checkout testing
python .agents/branch_protection.py
# Expected: Exit code 0 with success message
```

### Test 4: Merge Workflow

```bash
# Simulate proper merge workflow
git checkout testing
echo "feature" > feature.txt
git add feature.txt
git commit -m "Add feature"

git checkout main
git merge testing
# Expected: Post-merge hook reminder

git checkout testing
# Ready for continued development
```

## Usage Instructions

### For Repository Maintainers

1. **Initial Setup**: Run all the commands above to install protection
2. **Team Onboarding**: Ensure all team members understand the workflow
3. **CI/CD Integration**: Configure pipelines to work with testing/main workflow
4. **Periodic Testing**: Verify protection components remain functional

### For Developers

1. **Daily Workflow**: Always work on `testing` branch
2. **Feature Completion**: Merge to `main` only when ready for release
3. **Post-Merge**: Immediately switch back to `testing` branch
4. **Error Recovery**: Use provided commands if accidentally on `main`

### For AI Agents

1. **Pre-Modification Check**: Always run `python .agents/branch_protection.py`
2. **Branch Verification**: Check current branch before any file operations
3. **Merge Assistance**: Only help with merges when explicitly authorized
4. **Protection Respect**: Never bypass or circumvent protection measures

## Benefits

This protection system provides:

✅ **Prevents Accidental Commits**: Git hooks block direct commits to main
✅ **Enforces Workflow**: Clear separation between development and release branches
✅ **Human-Friendly**: Clear error messages and recovery instructions
✅ **AI-Safe**: Prevents AI agents from corrupting protected branches
✅ **Merge-Aware**: Allows necessary merge operations while protecting normal development
✅ **Self-Documenting**: Protection messages include instructions for resolution
✅ **Testable**: Each component can be independently verified and tested

## Implementation Priority

1. **Git Hooks** (highest priority - protects against human errors)
2. **AI Protection Script** (high priority - protects against AI errors)
3. **Testing Branch Setup** (medium priority - establishes workflow)
4. **Documentation Updates** (medium priority - ensures clarity)
5. **Setup Scripts** (low priority - convenience for new repositories)

Implement in this order to establish protection as quickly as possible while building toward a complete system.