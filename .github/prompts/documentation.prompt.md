---
description: "Create or update project documentation including headers, docstrings, README.md, PROJECT-DOC.md, and CHANGELOG.md with Linux-only focus"
mode: "agent"
---

# Create or Update Project Documentation

Handle all documentation tasks for the project.

## Basic Process Flow
1. Analyze the current code in the file or project
2. Update header, docstrings, and inline comments to reflect current implementation and formatting standards
3. Create missing docstrings and inline comments as needed ensuring that they follow repository guidelines
4. Update existing README.md, PROJECT-DOC.md, and CHANGELOG.md to reflect current project state and code changes
5. Create missing documentation files if they do not exist

## General Guidelines
- **MANDATORY**: Do not change any code logic or implementation
- **MANDATORY**: Only create or update documentation elements (headers, docstrings, inline comments, .md files)

## CRITICAL: Linux Environment Only
- **IMPORTANT**: All documentation must reflect **Linux-only compatibility**
- **NO Windows references** - document Linux paths, commands, system requirements only
- **Python 3.14+ REQUIRED**: Document latest language features and requirements

## File Header Format Compliance
Ensure all files have proper headers following repository standards with shebang, encoding, and complete docstring format as specified in [copilot-instructions.md](../copilot-instructions.md).
- Ensure header content reflects current code implementation.
- Update "Date Changed" to current date.

## Docstring Format Compliance
- Ensure all docstrings follow the repository's specified format as outlined in [copilot-instructions.md](../copilot-instructions.md).
- Do not specify types in docstrings; rely on type hints instead.
- Ensure docstring content reflects current code state.

## Inline Documentation
- Inline comments should be used for each significant code block for readability and AI autocompletion context.
- The comments should be at the top of the code block and briefly explain its purpose, preferably in one line.
- Add or update inline comments for complex logic, Linux-specific implementations, and important decisions.

## Repository Integration
- Follow [repository guidelines](../copilot-instructions.md) for documentation standards
- Ensure documentation reflects clean, confident design patterns

## MINIMIZE .md File Creation
- **IMPORTANT**: Only create/update README.md, PROJECT-DOC.md, CHANGELOG.md as needed. The exception is for auto-generated API docs in library folders (common_lib/docs/).

## Project Documentation

### General Documentation Files

- **README.md**: Create or update comprehensive README.md with project directory structure, installation, usage, etc.
- **CHANGELOG.md**: Maintain CHANGELOG.md with version history, changes, and Linux-specific notes.

### Project Documentation (Big Picture) -> Star-Trek-Retro-Remake/docs/*.md

Create or update the following documentation files in the `docs/` directory:

- **ARCHITECTURE.md**: Detailed architecture document covering system design, patterns used, and module interactions.
- **CALL_CHAIN_FLOW.md**: Contains visual flow charts showing how the game's components interact, where to implement specific features, and the execution flow from startup to gameplay.
- **DOCUMENTATION_STANDARDS.md**: This document defines the documentation standards for the Star Trek Retro Remake project, establishing clear rules for where documentation should be located and what it should contain.
- **ARCHITECTURE.md**: Detailed architecture document covering system design, patterns used, and module interactions.
- **PYTHON_FILE_REFERENCE.md**: This document provides a clear reference for the purpose of each Python file in the Star Trek Retro Remake project and indicates where to add specific types of code.
- **VERSIONING_GUIDELINES.md**: This document outlines the simplified versioning approach for the Python repository. The new system uses a clean MAJOR.MINOR.PATCH format without development stage extensions and integrates with the `/version-update` prompt command for automated version management.
- **QTDESIGNER_WORKFLOW.md**: The Star Trek Retro Remake project uses Qt Designer for UI design and PySide6 for runtime UI management. This document describes the workflow for designing, compiling, and using UI files.

### Component Documentation (File-Level) -> Star-Trek-Retro-Remake/STRR/

- Create or update `_doc.md` files for each *.py file in the STRR/ directory (recursively).
- Each `_doc.md` file should provide comprehensive documentation for its corresponding Python module, including purpose, architecture, usage examples, and integration points.

### Testing Documentation

- It is not necessary to create separate documentation files for test modules.
- If there are existing test documentation files they should be relocated to the /tests/ directory.

### Other Documentation

- Create or update one README.md file for each of the following directories:
 - /backup/ and subdirectories
 - /scripts/ and subdirectories
- This README.md should describe the purpose of each file in the respective directory, its purpose, and relation to the overall project.