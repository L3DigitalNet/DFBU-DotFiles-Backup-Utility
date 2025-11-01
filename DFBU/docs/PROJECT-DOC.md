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

**Architecture Philosophy**: The codebase follows a clean, confident design approach with minimal defensive programming. Path validation occurs at architectural boundaries, allowing core business logic to execute confidently without scattered error checks. This version-aware approach (pre-v1.0.0) focuses on core functionality and clean architecture, deferring comprehensive error handling until the v1.0.0 release.

## Key Features

- **TOML Configuration**: Flexible dotfile management via `data/dfbu-config.toml` with comprehensive validation
- **Dual-Mode Operation**: Interactive backup and restore functionality with dedicated CLIHandler class
- **Hostname-based Structure**: Organized backups by machine hostname managed by PathAssembler utility
- **Python 3.14 Path.copy()**: Enhanced file copying with metadata preservation and symlink following
- **ANSI Color Output**: Color-coded terminal output using embedded utility classes
- **Interactive CLI**: Fully separated UI concerns via CLIHandler with interactive menu integration
- **Robust Validation**: ConfigValidator class with comprehensive type checking and range validation at architectural boundaries
- **Operation Classes**: MirrorBackup and ArchiveBackup classes for clean separation of concerns
- **Command-line Arguments**: Support for `--dry-run` and `--force` flags via argparse
- **Archive Support**: Compressed TAR.GZ archive creation with rotation and retention policies
- **Confident Code Design**: Minimal defensive programming with validation at boundaries, clean execution paths in core logic
- **Simplified Return Types**: Pythonic APIs using None to indicate failure rather than redundant tuple returns

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
- **Architectural Patterns**: Confident design approach and validation boundaries
- **Error Handling**: Version-aware error handling strategy (pre-v1.0.0 vs. post-v1.0.0)

## Architectural Patterns (v0.3.2+)

### Confident Code Design

The codebase follows a **confident design philosophy** that minimizes defensive programming:

- **Validation at Boundaries**: Path validation and type checking occur at architectural boundaries (ViewModel, configuration loading)
- **Clean Execution Paths**: Core business logic executes confidently without scattered None checks or "just in case" conditionals
- **Pythonic Return Types**: Methods return `Path | None` instead of `tuple[Path | None, bool]` - None indicates failure
- **Trust Architectural Guarantees**: Once data passes validation boundaries, core methods trust the validity of inputs

### Examples

**Before (Defensive)**:

```python
def copy_file(src: Path, dest: Path) -> tuple[Path | None, bool]:
    if not self.check_readable(src):  # Defensive check
        return None, False
    try:
        # ... copy logic
        return dest, True
    except Exception:
        return dest, False
```

**After (Confident)**:

```python
def copy_file(src: Path, dest: Path) -> bool:
    # Assumes src is validated at boundary (ViewModel)
    src.copy(dest, follow_symlinks=True, preserve_metadata=True)
    return True
```

### Version-Aware Error Handling

- **Pre-v1.0.0 (Current)**: Focus on clean architecture and core functionality; minimal error handling
- **Post-v1.0.0 (Planned)**: Comprehensive error handling with proper logging and recovery strategies

## External Resources

- **Main Documentation**: [README.md](../README.md)
- **Repository Guidelines**: [../../.github/copilot-instructions.md](../../.github/copilot-instructions.md)
- **CLI Tool Guidelines**: [../../.github/instructions/cli-tool.instructions.md](../../.github/instructions/cli-tool.instructions.md)

---

For detailed installation, configuration, and usage information, please refer to the main [README.md](../README.md) file.
