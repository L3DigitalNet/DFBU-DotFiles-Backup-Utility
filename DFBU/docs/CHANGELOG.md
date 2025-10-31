# Changelog - Dotfiles Backup Utility

All notable changes to this project will be documented in this file.

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

## [0.3.0] - 2025-10-30

### Added

- **PathAssembler utility class**: Centralized path construction logic for backup destinations
- **ConfigValidator utility class**: Robust TOML configuration validation with type and range checking
- **MirrorBackup operation class**: Dedicated class for mirror backup operations encapsulation
- **ArchiveBackup operation class**: Dedicated class for archive creation and rotation operations
- **CLIHandler utility class**: Complete separation of CLI interaction from business logic
- Comprehensive validation for compression levels (0-9) and archive counts (>= 1)
- Type-safe configuration validation with sensible defaults for missing fields
- Dedicated methods for file and directory processing in backup operations

### Changed

- **Major Architecture Refactoring**: Implemented 4 key architecture improvements for better maintainability
- Separated CLI interaction from business logic using CLIHandler pattern
- Extracted path assembly logic to dedicated PathAssembler utility (~100 lines of duplication removed)
- Refactored backup operations into dedicated MirrorBackup and ArchiveBackup classes
- Enhanced configuration validation with ConfigValidator for robust error prevention
- Updated DotFile class to use PathAssembler for destination path construction
- Simplified Options class initialization with pre-validated configuration data
- All legacy functions now delegate to appropriate utility classes
- Improved code organization with clear separation of concerns
- Enhanced testability through isolated, focused classes
- Updated file header to reflect architecture improvements and new features
- Updated Date Changed to 2025-10-30

### Removed

- Duplicate path assembly methods (_assemble_mirror_dest_path, _assemble_archive_dest_path) from DotFile
- Redundant validation logic replaced with centralized ConfigValidator
- ~300+ lines of duplicated/redundant code through consolidation

### Fixed

- Inconsistent path construction logic now unified in PathAssembler
- Configuration validation gaps addressed with comprehensive ConfigValidator

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
