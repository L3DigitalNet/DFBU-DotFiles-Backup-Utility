# Coding Preferences - DFBU DotFiles Backup Utility

## ⚠️ CRITICAL: Branch Protection Rules

**BEFORE ANY FILE MODIFICATIONS, AI AGENTS MUST:**

1. **Check current Git branch** using: `git branch --show-current`
2. **Verify branch is NOT 'main'** (unless explicitly authorized for merge assistance)
3. **Run branch protection check**: `python .agents/branch_protection.py`

- **testing branch**: All development, modifications, and commits happen here
- **main branch**: PROTECTED - Only for merges from testing (human-approved only)

❌ **NEVER** make file changes on the 'main' branch
✅ **ALWAYS** verify branch before any file operations
✅ **ONLY** assist with merges when human gives explicit permission

See [docs/BRANCH_PROTECTION.md](../docs/BRANCH_PROTECTION.md) for full rules and merge protocol.

## Key Principles

- **MVVM separation is sacred** — see [DFBU/docs/ARCHITECTURE.md](../DFBU/docs/ARCHITECTURE.md)
- **Type hints are mandatory** — modern Python 3.10+ syntax (`list[str]`, `str | None`)
- **Tests must pass before commit** — `pytest DFBU/tests/` and `mypy DFBU/`
- **Inject dependencies, don't create them** — use Protocol interfaces
- **Signals for cross-layer communication** — never direct method calls between layers
- **UI from .ui files only** — NEVER hardcode UI in Python, use Qt Designer
- **UV for dependencies** — always use UV for virtual environment and package management

## Quick Reference

```bash
pytest DFBU/tests/                    # All tests
pytest DFBU/tests/ --cov=DFBU         # With coverage
mypy DFBU/                            # Type check
python DFBU/dfbu_gui.py               # Run GUI
```
