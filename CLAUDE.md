# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DFBU (DotFiles Backup Utility) is a Python 3.14+ Linux application for configuration file backup/restoration with CLI and GUI (PySide6) interfaces. Uses UV for package management.

## Essential Commands

```bash
# Setup
./scripts/setup.sh                    # Full setup (UV, venv, dependencies)
source .venv/bin/activate             # Activate virtual environment

# Run Application
python DFBU/dfbu-gui.py               # GUI mode
python DFBU/dfbu.py                   # CLI mode

# Testing
pytest DFBU/tests/                    # All tests
pytest DFBU/tests/test_model.py -v    # Single file
pytest DFBU/tests/ -m unit            # Unit tests only
pytest DFBU/tests/ -m integration     # Integration tests only
pytest DFBU/tests/ -m gui             # GUI tests (requires QApplication)
pytest DFBU/tests/ -m "not slow"      # Skip slow tests
pytest DFBU/tests/ --cov=DFBU --cov-report=html  # With coverage

# Type Checking
mypy DFBU/                            # Run type checker
```

## Critical: Branch Protection

**NEVER modify files on `main` branch. Always work on `testing` branch.**

```bash
python .agents/branch_protection.py   # Verify current branch before modifications
git checkout testing                  # Switch if needed
```

## Architecture: MVVM with Facade Pattern

```text
View (MainWindow, view.py)
    ↕ signals/slots
ViewModel (DFBUViewModel, viewmodel.py)
    ↕ method calls (via Protocols)
Model (DFBUModel, model.py - Facade)
    ↕ delegates to
Components (implement Protocol interfaces):
    ├── ConfigManager (config_manager.py)   # Config I/O, TOML, CRUD
    ├── FileOperations (file_operations.py) # Path handling, copying, archives
    ├── BackupOrchestrator (backup_orchestrator.py) # Backup/restore coordination
    └── StatisticsTracker (statistics_tracker.py)   # Operation metrics
```

### Layer Responsibilities

**Model Layer** - Pure Python only, no Qt imports:

- Business logic, data validation, file operations
- ConfigManager handles TOML configuration with rotating backups
- FileOperations uses Python 3.14 `Path.copy()` for metadata preservation
- Components implement Protocol interfaces (`DFBU/gui/protocols.py`) for dependency injection

**ViewModel Layer** - QObject with signals:

- Presentation logic, state management
- Emits signals for state changes (never direct widget manipulation)
- Uses worker threads (QThread subclasses) for non-blocking operations

**View Layer** - PySide6 widgets:

- **UI MUST be loaded from Qt Designer `.ui` files** in `DFBU/gui/designer/` - never hardcode layouts
- Load `.ui` files with `QUiLoader`, access widgets via `findChild()`
- Minimal logic, connects signals to ViewModel

### Shared Types

`DFBU/core/common_types.py` defines `TypedDict` classes shared between CLI and GUI:

- `DotFileDict`: Dotfile entry (category, application, description, paths, enabled)
- `OptionsDict`: Backup settings (mirror, archive, hostname_subdir, date_subdir, compression)

## Code Standards

### Type Hints (Mandatory)

Use modern Python 3.10+ syntax:

```python
# Correct
def process(items: list[str], config: dict[str, Any] | None = None) -> bool:

# Wrong - old syntax
from typing import List, Optional
def process(items: List[str], config: Optional[Dict] = None) -> bool:
```

Required on all functions, parameters, return values, and class attributes.

### Threading Pattern

Long-running operations must use `QThread` subclasses (see `DFBU/gui/config_workers.py`):

```python
class ConfigLoadWorker(QThread):
    progress_updated = Signal(int)
    load_finished = Signal(bool, str, int)  # success, error, count

    def run(self) -> None:
        self.progress_updated.emit(10)
        success, error = self.config_manager.load_config()
        self.progress_updated.emit(100)
        self.load_finished.emit(success, error, count)
```

### Configuration

TOML config at `DFBU/data/dfbu-config.toml`:

```toml
[paths]
mirror_dir = "~/backups/mirror"
archive_dir = "~/backups/archives"

[options]
mirror = true
archive = true
hostname_subdir = true
date_subdir = false

[[dotfile]]
category = "Shell"
application = "Bash"
description = "Bash shell configuration"
path = "~/.bashrc"          # Single path
enabled = true

[[dotfile]]
category = "Terminal"
application = "Konsole"
description = "Konsole terminal"
paths = [                    # Multiple paths supported
    "~/.config/konsolerc",
    "~/.local/share/konsole/Bash.profile",
]
enabled = true
```

## Testing Patterns

Tests use AAA pattern (Arrange-Act-Assert) with pytest-qt for signal testing:

```python
def test_viewmodel_emits_signal(qtbot, mocker):
    mock_service = mocker.Mock()
    mock_service.fetch.return_value = ["item1"]
    vm = DataViewModel(mock_service)

    with qtbot.waitSignal(vm.data_loaded, timeout=1000):
        vm.load_data()
```

Test markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.gui`, `@pytest.mark.slow`

Fixtures in `DFBU/tests/conftest.py` provide `qapp`, `temp_config_path`, `temp_dotfile`, mock services.

## Key Files

- `.github/copilot-instructions.md` - Detailed coding guidelines and SOLID patterns
- `AGENTS.md` - AI agent reference with templates and troubleshooting
- `.agents/memory.instruction.md` - Coding preferences and branch protection
- `DFBU/gui/protocols.py` - Protocol definitions for dependency injection
- `DFBU/gui/config_workers.py` - Worker thread implementations
- `DFBU/core/common_types.py` - Shared TypedDict definitions
- `DFBU/tests/conftest.py` - Pytest fixtures for Qt and file testing
