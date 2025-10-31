# Common Library - v0.2.0

## Description

This directory contains shared code and utilities used across multiple projects in the Python repository. It provides reusable components to streamline development and maintain consistency across command-line applications, desktop applications, and utilities. The library follows the repository's standard library first approach and DRY principles to minimize dependencies and code duplication.

## Files Overview

- **`cust_class.py`**: Custom classes for terminal applications including ANSI color formatting, interactive CLI menus, and performance monitoring (3 main classes)
- **`cust_func.py`**: Custom functions module providing reusable utility functions for common programming tasks (placeholder structure for future utility functions)
- **`__init__.py`**: Package initialization file for importing classes and functions with centralized exports and version management
- **`version.py`**: Version information and metadata for the common library package
- **`README.md`**: Comprehensive documentation for all classes, functions, and usage patterns

## Current Status

**Version 0.2.0** - Implementation with core terminal interface classes and performance monitoring. The library provides essential building blocks for terminal applications with proper ANSI color support, interactive menus, and performance analysis capabilities.

## Available Classes

### AnsiColor (cust_class.py)

A utility class for building ANSI escape sequences for terminal text formatting and styling, supporting both standard and bright colors for foreground and background, plus various text styling options.

**Key Features:**

- **Standard and bright colors** for foreground and background text (18 total color options)
- **Text styling options** including bold, dim, underline, blinking, and hidden
- **Property-based access** to formatting codes for easy use in applications
- **Comprehensive color support** with validation and type safety
- **Cross-platform compatibility** designed for Linux terminal environments
- **Type safety** with comprehensive type hints and validation

**Supported Colors:**

- **Standard**: black, red, green, yellow, blue, magenta, cyan, white, default
- **Bright**: bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, bright white

**Basic Usage:**

```python
from common_lib import AnsiColor

# Create color formatter with specific colors
red_on_yellow = AnsiColor("red", "yellow")
print(f"{red_on_yellow.code}Colored text{red_on_yellow.reset}")

# Use styling properties for enhanced formatting
formatter = AnsiColor("green", "black")
print(f"{formatter.bold}Bold green text{formatter.reset}")
print(f"{formatter.underline}Underlined green text{formatter.reset}")
```

**Advanced Usage:**

```python
# Use styling properties for enhanced formatting
formatter = AnsiColor("green", "black")
print(f"{formatter.bold}Bold green text{formatter.reset}")
print(f"{formatter.underline}Underlined green text{formatter.reset}")

# Quick color access
blue_text = AnsiColor("blue")
print(f"{blue_text.code}Blue text{blue_text.reset}")
```

## CLIMenu (cust_class.py)

A simple command-line interface menu utility class that provides basic CLI menu display and interactive user prompts with yes/no/quit functionality.

**Key Features:**

- **Numbered menu options** with automatic list generation
- **Interactive user input** with input validation and error handling
- **Quit functionality** with graceful exit handling (Ctrl+C and 'q' command)
- **Function mapping** to execute selected menu options
- **Simple interface** for quick CLI menu implementation
- **Error handling** for EOF and KeyboardInterrupt exceptions

**Basic Usage:**

```python
from common_lib import CLIMenu

def task_one():
    print("Executing task one...")

def task_two():
    print("Executing task two...")

# Create and run menu
menu = CLIMenu()
menu_options = {
    "Run Task One": task_one,
    "Run Task Two": task_two,
}
menu.run(menu_options)

# Yes/No/Quit prompt
menu = CLIMenu()
if menu.ynq("Do you want to continue?"):
    print("User selected yes")
else:
    print("User selected no")
```

## PerfMon (cust_class.py)

A performance monitoring and logging utility class that provides comprehensive performance tracking, statistical analysis, and logging capabilities for function execution times.

**Key Features:**

- **Automatic execution time tracking** with function name detection
- **Statistical analysis** including all-time averages and rolling averages
- **Performance logging** to hostname-specific log files with timestamps
- **Comprehensive statistics** with configurable rolling window sizes (5, 10, 20, 50 calls)
- **Log file management** with automatic directory creation and proper formatting
- **Color-coded terminal output** using integrated AnsiColor formatting
- **Hostname identification** for multi-system logging environments
- **Raw logging capabilities** for custom log entries and section headers

**Basic Usage:**

