---
mode: "agent"
description: "Create a new ViewModel class following MVVM architecture and SOLID principles"
---

# Create New ViewModel

Create a new ViewModel class in the `src/viewmodels/` directory following MVVM architecture, SOLID principles, and repository guidelines.

## Overview

ViewModels mediate between Views and Models, handling presentation logic and state management using Qt signals and slots.

## Guidelines

### Requirements
- **INHERIT** from `QObject` for signal/slot support
- **DEFINE** signals for state changes
- **ACCEPT** dependencies through constructor (dependency injection)
- **NO** direct widget manipulation
- **NO** business logic (delegate to Models/Services)
- **TYPE HINTS** on all methods and parameters
- **DOCSTRINGS** on all public APIs

### Location
Place new viewmodel in: `src/viewmodels/[viewmodel_name].py`

### Naming Convention
- **File**: `snake_case_viewmodel.py` (e.g., `user_profile_viewmodel.py`)
- **Class**: `PascalCaseViewModel` (e.g., `UserProfileViewModel`)

## Template Structure

```python
"""ViewModel for [feature description]."""
import logging
from PySide6.QtCore import QObject, Signal, Slot
from typing import Protocol

from src.models.my_model import MyModel


logger = logging.getLogger(__name__)


class ServiceProtocol(Protocol):
    """Protocol defining service interface."""

    def fetch_data(self) -> list[dict]:
        """Fetch data from external source."""
        ...

    def save_data(self, data: dict) -> bool:
        """Save data to external source."""
        ...


class MyViewModel(QObject):
    """ViewModel for [feature description].

    Manages state and presentation logic for [feature].
    Signals are emitted when state changes occur.
    """

    # Signals - define at class level
    data_loaded = Signal(list)  # Emitted when data is loaded
    data_saved = Signal(bool)   # Emitted when data is saved
    error_occurred = Signal(str)  # Emitted on errors
    loading_changed = Signal(bool)  # Emitted when loading state changes

    def __init__(self, service: ServiceProtocol):
        """Initialize ViewModel.

        Args:
            service: Service for data operations.
        """
        super().__init__()
        self._service = service
        self._data: list[dict] = []
        self._is_loading = False

    @property
    def is_loading(self) -> bool:
        """Get current loading state."""
        return self._is_loading

    @Slot()
    def load_data(self) -> None:
        """Load data from service.

        Emits data_loaded signal on success or error_occurred on failure.
        """
        try:
            self._set_loading(True)
            self._data = self._service.fetch_data()
            self.data_loaded.emit(self._data)
            logger.info("Data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            self.error_occurred.emit(f"Failed to load data: {str(e)}")
        finally:
            self._set_loading(False)

    @Slot(dict)
    def save_item(self, item: dict) -> None:
        """Save an item.

        Args:
            item: Item data to save.

        Emits data_saved signal with result.
        """
        try:
            self._set_loading(True)
            success = self._service.save_data(item)
            self.data_saved.emit(success)
            if success:
                logger.info("Item saved successfully")
            else:
                logger.warning("Item save failed")
        except Exception as e:
            logger.error(f"Error saving item: {e}")
            self.error_occurred.emit(f"Failed to save: {str(e)}")
        finally:
            self._set_loading(False)

    def _set_loading(self, loading: bool) -> None:
        """Set loading state and emit signal if changed.

        Args:
            loading: New loading state.
        """
        if self._is_loading != loading:
            self._is_loading = loading
            self.loading_changed.emit(self._is_loading)
```

## ViewModel Patterns

### Simple State Management
```python
class CounterViewModel(QObject):
    """Manages counter state."""

    value_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self._value = 0

    @Slot()
    def increment(self) -> None:
        """Increment counter."""
        self._value += 1
        self.value_changed.emit(self._value)

    @Slot()
    def decrement(self) -> None:
        """Decrement counter."""
        self._value -= 1
        self.value_changed.emit(self._value)
```

### Collection Management
```python
class ListViewModel(QObject):
    """Manages a list of items."""

    items_changed = Signal(list)
    item_added = Signal(object)
    item_removed = Signal(int)

    def __init__(self, service: DataService):
        super().__init__()
        self._service = service
        self._items: list[Item] = []

    @Slot(object)
    def add_item(self, item: Item) -> None:
        """Add item to list."""
        self._items.append(item)
        self.item_added.emit(item)
        self.items_changed.emit(self._items)

    @Slot(int)
    def remove_item(self, index: int) -> None:
        """Remove item at index."""
        if 0 <= index < len(self._items):
            self._items.pop(index)
            self.item_removed.emit(index)
            self.items_changed.emit(self._items)
```

