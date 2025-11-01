#!/usr/bin/env bash
# Setup script for Git hooks and testing branch
# Run this script after cloning the repository to set up branch protection

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_FILE="$REPO_ROOT/.git/hooks/pre-commit"

echo "🔧 Setting up Git branch protection..."
echo ""

# Create the pre-commit hook
cat > "$HOOK_FILE" << 'EOF'
#!/usr/bin/env bash
# Pre-commit hook to prevent commits to main branch
# This enforces the repository policy that all code changes must be made on the testing branch

BRANCH=$(git symbolic-ref HEAD 2>/dev/null | sed 's#refs/heads/##')

if [ "$BRANCH" = "main" ]; then
    echo "⛔ COMMIT BLOCKED: You are on the 'main' branch"
    echo ""
    echo "Repository policy: All code changes must be made on the 'testing' branch."
    echo ""
    echo "To fix this:"
    echo "  1. Switch to testing branch: git checkout testing"
    echo "  2. If testing branch doesn't exist: git checkout -b testing"
    echo "  3. Make your changes and commit there"
    echo ""
    echo "Only merge to main after review."
    exit 1
fi

exit 0
EOF

# Make the hook executable
chmod +x "$HOOK_FILE"
echo "✅ Pre-commit hook installed at .git/hooks/pre-commit"

# Check if testing branch exists
if git show-ref --verify --quiet refs/heads/testing; then
    echo "✅ Testing branch already exists"
else
    echo "📝 Creating testing branch..."
    git branch testing
    echo "✅ Testing branch created"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  • Switch to testing branch: git checkout testing"
echo "  • Make your changes on the testing branch"
echo "  • Commits to 'main' are now blocked"
echo ""
