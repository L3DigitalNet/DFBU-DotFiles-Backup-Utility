---
description: "Create or update project documentation including headers, docstrings, README.md, PROJECT-DOC.md, and CHANGELOG.md with Linux-only focus"
mode: "agent"
---

# Create or Update Project Documentation

Handle all documentation tasks for ${file} or project.

## Basic Process Flow
1. Analyze the current code in the file or project
2. Update header, docstrings, and inline comments to reflect current implementation and formatting standards
3. Create missing docstrings and inline comments as needed ensuring that they follow repository guidelines
4. Update existing README.md, PROJECT-DOC.md, and CHANGELOG.md to reflect current project state and code changes
5. Create missing documentation files if they do not exist
6. Remove any temporary or outdated documentation files (such as change summaries not in CHANGELOG.md, old README versions, etc., testing notes, etc.)

## General Guidelines
- **MANDATORY**: Do not change any code logic or implementation
- **MANDATORY**: Only create or update documentation elements (headers, docstrings, inline comments, .md files)

## CRITICAL: Linux Environment Only
- **IMPORTANT**: All documentation must reflect **Linux-only compatibility**
- **NO Windows references** - document Linux paths, commands, system requirements only
- **Python 3.14+ REQUIRED**: Document latest language features and requirements
- **PySide6 for GUI**: Document usage of PySide6 for any GUI components

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
- **IMPORTANT**: Only create/update README.md, PROJECT-DOC.md, CHANGELOG.md as needed.

## Project Documentation
- **README.md**: Create or update comprehensive README.md with project directory structure, installation, usage, examples for Linux.
- **PROJECT-DOC.md**: Ensure PROJECT-DOC.md reflects architecture, design patterns, and Linux-specific considerations.
- **CHANGELOG.md**: Maintain CHANGELOG.md with version history, changes, and Linux-specific notes.
- Follow [repository guidelines](../copilot-instructions.md) for documentation standards.

## Version Control
- Ensure consistent versioning across all documentation files.
- Reflect version changes in CHANGELOG.md accurately.
- AI has authority to increment by 0.0.1 as needed based on changes made.
