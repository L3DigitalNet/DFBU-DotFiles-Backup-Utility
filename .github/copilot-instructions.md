# GitHub Copilot Instructions - DFBU Desktop Application

## Project Overview

DFBU (DotFiles Backup Utility) is a Python 3.14+ Linux desktop application for configuration file backup/restoration with a PySide6 GUI interface.

**Platform:** Linux only
**Python Version:** 3.14+
**PySide6 Version:** 6.6.0+
**Package Manager:** UV
**UI Design Tool:** Qt Designer (.ui files - NO hardcoded UI)

For comprehensive architecture documentation, see [DFBU/docs/ARCHITECTURE.md](../DFBU/docs/ARCHITECTURE.md).
For development setup and contribution guidelines, see [CONTRIBUTING.md](../CONTRIBUTING.md).

## Core Architecture

### MVVM Pattern

- **Model** (`DFBU/gui/model.py` + components): Business logic, data management (no UI dependencies)
- **View** (`DFBU/gui/view.py`): PySide6 UI components loaded from .ui files
- **ViewModel** (`DFBU/gui/viewmodel.py`): Mediates between View and Model
  - Uses Qt signals/slots for reactive binding
  - Manages QThread workers for non-blocking operations
  - ViewModels should be testable without UI instantiation

### Directory Structure

```
DFBU/
├── dfbu_gui.py               # Application entry point
├── core/                     # Shared utilities (no Qt imports)
│   ├── common_types.py       # TypedDict definitions
│   └── yaml_config.py        # YAML config loading/saving
├── gui/                      # MVVM presentation layer
│   ├── model.py              # Model facade
│   ├── viewmodel.py          # Presentation logic
│   ├── view.py               # PySide6 UI
│   ├── protocols.py          # Protocol interfaces for DI
│   ├── config_manager.py     # Configuration management
│   ├── file_operations.py    # File system operations
│   ├── backup_orchestrator.py # Backup/restore coordination
│   ├── error_handler.py      # Structured error handling
│   ├── verification_manager.py # Backup integrity
│   ├── restore_backup_manager.py # Pre-restore safety
│   ├── size_analyzer.py      # File size analysis
│   ├── statistics_tracker.py # Operation metrics
│   ├── config_workers.py     # QThread workers
│   └── designer/             # Qt Designer .ui files (MANDATORY)
├── data/                     # YAML configuration files
└── tests/                    # Test suite (pytest + pytest-qt) (see DFBU/tests/)
```

## UI Design Standards (CRITICAL)

### NEVER Hardcode UI in Python

**MANDATORY**: All UI must be created in Qt Designer and saved as .ui files.

**Correct Workflow:**

1. Design UI in Qt Designer → Save as `DFBU/gui/designer/component_name.ui`
2. Load .ui file in Python using `QUiLoader`
3. Access widgets using `findChild()`
4. Connect signals to ViewModel

**Example:**

```python
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import os

class MyView(QMainWindow):
    def _load_ui(self):
        ui_file_path = os.path.join(
            os.path.dirname(__file__), 'ui', 'my_view.ui'
        )
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.setCentralWidget(self.ui)

        # Access widgets by objectName from Qt Designer
        self.button = self.ui.findChild(QPushButton, "myButton")
```

**FORBIDDEN:**

```python
# ❌ NEVER do this
button = QPushButton("Text")
layout = QVBoxLayout()
layout.addWidget(button)
```

### Virtual Environment Management with UV

**ALWAYS use UV** for package management:

```bash
# Create venv
uv venv

# Activate
source .venv/bin/activate

# Install dependencies
uv pip install -r DFBU/requirements.txt

# Add package
uv pip install package-name

# Update requirements
uv pip freeze > DFBU/requirements.txt
```

## SOLID Principles Implementation

### Single Responsibility Principle (SRP)

- Each class has one clear purpose
- Separate data validation from business logic
- UI event handling separated from business logic

### Open/Closed Principle (OCP)

- Use abstract base classes for extensibility
- Prefer composition over inheritance
- Use dependency injection for flexibility

### Liskov Substitution Principle (LSP)

