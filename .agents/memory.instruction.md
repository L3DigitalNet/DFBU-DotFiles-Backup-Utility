---
applyTo: '**'
---

# Coding Preferences - PySide6 Desktop Application Template

## ⚠️ CRITICAL: Branch Protection Rules (MANDATORY FOR ALL AI AGENTS)

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

### Enforcement

The following protections are in place:

- Git pre-commit hook: Blocks commits to main
- Git post-checkout hook: Warns when switching to main
- Git post-merge hook: Reminds to switch back to testing
- Python script: `.agents/branch_protection.py` - AI agents should check this before modifications

**If AI agent detects it's on 'main' branch without explicit merge authorization, it must:**

1. Refuse to make any file changes
2. Inform human of the protection violation
3. Suggest switching to testing: `git checkout testing`

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

### Fixed Technologies

- **UI Framework**: PySide6 (Qt for Python) - Latest version compatible with Python 3.14
- **Language**: Python 3.14
- **Platform**: Linux only (no Windows/Mac compatibility required)
- **Testing**: Pytest with pytest-qt plugin
- **Type Checking**: Use type hints everywhere
- **Virtual Environment**: UV (fast Python package installer and resolver)
- **UI Design**: Qt Designer (.ui files, NO hardcoded UI)

### Required Dependencies

```
PySide6
pytest
pytest-qt
pytest-mock
```

### UV Virtual Environment Management

**CRITICAL**: Use UV for all virtual environment and dependency management:

```bash
# Install UV (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Add new dependency
uv pip install package-name
```

### UI Design Standards (MANDATORY)

**NEVER hardcode UI in Python**. Always use Qt Designer:

1. **Create UI in Qt Designer**: Design all layouts, widgets, and properties in `.ui` files
2. **Save .ui files**: Store in `src/views/ui/` directory
3. **Load in Python**: Use `QUiLoader` to load .ui files at runtime

**Example Structure**:

```
src/views/
├── ui/                    # Qt Designer .ui files
│   ├── main_window.ui
│   ├── settings_dialog.ui
│   └── custom_widget.ui
├── main_window.py         # Loads main_window.ui
└── settings_dialog.py     # Loads settings_dialog.ui
```

## Code Organization Standards

### File Structure (Strict)

```
src/
├── models/           # Domain logic, data classes
├── viewmodels/       # Presentation logic, QObject-based
├── views/            # PySide6 UI components
├── services/         # External integrations, I/O
├── utils/            # Helpers, constants
└── main.py

tests/
├── unit/             # Model & ViewModel tests
├── integration/      # Full-stack tests
└── conftest.py       # Shared fixtures
```

### Naming Conventions

- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

## Coding Patterns

### ViewModel Pattern (Standard)

```python
from PySide6.QtCore import QObject, Signal, Slot

class MyViewModel(QObject):
    # Signals for state changes
    state_changed = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, service: ServiceProtocol):
        super().__init__()
        self._service = service

    @Slot()
    def perform_action(self):
        try:
            result = self._service.execute()
            self.state_changed.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))
```

### View Pattern with .ui Files (MANDATORY)

```python
from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import os

class MyView(QMainWindow):
    def __init__(self, viewmodel: MyViewModel):
        super().__init__()
        self._viewmodel = viewmodel
        self._load_ui()
        self._connect_signals()

    def _load_ui(self):
        """Load UI from .ui file created in Qt Designer."""
        ui_file_path = os.path.join(
            os.path.dirname(__file__),
            'ui',
            'my_view.ui'
        )
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # Set loaded UI as central widget (for QMainWindow)
        self.setCentralWidget(self.ui)

        # Access widgets from loaded UI
        self.button = self.ui.findChild(QPushButton, "myButton")
        self.label = self.ui.findChild(QLabel, "myLabel")

    def _connect_signals(self):
        self._viewmodel.state_changed.connect(self._on_state_changed)
        # UI signals
        self.button.clicked.connect(self._viewmodel.perform_action)

    def _on_state_changed(self, value: str):
        # Update UI
        pass
```

### Model Pattern (Standard)

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DataModel:
    id: int
    name: str
    value: Optional[float] = None

    def validate(self) -> bool:
        """Business validation logic."""
        return len(self.name) > 0 and self.id > 0

    def calculate(self) -> float:
        """Business logic."""
        return self.value or 0.0
```

## Testing Standards

### Test Structure (Required)

```python
# Arrange-Act-Assert pattern
def test_viewmodel_updates_state(qtbot):
    # Arrange
    mock_service = Mock()
    viewmodel = MyViewModel(service=mock_service)

    # Act
    with qtbot.waitSignal(viewmodel.state_changed):
        viewmodel.perform_action()

    # Assert
    mock_service.execute.assert_called_once()
```

### Test Coverage Requirements

- All ViewModels: 90%+ coverage
- All Models: 95%+ coverage
- Views: Focus on integration tests
- Test failure paths, not just happy paths

## Error Handling

### Exception Strategy

```python
# Custom exceptions for domain
class ValidationError(Exception):
    """Raised when data validation fails."""

