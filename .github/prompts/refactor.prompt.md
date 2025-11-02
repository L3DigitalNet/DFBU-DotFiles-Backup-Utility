---
description: "Code Refactoring and Optimization following repository guidelines"
mode: "agent"
---

# Code Refactoring and Optimization

Perform comprehensive refactoring of ${file} or project following repository guidelines and clean architecture principles.

Follow [repository guidelines](../copilot-instructions.md).

## Core Refactoring Principles

### DRY (Don't Repeat Yourself) - HIGH PRIORITY
- **MUST** eliminate ALL code duplication through abstraction and modularization
- **MUST** maintain single source of truth for all data structures and business logic
- **MUST** centralize constants and configuration in dedicated modules
- **MUST** extract common patterns into base classes or utility functions
- **MUST** consolidate similar logic into unified implementations

### Python Standard Library First - MANDATORY
- **MUST** use Python standard library solutions before considering external dependencies
- **MUST** leverage built-in modules: `pathlib`, `json`, `csv`, `datetime`, `collections`, `itertools`, `functools`
- **ONLY** add external dependencies when standard library cannot reasonably solve the problem
- **MUST** justify external dependencies with comments explaining why standard library is insufficient
- **MUST** replace existing external dependencies with standard library equivalents where possible

### Clean Code and Confident Design - ESSENTIAL
- **PREFER** confident, clean code over defensive programming patterns
- **AVOID** unnecessary null/None checks when program flow guarantees valid values
- **PREFER** explicit initialization and clear program flow over defensive conditionals
- **MUST** design code that reflects actual program behavior and constraints
- **MUST** order functions and classes to reflect logical flow and dependencies; classes always listed first
- **AVOID** excessive defensive checks that add noise without meaningful protection
- **PREFER** early validation and fail-fast approaches over scattered defensive checks
- **MUST** use type hints to document and enforce design assumptions
- **PREFER** clear, linear program flow with proper initialization order
- **AVOID** "just in case" code that handles scenarios that shouldn't occur in correct usage

## Type Hints and Documentation

### Type Hint Requirements
- **MUST** include type hints for ALL functions, methods, variables, constants, and data structures
- **MUST** use modern union syntax: `str | None` not `Optional[str]`
- **MUST** use collection types: `list[str]`, `dict[str, int]`, `set[int]`
- **MUST** use `Final` for constants, `ClassVar` for class variables, `TypedDict` for structured dicts
- **MUST** use `Protocol` for interfaces, `TypeVar`/`Generic` for reusable components
- **AVOID** `Any` type - use specific types or protocols

### Documentation Standards
- Follow repository docstring standards as per [copilot-instructions.md](../copilot-instructions.md)
- **MUST** include docstrings for ALL public functions, methods, and classes
- **MUST** follow specific docstring format patterns
- **MUST** maintain 80 character limit for docstring lines
- **STREAMLINED** approach: Brief descriptions with types in hints, examples only for complex logic

## Architectural Improvements

### Single Responsibility Principle
- **MUST** keep functions focused (single responsibility)
- **MUST** ensure each class has clear, cohesive purpose
- **MUST** organize code into focused, single-purpose modules
- **MUST** separate business logic, data access, and presentation layers
- **AVOID** deep nesting (max 3 levels)
- **AVOID** complex conditional statements

### Clean Architecture Patterns
- **MUST** implement proper separation of concerns
- **MUST** create clear interfaces and boundaries between components
- **MUST** design for composition over inheritance
- **MUST** follow SOLID principles in class design
- **MUST** implement clear dependency management

## Code Quality Standards

### Function and Class Design
- **MUST** use descriptive, self-documenting names for all elements
- **MUST** follow strict PEP 8 compliance
- **MUST** use f-string formatting (never `.format()` or `%` formatting)
- **MUST** list function arguments on separate lines when more than two arguments
- **MUST** align arguments with opening parenthesis or use hanging indent (4 spaces)

### Performance and Maintainability
- **MUST** optimize for readability and maintainability over premature optimization
- **MUST** reduce complexity through clear design patterns
- **MUST** use built-in functions and data structures for better performance
- **MAY** suggest external libraries ONLY when they provide significant, justified benefits
- **PREFER** eliminate performance bottlenecks through proper algorithm and data structure choices if this does not compromise code clarity

## Version-Aware Refactoring Strategy

### Pre-v1.0.0 Focus (Current Phase)
- **DEFER** comprehensive error handling until v1.0.0
- **FOCUS** on clean architecture, confident design patterns
- **PRIORITIZE** core functionality and clear program flow
- **IMPLEMENT** proper initialization sequences that guarantee valid state
- **AVOID** excessive defensive programming patterns

### Incremental Improvement Approach
- **MUST** make small, testable improvements rather than large rewrites
- **MUST** preserve external behavior during refactoring
- **MUST** maintain or improve test coverage
- **MUST** update documentation to reflect changes

## Repository Integration

### Project Structure Compliance
- **MUST** follow project template structure from `templates/my_project_folder_template/`
- **MUST** store ALL test files in each project's `/tests/` directory
- **MUST** maintain proper `__init__.py` files and package organization

### Linux Environment Compliance
- **PYTHON VERSION**: Ensure compatibility with Python 3.14+.
- **IMPORTANT** All refactored code designed for Linux environments only
- **MUST** use Linux-specific paths, commands, and system calls where appropriate
- **NOT COMPATIBLE** with Windows environments

## Refactoring Decision Framework

### When refactoring, prioritize:
1. **DRY Violations**: Can this logic be unified with existing implementations?
2. **Standard Library**: Can external dependencies be replaced with built-in solutions?
3. **Type Safety**: Are all elements properly typed and documented?
4. **Confident Design**: Can defensive patterns be replaced with architectural solutions?
5. **Reusability**: Can this be generalized for use by other projects?
