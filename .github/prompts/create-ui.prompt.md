---
mode: "agent"
description: "Create or update a Qt Designer .ui file representing the current state of the Qt UI as defined in Python code"
---

# Create Qt Designer .ui File from Python Code

## Overview

This prompt generates a complete, valid Qt Designer `.ui` file by **discovering and extracting ALL UI elements directly from Python source code**. It is fully automated and requires NO manual updates when new UI elements are added.

### Key Principles

1. **Zero Hardcoding**: No widget names or types are assumed—everything is discovered
2. **Complete Coverage**: Every `findChild()` call gets a matching UI element
3. **Future-Proof**: Works regardless of how many widgets exist now or later
4. **Code-Driven**: The Python code is the single source of truth
5. **Validation Built-In**: Automatic verification ensures completeness

### What This Prompt Does

1. Scans ALL Python files to find widget references
2. Discovers ALL Qt widget types actually used
3. Extracts properties, layouts, and hierarchies from code
4. Generates complete, valid Qt Designer 4.0 XML
5. Validates output against source code
6. Produces Designer-compatible `.ui` file

### Output Location

`/home/chris/GitHub/DFBU-DotFiles-Backup-Utility/DFBU/gui/designer/main_window_complete.ui`

---

## Objective

Generate a complete Qt Designer `.ui` file (XML format) that accurately represents ALL UI widgets, layouts, actions, and properties currently referenced in the project's Python view code. This process is fully automated and discovers all elements dynamically, requiring NO manual updates as the UI evolves.

## Process

### 1. Discover All View Files

**IMPORTANT:** Do not assume file locations. Dynamically discover ALL view-related files:

1. **Primary view module**: Search for `view.py` or similar in `DFBU/gui/`
2. **Dialog modules**: Discover all dialog classes (search for `Dialog` suffix in class names)
3. **Custom widgets**: Find all custom widget implementations (search for widget-related imports)
4. **UI helper modules**: Locate any UI utility or component modules

**Discovery Commands:**
```bash
# Find all view-related Python files
find DFBU/gui -name "*view*.py" -o -name "*dialog*.py" -o -name "*widget*.py"

# Search for QMainWindow usage
grep -r "QMainWindow" DFBU/gui/

# Find UI loader usage
grep -r "QUiLoader\|loadUi" DFBU/gui/
```

### 2. Extract Complete Widget Inventory

Systematically scan ALL discovered files to build a complete widget inventory:

**Step 2.1: Scan for Widget References**

Search for ALL `findChild()` patterns:
```python
# Pattern 1: Direct assignment
self.widget_name = self.main_window.findChild(WidgetType, "objectName")

# Pattern 2: Helper method calls
self._get_required_ui_element(WidgetType, "objectName")
self._get_optional_ui_element(WidgetType, "objectName")

# Pattern 3: Inline usage
widget = parent.findChild(WidgetType, "name")
```

**Step 2.2: Identify All Qt Widget Types**

Discover all Qt widget types actually used in the codebase:
```bash
# Find all PySide6 widget imports
grep -r "from PySide6.QtWidgets import" DFBU/gui/

# Find all PySide6 GUI imports (QAction, etc.)
grep -r "from PySide6.QtGui import" DFBU/gui/

# Find all custom widget classes
grep -r "class.*\(Q.*\):" DFBU/gui/
```

**Step 2.3: Map Object Names to Widget Types**

Create a complete mapping:
```python
{
    "objectName": {
        "type": "QWidgetType",
        "source_file": "path/to/file.py",
        "line_number": 123,
        "parent_context": "layout or parent widget"
    }
}
```

### 3. Discover Layout Structure

**Step 3.1: Identify Main Window Components**

Search for references to these standard QMainWindow areas:
- Central widget (`centralwidget`, `centralWidget`)
- Menu bar (`menubar`, `menuBar`)
- Status bar (`statusbar`, `statusBar`)
- Toolbars (search for `QToolBar`, `addToolBar`)
- Dock widgets (search for `QDockWidget`, `addDockWidget`)

**Step 3.2: Discover Layout Hierarchy**

For each container widget, determine:
1. Layout type (`QVBoxLayout`, `QHBoxLayout`, `QGridLayout`, `QFormLayout`)
2. Child widgets in order
3. Spacers and stretch factors
4. Margins and spacing values

