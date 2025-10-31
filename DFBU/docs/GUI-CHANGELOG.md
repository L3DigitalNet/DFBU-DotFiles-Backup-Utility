# Changelog - Dotfiles Backup Utility GUI

All notable changes to the GUI component of this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Version Format

- **MAJOR**: Feature completeness milestones
- **MINOR**: New functionality additions
- **PATCH**: Bug fixes and code refactoring
- **Development Stages**: `.dev`, `.a` (alpha), `.b` (beta), `.rc` (release candidate)

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.5.3] - 2025-10-31

### Added

### Changed

- **Documentation Update**: Updated all GUI module headers to current date (2025-10-31)
- Enhanced documentation consistency across Model, View, and ViewModel layers
- Updated GUI project documentation version tracking
- Improved MVVM architecture documentation clarity

### Fixed

- Corrected version numbering and date consistency in GUI documentation

## [0.5.2] - 2025-10-30

### Added

- **Automatic Config Backup with Rotation**: Timestamped backups of dfbu-config.toml on every save with automatic rotation
- Created reusable file_backup utility module in common_lib for rotating file backups
- create_rotating_backup() function with configurable max backup count and timestamp format
- Automatic backup directory creation (.dfbu-config.toml.backups) next to config file
- Collision handling for rapid successive backups within same timestamp
- Default retention of 10 config backups with automatic deletion of oldest
- **Incremental Mirror Backup**: File comparison mechanism to skip unchanged files during mirror operations
- files_are_identical() method in Model for efficient file comparison using size and mtime
- skip_identical parameter in copy_file() and copy_directory() methods
- Automatic file comparison during mirror backups to avoid unnecessary copying
- Enhanced item_skipped signal with "File unchanged" reason for skipped identical files

### Changed

- Mirror backup operations now compare files before copying to optimize performance
- File comparison uses size and modification time (within 1-second tolerance) for efficiency
- BackupWorker now tracks and reports skipped files separately from copied files
- Improved backup statistics to distinguish between processed and skipped items
- Enhanced user feedback showing which files were skipped due to being unchanged

### Deprecated

### Removed

### Fixed

### Security

## [0.5.2] - 2025-10-30

### Fixed

- **Critical Performance Issue**: Eliminated multi-second hang when toggling dotfile enabled/disabled status
- Removed unnecessary full filesystem validation (hundreds of I/O operations) on toggle operations
- Replaced blocking QMessageBox confirmation dialog with non-blocking status bar feedback (3-second timeout)
- Implemented `_update_dotfile_table_fast()` method that reuses cached validation data
- Refactored table update logic into `_populate_dotfile_table()` for code reuse
- Removed `dotfiles_updated` signal emission from toggle operation (not needed for metadata-only changes)

### Changed

- Toggle operation now provides feedback via status bar instead of modal dialog
- Status bar message displays for 3 seconds with application name and new state
- Table refresh after toggle uses cached validation data for instant response

## [0.5.1] - 2025-10-30

### Changed

- **Dotfile List Sorting**: Disabled dotfiles now appear at the top of the list for easier management
- Enhanced table sorting logic to prioritize disabled entries (enabled=False before enabled=True)
- Added _get_original_dotfile_index() helper method to maintain correct index mapping after sorting
- Updated all selection-based operations (update, remove, toggle) to use original dotfile indices
- Improved user experience by making disabled dotfiles immediately visible without scrolling

## [0.5.0] - 2025-10-30

### Added

- **Manual Dotfile Enable/Disable Feature**: Users can now disable dotfiles without removing them from configuration
- "Enabled" column in dotfile table with visual indicator (✓ = enabled, ✗ = disabled)
- "Toggle Enabled/Disabled" button for quick status changes
- Enabled checkbox in Add/Update Dotfile dialog for setting initial state
- Automatic filtering of disabled dotfiles during backup operations
- toggle_dotfile_enabled() method in Model for toggling enabled status
- command_toggle_dotfile_enabled() in ViewModel layer
- Persistent storage of enabled status in TOML configuration
- Color-coded enabled status (green for enabled, gray for disabled)
- Confirmation dialog showing new status when toggling dotfiles

### Changed

- DotFileDict TypedDict extended with "enabled" boolean field
- _validate_dotfile() method now handles enabled field with default value True
- save_config() method includes enabled field when writing TOML
- add_dotfile() and update_dotfile() methods accept enabled parameter
- BackupWorker filters out disabled dotfiles (enabled=False) during mirror and archive operations
- Dotfile table expanded from 6 to 7 columns to accommodate enabled status
- Enhanced AddDotfileDialog with enabled checkbox for new and updated entries

