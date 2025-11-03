---
mode: "agent"
description: "Clean up the repository by removing unnecessary files and ensuring proper file organization for PySide6 MVVM projects"
---

# Repository Cleanup Prompt

## Objective

Clean up the PySide6 desktop application repository by removing unnecessary files and ensuring all necessary files are in their proper directories according to MVVM architecture and project standards.

## Cleanup Categories

### 1. Auto-Generated Build/Cache Files

**Remove these if found:**
- `__pycache__/` directories (Python bytecode cache)
- `*.pyc`, `*.pyo`, `*.pyd` files (compiled Python)
- `.pytest_cache/` (pytest cache directory)
- `.ruff_cache/` (Ruff linter cache)
- `.mypy_cache/` (mypy type checker cache)
- `*.egg-info/` directories (pip/setuptools metadata)
- `.coverage*` files (coverage.py data files)
- `htmlcov/` (coverage HTML reports)
- `dist/`, `build/` (package build artifacts)

**Rationale:** These are automatically regenerated during development and should not be in version control (should be in .gitignore).

### 2. Temporary/Backup Files

**Remove these if found:**
- `*.bak`, `*.tmp`, `*.swp` files
- `*~` files (editor backups)
- Empty `backup/` directories
- Files with names like `old_*`, `test_*` (not actual test files), `temp_*`

**Rationale:** Temporary files and backups clutter the repository. Version control provides the backup mechanism.

### 3. Obsolete Migration Scripts

**Remove if migration is complete:**
- `scripts/migrate_json_to_toml.py` (if all configs are TOML-only)
- `scripts/convert_*` scripts (if conversion is complete)
- Any `migration_*` files that are no longer needed

**Rationale:** Once a migration is complete and verified, the migration scripts are no longer needed.

### 4. Duplicate Documentation Files

**Remove duplicates, keep canonical version:**
- Status/summary markdown files in root
- Duplicate README files
- Temporary documentation created during development

**Keep:**
- Main `README.md` in root
- `AGENTS.md`, `CONTRIBUTING.md`, `QUICKSTART.md`
- All core documentation files

**Rationale:** Documentation should be centralized and not duplicated.

### 5. Orphaned/Unused Files

**Check for and remove:**
- Unused test fixtures or data files
- Old demo/example scripts not part of template
- Commented-out code files or `.old` extensions
- Unused `.ui` files from Qt Designer

**Rationale:** Unused files add confusion and maintenance burden.

## Verification Steps

After cleanup, verify:

1. **All tests pass:**
   ```bash
   pytest tests/ -v
   ```

2. **No import errors:**
   ```bash
   python src/main.py
   ```

3. **Git status is clean:**
   ```bash
   git status
   ```

4. **Check .gitignore includes:**
   - `__pycache__/`
   - `*.egg-info/`
   - `.pytest_cache/`
   - `.mypy_cache/`
   - `venv/` or `.venv/`
   - `*.pyc`
   - `.coverage`
   - `htmlcov/`

## Proper MVVM Directory Structure

Ensure files are in correct locations:

### Source Code
- `src/models/` - Business logic and domain entities (no Qt imports)
- `src/viewmodels/` - Presentation logic (QObject with signals)
- `src/views/` - PySide6 UI components (widgets and .ui files)
- `src/services/` - External integrations and APIs
- `src/utils/` - Helper functions and constants
- `src/main.py` - Application entry point

### Tests
- `tests/unit/` - Unit tests for models and viewmodels
- `tests/integration/` - Integration tests
- `tests/conftest.py` - Pytest configuration with QApplication fixture

### Configuration
- `pyproject.toml` - Project configuration and dependencies
- `requirements.txt` - Python dependencies
- `.github/copilot-instructions.md` - Development guidelines

### Documentation
- `README.md` - Main project README
- `AGENTS.md` - Quick reference for AI agents
- `CONTRIBUTING.md` - Contribution guidelines
- `QUICKSTART.md` - Getting started guide
- `.agents/memory.instruction.md` - AI agent memory and preferences

## Execution Checklist

- [ ] Remove all `__pycache__` directories
- [ ] Remove all `.egg-info` directories
- [ ] Remove `.pytest_cache/` directory
- [ ] Remove `.mypy_cache/` directory
- [ ] Remove `htmlcov/` directory (coverage reports)
- [ ] Remove `.coverage` files
- [ ] Remove any `backup/` directories if empty
- [ ] Remove duplicate/status markdown files from root
- [ ] Check for orphaned/unused files
- [ ] Verify proper MVVM directory structure
- [ ] Run test suite to verify nothing broke
- [ ] Confirm .gitignore is comprehensive

## MVVM Layer Validation

Verify architectural integrity:

- [ ] No Qt imports in `src/models/` files
- [ ] ViewModels inherit from `QObject`
- [ ] Views accept ViewModels in constructor
- [ ] Dependencies injected, not created inside classes
- [ ] Signal/slot connections used for cross-layer communication

## Notes

- Always preserve MVVM layer separation
- Keep `pyproject.toml`, `requirements.txt`, `LICENSE`, `.gitignore`
- Keep example files that demonstrate MVVM patterns
- Version control (`.git/`) and virtual environment should already be ignored
- Preserve `.github/` and `.agents/` directories
