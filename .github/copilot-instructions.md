# DFBU (Dotfiles Backup Utility) - Copilot Instructions

**Project:** DFBU - Dotfiles Backup Utility
**Author:** Chris Purcell
**Email:** <chris@l3digital.net>
**GitHub:** <https://github.com/L3DigitalNet>
**Version:** 0.5.5
**Last Updated:** November 2, 2025

---

## Project Overview

DFBU is a Linux-only Python 3.14+ application for managing system configuration file backups with dual interfaces:
- **CLI Tool** (`dfbu.py`): Interactive terminal-based backup utility
- **GUI Application** (`dfbu-gui.py`): PySide6-based desktop application with MVVM architecture

The project emphasizes clean architecture, SOLID principles, confident design patterns, and minimal defensive programming with validation at architectural boundaries.

---

## Core Architecture Principles

### MVVM Architecture (GUI Application)

The GUI application strictly follows the Model-View-ViewModel pattern:

```
View (view.py)
  ↕ Signals/Slots
ViewModel (viewmodel.py)
  ↕ Commands/Properties
Model (model.py - Facade)
  ├── ConfigManager
  ├── FileOperations
  ├── BackupOrchestrator
  └── StatisticsTracker
```

**Separation of Concerns:**
- **View**: Pure UI presentation, no business logic, delegates all actions to ViewModel
- **ViewModel**: Presentation logic, worker thread management, signal coordination, state management
- **Model**: Business logic facade coordinating specialized components via delegation
- **Components**: Single-responsibility classes handling specific domains (config, files, orchestration, stats)

### SOLID Principles

**Single Responsibility Principle (SRP):**
- Each class has ONE reason to change
- `ConfigManager`: Configuration I/O and validation only
- `FileOperations`: File/directory operations and archive handling only
- `BackupOrchestrator`: Coordination and workflow logic only
- `StatisticsTracker`: Metrics and statistics only
- `DFBUModel`: Facade coordinating components (no business logic implementation)

**Open/Closed Principle (OCP):**
- Components are open for extension (subclassing) but closed for modification
- New backup strategies can extend `BackupOrchestrator` without modifying core logic
- New file operations can extend `FileOperations` without breaking existing code

**Liskov Substitution Principle (LSP):**
- Worker threads (`BackupWorker`, `RestoreWorker`) are substitutable QThread implementations
- Components can be swapped with compatible implementations without breaking facade

**Interface Segregation Principle (ISP):**
- Components expose minimal public APIs focused on their responsibilities
- ViewModel only exposes properties/commands View needs
- Model facade only exposes methods ViewModel needs

**Dependency Inversion Principle (DIP):**
- High-level modules (ViewModel) depend on abstractions (Model facade), not concrete implementations
- Model coordinates components via composition, not tight coupling
- TypedDict definitions (`DotFileDict`, `OptionsDict`) provide abstract contracts

### Confident Code Design Philosophy

**Validation at Architectural Boundaries:**
```python
# ✅ CORRECT: Validate at boundary (ViewModel or config load)
def add_dotfile(self, dotfile: DotFileDict) -> bool:
    # Validation happens HERE (architectural boundary)
    if not self._validate_dotfile_paths(dotfile):
        return False

    # After validation, core logic executes confidently
    self.config_manager.add_dotfile(dotfile)
    return True
```

**Clean Execution Paths:**
```python
# ✅ CORRECT: Confident execution after validation
def copy_file(self, src: Path, dest: Path) -> bool:
    # No defensive checks - assumes validation occurred at boundary
    src.copy(dest, follow_symlinks=True, preserve_metadata=True)
    return True

# ❌ INCORRECT: Scattered defensive checks
def copy_file(self, src: Path, dest: Path) -> bool:
    if not src.exists():  # Defensive - should validate at boundary
        return False
    if not src.is_file():  # Defensive - should validate at boundary
        return False
    # ... redundant checks throughout
```

