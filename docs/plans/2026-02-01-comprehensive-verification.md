# Comprehensive Bug Search & Verification Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Systematically verify all DFBU features work correctly, identify bugs, and fix any issues before moving to v0.9.0 integration.

**Architecture:** Test-driven verification using existing test infrastructure, manual GUI testing, and static analysis. Each feature verified in isolation then in integration.

**Tech Stack:** Python 3.14, pytest, pytest-qt, mypy, PySide6

---

## Current State Summary

| Metric | Value |
|--------|-------|
| Tests passing | 375 |
| Tests skipped | 19 |
| Tests broken (import error) | 30 (test_verification_manager.py) |
| Coverage | 84% overall |
| Low coverage components | error_handler.py (38%), verification_manager.py (16%), viewmodel.py (55%) |

## Critical Issues Found During Analysis

1. **BROKEN:** `test_verification_manager.py` uses wrong import style (absolute vs relative)
2. **LOW COVERAGE:** `error_handler.py` at 38% - new component needs tests
3. **LOW COVERAGE:** `verification_manager.py` at 16% - test file broken
4. **SKIPPED TESTS:** 19 tests skipped - need investigation

---

## Phase 1: Fix Broken Tests

### Task 1.1: Fix test_verification_manager.py Import Error

**Files:**
- Modify: `DFBU/tests/test_verification_manager.py:17`

**Step 1: Read current import and understand the pattern**

The file uses:
```python
from DFBU.gui.verification_manager import VerificationManager
```

But other tests use:
```python
sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))
from verification_manager import VerificationManager
```

**Step 2: Fix the imports**

Replace line 17 with the standard pattern:
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))
from verification_manager import VerificationManager
```

**Step 3: Run test to verify it loads**

Run: `uv run pytest DFBU/tests/test_verification_manager.py --collect-only -q`
Expected: Tests collected successfully (30 tests)

**Step 4: Run the full test file**

Run: `uv run pytest DFBU/tests/test_verification_manager.py -v`
Expected: All tests pass

**Step 5: Commit**

```bash
git add DFBU/tests/test_verification_manager.py
git commit -m "fix: correct import path in test_verification_manager.py"
```

---

### Task 1.2: Investigate Skipped Tests

**Files:**
- Read: Various test files

**Step 1: List all skipped tests with reasons**

Run: `uv run pytest DFBU/tests/ -v --collect-only | grep -i skip`

**Step 2: Categorize skipped tests**

- Platform-specific skips (expected)
- Missing fixture skips (bug)
- Conditional skips (investigate)

**Step 3: Document findings and create follow-up tasks if needed**

---

## Phase 2: Component-by-Component Verification

### Task 2.1: Verify ConfigManager (config_manager.py)

**Coverage:** 87%

**Files:**
- Test: `DFBU/tests/test_config_manager_yaml.py`
- Source: `DFBU/gui/config_manager.py`

**Step 1: Run ConfigManager tests**

Run: `uv run pytest DFBU/tests/test_config_manager_yaml.py -v`
Expected: All 18 tests pass

**Step 2: Check uncovered lines**

Uncovered lines: 82, 85, 89-90, 114-115, 119-120, 244, 253-258, 293-296, 322-323, 356, 409-410, 483, 497, 541, 568, 579-582, 611-612, 706

**Step 3: Identify critical uncovered paths**

Read the source at those line numbers to determine if they represent:
- Error handling paths (acceptable)
- Critical business logic (needs tests)
- Edge cases (nice to have)

**Step 4: Document any bugs found**

---

### Task 2.2: Verify FileOperations (file_operations.py)

**Coverage:** 78%

**Files:**
- Test: `DFBU/tests/test_model_file_operations.py`
- Source: `DFBU/gui/file_operations.py`

**Step 1: Run FileOperations tests**

Run: `uv run pytest DFBU/tests/test_model_file_operations.py -v`
Expected: 22 tests pass

**Step 2: Check critical functionality**

- File copying with metadata preservation
- Archive creation (tar.gz)
- Path expansion (~/ handling)
- Symlink handling

**Step 3: Manual verification of archive creation**

Create a test archive using the GUI and verify:
- Archive contains expected files
- Compression works
- Can extract successfully

---

### Task 2.3: Verify BackupOrchestrator (backup_orchestrator.py)

**Coverage:** 90%

**Files:**
- Test: `DFBU/tests/test_backup_orchestrator.py`
- Source: `DFBU/gui/backup_orchestrator.py`

**Step 1: Run BackupOrchestrator tests**

Run: `uv run pytest DFBU/tests/test_backup_orchestrator.py -v`
Expected: 28 tests pass

**Step 2: Verify pre-restore backup integration**

Run tests that exercise RestoreBackupManager integration:
```bash
uv run pytest DFBU/tests/test_backup_orchestrator.py -v -k "restore"
```

**Step 3: Check uncovered lines (211, 218, 403-419, 428, 484, 540-547)**

Read source to understand what's not covered.

---

### Task 2.4: Verify RestoreBackupManager (restore_backup_manager.py)

**Coverage:** 86%

**Files:**
- Test: `DFBU/tests/test_restore_backup_manager.py`
- Source: `DFBU/gui/restore_backup_manager.py`

**Step 1: Run tests**

Run: `uv run pytest DFBU/tests/test_restore_backup_manager.py -v`
Expected: 24 tests pass

**Step 2: Verify retention policy**

Check that old backups are properly cleaned up when limit exceeded.

---

### Task 2.5: Verify VerificationManager (verification_manager.py)

**Coverage:** 16% (after fixing imports)

**Files:**
- Test: `DFBU/tests/test_verification_manager.py`
- Source: `DFBU/gui/verification_manager.py`

**Step 1: Run tests after fixing imports (Task 1.1)**

Run: `uv run pytest DFBU/tests/test_verification_manager.py -v`
Expected: 30 tests pass

**Step 2: Verify coverage improved**

Run: `uv run pytest DFBU/tests/test_verification_manager.py --cov=DFBU.gui.verification_manager`

**Step 3: Test hash verification manually**

Create two identical files, verify they pass hash check.
Create two different files, verify they fail hash check.

---

### Task 2.6: Verify ErrorHandler (error_handler.py)

**Coverage:** 38% - NEEDS NEW TESTS

**Files:**
- Create: `DFBU/tests/test_error_handler.py`
- Source: `DFBU/gui/error_handler.py`

**Step 1: Create comprehensive test file**

Test classes needed:
- `TestErrorHandlerInit`
- `TestCreatePathResult`
- `TestCreateOperationResult`
- `TestHandleException`
- `TestFormatUserMessage`
- `TestFinalizeResult`
- `TestFormatSummaryForLog`
- `TestGetRetryablePaths`
- `TestCategorizeException`
- `TestIsRetryable`

**Step 2: Write tests for exception categorization**

```python
@pytest.mark.unit
def test_categorize_permission_error():
    handler = ErrorHandler()
    result = handler._categorize_exception(PermissionError("denied"))
    assert result == "permission"

