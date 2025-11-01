# GUI Refactoring Testing Checklist

## Pre-Testing Setup

- [  ] Ensure PySide6 is installed and up to date
- [  ] Verify the UI file exists at: `DFBU/gui/designer/main_window_complete.ui`
- [  ] Backup current configuration if testing with real data

## Application Launch

- [  ] Application starts without errors
- [  ] Main window displays correctly
- [  ] Window title shows correct version number
- [  ] All three tabs are visible (Backup, Restore, Configuration)

## Backup Tab

### Configuration Section

- [  ] "Browse..." button opens file dialog
- [  ] Selected config path displays in text field
- [  ] "Load Configuration" button works
- [  ] Status bar updates after loading config

### Dotfiles Table

- [  ] Table displays with all 8 columns
- [  ] Columns: Enabled, Status, Category, Subcategory, Application, Type, Size, Path
- [  ] Sorting works on all columns
- [  ] Total size label displays correctly
- [  ] Table selection enables/disables buttons appropriately

### Dotfile Management Buttons

- [  ] "New" button opens Add Dotfile dialog
- [  ] "Update" button (enabled when row selected)
- [  ] "Remove" button (enabled when row selected)
- [  ] "Toggle Active" button (enabled when row selected)
- [  ] "Save Configuration" button works

### Backup Options

- [  ] Mirror checkbox works
- [  ] Archive checkbox works
- [  ] "Start Backup" button initiates backup
- [  ] Progress bar appears during backup
- [  ] Operation log shows backup progress

## Restore Tab

### Source Selection

- [  ] Info label displays correctly
- [  ] "Browse..." button opens directory dialog
- [  ] Selected path displays in text field
- [  ] "Start Restore" button becomes enabled after valid path selected

### Restore Information

- [  ] Information text displays correctly
- [  ] Warning message is visible

### Operation Log

- [  ] Progress label shows status
- [  ] Log text area displays restore operations
- [  ] Progress bar shows during restore

## Configuration Tab

### Backup Paths

- [  ] Mirror directory path field displays
- [  ] Archive directory path field displays
- [  ] Browse buttons for both paths work
- [  ] Directory dialogs open correctly

### Backup Modes

- [  ] Mirror backup checkbox works
- [  ] Archive backup checkbox works

### Directory Structure

- [  ] Hostname subdirectory checkbox works
- [  ] Date subdirectory checkbox works

### Archive Options

- [  ] Compression level spinbox (0-9) works
- [  ] Rotate archives checkbox works
- [  ] Max archives spinbox works
- [  ] Max archives spinbox enables/disables with rotation checkbox

### Save Configuration

- [  ] "Save Configuration" button becomes enabled when changes made
- [  ] Save confirmation dialog appears
- [  ] Configuration saves successfully
- [  ] Success message displays

## Menu Bar

### File Menu

- [  ] "Load Configuration..." (Ctrl+O) works
- [  ] Separator line displays
- [  ] "Exit" (Ctrl+Q) closes application

### Operations Menu

- [  ] "Start Backup" (Ctrl+B) works
- [  ] "Start Restore" (Ctrl+R) works

### Help Menu

- [  ] "About" opens about dialog
- [  ] About dialog shows version, author, contact info

## Progress and Status

- [  ] Status bar displays messages
- [  ] Progress bar appears in status bar during operations
- [  ] Progress bar hides when operations complete
- [  ] Progress percentage updates correctly

## Window Behavior

- [  ] Window can be resized
- [  ] Minimum window size is enforced (1000x700)
- [  ] Window geometry persists between sessions
- [  ] Closing window saves settings

## Error Handling

- [  ] Invalid config file shows error message
- [  ] Missing config file shows warning
- [  ] Invalid restore path shows warning
- [  ] Operation errors display in log

## Integration Tests

- [  ] Load config → Select dotfiles → Backup works end-to-end
- [  ] Browse restore path → Start restore works end-to-end
- [  ] Modify configuration → Save → Reload config preserves changes
- [  ] Add new dotfile → Save → Reload shows new dotfile
- [  ] Toggle dotfile enabled → Save → State persists

## Visual/Layout Tests

- [  ] All labels are readable and aligned
- [  ] Buttons are appropriately sized
- [  ] Text fields expand properly
- [  ] Tables resize with window
- [  ] No overlapping widgets
- [  ] Consistent spacing throughout
- [  ] Tab navigation works correctly

## Performance

- [  ] Application launches quickly
- [  ] UI remains responsive during operations
- [  ] Table sorting is fast
- [  ] No memory leaks after multiple operations

## Notes

- Any failures or issues found:

- Screenshots of visual issues (if any):

- Suggestions for improvements:

## Testing Completed By

- Name: _________________
- Date: _________________
- Version: _________________
- Result: [ ] PASS  [ ] FAIL  [ ] PARTIAL
