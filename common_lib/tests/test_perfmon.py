#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PerfMon Class Test Suite

Description:
    Comprehensive test suite for the PerfMon class to verify performance
    monitoring functionality including logging, statistics calculation,
    and average computation for function execution times.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 20-10-2025
Date Changed: 20-10-2025
Version: 0.1.0.dev1
License: MIT

Features:
    - Test PerfMon initialization with default and custom log directories
    - Test performance time reporting and logging functionality
    - Test average calculation and rolling averages computation
    - Test log file parsing and statistics generation
    - Test edge cases and error conditions
    - Mock scenarios for isolated testing
    - Test new raw logging methods (log_raw_line, log_separator, log_section_header)
"""

import tempfile
import time
from pathlib import Path
from socket import gethostname
from unittest.mock import patch, MagicMock

import pytest

from cust_class import PerfMon


class TestPerfMonInitialization:
    """Test PerfMon class initialization and setup."""

    def test_init_with_default_log_dir(self) -> None:
        """Test initialization uses caller's directory when no log_dir specified."""
        perfmon = PerfMon()

        # Should use the directory where this test file is located
        expected_log_dir = Path(__file__).parent / "logs"
        assert perfmon.log_path.parent == expected_log_dir
        assert expected_log_dir.exists()
        assert perfmon.hostname == gethostname()
        assert perfmon.log_path.name == f"{gethostname()}_perfmon.log"

    def test_init_with_custom_log_dir_string(self) -> None:
        """Test initialization with custom log directory as string."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_log_dir = f"{temp_dir}/custom_logs"

            perfmon = PerfMon(log_dir=custom_log_dir)

            expected_log_path = Path(custom_log_dir) / f"{gethostname()}_perfmon.log"
            assert perfmon.log_path == expected_log_path
            assert Path(custom_log_dir).exists()

    def test_init_with_custom_log_dir_path(self) -> None:
        """Test initialization with custom log directory as Path object."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_log_dir = Path(temp_dir) / "custom_logs"

            perfmon = PerfMon(log_dir=custom_log_dir)

            expected_log_path = custom_log_dir / f"{gethostname()}_perfmon.log"
            assert perfmon.log_path == expected_log_path
            assert custom_log_dir.exists()

    def test_log_directory_creation(self) -> None:
        """Test that log directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_log_dir = Path(temp_dir) / "nested" / "log" / "directory"

            # Ensure directory doesn't exist initially
            assert not nested_log_dir.exists()

            perfmon = PerfMon(log_dir=nested_log_dir)

            # Verify directory was created
            assert nested_log_dir.exists()
            assert perfmon.log_path.parent == nested_log_dir


class TestPerfMonLogging:
    """Test PerfMon logging functionality."""

    def test_report_time_basic(self) -> None:
        """Test basic time reporting functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            start_time = time.perf_counter()
            time.sleep(0.01)  # Small delay for measurable difference
            end_time = time.perf_counter()

            # Capture stdout to verify print output
            import sys
            from io import StringIO

            captured_output = StringIO()
            sys.stdout = captured_output

            try:
                perfmon.report_time(start_time, end_time)
                output = captured_output.getvalue()

                # Verify console output contains function name and time
                assert "test_report_time_basic()" in output
                assert "seconds" in output

                # Verify log file was created and contains entry
                assert perfmon.log_path.exists()
                log_content = perfmon.log_path.read_text()
                assert "test_report_time_basic()" in log_content
                assert gethostname() in log_content
                assert "seconds" in log_content

            finally:
                sys.stdout = sys.__stdout__

    def test_log_raw_line(self) -> None:
        """Test log_raw_line method writes without timestamp formatting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            test_message = "This is a raw log line"
            perfmon.log_raw_line(test_message)

            log_content = perfmon.log_path.read_text()
            lines = log_content.strip().split("\n")

            # Should find the raw message without timestamp formatting
            assert test_message in lines
            # Verify it's written as-is (not within a timestamp format)
            raw_line = next(line for line in lines if line == test_message)
            assert raw_line == test_message

    def test_log_separator(self) -> None:
        """Test log_separator method writes separator lines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            # Test default separator
            perfmon.log_separator()

            # Test custom separator
            custom_sep = "-" * 30
            perfmon.log_separator(custom_sep)

            log_content = perfmon.log_path.read_text()
            lines = log_content.strip().split("\n")

            # Should contain both separators
            assert "=" * 50 in lines
            assert custom_sep in lines

    def test_log_section_header(self) -> None:
        """Test log_section_header method writes formatted headers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            test_title = "Test Section"
            perfmon.log_section_header(test_title)

            log_content = perfmon.log_path.read_text()

            # Should contain the formatted header with uppercase title
            assert "TEST SECTION" in log_content
            assert "=" * 20 in log_content

    def test_report_time_precision(self) -> None:
        """Test time reporting with different precision values."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            start_time = 1000.123456789
            end_time = 1001.987654321

            # Test different precision values
            for ndigits in [1, 2, 4, 6]:
                perfmon.report_time(start_time, end_time, ndigits=ndigits)

                log_content = perfmon.log_path.read_text()
                expected_diff = round(end_time - start_time, ndigits)
                assert f"[{expected_diff}]" in log_content

    @patch("inspect.currentframe")
    def test_report_time_unknown_function(self, mock_frame: MagicMock) -> None:
        """Test behavior when function name cannot be determined."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            # Mock frame to return None
            mock_frame.return_value = None

            start_time = time.perf_counter()
            end_time = start_time + 0.1

            perfmon.report_time(start_time, end_time)

            log_content = perfmon.log_path.read_text()
            assert "unknown()" in log_content


class TestPerfMonStatistics:
    """Test PerfMon statistics and average calculation functionality."""

    def test_calculate_averages_empty_log(self) -> None:
        """Test average calculation with empty or non-existent log file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            # Test with non-existent log file
            stats = perfmon.get_performance_stats()
            assert stats == {}

            # Test with empty log file
            perfmon.log_path.touch()
            stats = perfmon.get_performance_stats()
            assert stats == {}

    def test_calculate_averages_single_function(self) -> None:
        """Test average calculation with single function multiple calls."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)
            hostname = gethostname()

            # Create test log entries
            test_times = [0.1234, 0.2345, 0.3456, 0.4567, 0.5678]
            log_entries = []

            for i, exec_time in enumerate(test_times):
                log_entry = (
                    f"[2025-10-20 10:00:{i:02d}.000] "
                    f"[{hostname}] [test_function()] [{exec_time}] seconds"
                )
                log_entries.append(log_entry)

            perfmon.log_path.write_text("\n".join(log_entries))

            stats = perfmon.get_performance_stats()

            assert "test_function" in stats
            function_stats = stats["test_function"]

            # Verify all-time average
            expected_avg = sum(test_times) / len(test_times)
            assert function_stats["all_time_average"] == round(expected_avg, 4)
            assert function_stats["total_calls"] == len(test_times)

            # Verify rolling averages
            rolling_avgs = function_stats["rolling_averages"]
            assert "last_5" in rolling_avgs
            assert rolling_avgs["last_5"] == round(expected_avg, 4)  # All 5 values

    def test_calculate_averages_multiple_functions(self) -> None:
        """Test average calculation with multiple functions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)
            hostname = gethostname()

            # Create test data for multiple functions
            test_data = {
                "function_a": [0.1, 0.2, 0.3],
                "function_b": [0.5, 0.6],
                "function_c": [1.0, 1.1, 1.2, 1.3, 1.4, 1.5],
            }

            log_entries = []
            for func_name, times in test_data.items():
                for i, exec_time in enumerate(times):
                    log_entry = (
                        f"[2025-10-20 10:00:{i:02d}.000] "
                        f"[{hostname}] [{func_name}()] [{exec_time}] seconds"
                    )
                    log_entries.append(log_entry)

            perfmon.log_path.write_text("\n".join(log_entries))

            stats = perfmon.get_performance_stats()

            # Verify all functions are present
            for func_name in test_data.keys():
                assert func_name in stats

            # Verify function_a statistics
            func_a_stats = stats["function_a"]
            assert func_a_stats["total_calls"] == 3
            assert func_a_stats["all_time_average"] == 0.2  # (0.1+0.2+0.3)/3

            # Verify function_c has rolling averages (6 calls >= 5)
            func_c_stats = stats["function_c"]
            assert "last_5" in func_c_stats["rolling_averages"]

    def test_calculate_averages_rolling_windows(self) -> None:
        """Test rolling average calculations for different window sizes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)
            hostname = gethostname()

            # Create 60 test entries to test all rolling windows
            test_times = [i * 0.01 for i in range(1, 61)]  # 0.01, 0.02, ..., 0.60

            log_entries = []
            for i, exec_time in enumerate(test_times):
                log_entry = (
                    f"[2025-10-20 10:00:{i:02d}.000] "
                    f"[{hostname}] [test_function()] [{exec_time}] seconds"
                )
                log_entries.append(log_entry)

            perfmon.log_path.write_text("\n".join(log_entries))

            stats = perfmon.get_performance_stats()
            function_stats = stats["test_function"]
            rolling_avgs = function_stats["rolling_averages"]

            # Verify all rolling windows are present
            assert "last_5" in rolling_avgs
            assert "last_10" in rolling_avgs
            assert "last_20" in rolling_avgs
            assert "last_50" in rolling_avgs

            # Verify last_5 calculation (last 5 values: 0.56, 0.57, 0.58, 0.59, 0.60)
            expected_last_5 = sum(test_times[-5:]) / 5
            assert rolling_avgs["last_5"] == round(expected_last_5, 4)

    def test_calculate_averages_invalid_log_entries(self) -> None:
        """Test handling of invalid or malformed log entries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)
            hostname = gethostname()

            # Mix valid and invalid log entries
            log_entries = [
                f"[2025-10-20 10:00:01.000] [{hostname}] [valid_function()] [0.1234] seconds",
                "Invalid log entry without proper format",
                "[2025-10-20 10:00:02.000] [wrong_hostname] [function()] [0.2345] seconds",
                f"[2025-10-20 10:00:03.000] [{hostname}] [another_valid()] [0.3456] seconds",
                "Another invalid entry",
                f"[2025-10-20 10:00:04.000] [{hostname}] [valid_function()] [0.4567] seconds",
            ]

            perfmon.log_path.write_text("\n".join(log_entries))

            stats = perfmon.get_performance_stats()

            # Should only parse valid entries with correct hostname
            assert "valid_function" in stats
            assert "another_valid" in stats
            assert stats["valid_function"]["total_calls"] == 2
            assert stats["another_valid"]["total_calls"] == 1

    def test_log_averages_functionality(self) -> None:
        """Test the log_averages method writes statistics to log file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)
            hostname = gethostname()

            # Create some test data
            log_entries = [
                f"[2025-10-20 10:00:01.000] [{hostname}] [test_function()] [0.1234] seconds",
                f"[2025-10-20 10:00:02.000] [{hostname}] [test_function()] [0.2345] seconds",
            ]

            perfmon.log_path.write_text("\n".join(log_entries))

            # Call log_averages
            perfmon.log_averages()

            # Read log file and verify summary was added
            log_content = perfmon.log_path.read_text()
            assert "Performance Averages Summary:" in log_content
            assert "Function: test_function" in log_content
            assert "All-Time Average:" in log_content
            assert "Total Calls:" in log_content

    def test_log_averages_uses_raw_line(self) -> None:
        """Test that log_averages uses log_raw_line for blank lines."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)
            hostname = gethostname()

            # Create some test data
            log_entries = [
                f"[2025-10-20 10:00:01.000] [{hostname}] [test_function()] [0.1234] seconds",
            ]

            perfmon.log_path.write_text("\n".join(log_entries))

            # Call log_averages
            perfmon.log_averages()

            # Read log file and verify blank lines are present without timestamps
            log_content = perfmon.log_path.read_text()
            lines = log_content.split("\n")

            # Should have blank lines without timestamp formatting
            blank_lines = [line for line in lines if line == ""]
            assert len(blank_lines) >= 2  # Before and after summary