**Pythonic Return Types:**
```python
# ✅ CORRECT: None indicates failure
def load_config(self) -> tuple[bool, str]:
    try:
        # ... load logic
        return True, ""
    except Exception as e:
        return False, str(e)

# ✅ CORRECT: Simple boolean for operations
def save_config(self) -> bool:
    try:
        # ... save logic
        return True
    except Exception:
        return False
```

**Version-Aware Error Handling:**
- **Pre-v1.0.0 (Current)**: Focus on clean architecture and core functionality; minimal error handling
- **Post-v1.0.0 (Planned)**: Comprehensive error handling with logging and recovery strategies
- Current approach: Let exceptions propagate to boundaries where they're handled appropriately

---

## Code Style and Standards

### Python Version and Features

**Required:** Python 3.14+

**Modern Features to Use:**
- `Path.copy()` with `preserve_metadata=True` and `follow_symlinks=True`
- Pattern matching with `match/case` statements
- TypedDict for configuration data structures
- Type hints everywhere (enforced by ruff ANN rules)
- `sys.path.insert(0, str(Path(__file__).parent.parent))` for local imports

### Type Hints and Annotations

**Full type hint coverage required:**
```python
# ✅ CORRECT: Complete type hints
def validate_dotfile(
    self,
    dotfile: dict[str, Any],
) -> DotFileDict:
    """Validate individual dotfile entry."""
    # ... implementation

# ❌ INCORRECT: Missing type hints
def validate_dotfile(dotfile):
    # ... implementation
```

**Use TypedDict for structured data:**
```python
from typing import TypedDict

class DotFileDict(TypedDict):
    category: str
    subcategory: str
    application: str
    description: str
    paths: list[str]
    mirror_dir: str
    archive_dir: str
    enabled: bool
```

### Linting and Formatting

**Ruff Configuration** (enforced via `pyproject.toml`):
- Target: Python 3.14+
- Line length: 88 (Black-compatible)
- Rules enabled: E, W, F, I, N, UP, ANN, B, C4, DTZ, T10, ISC, ICN
- Import sorting: isort-compatible
- Comprehensive PEP 8 compliance

**Import Organization:**
```python
# Standard library imports
import sys
from pathlib import Path
from typing import Any, Final

# External dependencies
from PySide6.QtCore import QObject, Signal

# Local imports (after sys.path manipulation)
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.common_types import DotFileDict, OptionsDict
from core.validation import ConfigValidator
```

### Documentation Standards

**Module Docstrings:**
```python
"""
Module Name - Brief Description

Description:
    Detailed description of module purpose, responsibilities, and role
    in the architecture. Explain patterns used and design decisions.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: MM-DD-YYYY
Date Changed: MM-DD-YYYY
License: MIT

Features:
    - Feature 1 with specific details
    - Feature 2 with specific details
    - Feature 3 with specific details

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - Dependencies listed here

Classes:
    - ClassName1: Brief description
    - ClassName2: Brief description

Functions:
    - function_name1: Brief description
    - function_name2: Brief description
    - None (if no standalone functions)
"""
```

**Class Docstrings:**
```python
class DFBUModel:
    """
    Brief description of class purpose.

    Detailed description of class role in architecture, patterns used,
    and key responsibilities. Explain relationships with other components.

    Attributes:
        config_path: Path to TOML configuration file
        options: Backup operation options from configuration
        dotfiles: List of dotfile metadata from configuration

    Public methods:
        load_config: Load and validate TOML configuration
        save_config: Save configuration changes back to TOML file

    Private methods:
        _internal_method: Brief description of internal method
    """
```

**Method Docstrings:**
```python
def validate_dotfile(
    self,
    dotfile: dict[str, Any],
) -> DotFileDict:
    """
    Validate individual dotfile entry.

    Validates required fields, performs type checking, and handles
    backward compatibility for legacy path format (path → paths).

    Args:
        dotfile: Raw dotfile dictionary from TOML file

    Returns:
        Validated DotFileDict with all required fields and proper types

    Raises:
        ValueError: If required fields are missing or invalid
    """
```

