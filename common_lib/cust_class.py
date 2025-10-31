#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Repository - Custom Classes Library

Description:
    Library of custom classes for terminal applications and command-line
    interfaces, providing ANSI color formatting, interactive CLI menus,
    and performance monitoring. Designed for creating robust terminal
    applications with proper user interaction patterns and visual formatting.
    This module serves as a foundational component for other projects in
    the repository, implementing common patterns for terminal interaction.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-18-2025
Date Changed: 10-29-2025
License: MIT

Features:
    - AnsiColor class for terminal text formatting and styling with properties
    - CLIMenu class for simple interactive command-line menus with y/n/q prompts
    - PerfMon class for performance monitoring and logging with statistics
    - Python standard library first approach with minimal dependencies
    - Clean architecture with confident design patterns

Requirements:
    - Linux environment
    - Python 3.14+
    - POSIX-compliant terminal for ANSI color support

Known Issues:
    - Limited error handling

Planned Features:
    - Script argument parsing
    - Error handling and input validation at v1.0.0
    - Additional performance monitoring metrics and visualization
"""

import inspect
import logging
import re
import sys
import time
from collections import defaultdict

from pathlib import Path
from socket import gethostname
from typing import Any, Dict, Final


# Version information
__version__ = "0.2.0"


class AnsiColor:
    """
    Build ANSI escape sequences for terminal text formatting and styling.

    Attributes:
        fg_color: Foreground color name for text
        bg_color: Background color name for text
        reset: ANSI reset sequence to clear all formatting
        code: Complete ANSI color code for current configuration

    Public methods:
        bold: Returns ANSI code with bold styling
        dim: Returns ANSI code with dim styling
        underline: Returns ANSI code with underline styling
        blinking: Returns ANSI code with blinking styling
        hidden: Returns ANSI code with hidden text styling

    Private methods:
        _code: Assembles ANSI color code with optional styling
    """

    # Valid ANSI color names
    _valid_colors: Final[set[str]] = {
        "black",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "white",
        "default",
        "bright black",
        "bright red",
        "bright green",
        "bright yellow",
        "bright blue",
        "bright magenta",
        "bright cyan",
        "bright white",
    }

    # ANSI color codes mapping
    _fg_color_codes: Final[dict[str, str]] = {
        "black": "30",
        "red": "31",
        "green": "32",
        "yellow": "33",
        "blue": "34",
        "magenta": "35",
        "cyan": "36",
        "white": "37",
        "default": "39",
        "bright black": "90",
        "bright red": "91",
        "bright green": "92",
        "bright yellow": "93",
        "bright blue": "94",
        "bright magenta": "95",
        "bright cyan": "96",
        "bright white": "97",
    }

    _bg_color_codes: Final[dict[str, str]] = {
        "black": "40",
        "red": "41",
        "green": "42",
        "yellow": "43",
        "blue": "44",
        "magenta": "45",
        "cyan": "46",
        "white": "47",
        "default": "49",
        "bright black": "100",
        "bright red": "101",
        "bright green": "102",
        "bright yellow": "103",
        "bright blue": "104",
        "bright magenta": "105",
        "bright cyan": "106",
        "bright white": "107",
    }

    def __init__(
        self,
        fg_color: str = "default",
        bg_color: str = "default",
    ) -> None:
        """
        Initialize ANSI color formatter.

        Args:
            fg_color: Foreground color name
            bg_color: Background color name

        Returns:
            None
        """
        # Normalize input colors to lowercase and strip whitespace
        self.fg_color: str = fg_color.lower().strip()
        self.bg_color: str = bg_color.lower().strip()

        # Set ANSI reset sequence constant for clearing all formatting
        self.reset: Final[str] = "\u001b[0m"
        # NOTE: Validation deferred until v1.0.0 per confident design guidelines

        # Generate complete ANSI escape sequence for current color configuration
        self.code: str = self._code()

    def __str__(self) -> str:
        return self.code

    def _code(self, style_code: str = "") -> str:
        """
        Assemble ANSI color code with optional styling.

        Args:
            style_code: Optional ANSI style code

        Returns:
            Complete ANSI escape sequence
        """
        # Look up ANSI codes for foreground and background colors
        fg_code = self._fg_color_codes[self.fg_color]
        bg_code = self._bg_color_codes[self.bg_color]

        # Build complete ANSI escape sequence with optional style code
        if style_code:
            return f"\u001b[{fg_code};{bg_code};{style_code}m"
        return f"\u001b[{fg_code};{bg_code}m"

    @property
    def bold(self) -> str:
        """
        Get ANSI color code with bold styling.

        Args:
            None

        Returns:
            ANSI escape sequence with bold formatting
        """
        return self._code("1")

    @property
    def dim(self) -> str:
        """
        Get ANSI color code with dim styling.

        Args:
            None

        Returns:
            ANSI escape sequence with dim formatting
        """
        return self._code("2")

    @property
    def underline(self) -> str:
        """
        Get ANSI color code with underline styling.

        Args:
            None

        Returns:
            ANSI escape sequence with underline formatting
        """
        return self._code("4")

    @property
    def blinking(self) -> str:
        """
        Get ANSI color code with blinking styling.

        Args:
            None

        Returns:
            ANSI escape sequence with blinking formatting
        """
        return self._code("5")

    @property
    def hidden(self) -> str:
        """
        Get ANSI color code with hidden text styling.

        Args:
            None

        Returns:
            ANSI escape sequence with hidden text formatting
        """
        return self._code("8")


class CLIMenu:
    """
    Simple command-line interface menu utility class.

    Attributes:
        None

    Public methods:
        run: Display menu options and handle user input selection
        ynq: Display yes/no/quit prompt and handle user response

    Private methods:
        None
    """

    def run(
        self,
        menu_options: dict[str, Any],
    ) -> None:
        """
        Display menu options with numbered selection and handle user input.

        Args:
            menu_options: Dictionary mapping option names to functions

        Returns:
            None
        """
        # Display numbered menu options to user
        print("\nMenu Options:")
        for i, option in enumerate(menu_options.keys(), 1):
            print(f"{i}. {option}")

        # Get user selection and execute corresponding function
        while True:
            try:
                choice = input("\nSelect option (number): ").strip()
                option_num = int(choice)

                # Validate selection is within range
                if 1 <= option_num <= len(menu_options):
                    option_name = list(menu_options.keys())[option_num - 1]
                    selected_function = menu_options[option_name]
                    selected_function()
                    break
                else:
                    print(f"Invalid selection. Please choose 1-{len(menu_options)}")

            except (ValueError, KeyboardInterrupt, EOFError):
                print("\nInvalid input or quit by user. Exiting...")
                sys.exit(0)

    def ynq(
        self,
        prompt: str,
    ) -> bool:
        """
        Display yes/no/quit prompt and handle user input.

        Args:
            prompt: Question to display to user

        Returns:
            True for 'yes', False for 'no'. Exits program on 'quit'
        """
        # Loop until valid response is entered
        while True:
            try:
                # Display prompt and get user input
                response = input(f"{prompt.strip()} (y/n/q) ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                # Handle Ctrl+C or EOF gracefully
                print("\nQuit by user. Exiting...")
                sys.exit(0)

            # Process user response and return appropriate boolean or exit
            if response in ("y", "yes"):
                return True
            elif response in ("n", "no"):
                return False
            elif response in ("q", "quit"):
                print("Quit by user. Exiting...")
                sys.exit(0)
            else:
                print("Invalid entry. Try again.")


class PerfMon:
    """
    Performance monitoring and logging utility class.

    Attributes:
        hostname: System hostname for log identification
        log_path: Path to the performance log file
        logger: Logger instance for writing performance data

    Public methods:
        log_averages: Log calculated performance averages to file
        get_performance_stats: Get comprehensive performance statistics
        log_raw_line: Write single line to log without timestamp
        log_separator: Write separator line without timestamp
        log_section_header: Write section header without timestamp
        report_time: Report execution time between two measurements

    Private methods:
        _setup_logging: Configure logging handler and formatter
        _calculate_averages: Calculate performance statistics from log file
    """

    # Color constants using AnsiColor class
    _reset = AnsiColor().reset
    _default = AnsiColor("default")
    _black = AnsiColor("black")
    _blue = AnsiColor("blue")
    _b_blue = AnsiColor("bright blue")
    _red = AnsiColor("red")
    _b_red = AnsiColor("bright red")
    _green = AnsiColor("green")
    _b_green = AnsiColor("bright green")
    _yellow = AnsiColor("yellow")
    _b_yellow = AnsiColor("bright yellow")
    _magenta = AnsiColor("magenta")
    _b_magenta = AnsiColor("bright magenta")
    _cyan = AnsiColor("cyan")
    _b_cyan = AnsiColor("bright cyan")
    _white = AnsiColor("white")
    _b_white = AnsiColor("bright white")

    def __init__(self, log_dir: Path | str | None = None) -> None:
        """
        Initialize performance monitor with logging setup.

        Args:
            log_dir: Directory to store log file

        Returns:
            None
        """
        if log_dir:
            log_dir = Path(log_dir)
        else:
            # Determine caller's project directory by finding the calling module
            current_frame = inspect.currentframe()
            if current_frame and current_frame.f_back:
                caller_frame = current_frame.f_back
                caller_file = Path(caller_frame.f_code.co_filename)
                # Find project root by looking for the directory containing the caller
                project_root = caller_file.parent
                log_dir = project_root / "logs"
            else:
                # Fallback to current working directory if frame inspection fails
                log_dir = Path.cwd() / "logs"

        # Create log directory if it doesn't exist
        log_dir.mkdir(parents=True, exist_ok=True)

        # Set hostname and log file path for this performance monitor instance
        self.hostname: str = gethostname()
        self.log_path = log_dir / f"{self.hostname}_perfmon.log"
        self.logger: logging.Logger  # Will be set in _setup_logging

        # Configure logging handler and formatter
        self._setup_logging()

    def _setup_logging(self) -> None:
        """
        Setup logging to a file with proper handler configuration.

        Args:
            None

        Returns:
            None
        """
        # Create a logger specific to this PerfMon instance to avoid conflicts
        self.logger = logging.getLogger(f"perfmon_{id(self)}")
        self.logger.setLevel(logging.INFO)

        # Clear any existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Create file handler for writing to log file
        file_handler = logging.FileHandler(str(self.log_path), mode="a")
        file_handler.setLevel(logging.INFO)

        # Create formatter with timestamp and milliseconds
        formatter = logging.Formatter(
            "[{asctime}.{msecs:03.0f}] {message}",
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{",
        )
        file_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(file_handler)

    def _calculate_averages(self) -> Dict[str, Any]:
        """
        Calculate performance statistics from log file.

        Args:
            None

        Returns:
            Dictionary with function performance statistics
        """
        function_times: Dict[str, Any] = {}

        # Check if log file exists before attempting to read
        if not self.log_path.exists():
            return function_times

        # Pattern to match log entries: [timestamp] [hostname] [function_name()] [time] seconds
        # Only matches lines with the expected hostname to ensure log integrity
        # Uses [^\[\]]+ to match any characters except brackets in function name
        log_pattern = re.compile(
            rf"\[.*?\] \[{re.escape(self.hostname)}\] \[([^\[\]]+)\(\)\] \[(\d+\.?\d*)\] seconds"
        )

        # Store all times for each function to calculate averages
        function_data: Dict[str, list[float]] = defaultdict(list)

        # Read and parse log file
        with self.log_path.open("r", encoding="utf-8", errors="replace") as log_file:
            for line in log_file:
                # Skip lines with replacement characters (from corrupted data)
                line = line.strip()
                if "�" in line:
                    continue

                # Parse log line and extract function name and execution time
                match = log_pattern.search(line)
                if match:
                    function_name = match.group(1)
                    execution_time = float(match.group(2))
                    function_data[function_name].append(execution_time)

        # Calculate averages for each function with different rolling windows
        rolling_window_sizes = [5, 10, 20, 50]  # Common rolling average windows

        for function_name, times in function_data.items():
            if not times:
                continue

            # Calculate all-time average
            all_time_avg = sum(times) / len(times)

            # Calculate rolling averages for different window sizes
            rolling_averages: Dict[str, float] = {}
            for window_size in rolling_window_sizes:
                if len(times) >= window_size:
                    recent_times = times[-window_size:]
                    rolling_avg = sum(recent_times) / len(recent_times)
                    rolling_averages[f"last_{window_size}"] = round(rolling_avg, 4)

            # Store comprehensive statistics for this function
            function_times[function_name] = {
                "all_time_average": round(all_time_avg, 4),
                "total_calls": len(times),
                "rolling_averages": rolling_averages,
            }

        return function_times

    def log_averages(self) -> None:
        """
        Log calculated performance averages to file.

        Args:
            None

        Returns:
            None
        """
        # Calculate comprehensive performance statistics
        function_stats = self._calculate_averages()

        # Write performance summary to log file with formatting
        self.log_raw_line("")
        self.logger.info("Performance Averages Summary:")
        for function_name, stats in function_stats.items():
            self.logger.info(
                f"  Function: {function_name} | "
                f"All-Time Average: [{stats['all_time_average']}] | "
                f"Total Calls: {stats['total_calls']} | "
                f"Rolling Averages: {stats['rolling_averages']}"
            )
        self.log_raw_line("")

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive performance statistics for all logged functions.

        Args:
            None

        Returns:
            Dictionary with function performance statistics
        """
        return self._calculate_averages()

    def log_raw_line(self, message: str) -> None:
        """
        Write single line to log file without timestamp formatting.

        Args:
            message: Text to write to log file

        Returns:
            None
        """
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")

    def log_separator(self, separator: str = "=" * 50) -> None:
        """
        Write separator line without timestamp.

        Args:
            separator: Separator text to write

        Returns:
            None
        """
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{separator}\n")

    def log_section_header(self, title: str) -> None:
        """
        Write section header without timestamp.

        Args:
            title: Section title text

        Returns:
            None
        """
        header = f"\n{'=' * 20} {title.upper()} {'=' * 20}\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(header)

    def report_time(
        self,
        start_time: float,
        end_time: float,
        ndigits: int = 4,
    ) -> None:
        """
        Report execution time between two time.perf_counter() calls.

        Args:
            start_time: Starting time from time.perf_counter()
            end_time: Ending time from time.perf_counter()
            ndigits: Number of decimal places for time difference

        Returns:
            None
        """
        # Calculate execution time difference
        start = start_time
        end = end_time
        diff = round((end - start), ndigits)

        # Get the current frame object to determine calling function name
        current_frame = inspect.currentframe()
        parent_function_name = "unknown"

        # Extract parent function name from call stack for logging context
        if current_frame and current_frame.f_back:
            parent_frame = current_frame.f_back
            parent_code = parent_frame.f_code
            parent_function_name = parent_code.co_name

        # Log performance data and display colored output to terminal
        self.logger.info(
            f"[{self.hostname}] [{parent_function_name}()] [{diff}] seconds"
        )
        print(
            f"{self._green.bold}{parent_function_name}(){self._reset} took "
            f"{self._green.bold}{diff}{self._reset} seconds"
        )
