---
mode: "agent"
description: "Create a new View class following MVVM architecture and PySide6 best practices"
---

# Create New View

# Create New View

Create a new View class in the `DFBU/gui/` directory following MVVM architecture, PySide6 best practices, and repository guidelines.

## Overview

Views are PySide6 UI components that present data from ViewModels and capture user input. They should contain minimal logic.

## CRITICAL: UI Design with Qt Designer

**MANDATORY**: All UI must be designed in Qt Designer and saved as `.ui` files.

### UI File Location
- **NEVER** hardcode UI in Python
- **ALWAYS** design in Qt Designer
- **SAVE** to `DFBU/gui/designer/[view_name].ui`
- **LOAD** in Python using `QUiLoader`

### Location
Place new view in: `DFBU/gui/[view_name].py`

## Overview

Views are PySide6 UI components that display data and capture user input. They connect to ViewModels via signals/slots and contain minimal logic.

## Guidelines

### Requirements
- **INHERIT** from appropriate Qt widget (QWidget, QMainWindow, QDialog)
- **ACCEPT** ViewModel in constructor
- **SEPARATE** UI setup and signal connections
- **MINIMAL** logic (only UI state management)
- **NO** business logic or data validation
- **TYPE HINTS** on all methods
- **DOCSTRINGS** for public APIs

### Naming Convention
- **File**: `snake_case.py` (e.g., `user_profile_view.py`)
- **Class**: `PascalCase` (e.g., `UserProfileView`)

## Template Structure

### Basic Widget View
```python
"""View for [feature description]."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget
from PySide6.QtCore import Qt

from src.viewmodels.my_viewmodel import MyViewModel


class MyView(QWidget):
    """View for [feature description].

    Displays [description] and allows user to [actions].
    """

    def __init__(self, viewmodel: MyViewModel):
        """Initialize view.

        Args:
            viewmodel: ViewModel to bind to this view.
        """
        super().__init__()
        self._viewmodel = viewmodel
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Main layout
        layout = QVBoxLayout(self)

        # Widgets
        self._title_label = QLabel("My View")
        self._title_label.setAlignment(Qt.AlignCenter)

        self._list_widget = QListWidget()

        self._load_button = QPushButton("Load Data")
        self._save_button = QPushButton("Save")
        self._save_button.setEnabled(False)

        # Add to layout
        layout.addWidget(self._title_label)
        layout.addWidget(self._list_widget)
        layout.addWidget(self._load_button)
        layout.addWidget(self._save_button)

        # Window properties
        self.setWindowTitle("My View")
        self.setMinimumSize(400, 300)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # View → ViewModel
        self._load_button.clicked.connect(self._viewmodel.load_data)
        self._save_button.clicked.connect(self._on_save_clicked)
        self._list_widget.itemSelectionChanged.connect(self._on_selection_changed)

        # ViewModel → View
        self._viewmodel.data_loaded.connect(self._on_data_loaded)
        self._viewmodel.error_occurred.connect(self._on_error)
        self._viewmodel.loading_changed.connect(self._on_loading_changed)

    def _on_data_loaded(self, data: list) -> None:
        """Handle data loaded from ViewModel.

        Args:
            data: List of data items to display.
        """
        self._list_widget.clear()
        for item in data:
            self._list_widget.addItem(str(item))

    def _on_error(self, message: str) -> None:
        """Handle error from ViewModel.

        Args:
            message: Error message to display.
        """
        # Show error to user (e.g., status bar, message box)
        self.statusBar().showMessage(f"Error: {message}", 5000)

    def _on_loading_changed(self, is_loading: bool) -> None:
        """Handle loading state change.

        Args:
            is_loading: True if loading, False otherwise.
        """
        self._load_button.setEnabled(not is_loading)
        self._load_button.setText("Loading..." if is_loading else "Load Data")

    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        # Gather data from UI
        current_item = self._list_widget.currentItem()
        if current_item:
            data = {"text": current_item.text()}
            self._viewmodel.save_item(data)

    def _on_selection_changed(self) -> None:
        """Handle list selection change."""
        has_selection = bool(self._list_widget.currentItem())
        self._save_button.setEnabled(has_selection)
```

