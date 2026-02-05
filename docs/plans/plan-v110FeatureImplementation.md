# DFBU v1.1.0 Feature Implementation Plan

**Date**: February 5, 2026
**Author**: AI Planning Agent
**Status**: Draft

---

## Overview

This plan covers implementing three high-value features for DFBU v1.1.0:

1. **Backup Profiles** - Named presets for different backup configurations
2. **Backup Preview/Dry Run** - Preview files before backup execution
3. **Dashboard/Statistics** - Visual insights into backup history and health

Each feature follows the existing MVVM architecture patterns with full test coverage.

---

## Phase 1: Backup Profiles (2-3 days)

**Goal**: Allow users to create, save, switch between, and manage named backup profiles that store different dotfile selection and option combinations.

### Step 1.1: Define Profile TypedDict and Model

- Add `ProfileDict` to `DFBU/core/common_types.py` with fields: `name`, `description`, `excluded`, `options_overrides`, `created_at`, `modified_at`
- Create `DFBU/gui/profile_manager.py` with `ProfileManager` class following `ConfigManager` pattern
- Implement CRUD operations: `load_profiles()`, `save_profile()`, `delete_profile()`, `get_active_profile()`

### Step 1.2: Add Profile Storage

- Create `DFBU/data/profiles.yaml` for profile persistence
- Add `active_profile` field to `DFBU/data/session.yaml` structure
- Update `SessionDict` in `DFBU/core/common_types.py`

### Step 1.3: Integrate with Model Facade

- Add `ProfileManager` as component in `DFBU/gui/model.py` (follow existing component pattern)
- Expose profile operations through facade: `load_profiles()`, `switch_profile()`, `create_profile()`, `delete_profile()`

### Step 1.4: Create ProfileViewModel Signals

- Add signals to `DFBU/gui/viewmodel.py`: `profile_loaded`, `profile_switched`, `profiles_list_changed`
- Add commands: `command_switch_profile()`, `command_create_profile()`, `command_delete_profile()`
- Wire profile changes to update exclusions and options

### Step 1.5: Design Profile UI in Qt Designer

- Create `DFBU/gui/designer/profile_dialog.ui` for profile editor
- Add profile selector combo box to backup tab in `DFBU/gui/designer/main_window_complete.ui`
- Add "Save as Profile" and "Manage Profiles" buttons

### Step 1.6: Implement View Components

- Create `ProfileDialog` class in `DFBU/gui/profile_dialog.py`
- Add profile selector widget handling in `MainWindow._find_backup_tab_widgets()`
- Connect profile UI signals to ViewModel commands

### Step 1.7: Write Tests

- Create `DFBU/tests/test_profile_manager.py` - unit tests for ProfileManager
- Create `DFBU/tests/test_viewmodel_profiles.py` - signal/command tests
- Add integration test for profile switching workflow

---

## Phase 2: Backup Preview/Dry Run (1-2 days)

**Goal**: Show users exactly what files will be backed up before executing, including size estimation and file status (new, changed, unchanged).

### Step 2.1: Define Preview TypedDict

- Add `PreviewItemDict` to `DFBU/core/common_types.py`: `path`, `size`, `status` (new/changed/unchanged), `reason`
- Add `BackupPreviewDict`: `items`, `total_size`, `new_count`, `changed_count`, `unchanged_count`

### Step 2.2: Create PreviewGenerator Service

- Create `DFBU/gui/preview_generator.py` with `PreviewGenerator` class
- Leverage existing `FileOperations.files_are_identical()` and `calculate_path_size()` methods
- Implement `generate_preview(dotfiles, mirror_dir) -> BackupPreviewDict`

### Step 2.3: Integrate with Model Facade

- Add `PreviewGenerator` to `DFBU/gui/model.py` components
- Add facade method `generate_backup_preview()`

### Step 2.4: Add Preview Worker Thread

- Add `PreviewWorker(QThread)` to `DFBU/gui/config_workers.py` following `SizeAnalysisWorker` pattern
- Emit progress signals during preview generation

### Step 2.5: Create ViewModel Commands

- Add signals to `DFBU/gui/viewmodel.py`: `preview_ready`, `preview_progress`
- Add `command_generate_preview()` method
- Store preview result for display

### Step 2.6: Design Preview Dialog UI

- Create `DFBU/gui/designer/preview_dialog.ui` with tree view, size summary, status legend
- Add "Preview Backup" button to backup tab

