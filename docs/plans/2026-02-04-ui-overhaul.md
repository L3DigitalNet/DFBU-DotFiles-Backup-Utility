# DFBU UI Overhaul — Complete Implementation Plan

**Created:** 2026-02-04
**Status:** Planned
**Branch:** `feature/ui-overhaul` (create from `testing`)

## Overview

Transform DFBU's PySide6 GUI from default Qt styling to a polished, branded desktop application. 12 improvement areas ordered from highest to lowest impact. All changes preserve the existing MVVM architecture and `.ui` file loading pattern.

## Goals

1. Transform visual appearance from default Qt to polished branded desktop app
2. Establish a centralized theming and color system
3. Improve UX flow by reducing modal dialog fatigue
4. Enhance information hierarchy across all four tabs
5. Add missing polish: empty states, app icon, log filtering
6. Maintain existing MVVM architecture and `.ui` file pattern

## Dependency Graph

```
Step 1 (Color Palette) ─┬─→ Step 2 (QSS Theme) ─┬─→ Step 6 (Backup Tab Redesign)
                        │                         ├─→ Step 7 (Log Filtering)
                        │                         ├─→ Step 8 (Config Sections)
                        │                         └─→ Step 9 (Empty States)
                        ├─→ Step 4 (Spacing)
                        └─→ Step 5 (Toast Messages)
Step 3 (App Icon) ──────── (independent)
Step 10 (Restore Tab) ──── (independent)
Step 11 (Help Content) ─── (independent)
Step 12 (Final QA) ──────── (depends on all above)
```

## Files Summary

### New Files

| File | Step | Purpose |
|------|------|---------|
| `DFBU/gui/theme.py` | 1 | Centralized colors, spacing, typography constants |
| `DFBU/gui/styles/__init__.py` | 2 | Package init for styles |
| `DFBU/gui/styles/dfbu_light.qss` | 2 | Qt stylesheet for light theme |
| `DFBU/gui/theme_loader.py` | 2 | Utility to load and apply QSS at runtime |
| `DFBU/resources/help/quick_start.html` | 11 | Externalized help content |
| `DFBU/resources/help/config_reference.html` | 11 | Externalized help content |

### Modified Files

| File | Steps | Changes |
|------|-------|---------|
| `DFBU/dfbu_gui.py` | 2, 3 | Apply theme, set app icon |
| `DFBU/gui/view.py` | 1, 5, 6, 7, 9 | Color constants, toast messages, layout, log methods, empty states |
| `DFBU/gui/size_warning_dialog.py` | 1 | Use DFBUColors for level colors |
| `DFBU/gui/constants.py` | 1 | Import or merge with theme.py |
| `DFBU/gui/help_dialog.py` | 11 | Load external HTML files |
| `DFBU/gui/viewmodel.py` | 10 | Add restore source scanning |
| `DFBU/gui/designer/main_window_complete.ui` | 4, 6, 7, 8 | Spacing, layout restructure, log toolbar, config groups |
| `DFBU/gui/designer/add_dotfile_dialog.ui` | 4 | Spacing fixes |
| `DFBU/gui/designer/recovery_dialog.ui` | 4 | Spacing fixes |
| `DFBU/gui/designer/size_warning_dialog.ui` | 4 | Spacing fixes |

---

## Step 1 — P0-A: Centralized Color Palette & Theme Constants

**Effort:** Low | **Impact:** High (foundation for everything)

Create `DFBU/gui/theme.py` defining all colors, spacing, and typography constants derived from the brand icon palette (`DFBU/resources/icons/dfbu.svg`).

### New file: `DFBU/gui/theme.py`

