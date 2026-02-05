# DFBU UI Refinement Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the sparse, half-baked DFBU UI into a polished, streamlined interface by removing the menubar entirely, adding a split-pane layout with always-visible log, and reordering tabs to match logical workflow.

**Architecture:** The changes focus on the View layer only (MVVM pattern). We modify the Qt Designer `.ui` file to restructure the layout (QSplitter for split-pane, header toolbar for menu replacements), update `view.py` to handle new widgets and add QShortcut bindings for keyboard access, and extend the QSS stylesheet for new components.

**Tech Stack:** PySide6/Qt6, QUiLoader pattern, QSplitter, QShortcut, Python 3.14+

---

## Summary of Changes

| Area | Current | Proposed |
|------|---------|----------|
| Menubar | File, Operations, Help menus | **Remove entirely** |
| Essential Actions | In menus | Header toolbar with Help/About buttons |
| Layout | Tabs fill entire window | QSplitter: Tabs (65% left) + Log pane (35% right) |
| Tab Order | Backup → Restore → Configuration → Logs | Backup → Configuration → Restore (no Logs tab) |
| Keyboard Shortcuts | Via menu accelerators | QShortcut bindings in view.py |

---

## Task 1: Add Header Toolbar to UI

**Purpose:** Create the header bar that will hold app branding and action buttons (Help, About) to replace menu functionality.

**Files:**
- Modify: `DFBU/gui/designer/main_window_complete.ui`

**Step 1: Add headerBar widget before tab_widget**

In the `.ui` file, insert this new widget as the first item in `main_layout` (before the `<item>` containing `tab_widget` at line 45):

```xml
<item>
 <widget class="QWidget" name="headerBar">
  <property name="sizePolicy">
   <sizepolicy hsizetype="Expanding" vsizetype="Fixed">
    <horstretch>0</horstretch>
    <verstretch>0</verstretch>
   </sizepolicy>
  </property>
  <property name="minimumSize">
   <size>
    <width>0</width>
    <height>48</height>
   </size>
  </property>
  <property name="maximumSize">
   <size>
    <width>16777215</width>
    <height>48</height>
   </size>
  </property>
  <property name="styleSheet">
   <string>background-color: #F8FAFC; border-bottom: 1px solid #E2E8F0;</string>
  </property>
  <layout class="QHBoxLayout" name="headerBarLayout">
   <property name="spacing">
    <number>12</number>
   </property>
   <property name="leftMargin">
    <number>16</number>
   </property>
   <property name="topMargin">
    <number>8</number>
   </property>
   <property name="rightMargin">
    <number>16</number>
   </property>
   <property name="bottomMargin">
    <number>8</number>
   </property>
   <item>
    <widget class="QLabel" name="headerIcon">
     <property name="maximumSize">
      <size>
       <width>24</width>
       <height>24</height>
      </size>
     </property>
     <property name="pixmap">
      <pixmap>../resources/icons/dfbu.svg</pixmap>
     </property>
     <property name="scaledContents">
      <bool>true</bool>
     </property>
    </widget>
   </item>
   <item>
    <widget class="QLabel" name="headerTitle">
     <property name="styleSheet">
      <string>font-size: 15px; font-weight: bold; color: #1E293B; border: none; background: transparent;</string>
     </property>
     <property name="text">
      <string>DFBU - Dotfiles Backup Utility</string>
     </property>
    </widget>
   </item>
   <item>
    <spacer name="headerSpacer">
     <property name="orientation">
      <enum>Qt::Orientation::Horizontal</enum>
     </property>
     <property name="sizeHint" stdset="0">
      <size>
       <width>40</width>
       <height>20</height>
      </size>
     </property>
    </spacer>
   </item>
   <item>
    <widget class="QPushButton" name="helpButton">
     <property name="sizePolicy">
      <sizepolicy hsizetype="Fixed" vsizetype="Fixed">
       <horstretch>0</horstretch>
       <verstretch>0</verstretch>
      </sizepolicy>
     </property>
     <property name="minimumSize">
      <size>
       <width>32</width>
       <height>32</height>
      </size>
     </property>
     <property name="maximumSize">
      <size>
       <width>32</width>
       <height>32</height>
      </size>
     </property>
     <property name="toolTip">
      <string>Help (F1)</string>
     </property>
     <property name="text">
      <string>?</string>
     </property>
     <property name="styleSheet">
      <string>font-weight: bold; font-size: 14px;</string>
     </property>
    </widget>
   </item>
   <item>
    <widget class="QPushButton" name="aboutButton">
     <property name="sizePolicy">
      <sizepolicy hsizetype="Maximum" vsizetype="Fixed">
       <horstretch>0</horstretch>
       <verstretch>0</verstretch>
      </sizepolicy>
     </property>
     <property name="minimumSize">
      <size>
       <width>0</width>
       <height>32</height>
      </size>
     </property>
     <property name="toolTip">
      <string>About DFBU</string>
     </property>
     <property name="text">
      <string>About</string>
     </property>
    </widget>
   </item>
  </layout>
 </widget>
</item>
```