class TestPerfMonIntegration:
    """Integration tests for PerfMon class."""

    def test_real_function_timing(self) -> None:
        """Test timing actual function execution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            def timed_function() -> None:
                """Sample function to time."""
                start = time.perf_counter()
                time.sleep(0.01)  # Simulate work
                end = time.perf_counter()
                perfmon.report_time(start, end)

            # Execute function multiple times
            for _ in range(3):
                timed_function()

            # Verify statistics
            stats = perfmon.get_performance_stats()
            assert "timed_function" in stats
            assert stats["timed_function"]["total_calls"] == 3
            assert stats["timed_function"]["all_time_average"] > 0.01

    def test_concurrent_logging(self) -> None:
        """Test behavior with concurrent logging scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon1 = PerfMon(log_dir=temp_dir)
            perfmon2 = PerfMon(log_dir=temp_dir)  # Same log directory

            # Both should use the same log file
            assert perfmon1.log_path == perfmon2.log_path

            # Log from both instances
            start = time.perf_counter()
            end = start + 0.1

            perfmon1.report_time(start, end)
            perfmon2.report_time(start, end + 0.1)

            # Verify both entries are in the log
            log_content = perfmon1.log_path.read_text()
            assert log_content.count("test_concurrent_logging()") == 2

    def test_mixed_logging_methods(self) -> None:
        """Test using both timestamp and raw logging methods together."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            # Use raw logging methods
            perfmon.log_section_header("Test Section")
            perfmon.log_raw_line("Raw message")
            perfmon.log_separator()

            # Use timestamp logging
            start = time.perf_counter()
            end = start + 0.1
            perfmon.report_time(start, end)

            # Verify mixed content
            log_content = perfmon.log_path.read_text()
            assert "TEST SECTION" in log_content
            assert "Raw message" in log_content
            assert "=" * 50 in log_content
            assert "test_mixed_logging_methods()" in log_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