---

## File Organization and Structure

### Project Layout

```
DFBU/
├── dfbu.py                    # CLI application entry point
├── dfbu-gui.py                # GUI application entry point
├── core/                      # Shared core modules
│   ├── __init__.py
│   ├── common_types.py        # TypedDict definitions (shared)
│   └── validation.py          # Configuration validation (shared)
├── gui/                       # GUI-specific modules
│   ├── model.py               # Model facade (MVVM)
│   ├── viewmodel.py           # ViewModel layer (MVVM)
│   ├── view.py                # View layer (MVVM)
│   ├── config_manager.py      # Config I/O component (SRP)
│   ├── file_operations.py     # File I/O component (SRP)
│   ├── backup_orchestrator.py # Orchestration component (SRP)
│   ├── statistics_tracker.py  # Statistics component (SRP)
│   ├── constants.py           # GUI constants
│   └── designer/              # Qt Designer UI files
│       └── main_window_complete.ui
├── docs/                      # Documentation
│   ├── PROJECT-DOC.md         # CLI project documentation
│   ├── GUI-PROJECT-DOC.md     # GUI project documentation
│   ├── CHANGELOG.md           # CLI changelog
│   └── GUI-CHANGELOG.md       # GUI changelog
└── tests/                     # Test suite
    ├── test_model.py
    ├── test_viewmodel_*.py
    ├── test_backup_orchestrator.py
    └── ... (other test modules)
```

### Module Responsibilities

**Core Modules (Shared):**
- `common_types.py`: TypedDict definitions used by both CLI and GUI
- `validation.py`: Configuration validation logic (CLI and GUI)

**GUI Components:**
- `model.py`: Facade coordinating all components, maintains backward compatibility
- `viewmodel.py`: Presentation logic, worker threads, signal/slot coordination
- `view.py`: Pure UI presentation, PySide6 widgets, no business logic
- `config_manager.py`: Configuration file I/O, TOML parsing, rotating backups
- `file_operations.py`: File/directory copying, archive creation/rotation
- `backup_orchestrator.py`: Backup/restore workflow coordination
- `statistics_tracker.py`: Operation metrics tracking

---

## Development Guidelines

### Adding New Features

**1. Identify the Architectural Layer:**
- **View layer?** Add to `view.py` (UI presentation only)
- **ViewModel layer?** Add to `viewmodel.py` (presentation logic, commands)
- **Model layer?** Add to appropriate component or create new component
- **Shared logic?** Add to `core/` modules

**2. Follow SOLID Principles:**
- Does the feature fit existing component's responsibility? Add there.
- Does it require new responsibility? Create new component.
- Keep components focused on single responsibility.

**3. Maintain MVVM Separation:**
```python
# ❌ INCORRECT: Business logic in View
class MainWindow(QMainWindow):
    def on_backup_clicked(self):
        # Don't do this - business logic in View!
        for dotfile in self.dotfiles:
            self.copy_file(dotfile)

# ✅ CORRECT: Delegate to ViewModel
class MainWindow(QMainWindow):
    def on_backup_clicked(self):
        # View just delegates to ViewModel
        self.viewmodel.execute_backup()
```

**4. Add Tests:**
- Unit tests for new components/methods
- Integration tests for workflows
- Maintain >90% code coverage
- Test files in `tests/` directory matching `test_*.py` pattern

### Modifying Existing Code

**1. Understand the Architecture:**
- Read module docstring to understand responsibilities
- Check if modification fits component's single responsibility
- Verify you're working in correct architectural layer

**2. Maintain Backward Compatibility:**
```python
# ✅ CORRECT: Maintain existing API while refactoring
class DFBUModel:
    @property
    def dotfiles(self) -> list[DotFileDict]:
        """Expose dotfiles from ConfigManager."""
        return self.config_manager.dotfiles

    @dotfiles.setter
    def dotfiles(self, value: list[DotFileDict]) -> None:
        """Maintain backward compatibility with direct assignment."""
        self.config_manager.dotfiles = value
```