**Step 2: Run the app to verify header appears**

Run: `python DFBU/dfbu_gui.py`
Expected: Header bar visible at top with icon, title, Help (?) and About buttons

**Step 3: Commit**

```bash
git add DFBU/gui/designer/main_window_complete.ui
git commit -m "$(cat <<'EOF'
feat(ui): add header toolbar with branding and action buttons

Adds a fixed-height header bar at the top of the main window containing
the app icon, title, and Help/About buttons. This prepares for removing
the menubar in the next step.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Remove Menubar from UI

**Purpose:** Remove the sparse menubar (File has only Exit, Operations duplicates buttons, Help has only User Guide/About).

**Files:**
- Modify: `DFBU/gui/designer/main_window_complete.ui`

**Step 1: Remove menubar widget section**

Delete the entire `<widget class="QMenuBar">` section (lines 1591-1627 in the original file):

```xml
<!-- DELETE THIS ENTIRE BLOCK -->
<widget class="QMenuBar" name="menubar">
  ...entire menubar definition...
</widget>
```

**Step 2: Remove action definitions**

Delete all `<action>` definitions (lines 1646-1690 in the original file):

```xml
<!-- DELETE THESE ACTIONS -->
<action name="actionExit">...</action>
<action name="actionStartBackup">...</action>
<action name="actionStartRestore">...</action>
<action name="actionAbout">...</action>
<action name="actionVerifyBackup">...</action>
<action name="actionUserGuide">...</action>
```

**Step 3: Run the app to verify menubar is gone**

Run: `python DFBU/dfbu_gui.py`
Expected: No menubar visible, header toolbar still present

**Step 4: Commit**

```bash
git add DFBU/gui/designer/main_window_complete.ui
git commit -m "$(cat <<'EOF'
feat(ui): remove sparse menubar entirely

The menubar had minimal utility (File->Exit, duplicated Operations,
sparse Help menu). Actions are now accessible via header toolbar
buttons and keyboard shortcuts.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Update view.py to Remove Menu Code and Add Header Handlers

**Purpose:** Remove dead menu code from view.py and wire up the new header buttons.

**Files:**
- Modify: `DFBU/gui/view.py`

**Step 1: Add QShortcut import**

At the top of view.py, add to the QtGui imports (around line 47):

```python
from PySide6.QtGui import QAction, QCloseEvent, QColor, QPixmap, QTextCursor, QShortcut, QKeySequence
```

**Step 2: Remove `_find_menu_actions` method**

Delete the entire `_find_menu_actions` method (lines 760-792).

**Step 3: Remove the call to `_find_menu_actions`**

In `_discover_widgets` method, remove the line:
```python
self._find_menu_actions(loaded_window)
```

**Step 4: Remove menu action signal connections**

In `_connect_ui_signals` method, delete lines 876-882:
```python
# Menu action connections
self.action_exit.triggered.connect(self.close)
self.action_start_backup.triggered.connect(self._on_start_backup)
self.action_start_restore.triggered.connect(self._on_start_restore)
self.action_verify_backup.triggered.connect(self._on_verify_backup)
self.action_about.triggered.connect(self._show_about)
self.action_user_guide.triggered.connect(self._show_user_guide)
```

