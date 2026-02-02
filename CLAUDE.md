# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DFBU (DotFiles Backup Utility) is a Python 3.14+ Linux desktop application for configuration file backup/restoration with a PySide6 GUI interface. Uses UV for package management.

**Current Version:** 1.0.0 — Production ready with full error handling and file size management

## Essential Commands

```bash
# Setup
./scripts/setup.sh                    # Full setup (UV, venv, dependencies)
source .venv/bin/activate             # Activate virtual environment

# Run Application
python DFBU/dfbu-gui.py               # Run the GUI application

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
    ├── ConfigManager (config_manager.py)        # Config I/O, YAML, CRUD
    ├── FileOperations (file_operations.py)      # Path handling, copying, archives
    ├── BackupOrchestrator (backup_orchestrator.py) # Backup/restore coordination
    ├── StatisticsTracker (statistics_tracker.py)   # Operation metrics
    ├── RestoreBackupManager (restore_backup_manager.py) # Pre-restore safety backups
    ├── VerificationManager (verification_manager.py)    # Backup integrity verification
    └── ErrorHandler (error_handler.py)          # Structured error handling
```

### Layer Responsibilities

**Model Layer** - Pure Python only, no Qt imports:

- Business logic, data validation, file operations
- ConfigManager handles YAML configuration with rotating backups
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

`DFBU/core/common_types.py` defines `TypedDict` classes used across the application:

- `DotFileDict`: Dotfile entry (application, description, paths, tags)
- `OptionsDict`: Backup settings (mirror, archive, hostname_subdir, date_subdir, compression)
- `VerificationResultDict`: File verification result (path, status, size/hash match)
- `OperationResultDict`: Structured operation result (status, completed, failed, warnings)
- `PathResultDict`: Per-path result with error categorization and retry eligibility
- `SizeReportDict`: Backup size analysis with threshold warnings (v1.0.0)

For comprehensive architecture documentation, see [DFBU/docs/ARCHITECTURE.md](DFBU/docs/ARCHITECTURE.md).

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

YAML config split across three files in `DFBU/data/`:

**settings.yaml** - Application settings:

```yaml
paths:
  mirror_dir: ~/backups/mirror
  archive_dir: ~/backups/archives
  restore_backup_dir: ~/.local/share/dfbu/restore-backups

options:
  mirror: true
  archive: true
  hostname_subdir: true
  date_subdir: false
  archive_format: tar.gz
  archive_compression_level: 9
  rotate_archives: true
  max_archives: 5
  pre_restore_backup: true
  max_restore_backups: 5
  verify_after_backup: true
  hash_verification: false
```

**dotfiles.yaml** - Dotfile library:

```yaml
Bash:
  description: Bash shell configuration
  paths: ~/.bashrc
  tags: shell, terminal

Konsole:
  description: KDE terminal emulator
  paths:
    - ~/.config/konsolerc
    - ~/.local/share/konsole/Bash.profile
  tags: kde, terminal
```

**session.yaml** - Runtime exclusions (files excluded from backup):

```yaml
excluded:
  - Firefox
  - Steam
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

For comprehensive testing documentation, see [DFBU/tests/README.md](DFBU/tests/README.md).

## Key Files

- `.github/copilot-instructions.md` - Detailed coding guidelines and SOLID patterns
- `AGENTS.md` - AI agent reference with templates and troubleshooting
- `.agents/memory.instruction.md` - Coding preferences and branch protection
- `DFBU/gui/protocols.py` - Protocol definitions for dependency injection
- `DFBU/gui/config_workers.py` - Worker thread implementations
- `DFBU/core/common_types.py` - Shared TypedDict definitions
- `DFBU/core/yaml_config.py` - YAML config loading/saving with schema validation
- `DFBU/core/validation.py` - Configuration validation rules
- `DFBU/tests/conftest.py` - Pytest fixtures for Qt and file testing
- `docs/plans/` - Implementation plans for production readiness features
- `docs/INDEX.md` - Complete documentation index
