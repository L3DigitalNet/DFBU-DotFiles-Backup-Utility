# Agent Instructions for PySide6 Desktop Application Development

## Quick Reference

This template is for building desktop applications with:

- **UI**: PySide6 (Qt for Python) - Latest version compatible with Python 3.14 (6.8.0+)
- **Language**: Python 3.14
- **Platform**: Linux only
- **Architecture**: MVVM (Model-View-ViewModel)
- **Principles**: SOLID
- **Testing**: Pytest with pytest-qt
- **Virtual Environment**: UV (fast Python package installer)
- **UI Design**: Qt Designer (.ui files - NO hardcoded UI)

## Essential Files

- `.github/copilot-instructions.md` - Comprehensive GitHub Copilot instructions
- `.agents/memory.instruction.md` - Coding preferences and patterns
- `.agents/branch_protection.py` - Branch protection checker for AI agents
- `docs/BRANCH_PROTECTION.md` - Complete branch protection documentation
- `docs/BRANCH_PROTECTION_QUICK.md` - Quick reference for branch protection
- `CLAUDE.md` - Claude Code / AI assistant instructions
- This file (AGENTS.md) - Quick agent reference

## ⚠️ CRITICAL: Branch Protection (AI Agents)

**BEFORE ANY FILE MODIFICATION, RUN:**

```bash
python .agents/branch_protection.py
```

**Rules:**

- ❌ NEVER modify files on `main` branch
- ✅ ALWAYS work on `testing` branch
- ✅ ONLY assist with merges when human explicitly authorizes
- ✅ After merge assistance, remind human to switch back to `testing`

See `BRANCH_PROTECTION_QUICK.md` for full details.

## Development Checklist

### Starting a New Feature

- [ ] Identify which layer(s) are affected (Model/View/ViewModel)
- [ ] Design the data flow: Model → ViewModel → View
- [ ] Write tests first (TDD approach)
- [ ] Implement Model (pure Python, no Qt)
- [ ] Implement ViewModel (QObject, signals)
- [ ] Implement View (PySide6 widgets)
- [ ] Verify SOLID principles are maintained
- [ ] Run full test suite

### Code Review Checklist

- [ ] MVVM separation maintained (no Qt in Models)
- [ ] SOLID principles followed
- [ ] Type hints on all functions/methods
- [ ] Docstrings on all public APIs
- [ ] Tests written and passing
- [ ] No business logic in Views
- [ ] UI loaded from .ui files (NO hardcoded layouts)
- [ ] Dependencies injected, not created
- [ ] Signals used for cross-layer communication
- [ ] No blocking operations on UI thread
- [ ] Error handling implemented
- [ ] Logging added for important operations

## Architecture Rules (Non-Negotiable)

### Model Layer

✅ **Allowed**: Pure Python, dataclasses, business logic, validation, domain exceptions
❌ **Forbidden**: Any Qt imports, UI concerns, direct file I/O (use services)

### ViewModel Layer

✅ **Allowed**: QObject, signals/slots, presentation logic, calling services, state management
❌ **Forbidden**: Direct widget manipulation, business logic, UI styling

### View Layer

✅ **Allowed**: Loading .ui files, PySide6 widgets, signal connections, finding child widgets
❌ **Forbidden**: Hardcoded UI layouts, business logic, data validation, direct model access

## Common Tasks

### Creating a New Feature

```bash
# 1. Create model
touch src/models/my_feature.py

# 2. Create viewmodel
touch src/viewmodels/my_feature_viewmodel.py

# 3. Design UI in Qt Designer
designer src/views/ui/my_feature_view.ui

# 4. Create view (loads .ui file)
touch src/views/my_feature_view.py

# 5. Create tests
touch tests/unit/test_my_feature_model.py
touch tests/unit/test_my_feature_viewmodel.py
```

### Running Tests

```bash
# All tests
pytest tests/

# With coverage
pytest --cov=src --cov-report=html tests/

# Specific test file
pytest tests/unit/test_my_feature.py

# Specific test
pytest tests/unit/test_my_feature.py::TestMyFeature::test_specific_case
```

### Type Checking

```bash
mypy src/
```

## Quick Patterns

### Dependency Injection Setup

```python
# In main.py or application factory
def create_application():
    # Create services (bottom layer)
    config_service = ConfigService()
    data_service = DataService(config_service)

    # Create viewmodels (middle layer)
    main_viewmodel = MainViewModel(data_service)

    # Create views (top layer)
    main_window = MainWindow(main_viewmodel)

    return main_window
```

### Signal Communication Pattern

```python
# ViewModel emits changes
class DataViewModel(QObject):
    data_loaded = Signal(list)

    def load_data(self):
        data = self._service.fetch()
        self.data_loaded.emit(data)

# View reacts to changes
class DataView(QWidget):
    def __init__(self, vm: DataViewModel):
        super().__init__()
        vm.data_loaded.connect(self._update_list)
        self.load_button.clicked.connect(vm.load_data)
```

### Testing Pattern

```python
def test_viewmodel_emits_signal(qtbot, mocker):
    # Arrange
    mock_service = mocker.Mock()
    mock_service.fetch.return_value = ["item1", "item2"]
    vm = DataViewModel(mock_service)

    # Act
    with qtbot.waitSignal(vm.data_loaded, timeout=1000) as blocker:
        vm.load_data()

    # Assert
    assert blocker.args[0] == ["item1", "item2"]
    mock_service.fetch.assert_called_once()
```

## Troubleshooting

### Issue: "QApplication not created"

**Solution**: Create QApplication fixture in conftest.py:

```python
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
```

### Issue: Circular dependency between View and ViewModel

**Solution**: Always pass ViewModel TO View, never the reverse. Use signals for communication.

### Issue: Tests fail with "No event loop"

