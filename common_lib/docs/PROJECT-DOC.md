# Common Library Project Documentation

**Description:** Comprehensive project documentation for Common Library. This single project documentation file provides detailed information about installation, usage, API reference, and examples for developers and users.

**Author:** Chris Purcell
**Email:** <chris@l3digital.net>
**GitHub:** <https://github.com/L3DigitalNet>
**Date Created:** 10-18-2025
**Date Changed:** 10-29-2025
**Version:** 0.2.0

## Overview

The Common Library is a collection of reusable utilities and shared code used across all projects in the Python repository. It provides essential building blocks for terminal applications with proper ANSI color support, interactive CLI menus, and comprehensive performance monitoring capabilities. The library follows clean architecture principles and is designed exclusively for Linux environments.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [API Reference](#api-reference)
4. [Examples](#examples)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Contributing](#contributing)

## Installation

### Linux Environment Requirements

- **Operating System:** Linux/Unix systems only (POSIX-compliant)
- **Python Version:** Python 3.14+ minimum for latest language features
- **Terminal:** ANSI color support required for full functionality
- **Dependencies:** None - uses Python standard library only

### Installation Steps

1. **Clone Repository:**

   ```bash
   git clone https://github.com/L3DigitalNet/Python.git
   cd Python/projects/common_lib
   ```

2. **Verify Python Version:**

   ```bash
   python3 --version  # Should be 3.14+
   ```

3. **Import in Your Project:**

   ```python
   # Add to your Python path or use relative imports
   from common_lib import AnsiColor, CLIMenu, PerfMon
   ```

## Quick Start

### Basic Color Formatting

```python
from common_lib import AnsiColor

# Create colored text
red_text = AnsiColor("red", "black")
print(f"{red_text.bold}Important Message{red_text.reset}")
```

### Simple CLI Menu

```python
from common_lib import CLIMenu

def option_one():
    print("Executing option one...")

menu = CLIMenu()
options = {"Option 1": option_one}
menu.run(options)
```

### Performance Monitoring

```python
import time
from common_lib import PerfMon

perf = PerfMon()
start = time.perf_counter()
# Your code here
end = time.perf_counter()
perf.report_time(start, end)
```

## API Reference

### AnsiColor Class

**Purpose:** Build ANSI escape sequences for terminal text formatting and styling.

**Constructor:**
```python
AnsiColor(fg_color: str = "default", bg_color: str = "default") -> None
```

**Properties:**
- `code: str` - Complete ANSI escape sequence
- `reset: str` - ANSI reset sequence
- `bold: str` - Bold styling
- `dim: str` - Dim styling  
- `underline: str` - Underline styling
- `blinking: str` - Blinking styling
- `hidden: str` - Hidden text styling

**Supported Colors:**
- Standard: black, red, green, yellow, blue, magenta, cyan, white, default
- Bright: bright black, bright red, bright green, bright yellow, bright blue, bright magenta, bright cyan, bright white

### CLIMenu Class

**Purpose:** Simple command-line interface menu utility.

**Methods:**
```python
run(menu_options: dict[str, Any]) -> None
ynq(prompt: str) -> bool
```

**Features:**
- Numbered menu display with automatic selection handling
- Yes/No/Quit prompts with graceful exit handling
- Keyboard interrupt handling (Ctrl+C)

### PerfMon Class

**Purpose:** Performance monitoring and logging utility.

**Constructor:**
```python
PerfMon(log_dir: Path | str | None = None) -> None
```

**Key Methods:**
```python
report_time(start_time: float, end_time: float, ndigits: int = 4) -> None
get_performance_stats() -> Dict[str, Any]
log_averages() -> None
log_raw_line(message: str) -> None
log_separator(separator: str = "=" * 50) -> None
log_section_header(title: str) -> None
```

**Statistics Features:**
- All-time averages for each function
- Rolling averages (last 5, 10, 20, 50 calls)
- Total call counts and execution times
- Hostname-specific logging with timestamps

## Examples

### Advanced AnsiColor Usage

```python
from common_lib import AnsiColor

# Create multiple formatters
error = AnsiColor("bright red", "black")
success = AnsiColor("bright green", "black")
warning = AnsiColor("bright yellow", "black")
info = AnsiColor("bright blue", "black")

# Use in application
print(f"{error.bold}ERROR:{error.reset} Something went wrong!")
print(f"{success.code}SUCCESS:{success.reset} Operation completed")
print(f"{warning.underline}WARNING:{warning.reset} Check this setting")
print(f"{info.blinking}INFO:{info.reset} Processing...")
```

### Complex CLI Menu

```python
from common_lib import CLIMenu

class AppMenu:
    def __init__(self):
        self.menu = CLIMenu()
    
    def start_service(self):
        print("Starting service...")
        if self.menu.ynq("Continue with startup?"):
            print("Service started successfully")
    
    def stop_service(self):
        print("Stopping service...")
    
    def show_status(self):
        print("Service status: Running")
    
    def run_main_menu(self):
        options = {
            "Start Service": self.start_service,
            "Stop Service": self.stop_service,
            "Show Status": self.show_status,
        }
        self.menu.run(options)

# Usage
app = AppMenu()
app.run_main_menu()
```

### Comprehensive Performance Monitoring

```python
import time
from pathlib import Path
from common_lib import PerfMon

class DataProcessor:
    def __init__(self):
        # Initialize with custom log directory
        self.perf = PerfMon(log_dir=Path.cwd() / "performance_logs")
    
    def process_data(self, data_size: int):
        start = time.perf_counter()
        
        # Simulate data processing
        time.sleep(0.1 * data_size)  # Simulate work
        
        end = time.perf_counter()
        self.perf.report_time(start, end)
    
    def generate_report(self):
        # Add section header to log
        self.perf.log_section_header("Performance Report")
        
        # Get and display statistics
        stats = self.perf.get_performance_stats()
        for func_name, data in stats.items():
            print(f"Function: {func_name}")
            print(f"  Average: {data['all_time_average']}s")
            print(f"  Total calls: {data['total_calls']}")
            print(f"  Rolling averages: {data['rolling_averages']}")
        
        # Log comprehensive averages
        self.perf.log_averages()
        
        # Add separator
        self.perf.log_separator("="*50)

# Usage
processor = DataProcessor()
for i in range(10):
    processor.process_data(i % 3 + 1)
processor.generate_report()
```

## Configuration

### Log Directory Configuration

The PerfMon class automatically determines log directory location:

1. **Explicit path:** Pass `log_dir` parameter to constructor
2. **Auto-detection:** Uses calling module's directory + `/logs/`
3. **Fallback:** Current working directory + `/logs/`

### Terminal Configuration

For optimal ANSI color support on Linux:

```bash
# Ensure terminal supports 256 colors
echo $TERM  # Should show xterm-256color or similar

# Test color support
tput colors  # Should return 256 or higher
```

### Environment Variables

```bash
# Optional: Set explicit terminal type
export TERM=xterm-256color

# Verify POSIX compliance
echo $SHELL  # Should show bash, zsh, or similar
```

## Troubleshooting

### Common Issues

**Colors not displaying correctly:**
- Verify terminal ANSI support: `tput colors`
- Check terminal type: `echo $TERM`
- Ensure Linux/Unix environment

**PerfMon log files not created:**
- Check directory permissions: `ls -la logs/`
- Verify path accessibility: `mkdir -p logs && touch logs/test.log`
- Review error messages in application output

**CLIMenu input not working:**
- Verify Python input() function works: `python3 -c "print(input('Test: '))"`
- Check terminal stdin availability
- Ensure no background process interference

### Debug Mode

Enable debugging for troubleshooting:

```python
import logging
from common_lib import PerfMon

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Create PerfMon instance with debug info
perf = PerfMon()
print(f"Log path: {perf.log_path}")
print(f"Hostname: {perf.hostname}")
```

## Contributing

### Development Guidelines

1. **Follow repository standards:** See `.github/copilot-instructions.md`
2. **Linux-only development:** Test on Linux systems exclusively
3. **Standard library first:** Justify external dependencies
4. **Type hints required:** Full type annotation for all code
5. **Testing:** Use pytest framework for all tests

### Code Style

```python
# Required header format
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module docstring following repository format"""

# Type hints for all functions
def example_function(param: str, count: int = 1) -> list[str]:
    """
    Function description following Google/NumPy style.
    
    Args:
        param: Description of parameter
        count: Description with default value
    
    Returns:
        Description of return value
    """
    # Inline comments for significant code blocks
    result_list = []
    
    # Process parameter according to count
    for i in range(count):
        result_list.append(f"{param}_{i}")
    
    return result_list
```

### Testing Requirements

```python
# Test file structure: tests/test_module.py
import pytest
from common_lib import AnsiColor

def test_ansi_color_creation():
    """Test basic AnsiColor functionality."""
    color = AnsiColor("red", "black")
    assert isinstance(color.code, str)
    assert color.fg_color == "red"
    assert color.bg_color == "black"

def test_ansi_color_styling():
    """Test styling properties."""
    color = AnsiColor("blue")
    assert "1m" in color.bold  # Bold code
    assert "4m" in color.underline  # Underline code
```

## Future Improvements

- **Enhanced error handling:** Comprehensive exception types and validation at v1.0.0
- **Additional CLI features:** Advanced menu navigation and input validation
- **Performance visualization:** Graphical performance reporting capabilities
- **Integration utilities:** Enhanced project integration and automation tools
- **Documentation generation:** Automated API documentation from docstrings
- **Testing expansion:** Comprehensive test coverage and integration testing

## Known Issues

- Error handling and input validation deferred until version 1.0.0 per repository confident design guidelines
- Some edge cases in log file parsing may not be handled (will be addressed in v1.0.0)
- CLI menu lacks advanced navigation features (planned for future releases)
