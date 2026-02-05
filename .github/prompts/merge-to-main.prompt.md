---
mode: "agent"
description: "Complete end-to-end merge process from preparation to integration"
---

# Complete Feature Branch Merge Process

Execute the complete process for merging a feature branch into the main branch of the PySide6 MVVM desktop application repository, including preparation, validation, and integration.

## Overview

This prompt guides you through the entire merge workflow:

1. **Pre-merge preparation and validation**
2. **Final testing and documentation updates**
3. **Merge execution and verification**
4. **Post-merge cleanup and validation**

## Phase 1: Pre-Merge Preparation

### Step 1: Architecture and Code Quality Review

**MVVM Architecture Validation:**

- [ ] **Model Layer**: No Qt imports, pure business logic only
- [ ] **ViewModel Layer**: QObject-based, proper signal/slot usage
- [ ] **View Layer**: UI-only concerns, minimal logic
- [ ] **Service Layer**: External integrations properly abstracted
- [ ] **Dependency Injection**: Used throughout, no hardcoded dependencies
- [ ] **SOLID Principles**: All principles maintained across layers

**Code Standards Check:**

```bash
# Type checking
mypy DFBU/

# Linting and formatting
ruff check DFBU/ DFBU/tests/
ruff format --check DFBU/ DFBU/tests/
```

### Step 2: Comprehensive Testing

**Run Full Test Suite:**

```bash
# All tests with coverage
pytest DFBU/tests/ -v --cov=DFBU --cov-report=html --cov-report=term

# Specific test categories
pytest DFBU/tests/ -m unit -v            # Unit tests
pytest DFBU/tests/ -m integration -v     # Integration tests

# Test specific patterns
pytest -k "viewmodel" DFBU/tests/ -v     # ViewModel tests
pytest -k "model" DFBU/tests/ -v         # Model tests
```

**Testing Checklist:**

- [ ] All new features have unit tests (90%+ coverage for ViewModels, 95%+ for Models)
- [ ] Integration tests for complete workflows
- [ ] Qt-specific tests use `pytest-qt` and `qtbot`
- [ ] Mock external dependencies appropriately
- [ ] Test both success and failure paths
- [ ] Edge cases and null-checking scenarios covered

**Known Test Exceptions (Document if applicable):**

If there are intentionally failing tests, document them:

```markdown
### Expected Test Failures

The following tests are expected to fail as part of the current design:

1. `test_handle_x_without_y` - Deferred error handling for v1.0.0
2. `test_validation_edge_case` - Confident design pattern in use
3. `test_null_check_scenario` - Future v1.0.0 requirement

**Status:** Documented design decisions per project guidelines
**Action:** None required for merge
```

### Step 3: Documentation and Changelog

**Documentation Updates:**

- [ ] **README.md**: Updated with new features/changes
- [ ] **AGENTS.md**: Updated if architecture patterns changed
- [ ] **API Documentation**: Docstrings added for all public methods/classes
- [ ] **Type Hints**: Present and accurate on all functions/methods

**Changelog Update:**

```bash
# Update CHANGELOG.md with semantic versioning
# Example format:

## [Unreleased]

### Added
- New ViewModel for [feature] with reactive data binding
- Service layer implementation for [external integration]
- Comprehensive test suite with 95% coverage

### Changed
- Improved error handling in [component]
- Updated dependencies to latest compatible versions

### Fixed
- Threading issue in background operations
- Memory leak in widget cleanup

### Documentation
- Added architecture diagrams
- Updated API documentation
- Expanded testing guidelines
```

### Step 4: Merge Conflict Resolution

**Sync with Main Branch:**

```bash
# Fetch latest main
git fetch origin main

# Check for conflicts
git merge-base HEAD origin/main
git diff origin/main...HEAD

# Rebase onto main if needed
git rebase origin/main

# If conflicts occur, resolve them:
# 1. Edit conflicted files
# 2. git add <resolved-files>
# 3. git rebase --continue
# 4. Re-run tests after resolution
```

**Post-Rebase Validation:**

```bash
# Ensure tests still pass after rebase
pytest DFBU/tests/ -v

# Verify application version or startup
python -c "import DFBU; print(DFBU.__version__)"
```

## Phase 2: Merge Execution

### Step 5: Final Pre-Merge Validation

**Current Status Check:**

```bash
# Verify clean working directory
git status
git branch --show-current

# Verify all changes committed
git diff --cached
git diff HEAD

# Confirm branch and commit history
git log --oneline -10
```

**Prerequisites Verification:**

- [ ] Currently on feature/testing branch
- [ ] No uncommitted changes
- [ ] All tests passing (with documented exceptions)
- [ ] Documentation updated
- [ ] Changelog reflects all changes
- [ ] No merge conflicts with main
- [ ] Code review completed and approved

