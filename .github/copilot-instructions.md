# GitHub Copilot Instructions - PySide6 Desktop Application Template

## Project Overview
This is a template for desktop applications built with PySide6, Python 3.14, following MVVM architecture and SOLID principles, with Pytest for testing.

**Platform:** Linux only (no Windows or macOS compatibility required)
**Python Version:** 3.14
**PySide6 Version:** Latest compatible with Python 3.14 (6.8.0+)
**Virtual Environment Manager:** UV (fast Python package installer)
**UI Design Tool:** Qt Designer (.ui files - NO hardcoded UI)

## Core Architecture

### MVVM Pattern
- **Model**: Business logic and data management (no UI dependencies)
- **View**: PySide6 UI components (QWidget, QMainWindow, etc.)
- **ViewModel**: Mediates between View and Model, handles presentation logic
  - Uses Qt signals/slots for reactive binding
  - No direct Qt imports in ViewModels when possible
  - ViewModels should be testable without UI instantiation

### Directory Structure
```
src/
├── models/           # Business logic, data classes, domain entities
├── viewmodels/       # Presentation logic, state management
├── views/            # PySide6 UI components
│   ├── ui/           # Qt Designer .ui files (MANDATORY)
│   └── *.py          # Python files that LOAD .ui files
├── services/         # External integrations, APIs, file I/O
├── utils/            # Helper functions, constants
└── main.py           # Application entry point

tests/
├── unit/             # Unit tests for models, viewmodels
├── integration/      # Integration tests
└── conftest.py       # Pytest fixtures and configuration
```

## UI Design Standards (CRITICAL)

### NEVER Hardcode UI in Python

**MANDATORY**: All UI must be created in Qt Designer and saved as .ui files.

**Correct Workflow:**
1. Design UI in Qt Designer → Save as `src/views/ui/component_name.ui`
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
uv pip install -r requirements.txt

# Add package
uv pip install package-name

# Update requirements
uv pip freeze > requirements.txt
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

**Type checking:**
- Run `mypy src/` regularly to verify type correctness
- Fix ALL type checking errors before committing
- Use `# type: ignore[error-code]` sparingly with justification comments

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

### Test Structure
```python
# tests/unit/test_model.py
import pytest
from src.models.my_model import MyModel

class TestMyModel:
    @pytest.fixture
    def model(self):
        return MyModel()

    def test_basic_functionality(self, model):
        # Arrange
        expected = "value"

        # Act
        result = model.process(expected)

        # Assert
        assert result == expected
```

### Testing ViewModels
```python
# tests/unit/test_viewmodel.py
import pytest
from pytestqt.qtbot import QtBot
from src.viewmodels.my_viewmodel import MyViewModel

def test_signal_emission(qtbot):
    vm = MyViewModel()

    with qtbot.waitSignal(vm.data_changed, timeout=1000):
        vm.update_data("test")
```

### Mocking
- Use `pytest-mock` for mocking dependencies
- Mock external services and file I/O
- Test ViewModels without instantiating Views

### Fixtures
```python
# tests/conftest.py
import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
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
