---
mode: "agent"
description: "Commit, push, and merge the testing branch into the main branch after preparing for the merge"
---

# Merge Testing Branch into Main Branch

This prompt is designed to help finalize the integration of changes from the `testing` branch into the `main` branch of the Star Trek Retro Remake repository.

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
git merge testing --no-ff -m "Merge testing branch - UI enhancements and documentation updates"
```

**Option B: Squash and Merge (Clean History)**

```bash
git merge testing --squash
git commit -m "Merge testing branch - UI enhancements and documentation updates

- Added complete Qt Designer main window implementation
- Expanded DESIGN.md with comprehensive architecture details
- Added new prompt files for UI creation and venv initialization
- Updated copilot instructions with branch protection policy
- Fixed minor whitespace issues
- All tests passing (289/292, 3 intentional edge cases documented)"
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

1. **Optional: Delete testing branch locally** (if no longer needed):

   ```bash
   git branch -d testing
   ```

2. **Optional: Delete testing branch remotely** (if no longer needed):

   ```bash
   git push origin --delete testing
   ```

   ⚠️ **WARNING:** Only delete if you're done with the testing branch. The project typically keeps it for ongoing development.

3. **Return to testing branch for continued development** (if keeping it):

   ```bash
   git checkout testing
   git merge main  # Sync testing with main
   ```

4. **Run tests on main branch** to verify everything works:

   ```bash
   git checkout main
   uv run pytest STRR/tests/ -v
   ```

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

### Test Failures (3 edge cases)

The testing branch has 3 intentionally failing tests related to null-checking edge cases:

1. `test_handle_ship_move_request_without_player_ship`
2. `test_handle_combat_action_without_player_ship`
3. `test_is_valid_move_no_sector`

**Status:** These are **intentional design decisions** per project guidelines:

- Project uses "confident design patterns"
- Error handling deferred to v1.0.0
- Code assumes valid state after initialization
- Tests document future v1.0.0 requirements

**Action Required:** None - these are documented as expected behavior for v0.0.x

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

## Expected Changes

After merge, the main branch will include:

- **7 files changed**: +2719 insertions, -618 deletions
- **New UI Files**: Complete Qt Designer main window implementation
- **Documentation**: Major DESIGN.md expansion
- **New Prompts**: UI creation and venv initialization guides
- **Updated Guidelines**: Branch protection policy in copilot instructions
- **Current Version**: v0.0.21

## Success Criteria

The merge is successful when:

1. ✅ Main branch contains all testing branch commits
2. ✅ No merge conflicts remain
3. ✅ Tests pass on main branch (289/292 with 3 documented exceptions)
4. ✅ Remote repository updated
5. ✅ Project documentation reflects merge
6. ✅ Team notified of merge completion

## Additional Notes

- **Branch Strategy**: The project maintains `main` for stable releases and `testing` for active development
- **Code Changes Policy**: All code changes MUST go through `testing` branch first
- **Documentation**: Can be updated directly on `main` after explicit approval
- **Version Numbering**: After merge, consider if next version should increment MINOR or PATCH

## Support

If you encounter issues during the merge process:

1. Check the repository's GitHub Issues page
2. Review the project's ARCHITECTURE.md and DESIGN.md
3. Consult the CHANGELOG.md for recent changes
4. Refer to the merge_prep.prompt.md for preparation details