**3. Update Tests:**
- Modify existing tests to reflect changes
- Add new tests for new behavior
- Ensure all tests pass before committing

### Code Review Checklist

**Architecture:**
- [ ] Correct MVVM layer (View/ViewModel/Model)?
- [ ] Follows SOLID principles?
- [ ] Proper separation of concerns?
- [ ] No business logic in View?
- [ ] No UI code in Model?

**Code Quality:**
- [ ] Full type hint coverage?
- [ ] Ruff linting passes?
- [ ] Follows confident design philosophy?
- [ ] Validation at boundaries, not scattered?
- [ ] Proper docstrings (module, class, method)?

**Testing:**
- [ ] Unit tests added/updated?
- [ ] All tests pass?
- [ ] Code coverage maintained/improved?

**Documentation:**
- [ ] Module docstring updated?
- [ ] Class/method docstrings added?
- [ ] CHANGELOG.md updated (if user-facing)?
- [ ] PROJECT-DOC.md updated (if architectural)?

---

## Testing Standards

### Test Organization

**File Structure:**
```python
"""
Test Module Name

Description:
    Unit tests for specific component including initialization,
    core functionality, error handling, and edge cases.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: MM-DD-YYYY
License: MIT
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))

from model import DFBUModel


class TestComponentInitialization:
    """Test suite for component initialization."""

    def test_component_initializes_correctly(self) -> None:
        """Test component initializes with correct default values."""
        # Arrange
        # ... setup

        # Act
        # ... execute

        # Assert
        # ... verify
```

### Test Patterns

**Arrange-Act-Assert Pattern:**
```python
def test_load_config_valid_minimal(self, tmp_path: Path) -> None:
    """Test loading minimal valid config succeeds."""
    # Arrange: Set up test data and dependencies
    config_path = tmp_path / "minimal.toml"
    config_path.write_text("""
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true
""")
    model = DFBUModel(config_path)

    # Act: Execute the operation being tested
    success, error_message = model.load_config()

    # Assert: Verify expected outcomes
    assert success is True
    assert error_message == ""
    assert len(model.dotfiles) >= 0
```

**Test Naming Convention:**
```python
# Pattern: test_<method_name>_<condition>_<expected_result>

def test_load_config_file_not_found_returns_error(self) -> None:
    """Test loading nonexistent config file returns error."""

def test_validate_dotfile_missing_paths_raises_error(self) -> None:
    """Test validation fails when required paths field is missing."""

def test_save_config_creates_rotating_backup(self) -> None:
    """Test saving config creates timestamped backup."""
```

### Running Tests

**Command Line:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=DFBU --cov-report=html

# Run specific test file
pytest DFBU/tests/test_model.py

# Run specific test class
pytest DFBU/tests/test_model.py::TestDFBUModelConfigManagement

# Run specific test
pytest DFBU/tests/test_model.py::TestDFBUModelConfigManagement::test_load_config_valid_minimal
```

**Coverage Requirements:**
- Minimum coverage: 90%
- Focus on business logic (Model/ViewModel layers)
- View layer tested via integration tests

---

## Common Patterns and Anti-Patterns

### ✅ Correct Patterns

**1. Facade Pattern (Model Layer):**
```python
class DFBUModel:
    """Facade coordinating specialized components."""

    def __init__(self, config_path: Path):
        self.config_manager = ConfigManager(config_path)
        self.file_ops = FileOperations()
        self.orchestrator = BackupOrchestrator(self.file_ops, ...)
        self.stats = StatisticsTracker()

    def execute_backup(self) -> bool:
        """Delegate to orchestrator."""
        return self.orchestrator.execute_mirror_backup(
            self.config_manager.dotfiles,
            ...
        )