**Step 5: Add method to find header widgets**

Add a new method after `_find_status_widgets`:

```python
def _find_header_widgets(self, ui_widget: QWidget) -> None:
    """Find and store references to header bar widgets."""
    self._help_btn: QPushButton = ui_widget.findChild(
        QPushButton, "helpButton"
    )  # type: ignore[assignment]
    self._about_btn: QPushButton = ui_widget.findChild(
        QPushButton, "aboutButton"
    )  # type: ignore[assignment]
```

**Step 6: Call the new method in `_discover_widgets`**

Add after `_find_status_widgets()` call:
```python
self._find_header_widgets(ui_widget)
```

**Step 7: Add method to setup keyboard shortcuts**

Add a new method after `_connect_ui_signals`:

```python
def _setup_shortcuts(self) -> None:
    """Set up keyboard shortcuts for actions previously in menus."""
    QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
    QShortcut(QKeySequence("F1"), self, self._show_user_guide)
    QShortcut(QKeySequence("Ctrl+B"), self, self._on_start_backup)
    QShortcut(QKeySequence("Ctrl+R"), self, self._on_start_restore)
    QShortcut(QKeySequence("Ctrl+V"), self, self._on_verify_backup)
```

**Step 8: Connect header buttons in `_connect_ui_signals`**

Add at the end of `_connect_ui_signals`:
```python
# Header bar connections
if self._help_btn:
    self._help_btn.clicked.connect(self._show_user_guide)
if self._about_btn:
    self._about_btn.clicked.connect(self._show_about)
```

**Step 9: Call `_setup_shortcuts` in `__init__`**

After the `_connect_ui_signals()` call in `__init__`, add:
```python
self._setup_shortcuts()
```

**Step 10: Run type checker**

Run: `mypy DFBU/`
Expected: 0 errors

**Step 11: Run the app to verify**

Run: `python DFBU/dfbu_gui.py`
Expected:
- Help button opens user guide
- About button opens about dialog
- Ctrl+Q exits
- F1 opens help
- Ctrl+B starts backup (when config loaded)
- Ctrl+R starts restore
- Ctrl+V verifies backup

**Step 12: Commit**