- Derived classes must be substitutable for base classes
- Maintain consistent contracts in inheritance hierarchies

### Interface Segregation Principle (ISP)

- Create focused interfaces/protocols
- Clients shouldn't depend on unused methods
- Use Python's `Protocol` for type hints

### Dependency Inversion Principle (DIP)

- Depend on abstractions, not concrete implementations
- Inject dependencies through constructors
- Use abstract base classes or Protocols for dependencies

## PySide6 Best Practices

### Signals and Slots

```python
# In ViewModel
from PySide6.QtCore import QObject, Signal

class MyViewModel(QObject):
    data_changed = Signal(str)  # Define signals for data changes

    def update_data(self, value: str):
        # Business logic
        self.data_changed.emit(value)
```

### Threading

- Use `QThread` for long-running operations
- Never block the UI thread
- Use signals for thread communication

### Resource Management

- Use `QResource` for embedded resources
- Properly cleanup widgets with `deleteLater()`
- Use context managers where applicable

### UI Files

- Use Qt Designer for complex layouts (.ui files)
- Load with `QUiLoader` or `pyside6-uic` compiler
- Keep UI logic in View layer only

## Python Code Standards

### Type Hints (MANDATORY - STRICT ENFORCEMENT)

**CRITICAL**: Type hints are MANDATORY for ALL code, not optional guidelines.

**Required type hints:**

- ✅ **ALL** function parameters (including `self` when helpful)
- ✅ **ALL** function return values (including `None` and `-> None`)
- ✅ **ALL** class attributes defined in `__init__`
- ✅ **ALL** module-level variables and constants
- ✅ **ALL** lambda parameters when type isn't obvious
- ✅ **ALL** property getters and setters

**Type hint standards:**

- Use modern Python 3.10+ syntax: `list[str]` not `List[str]`
- Use `|` union syntax: `str | None` not `Optional[str]`
- Use `collections.abc` for protocols: `Callable`, `Iterable`, `Sequence`
- Always specify generic types: `list[DotFileDict]` not `list`
- Use `Final` for constants that should never change
- Use `TypedDict` for structured dictionaries
- Use `Protocol` for interface definitions

**Examples:**

```python
from typing import Final, Protocol
from collections.abc import Callable
from pathlib import Path

# Module-level constants (use Final)
MAX_RETRIES: Final[int] = 3
CONFIG_DIR: Final[Path] = Path.home() / ".config"

# Function with full type hints
def process_data(
    items: list[str],
    config: dict[str, Any] | None = None,
    callback: Callable[[str], bool] | None = None
) -> bool:
    """Process items with optional config."""
    return True

# Class with typed attributes
class DataProcessor:
    """Process data items."""

    def __init__(self, max_items: int) -> None:
        """Initialize processor."""
        self.max_items: int = max_items
        self.processed_count: int = 0
        self._cache: dict[str, Any] = {}

    @property
    def is_full(self) -> bool:
        """Check if processor is at capacity."""
        return self.processed_count >= self.max_items

# Protocol for interface definition
class DataServiceProtocol(Protocol):
    """Protocol for data service implementations."""

    def fetch(self, key: str) -> list[dict[str, Any]]:
        """Fetch data by key."""
        ...

    def store(self, key: str, data: list[dict[str, Any]]) -> bool:
        """Store data with key."""
        ...
```

**Type checking (STRICT - MANDATORY):**

- **Conservative MyPy configuration enabled** - See `.mypy-strict-config.md` for full details
- Run `mypy DFBU/` regularly to verify type correctness
- **ALL type checking errors MUST be fixed before committing** - No exceptions
- Configuration enforces:
  - Complete type hints on all functions (parameters and returns)
  - No untyped function calls
  - Explicit type parameters for generics (`list[str]` not `list`)
  - Minimal use of `Any` type
  - Strict Optional handling (`| None` not implicit)
  - No redundant type casts
- Use `# type: ignore[error-code]` only when absolutely necessary with detailed justification
- Example: `result = qt_func()  # type: ignore[no-untyped-call]  # Qt stub incomplete`

### Error Handling

- Use specific exception types
- Handle Qt exceptions appropriately
- Log errors with proper context