class ServiceError(Exception):
    """Raised when external service fails."""

# In code
def process(data: dict) -> Result:
    if not data:
        raise ValidationError("Data cannot be empty")

    try:
        return external_service.call(data)
    except ConnectionError as e:
        raise ServiceError(f"Service unavailable: {e}")
```

### Logging (Always)

```python
import logging

logger = logging.getLogger(__name__)

def risky_operation():
    try:
        # operation
        logger.info("Operation completed")
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        raise
```

## Dependency Injection

### Constructor Injection (Preferred)

```python
# Define protocol
from typing import Protocol

class DataServiceProtocol(Protocol):
    def fetch(self) -> list:
        ...

# Use in class
class MyViewModel:
    def __init__(self, data_service: DataServiceProtocol):
        self._data_service = data_service
```

### Factory Pattern (For Complex Setup)

```python
class ApplicationFactory:
    @staticmethod
    def create_main_window() -> MainWindow:
        # Create dependencies
        service = DataService()
        viewmodel = MainViewModel(service)
        view = MainView(viewmodel)
        return view
```

## Qt-Specific Guidelines

### Signal/Slot Best Practices

- Define all signals at class level
- Use type-safe signals: `Signal(str, int)`
- Use `@Slot` decorator for slots
- Connect in `__init__` or dedicated setup method
- Disconnect when objects are destroyed

### Threading Rules

- Never block UI thread
- Use `QThread` for background work
- Communicate via signals only
- No shared mutable state between threads

### Resource Management

- Use `deleteLater()` for widget cleanup
- Close resources in `closeEvent()`
- Use context managers for files
- Clean up timers and threads

## Type Hints (Mandatory)

### Standard Usage

```python
from typing import List, Dict, Optional, Protocol, TypeVar

T = TypeVar('T')

def process_items(
    items: List[str],
    config: Optional[Dict[str, Any]] = None
) -> bool:
    """Process items with optional configuration."""
    return True

class Repository(Protocol):
    def save(self, item: T) -> None:
        ...
```

## Documentation Requirements

### Docstring Format (Google Style)

```python
def complex_function(param1: str, param2: int) -> dict:
    """One-line summary.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Dictionary containing results.

    Raises:
        ValueError: If param2 is negative.
    """
```

### When to Document

- All public classes and methods
- Complex algorithms
- Non-obvious design decisions
- Workarounds and known issues

## Performance Patterns

### Lazy Loading

```python
class DataViewModel(QObject):
    def __init__(self):
        super().__init__()
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self._load_data()
        return self._data
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(param: int) -> float:
    # computation
    return result
```

## Solutions Repository

### Problem: Testing Qt Signals

**Solution**: Use `pytest-qt`'s `qtbot.waitSignal()`

```python
def test_signal_emission(qtbot):
    obj = MyQObject()
    with qtbot.waitSignal(obj.my_signal, timeout=1000):
        obj.trigger()
```

### Problem: Circular Dependencies Between ViewModel and View

**Solution**: Pass ViewModel to View, not vice versa. View observes ViewModel via signals.

### Problem: Model Needs UI Feedback

**Solution**: Models should never know about UI. Use callback functions or return status objects.

### Problem: Testing Without QApplication

**Solution**: Create session-scoped fixture in conftest.py

```python
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
```

## Anti-Patterns to Avoid

❌ **DON'T**: Import Qt in Models
✅ **DO**: Keep Models pure Python

❌ **DON'T**: Put business logic in Views
✅ **DO**: Keep Views as dumb renderers

❌ **DON'T**: Create god classes
✅ **DO**: Follow SRP, keep classes focused

❌ **DON'T**: Use global state
✅ **DO**: Inject dependencies explicitly

❌ **DON'T**: Block UI thread with long operations
✅ **DO**: Use QThread or QThreadPool

❌ **DON'T**: Create circular dependencies
✅ **DO**: Use dependency injection and clear hierarchy

## Quick Reference Commands

### Running Tests

```bash
pytest tests/                          # All tests
pytest tests/unit/                     # Unit tests only
pytest -v --cov=src tests/            # With coverage
pytest -k "test_viewmodel" tests/     # Specific pattern
```

### Type Checking

```bash
mypy src/                             # Type check source
```

### Code Quality

```bash
pylint src/                           # Linting
black src/ tests/                     # Formatting
isort src/ tests/                     # Import sorting
```

## Development Workflow

1. **Design**: Identify Model, ViewModel, View responsibilities
2. **Test First**: Write failing test
3. **Implement**: Make test pass
4. **Refactor**: Improve while keeping tests green
5. **Document**: Add docstrings and comments
6. **Verify**: Run full test suite and type checking

## Remember

- MVVM separation is sacred
- Type hints are not optional
- Tests must pass before commit
- Inject dependencies, don't create them
- Signals for communication, not method calls
- Pure functions where possible
- Explicit is better than implicit
