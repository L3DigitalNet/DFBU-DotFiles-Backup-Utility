# Changelog

All notable changes to the Common Library project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **file_backup module**: Reusable utility for rotating file backups
- create_rotating_backup() function with timestamped backup creation and automatic rotation
- rotate_old_backups() function for maintaining maximum backup count
- get_backup_files() function for discovering and sorting backup files by age
- Configurable maximum backup count (default: 10)
- Custom timestamp format support (default: ISO 8601 compatible YYYYMMDD_HHMMSS)
- Automatic backup directory creation
- Collision handling for rapid successive backups within same timestamp
- Comprehensive pytest test suite with 18 tests covering all functionality
- Integration tests for full rotation workflow scenarios

## [0.2.0] - 2025-10-29

### Changed

- Updated version from 0.2.0.dev1 to 0.2.0 (stable release)
- Enhanced inline documentation with comprehensive comments for all significant code blocks
- Improved docstring format compliance following repository standards
- Updated README.md and PROJECT-DOC.md to reflect Linux-only environment requirements
- Enhanced CLIMenu.run() method with complete implementation and error handling

### Added

- Comprehensive inline comments throughout all classes for better readability and AI context
- Detailed PROJECT-DOC.md with installation, usage, API reference, and troubleshooting sections
- Linux-specific installation and configuration instructions
- Advanced usage examples for all classes with real-world scenarios
- Comprehensive API documentation with method signatures and parameters
- Troubleshooting guide for common Linux terminal and ANSI color issues
- Contributing guidelines following repository standards
- Enhanced documentation structure for better maintainability

### Fixed

- Corrected version inconsistencies between README.md and cust_class.py
- Fixed CLIMenu.run() method placeholder implementation with full functionality
- Improved error handling in CLIMenu with proper user input validation
- Enhanced comment formatting for better code readability

## [0.2.0.dev1] - 2025-10-27

### Changed

- Incremented version from 0.1.0.dev1 to 0.2.0.dev1 in cust_class.py
- Updated version information in file header and **version** variable
- Enhanced PerfMon class with comprehensive statistical analysis capabilities
- Improved PerfMon logging with hostname-specific log files and automatic directory detection

### Added

- PerfMon class comprehensive performance monitoring with rolling averages
- Statistical analysis with configurable rolling window sizes (5, 10, 20, 50 calls)
- Automatic function name detection using inspect module
- Color-coded terminal output for performance reporting
- Log file corruption resistance with error handling
- Custom log entry methods (log_raw_line, log_separator, log_section_header)
- Hostname identification for multi-system logging environments
- Created CHANGELOG.md to track version changes and project evolution

### Removed

- CursesCLIMenu class (was not implemented in actual code)
- Unused imports and dependencies

## [0.1.0.dev1] - 2025-10-18

### Initial Release

- Initial release of custom classes library
- AnsiColor class for terminal text formatting and styling with properties
- CLIMenu class for simple interactive command-line menus with y/n/q prompts
- Basic PerfMon class for performance monitoring functionality
- Cross-platform compatibility for Linux environments
- Type hints and comprehensive documentation following PEP standards
- Minimal dependencies using Python standard library only

### Features

- ANSI color support with foreground/background colors and styling
- Interactive CLI menu systems with numbered selections
- Comprehensive performance monitoring with statistical analysis and logging
- Terminal-based user interface utilities