```

**2. Signal-Based Communication (MVVM):**
```python
# ViewModel exposes signals
class DFBUViewModel(QObject):
    backup_completed = Signal(bool)
    progress_updated = Signal(int)

    def execute_backup(self) -> None:
        """Start backup in worker thread."""
        self.worker = BackupWorker()
        self.worker.backup_finished.connect(self._on_backup_finished)
        self.worker.start()

# View connects to signals
class MainWindow(QMainWindow):
    def __init__(self, viewmodel: DFBUViewModel):
        super().__init__()
        self.viewmodel = viewmodel
        self.viewmodel.backup_completed.connect(self._on_backup_completed)
```

**3. Property Exposure (ViewModel):**
```python
class DFBUViewModel(QObject):
    @property
    def dotfiles(self) -> list[DotFileDict]:
        """Expose dotfiles for View data binding."""
        return self.model.dotfiles

    @property
    def statistics(self) -> BackupStatistics:
        """Expose statistics for View display."""
        return self.model.statistics
```

### ❌ Anti-Patterns to Avoid

**1. Business Logic in View:**
```python
# ❌ INCORRECT: View contains business logic
class MainWindow(QMainWindow):
    def on_save_clicked(self):
        # Don't validate or process data in View!
        if not self.validate_form():
            return
        dotfile = self.create_dotfile_from_form()
        self.model.add_dotfile(dotfile)

# ✅ CORRECT: View delegates to ViewModel
class MainWindow(QMainWindow):
    def on_save_clicked(self):
        # Just collect UI data and delegate
        dotfile_data = self.get_form_data()
        self.viewmodel.add_dotfile_command(dotfile_data)
```

**2. UI Code in Model:**
```python
# ❌ INCORRECT: Model imports Qt and shows dialogs
from PySide6.QtWidgets import QMessageBox

class DFBUModel:
    def save_config(self) -> bool:
        try:
            # ... save logic
            QMessageBox.information(None, "Success", "Config saved!")  # NO!
            return True
        except Exception as e:
            QMessageBox.critical(None, "Error", str(e))  # NO!
            return False

# ✅ CORRECT: Model returns results, ViewModel/View handle UI
class DFBUModel:
    def save_config(self) -> tuple[bool, str]:
        try:
            # ... save logic
            return True, ""
        except Exception as e:
            return False, str(e)
```

**3. Scattered Defensive Checks:**
```python
# ❌ INCORRECT: Defensive checks scattered throughout
def copy_file(self, src: Path, dest: Path) -> bool:
    if not src:  # Unnecessary
        return False
    if not src.exists():  # Should validate at boundary
        return False
    if not src.is_file():  # Should validate at boundary
        return False
    # ... more defensive checks
    src.copy(dest)
    return True

# ✅ CORRECT: Validate once at boundary, execute confidently
def add_dotfile_command(self, dotfile: DotFileDict) -> bool:
    # Validate at architectural boundary
    if not self._validate_dotfile(dotfile):
        return False

    # Core logic executes confidently
    self.model.add_dotfile(dotfile)
    return True
```

**4. Breaking SOLID Principles:**
```python
# ❌ INCORRECT: Class with multiple responsibilities
class ConfigFileBackupStatisticsManager:
    """Violates SRP - too many responsibilities!"""

    def load_config(self): ...
    def save_config(self): ...
    def backup_files(self): ...
    def track_statistics(self): ...

# ✅ CORRECT: Separate concerns into focused components
class ConfigManager:
    """Single responsibility: configuration I/O."""
    def load_config(self): ...
    def save_config(self): ...

class BackupOrchestrator:
    """Single responsibility: backup coordination."""
    def execute_backup(self): ...

class StatisticsTracker:
    """Single responsibility: metrics tracking."""
    def track_operation(self): ...
```

---

## Configuration Management

### TOML Configuration Format

**Structure:**
```toml
[paths]
mirror_dir = "~/Backups/DotFiles/Mirror"
archive_dir = "~/Backups/DotFiles/Archives"