**Step 3.3: Find Layout Reference Documentation**

Check for layout documentation:
```bash
# Look for layout reference files
find DFBU/gui -name "*LAYOUT*.md" -o -name "*layout*.md"
find DFBU/docs/ -name "*LAYOUT*.md" -o -name "*layout*.md"
```

Reference these files to understand the intended structure.

### 4. Extract Widget Properties

For EACH discovered widget, scan the code for property assignments:

**Step 4.1: Search for Property Setters**

```python
# Direct property calls
widget.setText("...")
widget.setToolTip("...")
widget.setMinimumSize(width, height)
widget.setMaximumSize(width, height)
widget.setEnabled(bool)
widget.setVisible(bool)
widget.setStyleSheet("...")
widget.setShortcut("...")
widget.setCheckable(bool)
widget.setValue(int)
widget.setMaximum(int)
widget.setFormat("...")
```

**Step 4.2: Infer Defaults from Context**

- Labels: Extract text from nearby code comments or variable names
- Progress bars: Default to 0-100 range, value=0
- Buttons: Text from variable name or nearby comments
- Actions: Text and shortcuts from nearby code

**Step 4.3: Discover Action Connections**

Find all signal connections:
```python
widget.clicked.connect(...)
action.triggered.connect(...)
widget.textChanged.connect(...)
```

Document these for reference (though .ui file may not include them all).

### 5. Build Complete UI File Structure

Generate XML with FULL hierarchy based on discovered structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">...</property>
  <property name="windowTitle">...</property>

  <!-- Central Widget with discovered layout -->
  <widget class="QWidget" name="centralwidget">
   <layout class="QVBoxLayout">
    <!-- All discovered central widgets here -->
   </layout>
  </widget>

  <!-- Menu Bar with ALL discovered menus and actions -->
  <widget class="QMenuBar" name="menubar">
   <widget class="QMenu" name="menuName">
    <addaction name="actionName"/>
   </widget>
  </widget>

  <!-- Status Bar -->
  <widget class="QStatusBar" name="statusbar"/>

  <!-- ALL discovered toolbars -->
  <widget class="QToolBar" name="toolbarName">
   <addaction name="actionName"/>
  </widget>

  <!-- ALL discovered dock widgets -->
  <widget class="QDockWidget" name="dockName">
   <widget class="QWidget" name="dockWidgetContents">
    <layout class="...">
     <!-- All dock content widgets -->
    </layout>
   </widget>
  </widget>
 </widget>

 <!-- ALL discovered actions -->
 <action name="actionName">
  <property name="text"><string>...</string></property>
  <property name="toolTip"><string>...</string></property>
  <property name="shortcut"><string>...</string></property>
 </action>
</ui>
```

### 6. Discover Styling and Theming

**Step 6.1: Find Style Definitions**

Search for all stylesheet assignments:
```bash
# Find stylesheet calls
grep -r "setStyleSheet" DFBU/gui/

# Find theme/style configuration files
find DFBU/data -name "*theme*.toml" -o -name "*style*.toml"
find DFBU/gui -name "*theme*.py" -o -name "*style*.py"
```

**Step 6.2: Extract Style Rules**

For each stylesheet found, extract:
- Widget-specific styles
- Color schemes
- Font definitions
- Border and spacing rules
- Hover/pressed states

**Step 6.3: Consolidate Application-Wide Styles**

Generate a main styleSheet property for QMainWindow that includes all discovered styles.

### 7. Generate Widget Type Templates

For each widget type discovered in the codebase, use appropriate XML template:

**QLabel (text display)**:
```xml
<widget class="QLabel" name="objectName">
 <property name="text"><string>Label Text</string></property>
 <property name="alignment"><set>Qt::AlignCenter</set></property>
</widget>
```

**QLabel (custom display like game surface)**:
```xml
<widget class="QLabel" name="gameDisplay">
 <property name="minimumSize">
  <size><width>800</width><height>600</height></size>
 </property>
 <property name="alignment"><set>Qt::AlignCenter</set></property>
 <property name="sizePolicy">
  <sizepolicy hsizetype="Expanding" vsizetype="Expanding">
   <horstretch>1</horstretch><verstretch>1</verstretch>
  </sizepolicy>
 </property>
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
 <property name="features">
  <set>QDockWidget::DockWidgetClosable|QDockWidget::DockWidgetMovable|QDockWidget::DockWidgetFloatable</set>
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

