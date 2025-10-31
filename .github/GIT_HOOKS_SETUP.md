# Git Hook Setup

## Quick Start

After cloning this repository, run:

```bash
./setup-git-hooks.sh
```

This will:

- Install a pre-commit hook that prevents commits to `main` branch
- Create the `testing` branch if it doesn't exist
- Ensure you follow the repository's branch protection policy

## Branch Protection Policy

All code changes must be made on the `testing` branch, not `main`. The pre-commit hook enforces this automatically.

## Manual Setup

If you prefer to set up manually:

1. Copy the pre-commit hook:

   ```bash
   cp .git/hooks/pre-commit.sample .git/hooks/pre-commit
   # Or create from scratch - see setup-git-hooks.sh for content
   ```

2. Make it executable:

   ```bash
   chmod +x .git/hooks/pre-commit
   ```

3. Create testing branch if needed:

   ```bash
   git branch testing
   git checkout testing
   ```

## Bypassing the Hook

If you absolutely need to bypass the hook (rare cases only):

```bash
git commit --no-verify
```

**Warning:** Only bypass this protection when explicitly approved, such as during a human-initiated merge process.
