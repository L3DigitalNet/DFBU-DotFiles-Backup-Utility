------
mode: "agent"
description: "Create or update a Qt Designer .ui file from Python View code following MVVM architecture"
------

# Create Qt Designer .ui File for PySide6 MVVM Application

## Overview

This prompt generates a complete, valid Qt Designer `.ui` file by analyzing the View layer of a PySide6 MVVM application. It extracts UI elements from Python code and creates a Designer-compatible XML file.

### Key Principles

1. **View Layer Focus**: Only analyze `src/views/` Python files
2. **Complete Coverage**: Every widget referenced in code gets a UI element
3. **MVVM Compliant**: UI file reflects View layer, not ViewModel or Model
4. **Code-Driven**: Python View code is the single source of truth
5. **Designer Compatible**: Output is valid Qt Designer 4.0 XML

### What This Prompt Does

1. Scans View files (`src/views/*.py`) for widget definitions
2. Discovers all PySide6 widget types used
3. Extracts properties, layouts, and hierarchies from code
4. Generates complete, valid Qt Designer 4.0 XML
5. Validates output against View source code
6. Produces Designer-compatible `.ui` file

### Output Location

`src/views/[view_name].ui`

---

## Objective

Generate a complete Qt Designer `.ui` file (XML format) that accurately represents ALL UI widgets, layouts, actions, and properties defined in a View class. This supports the MVVM pattern by separating UI design from logic.

## Process

### 1. Analyze View File

Identify the target View class in `src/views/`:

```bash
# List all View files
ls src/views/*.py

# Examine specific View file
cat src/views/main_window.py
```

### 2. Extract Widget Hierarchy

Analyze the `_setup_ui()` method to understand widget structure:

- Parent-child relationships
- Layout hierarchy
- Widget types and names
- Properties and attributes

### 3. Identify Signal Connections

Note signal connections in `_connect_signals()` for documentation purposes (not included in .ui file):

- Button click handlers
- Text change handlers
- Custom signals

### 4. Generate .ui XML Structure

Create Qt Designer 4.0 XML with:

**Root Structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>ClassName</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect><x>0</x><y>0</y><width>800</width><height>600</height></rect>
  </property>
  <property name="windowTitle">
   <string>Application Title</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <!-- Central widget contents -->
  </widget>
 </widget>
 <resources/>
 <connections/>
</ui>
```

### 5. Map Python Widgets to .ui Elements

For each widget in Python code, create corresponding .ui element:

**Python Code:**
```python
self._button = QPushButton("Click Me")
self._button.setObjectName("actionButton")
```

**Corresponding .ui XML:**
```xml
<widget class="QPushButton" name="actionButton">
 <property name="text">
  <string>Click Me</string>
 </property>
</widget>
```

### 6. Handle Common Widget Types

#### Buttons
- QPushButton
- QToolButton
- QRadioButton
- QCheckBox

#### Input Widgets
- QLineEdit
- QTextEdit
- QPlainTextEdit
- QSpinBox
- QDoubleSpinBox
- QComboBox

#### Display Widgets
- QLabel
- QProgressBar
- QLCDNumber

#### Containers
- QGroupBox
- QTabWidget
- QFrame
- QScrollArea

#### Lists and Trees
- QListWidget
- QTreeWidget
- QTableWidget

### 7. Generate Widget Type Templates

For each widget type discovered in the codebase, use appropriate XML template:

**QLabel (text display)**:
```xml
<widget class="QLabel" name="objectName">
 <property name="text"><string>Label Text</string></property>
 <property name="alignment"><set>Qt::AlignCenter</set></property>
</widget>
```

**QPushButton**:
```xml
<widget class="QPushButton" name="objectName">
 <property name="text"><string>Button Text</string></property>
 <property name="toolTip"><string>Help text</string></property>
</widget>
```

**QProgressBar**:
```xml
<widget class="QProgressBar" name="objectName">
 <property name="value"><number>0</number></property>
 <property name="maximum"><number>100</number></property>
 <property name="textVisible"><bool>true</bool></property>
 <property name="format"><string>%p%</string></property>
</widget>
```

**QAction (menus/toolbars)**:
```xml
<action name="actionName">
 <property name="text"><string>Action Text</string></property>
 <property name="toolTip"><string>Help text</string></property>
 <property name="shortcut"><string>Ctrl+A</string></property>
 <property name="checkable"><bool>false</bool></property>
</action>
```

**QDockWidget**:
```xml
<widget class="QDockWidget" name="dockName">
 <property name="windowTitle"><string>Dock Title</string></property>
 <property name="allowedAreas">
  <set>Qt::LeftDockWidgetArea|Qt::RightDockWidgetArea</set>
 </property>
 <attribute name="dockWidgetArea"><number>2</number></attribute>
 <widget class="QWidget" name="dockWidgetContents">
  <layout class="QVBoxLayout">
   <!-- Dock content widgets -->
  </layout>
 </widget>
