#!/usr/bin/env python3
"""
Description:
    Comprehensive test runner for PerfMon class without pytest dependency
Author:
    Chris
Email:
    N/A
GitHub:
    N/A
Date Created:
    2025-01-10
Date Changed:
    2025-01-10
Version:
    1.0.0
License:
    MIT
Features:
    Run all PerfMon tests including original and comprehensive suites
"""

import sys
import traceback
from typing import Callable
import tempfile
import time
import random
import threading
from socket import gethostname

from cust_class import PerfMon


class TestRunner:
    """Simple test runner to replace pytest."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def run_test(self, test_func: Callable, test_name: str) -> None:
        """Run a single test function."""
        try:
            print(f"Running {test_name}...")
            test_func()
            print(f"✓ {test_name} PASSED")
            self.passed += 1
        except Exception as e:
            print(f"✗ {test_name} FAILED: {e}")
            self.failed += 1
            self.errors.append(f"{test_name}: {e}\n{traceback.format_exc()}")

    def report(self) -> None:
        """Print test results summary."""
        total = self.passed + self.failed
        print(f"\n{'=' * 60}")
        print(f"Test Results: {self.passed}/{total} passed")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")

        if self.errors:
            print("\nFailure Details:")
            for error in self.errors:
                print(f"{'-' * 40}\n{error}")

        print(f"{'=' * 60}")


# Original test functions (simplified from test_perfmon.py)
def test_init_with_default_log_dir() -> None:
    """Test PerfMon initialization with default log directory."""
    perfmon = PerfMon()
    # Check that log_path points to a logs directory and ends with hostname_perfmon.log
    assert "logs" in str(perfmon.log_path)
    assert str(perfmon.log_path).endswith("_perfmon.log")


def test_init_with_custom_log_dir() -> None:
    """Test PerfMon initialization with custom log directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        perfmon = PerfMon(log_dir=temp_dir)
        # Check that log_path is in the specified temp directory
        assert str(perfmon.log_path).startswith(temp_dir)
        assert str(perfmon.log_path).endswith("_perfmon.log")


def test_logging_functionality() -> None:
    """Test basic logging functionality."""
    with tempfile.TemporaryDirectory() as temp_dir:
        perfmon = PerfMon(log_dir=temp_dir)

        # Simulate a function call
        start_time = time.perf_counter()
        time.sleep(0.01)  # Small sleep to ensure measurable time
        end_time = time.perf_counter()

        perfmon.report_time(start_time, end_time)

        # Check that log file was created and contains expected content
        assert perfmon.log_path.exists()
        content = perfmon.log_path.read_text()
        assert "test_logging_functionality" in content


def test_get_performance_stats() -> None:
    """Test performance statistics retrieval."""
    with tempfile.TemporaryDirectory() as temp_dir:
        perfmon = PerfMon(log_dir=temp_dir)

        # Generate some test data
        start_time = time.perf_counter()
        time.sleep(0.01)
        end_time = time.perf_counter()

        perfmon.report_time(start_time, end_time)

        stats = perfmon.get_performance_stats()
        assert "test_get_performance_stats" in stats
        assert "total_calls" in stats["test_get_performance_stats"]
        assert "all_time_average" in stats["test_get_performance_stats"]


# Comprehensive test functions
def test_concurrent_logging() -> None:
    """Test concurrent logging from multiple threads."""
    with tempfile.TemporaryDirectory() as temp_dir:
        perfmon = PerfMon(log_dir=temp_dir)

        def worker_thread(thread_id: int) -> None:
            """Worker function for thread testing."""
            for i in range(10):
                start = time.perf_counter()
                time.sleep(0.001)  # Small sleep
                end = time.perf_counter()
                perfmon.report_time(start, end)

        # Start multiple threads
        threads = []
        num_threads = 5
        for i in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all calls were logged
        stats = perfmon.get_performance_stats()
        assert "worker_thread" in stats
        assert stats["worker_thread"]["total_calls"] == num_threads * 10


def test_unicode_function_names() -> None:
    """Test handling of unicode function names."""
    with tempfile.TemporaryDirectory() as temp_dir:
        perfmon = PerfMon(log_dir=temp_dir)

        # Create log entries with unicode function names
        hostname = gethostname()
        unicode_entries = [
            f"[2025-10-20 10:00:01.000] [{hostname}] [函数_测试()] [0.1234] seconds",
            f"[2025-10-20 10:00:02.000] [{hostname}] [función_prueba()] [0.2345] seconds",
            f"[2025-10-20 10:00:03.000] [{hostname}] [тест_функция()] [0.3456] seconds",
            f"[2025-10-20 10:00:04.000] [{hostname}] [🚀_rocket_function()] [0.4567] seconds",
        ]

        # Write unicode entries to log file
        perfmon.log_path.write_text("\n".join(unicode_entries) + "\n", encoding="utf-8")

        # Parse and verify unicode function names
        stats = perfmon.get_performance_stats()

        expected_functions = [
            "函数_测试",
            "función_prueba",
            "тест_функция",
            "🚀_rocket_function",
        ]
        for func_name in expected_functions:
            assert func_name in stats, (
                f"Unicode function '{func_name}' not found in stats"
            )


