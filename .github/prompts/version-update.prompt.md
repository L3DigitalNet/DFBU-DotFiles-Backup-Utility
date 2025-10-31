---
mode: "agent"
description: "Version update and changelog management using MAJOR.MINOR.PATCH system"
---

# Version Update Prompt

Handle version updates and changelog maintenance using the simplified MAJOR.MINOR.PATCH versioning system.

## Command Usage

This prompt responds to `/version-update` commands in two formats:

### Format 1: Specific Version

## Version Format Requirements

### Semantic Versioning - MANDATORY
- **MUST** follow format: `MAJOR.MINOR.PATCH`
- **NO** development stage extensions (.dev, .a, .b, .rc)
- **NEW** projects start at version `0.0.1`
- **VERSION** 1.0.0 indicates first full release

### Version Significance
- **MAJOR:** Breaking changes or major feature milestones
- **MINOR:** New functionality in backward-compatible manner
- **PATCH:** Bug fixes and small improvements
- **NOTE:** MINOR and PATCH meanings determined by developer discretion

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
- **NEW** functions, classes, and modules
- **MODIFIED** existing functionality or behavior
- **FIXED** bugs and error conditions
- **REMOVED** deprecated features
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