### Step 2.7: Implement Preview Dialog

- Create `PreviewDialog` class with tree view population
- Color-code items by status (green=new, yellow=changed, gray=unchanged)
- Add "Proceed with Backup" and "Cancel" buttons

### Step 2.8: Write Tests

- Create `DFBU/tests/test_preview_generator.py` - unit tests
- Add ViewModel signal tests for preview workflow

---

## Phase 3: Dashboard/Statistics View (2-3 days)

**Goal**: Provide a visual dashboard showing backup history, success rates, storage usage trends, and backup health.

### Step 3.1: Define Dashboard TypedDicts

- Add to `DFBU/core/common_types.py`: `BackupHistoryEntry`, `DashboardMetrics`
- Include: `timestamp`, `profile`, `items_backed`, `size`, `duration`, `success`

### Step 3.2: Create BackupHistory Service

- Create `DFBU/gui/backup_history.py` with `BackupHistoryManager`
- Store history in `DFBU/data/backup_history.yaml`
- Implement: `record_backup()`, `get_history()`, `get_metrics()`

### Step 3.3: Integrate History Recording

- Hook into `BackupOrchestrator` completion to record history
- Add `BackupHistoryManager` to `DFBU/gui/model.py` facade

### Step 3.4: Create DashboardViewModel

- Either extend `DFBUViewModel` or create separate `DashboardViewModel`
- Add signals: `metrics_updated`, `history_loaded`
- Calculate derived metrics: success rate, average size, frequency

### Step 3.5: Design Dashboard Tab UI

- Create dashboard widgets in `DFBU/gui/designer/main_window_complete.ui` as new tab
- Include: summary cards, history table, chart placeholders

### Step 3.6: Implement Dashboard View

- Add `_create_dashboard_tab()` and `_find_dashboard_tab_widgets()` to `DFBU/gui/view.py`
- Implement metric card updates
- Implement history table population

### Step 3.7: Write Tests

- Create `DFBU/tests/test_backup_history.py` - unit tests
- Create `DFBU/tests/test_dashboard_viewmodel.py` - ViewModel tests

---

## Implementation Decisions

### Profile Import/Export

**Recommendation**: Include JSON export for sharing profiles between machines. Adds ~0.5 days but significantly increases utility.

### Chart Library Choice

| Option            | Pros                  | Cons                  |
| ----------------- | --------------------- | --------------------- |
| ASCII/text charts | No dependency         | Limited visual appeal |
| matplotlib        | Full charting         | Heavy dependency      |
| pyqtgraph         | Qt-native, performant | Moderate dependency   |

**Recommendation**: Start with simple text-based summaries, upgrade to pyqtgraph if user demand exists.

### Preview Performance

For large dotfile collections, consider:

- Caching file hashes between previews
- Progressive loading with early results
- Optional "quick preview" mode (size-only)

---

## Future Feature Ideas

These features were considered but deferred for future releases:

### High Value

- **Scheduled Backups** - Cron integration, background daemon
- **Differential/Incremental Backups** - Only backup changed files
- **Backup Comparison Tool** - Compare two backup archives

### Medium Value

- **Search & Filter** - Search dotfiles by name, path, tags
- **Import/Export Configurations** - Share setups across machines
- **Backup Notifications** - Desktop/email notifications

### Advanced Features

- **Cloud Backup Integration** - S3, Google Drive, Dropbox
- **Backup Encryption** - GPG encryption for archives
- **Version Control Integration** - Git-tracked backups
- **Multi-Machine Sync** - Sync configs between computers

### UI/UX Improvements

- **Dark Mode / Themes** - Light/dark toggle, custom schemes
- **Keyboard Shortcuts** - Configurable keybindings
- **Template System** - Pre-built backup templates

---

## Testing Strategy

All features follow the existing test patterns:

1. **Unit Tests**: Test each component in isolation
2. **Signal Tests**: Use `qtbot.waitSignal()` for ViewModel signals
3. **Integration Tests**: Test complete workflows
4. **Coverage Target**: 80%+ on new code

---

## Timeline Summary

| Phase | Feature         | Duration | Dependencies       |
| ----- | --------------- | -------- | ------------------ |
| 1     | Backup Profiles | 2-3 days | None               |
| 2     | Backup Preview  | 1-2 days | None               |
| 3     | Dashboard       | 2-3 days | Phase 1 (optional) |

**Total Estimated Time**: 5-8 days

---

_Last Updated: February 5, 2026_
