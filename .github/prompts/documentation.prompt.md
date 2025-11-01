---
description: "Create or update project documentation including headers, docstrings, README.md, PROJECT-DOC.md, and CHANGELOG.md with Linux-only focus"
mode: "agent"
---

# Create or Update Project Documentation

Handle all documentation tasks for ${file} or project.

## Process Flow
1. Analyze the current code in the file or project
2. Update header, docstrings, and inline comments to reflect current implementation and formatting standards
3. Create missing docstrings and inline comments as needed ensuring that they follow repository guidelines
4. Update existing README.md, PROJECT-DOC.md, and CHANGELOG.md to reflect current project state and code changes
5. Create missing documentation files if they do not exist
6. Remove any temporary or outdated documentation files

## General Guidelines
- **MANDATORY**: Do not change any code logic or implementation
- **MANDATORY**: Only create or update documentation elements (headers, docstrings, inline comments, .md files)

## Documentation Organization Rules
1. **README.md Minimalism:**
   - MUST be very basic and natural-sounding
   - NEVER write content that appears AI-generated
   - Humans manually enter most information
   - These are front-facing documents for GitHub visitors
   - Human maintainer retains full control over README.md contents

2. **File Organization:**
   - ALL general documentation goes in project's `/docs/` directory
   - ALL test documentation goes in project's `/tests/` directory
   - Keep .md file creation to absolute minimum
   - Only create .md files when absolutely necessary

3. **Required Documentation Files:**
   - `CHANGELOG.md` - in `/docs/` directory
   - `PROJECT-DOC.md` - in `/docs/` directory
   - Configuration guides - in `/docs/` directory
   - Test documentation - in `/tests/` directory

## Environment Requirements
- **Linux Environment Only**: All documentation must reflect Linux-only compatibility
- **NO Windows references**: Document Linux paths, commands, system requirements only
- **Python 3.14+ Required**: Document latest language features and requirements
- **PySide6 for GUI**: Document usage of PySide6 for any GUI components

## Documentation Standards
### File Headers
- Ensure all files have proper headers following repository standards
- Include shebang and complete docstring format as specified in [copilot-instructions.md](../copilot-instructions.md)
- **Note**: UTF-8 encoding headers are NOT required in Python 3 (UTF-8 is the default)
- Header content must reflect current code implementation
- Update "Date Changed" to current date

### Docstrings
- Follow repository's specified format from [copilot-instructions.md](../copilot-instructions.md)
- Do not specify types in docstrings; rely on type hints instead
- Ensure docstring content reflects current code state

### Inline Comments
- Use for each significant code block for readability and AI autocompletion context
- Place comments at the top of code blocks explaining their purpose, preferably in one line
- Add or update comments for complex logic, Linux-specific implementations, and important decisions

## Specific Documentation Files
- **README.md**: Keep minimal and natural-sounding (located in project root)
- **PROJECT-DOC.md**: Reflect architecture, design patterns, and Linux-specific considerations (located in `/docs/`)
- **CHANGELOG.md**: Maintain version history, changes, and Linux-specific notes (located in `/docs/`)

## Version Control
- Ensure consistent versioning across all documentation files
- Reflect version changes in CHANGELOG.md accurately
- AI has authority to increment by 0.0.1 as needed based on changes made