```bash
git add DFBU/gui/view.py
git commit -m "$(cat <<'EOF'
feat(ui): wire up header buttons and keyboard shortcuts

- Removes dead menu action code
- Adds header button signal connections
- Implements QShortcut bindings for Ctrl+Q, F1, Ctrl+B, Ctrl+R, Ctrl+V

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Implement Split-Pane Layout with QSplitter

**Purpose:** Create a 65/35 split with tabs on left and always-visible log pane on right.

**Files:**
- Modify: `DFBU/gui/designer/main_window_complete.ui`

**Step 1: Wrap tab_widget in QSplitter**

Replace the current `<item>` containing `tab_widget` with a QSplitter structure. The new structure should be:

```xml
<item>
 <widget class="QSplitter" name="mainSplitter">
  <property name="orientation">
   <enum>Qt::Orientation::Horizontal</enum>
  </property>
  <property name="childrenCollapsible">
   <bool>false</bool>
  </property>
  <!-- Tab widget goes here as first child -->
  <widget class="QTabWidget" name="tab_widget">
    <!-- KEEP ALL EXISTING tab_widget CONTENT -->
  </widget>
  <!-- Log pane as second child -->
  <widget class="QWidget" name="logPane">
   <property name="sizePolicy">
    <sizepolicy hsizetype="Expanding" vsizetype="Expanding">
     <horstretch>35</horstretch>
     <verstretch>0</verstretch>
    </sizepolicy>
   </property>
   <property name="minimumSize">
    <size>
     <width>300</width>
     <height>0</height>
    </size>
   </property>
   <layout class="QVBoxLayout" name="logPaneLayout">
    <property name="spacing">
     <number>0</number>
    </property>
    <property name="leftMargin">
     <number>0</number>
    </property>
    <property name="topMargin">
     <number>0</number>
    </property>
    <property name="rightMargin">
     <number>0</number>
    </property>
    <property name="bottomMargin">
     <number>0</number>
    </property>
    <!-- Log header -->
    <item>
     <widget class="QWidget" name="logHeader">
      <property name="sizePolicy">
       <sizepolicy hsizetype="Expanding" vsizetype="Fixed">
        <horstretch>0</horstretch>
        <verstretch>0</verstretch>
       </sizepolicy>
      </property>
      <property name="minimumSize">
       <size>
        <width>0</width>
        <height>48</height>
       </size>
      </property>
      <property name="styleSheet">
       <string>background-color: #F8FAFC; border-bottom: 1px solid #E2E8F0;</string>
      </property>
      <layout class="QHBoxLayout" name="logHeaderLayout">
       <property name="spacing">
        <number>4</number>
       </property>
       <property name="leftMargin">
        <number>12</number>
       </property>
       <property name="topMargin">
        <number>8</number>
       </property>
       <property name="rightMargin">
        <number>12</number>
       </property>
       <property name="bottomMargin">
        <number>8</number>
       </property>
       <item>
        <widget class="QLabel" name="logPaneTitle">
         <property name="styleSheet">
          <string>font-weight: bold; font-size: 13px; color: #1E293B; border: none; background: transparent;</string>
         </property>
         <property name="text">
          <string>Operation Log</string>
         </property>
        </widget>
       </item>
       <item>
        <spacer name="logHeaderSpacer1">
         <property name="orientation">
          <enum>Qt::Orientation::Horizontal</enum>
         </property>
         <property name="sizeType">
          <enum>QSizePolicy::Policy::Fixed</enum>
         </property>
         <property name="sizeHint" stdset="0">
          <size>
           <width>16</width>
           <height>20</height>
          </size>
         </property>
        </spacer>
       </item>
       <item>
        <widget class="QPushButton" name="logPaneFilterAllButton">
         <property name="text">
          <string>All</string>
         </property>
         <property name="checkable">
          <bool>true</bool>
         </property>
         <property name="checked">
          <bool>true</bool>
         </property>
         <property name="sizePolicy">
          <sizepolicy hsizetype="Maximum" vsizetype="Maximum">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QPushButton" name="logPaneFilterInfoButton">
         <property name="text">
          <string>Info</string>
         </property>
         <property name="checkable">
          <bool>true</bool>
         </property>
         <property name="checked">
          <bool>true</bool>
         </property>
         <property name="sizePolicy">
          <sizepolicy hsizetype="Maximum" vsizetype="Maximum">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QPushButton" name="logPaneFilterWarningButton">
         <property name="text">
          <string>Warn</string>
         </property>
         <property name="checkable">
          <bool>true</bool>
         </property>
         <property name="checked">
          <bool>true</bool>
         </property>
         <property name="sizePolicy">
          <sizepolicy hsizetype="Maximum" vsizetype="Maximum">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QPushButton" name="logPaneFilterErrorButton">
         <property name="text">
          <string>Errors</string>
         </property>
         <property name="checkable">
          <bool>true</bool>
         </property>
         <property name="checked">
          <bool>true</bool>
         </property>
         <property name="sizePolicy">
          <sizepolicy hsizetype="Maximum" vsizetype="Maximum">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
        </widget>
       </item>
       <item>
        <spacer name="logHeaderSpacer2">
         <property name="orientation">
          <enum>Qt::Orientation::Horizontal</enum>
         </property>
         <property name="sizeHint" stdset="0">
          <size>
           <width>40</width>
           <height>20</height>
          </size>
         </property>
        </spacer>
       </item>
       <item>
        <widget class="QPushButton" name="logPaneClearButton">
         <property name="text">
          <string>Clear</string>
         </property>
         <property name="sizePolicy">
          <sizepolicy hsizetype="Maximum" vsizetype="Maximum">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QPushButton" name="logPaneSaveButton">
         <property name="text">
          <string>Save</string>
         </property>
         <property name="sizePolicy">
          <sizepolicy hsizetype="Maximum" vsizetype="Maximum">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
        </widget>
       </item>
       <item>
        <widget class="QPushButton" name="logPaneVerifyButton">
         <property name="text">
          <string>Verify</string>
         </property>
         <property name="toolTip">
          <string>Verify integrity of the last backup operation</string>
         </property>
         <property name="sizePolicy">
          <sizepolicy hsizetype="Maximum" vsizetype="Maximum">
           <horstretch>0</horstretch>
           <verstretch>0</verstretch>
          </sizepolicy>
         </property>
        </widget>
       </item>
      </layout>
     </widget>
    </item>
    <!-- Log text area -->
    <item>
     <widget class="QTextEdit" name="logPaneBox">
      <property name="sizePolicy">
       <sizepolicy hsizetype="Expanding" vsizetype="Expanding">
        <horstretch>0</horstretch>
        <verstretch>0</verstretch>
       </sizepolicy>
      </property>
      <property name="readOnly">
       <bool>true</bool>
      </property>
     </widget>
    </item>
   </layout>
  </widget>
 </widget>
