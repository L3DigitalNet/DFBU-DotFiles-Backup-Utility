---
mode: "agent"
description: "Create a complete MVVM feature with Model, ViewModel, View, Service, and tests"
---

# Create Complete MVVM Feature

Create a complete feature following MVVM architecture with all necessary layers: Model, ViewModel, View, Service (if needed), and comprehensive tests.

## Overview

This prompt guides you through creating a fully integrated feature that demonstrates proper MVVM separation, SOLID principles, and testing practices.

## Planning Phase

Before creating files, plan the feature:

### 1. Define Feature Requirements
- **Purpose**: What does this feature do?
- **User Actions**: What can the user do?
- **Data**: What data does it work with?
- **External Dependencies**: Files, APIs, databases?

### 2. Identify MVVM Components

**Model Layer:**
- Business logic needed?
- Data validation required?
- Domain entities?

**Service Layer:**
- External integrations (files, APIs)?
- Data persistence needed?

**ViewModel Layer:**
- What state needs to be managed?
- What signals will be emitted?
- What user actions to handle?

**View Layer:**
- Widget type (QWidget, QDialog, QMainWindow)?
- UI components needed?
- User interactions?

## Implementation Order

### Step 1: Create Model (if needed)

**File**: `DFBU/gui/[feature]_model.py`

```python
"""Model for [feature] business logic."""
from dataclasses import dataclass


@dataclass
class FeatureModel:
    """Represents [feature] domain entity.

    Attributes:
        field1: Description.
        field2: Description.
    """
    field1: str
    field2: int

    def validate(self) -> tuple[bool, str]:
        """Validate model data.

        Returns:
            Tuple of (is_valid, error_message).
        """
        if not self.field1:
            return False, "Field1 is required"
        if self.field2 < 0:
            return False, "Field2 must be non-negative"
        return True, ""

    def process(self) -> str:
        """Execute business logic.

        Returns:
            Processed result.
        """
        return f"{self.field1}: {self.field2}"
```

**Test**: `tests/unit/test_[feature]_model.py`

```python
"""Tests for FeatureModel."""
import pytest
from src.models.feature_model import FeatureModel


class TestFeatureModel:
    """Test suite for FeatureModel."""

    @pytest.fixture
    def model(self):
        """Create model instance."""
        return FeatureModel(field1="test", field2=42)

    def test_validate_returns_true_for_valid_data(self, model):
        """Test validation with valid data."""
        is_valid, message = model.validate()
        assert is_valid is True
        assert message == ""

    def test_process_returns_formatted_string(self, model):
        """Test process method."""
        result = model.process()
        assert result == "test: 42"
```

### Step 2: Create Service (if needed)

**File**: `DFBU/gui/[feature]_service.py`

```python
"""Service for [feature] data operations."""
import logging
from pathlib import Path
from typing import Protocol


logger = logging.getLogger(__name__)


class FeatureServiceProtocol(Protocol):
    """Protocol for feature service."""

    def load_data(self) -> list[dict]:
        """Load data from source."""
        ...

    def save_data(self, data: dict) -> bool:
        """Save data to source."""
        ...


class FeatureService:
    """Handles [feature] data persistence."""

    def __init__(self, data_dir: Path):
        """Initialize service.

        Args:
            data_dir: Directory for data storage.
        """
        self._data_dir = data_dir

    def load_data(self) -> list[dict]:
        """Load data from file.

        Returns:
            List of data dictionaries.

        Raises:
            IOError: If file cannot be read.
        """
        file_path = self._data_dir / "feature_data.json"
        import json
        with open(file_path, 'r') as f:
            return json.load(f)

    def save_data(self, data: dict) -> bool:
        """Save data to file.

        Args:
            data: Data to save.

        Returns:
            True if successful.

        Raises:
            IOError: If file cannot be written.
        """
        file_path = self._data_dir / "feature_data.json"
        import json
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
```

**Test**: `tests/unit/test_[feature]_service.py`

```python
"""Tests for FeatureService."""
import pytest
from pathlib import Path
import tempfile

from src.services.feature_service import FeatureService


class TestFeatureService:
    """Test suite for FeatureService."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def service(self, temp_dir):
        """Create service instance."""
        return FeatureService(temp_dir)

    def test_save_and_load_data(self, service):
        """Test saving and loading data."""
        test_data = {"id": 1, "name": "test"}

        success = service.save_data(test_data)
        assert success is True

        loaded = service.load_data()
        assert loaded == [test_data]
```

### Step 3: Create ViewModel

**File**: `DFBU/gui/[feature]_viewmodel.py`