**Solution**: Use `pytest-qt` plugin and pass `qtbot` fixture to tests that need Qt.

### Issue: UI freezes during long operation

**Solution**: Move operation to QThread:

```python
class Worker(QObject):
    finished = Signal(object)

    def run(self):
        result = long_operation()
        self.finished.emit(result)

# In ViewModel
self.thread = QThread()
self.worker = Worker()
self.worker.moveToThread(self.thread)
self.thread.started.connect(self.worker.run)
self.worker.finished.connect(self._handle_result)
self.thread.start()
```

## File Templates

### Model Template

```python
"""Module docstring describing purpose."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class MyModel:
    """Description of the model."""

    id: int
    name: str
    value: Optional[float] = None

    def validate(self) -> bool:
        """Validate model data."""
        return self.id > 0 and len(self.name) > 0

    def calculate(self) -> float:
        """Business logic method."""
        return self.value or 0.0
```

### ViewModel Template

```python
"""Module docstring describing purpose."""
import logging
from PySide6.QtCore import QObject, Signal, Slot
from typing import Protocol


logger = logging.getLogger(__name__)


class ServiceProtocol(Protocol):
    """Protocol defining service interface."""
    def fetch(self) -> list:
        ...


class MyViewModel(QObject):
    """Description of the viewmodel."""

    # Signals
    data_changed = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, service: ServiceProtocol):
        """Initialize viewmodel.

        Args:
            service: Service for data operations.
        """
        super().__init__()
        self._service = service
        self._data = []

    @Slot()
    def load_data(self) -> None:
        """Load data from service."""
        try:
            self._data = self._service.fetch()
            self.data_changed.emit(self._data)
            logger.info("Data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            self.error_occurred.emit(str(e))
```

### View Template (with .ui file)

```python
"""Module docstring describing purpose."""
import os
from PySide6.QtWidgets import QMainWindow, QPushButton, QListWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from .my_viewmodel import MyViewModel


class MyView(QMainWindow):
    """Description of the view.

    CRITICAL: UI is loaded from Qt Designer .ui file, NOT hardcoded.
    """

    def __init__(self, viewmodel: MyViewModel):
        """Initialize view.

        Args:
            viewmodel: ViewModel to bind to this view.
        """
        super().__init__()
        self._viewmodel = viewmodel
        self._load_ui()
        self._connect_signals()

    def _load_ui(self) -> None:
        """Load UI from Qt Designer .ui file."""
        ui_file_path = os.path.join(
            os.path.dirname(__file__),
            'ui',
            'my_view.ui'
        )

        ui_file = QFile(ui_file_path)
        if not ui_file.open(QFile.ReadOnly):
            raise RuntimeError(f"Cannot open UI file: {ui_file_path}")

        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.setCentralWidget(self.ui)

        # Get widget references by objectName from Qt Designer
        self._list_widget = self.ui.findChild(QListWidget, "listWidget")
        self._load_button = self.ui.findChild(QPushButton, "loadButton")

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # View to ViewModel
        self._load_button.clicked.connect(self._viewmodel.load_data)

        # ViewModel to View
        self._viewmodel.data_changed.connect(self._on_data_changed)
        self._viewmodel.error_occurred.connect(self._on_error)

    def _on_data_changed(self, data: list) -> None:
        """Handle data changed signal."""
        self._list_widget.clear()
        self._list_widget.addItems(data)

    def _on_error(self, message: str) -> None:
        """Handle error signal."""
        # Show error to user
        pass
```

### Test Template

```python
"""Tests for MyModel."""
import pytest
from src.models.my_model import MyModel


class TestMyModel:
    """Test suite for MyModel."""

    @pytest.fixture
    def model(self):
        """Create a model instance for testing."""
        return MyModel(id=1, name="Test")

    def test_validate_returns_true_for_valid_data(self, model):
        """Test that validate returns True for valid data."""
        # Arrange
        # (model fixture is already arranged)

        # Act
        result = model.validate()

        # Assert
        assert result is True

    def test_validate_returns_false_for_invalid_id(self):
        """Test that validate returns False when id is invalid."""
        # Arrange
        model = MyModel(id=0, name="Test")

        # Act
        result = model.validate()

        # Assert
        assert result is False
```

## Resources

### Key Documentation

- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-qt Plugin](https://pytest-qt.readthedocs.io/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [MVVM Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel)

### Project Setup Commands

```bash
# Run setup script (installs UV, creates venv, installs dependencies)
./setup.sh

# Activate virtual environment
source .venv/bin/activate

# Or manually with UV:
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Add new package
uv pip install package-name

# Run tests
pytest tests/ -v

# Generate coverage report
pytest --cov=src --cov-report=html tests/
```

## AI Agent Workflow

When an AI agent is working on this codebase:

1. **Read memory first**: Check `.agents/memory.instruction.md` for preferences
2. **Follow MVVM strictly**: Never mix concerns between layers
3. **Write tests first**: TDD approach is preferred
4. **Use type hints**: Always include type annotations
5. **Inject dependencies**: Never create dependencies inside classes
6. **Document decisions**: Add comments for non-obvious choices
7. **Run tests after changes**: Verify nothing breaks
8. **Update memory**: Add new patterns or solutions discovered

## Remember

- **Separation is sacred**: MVVM layers must not leak
- **SOLID is mandatory**: Not optional guidelines
- **Tests are required**: Code without tests is incomplete
- **Type hints everywhere**: Make code self-documenting
- **Signals for communication**: Not direct method calls between layers
- **No blocking the UI**: Long operations must be threaded
- **Explicit over implicit**: Clear is better than clever
- **UI from .ui files only**: NEVER hardcode UI in Python - use Qt Designer
- **UV for dependencies**: Always use UV for virtual environment and package management
