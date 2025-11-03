# GitHub Copilot Prompts for PySide6 MVVM Template

This directory contains specialized prompts for developing PySide6 desktop applications following MVVM architecture and SOLID principles.

## Available Prompts

### MVVM Component Creation

#### `create-feature.prompt.md`

**Purpose**: Create a complete MVVM feature with all layers
**Creates**: Model, Service, ViewModel, View, and tests
**Use When**: Starting a new feature from scratch
**Output**: Complete feature with proper layer separation

#### `create-model.prompt.md`

**Purpose**: Create a new Model class
**Creates**: Model class in `src/models/` with tests
**Use When**: Need business logic or domain entity
**Key Points**: No Qt imports, pure Python, validation logic

#### `create-viewmodel.prompt.md`

**Purpose**: Create a new ViewModel class
**Creates**: ViewModel in `src/viewmodels/` with tests
**Use When**: Need presentation logic and state management
**Key Points**: Inherits QObject, defines signals, uses dependency injection

#### `create-view.prompt.md`

**Purpose**: Create a new View class
**Creates**: View in `src/views/`
**Use When**: Need UI component
**Key Points**: Accepts ViewModel, minimal logic, signal/slot connections

#### `create-service.prompt.md`

**Purpose**: Create a new Service class
**Creates**: Service in `src/services/` with protocol and tests
**Use When**: Need external integration (files, APIs, database)
**Key Points**: Protocol-based, proper error handling

#### `create-ui.prompt.md`

**Purpose**: Generate Qt Designer .ui file from Python code
**Creates**: .ui XML file in `src/views/`
**Use When**: Want to design UI visually in Qt Designer
**Key Points**: Maps Python widgets to Qt Designer XML

### Code Quality and Maintenance

#### `code-review.prompt.md`

**Purpose**: Comprehensive code review
**Checks**: MVVM separation, SOLID principles, type hints, tests
**Use When**: Before merging or for quality assessment
**Output**: Structured review with issues and recommendations

#### `refactor.prompt.md`

**Purpose**: Refactor code following MVVM and SOLID
**Improves**: Layer separation, DRY, type safety, patterns
**Use When**: Code needs restructuring or cleanup
**Key Points**: Maintains MVVM boundaries, eliminates duplication

#### `arrange_code.prompt.md`

**Purpose**: Organize code structure logically
**Rearranges**: Classes, methods, functions
**Use When**: Code organization is messy
**Key Points**: MVVM-aware ordering, no logic changes

#### `cleanup.prompt.md`

**Purpose**: Clean up repository files
**Removes**: Cache files, duplicates, unused code
**Use When**: Repository needs housekeeping
**Key Points**: Preserves MVVM structure, validates architecture

### Testing and Debugging

#### `test.prompt.md`

**Purpose**: Create and manage tests
**Creates**: Unit and integration tests using pytest
**Use When**: Need test coverage
**Key Points**: pytest-qt for Qt testing, MVVM-specific patterns

#### `debug.prompt.md`

**Purpose**: Analyze code for bugs
**Identifies**: MVVM violations, memory leaks, logic errors
**Use When**: Troubleshooting issues
**Key Points**: MVVM-specific checks, threading issues

### Documentation

#### `documentation.prompt.md`

**Purpose**: Create or update documentation
**Updates**: Docstrings, README, inline comments
**Use When**: Documentation is missing or outdated
**Key Points**: Type hints, MVVM architecture docs

#### `explain.prompt.md`

**Purpose**: Explain code selection
**Output**: Clear explanation of purpose and design
**Use When**: Need to understand code
**Mode**: Ask mode (interactive)

### Version Control and Deployment

#### `version-update.prompt.md`

**Purpose**: Update version and changelog
**Updates**: Version numbers, CHANGELOG.md
**Use When**: Releasing new version
**Format**: Semantic versioning (MAJOR.MINOR.PATCH)

#### `merge-to-main.prompt.md`

**Purpose**: Complete end-to-end branch merge process
**Performs**: Pre-merge preparation, validation, merge execution, and post-merge verification
**Use When**: Ready to merge feature branch into main
**Output**: Successfully merged main branch with comprehensive validation

#### `venv-init.prompt.md`

**Purpose**: Initialize Python virtual environment
**Creates**: venv with dependencies
**Use When**: Setting up new development environment
**Key Points**: Python 3.10+, PySide6, pytest

## Prompt Usage

### Using Prompts in GitHub Copilot

1. **Chat Mode**: Reference prompt in chat

   ```text
   @workspace Use the create-model.prompt.md to create a User model
   ```

2. **File Context**: Open prompt file and ask Copilot to execute it

3. **Quick Access**: Use workspace command palette to access prompts

### Customizing Prompts

All prompts can be customized for your specific needs:

1. Edit the `.prompt.md` file
2. Modify guidelines and templates
3. Add project-specific requirements
4. Commit changes to version control

## Prompt Development Guidelines

When creating new prompts:

- **Use descriptive filenames**: `[action]-[component].prompt.md`
- **Include frontmatter**: mode, description
- **Provide templates**: Code examples and patterns
- **MVVM-first**: Always consider layer separation
- **Include checklists**: Help ensure completeness
- **Add testing**: Include test creation guidance

## Integration with Repository

These prompts work with:

- **`.github/copilot-instructions.md`**: Comprehensive guidelines
- **`AGENTS.md`**: Quick reference for AI agents
- **`.agents/memory.instruction.md`**: Coding preferences

## Quick Reference by Task

### Starting New Work

1. `create-feature.prompt.md` - Complete feature
2. `create-model.prompt.md` - Just Model layer
3. `create-viewmodel.prompt.md` - Just ViewModel layer
4. `create-view.prompt.md` - Just View layer

### Improving Code

1. `refactor.prompt.md` - Restructure code
2. `code-review.prompt.md` - Review quality
3. `arrange_code.prompt.md` - Organize files
4. `cleanup.prompt.md` - Remove cruft

### Testing & Debugging

1. `test.prompt.md` - Add tests
2. `debug.prompt.md` - Find bugs

### Documentation & Release

1. `documentation.prompt.md` - Update docs
2. `version-update.prompt.md` - New version
3. `merge-to-main.prompt.md` - Complete merge process

## Best Practices

1. **Read the full prompt** before using
2. **Customize for your needs** - prompts are templates
3. **Follow MVVM principles** - all prompts enforce architecture
4. **Test everything** - prompts include test creation
5. **Document as you go** - use documentation prompts regularly

## Getting Help

- See `AGENTS.md` for quick reference
- Read `.github/copilot-instructions.md` for detailed guidelines
- Check individual prompt files for specific requirements
- Consult PySide6 documentation for Qt specifics

## Contributing

When adding new prompts:

1. Follow existing prompt structure
2. Include MVVM-specific guidance
3. Provide code templates
4. Add testing instructions
5. Update this README
6. Test with GitHub Copilot

---

**Template Version**: 0.1.0
**Last Updated**: 2025-11-02
**Maintained By**: Template Contributors
