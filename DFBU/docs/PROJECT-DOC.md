# DFBU GUI Project Documentation

**Description:** Comprehensive project documentation for Dotfiles Backup Utility GUI (DFBU GUI). This document provides detailed technical information about the MVVM architecture, implementation details, and development guidelines.

**Author:** Chris Purcell
**Email:** <chris@l3digital.net>
**GitHub:** <https://github.com/L3DigitalNet>
**Version:** 0.9.1
**Date Created:** 10-18-2025
**Date Changed:** 02-01-2026

## Overview

DFBU GUI is a modern desktop application built with Python 3.14+ and PySide6, implementing a clean MVVM (Model-View-ViewModel) architectural pattern for managing Linux system configuration file backups. The application provides an intuitive graphical interface with threaded operations, real-time progress tracking, exclusion-based dotfile selection, incremental mirror backups with file change detection, automatic config backup rotation, and comprehensive error handling.

The Model layer has been refactored (v0.4.0+) to follow SOLID principles, with DFBUModel acting as a facade coordinating four focused components: ConfigManager, FileOperations, BackupOrchestrator, and StatisticsTracker.

For installation and usage instructions, see the main [README.md](../README.md) file.

## Architecture

### MVVM Pattern

The application follows the Model-View-ViewModel architectural pattern:

- **Model**: Business logic and data management (DFBUModel as facade)
- **View**: PySide6 GUI components (MainWindow)
- **ViewModel**: Presentation logic and state management (DFBUViewModel)

### Model Layer Components (v0.4.0+)

The Model layer uses a facade pattern with specialized components:

#### DFBUModel (Facade)

- **Lines**: 737
- **Role**: Coordinates all model components via delegation
- **Components**: ConfigManager, FileOperations, BackupOrchestrator, StatisticsTracker, ErrorHandler, VerificationManager, RestoreBackupManager
- **Properties**: Exposes component state (config_path, options, dotfiles, statistics, etc.)
- **Backward Compatibility**: Full API compatibility maintained via property setters

#### ConfigManager

- **Lines**: 814
- **Responsibilities**:
  - Configuration file I/O (load, save with rotating backups)
  - YAML parsing and serialization (ruamel.yaml)
  - Dotfile CRUD operations (add, update, remove)
  - Configuration validation integration
  - Exclusion-based selection management (session.yaml)

#### FileOperations

- **Lines**: 686
- **Responsibilities**:
  - Path expansion and validation
  - File/directory copying with metadata preservation
  - Archive creation (TAR.GZ compression)
  - Archive rotation and cleanup
  - Restore path reconstruction
  - Metadata-based file comparison

#### BackupOrchestrator

- **Lines**: 549
- **Responsibilities**:
  - Mirror backup coordination
  - Archive backup coordination
  - Restore operation coordination
  - Progress tracking and callbacks
  - Dotfile path validation
  - Statistics integration

#### ErrorHandler (v0.9.0+)

- **Lines**: 443
- **Responsibilities**:
  - Error categorization (PERMISSION, NOT_FOUND, DISK_FULL, etc.)
  - Recovery suggestion generation
  - Retry eligibility determination
  - Integration with RecoveryDialog

#### VerificationManager (v0.8.0+)

- **Lines**: 355
- **Responsibilities**:
  - Backup integrity verification
  - Size/hash comparison
  - Verification report generation
  - Post-backup verification workflow

#### RestoreBackupManager (v0.6.0+)

- **Lines**: 267
- **Responsibilities**:
  - Pre-restore safety backups
  - Timestamped backup directories
  - TOML manifest generation
  - Retention policy enforcement

## External Resources

- **Main README**: [../README.md](../README.md)
- **Repository Guidelines**: [../../../.github/copilot-instructions.md](../../../.github/copilot-instructions.md)
- **Desktop App Guidelines**: [../../../.github/instructions/desktop-application.instructions.md](../../../.github/instructions/desktop-application.instructions.md)
- **Python Documentation**: <https://docs.python.org/3.14/>
- **PySide6 Documentation**: <https://doc.qt.io/qtforpython/>