### Main Window View
```python
"""Main window view."""
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStatusBar, QMenuBar
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt

from src.viewmodels.main_viewmodel import MainViewModel


class MainWindow(QMainWindow):
    """Main application window.

    Provides the primary user interface for the application.
    """

    def __init__(self, viewmodel: MainViewModel):
        """Initialize main window.

        Args:
            viewmodel: Main ViewModel instance.
        """
        super().__init__()
        self._viewmodel = viewmodel
        self._setup_ui()
        self._create_actions()
        self._create_menus()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)

        # ... add widgets to layout ...

        # Window properties
        self.setWindowTitle("Application Name")
        self.setGeometry(100, 100, 800, 600)

        # Status bar
        self.setStatusBar(QStatusBar())

    def _create_actions(self) -> None:
        """Create menu actions."""
        self._open_action = QAction("&Open", self)
        self._open_action.setShortcut("Ctrl+O")
        self._open_action.setStatusTip("Open file")

        self._save_action = QAction("&Save", self)
        self._save_action.setShortcut("Ctrl+S")
        self._save_action.setStatusTip("Save file")

        self._exit_action = QAction("E&xit", self)
        self._exit_action.setShortcut("Ctrl+Q")
        self._exit_action.setStatusTip("Exit application")

    def _create_menus(self) -> None:
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self._open_action)
        file_menu.addAction(self._save_action)
        file_menu.addSeparator()
        file_menu.addAction(self._exit_action)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # Actions → ViewModel
        self._open_action.triggered.connect(self._viewmodel.open_file)
        self._save_action.triggered.connect(self._viewmodel.save_file)
        self._exit_action.triggered.connect(self.close)

        # ViewModel → View
        self._viewmodel.status_message.connect(self._on_status_message)

    def _on_status_message(self, message: str) -> None:
        """Display status message.

        Args:
            message: Message to display in status bar.
        """
        self.statusBar().showMessage(message, 3000)
```

### Dialog View
```python
"""Dialog view."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt

from src.viewmodels.dialog_viewmodel import DialogViewModel


class MyDialog(QDialog):
    """Dialog for [purpose].

    Allows user to [action/purpose].
    """

    def __init__(self, viewmodel: DialogViewModel, parent=None):
        """Initialize dialog.

        Args:
            viewmodel: ViewModel for this dialog.
            parent: Parent widget.
        """
        super().__init__(parent)
        self._viewmodel = viewmodel
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Content
        self._label = QLabel("Dialog content")
        layout.addWidget(self._label)

        # Button box
        button_layout = QHBoxLayout()
        self._ok_button = QPushButton("OK")
        self._cancel_button = QPushButton("Cancel")
        button_layout.addStretch()
        button_layout.addWidget(self._ok_button)
        button_layout.addWidget(self._cancel_button)
        layout.addLayout(button_layout)

        # Dialog properties
        self.setWindowTitle("My Dialog")
        self.setModal(True)
        self.setMinimumWidth(300)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        self._ok_button.clicked.connect(self.accept)
        self._cancel_button.clicked.connect(self.reject)
```

## Loading .ui Files

If using Qt Designer .ui files:

