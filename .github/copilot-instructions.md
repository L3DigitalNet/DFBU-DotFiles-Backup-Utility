#!/usr/bin/env python3
"""
Project Title - Brief Description

Note: UTF-8 encoding headers are NOT required in Python 3 (UTF-8 is default).
Do not add encoding declarations unless non-UTF-8 encoding is actually needed.

Description:
    What this module does and why.

Author: [Full Name]
Email: [email@domain.com]
GitHub: [https://github.com/username]
Date Created: [MM-DD-YYYY]
Date Changed: [MM-DD-YYYY]
License: [License Type]

Features:
    - [Domain-specific features]
    - Standard library first approach
    - Clean confident design patterns

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - Additional technical requirements and dependencies

Known Issues:
    - Current limitations or known problems
    - Areas that need improvement or attention

Planned Features:
    - Future enhancement 1
    - Future enhancement 2
    - Additional planned improvements

Classes:
    - Class1: Brief description
    - Class2: Brief description

Functions:
    - function1(): Brief description
    - function2(): Brief description
"""

### Documentation Format
```python
class ExampleClass:
    """
    Brief description of the class purpose.

    Attributes:
        attribute1: description of first attribute
        attribute2: description of second attribute
        attribute3: description of third attribute

    Public methods:
        method1: description of first public method
        method2: description of second public method

    Private methods:
        _private_method: description of private method

    Static methods:
        static_method: description of static method
    """
```

#### Function Docstring Format:
```python
def example_function(param1: str, param2: int) -> str:
    """
    Brief description of function purpose.

    Args:
        param1: description of first parameter
        param2: description of second parameter

    Returns:
        description of return value
    """
```

## Project Organization

### Structure
- **Tests:** ALL test files and test documentation in project's `/tests/` directory
- **Config:** Separate files, never hardcode values
- **Docs:** ALL documentation in project's `/docs/` directory (PROJECT-DOC.md, CHANGELOG.md, configuration guides, usage docs, feature docs)
- **README.md:** Basic, human-written content only - kept in project root, never AI-verbose

### Testing with pytest
- **Framework:** pytest only, AAA pattern (Arrange-Act-Assert)
- **Storage:** ALL test files in project's `/tests/` directory
- **Naming:** Test files start with `test_`, test functions start with `test_`
- **Assertions:** Use pytest's assert statement only (no unittest-style assertions)
- **Coverage:** 90%+ for critical paths
- **Focus:** Core functionality and happy paths before v1.0.0
- **Test Names:** Descriptive names that explain expected behavior
- **Test Quality:** Keep tests fast, isolated, and deterministic
- **Test Targets:** Actual program behavior, initialization sequences, program flow, type compliance, public interfaces
- **Minimize:** Error handling and edge case testing until v1.0.0
- **Prioritize:** Core functionality testing and business logic validation
- **Features:** Use fixtures, parametrize, markers for categorization (unit, integration, slow, etc.)

### Version Management
- **Format:** MAJOR.MINOR.PATCH (start 0.0.1, v1.0.0 = first release)
- **Changelog:** Update `/docs/CHANGELOG.md` on version increment
- **Content:** Analyze code changes, categorize (Added/Changed/Fixed/Removed)
- **Headers:** Update "Date Changed" field when version updated

## AI Code Generation Rules

When generating code:

1. **Dependencies:** Standard library first, justify external dependencies
3. **Quality:** Type hints for ALL elements, streamlined docstrings, proper headers
4. **Architecture:** Follow patterns, SOLID principles, composition over inheritance
5. **Confident Design:** Avoid defensive programming, use architectural solutions over scattered checks
6. **Version Awareness:** Defer error handling/validation until around v0.8.0 (unless absolutely necessary), focus on clean architecture
7. **Public Repository Rules:**
   - Keep README.md basic and human-sounding
   - Minimize .md file creation to avoid repository pollution
   - Place all docs in `/docs/` directory, all tests in `/tests/` directory
   - Never create scattered documentation files