```python
import time
from common_lib import PerfMon

# Create performance monitor (auto-detects log directory)
perf = PerfMon()

# Monitor function execution time
start_time = time.perf_counter()
# ... your code here ...
end_time = time.perf_counter()

# Report execution time (auto-detects function name)
perf.report_time(start_time, end_time)

# Get performance statistics for all logged functions
stats = perf.get_performance_stats()
print(stats)

# Log comprehensive averages summary
perf.log_averages()

# Custom log entries
perf.log_section_header("Custom Section")
perf.log_raw_line("Custom log entry")
perf.log_separator("="*30)
```

**Performance Statistics:**

The PerfMon class provides detailed statistics including:

- **All-time averages** for each monitored function
- **Total call counts** for function execution tracking
- **Rolling averages** with configurable window sizes (last 5, 10, 20, 50 calls)
- **Function execution time** with millisecond precision
- **Hostname-specific logging** for distributed system monitoring

**Log File Features:**

- **Automatic log directory** detection based on calling module location
- **Hostname-specific filenames** for multi-system environments
- **Timestamped entries** with microsecond precision
- **Structured logging format** for easy parsing and analysis
- **Corruption resistance** with error handling for malformed log entries

---

## Available Functions (cust_func.py)

The `cust_func.py` module is designed to house reusable utility functions that can be shared across multiple projects. Currently, this module contains:

**Key Features:**

- **Placeholder structure** for future utility functions
- **Standard library first** approach to minimize dependencies
- **Comprehensive type hints** and documentation standards
- **Linux environment optimization** for POSIX-compliant implementations
- **Repository coding standards** compliance with PEP 8 and docstring requirements

**Current Status:**

The module is currently in its initial state with placeholder structure. Future utility functions will be added here following the repository guidelines:

- Functions that can be reused across multiple projects
- Python standard library solutions before external dependencies
- Comprehensive error handling and input validation
- Type hints for all function parameters and return values
- Google/NumPy style docstrings with examples

**Usage Pattern:**

```python
from common_lib import cust_func

# Future utility functions will be accessible here
# result = cust_func.utility_function(param1, param2)
```

**Note:** This module follows the DRY (Don't Repeat Yourself) principle by providing a centralized location for utility functions that would otherwise be duplicated across projects.

---

## Package Imports

All classes can be imported directly from the package:

```python
# Import all main classes
from common_lib import AnsiColor, CLIMenu, PerfMon

# Import utility functions module (placeholder)
from common_lib import cust_func

# Or import individual classes as needed
from common_lib import AnsiColor
from common_lib import CLIMenu
from common_lib import PerfMon
```

## Usage Notes

- All classes are designed for **Linux environments** and assume POSIX-compliant terminal capabilities
- The library uses **Python standard library only** - no external dependencies required
- All classes follow repository coding standards with comprehensive **type hints** and **docstrings**
- **AnsiColor** provides cross-platform ANSI escape sequence support for Linux terminals
- **PerfMon** automatically detects log directory location based on calling module
- **Testing ready** structure supports comprehensive unit testing with PyTest framework
- **DRY principle** implementation reduces code duplication across projects

## Version Information

- **Current Version**: 0.2.0 (cust_class.py)
- **Functions Version**: 0.1.0 (cust_func.py)
- **Package Version**: 0.2.0 (common_lib package)
- **Total Classes**: 3 main utility classes (AnsiColor, CLIMenu, PerfMon)
- **Python Requirements**: Python 3.14+ minimum
- **Platform**: Linux/Unix systems only

## Future Development

Planned enhancements for future versions:

- **ErrorHandler class**: Comprehensive exception handling with 31+ specialized exception types
- **LogManager class**: Advanced logging with rotation, cleanup, and multi-destination support
- **Additional utility functions** in `cust_func.py` based on project needs
- **Enhanced CLI functionality** with more interactive features
- **Integration improvements** with other repository projects

## Documentation

- **Inline Documentation**: All classes have comprehensive docstrings with usage examples following Google/NumPy style
- **Type Hints**: Full type annotation support for better IDE integration and development experience
- **Error Handling**: Complete documentation within ErrorHandler class docstrings with 31 specialized exception types
- **Repository Standards**: All code follows `.github/copilot-instructions.md` guidelines for consistency
- **API Design**: Classes designed for extensibility and ease of use across different project types
- **Testing Framework**: Ready for comprehensive unit testing with PyTest (tests to be implemented)