## [0.4.0] - 2025-10-30

### Added

- **Interactive Dotfile Management**: Add and remove dotfile entries directly from the GUI
- AddDotfileDialog class with form-based input for new dotfile entries
- Browse button in AddDotfileDialog for file/directory selection
- Add Dotfile and Remove Selected buttons in dotfile list section
- Selection tracking for dotfile table with enable/disable button states
- Confirmation dialog when removing dotfile entries
- command_add_dotfile() and command_remove_dotfile() in ViewModel layer
- add_dotfile() and remove_dotfile() methods in Model layer
- dotfiles_updated signal for reactive UI updates when dotfiles change
- Automatic table refresh when dotfiles are added or removed

### Changed

- Enhanced dotfile list section with management buttons
- Updated MVVM pattern to support dotfile CRUD operations
- Improved user experience with interactive configuration editing
- Version incremented to 0.4.0 for new feature milestone
- Updated all documentation headers to reflect new dotfile management features
- Enhanced Features sections in all module files

## [0.3.1] - 2025-10-30

### Added

- Python version compatibility check with automatic fallback to shutil.copy2 for Python < 3.14
- Proper setter methods (set_mirror_mode, set_archive_mode) in ViewModel for type-safe options modification
- Zero division protection in RestoreWorker progress calculation
- Signal disconnection in worker completion handlers to prevent memory leaks
- Progress bar hiding and button re-enabling on error conditions
- Detailed error messages from load_config with specific failure context
- Individual file stat() error handling in archive rotation to prevent race conditions

### Changed

- Improved load_config return type to tuple[bool, str] for detailed error reporting
- Enhanced checkbox state change handlers to use ViewModel setter methods instead of direct TypedDict modification
- Updated copy_file to use version check before attempting Path.copy()
- Improved archive rotation with robust error handling for file stat operations
- Enhanced error handling UI feedback with proper progress bar state management

### Fixed

- **Critical**: Import ordering in dfbug.py - moved sys.path.insert before import statements
- **Critical**: Checkbox synchronization - connected checkbox signals to update model options
- **Critical**: Memory leak - added signal disconnection when backup/restore operations complete
- **Critical**: Progress bar stuck state - now properly hides and resets on errors
- **Critical**: Python 3.13 compatibility - added shutil.copy2 fallback for Path.copy()
- **High Priority**: Error reporting - load_config now returns specific error messages instead of generic failures
- **High Priority**: Race condition - archive rotation handles individual file stat() failures gracefully
- **High Priority**: Zero division - both BackupWorker and RestoreWorker protect against division by zero in progress calculations
- Type safety - eliminated direct TypedDict modification in favor of proper encapsulation

## [0.3.0] - 2025-10-30

### Added

- Modern desktop GUI application with PySide6 framework
- MVVM architectural pattern with clean separation of concerns
- Tab-based interface for Backup, Restore, and Configuration views
- Worker threads (BackupWorker, RestoreWorker) for non-blocking operations
- Real-time progress tracking with progress bars and operation logs
- Window state persistence using QSettings
- Signal-based reactive data binding between components
- Interactive file selection dialogs for configuration and restore source
- Visual dotfile validation with color-coded status indicators (✓/✗)
- Keyboard shortcuts for common operations (Ctrl+O, Ctrl+B, Ctrl+R, Ctrl+Q)
- Menu bar with File, Operations, and Help menus
- Confirmation dialogs before backup and restore operations

### Changed

- Migrated from CLI to desktop GUI application
- Restructured codebase into MVVM pattern (Model, ViewModel, View)
- Enhanced user experience with visual feedback and progress tracking
- Improved architecture with threaded operations for responsive UI
- Updated version to 0.3.0 for GUI milestone

## [0.2.2] - 2025-10-29

### Added

- FileSystemHelper utility class for eliminating DRY violations across codebase
- TypedDict definitions (DotFileDict, OptionsDict) for type-safe configuration handling
- Comprehensive type hints throughout entire codebase for all functions and classes
- Enhanced inline comments for improved code readability and AI context
- Detailed docstrings for all classes, methods, and functions following repository standards
- Full documentation updates reflecting current implementation state

### Changed