[options]
mirror = true
archive = false
hostname_subdir = true
date_subdir = false
archive_compression_level = 9
max_archives = 5

[[dotfile]]
category = "Shell"
subcategory = "Bash"
application = "Bash"
description = "Bash configuration"
paths = ["~/.bashrc", "~/.bash_profile"]
enabled = true
```

**Validation Requirements:**
- All fields must have proper types
- Paths must be valid (checked at boundaries)
- Numeric values must be within valid ranges
- Backward compatibility for legacy `path` (string) → `paths` (list) migration

### Configuration Components

**ConfigValidator (core/validation.py):**
- Shared validation logic for CLI and GUI
- TypedDict-based validation
- Default values for missing fields
- Backward compatibility handling

**ConfigManager (gui/config_manager.py):**
- TOML file I/O (load/save)
- Rotating backups (up to 10 backups)
- Dotfile CRUD operations
- Integration with ConfigValidator

---

## Threading and Concurrency

### Worker Threads (GUI)

**Pattern:**
```python
class BackupWorker(QThread):
    """Worker thread for non-blocking backup operations."""

    # Define signals
    progress_updated = Signal(int)
    item_processed = Signal(str)
    backup_finished = Signal(bool)
    error_occurred = Signal(str)

    def run(self) -> None:
        """Main thread execution method."""
        try:
            # Perform long-running operation
            result = self.model.execute_backup()
            self.backup_finished.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))
```

**ViewModel Coordination:**
```python
class DFBUViewModel(QObject):
    def execute_backup_command(self) -> None:
        """Start backup in background thread."""
        # Create worker
        self.worker = BackupWorker()
        self.worker.set_model(self.model)

        # Connect signals
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.backup_finished.connect(self._on_backup_finished)

        # Start worker
        self.worker.start()

    def _on_backup_finished(self, success: bool) -> None:
        """Handle backup completion."""
        self.backup_completed.emit(success)
        self.worker = None  # Clean up reference
```

**View Connection:**
```python
class MainWindow(QMainWindow):
    def __init__(self, viewmodel: DFBUViewModel):
        super().__init__()
        self.viewmodel = viewmodel

        # Connect ViewModel signals to View slots
        self.viewmodel.backup_completed.connect(self._on_backup_completed)
        self.viewmodel.progress_updated.connect(self._update_progress_bar)

    def _on_backup_completed(self, success: bool) -> None:
        """Update UI after backup completes."""
        if success:
            self.status_label.setText("Backup completed successfully!")
        else:
            self.status_label.setText("Backup failed!")
```

---

## File Operations

### Path Handling

**Modern Python 3.14 Path.copy():**
```python
# ✅ CORRECT: Use Path.copy() with metadata preservation
from pathlib import Path

src = Path("~/.bashrc").expanduser()
dest = Path("~/Backups/bashrc").expanduser()

# Copy with metadata and follow symlinks
src.copy(dest, follow_symlinks=True, preserve_metadata=True)
```

**Path Expansion:**
```python
def expand_path(self, path_str: str) -> Path:
    """
    Expand path with ~ and environment variables.

    Args:
        path_str: Path string potentially containing ~ or $VAR

    Returns:
        Fully expanded Path object
    """
    expanded = Path(path_str).expanduser()
    # Note: Path doesn't expand env vars automatically
    if "$" in str(expanded):
        expanded = Path(os.path.expandvars(str(expanded)))
    return expanded
```

### Archive Operations

**Creating Archives:**
```python
def create_archive(
    self,
    source_dir: Path,
    output_path: Path,
    compression_level: int = 9,
) -> bool:
    """
    Create compressed TAR.GZ archive.

    Args:
        source_dir: Directory to archive
        output_path: Path for output archive file
        compression_level: Compression level (1-9, default 9)

    Returns:
        True if archive created successfully, False otherwise
    """
    try:
        with tarfile.open(
            output_path,
            mode=f"w:gz",
            compresslevel=compression_level,
        ) as tar:
            tar.add(source_dir, arcname=source_dir.name)
        return True
    except Exception:
        return False
