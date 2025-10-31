# Versioning Guidelines & Implementation

## Overview

This document outlines a relaxed custom versioning approach for the DFBU repository. The system uses a clean MAJOR.HUMAN.MINOR format without development stage extensions and integrates with the `/version-update` prompt command for automated version management.

## Version Format

### Semantic Versioning Standard

- **Format:** `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- **NO** development stage extensions (`.dev`, `.a`, `.b`, `.rc`)
- **Version 1.0.0** indicates that I would consider the software generally complete

### Version Significance

- **MAJOR:** Breaking changes or completion of all major project goals
- **MINOR:** New features, significant improvements, or additions in backward-compatible manner
- **PATCH:** Bug fixes, refactoring, documentation updates, minor improvements
- **NOTE:** Version increments determined by developer discretion and change impact

## Command Usage

### Version Update Commands

- Triggered via `/version-update` prompt commands:
- This should prompt the AI to analyze all relevant project files and update versions accordingly.
- If a version elevation above AI authority is needed then the exact version should be specified following /version-update.
  - Example: /version-update dfbu.py 1.2.3
- The AI should then update all relevant files to reflect the new version