```python
"""ViewModel for [feature]."""
import logging
from PySide6.QtCore import QObject, Signal, Slot

from src.models.feature_model import FeatureModel
from src.services.feature_service import FeatureServiceProtocol


logger = logging.getLogger(__name__)


class FeatureViewModel(QObject):
    """Manages [feature] state and logic.

    Coordinates between Model and View layers.
    """

    # Signals
    data_loaded = Signal(list)
    data_saved = Signal(bool)
    error_occurred = Signal(str)
    validation_changed = Signal(bool, str)

    def __init__(self, service: FeatureServiceProtocol):
        """Initialize ViewModel.

        Args:
            service: Service for data operations.
        """
        super().__init__()
        self._service = service
        self._current_model: FeatureModel | None = None

    @Slot()
    def load_data(self) -> None:
        """Load data from service."""
        try:
            data = self._service.load_data()
            self.data_loaded.emit(data)
            logger.info("Data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            self.error_occurred.emit(str(e))

    @Slot(str, int)
    def update_model(self, field1: str, field2: int) -> None:
        """Update current model and validate.

        Args:
            field1: First field value.
            field2: Second field value.
        """
        self._current_model = FeatureModel(field1=field1, field2=field2)
        is_valid, message = self._current_model.validate()
        self.validation_changed.emit(is_valid, message)

    @Slot()
    def save(self) -> None:
        """Save current model."""
        if not self._current_model:
            self.error_occurred.emit("No data to save")
            return

        is_valid, message = self._current_model.validate()
        if not is_valid:
            self.error_occurred.emit(message)
            return

        try:
            data = {"field1": self._current_model.field1,
                    "field2": self._current_model.field2}
            success = self._service.save_data(data)
            self.data_saved.emit(success)
            logger.info("Data saved successfully")
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            self.error_occurred.emit(str(e))
```

**Test**: `tests/unit/test_[feature]_viewmodel.py`

```python
"""Tests for FeatureViewModel."""
import pytest
from pytestqt.qtbot import QtBot

from src.viewmodels.feature_viewmodel import FeatureViewModel


class TestFeatureViewModel:
    """Test suite for FeatureViewModel."""

    @pytest.fixture
    def mock_service(self, mocker):
        """Create mock service."""
        mock = mocker.Mock()
        mock.load_data.return_value = [{"id": 1}]
        mock.save_data.return_value = True
        return mock

    @pytest.fixture
    def viewmodel(self, mock_service):
        """Create ViewModel instance."""
        return FeatureViewModel(mock_service)

    def test_load_data_emits_signal(self, qtbot, viewmodel, mock_service):
        """Test that load_data emits data_loaded signal."""
        with qtbot.waitSignal(viewmodel.data_loaded, timeout=1000) as blocker:
            viewmodel.load_data()

        assert blocker.args[0] == [{"id": 1}]
        mock_service.load_data.assert_called_once()

    def test_update_model_validates_data(self, qtbot, viewmodel):
        """Test that update_model validates input."""
        with qtbot.waitSignal(viewmodel.validation_changed, timeout=1000) as blocker:
            viewmodel.update_model("test", 42)

        is_valid, message = blocker.args
        assert is_valid is True
        assert message == ""

    def test_save_with_invalid_data_emits_error(self, qtbot, viewmodel):
        """Test that save with invalid data emits error."""
        viewmodel.update_model("", -1)  # Invalid data

        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            viewmodel.save()

        assert "required" in blocker.args[0].lower()
```

### Step 4: Create View

**File**: `DFBU/gui/[feature]_view.py`

