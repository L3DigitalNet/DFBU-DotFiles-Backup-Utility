# In-App Documentation Design

**Date**: 2026-02-01
**Status**: Approved
**Scope**: Add tooltips to all configuration controls and create a central help dialog accessible from the Help menu.

## Overview

DFBU currently has sparse in-app documentation. This design adds:
1. Concise tooltips for all configuration controls
2. A tabbed help dialog with Quick Start and Configuration Reference sections

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Tooltip verbosity | Concise (one sentence) | More usable than detailed text; doesn't overwhelm |
| Help format | In-app tabbed dialog | Native feel, keeps users in the app |
| Help sections | Minimal (Quick Start + Config Reference) | Focused on essentials users actually need |
| Menu access | New "User Guide" action (F1) | Clear separation from About dialog |

## 1. Tooltip System

### Architecture

Create a centralized `TooltipManager` class that:
- Stores all tooltip text in a dictionary keyed by widget object name
- Applies tooltips programmatically after UI load
- Includes an `enabled` property for future "disable tooltips" setting

**File**: `DFBU/gui/tooltip_manager.py`

### Tooltip Definitions

#### Backup Tab
| Widget | Tooltip |
|--------|---------|
| `filterLineEdit` | "Filter the file list by application name, tags, or path" |
| `fileGroupAddFileButton` | "Add a new dotfile entry to the configuration" |
| `fileGroupUpdateFileButton` | "Edit the selected dotfile entry" |
| `fileGroupRemoveFileButton` | "Remove the selected dotfile from the configuration" |
| `fileGroupToggleEnabledButton` | "Include or exclude selected files from backup operations" |
| `fileGroupSaveFilesButton` | *(existing)* "Save enable/disable changes to the configuration file" |
| `mirrorCheckbox` | "Copy files to an uncompressed directory preserving folder structure" |
| `archiveCheckbox` | "Create a compressed archive of all selected files" |
| `forceBackupCheckbox` | *(existing)* "Copy all files even if unchanged" |
| `startBackupButton` | *(existing)* "Start backup operation" |

#### Restore Tab
| Widget | Tooltip |
|--------|---------|
| `restoreSourceEdit` | "Path to the backup directory containing your hostname folder" |
| `restoreSourceBrowseButton` | "Browse for a backup directory to restore from" |
| `restoreSourceButton` | "Restore files from the selected backup to their original locations" |

#### Configuration Tab
| Widget | Tooltip |
|--------|---------|
| `config_mirror_path_edit` | "Directory where uncompressed mirror backups are stored" |
| `browse_mirror_btn` | "Browse for a mirror backup directory" |
| `configArchivePathEdit` | "Directory where compressed archive backups are stored" |
| `browseArchiveButton` | "Browse for an archive backup directory" |
| `config_mirror_checkbox` | "Enable copying files to the mirror directory during backup" |
| `config_archive_checkbox` | "Enable creating compressed archives during backup" |
| `config_hostname_checkbox` | "Create a subdirectory named after this computer's hostname" |
| `config_date_checkbox` | "Create a subdirectory with today's date for each backup" |
| `config_compression_spinbox` | *(existing)* "0 = no compression, 9 = maximum compression" |
| `config_rotate_checkbox` | "Automatically delete oldest archives when the limit is reached" |
| `config_max_archives_spinbox` | *(existing)* "Maximum number of archives to keep" |
| `config_pre_restore_checkbox` | *(existing)* "Backup existing files before restore operations" |
| `config_max_restore_spinbox` | *(existing)* "Maximum number of pre-restore backups to keep" |
| `config_restore_path_edit` | *(existing)* "Directory to store pre-restore backups" |
| `browse_restore_btn` | "Browse for a pre-restore backup directory" |
| `saveConfigButton` | "Save all configuration changes to settings.yaml" |

#### Logs Tab
| Widget | Tooltip |
|--------|---------|
| `verifyBackupButton` | *(existing)* "Verify integrity of the last backup operation" |
| `pushButton` (Save Log) | "Save the current log output to a file" |

## 2. Help Dialog

### Architecture

Create a `HelpDialog` class as a `QDialog` subclass with a `QTabWidget`.

**File**: `DFBU/gui/help_dialog.py`

### Dialog Properties

- **Title**: "DFBU User Guide"
- **Size**: 600x500 (default), resizable
- **Modality**: Application modal
- **Shortcut**: F1

### Tab 1: Quick Start

```
DFBU - DotFiles Backup Utility

DFBU backs up your Linux configuration files (dotfiles) to keep them
safe and portable across machines.

BACKING UP FILES
1. On the Backup tab, check the files you want to include
2. Choose Mirror (uncompressed) and/or Archive (compressed) options
3. Click "Start Backup"

Your files are copied to the configured backup directories, organized
by hostname.

RESTORING FILES
1. Go to the Restore tab
2. Click "Browse..." and select your backup directory
   (the folder containing your hostname subdirectory)
3. Click "Start Restore"

Warning: Restore overwrites existing files at their original locations.

WHERE ARE MY BACKUPS?
View and change backup locations on the Configuration tab:
- Mirror Directory: Uncompressed copies preserving folder structure
- Archive Directory: Compressed .tar.gz archives
```

### Tab 2: Configuration Reference

Organized by section headers with each setting showing name, description, and default value.

**Sections**:
- Backup Paths
- Backup Modes
- Directory Structure
- Archive Options
- Pre-Restore Safety

Content rendered as HTML in a `QTextBrowser` widget for rich formatting.

## 3. Menu Integration

### UI Changes (`main_window_complete.ui`)

Add new action:
```xml
<action name="actionUserGuide">
  <property name="text">
    <string>&amp;User Guide</string>
  </property>
  <property name="shortcut">
    <string>F1</string>
  </property>
</action>
```

Update menuHelp:
```xml
<widget class="QMenu" name="menuHelp">
  <property name="title">
    <string>&amp;Help</string>
  </property>
  <addaction name="actionUserGuide"/>
  <addaction name="separator"/>
  <addaction name="actionAbout"/>
</widget>
```

### View Layer Wiring (`DFBU/gui/view.py`)

```python
from DFBU.gui.tooltip_manager import TooltipManager
from DFBU.gui.help_dialog import HelpDialog

class MainWindow(QMainWindow):
    def __init__(self, ...):
        # ... existing init code ...

        # Apply tooltips
        self._tooltip_manager = TooltipManager()
        self._tooltip_manager.apply_tooltips(self)

        # Connect help menu
        self.actionUserGuide.triggered.connect(self._show_help_dialog)

    def _show_help_dialog(self) -> None:
        dialog = HelpDialog(self)
        dialog.exec()
```

## File Summary

| File | Change |
|------|--------|
| `DFBU/gui/tooltip_manager.py` | **New** — TooltipManager class with tooltip definitions |
| `DFBU/gui/help_dialog.py` | **New** — HelpDialog class with Quick Start and Config Reference |
| `DFBU/gui/designer/main_window_complete.ui` | Add actionUserGuide, update menuHelp |
| `DFBU/gui/view.py` | Import and wire TooltipManager + HelpDialog |

## Future Extensibility

- **Disable tooltips**: Add setting to `settings.yaml`, check `TooltipManager.enabled` before applying
- **Contextual help**: `HelpDialog` could accept `default_tab` parameter to open relevant section
- **Extended content**: HTML format allows easy updates without UI changes