**QTabWidget**:
```xml
<widget class="QTabWidget" name="tabWidgetName">
 <property name="currentIndex"><number>0</number></property>
 <widget class="QWidget" name="tab1">
  <attribute name="title"><string>Tab 1</string></attribute>
  <layout class="QVBoxLayout">
   <!-- Tab content -->
  </layout>
 </widget>
</widget>
```

**QGroupBox**:
```xml
<widget class="QGroupBox" name="groupBoxName">
 <property name="title"><string>Group Title</string></property>
 <layout class="QVBoxLayout">
  <!-- Grouped widgets -->
 </layout>
</widget>
```

### 8. Automated Validation Process

**Step 8.1: Cross-Reference Check**

Generate a validation report that confirms:

```python
# For each findChild() call found
findChild_widgets = extract_findchild_calls(source_files)

# For each widget in generated .ui file
ui_widgets = parse_ui_file_widgets("main_window_complete.ui")

# Compare and report
missing_in_ui = findChild_widgets - ui_widgets
extra_in_ui = ui_widgets - findChild_widgets

# Report any mismatches
if missing_in_ui:
    print(f"ERROR: Widgets in code but missing in .ui: {missing_in_ui}")
if extra_in_ui:
    print(f"WARNING: Widgets in .ui but not referenced in code: {extra_in_ui}")
```

**Step 8.2: Structure Validation**

Verify XML structure integrity:
- [ ] Valid XML syntax
- [ ] Qt Designer 4.0 format compliance
- [ ] All referenced actions are defined
- [ ] All layouts have parent widgets
- [ ] Dock widget areas are valid (1=Left, 2=Right, 4=Top, 8=Bottom)
- [ ] Toolbar areas are valid (1=Left, 2=Right, 4=Top, 8=Bottom)
- [ ] All addaction references point to defined actions

**Step 8.3: Property Completeness**

For critical widgets, ensure required properties:
- objectName (REQUIRED for all widgets)
- Window titles for MainWindow, Docks, Toolbars
- Text for labels, buttons, actions
- Geometry for MainWindow
- Size policies for expanding widgets

### 9. Output Generation

**Location**: `/home/chris/GitHub/DFBU-DotFiles-Backup-Utility/DFBU/gui/designer/main_window_complete.ui`
**Format**: UTF-8 encoded XML, 1-space indentation (Qt Designer default)
**Structure**: Complete, valid Qt Designer XML

**Validation Commands**:
```bash
# Test XML validity
xmllint --noout /home/chris/GitHub/DFBU-DotFiles-Backup-Utility/DFBU/gui/designer/main_window_complete.ui

# Open in Qt Designer
pyside6-designer /home/chris/GitHub/DFBU-DotFiles-Backup-Utility/DFBU/gui/designer/main_window_complete.ui

# Test in application
cd /home/chris/GitHub/DFBU-DotFiles-Backup-Utility
python DFBU/dfbu-gui.py
```

## Adaptive Discovery Rules

These rules ensure the prompt works regardless of future UI additions:

### Rule 1: Complete Code Scanning

**NEVER assume what exists.** Always scan:
- All Python files in `DFBU/gui/`
- All dialog/widget custom classes
- All view-related modules
- All UI configuration files in `DFBU/data/`

### Rule 2: Type-Driven Widget Creation

For EVERY widget type found in imports:
1. Find all object names for that type
2. Extract properties from code
3. Generate appropriate XML element
4. Include in correct parent container

### Rule 3: Hierarchical Structure Discovery

Build layout hierarchy by:
1. Starting with QMainWindow
2. Finding central widget and its layout
3. Discovering all child widgets recursively
4. Mapping parent-child relationships
5. Preserving layout order from code

### Rule 4: Action Auto-Discovery

For every QAction:
1. Find where it's created or referenced
2. Extract text, tooltip, shortcut from code
3. Determine if it's in menubar, toolbar, or both
4. Generate action definition at bottom of XML
5. Add references in appropriate locations

### Rule 5: Property Inference

If property not explicitly set in code:
- Use Qt default values
- Infer from variable names (e.g., "hullProgressBar" → "Hull: %p%")
- Use sensible defaults for type (QProgressBar value=0, max=100)

### Rule 6: Future-Proof Patterns