```python
"""View for [feature]."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QPushButton, QListWidget
)

from src.viewmodels.feature_viewmodel import FeatureViewModel


class FeatureView(QWidget):
    """View for [feature].

    Provides UI for [feature description].
    """

    def __init__(self, viewmodel: FeatureViewModel):
        """Initialize view.

        Args:
            viewmodel: ViewModel for this view.
        """
        super().__init__()
        self._viewmodel = viewmodel
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup user interface."""
        layout = QVBoxLayout(self)

        # Input section
        input_layout = QVBoxLayout()

        self._field1_label = QLabel("Field 1:")
        self._field1_input = QLineEdit()
        input_layout.addWidget(self._field1_label)
        input_layout.addWidget(self._field1_input)

        self._field2_label = QLabel("Field 2:")
        self._field2_input = QSpinBox()
        self._field2_input.setRange(0, 100)
        input_layout.addWidget(self._field2_label)
        input_layout.addWidget(self._field2_input)

        layout.addLayout(input_layout)

        # Error label
        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: red;")
        self._error_label.hide()
        layout.addWidget(self._error_label)

        # Buttons
        button_layout = QHBoxLayout()
        self._load_button = QPushButton("Load")
        self._save_button = QPushButton("Save")
        self._save_button.setEnabled(False)
        button_layout.addWidget(self._load_button)
        button_layout.addWidget(self._save_button)
        layout.addLayout(button_layout)

        # Data list
        self._data_list = QListWidget()
        layout.addWidget(self._data_list)

        self.setWindowTitle("Feature View")
        self.setMinimumSize(400, 300)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # View → ViewModel
        self._load_button.clicked.connect(self._viewmodel.load_data)
        self._save_button.clicked.connect(self._viewmodel.save)
        self._field1_input.textChanged.connect(self._on_input_changed)
        self._field2_input.valueChanged.connect(self._on_input_changed)

        # ViewModel → View
        self._viewmodel.data_loaded.connect(self._on_data_loaded)
        self._viewmodel.validation_changed.connect(self._on_validation_changed)
        self._viewmodel.error_occurred.connect(self._on_error)
        self._viewmodel.data_saved.connect(self._on_data_saved)

    def _on_input_changed(self) -> None:
        """Handle input change."""
        field1 = self._field1_input.text()
        field2 = self._field2_input.value()
        self._viewmodel.update_model(field1, field2)

    def _on_data_loaded(self, data: list) -> None:
        """Handle data loaded.

        Args:
            data: Loaded data list.
        """
        self._data_list.clear()
        for item in data:
            self._data_list.addItem(str(item))

    def _on_validation_changed(self, is_valid: bool, message: str) -> None:
        """Handle validation change.

        Args:
            is_valid: Whether data is valid.
            message: Validation message.
        """
        self._save_button.setEnabled(is_valid)
        if is_valid:
            self._error_label.hide()
        else:
            self._error_label.setText(message)
            self._error_label.show()

    def _on_error(self, message: str) -> None:
        """Handle error.

        Args:
            message: Error message.
        """
        self._error_label.setText(f"Error: {message}")
        self._error_label.show()

    def _on_data_saved(self, success: bool) -> None:
        """Handle data saved.

        Args:
            success: Whether save was successful.
        """
        if success:
            self._error_label.hide()
            # Optionally reload data
            self._viewmodel.load_data()
```

### Step 5: Integration and Testing

**Integration Test**: `tests/integration/test_[feature]_integration.py`

```python
"""Integration tests for feature."""
import pytest
from pathlib import Path
import tempfile

from src.models.feature_model import FeatureModel
from src.services.feature_service import FeatureService
from src.viewmodels.feature_viewmodel import FeatureViewModel
from src.views.feature_view import FeatureView


def test_complete_feature_workflow(qtbot):
    """Test complete feature workflow from View to Model."""
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        service = FeatureService(Path(tmpdir))
        viewmodel = FeatureViewModel(service)
        view = FeatureView(viewmodel)
        qtbot.addWidget(view)

        # Act - User enters data
        view._field1_input.setText("test")
        view._field2_input.setValue(42)
        qtbot.wait(100)

        # Assert - Save button should be enabled
        assert view._save_button.isEnabled()

        # Act - User saves
        with qtbot.waitSignal(viewmodel.data_saved, timeout=1000):
            view._save_button.click()

        # Assert - Data should be saved
        loaded = service.load_data()
        assert len(loaded) == 1
        assert loaded[0]["field1"] == "test"
        assert loaded[0]["field2"] == 42
```

## Checklist

- [ ] Feature requirements defined
- [ ] MVVM components identified
- [ ] Model created (if needed) with tests
- [ ] Service created (if needed) with tests
- [ ] ViewModel created with tests
- [ ] View created
- [ ] Integration test created
- [ ] All tests pass
- [ ] MVVM separation maintained
- [ ] SOLID principles followed
- [ ] Type hints on all methods
- [ ] Docstrings on public APIs
- [ ] No Qt imports in Model layer
- [ ] Dependencies injected
- [ ] Signals used for communication

## Common Patterns

### Feature with List Management
- Model: Item entity
- Service: CRUD operations
- ViewModel: List state management
- View: List display with add/remove buttons

### Feature with Form Validation
- Model: Validation rules
- ViewModel: Field-level validation
- View: Real-time feedback

### Feature with Async Operations
- Service: Background operations
- ViewModel: Thread management
- View: Loading indicators

## Testing Strategy

1. **Unit Tests**: Test each layer independently
2. **Integration Tests**: Test layer interactions
3. **Mock External Dependencies**: Use mocks for Services in ViewModel tests
4. **Use pytest-qt**: For Qt-related testing
5. **Aim for 80%+ Coverage**: Focus on critical paths
