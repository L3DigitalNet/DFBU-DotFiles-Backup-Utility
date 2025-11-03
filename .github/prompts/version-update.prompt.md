---
mode: "agent"
description: "Version update and changelog management for PySide6 MVVM applications"
---

# Version Update Prompt

Handle version updates and changelog maintenance for PySide6 MVVM desktop applications.

## Version Format

### Semantic Versioning - MANDATORY
- **FORMAT**: `MAJOR.MINOR.PATCH`
- **TEMPLATE START**: Version `0.1.0` (initial template)
- **NEW PROJECTS**: Start at `0.1.0` when customized
- **VERSION 1.0.0**: First stable release

### Version Significance
- **MAJOR**: Breaking changes, major architecture changes
- **MINOR**: New features, backward-compatible additions
- **PATCH**: Bug fixes, small improvements, documentation updates

## Version Update Process
1. **UPDATE** `__version__` variable in specified Python file
2. **COMPARE** current code with previous version to identify changes
3. **GENERATE** comprehensive changelog entry
4. **UPDATE** CHANGELOG.md in project's `/docs/` folder
5. **UPDATE** Date Changed in file header to current date

## CHANGELOG.md Requirements

### File Location and Structure
- **MUST** store CHANGELOG.md in project's `/docs/` folder
- **MUST** follow standard Keep a Changelog format
- **MUST** include version number, date, and detailed change descriptions

### Change Categories - REQUIRED FORMAT
```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [X.Y.Z] - YYYY-MM-DD
### Added
- New features and functionality

### Changed
- Changes to existing functionality

### Fixed
- Bug fixes and error corrections

### Removed
- Deprecated features that were removed

### Security
- Security-related improvements
```

### Automatic Changelog Generation
- **ANALYZE** code differences between current and previous version
- **IDENTIFY** all changes: new functions, modified behavior, bug fixes
- **CATEGORIZE** changes using standard sections (Added, Changed, Fixed, etc.)
- **WRITE** clear, descriptive change descriptions
- **INCLUDE** affected modules, classes, or functions when relevant

## Code Change Analysis

### Implementation Comparison Method
1. **EXAMINE** current code implementation
2. **COMPARE** with previous version behavior
3. **IDENTIFY** new features, modifications, and removals
4. **ASSESS** impact on functionality and user experience
5. **DOCUMENT** all user-visible changes

### Change Detection Focus
- **NEW** Models, ViewModels, Views, Services
- **MODIFIED** existing MVVM components
- **FIXED** bugs and architectural issues
- **REMOVED** deprecated components or features

## Version Update Process

1. **UPDATE** `__version__` in appropriate file (e.g., `src/__init__.py`)
2. **ANALYZE** changes since last version
3. **GENERATE** changelog entry with categorized changes
4. **UPDATE** CHANGELOG.md with new entry
5. **COMMIT** version change with appropriate message

## Version File Locations

For this template:
- Version string can be in `src/__init__.py` or `pyproject.toml`
- Consider adding `__version__ = "0.1.0"` to `src/__init__.py`

Example:
```python
# src/__init__.py
"""PySide6 MVVM Desktop Application."""

__version__ = "0.1.0"
```

## Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-11-02

### Added
- New ViewModel for user settings management
- Service layer for configuration persistence
- Integration tests for Model-ViewModel interaction

### Changed
- Refactored MainViewModel to use dependency injection
- Updated View signal connections to use type-safe slots

### Fixed
- Memory leak in View cleanup
- Signal connection duplication issue

## [0.1.0] - 2024-11-01

### Added
- Initial MVVM architecture setup
- Example Model, ViewModel, and View
- Basic test suite with pytest-qt
- Project documentation and guidelines
```
- **IMPROVED** performance or code quality
- **CHANGED** configuration or usage patterns

## File Header Updates

### Date Changed Updates - MANDATORY
```python
Date Changed: [MM-DD-YYYY]  # Current date when version updated
```

### Version Variable Updates
- **UPDATE** `__version__ = "X.Y.Z"` in main module
- **MAINTAIN** consistency across all version references
- **ENSURE** version matches changelog entry

## Repository Integration

### Linux Environment Compliance
- **DESIGNED** for Linux environments only
- **NOT COMPATIBLE** with Windows systems
- **USE** Linux-specific paths and commands

### Project Structure Requirements
- **FOLLOW** repository guidelines for version management
- **MAINTAIN** consistent versioning across all projects
- **STORE** changelog in `/docs/` folder structure
- **UPDATE** README.md if version affects usage

## Version 1.0.0 Special Significance

### Pre-1.0.0 Development (Current Standard)
- **FOCUS** on core functionality and clean architecture
- **DEFER** comprehensive error handling until 1.0.0
- **IMPLEMENT** confident design patterns
- **PRIORITIZE** feature development

### 1.0.0 Release Criteria
- **COMPLETE** core functionality
- **IMPLEMENT** comprehensive error handling
- **ESTABLISH** stable API design
- **ACHIEVE** production readiness

Use this prompt for automated version updates triggered by `/version-update` commands, maintaining consistent semantic versioning and comprehensive changelog documentation throughout the development lifecycle.
```
