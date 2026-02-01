# Coding Preferences - DFBU DotFiles Backup Utility

## ⚠️ CRITICAL: Branch Protection Rules

**BEFORE ANY FILE MODIFICATIONS, AI AGENTS MUST:**

1. **Check current Git branch** using: `git branch --show-current`
2. **Verify branch is NOT 'main'** (unless explicitly authorized for merge assistance)
3. **Run branch protection check**: `python .agents/branch_protection.py`

### Branch Usage Rules

- **testing branch**: All development, modifications, and commits happen here
- **main branch**: PROTECTED - Only for merges from testing (human-approved only)

### AI Agent Restrictions

❌ **NEVER** make file changes on the 'main' branch
❌ **NEVER** commit to the 'main' branch
❌ **NEVER** suggest changes to files when on 'main' branch
✅ **ALWAYS** verify branch before any file operations
✅ **ONLY** assist with merges when human gives explicit permission

### Exception: Merge Assistance

When human explicitly requests merge assistance:

1. Human must be on 'main' branch
2. Human must explicitly say "help me merge" or similar authorization
3. AI can guide through: `git merge testing`
4. After merge, AI must remind human to switch back: `git checkout testing`

## Architecture Mandates

### MVVM Structure (Non-Negotiable)

- **Models**: Pure Python, no Qt imports, business logic only
- **Views**: PySide6 widgets, minimal logic, UI-only concerns
- **ViewModels**: QObject-based, signals for state changes, testable without UI

### SOLID Principles (Required)

- Single Responsibility: One class = one purpose
- Open/Closed: Extend via inheritance/composition, not modification
- Liskov Substitution: Subtypes must be substitutable
- Interface Segregation: Small, focused interfaces using Protocol
- Dependency Inversion: Depend on abstractions, inject dependencies

## Technology Stack

- **Language**: Python 3.14+
- **Platform**: Linux only
- **UI Framework**: PySide6
- **UI Design**: Qt Designer (.ui files in `DFBU/gui/designer/`)
- **Testing**: Pytest with pytest-qt
- **Virtual Environment**: UV

## Type Hints (MANDATORY)

Use modern Python 3.10+ syntax:

```python
from typing import Final
from collections.abc import Callable

# Correct
def process(items: list[str], config: dict[str, Any] | None = None) -> bool:
    return True

MAX_RETRIES: Final[int] = 3
```

Run `mypy DFBU/` to verify type correctness.

## Testing Standards

Use Arrange-Act-Assert pattern with pytest-qt:

```python
def test_viewmodel_updates_state(qtbot, mocker):
    # Arrange
    mock_service = mocker.Mock()
    viewmodel = MyViewModel(service=mock_service)

    # Act
    with qtbot.waitSignal(viewmodel.state_changed):
        viewmodel.perform_action()

    # Assert
    mock_service.execute.assert_called_once()
```

## Quick Reference

```bash
pytest DFBU/tests/                    # All tests
pytest DFBU/tests/ --cov=DFBU         # With coverage
mypy DFBU/                            # Type check
python DFBU/dfbu-gui.py               # Run GUI
```

## Key Principles

- MVVM separation is sacred
- Type hints are mandatory
- Tests must pass before commit
- Inject dependencies, don't create them
- Signals for cross-layer communication
- Explicit is better than implicit