</widget>
```

**QToolBar**:
```xml
<widget class="QToolBar" name="toolbarName">
 <property name="windowTitle"><string>Toolbar Title</string></property>
 <property name="movable"><bool>false</bool></property>
 <property name="iconSize"><size><width>32</width><height>32</height></size></property>
 <attribute name="toolBarArea"><number>4</number></attribute>
 <addaction name="actionName"/>
</widget>
```

## Guidelines

### Do Include in .ui File

- Widget hierarchy and structure
- Layout configuration
- Widget properties (text, tooltips, sizes)
- Menus and toolbars
- Window geometry and title

### Do NOT Include in .ui File

- Signal/slot connections (keep in Python `_connect_signals()`)
- Business logic
- ViewModel references
- Complex initialization logic
- Dynamic widget creation

### Object Naming Convention

Use descriptive, snake_case names for widgets:

```python
self._save_button = QPushButton()      # name="save_button"
self._user_name_input = QLineEdit()    # name="user_name_input"
self._status_label = QLabel()          # name="status_label"
```

## Loading .ui Files in Python

After creating the .ui file, load it in the View:

```python
from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

class MainWindow(QMainWindow):
    def __init__(self, viewmodel: MainViewModel):
        super().__init__()
        self._viewmodel = viewmodel
        self._load_ui()
        self._connect_signals()

    def _load_ui(self) -> None:
        """Load UI from .ui file."""
        loader = QUiLoader()
        ui_file = QFile("src/views/main_window.ui")
        ui_file.open(QFile.ReadOnly)
        self._ui = loader.load(ui_file, self)
        ui_file.close()
        self.setCentralWidget(self._ui)

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # Access widgets via self._ui
        self._ui.save_button.clicked.connect(self._viewmodel.save)
```

## Validation

After generating the .ui file:

1. **Open in Qt Designer**: Verify visual layout
2. **Load in Python**: Test with QUiLoader
3. **Check Widget Names**: Ensure accessible from code
4. **Verify Properties**: Text, sizes, enabled states correct
5. **Test Layouts**: Resize window, check behavior

## Benefits for MVVM

- **Clean Separation**: UI design isolated from logic
- **Designer-Friendly**: Non-programmers can modify UI
- **Easy Testing**: ViewModel tests don't need UI
- **Rapid Prototyping**: Quick UI iterations
- **Professional Polish**: Access to full Designer features

## Next Steps

After creating .ui file:

1. Update View Python code to load .ui file
2. Update `_connect_signals()` to reference loaded widgets
3. Test View with ViewModel
4. Document any custom styling or behaviors
5. Commit both .ui and .py files

---

## Quick Reference: Widget Properties

### Common Property Extraction

```python
# Common setter patterns to search for:
widget.setText("...")         → <property name="text">
widget.setToolTip("...")      → <property name="toolTip">
widget.setMinimumSize(w, h)   → <property name="minimumSize">
widget.setMaximumSize(w, h)   → <property name="maximumSize">
widget.setEnabled(bool)       → <property name="enabled">
widget.setVisible(bool)       → <property name="visible">
widget.setStyleSheet("...")   → <property name="styleSheet">
widget.setValue(int)          → <property name="value">
widget.setMaximum(int)        → <property name="maximum">
action.setShortcut("...")     → <property name="shortcut">
```

### Layout Types

```python
# Layout creation patterns:
QVBoxLayout()    → <layout class="QVBoxLayout">
QHBoxLayout()    → <layout class="QHBoxLayout">
QGridLayout()    → <layout class="QGridLayout">
QFormLayout()    → <layout class="QFormLayout">
```

### Dock Widget Areas

```python
# Area constants (for attribute dockWidgetArea):
Qt.LeftDockWidgetArea   = 1
Qt.RightDockWidgetArea  = 2
Qt.TopDockWidgetArea    = 4
Qt.BottomDockWidgetArea = 8
```

### Toolbar Areas

```python
# Area constants (for attribute toolBarArea):
Qt.LeftToolBarArea   = 1
Qt.RightToolBarArea  = 2
Qt.TopToolBarArea    = 4
Qt.BottomToolBarArea = 8
```

## Standard Qt Designer Structure

Complete .ui file template:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>ViewClassName</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>800</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Window Title</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <layout class="QVBoxLayout" name="verticalLayout">
    <!-- Widgets here -->
   </layout>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>800</width>
     <height>22</height>
    </rect>
   </property>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
 </widget>
 <resources/>
 <connections/>
</ui>