### Form Validation
```python
class FormViewModel(QObject):
    """Manages form state and validation."""

    validation_changed = Signal(bool, str)
    form_submitted = Signal(dict)

    def __init__(self, model: FormModel):
        super().__init__()
        self._model = model
        self._data = {}

    @Slot(str, str)
    def update_field(self, field_name: str, value: str) -> None:
        """Update field value and validate.

        Args:
            field_name: Name of the field to update.
            value: New value for the field.
        """
        self._data[field_name] = value
        is_valid, message = self._model.validate_field(field_name, value)
        self.validation_changed.emit(is_valid, message)

    @Slot()
    def submit(self) -> None:
        """Submit form if valid."""
        if self._model.validate_all(self._data):
            self.form_submitted.emit(self._data)
```

## Testing ViewModels

Create test file in `tests/unit/test_[viewmodel_name].py`:

```python
"""Tests for MyViewModel."""
import pytest
from pytestqt.qtbot import QtBot

from src.viewmodels.my_viewmodel import MyViewModel


class TestMyViewModel:
    """Test suite for MyViewModel."""

    @pytest.fixture
    def mock_service(self, mocker):
        """Create mock service."""
        mock = mocker.Mock()
        mock.fetch_data.return_value = [{"id": 1, "name": "test"}]
        mock.save_data.return_value = True
        return mock

    @pytest.fixture
    def viewmodel(self, mock_service):
        """Create ViewModel instance."""
        return MyViewModel(mock_service)

    def test_load_data_emits_signal(self, qtbot, viewmodel, mock_service):
        """Test that load_data emits data_loaded signal."""
        # Arrange
        expected_data = [{"id": 1, "name": "test"}]

        # Act & Assert
        with qtbot.waitSignal(viewmodel.data_loaded, timeout=1000) as blocker:
            viewmodel.load_data()

        assert blocker.args[0] == expected_data
        mock_service.fetch_data.assert_called_once()

    def test_load_data_sets_loading_state(self, qtbot, viewmodel):
        """Test that load_data updates loading state."""
        # Arrange
        loading_states = []
        viewmodel.loading_changed.connect(loading_states.append)

        # Act
        viewmodel.load_data()
        qtbot.wait(100)  # Allow signals to process

        # Assert
        assert loading_states == [True, False]

    def test_error_emits_error_signal(self, qtbot, viewmodel, mock_service):
        """Test that errors emit error_occurred signal."""
        # Arrange
        mock_service.fetch_data.side_effect = Exception("Test error")

        # Act & Assert
        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            viewmodel.load_data()

        assert "Test error" in blocker.args[0]
```

## Integration with Views

Views connect to ViewModel signals:

```python
# In View
class MyView(QWidget):
    def __init__(self, viewmodel: MyViewModel):
        super().__init__()
        self._viewmodel = viewmodel
        self._setup_ui()
        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect ViewModel signals to View slots."""
        # ViewModel → View
        self._viewmodel.data_loaded.connect(self._on_data_loaded)
        self._viewmodel.error_occurred.connect(self._on_error)
        self._viewmodel.loading_changed.connect(self._on_loading_changed)

        # View → ViewModel
        self._load_button.clicked.connect(self._viewmodel.load_data)
        self._save_button.clicked.connect(self._on_save_clicked)

    def _on_data_loaded(self, data: list) -> None:
        """Handle data loaded from ViewModel."""
        self._list_widget.clear()
        for item in data:
            self._list_widget.addItem(str(item))

    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        item = {"name": self._name_input.text()}
        self._viewmodel.save_item(item)
```

## Checklist

- [ ] Created file in `src/viewmodels/`
- [ ] Inherits from `QObject`
- [ ] Signals defined at class level
- [ ] Dependencies injected through constructor
- [ ] Type hints on all methods
- [ ] Docstrings for public APIs
- [ ] No direct widget manipulation
- [ ] No business logic (uses Models/Services)
- [ ] Created unit tests in `tests/unit/`
- [ ] Tests use `qtbot` fixture
- [ ] All tests pass
- [ ] Follows SRP

## Common Patterns

### Async Operations
```python
from PySide6.QtCore import QThread, QObject, Signal

class Worker(QObject):
    """Background worker for async operations."""
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, service, operation):
        super().__init__()
        self._service = service
        self._operation = operation

    def run(self):
        """Execute operation in background."""
        try:
            result = self._operation(self._service)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

# In ViewModel
def start_async_operation(self):
    """Start async operation in background thread."""
    self._thread = QThread()
    self._worker = Worker(self._service, self._do_work)
    self._worker.moveToThread(self._thread)
    self._thread.started.connect(self._worker.run)
    self._worker.finished.connect(self._on_finished)
    self._worker.error.connect(self._on_error)
    self._thread.start()
```

### Command Pattern
```python
class Command:
    """Base command class."""
    def execute(self) -> None:
        raise NotImplementedError

    def undo(self) -> None:
        raise NotImplementedError

class CommandViewModel(QObject):
    """ViewModel with undo/redo support."""

    can_undo_changed = Signal(bool)
    can_redo_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []

    def execute_command(self, command: Command) -> None:
        """Execute command and add to undo stack."""
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()
        self.can_undo_changed.emit(True)
        self.can_redo_changed.emit(False)
```
