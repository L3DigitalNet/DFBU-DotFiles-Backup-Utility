# UI Design Guide - Qt Designer Workflow

## Overview

This project **NEVER** hardcodes UI in Python. All user interfaces are designed in Qt Designer and saved as `.ui` files.

## Quick Start

### 1. Open Qt Designer

```bash
# Open an existing .ui file
designer src/views/ui/main_window.ui

# Or launch Qt Designer to create a new file
designer
```

### 2. Design Your UI

1. **Choose a base widget** (QMainWindow, QDialog, QWidget)
2. **Drag and drop** widgets from the Widget Box
3. **Set properties** in the Property Editor
4. **Set objectName** for all widgets you'll access from Python
5. **Preview** your design (Form → Preview)

### 3. Save the .ui File

- Save to: `src/views/ui/your_view_name.ui`
- Use descriptive names matching your Python class

## Important: Object Names

**CRITICAL**: Set meaningful `objectName` properties in Qt Designer for widgets you'll access in Python.

Example:

- Button → `objectName`: `loadButton`
- List → `objectName`: `listWidget`
- Text Edit → `objectName`: `detailsText`

## Python Integration

### Loading .ui File in Python

```python
import os
from PySide6.QtWidgets import QMainWindow, QPushButton, QListWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile


class MyView(QMainWindow):
    def __init__(self):
        super().__init__()
        self._load_ui()

    def _load_ui(self):
        """Load UI from .ui file."""
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

        # For QMainWindow
        self.setCentralWidget(self.ui)

        # Access widgets by objectName
        self.my_button = self.ui.findChild(QPushButton, "myButton")
        self.my_list = self.ui.findChild(QListWidget, "myList")
```

### Connecting Signals

After loading the UI, connect widget signals to your methods:

```python
def _connect_signals(self):
    """Connect signals to slots."""
    self.my_button.clicked.connect(self._on_button_clicked)
    self.my_list.itemClicked.connect(self._on_item_clicked)

def _on_button_clicked(self):
    """Handle button click."""
    print("Button clicked!")

def _on_item_clicked(self, item):
    """Handle list item click."""
    print(f"Item clicked: {item.text()}")
```

## Common Patterns

### QMainWindow with Menu Bar

1. In Qt Designer: Add menu bar items
2. Set objectName for each QAction
3. In Python: Find actions and connect them

```python
# In Qt Designer: Create action with objectName="actionOpen"
# In Python:
action_open = self.ui.findChild(QAction, "actionOpen")
action_open.triggered.connect(self._on_open)
```

### Forms with Layouts

1. Use layout widgets (QVBoxLayout, QHBoxLayout, QGridLayout)
2. Set spacing and margins in Property Editor
3. Add widgets to layouts by dragging

### Dialog Windows

```python
from PySide6.QtWidgets import QDialog

class MyDialog(QDialog):
    def _load_ui(self):
        ui_file_path = os.path.join(
            os.path.dirname(__file__),
            'ui',
            'my_dialog.ui'
        )

        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        # For QDialog, set layout manually
        layout = QVBoxLayout(self)
        layout.addWidget(self.ui)
```

## Best Practices

### DO ✅

- **Use Qt Designer for ALL UI design**
- **Set meaningful objectName for all interactive widgets**
- **Use layouts for responsive design**
- **Preview your UI before saving**
- **Keep .ui files in `src/views/ui/` directory**
- **Match .ui filename with Python class name** (snake_case vs PascalCase)

### DON'T ❌

- **Never hardcode UI in Python** (`QPushButton("Text")`, `QVBoxLayout()`, etc.)
- **Don't skip setting objectName** - you won't be able to find widgets
- **Don't use absolute positioning** - use layouts instead
- **Don't mix .ui files with hardcoded UI** - choose one approach

## Troubleshooting

### "Cannot find widget with objectName"

**Problem**: `findChild()` returns `None`

**Solution**:

1. Open .ui file in Qt Designer
2. Select the widget
3. In Property Editor, set `objectName` property
4. Save the .ui file

### "Cannot open UI file"

**Problem**: `QFile.open()` returns `False`

**Solution**:

1. Check file path is correct
2. Verify .ui file exists
3. Check file permissions
4. Use absolute path or `os.path.join()` with `__file__`

### UI doesn't look right

**Problem**: Widgets overlap or don't resize properly

**Solution**:

1. Use layout widgets (QVBoxLayout, QHBoxLayout, QGridLayout)
2. Set size policies appropriately
3. Set stretch factors for flexible widgets
4. Preview in Qt Designer to verify

## Example: Creating a Simple Window

### Step 1: In Qt Designer

1. **New Form** → Choose "Main Window"
2. **Add widgets**:
   - Drag QLabel to center → Set text: "Hello World"
   - Set objectName: `helloLabel`
3. **Save as**: `src/views/ui/hello_window.ui`

### Step 2: In Python

```python
# src/views/hello_window.py
import os
from PySide6.QtWidgets import QMainWindow, QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile


class HelloWindow(QMainWindow):
    """Simple hello window."""

    def __init__(self):
        super().__init__()
        self._load_ui()
        self._setup_content()

    def _load_ui(self):
        ui_file_path = os.path.join(
            os.path.dirname(__file__),
            'ui',
            'hello_window.ui'
        )

        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)

        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.setCentralWidget(self.ui)

        # Access the label
        self.hello_label = self.ui.findChild(QLabel, "helloLabel")

    def _setup_content(self):
        """Set dynamic content."""
        self.hello_label.setText("Hello from Python!")


# Usage in main.py
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = HelloWindow()
    window.show()
    sys.exit(app.exec())
```

## Resources

- [Qt Designer Manual](https://doc.qt.io/qt-6/qtdesigner-manual.html)
- [PySide6 QUiLoader](https://doc.qt.io/qtforpython-6/PySide6/QtUiTools/QUiLoader.html)
- [Qt Layouts](https://doc.qt.io/qt-6/layout.html)
- [Qt Widget Classes](https://doc.qt.io/qt-6/widget-classes.html)

## Summary

Remember: **Design in Qt Designer → Load in Python → Connect signals**

This workflow keeps UI design visual and maintainable while keeping Python code focused on behavior and business logic.
