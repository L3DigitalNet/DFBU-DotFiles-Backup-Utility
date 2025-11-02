---
mode: "agent"
description: "Clean up the repository by removing unnecessary files and ensuring proper file organization"
---

# Repository Cleanup Prompt

## Objective

Clean up the Star Trek Retro Remake repository by removing unnecessary files and ensuring all necessary files are in their proper directories according to project standards.

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
- Status/summary markdown files in root (e.g., `IMPLEMENTATION_SUMMARY.md`, `GRID_INTEGRATION_COMPLETE.md`)
- README files that duplicate information in `docs/`
- Temporary documentation created during development

**Keep:**
- Main `README.md` in root
- All files in `docs/` directory (canonical documentation location)
- Module-specific `_doc.md` files alongside code

**Rationale:** Documentation should be centralized in `docs/` or co-located with code as `_doc.md` files.

### 5. Orphaned/Unused Files

**Check for and remove:**
- `.json` files outside of `backup/` (if project uses TOML-only)
- Unused test fixtures or data files
- Old demo scripts that are no longer relevant
- Commented-out code files or `.old` extensions

**Rationale:** Unused files add confusion and maintenance burden.

## Verification Steps

After cleanup, verify:

1. **All tests pass:**
   ```bash
   python -m pytest STRR/tests/ -v
   ```

2. **No import errors:**
   ```bash
   python -m STRR.main --help
   ```

3. **Git status is clean:**
   ```bash
   git status
   ```

4. **Check .gitignore includes:**
   - `__pycache__/`
   - `*.egg-info/`
   - `.pytest_cache/`
   - `.ruff_cache/`
   - `.mypy_cache/`
   - `.venv/`
   - `*.pyc`

## Proper Directory Structure

Ensure files are in correct locations:

### Configuration Files
- `STRR/config/*.toml` - Game configuration files
- `STRR/assets/data/sectors/*.toml` - Sector data files
- `pyproject.toml` - Project/build configuration (root)

### Source Code
- `STRR/src/` - All game source code
- `STRR/src/game/` - Game logic (MVC model/controller)
- `STRR/src/ui/` - UI components (MVC view)
- `STRR/src/engine/` - Core engine utilities

### Documentation
- `docs/` - All project documentation
- `STRR/src/**/*_doc.md` - Module-specific documentation co-located with code
- `README.md` - Main project README (root)

### Tests
- `STRR/tests/` - All test files
- `STRR/tests/conftest.py` - pytest configuration

### Scripts
- `scripts/` - Development/build scripts
- Scripts should be actively used, not obsolete

### Assets
- `STRR/assets/data/` - Game data files
- `STRR/assets/graphics/` - Image assets
- `STRR/assets/audio/` - Sound assets (when added)

## Execution Checklist

- [ ] Remove all `__pycache__` directories
- [ ] Remove all `.egg-info` directories
- [ ] Remove `.pytest_cache/` directory
- [ ] Remove any `backup/` directories if empty
- [ ] Remove obsolete migration scripts
- [ ] Remove duplicate/status markdown files from root
- [ ] Verify all `.json` files removed (if TOML-only)
- [ ] Check for orphaned/unused files
- [ ] Verify proper directory structure
- [ ] Run test suite to verify nothing broke
- [ ] Confirm .gitignore is comprehensive

## Notes

- Always preserve files in `docs/` directory
- Always preserve `_doc.md` files alongside source code
- Keep `pyproject.toml`, `Makefile`, `LICENSE`, `.gitignore`
- Keep active demo files (e.g., `demo_isometric_grid.py`)
- Version control (`.git/`) and virtual environment (`.venv/`) should already be ignored
