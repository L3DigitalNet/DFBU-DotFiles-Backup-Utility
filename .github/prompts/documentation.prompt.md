---
description: "Create or update project documentation including docstrings, README, and code comments for PySide6 MVVM applications"
mode: "agent"
---

# Create or Update Project Documentation

Handle all documentation tasks for the PySide6 MVVM template project.

## Basic Process Flow
1. Analyze the current code in the file or project
2. Update docstrings and inline comments to reflect current implementation
3. Ensure documentation follows repository guidelines
4. Update README.md and other markdown files as needed
5. Verify documentation reflects MVVM architecture

## General Guidelines
- **MANDATORY**: Do not change any code logic or implementation
- **MANDATORY**: Only create or update documentation elements
- **MANDATORY**: Follow MVVM architectural documentation standards
- **Python 3.10+ REQUIRED**: Document PySide6 compatibility requirements

## Docstring Standards

### Format
Use Google or NumPy docstring style as specified in [copilot-instructions.md](../copilot-instructions.md).

### Requirements
- **ALL** public classes, methods, and functions must have docstrings
- Use type hints instead of documenting types in docstrings
- Keep descriptions concise and clear
- Document parameters, returns, and raises
- Include usage examples for complex APIs

### Example
```python
def process_data(items: list[str], validate: bool = True) -> dict[str, int]:
    """Process a list of items and return frequency counts.

    Args:
        items: List of strings to process.
        validate: Whether to validate items before processing.

    Returns:
        Dictionary mapping items to their frequency counts.

    Raises:
        ValueError: If validate is True and invalid items found.

    Example:
        >>> process_data(['a', 'b', 'a'])
        {'a': 2, 'b': 1}
    """
```

## Inline Documentation
- Use inline comments for complex logic blocks
- Explain MVVM-specific patterns and choices
- Document Qt-specific behaviors
- Clarify signal/slot connections
- Note threading considerations

## MVVM Documentation Requirements

### Model Layer
- Document business logic and validation rules
- Explain domain-specific concepts
- Note any assumptions or constraints
- No Qt-related documentation needed

### ViewModel Layer
- Document signals and their purposes
- Explain state management approach
- Note threading considerations
- Document dependencies and injection

### View Layer
- Document UI structure and organization
- Explain custom widgets or behaviors
- Note Qt Designer usage if applicable
- Document signal/slot connections

## Project Documentation Files

### README.md
- Project overview and purpose
- Quick start guide
- Installation instructions
- MVVM architecture explanation
- Development workflow
- Testing approach

### AGENTS.md
- Quick reference for AI agents
- Common patterns and templates
- Troubleshooting guide
- Development checklist

### CONTRIBUTING.md
- How to contribute
- Code style guidelines
- MVVM principles to follow
- Testing requirements
- Pull request process

## Code Comments Best Practices

- **DO**: Explain why, not what
- **DO**: Document non-obvious design decisions
- **DO**: Explain MVVM layer boundaries
- **DO**: Note Qt-specific behaviors
- **DON'T**: State the obvious
- **DON'T**: Leave TODO comments without issues
- **DON'T**: Include commented-out code

## Documentation Checklist

- [ ] All public APIs have docstrings
- [ ] Type hints are present and accurate
- [ ] Complex logic has inline comments
- [ ] MVVM architecture is documented
- [ ] README is up to date
- [ ] Examples are working and clear
- [ ] Sphinx/pdoc compatible format (if applicable)

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