</item>
```

**Step 2: Update tab_widget stretch factor**

Add stretch factor to tab_widget (65%):

```xml
<widget class="QTabWidget" name="tab_widget">
 <property name="sizePolicy">
  <sizepolicy hsizetype="Expanding" vsizetype="Expanding">
   <horstretch>65</horstretch>
   <verstretch>0</verstretch>
  </sizepolicy>
 </property>
 <!-- rest of existing content -->
</widget>
```

**Step 3: Run the app to verify split layout**

Run: `python DFBU/dfbu_gui.py`
Expected:
- Split layout visible with tabs on left (~65%)
- Log pane always visible on right (~35%)
- Splitter is draggable
- Log pane doesn't collapse below 300px

**Step 4: Commit**

```bash
git add DFBU/gui/designer/main_window_complete.ui
git commit -m "$(cat <<'EOF'
feat(ui): implement 65/35 split-pane layout with always-visible log

Wraps tab widget in QSplitter with log pane on right. The log is now
always visible during operations without switching tabs. Includes
filter buttons, clear, save, and verify actions in log header.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Remove Logs Tab and Reorder Remaining Tabs

**Purpose:** Remove the now-redundant Logs tab and reorder to Backup → Configuration → Restore.

**Files:**
- Modify: `DFBU/gui/designer/main_window_complete.ui`

**Step 1: Delete the logTab widget**

Remove the entire `<widget class="QWidget" name="logTab">` section (lines 1408-1586 in the original file).

**Step 2: Reorder tab widgets**

In the `tab_widget`, reorder the remaining widgets:
1. `backupTab` (position 0 - unchanged)
2. `configTab` (position 1 - move from position 2)
3. `restoreTab` (position 2 - move from position 1)

**Step 3: Run the app to verify tab order**

Run: `python DFBU/dfbu_gui.py`
Expected:
- Only 3 tabs: Backup, Configuration, Restore
- No Logs tab
- Log pane still visible on right

**Step 4: Commit**

```bash
git add DFBU/gui/designer/main_window_complete.ui
git commit -m "$(cat <<'EOF'
feat(ui): remove Logs tab and reorder to Backup → Config → Restore

Removes redundant Logs tab (now in split pane). Reorders tabs to match
logical workflow: Backup (primary action), Configuration (setup),
Restore (rarely used last resort).

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Update view.py for New Log Pane Widgets

**Purpose:** Wire up the new log pane widgets and update tab index references.

**Files:**
- Modify: `DFBU/gui/view.py`

**Step 1: Add method to find log pane widgets**

Add a new method to find the log pane widgets:

```python
def _find_log_pane_widgets(self, ui_widget: QWidget) -> None:
    """Find and store references to log pane widgets (split view)."""
    self._log_pane_box: QTextEdit = ui_widget.findChild(
        QTextEdit, "logPaneBox"
    )  # type: ignore[assignment]
    self._log_pane_filter_all_btn: QPushButton = ui_widget.findChild(
        QPushButton, "logPaneFilterAllButton"
    )  # type: ignore[assignment]
    self._log_pane_filter_info_btn: QPushButton = ui_widget.findChild(
        QPushButton, "logPaneFilterInfoButton"
    )  # type: ignore[assignment]
    self._log_pane_filter_warning_btn: QPushButton = ui_widget.findChild(
        QPushButton, "logPaneFilterWarningButton"
    )  # type: ignore[assignment]
    self._log_pane_filter_error_btn: QPushButton = ui_widget.findChild(
        QPushButton, "logPaneFilterErrorButton"
    )  # type: ignore[assignment]
    self._log_pane_clear_btn: QPushButton = ui_widget.findChild(
        QPushButton, "logPaneClearButton"
    )  # type: ignore[assignment]
    self._log_pane_save_btn: QPushButton = ui_widget.findChild(
        QPushButton, "logPaneSaveButton"
    )  # type: ignore[assignment]
    self._log_pane_verify_btn: QPushButton = ui_widget.findChild(
        QPushButton, "logPaneVerifyButton"
    )  # type: ignore[assignment]
