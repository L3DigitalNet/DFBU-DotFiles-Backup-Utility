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

- **Project Structure**: Moved `common_types.py` and `validation.py` to new `core/` subdirectory for better organization
- **Imports**: Updated all import statements to use `from core.common_types` and `from core.validation` patterns
- **Core Package**: Created `core/__init__.py` to expose shared utilities (`DotFileDict`, `OptionsDict`, `ConfigValidator`)

### Deprecated

### Removed

### Fixed

### Security

## [0.4.0] - 2025-11-01

### Added

- **Component Architecture**: Implemented Single Responsibility Principle by splitting DFBUModel into focused components
  - `ConfigManager` class (555 lines): Handles all configuration operations (I/O, TOML parsing, dotfile CRUD, validation)
  - `FileOperations` class (620 lines): Manages all file system operations (path expansion, copying, archives, restore)
  - `BackupOrchestrator` class (420 lines): Coordinates backup/restore operations with progress tracking
  - `StatisticsTracker` class (158 lines): Tracks operation metrics using BackupStatistics dataclass

### Changed

- **DFBUModel Refactoring**: Transformed from monolithic class (1,178 lines) to clean facade pattern (583 lines)
  - 50.5% code reduction (595 lines eliminated)
  - Now coordinates 4 focused components via delegation
  - Added property setters for `config_path`, `mirror_base_dir`, and `archive_base_dir` for backward compatibility
  - Maintains full API compatibility with existing ViewModel
- **Architecture Improvements**:
  - Implemented facade pattern for clean component composition
  - Dependency injection via expand_path callback from FileOperations to ConfigManager
  - Each component now has single, well-defined responsibility
- **Test Suite**: Improved to 277/282 passing (98.2% pass rate), 78% code coverage
- Updated Date Changed header to 2025-11-01

### Fixed

- Test expectations corrected for `validate_dotfile_paths` return signature (exists, is_dir, type_str)
- View signal connection test fixed to properly test signal connections

## [0.3.2] - 2025-11-01

### Added

- KDiff3 configuration paths for development utility support
- Krusader user actions configuration path for enhanced file manager functionality

### Changed

- Import organization improvements with proper ordering
- Enhanced type safety with strict parameter added to zip() calls
- Updated type hints for better code clarity
- Updated Date Changed header to 2025-11-01

### Fixed

- **ConfigValidator.validate_options() - Compression Level**: Fixed validation logic to properly default to 9 for out-of-range values (< 0 or > 9) instead of clamping to range boundaries
- **ConfigValidator.validate_options() - Max Archives**: Fixed validation logic to properly default to 5 for values below 1 instead of clamping to minimum of 1
- **Type Safety in Configuration Validation**: Added try-except blocks to handle invalid type conversions (e.g., string values) gracefully, defaulting to safe values (compression_level=9, max_archives=5)
- Configuration validation now properly handles edge cases: out-of-range integers, invalid types, and missing values

## [0.3.1] - 2025-10-31

### Added

### Changed

- **Documentation Update**: Comprehensive documentation review and standardization
- Updated all file headers to current date (2025-10-31) for documentation maintenance
- Enhanced project documentation organization following repository guidelines
- Standardized inline comments and docstring formatting across all modules
- Updated README.md to maintain minimal, human-readable content per guidelines
- Improved CHANGELOG.md formatting and version tracking accuracy
- Enhanced PROJECT-DOC.md files with current implementation details
- Updated GUI documentation to reflect latest MVVM implementation

### Deprecated

### Removed

### Fixed

- Corrected documentation inconsistencies across project files
- Updated version tracking in pyproject.toml and all module headers

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