def test_corruption_recovery() -> None:
    """Test recovery from corrupted log files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        perfmon = PerfMon(log_dir=temp_dir)
        hostname = gethostname()

        # Create valid log entries
        valid_entries = [
            f"[2025-10-20 10:00:01.000] [{hostname}] [function_a()] [0.1234] seconds",
            f"[2025-10-20 10:00:02.000] [{hostname}] [function_b()] [0.2345] seconds",
        ]

        # Write valid entries
        perfmon.log_path.write_text("\n".join(valid_entries) + "\n")

        # Simulate corruption by appending binary data on a new line
        with perfmon.log_path.open("ab") as f:
            f.write(b"\x00\x01\x02\x03\xff\xfe\xfd\n")

        # Add more valid entries after corruption
        with perfmon.log_path.open("a", encoding="utf-8", errors="replace") as f:
            f.write(
                f"[2025-10-20 10:00:03.000] [{hostname}] [function_c()] [0.3456] seconds\n"
            )

        # Should handle corruption gracefully and parse valid entries
        stats = perfmon.get_performance_stats()

        assert "function_a" in stats
        assert "function_b" in stats
        assert "function_c" in stats
        assert len(stats) == 3


def test_web_application_simulation() -> None:
    """Simulate web application request monitoring."""
    with tempfile.TemporaryDirectory() as temp_dir:
        perfmon = PerfMon(log_dir=temp_dir)

        # Simulate different types of web requests
        request_types = [
            {"name": "database_query", "avg_time": 0.05, "variance": 0.02},
            {"name": "api_call", "avg_time": 0.15, "variance": 0.05},
            {"name": "file_processing", "avg_time": 0.30, "variance": 0.10},
            {"name": "cache_lookup", "avg_time": 0.001, "variance": 0.0005},
        ]

        # Simulate realistic request pattern
        for _ in range(50):  # Reduced for performance
            request_type = random.choice(request_types)

            # Simulate variable execution time
            base_time = request_type["avg_time"]
            variance = request_type["variance"]
            actual_time = max(0.0001, random.gauss(base_time, variance))

            start = time.perf_counter()
            end = start + actual_time

            # Use wrapper function approach
            def simulate_function_call(start_time: float, end_time: float) -> None:
                """Simulate a function call with a specific name."""
                perfmon.report_time(start_time, end_time)

            simulate_function_call(start, end)

        # Analyze results
        stats = perfmon.get_performance_stats()

        # Since we're using a wrapper function, check that it captured the calls
        assert "simulate_function_call" in stats
        wrapper_stats = stats["simulate_function_call"]

        # Should have processed all 50 requests
        assert wrapper_stats["total_calls"] == 50

        # Average time should be within reasonable bounds
        avg_time = wrapper_stats["all_time_average"]
        assert 0.001 <= avg_time <= 0.5


def test_performance_with_many_functions() -> None:
    """Test performance with many different function names."""
    with tempfile.TemporaryDirectory() as temp_dir:
        perfmon = PerfMon(log_dir=temp_dir)

        # Generate many different function calls
        for i in range(50):  # Reduced for performance

            def test_function(func_id: int) -> None:
                start = time.perf_counter()
                time.sleep(0.001)  # Small consistent sleep
                end = time.perf_counter()
                perfmon.report_time(start, end)

            test_function(i)

        # Verify statistics
        stats = perfmon.get_performance_stats()
        assert "test_function" in stats
        assert stats["test_function"]["total_calls"] == 50


def main() -> None:
    """Main test runner."""
    runner = TestRunner()

    print("🧪 PerfMon Comprehensive Test Suite")
    print("=" * 60)

    # Original tests
    runner.run_test(test_init_with_default_log_dir, "test_init_with_default_log_dir")
    runner.run_test(test_init_with_custom_log_dir, "test_init_with_custom_log_dir")
    runner.run_test(test_logging_functionality, "test_logging_functionality")
    runner.run_test(test_get_performance_stats, "test_get_performance_stats")

    # Comprehensive tests
    runner.run_test(test_concurrent_logging, "test_concurrent_logging")
    runner.run_test(test_unicode_function_names, "test_unicode_function_names")
    runner.run_test(test_corruption_recovery, "test_corruption_recovery")
    runner.run_test(test_web_application_simulation, "test_web_application_simulation")
    runner.run_test(
        test_performance_with_many_functions, "test_performance_with_many_functions"
    )

    # Report results
    runner.report()

    # Exit with appropriate code
    sys.exit(0 if runner.failed == 0 else 1)


if __name__ == "__main__":
    main()