```

**Step 2: Call the new method in `_discover_widgets`**

Add after `_find_header_widgets(ui_widget)`:
```python
self._find_log_pane_widgets(ui_widget)
```

**Step 3: Update operation_log reference**

Update the `operation_log` property to use the new log pane:

```python
# In __init__ or where operation_log is set
self.operation_log = self._log_pane_box
```

**Step 4: Connect log pane button signals**

Add to `_connect_ui_signals`:

```python
# Log pane connections (split view)
if self._log_pane_filter_all_btn:
    self._log_pane_filter_all_btn.clicked.connect(self._on_log_filter_all)
if self._log_pane_filter_info_btn:
    self._log_pane_filter_info_btn.clicked.connect(self._on_log_filter_changed)
if self._log_pane_filter_warning_btn:
    self._log_pane_filter_warning_btn.clicked.connect(self._on_log_filter_changed)
if self._log_pane_filter_error_btn:
    self._log_pane_filter_error_btn.clicked.connect(self._on_log_filter_changed)
if self._log_pane_clear_btn:
    self._log_pane_clear_btn.clicked.connect(self._on_clear_log)
if self._log_pane_save_btn:
    self._log_pane_save_btn.clicked.connect(self._on_save_log)
if self._log_pane_verify_btn:
    self._log_pane_verify_btn.clicked.connect(self._on_verify_backup)
```

**Step 5: Update tab index references**

Search for `setCurrentIndex(3)` (Logs tab) and remove those lines since log is always visible:

```python
# Remove these lines from _on_start_backup:
# self.tab_widget.setCurrentIndex(3)

# Remove these lines from _on_start_restore:
# self.tab_widget.setCurrentIndex(3)
```

**Step 6: Update filter button references in handlers**

Update `_on_log_filter_all` and `_on_log_filter_changed` to use the new log pane buttons:

```python
def _on_log_filter_all(self) -> None:
    """Handle 'All' filter button click - toggles all filters."""
    is_checked = self._log_pane_filter_all_btn.isChecked()
    self._log_pane_filter_info_btn.setChecked(is_checked)
    self._log_pane_filter_warning_btn.setChecked(is_checked)
    self._log_pane_filter_error_btn.setChecked(is_checked)
    self._apply_log_filter()

def _on_log_filter_changed(self) -> None:
    """Handle individual filter button changes."""
    # Update "All" button state based on individual filters
    all_checked = (
        self._log_pane_filter_info_btn.isChecked()
        and self._log_pane_filter_warning_btn.isChecked()
        and self._log_pane_filter_error_btn.isChecked()
    )
    self._log_pane_filter_all_btn.setChecked(all_checked)
    self._apply_log_filter()
```

**Step 7: Run type checker**

Run: `mypy DFBU/`
Expected: 0 errors

**Step 8: Run the app to verify log pane functionality**

Run: `python DFBU/dfbu_gui.py`
Expected:
- Log pane filter buttons work
- Clear button clears log
- Save button saves log
- Verify button triggers verification
- Operations log to the pane (no tab switching)

**Step 9: Commit**

```bash
git add DFBU/gui/view.py
git commit -m "$(cat <<'EOF'
feat(ui): wire up log pane widgets and remove tab switching