@pytest.mark.unit
def test_categorize_file_not_found():
    handler = ErrorHandler()
    result = handler._categorize_exception(FileNotFoundError("missing"))
    assert result == "not_found"
```

**Step 3: Write tests for user message formatting**

**Step 4: Write tests for operation result finalization**

**Step 5: Run all ErrorHandler tests**

Run: `uv run pytest DFBU/tests/test_error_handler.py -v`
Expected: All tests pass, coverage >80%

**Step 6: Commit**

```bash
git add DFBU/tests/test_error_handler.py
git commit -m "test: add comprehensive ErrorHandler tests"
```

---

## Phase 3: Model Layer Verification

### Task 3.1: Verify DFBUModel Facade (model.py)

**Coverage:** 95%

**Files:**
- Test: `DFBU/tests/test_model.py`, `DFBU/tests/test_model_additional_coverage.py`
- Source: `DFBU/gui/model.py`

**Step 1: Run all model tests**

Run: `uv run pytest DFBU/tests/test_model*.py -v`
Expected: 83 tests pass (35 + 26 + 22)

**Step 2: Verify component delegation**

Ensure model properly delegates to:
- ConfigManager
- FileOperations
- BackupOrchestrator
- StatisticsTracker
- RestoreBackupManager
- VerificationManager (new)
- ErrorHandler (new)

---

## Phase 4: ViewModel Layer Verification

### Task 4.1: Verify DFBUViewModel (viewmodel.py)

**Coverage:** 55% - needs improvement

**Files:**
- Test: `DFBU/tests/test_viewmodel_*.py`, `DFBU/tests/test_worker_signals.py`
- Source: `DFBU/gui/viewmodel.py`

**Step 1: Run all viewmodel tests**

Run: `uv run pytest DFBU/tests/test_viewmodel*.py DFBU/tests/test_worker*.py -v`

**Step 2: Identify missing coverage areas**

Major uncovered areas:
- Lines 216-227, 231-266: Command methods
- Lines 520-577: Worker coordination
- Lines 849-863, 876: Verification signals
- Lines 1243-1300: Error handling integration

**Step 3: Test signal emissions**

Use pytest-qt to verify signals emit correctly:
```python
def test_backup_completed_signal(qtbot, viewmodel):
    with qtbot.waitSignal(viewmodel.backup_completed, timeout=5000):
        viewmodel.run_backup()