```python
"""View loading from .ui file."""
from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

from src.viewmodels.main_viewmodel import MainViewModel


class MainWindow(QMainWindow):
    """Main window loading UI from .ui file."""

    def __init__(self, viewmodel: MainViewModel):
        """Initialize main window.

        Args:
            viewmodel: Main ViewModel instance.
        """
        super().__init__()
        self._viewmodel = viewmodel
        self._load_ui()
        self._connect_signals()

    def _load_ui(self) -> None:
        """Load UI from .ui file."""
        loader = QUiLoader()
        ui_file = QFile("DFBU/gui/designer/main_window.ui")
        ui_file.open(QFile.ReadOnly)
        self._ui = loader.load(ui_file, self)
        ui_file.close()

        # Set as central widget or use self._ui to access widgets
        self.setCentralWidget(self._ui)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # Access widgets through self._ui
        self._ui.load_button.clicked.connect(self._viewmodel.load_data)
        self._viewmodel.data_loaded.connect(self._on_data_loaded)

    def _on_data_loaded(self, data: list) -> None:
        """Handle data loaded."""
        self._ui.list_widget.clear()
        self._ui.list_widget.addItems([str(item) for item in data])
```

## View Best Practices

### Resource Management
```python
def closeEvent(self, event):
    """Handle window close event."""
    # Cleanup resources
    self._viewmodel.cleanup()
    event.accept()

def __del__(self):
    """Cleanup when view is destroyed."""
    # Disconnect signals if needed
    pass
```

### Threading Considerations
```python
from PySide6.QtCore import QTimer

def _on_long_operation_complete(self, result):
    """Handle long operation completion (runs on UI thread)."""
    # Safe to update UI here
    self._result_label.setText(str(result))

def _start_long_operation(self):
    """Start long operation in background."""
    # ViewModel handles threading
    self._viewmodel.start_long_operation()
```

### Responsive UI
```python
def _setup_ui(self):
    """Setup responsive UI."""
    # Use layouts for responsive design
    layout = QVBoxLayout(self)
    layout.setContentsMargins(10, 10, 10, 10)
    layout.setSpacing(5)

    # Set size policies
    self._list_widget.setSizePolicy(
        QSizePolicy.Expanding,
        QSizePolicy.Expanding
    )
```

## Testing Views (Optional)

Views are typically not unit tested, but can be integration tested:

```python
"""Integration test for MyView."""
import pytest
from pytestqt.qtbot import QtBot

from src.views.my_view import MyView
from src.viewmodels.my_viewmodel import MyViewModel


def test_view_displays_data(qtbot, mocker):
    """Test that view displays data from viewmodel."""
    # Arrange
    mock_service = mocker.Mock()
    mock_service.fetch_data.return_value = [{"id": 1}]
    viewmodel = MyViewModel(mock_service)
    view = MyView(viewmodel)
    qtbot.addWidget(view)

    # Act
    viewmodel.load_data()
    qtbot.wait(100)

    # Assert
    assert view._list_widget.count() == 1
```

## Checklist

- [ ] Created file in `DFBU/gui/`
- [ ] Designed UI in Qt Designer (saved to `DFBU/gui/designer/`)
- [ ] Inherits from appropriate Qt widget class
- [ ] Accepts ViewModel in constructor
- [ ] `_load_ui()` method loads .ui file with QUiLoader
- [ ] `_connect_signals()` method for connections
- [ ] Type hints on methods
- [ ] Docstrings for public APIs
- [ ] Minimal logic (UI state only)
- [ ] No business logic
- [ ] No data validation
- [ ] Proper resource cleanup
- [ ] Responsive layout
- [ ] Updated `DFBU/gui/__init__.py` if needed

## Common Patterns

### Custom Widgets
```python
class CustomWidget(QWidget):
    """Custom reusable widget."""

    value_changed = Signal(int)  # Custom signal

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def setValue(self, value: int) -> None:
        """Set widget value."""
        self._value = value
        self._update_display()
        self.value_changed.emit(value)
```

### Validation Feedback
```python
def _on_validation_changed(self, is_valid: bool, message: str):
    """Show validation feedback."""
    if is_valid:
        self._input.setStyleSheet("")
        self._error_label.hide()
    else:
        self._input.setStyleSheet("border: 1px solid red;")
        self._error_label.setText(message)
        self._error_label.show()
```