Watch for these extensibility patterns:
- Tab widgets → Can have N tabs, discover all dynamically
- Group boxes → Can contain any widgets, scan contents
- Layouts → Can be nested, traverse recursively
- Dock widgets → Can be added/removed, find all references
- Toolbars → Can have multiple, discover by QToolBar type
- Menus → Can be nested, traverse menu hierarchy

## Critical Success Factors

1. **Zero Assumptions**: Every widget discovered from code, not hardcoded
2. **Complete Coverage**: ALL findChild() calls have matching UI elements
3. **Valid XML**: Always produces parseable, Designer-compatible output
4. **Extensible**: Works today and after 100 new widgets added
5. **Automated**: Requires NO human intervention or updates

## Output Requirements

The generated `.ui` file MUST:
- Be valid Qt Designer 4.0 XML
- Include XML declaration: `<?xml version="1.0" encoding="UTF-8"?>`
- Contain every widget referenced in ANY Python file
- Have correct hierarchy matching code structure
- Be immediately openable in `pyside6-designer`
- Work in application without code changes

## Testing Strategy

After generation, automatically verify:
1. XML parses without errors
2. Every findChild() object name exists in .ui
3. Can open in Qt Designer
4. Application loads without widget errors
5. All actions are accessible from UI

If ANY test fails, regenerate with corrections.

---

## Quick Reference: Discovery Patterns

### Finding Widgets

```bash
# All findChild calls
grep -rn "findChild" DFBU/gui/view.py DFBU/gui/

# All widget types imported
grep -rn "from PySide6.QtWidgets import" DFBU/gui/

# All action references
grep -rn "QAction" DFBU/gui/view.py

# All UI loader usage
grep -rn "QUiLoader\|loadUi" DFBU/gui/
```

### Widget Type Detection

```python
# Extract from code patterns:
self.widget = self.main_window.findChild(WidgetType, "objectName")
                                         ^^^^^^^^^^    ^^^^^^^^^^
                                         Use this      Exact XML name

# Widget types to search for:
QLabel, QPushButton, QProgressBar, QLineEdit, QTextEdit,
QComboBox, QSpinBox, QCheckBox, QRadioButton, QSlider,
QDockWidget, QTabWidget, QGroupBox, QAction, QMenu, QToolBar
```

### Property Extraction

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

### Layout Detection

```python
# Layout creation patterns:
layout = QVBoxLayout()    → <layout class="QVBoxLayout">
layout = QHBoxLayout()    → <layout class="QHBoxLayout">
layout = QGridLayout()    → <layout class="QGridLayout">
layout = QFormLayout()    → <layout class="QFormLayout">

# Layout methods:
layout.addWidget(widget)     → Widget order in XML
layout.addLayout(sublayout)  → Nested layout
layout.addStretch()          → <spacer> element
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

## Example Complete Workflow

```bash
# 1. Find all view files
find DFBU/gui -name "*view*.py" -o -name "*dialog*.py"

# 2. Extract all widget references
grep -rn "findChild" DFBU/gui/view.py | awk '{print $2}' > widgets.txt

# 3. For each widget, determine type
for widget in $(cat widgets.txt); do
    grep -B5 "$widget" DFBU/gui/view.py | grep "findChild"
done

# 4. Build XML structure (automated in prompt execution)
# 5. Validate XML
xmllint --noout /home/chris/GitHub/DFBU-DotFiles-Backup-Utility/DFBU/gui/designer/main_window_complete.ui

# 6. Test in Designer
pyside6-designer /home/chris/GitHub/DFBU-DotFiles-Backup-Utility/DFBU/gui/designer/main_window_complete.ui

# 7. Test in application
python DFBU/dfbu-gui.py
```

---

## Maintenance

**This prompt requires ZERO maintenance** as the UI evolves because:
- It discovers widgets from code, not a hardcoded list
- It adapts to new widget types automatically
- It extracts properties dynamically
- It validates completeness automatically

**When to re-run this prompt:**
- After adding new UI elements in Python code
- After modifying widget properties in Python
- After restructuring layouts
- To sync `.ui` file with current codebase state

**What NOT to do:**
- ❌ Manually edit this prompt to add specific widget names
- ❌ Hardcode widget lists or expected structures
- ❌ Assume specific UI components exist
- ✅ Trust the discovery process to find everything