- Adds log pane widget discovery and signal connections
- Updates operation_log to use logPaneBox
- Removes tab switching to Logs tab (now always visible)
- Updates filter handlers to use log pane buttons

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Add QSS Styles for New Components

**Purpose:** Ensure consistent styling for header bar and log pane.

**Files:**
- Modify: `DFBU/gui/styles/dfbu_light.qss`

**Step 1: Add header bar styles**

Add after the Status Bar section:

```css
/* ==========================================================================
   14. Header Bar — #headerBar
   ========================================================================== */

#headerBar {
    background-color: #F8FAFC;
    border-bottom: 1px solid #E2E8F0;
}

#headerBar QPushButton {
    padding: 4px 12px;
    min-height: 28px;
}

#headerTitle {
    font-size: 15px;
    font-weight: bold;
    color: #1E293B;
    background: transparent;
    border: none;
}


/* ==========================================================================
   15. Log Pane — #logPane
   ========================================================================== */

#logPane {
    background-color: #FFFFFF;
    border-left: 1px solid #E2E8F0;
}

#logHeader {
    background-color: #F8FAFC;
    border-bottom: 1px solid #E2E8F0;
}

#logPaneTitle {
    font-weight: bold;
    font-size: 13px;
    color: #1E293B;
    background: transparent;
    border: none;
}

#logHeader QPushButton {
    padding: 4px 8px;
    font-size: 12px;
    min-height: 24px;
}
```

**Step 2: Run the app to verify styles**

Run: `python DFBU/dfbu_gui.py`
Expected: Header bar and log pane have consistent styling with the rest of the app

**Step 3: Commit**

```bash
git add DFBU/gui/styles/dfbu_light.qss
git commit -m "$(cat <<'EOF'
style(ui): add QSS rules for header bar and log pane

Adds consistent styling for the new header toolbar and split-pane
log components to match the existing design system.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Run Tests and Final Verification

**Purpose:** Ensure all changes work correctly and don't break existing functionality.

**Files:**
- None (verification only)

**Step 1: Run type checker**

Run: `mypy DFBU/`
Expected: 0 errors

**Step 2: Run unit tests**

Run: `pytest DFBU/tests/ -m "not slow" -v`
Expected: All tests pass

**Step 3: Manual verification checklist**

Run: `python DFBU/dfbu_gui.py`

Verify:
- [ ] No menubar visible
- [ ] Header bar shows icon, title, Help (?), About buttons
- [ ] Help button opens user guide
- [ ] About button opens about dialog
- [ ] Split layout: tabs on left (~65%), log pane on right (~35%)
- [ ] Splitter is draggable
- [ ] Log pane minimum width: 300px
- [ ] Tab order: Backup → Configuration → Restore (3 tabs only)
- [ ] Log filter buttons work (All/Info/Warn/Errors)
- [ ] Clear Log button works
- [ ] Save Log button works
- [ ] Verify button works
- [ ] Keyboard shortcuts:
  - [ ] Ctrl+Q exits
  - [ ] F1 opens help
  - [ ] Ctrl+B starts backup (when config loaded)
  - [ ] Ctrl+R starts restore
  - [ ] Ctrl+V verifies backup
- [ ] Backup operation logs to pane (no tab switching)
- [ ] Restore operation logs to pane (no tab switching)

**Step 4: Commit verification**

```bash
git status
```
Expected: Clean working tree (all changes committed)

---

## Files Modified Summary

| File | Changes |
|------|---------|
| `DFBU/gui/designer/main_window_complete.ui` | Add header toolbar, remove menubar, add QSplitter with log pane, remove Logs tab, reorder tabs |
| `DFBU/gui/view.py` | Remove menu code, add header/log pane widget discovery, add QShortcut bindings, update tab index references |
| `DFBU/gui/styles/dfbu_light.qss` | Add styles for #headerBar and #logPane |

---

## Verification Commands

```bash
# Type check
mypy DFBU/

# Run tests
pytest DFBU/tests/ -m "not slow" -v

# Run application
python DFBU/dfbu_gui.py
```