```python
import logging

logger = logging.getLogger(__name__)

try:
    # operation
except SpecificException as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
```

### Documentation

- Use docstrings for all public classes and methods
- Follow Google or NumPy docstring format

```python
def calculate_total(items: List[float]) -> float:
    """Calculate the total sum of items.

    Args:
        items: List of numeric values to sum.

    Returns:
        The sum of all items.

    Raises:
        ValueError: If items list is empty.
    """
```

## Testing with Pytest

For comprehensive testing documentation, fixtures, and coverage details, see [DFBU/tests/README.md](../DFBU/tests/README.md).

Tests use AAA pattern (Arrange-Act-Assert) with pytest-qt for signal testing:

```bash
pytest DFBU/tests/                    # All tests
pytest DFBU/tests/ -m unit            # Unit tests only
pytest DFBU/tests/ --cov=DFBU         # With coverage
```

## Dependency Injection Pattern

```python
# Using constructor injection
class MyViewModel:
    def __init__(self, data_service: DataServiceProtocol):
        self._data_service = data_service

    def load_data(self):
        return self._data_service.fetch()

# In main.py or factory
service = ConcreteDataService()
viewmodel = MyViewModel(data_service=service)
```

## Code Generation Guidelines

### When creating Models:

- Pure Python classes with business logic
- No PySide6 imports in models
- Use `@dataclass` for simple data containers
- Implement validation methods
- Return domain-specific exceptions

### When creating ViewModels:

- Inherit from `QObject` for signals/slots
- Define signals for state changes
- Accept dependencies through constructor
- No direct widget manipulation
- Testable without UI

### When creating Views:

- Inherit from appropriate Qt widget class
- Accept ViewModel in constructor
- Connect signals/slots in `__init__` or `setup_connections()`
- Keep logic minimal (only UI state)
- Use Qt Designer for complex layouts

### When creating Tests:

- Use Arrange-Act-Assert pattern
- One assertion per test when possible
- Use descriptive test names: `test_should_X_when_Y`
- Mock external dependencies
- Use `pytest-qt` for Qt-specific testing

## Common Patterns

### Command Pattern for Actions

```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def undo(self) -> None:
        pass
```

### Observer Pattern (via Qt Signals)

```python
# ViewModel emits signals
class DataViewModel(QObject):
    data_updated = Signal(dict)

# View observes signals
class DataView(QWidget):
    def __init__(self, viewmodel: DataViewModel):
        super().__init__()
        viewmodel.data_updated.connect(self.on_data_updated)
```

### Factory Pattern for Object Creation

```python
class ViewModelFactory:
    @staticmethod
    def create_main_viewmodel(services: dict) -> MainViewModel:
        return MainViewModel(
            data_service=services['data'],
            config_service=services['config']
        )
```

## Performance Considerations

- Use `QThreadPool` for parallel operations
- Implement lazy loading for large datasets
- Use `QAbstractItemModel` for large lists/trees
- Profile with `cProfile` for bottlenecks
- Cache expensive computations

## Security Best Practices

- Validate all user inputs
- Sanitize file paths
- Use secure credential storage (e.g., `keyring`)
- Never hardcode sensitive data
- Handle exceptions without exposing internals

## Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## Configuration Management

- Use `.env` files for environment-specific config
- Create `config.py` for application settings
- Support command-line arguments
- Validate configuration on startup

## Remember

- Test first when possible (TDD)
- Keep functions small and focused
- Prefer explicit over implicit
- Document non-obvious decisions
- Use type hints consistently
- Follow PEP 8 style guidelines
- Keep MVVM layers strictly separated
- Make code testable by design

## Project Documentation

- [docs/INDEX.md](../docs/INDEX.md) - Complete documentation index
- [DFBU/docs/ARCHITECTURE.md](../DFBU/docs/ARCHITECTURE.md) - Detailed architecture documentation
- [DFBU/tests/README.md](../DFBU/tests/README.md) - Testing documentation and fixtures
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Development setup and contribution guidelines
- [docs/BRANCH_PROTECTION.md](../docs/BRANCH_PROTECTION.md) - Branch protection rules
