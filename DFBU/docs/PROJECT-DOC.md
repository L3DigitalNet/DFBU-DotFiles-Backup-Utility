# DFBU Project Documentation

**Description:** Comprehensive project documentation for Dotfiles Backup Utility (DFBU). This single project documentation file provides detailed information about installation, usage, API reference, and examples for developers and users.

**Author:** Chris Purcell
**Email:** <chris@l3digital.net>
**GitHub:** <https://github.com/L3DigitalNet>
**Version:** 0.3.2
**Date Created:** 10-18-2025
**Date Changed:** 11-01-2025

## Overview

This documentation provides comprehensive information about the Dotfiles Backup Utility, a Linux-only Python 3.14+ application that uses TOML configuration to manage system configuration files with hostname-based directory structure and intelligent path handling. The application leverages Python's standard library exclusively with custom utility classes for clean code organization.

## Key Features

- **TOML Configuration**: Flexible dotfile management via `data/dfbu-config.toml` with comprehensive validation
- **Dual-Mode Operation**: Interactive backup and restore functionality with dedicated CLIHandler class
- **Hostname-based Structure**: Organized backups by machine hostname managed by PathAssembler utility
- **Python 3.14 Path.copy()**: Enhanced file copying with metadata preservation and symlink following
- **ANSI Color Output**: Color-coded terminal output using embedded utility classes
- **Interactive CLI**: Fully separated UI concerns via CLIHandler with interactive menu integration
- **Robust Validation**: ConfigValidator class with comprehensive type checking and range validation
- **Operation Classes**: MirrorBackup and ArchiveBackup classes for clean separation of concerns
- **Command-line Arguments**: Support for `--dry-run` and `--force` flags via argparse
- **Archive Support**: Compressed TAR.GZ archive creation with rotation and retention policies

## Quick Start

```bash
# Navigate to the project directory
cd Python/projects/DFBU

# Run the interactive backup utility
python3 dfbu.py
```

## Documentation Sections

- **Installation**: See main [README.md](../README.md#installation)
- **Configuration**: TOML file setup and format specification
- **Usage**: Interactive backup process and features
- **Architecture**: Class structure and implementation details
- **Error Handling**: Confident design patterns and user feedback

## External Resources

- **Main Documentation**: [README.md](../README.md)
- **Repository Guidelines**: [../../.github/copilot-instructions.md](../../.github/copilot-instructions.md)
- **CLI Tool Guidelines**: [../../.github/instructions/cli-tool.instructions.md](../../.github/instructions/cli-tool.instructions.md)

---

For detailed installation, configuration, and usage information, please refer to the main [README.md](../README.md) file.
