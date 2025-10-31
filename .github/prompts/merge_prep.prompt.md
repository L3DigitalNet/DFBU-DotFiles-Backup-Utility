---
mode: "agent"
description: "Prepare the repository for merging changes from a feature branch into the main branch"
---

# Prepare for Merge

This prompt is designed to help prepare the Star Trek Retro Remake repository for merging changes from a feature branch into the main branch.

## Pre-Merge Checklist

Before merging, ensure the following steps are completed, call the associated .prompt.md file(s) as needed):

1. **Code Review**
   - All changes have been reviewed by at least one other developer.
   - Code adheres to project coding standards and best practices.

2. **Testing**
   - All new features are covered by unit tests.
   - Existing tests pass without modification.
   - Run the test suite to confirm no regressions:
     ```bash
     python -m pytest STRR/tests/ -v
     ```

3. **Documentation**
   - Update any relevant documentation (e.g., README, API docs).
   - Ensure all new public methods/classes are documented.

4. **Changelog**
   - Update the changelog to include a summary of changes.
   - Follow the established format for changelog entries.

5. **Merge Conflicts**
   - Resolve any merge conflicts with the main branch.
   - Rebase the feature branch onto the latest main branch:
     ```bash
     git fetch origin
     git rebase origin/main
     ```

6. **Final Verification**
   - Perform a final round of testing on the rebased branch.
   - Confirm all changes are as expected before merging.

## Merge Process

Once the checklist is complete, proceed with the merge:

1. **Create a Pull Request**
   - Open a pull request (PR) from the feature branch to the main branch.
   - Include a summary of changes and any relevant context.

2. **Approval**
   - Obtain approval from at least one other developer.
   - Address any feedback or requested changes.

3. **Merge**
   - Once approved, merge the PR into the main branch.
   - Use a "squash and merge" strategy to maintain a clean commit history.

4. **Post-Merge Tasks**
   - Delete the feature branch to keep the repository tidy.
   - Monitor the main branch for any issues that arise from the merge.
