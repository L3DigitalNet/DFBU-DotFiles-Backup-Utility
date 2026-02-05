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

## DFBU Project Documentation

### Core Documentation Files
- **README.md**: Create or update comprehensive README.md with project directory structure, installation, usage, and architecture overview.
- **CHANGELOG.md**: Maintain CHANGELOG.md in `DFBU/docs/` with version history, changes, and Linux-specific notes.

### Project Documentation -> DFBU/docs/*.md

Create or update the following documentation files in the `DFBU/docs/` directory:

- **ARCHITECTURE.md**: Detailed architecture document covering MVVM design, SOLID principles, module interactions, and component responsibilities.
- **QUICKSTART.md**: Quick start guide for CLI usage, configuration, and basic operations.
- **QUICKSTART_UI_UV.md**: Quick start guide for GUI usage with UV package manager setup.
- **UI_DESIGN_GUIDE.md**: Guide for Qt Designer workflow, UI file management, and PySide6 integration.
- **README.md**: Test suite documentation explaining testing approach, fixtures, and coverage goals.

### Component Documentation (File-Level) -> DFBU/

For Python modules in `DFBU/gui/` and `DFBU/core/`:
- Maintain comprehensive docstrings for all public classes and methods
- Include inline comments for complex logic and MVVM-specific patterns
- Document signal/slot connections and threading considerations
- Explain Qt Designer .ui file integration where applicable

### Testing Documentation -> DFBU/tests/

- **README.md**: Comprehensive testing documentation explaining test organization, fixtures, markers, and coverage requirements
- Test files should have clear docstrings explaining test purpose and setup
- No separate `_doc.md` files needed for test modules

### Configuration Documentation

- Document TOML configuration structure and validation rules
- Explain backup modes (mirror vs archive) and directory organization
- Include examples of common configuration scenarios



### Testing Documentation

- It is not necessary to create separate documentation files for test modules.
- If there are existing test documentation files they should be relocated to `DFBU/tests/`.

### Other Documentation

- Create or update one README.md file for each of the following directories:
 - /backup/ and subdirectories
 - /scripts/ and subdirectories
- This README.md should describe the purpose of each file in the respective directory, its purpose, and relation to the overall project.