```

**Archive Rotation:**
```python
def rotate_archives(
    self,
    archive_dir: Path,
    max_archives: int,
    hostname: str,
) -> list[Path]:
    """
    Rotate archives keeping only most recent max_archives.

    Args:
        archive_dir: Directory containing archives
        max_archives: Maximum number of archives to retain
        hostname: Hostname pattern to match archives

    Returns:
        List of deleted archive paths
    """
    pattern = f"{hostname}_*.tar.gz"
    archives = sorted(
        archive_dir.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    deleted = []
    for old_archive in archives[max_archives:]:
        old_archive.unlink()
        deleted.append(old_archive)

    return deleted
```

---

## Dependencies and Requirements

### Python Version
- **Required:** Python 3.14+
- **Rationale:** Latest Path.copy() features, modern type hints, pattern matching

### External Dependencies

**Production:**
- `PySide6>=6.6.0`: GUI framework (Qt for Python)
- `tomli-w>=1.0.0`: TOML writing (reading via stdlib tomllib)

**Development:**
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting
- `ruff`: Linting and formatting

### Standard Library Modules

**Core:**
- `pathlib`: Modern path handling
- `tomllib`: TOML configuration reading (Python 3.11+)
- `sys`, `os`: System operations
- `typing`: Type hints and TypedDict

**File Operations:**
- `shutil`: File operations and directory copying
- `tarfile`: Archive creation and extraction

**Utilities:**
- `socket`: Hostname detection
- `datetime`: Timestamps and date operations
- `time`: Performance timing

---

## Version Control and Changelog

### Git Workflow

**Branch Structure:**
- `main`: Stable production-ready code
- `testing`: Development and testing branch
- Feature branches: `feature/<feature-name>`
- Bugfix branches: `bugfix/<bug-name>`

### Changelog Management

**Location:**
- CLI changes: `DFBU/docs/CHANGELOG.md`
- GUI changes: `DFBU/docs/GUI-CHANGELOG.md`

**Format:**
```markdown
## [0.5.5] - 2025-11-01

### Added
- New feature description with implementation details
- Another feature with architectural impact

### Changed
- Modified behavior with rationale
- Refactored component following SOLID principles

### Fixed
- Bug fix with root cause explanation

### Deprecated
- Feature marked for removal with migration path
```

---

## Summary of Key Principles

### When Writing Code:

1. **Architecture First**: Identify correct MVVM layer before coding
2. **SOLID Compliance**: Single responsibility, open/closed, proper abstraction
3. **Confident Design**: Validate at boundaries, execute confidently in core
4. **Type Safety**: Full type hints, TypedDict for structured data
5. **Clean Separation**: No business logic in View, no UI in Model
6. **Standard Library**: Prefer stdlib over external dependencies
7. **Documentation**: Comprehensive docstrings for all modules/classes/methods
8. **Testing**: Unit tests for components, integration tests for workflows

### When Reviewing Code:

1. **Architectural Alignment**: Correct layer, proper separation, SOLID compliance
2. **Code Quality**: Type hints, linting passes, confident design patterns
3. **Documentation**: Docstrings complete, changelogs updated
4. **Testing**: Tests added/updated, coverage maintained, all tests pass

### When Refactoring:

1. **Maintain Compatibility**: Keep existing APIs working
2. **Preserve Tests**: Update tests to match new behavior
3. **Document Changes**: Update docstrings and architecture docs
4. **Follow Patterns**: Use established patterns (facade, signals, etc.)

---

**Remember:** Clean architecture and SOLID principles lead to maintainable, testable, and extensible code. When in doubt, favor simplicity and separation of concerns over clever solutions.

---

*End of Copilot Instructions*
