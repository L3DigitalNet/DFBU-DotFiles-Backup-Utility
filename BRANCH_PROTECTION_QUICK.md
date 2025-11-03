# Branch Protection - Quick Reference

**For setting up branch protection on new repositories, see `create-branch-protections.prompt.md`**

## 🚨 Golden Rules

1. **ALL development happens on `testing` branch**
2. **NEVER commit directly to `main` branch**
3. **ONLY merge to `main` after testing and approval**
4. **ALWAYS switch back to `testing` after merging**

## For Humans

### Daily Workflow

```bash
# Always work on testing
git checkout testing

# Make changes, commit, test
git add .
git commit -m "your message"

# When ready to promote to main
git checkout main
git merge testing
git checkout testing  # Switch back immediately!
```

### If You Accidentally Switch to Main

```bash
# No changes made yet? Just switch back:
git checkout testing

# Made changes? Stash and move them:
git stash
git checkout testing
git stash pop
```

### Protection Errors

If you see:

```
❌ ERROR: Direct commits to 'main' branch are not allowed!
```

**Solution:**

```bash
git checkout testing  # Switch to testing branch
```

## For AI Agents

### Before ANY File Modification

```python
# Run branch protection check
import subprocess
result = subprocess.run(
    ["python", ".agents/branch_protection.py"],
    capture_output=True
)
if result.returncode != 0:
    # STOP - Cannot modify files
    print(result.stdout.decode())
    exit(1)
```

### Merge Assistance Only

AI can help with merges ONLY when human explicitly says:

- "help me merge testing to main"
- "assist with the merge"
- "I want to merge now"

**Never** suggest or perform file modifications on main.

## Protection Components

| Component | Protects Against | When Active |
|-----------|------------------|-------------|
| `pre-commit` hook | Direct commits to main | Every commit attempt |
| `post-checkout` hook | Forgetting you're on main | After branch switch |
| `post-merge` hook | Staying on main after merge | After merge completes |
| `branch_protection.py` | AI modifications to main | Before AI file operations |
| `memory.instruction.md` | AI violations | Every AI session |

## Testing Protection

```bash
# Test 1: Try to commit to main (should fail)
git checkout main
touch test.txt
git add test.txt
git commit -m "test"  # ❌ Will be blocked

# Test 2: Switch to main (should warn)
git checkout main  # ⚠️ Will display warning

# Test 3: AI protection script
git checkout main
python .agents/branch_protection.py  # ❌ Exit code 1

git checkout testing
python .agents/branch_protection.py  # ✅ Exit code 0
```

## Emergency Override

**Only use in genuine emergencies:**

```bash
# Disable pre-commit hook temporarily
git commit --no-verify

# Or rename hook
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
# ... do emergency work ...
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
```

## Summary

✅ **testing** = development, commits, changes, testing
❌ **main** = merges only, read-only otherwise

**Remember:** After every merge to main, immediately return to testing!
