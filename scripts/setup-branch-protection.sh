#!/bin/bash
# Branch Protection Setup Script
# Automatically sets up comprehensive branch protection for the repository

set -e

echo "🔒 Setting up Branch Protection System..."
echo ""

# Create .agents directory if it doesn't exist
mkdir -p .agents
echo "✓ Ensured .agents directory exists"

# Create Git hooks directory if it doesn't exist
mkdir -p .git/hooks
echo "✓ Ensured .git/hooks directory exists"

# Check if we're in a Git repository
if [ ! -d .git ]; then
    echo "❌ Error: Not in a Git repository"
    echo "   Please run this script from the root of a Git repository"
    exit 1
fi

echo ""
echo "📝 Installing Git hooks..."

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

# Run mypy type checking on staged Python files
STAGED_PY=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' | grep '^DFBU/' || true)
if [ -n "$STAGED_PY" ]; then
    echo "Running mypy type check..."
    if ! python -m mypy DFBU/ 2>/dev/null; then
        echo ""
        echo "❌ mypy type check failed. Fix type errors before committing."
        echo "   Run 'mypy DFBU/' to see the full error output."
        exit 1
    fi
    echo "✓ mypy type check passed"
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

echo "✓ Installed pre-commit hook (prevents commits to main)"
echo "✓ Installed post-checkout hook (warns when on main)"
echo "✓ Installed post-merge hook (reminds to switch back)"

# Check if branch protection script exists and make it executable
if [ -f .agents/branch_protection.py ]; then
    chmod +x .agents/branch_protection.py
    echo "✓ Made .agents/branch_protection.py executable"
else
    echo "⚠️  Warning: .agents/branch_protection.py not found"
    echo "   This file is required for AI agent protection"
    echo "   Please ensure it exists with proper content"
fi

echo ""
echo "🌿 Setting up testing branch..."

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

# Create testing branch if it doesn't exist
if git show-ref --verify --quiet refs/heads/testing; then
    echo "✓ Testing branch already exists"
else
    git checkout -b testing
    echo "✓ Created testing branch"
fi

# Ensure we're on testing branch for development
if [ "$CURRENT_BRANCH" != "testing" ]; then
    git checkout testing
    echo "✓ Switched to testing branch for development"
fi

# Try to push testing branch to remote (if remote exists and we have push access)
if git remote get-url origin >/dev/null 2>&1; then
    if git push -u origin testing >/dev/null 2>&1; then
        echo "✓ Pushed testing branch to origin"
    else
        echo "ℹ️  Could not push testing branch to remote (may not have push access)"
    fi
fi

echo ""
echo "🧪 Testing protection system..."

# Test the protection by trying to switch to main
echo "Testing checkout warning..."
if git checkout main >/dev/null 2>&1; then
    echo "✓ Protection system installed - main branch accessible"

    # Switch back to testing immediately
    git checkout testing >/dev/null 2>&1
    echo "✓ Switched back to testing branch"
else
    echo "⚠️  Could not test main branch checkout (branch may not exist)"
fi

# Test AI protection script if it exists
if [ -f .agents/branch_protection.py ]; then
    echo "Testing AI protection script..."
    if python3 .agents/branch_protection.py >/dev/null 2>&1; then
        echo "✓ AI protection script working correctly"
    else
        echo "⚠️  AI protection script may have issues"
    fi
fi

echo ""
echo "✅ Branch Protection Setup Complete!"
echo ""
echo "🛡️  Protection components installed:"
echo "   • Pre-commit hook (prevents commits to main)"
echo "   • Post-checkout hook (warns when on main)"
echo "   • Post-merge hook (reminds to switch back)"
echo "   • Testing branch (ready for development)"
echo ""
echo "🔍 To verify the protection works:"
echo "   1. Try committing to main: 'git checkout main && touch test && git add test && git commit -m test'"
echo "   2. Check AI protection: 'python .agents/branch_protection.py' (should work on testing, fail on main)"
echo ""
echo "📋 Daily workflow:"
echo "   • All development: git checkout testing"
echo "   • When ready to release: git checkout main && git merge testing && git checkout testing"
echo ""
echo "📚 For more information, see:"
echo "   • create-branch-protections.prompt.md (setup guide)"
echo "   • BRANCH_PROTECTION.md (complete documentation)"
echo "   • BRANCH_PROTECTION_QUICK.md (quick reference)"
echo ""
echo "🎯 Current branch: $(git rev-parse --abbrev-ref HEAD) (ready for development)"