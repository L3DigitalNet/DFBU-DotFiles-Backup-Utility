---
mode: "agent"
description: "Commit, push, and merge the testing branch into the main branch after preparing for the merge"
---

# Merge Testing Branch into Main Branch

This prompt is designed to help finalize the integration of changes from the `testing` branch into the `main` branch of the DFBU repository.

## 🔓 Branch Protection Exception

**IMPORTANT:** When this prompt is executed by a human using the `/merge_testing_to_main` command, AI agents are authorized to modify the `main` branch as part of the merge process. This is an explicit exception to the standard branch protection policy that prohibits AI agents from autonomously modifying `main`.

## Prerequisites

Before running this prompt, ensure you have completed the merge preparation checklist:

1. ✅ All tests are passing (or documented exceptions explained)
2. ✅ No merge conflicts with `main` branch
3. ✅ Documentation is up to date
4. ✅ Changelog reflects all changes
5. ✅ Code review completed
6. ✅ Currently on `testing` branch

## Merge Process

This prompt will guide you through the following steps:

### Step 1: Final Status Check

Verify current branch and status:

```bash
git status
git branch --show-current
```

Ensure you are on the `testing` branch with no uncommitted changes.

### Step 2: Commit Any Remaining Changes

If there are any uncommitted changes, commit them:

```bash
git add .
git commit -m "chore: final merge preparation updates"
```

### Step 3: Push Testing Branch to Remote

Ensure the testing branch is up to date on the remote:

```bash
git push origin testing
```

### Step 4: Switch to Main Branch

Switch to the main branch and ensure it's up to date:

**Note:** This step involves switching to and modifying the `main` branch, which is normally prohibited for AI agents. However, since this is a human-initiated merge process using the `/merge_testing_to_main` command, AI agents are authorized to perform these operations.

```bash
git checkout main
git pull origin main
```

### Step 5: Merge Testing into Main

Merge the testing branch into main using the project's preferred strategy:

**Option A: Merge Commit (Preserves History)**

```bash
git merge testing --no-ff -m "Merge testing branch - Updates and improvements"
```

**Option B: Squash and Merge (Clean History)**

```bash
git merge testing --squash
git commit -m "Merge testing branch - Updates and improvements

[Summarize the changes being merged from testing branch]
"
```

### Step 6: Push Main Branch to Remote

Push the merged main branch:

```bash
git push origin main
```

### Step 7: Verify Merge Success

Confirm the merge was successful:

```bash
git log --oneline -10
git diff origin/main..HEAD
```

The diff should show no differences if the push was successful.

### Step 8: Post-Merge Tasks

After successful merge:

1. **Keep testing branch for ongoing development**:

   ```bash
   git checkout testing
   git merge main  # Sync testing with main
   ```

2. **Run tests to verify everything works**:

   ```bash
   uv run pytest DFBU/tests/ -v
   ```

   ⚠️ **NOTE:** The project maintains `testing` branch for active development. Do not delete it.

## Rollback Procedure

If something goes wrong after merging to main, you can rollback:

### Before Pushing to Remote

If you haven't pushed yet:

```bash
git reset --hard HEAD~1  # Undo the merge commit
```

### After Pushing to Remote

If you've already pushed:

```bash
# Create a revert commit
git revert -m 1 HEAD
git push origin main
```

Or reset to a specific commit (requires force push):

```bash
git reset --hard <commit-hash-before-merge>
git push origin main --force
```

⚠️ **Use force push with extreme caution** - coordinate with team first.

## Known Issues

### Test Status

Check current test status with:

```bash
uv run pytest DFBU/tests/ -v
```

**Note:** Per project guidelines:

- Project uses "confident design patterns"
- Error handling deferred to v1.0.0 (unless critical)
- Tests should focus on happy path and core functionality before v1.0.0

**Action Required:** Review and document any failing tests before merge

## Merge Checklist Summary

- [ ] Verify current branch is `testing`
- [ ] Commit any uncommitted changes
- [ ] Push testing branch to remote
- [ ] Switch to main branch
- [ ] Pull latest main branch
- [ ] Merge testing into main (choose strategy)
- [ ] Push main branch to remote
- [ ] Verify merge success
- [ ] Run tests on main branch
- [ ] Complete post-merge tasks
- [ ] Document merge in project tracking

## Success Criteria

The merge is successful when:

1. ✅ Main branch contains all testing branch commits
2. ✅ No merge conflicts remain
3. ✅ Tests pass on main branch
4. ✅ Remote repository updated
5. ✅ Project documentation reflects merge
6. ✅ Changelog is up to date

## Additional Notes

- **Branch Strategy**: The project maintains `main` for stable releases and `testing` for active development
- **Code Changes Policy**: All code changes MUST go through `testing` branch first
- **Documentation**: Should be updated in `testing` branch and merged with code changes
- **Version Numbering**: After merge, consider if next version should increment MINOR or PATCH

## Support

If you encounter issues during the merge process:

1. Check the repository's GitHub Issues page
2. Review the project's documentation in `/DFBU/docs/`
3. Consult the CHANGELOG.md for recent changes
4. Refer to the merge_prep.prompt.md for preparation details