### Step 6: Execute Merge

**Commit Final Changes (if any):**

```bash
# If there are any uncommitted changes
git add .
git commit -m "chore: final merge preparation updates

- Updated documentation
- Resolved merge conflicts
- Finalized test coverage"
```

**Push Feature Branch:**

```bash
# Ensure remote branch is current
git push origin feature-branch-name

# Verify push successful
git status
```

**Switch to Main and Merge:**

```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Choose merge strategy based on project preference:
```

**Option A: Merge Commit (Preserves Development History):**

```bash
git merge feature-branch-name --no-ff -m "Merge feature: [descriptive name]

## Summary
- Implemented [primary feature/capability]
- Added comprehensive MVVM architecture for [component]
- Enhanced [existing functionality]

## Technical Details
- Added [X] new ViewModels with reactive data binding
- Implemented Service layer for [external integration]
- Created [X] new Models with validation logic
- Updated Views to support [new functionality]

## Testing
- Added [X] unit tests with [Y]% coverage
- Implemented integration tests for complete workflows
- All existing tests passing (XXX/XXX with [N] documented exceptions)

## Documentation
- Updated README and architecture documentation
- Added API documentation for all public interfaces
- Expanded development guidelines

## Compatibility
- Maintains backward compatibility
- No breaking changes to existing APIs
- Follows semantic versioning: v[X.Y.Z]"
```

**Option B: Squash and Merge (Clean Linear History):**

```bash
git merge feature-branch-name --squash

git commit -m "feat: implement [feature name] with MVVM architecture

- Add new ViewModel for [functionality] with reactive data binding
- Implement Service layer for [external integration]
- Create comprehensive test suite with [XX]% coverage
- Update Views to support [feature] with proper signal/slot usage
- Add Models with validation and business logic separation
- Update documentation and architecture guidelines

Technical Implementation:
- Maintains SOLID principles and MVVM separation
- Uses dependency injection throughout
- Follows project coding standards and patterns
- All tests passing ([XXX] total, [N] documented exceptions)

Closes #[issue-number] if applicable"
```

### Step 7: Push and Verify Merge

**Push Merged Main Branch:**

```bash
# Push updated main branch
git push origin main

# Verify push successful
git log --oneline -5
git diff origin/main~1..HEAD  # Should show no differences
```

**Verification Commands:**

```bash
# Verify merge integrity
git show --stat HEAD  # Show merge commit details
git log --graph --oneline -10  # Visualize commit history

# Confirm file changes
git diff HEAD~1 --name-only  # List changed files
git diff HEAD~1 --stat       # Show change statistics
```

## Phase 3: Post-Merge Validation

### Step 8: Post-Merge Testing

**Test Main Branch:**

```bash
# Switch to main and test
git checkout main

# Run full test suite on main
pytest DFBU/tests/ -v --cov=DFBU

# Test application startup
python DFBU/dfbu_gui.py

# Run any additional integration tests
pytest DFBU/tests/ -m integration -v
```

**Performance and Regression Testing:**

```bash
# If performance tests exist
pytest DFBU/tests/ -m performance -v  # if configured

# Memory usage check (if applicable)
python -m memory_profiler DFBU/dfbu_gui.py

# Run stress tests for new features
pytest DFBU/tests/ -m stress -v  # if configured
```

### Step 9: Branch Management

**Clean Up Feature Branch (Optional):**

```bash
# Delete local feature branch (if no longer needed)
git branch -d feature-branch-name

# Delete remote feature branch (if no longer needed)
git push origin --delete feature-branch-name
```

**⚠️ Warning:** Only delete branches if you're certain they're no longer needed. For testing branches, consider keeping them for ongoing development.

**Update Development Branch (if applicable):**

```bash
# If using a persistent testing/development branch
git checkout testing
git merge main  # Sync testing with main
git push origin testing
```

### Step 10: Final Documentation and Communication

**Update Project Status:**

- [ ] Update project version in `pyproject.toml` or `__init__.py`
- [ ] Tag release if this represents a version milestone:

```bash
# Create version tag
git tag -a v0.1.0 -m "Release version 0.1.0

- Implemented [major features]
- Enhanced [existing capabilities]
- Added comprehensive test coverage
- Updated documentation and guidelines"

git push origin v0.1.0
```

**Team Communication:**

- [ ] Notify team of successful merge
- [ ] Update project management tools (Jira, GitHub Projects, etc.)
- [ ] Document any post-merge tasks or follow-up items
- [ ] Update CI/CD status if applicable

## Rollback Procedures

### Emergency Rollback (Before Push)

If issues discovered before pushing to remote:

```bash
# Undo merge commit (before push)
git reset --hard HEAD~1

# Alternative: revert specific changes
git checkout HEAD~1 -- path/to/problematic/file
git commit -m "revert: undo problematic changes"
```

### Emergency Rollback (After Push)

If issues discovered after pushing to remote:

```bash
# Option 1: Create revert commit (recommended)
git revert -m 1 HEAD
git push origin main

# Option 2: Hard reset (requires coordination)
git reset --hard <commit-hash-before-merge>
git push origin main --force-with-lease
```

**⚠️ Critical:** Coordinate with team before force-pushing. Use revert commits when possible.

## Success Criteria

The merge is successful when:

- [ ] **Code Quality**: All linting and type checks pass
- [ ] **Architecture**: MVVM separation maintained, SOLID principles followed
- [ ] **Testing**: All tests pass (with documented exceptions explained)
- [ ] **Integration**: Main branch contains all feature commits
- [ ] **Functionality**: Application runs without regressions
- [ ] **Documentation**: All changes documented and changelog updated
- [ ] **Remote Sync**: Remote repository updated successfully
- [ ] **Team Notification**: Stakeholders informed of completion

## Expected Merge Impact

After successful merge, the main branch will include:

### File Changes
- **Files Modified**: [X] files changed
- **Lines Added**: +[XXX] insertions
- **Lines Removed**: -[XXX] deletions

### New Components
- **Models**: [List new model classes]
- **ViewModels**: [List new viewmodel classes]
- **Views**: [List new view components]
- **Services**: [List new service implementations]
- **Tests**: [List new test suites]

### Documentation Updates
- **Architecture**: Updated MVVM diagrams and patterns
- **API**: New public interface documentation
- **Guides**: Updated development and testing guidelines
- **Version**: Updated to v[X.Y.Z]

## Troubleshooting

### Common Issues and Solutions

**Merge Conflicts:**
```bash
# Resolve conflicts manually, then:
git add <resolved-files>
git commit -m "resolve: merge conflicts with main"
```

**Test Failures After Merge:**
```bash
# Investigate failing tests
pytest DFBU/tests/path/to/failing/test.py -v -s

# Check for environment issues
python -m pip check
python --version
```

**Application Won't Start:**
```bash
# Check for import errors
python -c "import DFBU"

# Verify dependencies
uv pip install -r DFBU/requirements.txt

# Check for missing files
find DFBU -name "*.py" -exec python -m py_compile {} \;
```

**Performance Regression:**
```bash
# Profile the application
python -m cProfile -o profile_output.prof DFBU/dfbu_gui.py

# Compare with previous baseline
# Investigate memory usage
python -m memory_profiler DFBU/dfbu_gui.py
```

## Support Resources

If you encounter issues during the merge process:

1. **Repository Documentation**:
   - `DFBU/docs/ARCHITECTURE.md` - System design patterns
   - `docs/INDEX.md` - Documentation index
   - `CONTRIBUTING.md` - Development workflow
   - `docs/BRANCH_PROTECTION.md` - Branch protection rules

2. **Testing Resources**:
   - `DFBU/tests/README.md` - Testing guidelines
   - `DFBU/tests/conftest.py` - Shared test fixtures
   - `.github/prompts/test.prompt.md` - Testing procedures

3. **Development Support**:
   - `.github/copilot-instructions.md` - Coding guidelines
   - `AGENTS.md` - Quick reference for AI agents
   - `.agents/memory.instruction.md` - Project preferences

4. **External Resources**:
   - [PySide6 Documentation](https://doc.qt.io/qtforpython/)
   - [pytest Documentation](https://docs.pytest.org/)
   - [MVVM Pattern Guidelines](https://docs.microsoft.com/en-us/dotnet/architecture/maui/mvvm)

---

## Quick Reference Checklist

**Pre-Merge (Complete All):**
- [ ] MVVM architecture validated
- [ ] All tests passing (with exceptions documented)
- [ ] Documentation updated
- [ ] Changelog current
- [ ] No merge conflicts
- [ ] Code review approved

**Merge Execution:**
- [ ] Feature branch pushed to remote
- [ ] Switched to main branch
- [ ] Main branch updated from remote
- [ ] Merge completed (commit or squash strategy)
- [ ] Main branch pushed to remote

**Post-Merge Validation:**
- [ ] Tests pass on main branch
- [ ] Application runs without issues
- [ ] No regressions detected
- [ ] Team notified
- [ ] Documentation reflects changes
- [ ] Version updated if applicable

**Success Confirmed When:**
✅ All checklist items completed
✅ Remote main branch updated
✅ Tests passing
✅ Application functional
✅ Team aware of changes