```

---

## Phase 5: View Layer Verification

### Task 5.1: Verify MainWindow (view.py)

**Coverage:** 69%

**Files:**
- Test: `DFBU/tests/test_view_comprehensive.py`
- Source: `DFBU/gui/view.py`

**Step 1: Run view tests**

Run: `uv run pytest DFBU/tests/test_view_comprehensive.py -v`
Expected: 29 tests pass

**Step 2: Manual GUI testing checklist**

- [ ] Application launches without errors
- [ ] All tabs display correctly
- [ ] Dotfile table shows data
- [ ] Add/Edit dialog works
- [ ] Backup button triggers operation
- [ ] Progress bar updates during backup
- [ ] Log panel shows messages
- [ ] Configuration tab loads settings
- [ ] Settings changes persist

---

## Phase 6: Static Analysis

### Task 6.1: Run Type Checker

**Step 1: Run mypy on entire codebase**

Run: `uv run mypy DFBU/`

**Step 2: Fix any type errors**

Document and fix type mismatches.

**Step 3: Run mypy strict mode on new files**

Run: `uv run mypy DFBU/gui/error_handler.py DFBU/gui/verification_manager.py --strict`

---

### Task 6.2: Check for Common Issues

**Step 1: Search for TODO/FIXME comments**

Run: `grep -r "TODO\|FIXME\|XXX\|HACK" DFBU/ --include="*.py"`

**Step 2: Search for bare except clauses**

Run: `grep -r "except:" DFBU/ --include="*.py"`

**Step 3: Search for unused imports**

Run: `uv run ruff check DFBU/ --select=F401`

---

## Phase 7: Integration Testing

### Task 7.1: End-to-End Backup Flow

**Step 1: Create test environment**

```bash
mkdir -p /tmp/dfbu-test/{source,mirror,archive}
echo "test content" > /tmp/dfbu-test/source/.testrc
```

**Step 2: Configure DFBU for test directories**

**Step 3: Run mirror backup**

- Verify file copied to mirror directory
- Verify timestamps preserved
- Verify verification runs (if enabled)

**Step 4: Run archive backup**

- Verify archive created
- Verify can extract archive
- Verify contents match source

**Step 5: Run restore**

- Verify pre-restore backup created
- Verify files restored correctly

---

### Task 7.2: Error Handling Integration

**Step 1: Test permission denied scenario**

Create a read-only file, attempt to backup/restore.

**Step 2: Test disk full scenario (simulated)**

Mock disk full error, verify graceful handling.

**Step 3: Test missing file scenario**

Delete a configured dotfile, run backup, verify error message.

---

## Phase 8: Documentation Verification

### Task 8.1: Verify CLAUDE.md Accuracy

**Step 1: Check all listed commands work**

Run each command in CLAUDE.md Essential Commands section.

**Step 2: Verify architecture description matches code**

Compare documented components to actual implementation.

**Step 3: Update any outdated information**

---

## Summary Checklist

### Tests
- [ ] Fix test_verification_manager.py import error (Task 1.1)
- [ ] Investigate 19 skipped tests (Task 1.2)
- [ ] Create test_error_handler.py (Task 2.6)
- [ ] All 405+ tests passing

### Coverage
- [ ] error_handler.py >80%
- [ ] verification_manager.py >80%
- [ ] viewmodel.py >70%
- [ ] Overall >85%

### Static Analysis
- [ ] mypy passes with no errors
- [ ] No bare except clauses
- [ ] No TODO/FIXME critical issues

### Manual Testing
- [ ] GUI launches correctly
- [ ] Backup flow works end-to-end
- [ ] Restore flow works with pre-restore backup
- [ ] Error messages are user-friendly

### Documentation
- [ ] CLAUDE.md accurate and up-to-date
- [ ] All commands documented work

---

## Execution Order

**Recommended sequence:**

1. **Phase 1** - Fix broken tests (critical path)
2. **Phase 6** - Static analysis (quick wins)
3. **Phase 2** - Component verification (thorough)
4. **Phase 3-5** - Layer verification (integration)
5. **Phase 7** - Integration testing (final validation)
6. **Phase 8** - Documentation (housekeeping)

Estimated effort: 2-4 hours for thorough verification