```python
class DFBUColors:
    """Centralized color palette derived from brand icon."""
    # Primary (from document shape in icon)
    PRIMARY = "#2563EB"
    PRIMARY_DARK = "#1D4ED8"
    PRIMARY_LIGHT = "#3B82F6"
    PRIMARY_SUBTLE = "#EFF6FF"  # 10% opacity equivalent

    # Success (from shield in icon)
    SUCCESS = "#10B981"
    SUCCESS_DARK = "#059669"
    SUCCESS_LIGHT = "#34D399"

    # Semantic
    WARNING = "#F59E0B"
    ALERT = "#F97316"
    CRITICAL = "#EF4444"

    # Neutral scale
    NEUTRAL_50 = "#F8FAFC"
    NEUTRAL_100 = "#F1F5F9"
    NEUTRAL_200 = "#E2E8F0"
    NEUTRAL_300 = "#CBD5E1"
    NEUTRAL_400 = "#94A3B8"
    NEUTRAL_500 = "#64748B"
    NEUTRAL_600 = "#475569"
    NEUTRAL_700 = "#334155"
    NEUTRAL_800 = "#1E293B"
    NEUTRAL_900 = "#0F172A"

    # Semantic aliases
    BACKGROUND = "#FFFFFF"
    SURFACE = NEUTRAL_50
    TEXT_PRIMARY = NEUTRAL_800
    TEXT_SECONDARY = NEUTRAL_500
    TEXT_DISABLED = NEUTRAL_400
    BORDER = NEUTRAL_200
    BORDER_FOCUS = PRIMARY


class DFBUSpacing:
    """4px base unit spacing system."""
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32


class DFBUTypography:
    """Font families and sizes."""
    FONT_FAMILY = "Segoe UI, Ubuntu, Cantarell, sans-serif"
    FONT_MONO = "JetBrains Mono, Fira Code, Consolas, monospace"
    SIZE_CAPTION = 11
    SIZE_BODY = 13
    SIZE_HEADING = 15
    SIZE_TITLE = 18
```

### Modifications

**`DFBU/gui/view.py`** — Replace all hardcoded colors:
- `QColor(0, 150, 0)` → `QColor(DFBUColors.SUCCESS)`
- `QColor(200, 0, 0)` → `QColor(DFBUColors.CRITICAL)`
- `QColor(128, 128, 128)` → `QColor(DFBUColors.TEXT_DISABLED)`

**`DFBU/gui/size_warning_dialog.py`** — Replace `LEVEL_COLORS` dict:
- `"warning": QColor(255, 193, 7)` → `QColor(DFBUColors.WARNING)`
- `"alert": QColor(255, 152, 0)` → `QColor(DFBUColors.ALERT)`
- `"critical": QColor(244, 67, 54)` → `QColor(DFBUColors.CRITICAL)`

### Verification

```bash
pytest DFBU/tests/ -m "not slow" -v
mypy DFBU/gui/theme.py
```

---

## Step 2 — P0-B: Create QSS Theme Stylesheet

**Effort:** Medium | **Impact:** Highest (transforms entire appearance)
**Depends on:** Step 1

### New file: `DFBU/gui/styles/dfbu_light.qss`

Comprehensive stylesheet covering all widget types:

1. **QMainWindow & QWidget** — Base background (#FFFFFF), font-family (system sans-serif stack)
2. **QTabWidget & QTabBar** — Brand blue active indicator bar, hover states, 12px padding, no border on content
3. **QPushButton** — Three variants:
   - Primary: blue bg (#2563EB), white text, hover darkens to #1D4ED8
   - Secondary: white bg, blue border, blue text
   - Danger: red bg (#EF4444) for destructive actions
   - All: border-radius 6px, padding 8px 16px, disabled state at 50% opacity
4. **QTableWidget** — Alternating rows (#F8FAFC / #FFFFFF), header with blue bg and white text, selection highlight with blue 15% opacity, 1px #E2E8F0 gridlines
5. **QLineEdit & QSpinBox** — 1px #E2E8F0 border, 2px blue border on focus, 8px padding, #94A3B8 placeholder
6. **QCheckBox** — Blue indicator when checked, rounded 3px indicator
7. **QProgressBar** — Blue (#2563EB) chunk fill, #E2E8F0 track, 8px height, rounded
8. **QTextEdit (log)** — Dark background (#1E293B), light text (#E2E8F0), monospace font, for terminal feel
9. **QMenuBar & QMenu** — Blue hover highlight, clean separators
10. **QStatusBar** — 1px top border (#E2E8F0), muted text (#64748B)
11. **QGroupBox** — Bold title, 1px #E2E8F0 border, 12px content margins
12. **QScrollBar** — 8px wide, rounded thumb (#CBD5E1), transparent track
13. **QToolTip** — Dark bg (#1E293B), white text, rounded 4px, no border

### New file: `DFBU/gui/theme_loader.py`

```python
from pathlib import Path
from PySide6.QtWidgets import QApplication

def load_theme(app: QApplication, theme_name: str = "dfbu_light") -> bool:
    """Load and apply a QSS theme to the application."""
    qss_path = Path(__file__).parent / "styles" / f"{theme_name}.qss"
    if not qss_path.exists():
        return False
    app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
    return True
```

### Modification: `DFBU/dfbu_gui.py`

Add after `QApplication` creation, before `window.show()`:

```python
from gui.theme_loader import load_theme
load_theme(app)
```

### Verification

```bash
pytest DFBU/tests/ -m gui -v  # GUI tests with theme applied
python DFBU/dfbu_gui.py       # Visual inspection
```

---

## Step 3 — P0-C: Set Application Icon

**Effort:** Trivial | **Impact:** Immediate brand presence

### Modification: `DFBU/dfbu_gui.py`

```python
from PySide6.QtGui import QIcon

icon_path = Path(__file__).parent / "resources" / "icons" / "dfbu.svg"
app.setWindowIcon(QIcon(str(icon_path)))
```

### Modification: `DFBU/gui/view.py` — `_show_about()`

Add icon to about dialog:

```python
from PySide6.QtGui import QPixmap

icon_path = Path(__file__).parent.parent / "resources" / "icons" / "dfbu-256.png"
msg = QMessageBox(self)
msg.setIconPixmap(QPixmap(str(icon_path)).scaled(64, 64))
msg.setWindowTitle(f"About {self.PROJECT_NAME}")
msg.setText(...)
msg.exec()
```

### Verification

```bash
python DFBU/dfbu_gui.py  # Check icon in title bar, taskbar, about dialog
```

---

## Step 4 — P1-A: Fix Spacing & Margins in .ui Files

**Effort:** Medium | **Impact:** High (removes cramped feel)

### Files to modify

All four `.ui` files in `DFBU/gui/designer/`:

**`main_window_complete.ui`:**
- Keep `main_layout` at 0 margins (tab widget fills window edge-to-edge — correct)
- Set `backupTabLayout` margins to 12px all sides
- Set `restoreTabLayout` margins to 12px all sides
- Set `configTabLayout` margins to 12px all sides
- Set all section/group layouts: spacing=8px, margins=12px
- Set button row horizontal layouts: spacing=8px
- Set fileGroupLabelContainer: top/bottom padding 8px

**`add_dotfile_dialog.ui`:**
- Set dialog layout margins to 16px
- Set form layout vertical spacing to 8px
- Set button area top margin to 12px

**`recovery_dialog.ui`:**
- Set dialog layout margins to 16px
- Set section spacing to 12px

**`size_warning_dialog.ui`:**
- Set dialog layout margins to 16px
- Set section spacing to 12px

### Approach

Edit `.ui` XML directly. Search for `<number>0</number>` in margin/spacing properties and replace with appropriate values from the spacing system.

### Verification

```bash
pytest DFBU/tests/ -m gui -v   # Verify QUiLoader still loads correctly
python DFBU/dfbu_gui.py        # Visual inspection
```

---

## Step 5 — P1-B: Replace Success Dialogs with Status Bar Messages

**Effort:** Low | **Impact:** Medium (eliminates dialog fatigue)

### Modification: `DFBU/gui/view.py`

**Convert success confirmations to status bar messages:**

| Method | Current | New |
|--------|---------|-----|
| `_on_add_dotfile()` ~line 1679 | `QMessageBox.information("Dotfile Added")` | `self.status_bar.showMessage("✓ Dotfile added", 3000)` |
| `_on_update_dotfile()` ~line 1734 | `QMessageBox.information("Dotfile Updated")` | `self.status_bar.showMessage("✓ Dotfile updated", 3000)` |
| `_on_remove_dotfile()` ~line 1776 | `QMessageBox.information("Dotfile Removed")` | `self.status_bar.showMessage("✓ Dotfile removed", 3000)` |
| `_on_save_config()` ~line 1574 | `QMessageBox.information("Configuration Saved")` | `self.status_bar.showMessage("✓ Configuration saved", 3000)` |
| `_on_save_dotfile_config()` ~line 1606 | `QMessageBox.information("Configuration Saved")` | `self.status_bar.showMessage("✓ Dotfile config saved", 3000)` |

**Keep as modal dialogs:**
- `_on_start_backup()` confirmation (starts long operation)
- `_on_start_restore()` confirmation (overwrites files)
- `_on_remove_dotfile()` confirmation prompt (destructive — keep the "are you sure?" but remove the "success" message)
- `_on_save_config()` confirmation prompt (keep the "are you sure?" but remove the "success" message)
- All `QMessageBox.critical()` and `QMessageBox.warning()` calls

### Optional Enhancement: Toast Notification Widget

Create `DFBU/gui/toast.py`:

```python
class ToastNotification(QWidget):
    """Floating auto-dismiss notification widget."""
    # Slides in from bottom-right, auto-fades after 3 seconds
    # Colored accent bar: green for success, blue for info, red for error
```

This is optional — status bar messages are the minimum viable improvement.

### Verification

```bash
pytest DFBU/tests/ -v  # Update tests that mock QMessageBox.information
```

---

## Step 6 — P2-A: Backup Tab Layout Redesign

**Effort:** High | **Impact:** High (better information hierarchy)
**Depends on:** Steps 1-4

### Current layout (vertical stack)

```
Filter → Table → CRUD buttons → Options checkboxes → Start Backup → Log
```

### Proposed layout

```
┌─────────────────────────────────────────────────────────┐
│ 🔍 [Filter input________________]           [+ Add]     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Dotfile Table (dominant — 70% of vertical space)       │
│  - Alternating rows with brand colors                   │
│  - Styled header row                                    │
│  - Selection highlight                                  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ [Edit] [Remove] [Toggle] [Save Changes]    Total: 4.2MB│
├─────────────────────────────────────────────────────────┤
│ ▶ Backup Options                                        │
│   ☑ Mirror  ☑ Archive  ☐ Force Full Backup              │
│                                    [▶ Start Backup]     │
└─────────────────────────────────────────────────────────┘
```

### Changes

**`main_window_complete.ui`:**
- Combine filter input + Add button into single horizontal toolbar row
- Set table stretch factor to dominate the tab
- Create compact horizontal action bar below table with Edit/Remove/Toggle/Save + total size label (right-aligned)
- Make Backup Options a collapsible QGroupBox (or always-visible compact strip)
- Style Start Backup as prominent primary button, right-aligned
- Remove operation log from Backup tab (it already exists in Logs tab)

**`view.py`:**
- Update `_find_backup_tab_widgets()` for any renamed/reorganized widgets
- Remove references to backup tab operation_log (if separated)
- Ensure `_on_start_backup()` switches to Logs tab (already does — line 901)

### Verification

```bash
pytest DFBU/tests/ -m gui -v
python DFBU/dfbu_gui.py  # Visual inspection of new layout
```

---

## Step 7 — P2-B: Enhanced Log Tab with Filtering & Color Coding

**Effort:** Medium | **Impact:** Medium

### New method in `DFBU/gui/view.py`

```python
def _append_log(self, message: str, level: str = "info") -> None:
    """Append a color-coded log entry."""
    color_map = {
        "success": DFBUColors.SUCCESS,
        "error": DFBUColors.CRITICAL,
        "warning": DFBUColors.WARNING,
        "skip": DFBUColors.TEXT_DISABLED,
        "info": DFBUColors.TEXT_SECONDARY,
        "header": DFBUColors.PRIMARY,
    }
    color = color_map.get(level, DFBUColors.TEXT_PRIMARY)
    html = f'<span style="color: {color};">{message}</span><br>'
    self.operation_log.moveCursor(QTextCursor.MoveOperation.End)
    self.operation_log.insertHtml(html)
    self.operation_log.ensureCursorVisible()
```

### Replace all log calls

| Current | New |
|---------|-----|
| `self.operation_log.append("✓ ...")` | `self._append_log("✓ ...", "success")` |
| `self.operation_log.append("✗ ...")` | `self._append_log("✗ ...", "error")` |
| `self.operation_log.append("⊘ ...")` | `self._append_log("⊘ ...", "skip")` |
| `self.operation_log.append("=== ... ===")` | `self._append_log("=== ... ===", "header")` |
| `insertPlainText("✓ ...")` | `self._append_log("✓ ...", "success")` |

### Add filter toolbar to Logs tab

**`main_window_complete.ui`:**
- Add horizontal widget above logBox containing:
  - QPushButton "All" (toggle, default active)
  - QPushButton "Info" (toggle)
  - QPushButton "Warnings" (toggle)
  - QPushButton "Errors" (toggle)
  - QSpacerItem (horizontal stretch)
  - QPushButton "Clear Log"
  - QPushButton "Save Log" (move from below)
  - QPushButton "Verify Backup" (move from below)

**`view.py`:**
- Track log entries with their levels in a list
- Filter toggles show/hide entries by reconstructing the visible HTML
- Clear Log button clears the log and the entries list

### Verification

```bash
pytest DFBU/tests/ -v
python DFBU/dfbu_gui.py  # Run a backup, verify colored log output
```

---

## Step 8 — P2-C: Configuration Tab Collapsible Sections

**Effort:** Medium | **Impact:** Medium

### Modification: `main_window_complete.ui`

Replace single form layout with 6 QGroupBox sections inside a QScrollArea:

```
┌─ Backup Paths ───────────────────────────────┐
│ Mirror Directory:  [path__________] [Browse]  │
│ Archive Directory: [path__________] [Browse]  │
└───────────────────────────────────────────────┘
┌─ Backup Modes ───────────────────────────────┐
│ ☑ Mirror backup    ☑ Archive backup           │
│ ☑ Hostname subdir  ☐ Date subdir              │
└───────────────────────────────────────────────┘
┌─ Archive Options ────────────────────────────┐
│ Compression level: [9 ▾]                      │
│ ☑ Rotate archives    Max archives: [5 ▾]     │
└───────────────────────────────────────────────┘
┌─ Pre-Restore Safety ────────────────────────┐
│ ☑ Enable pre-restore backup                   │
│ Max restore backups: [5 ▾]                    │
│ Backup directory: [path__________] [Browse]   │
└───────────────────────────────────────────────┘
┌─ Verification ───────────────────────────────┐
│ ☑ Verify after backup  ☐ Hash verification    │
└───────────────────────────────────────────────┘
┌─ Size Management ────────────────────────────┐
│ ☑ Size check enabled                          │
│ Warning: [10] MB  Alert: [100] MB             │
│ Critical: [1024] MB                           │
└───────────────────────────────────────────────┘
         [Save Configuration] [Reset to Defaults]
```

### Implementation options

**Option A: Standard QGroupBox** — Just visual grouping with styled borders. Simplest, keeps all sections always visible. Relies on QScrollArea for overflow.

**Option B: Collapsible sections** — Custom widget with QToolButton toggle that collapses/expands the group content. More interactive but more code.

**Recommendation: Option A** for initial implementation, upgrade to B later if needed.

### Modification: `view.py`

- Add `_on_reset_defaults()` handler that restores all options to their default values
- Update `_find_config_tab_widgets()` if widget names change
- Wire up Reset to Defaults button

### Verification

```bash
pytest DFBU/tests/ -m gui -v
python DFBU/dfbu_gui.py  # Verify all config options save/load correctly
```

---

## Step 9 — P3-A: Empty States & Onboarding

**Effort:** Low | **Impact:** Low-Medium

### Modification: `main_window_complete.ui`

Wrap the dotfile table area in a `QStackedWidget` with two pages:
- Page 0: Empty state widget (shown when no dotfiles)
- Page 1: Dotfile table + action bar (shown when dotfiles loaded)

### Empty state content

```
        ┌───────────────────────┐
        │      [DFBU Icon]      │
        │                       │
        │  No dotfiles          │
        │  configured yet       │
        │                       │
        │  Click "Add" to       │
        │  create your first    │
        │  entry, or load an    │
        │  existing config.     │
        │                       │
        │     [+ Add Dotfile]   │
        └───────────────────────┘
```

### Modification: `view.py`

- Find QStackedWidget reference
- Switch to page 0 on init and when `dotfile_count == 0`
- Switch to page 1 when `dotfiles_updated` signal fires with count > 0
- Connect the empty state's Add button to `_on_add_dotfile()`

### Verification

```bash
pytest DFBU/tests/ -m gui -v
python DFBU/dfbu_gui.py  # Launch without config, verify empty state
```

---

## Step 10 — P3-B: Restore Tab Enhancement

**Effort:** Medium | **Impact:** Low-Medium

### Modification: `main_window_complete.ui`

Add backup preview section below the source path:

```
┌─ Restore Source ─────────────────────────────┐
│ Path: [________________________] [Browse...] │
└──────────────────────────────────────────────┘
┌─ Backup Preview ─────────────────────────────┐
│ Hostname: devenv                              │
│ Files: 47 entries    Size: 12.4 MB            │
│                                               │
│ ┌────────────────────────────────────────┐   │
│ │  Bash (~/.bashrc) — 4.2 KB            │   │
│ │  Konsole (2 files) — 1.1 KB           │   │
│ │  Firefox (12 files) — 8.1 MB          │   │
│ └────────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
                             [▶ Start Restore]
```

### Modification: `DFBU/gui/viewmodel.py`

Add new method:

```python
def command_scan_restore_source(self, path: Path) -> dict | None:
    """Scan a backup directory and return metadata preview."""
    # Walk the directory, count files, sum sizes
    # Return: hostname, date, file_count, total_size, file_list
```

### Modification: `view.py`

- `_on_browse_restore_source()`: After selecting, trigger scan and populate preview
- Add `_populate_restore_preview(metadata: dict)` method
- Show/hide preview based on valid source

### Verification

```bash
pytest DFBU/tests/ -v  # Test scan with mock directories
python DFBU/dfbu_gui.py  # Browse to real backup, verify preview
```

---

## Step 11 — P3-C: Externalize Help Content

**Effort:** Low | **Impact:** Low

### New files

**`DFBU/resources/help/quick_start.html`:**
- Move content from `HelpDialog.QUICK_START_HTML` class constant

**`DFBU/resources/help/config_reference.html`:**
- Move content from `HelpDialog.CONFIG_REFERENCE_HTML` class constant

### Modification: `DFBU/gui/help_dialog.py`

Replace class constants with file loading:

```python
def _setup_ui(self) -> None:
    help_dir = Path(__file__).parent.parent / "resources" / "help"

    quick_start_browser = QTextBrowser()
    try:
        quick_start_browser.setHtml(
            (help_dir / "quick_start.html").read_text(encoding="utf-8")
        )
    except FileNotFoundError:
        quick_start_browser.setHtml("<p>Help content not available.</p>")
```

### Verification

```bash
pytest DFBU/tests/ -v
python DFBU/dfbu_gui.py  # Open Help dialog, verify content renders
```

---

## Step 12 — P3-D: Polish & Final QA

**Effort:** Low | **Impact:** Required (quality gate)
**Depends on:** All previous steps

### Checklist

- [ ] Grep for remaining hardcoded `QColor` or hex color values — ensure all use `DFBUColors`
- [ ] Test on KDE Plasma desktop
- [ ] Test on GNOME desktop
- [ ] Test on XFCE desktop (if available)
- [ ] Verify all keyboard shortcuts work (Ctrl+B, Ctrl+R, Ctrl+V, F1, Ctrl+Q)
- [ ] Test window resize from 1000x700 minimum to maximized
- [ ] Verify no widgets clip or overflow at minimum size
- [ ] Capture before/after screenshots for documentation
- [ ] Update `CLAUDE.md` with new files (theme.py, styles/, theme_loader.py, toast.py)
- [ ] Update `UI_GENERATION_REPORT.md` if `.ui` structure changed
- [ ] Run full test suite with all markers

### Commands

```bash
pytest DFBU/tests/ -v --cov=DFBU --cov-report=html
mypy DFBU/
python DFBU/dfbu_gui.py  # Full manual walkthrough
```

---

## Brand Color Reference

Derived from `DFBU/resources/icons/dfbu.svg`:

| Color | Hex | Usage |
|-------|-----|-------|
| Primary Blue | `#2563EB` | Buttons, active tabs, links, focus rings |
| Dark Blue | `#1D4ED8` | Hover states, pressed buttons |
| Light Blue | `#3B82F6` | Secondary accents |
| Subtle Blue | `#EFF6FF` | Backgrounds, selections |
| Success Green | `#10B981` | Status indicators, success messages |
| Dark Green | `#059669` | Success hover/pressed states |
| Warning Amber | `#F59E0B` | Warning level indicators |
| Alert Orange | `#F97316` | Alert level indicators |
| Critical Red | `#EF4444` | Error states, critical warnings |
| Slate 50 | `#F8FAFC` | Alternating table rows |
| Slate 200 | `#E2E8F0` | Borders, dividers |
| Slate 500 | `#64748B` | Secondary text |
| Slate 800 | `#1E293B` | Primary text, log background |