- Consolidated repeated patterns into FileSystemHelper static methods
- Refactored permission checking to use centralized FileSystemHelper.check_readable()
- Improved directory creation with unified FileSystemHelper.create_directory()
- Enhanced path expansion using consistent FileSystemHelper.expand_path()
- Updated all classes to use proper TypedDict types for configuration data
- Streamlined Options and DotFile initialization with validated typed dictionaries
- Improved docstring formatting and consistency across all code elements
- Enhanced MirrorBackup class with FileSystemHelper integration
- Improved ArchiveBackup class with consolidated helper methods
- Updated version to 0.2.2 reflecting code maturity
- Updated all documentation to reflect Linux-only compatibility
- Enhanced README.md with detailed architecture and dependency information
- Improved CHANGELOG.md formatting and version history accuracy

### Removed

- Duplicate code patterns for dry-run prefix formatting
- Redundant path expansion logic across multiple classes
- Repeated permission check patterns replaced with centralized helper
- Duplicate directory creation code eliminated through FileSystemHelper

## [0.2.1.dev1] - 2025-10-28

### Changed

- Updated version to 0.2.1.dev1 for continued development
- Updated documentation date references to reflect current development

## [0.2.0.dev1] - 2025-10-27

### Added

- **Dual-mode operation**: Interactive selection between backup and restore functionality
- **Restore functionality**: Complete implementation for restoring from hostname-based backup directories
- **Mode selection menu**: Interactive CLI menu for choosing backup vs. restore operations
- **Path resolution for restore**: Smart handling of hostname/home/root directory structures during restoration
- **Enhanced interactive workflow**: Separate confirmation prompts for backup and restore operations
- **Global DRY_RUN support**: Configurable dry-run mode for testing operations safely

### Changed

- Updated version to 0.2.0.dev1 for continued development
- Enhanced user workflow with dual-mode operation support
- Improved path handling for both backup and restore operations
- Updated documentation to reflect actual implementation vs. planned features
- Streamlined feature list in header to focus on implemented capabilities

### Fixed

- Corrected documentation to accurately reflect implemented vs. planned functionality
- Updated feature descriptions to match actual code implementation
- Clarified archive functionality status (configuration implemented, creation logic planned)

## [0.1.0.dev1] - 2025-10-27

### Added

- Initial version reset for major restructuring
- TOML configuration system replacing CSV-based configuration
- Options class for centralized backup configuration management
- Enhanced path handling with mirror_dir and archive_dir configuration
- Comprehensive dotfile metadata with category/subcategory/application structure
- Archive destination path support (implementation in progress)

### Changed

- Reset version numbering to align with development milestones
- Migrated from CSV to TOML configuration format using Python's tomllib
- Updated configuration file location to data/dfbu-config.toml
- Improved dotfile validation and path handling
- Enhanced user output with better formatting and color coding
- Updated documentation to reflect TOML configuration system

### Fixed

- Resolved configuration file parsing to use proper TOML format
- Improved path resolution for both home and root directory files
- Enhanced dotfile metadata validation and error reporting

## [0.4.2.dev1] - 2025-10-27 [SUPERSEDED]

### Added

- TOML configuration system replacing CSV-based configuration
- Options class for centralized backup configuration management
- Enhanced path handling with mirror_dir and archive_dir configuration
- Comprehensive dotfile metadata with category/subcategory/application structure
- Archive destination path support (implementation in progress)

### Changed

- Migrated from CSV to TOML configuration format using Python's tomllib
- Updated configuration file location to data/dfbu-config.toml
- Improved dotfile validation and path handling
- Enhanced user output with better formatting and color coding
- Updated documentation to reflect TOML configuration system

### Fixed

- Resolved configuration file parsing to use proper TOML format
- Improved path resolution for both home and root directory files
- Enhanced dotfile metadata validation and error reporting

## [0.4.1.dev1] - 2025-10-20

### Added

- Semantic versioning support with **version** variable
- Standardized changelog tracking

### Changed

- Updated version tracking to use semantic versioning format

## [0.4.0] - 2025-10-19

### Added

- CSV-driven configuration with Category/Subcategory/Application structure
- Hostname-based backup directory organization (~/GitHub/dotfiles/hostname/)
- Separate home and system file backup paths for clear organization
- Python 3.14 Path.copy() with symlink following and metadata preservation
- ANSI color-coded output using custom AnsiColor class from common_lib
- Interactive CLI menu integration with CLIMenu.ynq() for user confirmation
- Automatic directory creation and intelligent overwrite handling
- Comprehensive file existence checking and type detection

### Changed

- Migrated from defensive programming to confident design patterns
- Improved error handling and user feedback
- Enhanced terminal output with colorized status messages

### Fixed

- Resolved path handling issues for both home and system files
- Fixed metadata preservation during file copying operations