8. **Testing:** Use pytest framework, write tests for ALL logic, follow pytest conventions
9. **Version Management:** Update CHANGELOG.md in `/docs/` folder when incrementing versions, document all changes
10. **Inline Comments:** Include comments for each significant code block for readability and autocompletion context
11. **Type Safety:** Verify runtime behavior matches type annotations, use contract testing
12. **Architectural Patterns:** Implement proper separation of concerns and clear component boundaries

## Decision Framework

### When choosing between solutions:
1. **First:** Can Python standard library solve this?
2. **Second:** Does similar functionality already exist in the codebase?
3. **Third:** Can this be generalized for reuse by other projects?
4. **Last:** Is an external dependency truly necessary?

### Code smell indicators to avoid:
- Duplicate logic across files
- Hardcoded values that should be configurable
- Functions longer than 20 lines
- Missing type hints for functions, variables, constants, or data structures
- Untyped constants, module variables, class attributes, or collections
- Missing or inadequate docstrings
- Import statements for external libraries when standard library suffices
- Excessive defensive programming (scattered None checks, "just in case" conditionals)
- Complex nested conditionals that could be simplified with clear initialization
- Type hints that suggest uncertainty (Optional types) when values are guaranteed

## CLI Tool Development Guidelines

*Note: These are CLI-specific requirements. All common requirements (file headers, testing, inline documentation) are defined above.*

### CLI Requirements
- **MUST** use `argparse` for argument parsing
- **MUST** implement proper exit codes (0=success, non-zero=error)
- **MUST** handle SIGINT (Ctrl+C) gracefully
- **MUST** support `--verbose`, `--quiet`, `--help`, `--version`
- **MUST** provide progress indicators for long operations
- **MUST** use logging levels appropriately
- **MUST** test argument parsing, exit codes, and interactive modes using pytest
- **MUST** validate CLI behavior through automated testing of command-line interfaces

### CLI-Specific Header Features
- **MUST** include CLI-specific Features section with:
  - Proper exit codes (0=success, non-zero=error)
  - Signal handling for graceful shutdown (SIGINT/Ctrl+C)
  - Standard CLI options: --verbose, --quiet, --help, --version
  - Progress indicators for long-running operations

### CLI Code Generation Focus
- **Framework:** Use `argparse`, `pathlib`, built-in `logging`
- **Architecture:** Separate parsing → validation → execution
- **Pattern:** Follow template below

### CLI Code Template

```python
#!/usr/bin/env python3

def main() -> int:
    """Main entry point. Returns exit code."""
    # NOTE: Error handling deferred until v1.0.0 per main guidelines
    args = parse_arguments()
    setup_logging(args.verbose, args.quiet)
    return execute_command(args)

if __name__ == "__main__":
    sys.exit(main())
```

## Desktop Application Development Guidelines

*Note: These are Desktop-specific requirements. All common requirements (file headers, testing, inline documentation) are defined above.*

### Desktop Requirements
- **MUST** implement MVVM (Model–View–ViewModel) for Qt/PySide:
- **MUST** handle threading for non-blocking UI
- **MUST** provide user feedback for long operations
- **MUST** save/restore window state and preferences
- **MUST** separate business logic from GUI for testing
- **MUST** test business logic independently of GUI components
- **MUST** validate UI behavior through integration testing where appropriate

### Desktop Header Requirements
- **MUST** include Desktop-specific Features section with:
  - MVVM (Model–View–ViewModel) architectural pattern for clean separation of concerns
  - Threaded operations to prevent UI blocking
  - Window state persistence (size, position, preferences)
  - Responsive user feedback for long operations

### Desktop Code Generation Focus
- **Framework:** PySide6 first, justify alternatives
- **Architecture:** Separate business logic from UI, use MVVM
- **Pattern:** Follow template below

### Desktop Application Template

```python
#!/usr/bin/env python3

class Application:
    """Main application controller."""

    def __init__(self):
        self.model = DataModel()
        self.view = MainWindow(self)
        self.setup_event_handlers()

    def setup_event_handlers(self):
        """Connect UI events to business logic."""
        self.view.on_save = self.handle_save
        self.view.on_load = self.handle_load

    def run(self):
        """Start the application main loop."""
        # NOTE: Error handling deferred until v1.0.0 per main guidelines
        self.view.mainloop()
        self.cleanup()
```
