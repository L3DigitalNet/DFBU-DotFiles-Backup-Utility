# DFBU GUI - Path Configuration Feature

## Overview

The DFBU GUI now includes the ability to update the mirror source directory and archive source directory directly from the Configuration tab. These paths are automatically saved to the configuration file.

## How to Use

### 1. Load Configuration

- Open DFBU GUI
- Click "File" → "Load Configuration..." or use the Browse button on the Backup tab
- Select your `dfbu-config.toml` file
- The current paths will be displayed in the Configuration tab

### 2. Update Paths

Navigate to the **Configuration** tab. You'll see two path settings:

#### Mirror Directory

- **Location**: Under "Backup Paths" section
- **Purpose**: Destination for uncompressed mirror backups
- **Current Value**: Displayed in the "Mirror Directory" field
- **To Update**:
  - Click the "Browse..." button next to the Mirror Directory field
  - Select a new directory
  - The path will be updated in the text field

#### Archive Directory

- **Location**: Under "Backup Paths" section
- **Purpose**: Destination for compressed archive backups
- **Current Value**: Displayed in the "Archive Directory" field
- **To Update**:
  - Click the "Browse..." button next to the Archive Directory field
  - Select a new directory
  - The path will be updated in the text field

### 3. Save Changes

- After updating the paths, click the **"Save Configuration"** button at the bottom
- A confirmation dialog will appear
- Click "Yes" to save the changes
- The paths will be written to the `dfbu-config.toml` file under the `[paths]` section

### 4. Verify Changes

You can verify the changes by:

1. Checking the status bar message: "Configuration saved successfully"
2. Reloading the configuration file to see the updated paths
3. Opening the `dfbu-config.toml` file in a text editor

## Configuration File Format

The paths are saved in the TOML configuration file as:

```toml
[paths]
mirror_dir = "~/GitHub/dotfiles/"
archive_dir = "~/pCloudDrive/Backups/dotfiles/"
```

## Notes

- Paths support the `~` home directory shorthand
- Paths can be absolute (e.g., `/home/user/backups/`) or relative to home (e.g., `~/backups/`)
- The directories don't need to exist beforehand; they will be created during backup operations
- Changes take effect immediately after saving - no need to restart the application
- The backup operations on the Backup tab will use the updated paths

## Technical Details

### Architecture

This feature follows the MVVM (Model-View-ViewModel) pattern:

- **Model** (`model.py`):
  - `update_path(path_type, value)` - Updates the internal path variables
  - `save_config()` - Writes configuration to TOML file

- **ViewModel** (`viewmodel.py`):
  - `command_update_path(path_type, value)` - Mediates path updates
  - `command_save_config()` - Triggers configuration save

- **View** (`view.py`):
  - Line edits for displaying/editing paths
  - Browse buttons for directory selection
  - Save button for persisting changes
  - Signal handlers for UI events

### Path Types

- `"mirror_dir"` - Mirror backup destination directory
- `"archive_dir"` - Archive backup destination directory
