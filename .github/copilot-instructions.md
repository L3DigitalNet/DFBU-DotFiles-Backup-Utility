# Python Repository Guidelines

## ⛔ CRITICAL BRANCH PROTECTION RULE ⛔

**AI AGENTS MUST NEVER MAKE CODE CHANGES TO THE `main` BRANCH**

### Exception for Human-Initiated Merges:
**EXCEPTION:** If the merge is initiated by a human using the `/merge_testing_to_main` command, AI agents are then permitted to modify the `main` branch as part of that merge process.

### Enforcement Rules:
1. **ALL code changes** must be made to the `testing` branch (except during human-initiated `/merge_testing_to_main` command)
2. **BEFORE making ANY file edits**, verify current branch with: `git branch --show-current`
3. **IF on `main` branch**, STOP immediately and switch to `testing`: `git checkout testing`
   - **UNLESS** currently executing a human-initiated `/merge_testing_to_main` command
4. **NO EXCEPTIONS** except as noted above - This rule applies to:
   - New files creation
   - File modifications
   - File deletions
   - Any code changes whatsoever
5. **Merge workflow**: Only humans may initiate merges `testing` → `main` after review

### Verification Steps (MANDATORY before ANY code change):
```bash
# Step 1: Check current branch
git branch --show-current

# Step 2: If output is "main", switch to testing
git checkout testing

# Step 3: Verify switch was successful
git branch --show-current  # Must show "testing"
```

**VIOLATION CONSEQUENCES**: Any AI agent that modifies code on `main` branch is in direct violation of repository policy.

---

## Notes
- Projects use Python 3.14+ features (e.g., `Path.copy()`)
- #fetch https://docs.python.org/3.14/index.html for latest stdlib documentation

## Critical Requirements (AI Priority Order)

### 1. Environment & Dependencies
- **Linux-only:** All code for Linux environments exclusively
- **Standard library first:** Use Python stdlib before external dependencies
- **Justify externals:** Comment why stdlib is insufficient when adding dependencies
- **Key modules:** `pathlib`, `json`, `csv`, `datetime`, `collections`, `itertools`, `functools`

### 2. Code Architecture
- **DRY principle:** Use `projects/common_lib/` for shared utilities
- **Confident design:** Avoid defensive programming, prefer clear initialization
- **Single source of truth:** Centralize logic, eliminate duplication
- **Type safety:** Full type hints, modern union syntax (`str | None`)

### 3. Version Strategy
- **Error handling:** Defer until v1.0.0, focus on clean architecture first
- **Testing focus:** Happy path and core functionality before v1.0.0
- **Versioning:** MAJOR.MINOR.PATCH format, start at 0.0.1

## Technical Standards

### Python & Code Quality
- **Version:** Python 3.14+ minimum
- **Style:** Strict PEP 8, f-strings only (no `.format()` or `%`)
- **Types:** Full type hints everywhere - functions, variables, constants, collections
- **Modern syntax:** `str | None`, `list[str]`, `dict[str, int]`, `Final`, `Protocol`, `TypedDict`
- **Functions:** Small, focused, descriptive names, max 3 nesting levels

### File Structure (Required)
- **MUST** include shebang and encoding: `#!/usr/bin/env python3` and `# -*- coding: utf-8 -*-`
- **MUST** follow standard header format with project-specific Features section
- **MUST** include inline comments for each significant code block for readability and AI autocompletion context
- **MUST** place comments at the top of code blocks explaining their purpose, preferably in one line
- **MUST** add inline comments for complex logic, Linux-specific implementations, and important decisions

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Title - Brief Description

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
    - Custom libraries located at ../common_lib/
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
```

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
- **Template:** Use `templates/my_project_folder_template/`
- **Shared code:** `projects/common_lib/` for utilities
- **Tests:** ALL test files in project's `/tests/` directory
- **Config:** Separate files, never hardcode values
- **Docs:** README.md (root), PROJECT-DOC.md & CHANGELOG.md in `/docs/`

### Testing with pytest
- **Framework:** pytest only, AAA pattern (Arrange-Act-Assert)
- **Storage:** ALL test files in project's `/tests/` directory
- **Naming:** Test files start with `test_`, test functions start with `test_`
- **Assertions:** Use pytest's assert statement only (no unittest-style assertions)
- **Coverage:** 80%+ for critical paths
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
2. **Reuse:** Check existing codebase, consolidate duplicates, use `projects/common_lib/`
3. **Quality:** Complete examples, type hints for ALL elements, streamlined docstrings, proper headers
4. **Architecture:** Follow patterns, SOLID principles, composition over inheritance
5. **Confident Design:** Avoid defensive programming, use architectural solutions over scattered checks
6. **Version Awareness:** Defer error handling/validation until v1.0.0, focus on clean architecture
7. **Documentation:** Minimize .md file creation, avoid test summary docs, use README.md and single PROJECT-DOC.md per project
8. **Testing:** Use pytest framework, write tests for all business logic, follow pytest conventions
9. **Version Management:** Update CHANGELOG.md in `/docs/` folder when incrementing versions, document all changes
10. **Inline Comments:** Include comments for each significant code block for readability and AI context
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
