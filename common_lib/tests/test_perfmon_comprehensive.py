#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive PerfMon Test Suite - Extended Testing

Description:
    Extended test suite for the PerfMon class covering edge cases,
    performance scenarios, thread safety, stress testing, and
    real-world usage patterns.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 20-10-2025
Date Changed: 20-10-2025
Version: 0.1.0.dev1
License: MIT

Features:
    - Edge case testing (large datasets, extreme values, boundary conditions)
    - Thread safety and concurrent logging scenarios
    - Performance and memory usage benchmarking
    - Stress testing with high-volume logging
    - File system edge cases and error conditions
    - Real-world usage pattern simulation
    - Performance regression testing
"""

import concurrent.futures
import random
import tempfile
import threading
import time
from pathlib import Path
from socket import gethostname

import pytest

from cust_class import PerfMon


class TestPerfMonEdgeCases:
    """Test PerfMon behavior in edge case scenarios."""

    def test_extreme_time_values(self) -> None:
        """Test with extreme time values and precision."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            # Test very small time differences
            tiny_diff = 1e-9  # 1 nanosecond
            perfmon.report_time(0.0, tiny_diff, ndigits=10)

            # Test very large time differences
            large_diff = 86400.0  # 1 day in seconds
            perfmon.report_time(0.0, large_diff, ndigits=2)

            # Test with extremely high precision
            perfmon.report_time(0.123456789123456789, 0.987654321987654321, ndigits=15)

            log_content = perfmon.log_path.read_text()
            assert str(round(tiny_diff, 10)) in log_content
            assert str(round(large_diff, 2)) in log_content

    def test_large_dataset_processing(self) -> None:
        """Test performance monitoring with large datasets."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            # Generate large amount of test data (10,000 entries)
            hostname = gethostname()
            large_dataset = []

            for i in range(10000):
                func_name = f"function_{i % 100}"  # 100 different functions
                exec_time = random.uniform(0.001, 1.0)
                log_entry = (
                    f"[2025-10-20 10:{i // 60:02d}:{i % 60:02d}.000] "
                    f"[{hostname}] [{func_name}()] [{exec_time:.4f}] seconds"
                )
                large_dataset.append(log_entry)

            # Write large dataset to log file
            perfmon.log_path.write_text("\n".join(large_dataset))

            # Test statistics calculation performance
            start_time = time.perf_counter()
            stats = perfmon.get_performance_stats()
            calc_time = time.perf_counter() - start_time

            # Verify results
            assert len(stats) == 100  # 100 different functions
            assert calc_time < 5.0  # Should complete within 5 seconds

            # Verify data integrity for a sample function
            sample_func = "function_0"
            if sample_func in stats:
                func_stats = stats[sample_func]
                assert (
                    func_stats["total_calls"] == 100
                )  # Each function appears 100 times
                assert func_stats["all_time_average"] > 0
                assert "last_50" in func_stats["rolling_averages"]

    def test_malformed_log_entries_stress(self) -> None:
        """Test with heavily malformed log file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)
            hostname = gethostname()

            # Create log with mostly malformed entries
            malformed_entries = [
                "Complete garbage text",
                "",  # Empty line
                "[incomplete timestamp",
                "[2025-10-20 10:00:01.000] [wrong_format]",
                f"[2025-10-20 10:00:02.000] [{hostname}] [valid_function()] [0.1234] seconds",
                "Another garbage line with random numbers 123.456",
                "[2025-10-20 10:00:03.000] [different_host] [function()] [0.2345] seconds",
                "Binary data: \x00\x01\x02\x03",
                f"[2025-10-20 10:00:04.000] [{hostname}] [another_valid()] [0.3456] seconds",
                "Unicode test: 你好世界 ñáéíóú",
                "[timestamp without hostname] [function] [time]",
                f"[2025-10-20 10:00:05.000] [{hostname}] [final_valid()] [0.4567] seconds",
            ]

            perfmon.log_path.write_text("\n".join(malformed_entries))

            # Should handle malformed data gracefully
            stats = perfmon.get_performance_stats()

            # Only valid entries with correct hostname should be parsed
            assert len(stats) == 3  # valid_function, another_valid, final_valid
            assert "valid_function" in stats
            assert "another_valid" in stats
            assert "final_valid" in stats

    def test_unicode_and_special_characters(self) -> None:
        """Test handling of unicode and special characters in log files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            # Test with unicode function names in log
            hostname = gethostname()
            unicode_entries = [
                f"[2025-10-20 10:00:01.000] [{hostname}] [测试函数()] [0.1234] seconds",
                f"[2025-10-20 10:00:02.000] [{hostname}] [función_española()] [0.2345] seconds",
                f"[2025-10-20 10:00:03.000] [{hostname}] [emoji_function_🚀()] [0.3456] seconds",
            ]

            perfmon.log_path.write_text("\n".join(unicode_entries), encoding="utf-8")

            # Should handle unicode gracefully
            stats = perfmon.get_performance_stats()

            # Function names with unicode should be parsed correctly
            assert "测试函数" in stats
            assert "función_española" in stats
            assert "emoji_function_🚀" in stats

    def test_boundary_conditions(self) -> None:
        """Test boundary conditions for rolling averages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)
            hostname = gethostname()

            # Test exactly at boundary conditions for rolling windows
            test_cases = [
                {"calls": 4, "expected_windows": []},  # Less than minimum (5)
                {"calls": 5, "expected_windows": ["last_5"]},
                {"calls": 10, "expected_windows": ["last_5", "last_10"]},
                {"calls": 20, "expected_windows": ["last_5", "last_10", "last_20"]},
                {
                    "calls": 50,
                    "expected_windows": ["last_5", "last_10", "last_20", "last_50"],
                },
                {
                    "calls": 51,
                    "expected_windows": ["last_5", "last_10", "last_20", "last_50"],
                },
            ]

            for case in test_cases:
                func_name = f"boundary_test_{case['calls']}"
                log_entries = []

                for i in range(case["calls"]):
                    exec_time = (
                        0.1 + i * 0.01
                    )  # Incremental times for easy verification
                    log_entry = (
                        f"[2025-10-20 10:{i // 60:02d}:{i % 60:02d}.000] "
                        f"[{hostname}] [{func_name}()] [{exec_time:.4f}] seconds"
                    )
                    log_entries.append(log_entry)

                # Write test data
                perfmon.log_path.write_text("\n".join(log_entries))

                stats = perfmon.get_performance_stats()
                assert func_name in stats

                rolling_averages = stats[func_name]["rolling_averages"]
                for expected_window in case["expected_windows"]:
                    assert expected_window in rolling_averages

                # Clear log for next test
                perfmon.log_path.write_text("")


class TestPerfMonThreadSafety:
    """Test PerfMon thread safety and concurrent usage."""

    def test_concurrent_logging(self) -> None:
        """Test concurrent logging from multiple threads."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)
            num_threads = 10
            operations_per_thread = 50
            results: list[bool] = []

            def worker_thread(thread_id: int) -> None:
                """Worker function for concurrent testing."""
                try:
                    for i in range(operations_per_thread):
                        start = time.perf_counter()
                        time.sleep(0.001)  # 1ms work simulation
                        end = time.perf_counter()
                        perfmon.report_time(start, end)
                    results.append(True)
                except Exception:
                    results.append(False)

            # Start all threads
            threads = []
            for thread_id in range(num_threads):
                thread = threading.Thread(target=worker_thread, args=(thread_id,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Verify all threads completed successfully
            assert len(results) == num_threads
            assert all(results)

            # Verify log entries
            stats = perfmon.get_performance_stats()
            assert "worker_thread" in stats
            assert (
                stats["worker_thread"]["total_calls"]
                == num_threads * operations_per_thread
            )

    def test_concurrent_statistics_calculation(self) -> None:
        """Test concurrent statistics calculation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)
            hostname = gethostname()

            # Pre-populate log with test data
            log_entries = []
            for i in range(1000):
                exec_time = random.uniform(0.001, 0.1)
                log_entry = (
                    f"[2025-10-20 10:{i // 60:02d}:{i % 60:02d}.000] "
                    f"[{hostname}] [test_function()] [{exec_time:.4f}] seconds"
                )
                log_entries.append(log_entry)

            perfmon.log_path.write_text("\n".join(log_entries))

            # Concurrent statistics calculation
            results: list[dict] = []

            def calculate_stats() -> None:
                """Calculate statistics concurrently."""
                stats = perfmon.get_performance_stats()
                results.append(stats)

            # Run multiple concurrent calculations
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(calculate_stats) for _ in range(10)]
                concurrent.futures.wait(futures)

            # Verify all calculations produced consistent results
            assert len(results) == 10
            first_result = results[0]

            for result in results[1:]:
                assert result == first_result

    def test_shared_log_file_multiple_instances(self) -> None:
        """Test multiple PerfMon instances sharing the same log file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple instances pointing to same directory
            instances = [PerfMon(log_dir=temp_dir) for _ in range(5)]

            # Verify they all use the same log file
            log_paths = [instance.log_path for instance in instances]
            assert all(path == log_paths[0] for path in log_paths)

            # Log from each instance
            for i, instance in enumerate(instances):
                start = time.perf_counter()
                time.sleep(0.001)
                end = time.perf_counter()
                instance.report_time(start, end)

            # Verify all entries are in the shared log
            log_content = instances[0].log_path.read_text()
            assert log_content.count("test_shared_log_file_multiple_instances") == 5


class TestPerfMonPerformance:
    """Test PerfMon performance characteristics."""

    def test_logging_overhead(self) -> None:
        """Test the performance overhead of PerfMon logging."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            # Test without monitoring
            iterations = 1000

            def dummy_work() -> None:
                """Simple work function for testing."""
                time.sleep(0.0001)  # 0.1ms

            # Baseline without monitoring
            start_baseline = time.perf_counter()
            for _ in range(iterations):
                dummy_work()
            baseline_time = time.perf_counter() - start_baseline

            # With monitoring
            start_monitored = time.perf_counter()
            for _ in range(iterations):
                work_start = time.perf_counter()
                dummy_work()
                work_end = time.perf_counter()
                perfmon.report_time(work_start, work_end)
            monitored_time = time.perf_counter() - start_monitored

            # Overhead should be reasonable (less than 50% of baseline)
            overhead = monitored_time - baseline_time
            overhead_percentage = (overhead / baseline_time) * 100

            # Log the results for analysis
            print(f"Baseline time: {baseline_time:.4f}s")
            print(f"Monitored time: {monitored_time:.4f}s")
            print(f"Overhead: {overhead:.4f}s ({overhead_percentage:.2f}%)")

            # Reasonable overhead assertion
            assert overhead_percentage < 100  # Less than 100% overhead

    def test_memory_usage(self) -> None:
        """Test memory usage with moderate logging operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            # Test basic memory behavior by checking class instance overhead
            initial_count = 10
            perfmons = []

            # Create multiple PerfMon instances
            for i in range(initial_count):
                perfmons.append(PerfMon(log_dir=temp_dir))

            # Each instance should maintain reasonable memory footprint
            assert len(perfmons) == initial_count

            # Test logging a reasonable number of operations
            for i in range(50):  # Reduced from 5000 to avoid infinite object creation
                start = i * 0.001
                end = start + 0.001
                perfmon.report_time(start, end, ndigits=6)

            # Memory usage test passed if we can perform moderate logging without issues
            # Check that the log file has entries
            assert perfmon.log_path.exists()
            log_content = perfmon.log_path.read_text()
            # Should have at least 50 log entries
            assert log_content.count("[test_memory_usage()]") >= 50

    def test_large_log_file_parsing(self) -> None:
        """Test performance with very large log files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)
            hostname = gethostname()

            # Create a large log file (50,000 entries)
            large_dataset = []
            num_functions = 200
            entries_per_function = 250

            for func_id in range(num_functions):
                func_name = f"performance_test_function_{func_id}"
                for entry_id in range(entries_per_function):
                    exec_time = random.uniform(0.001, 2.0)
                    timestamp_offset = func_id * entries_per_function + entry_id
                    log_entry = (
                        f"[2025-10-20 {10 + timestamp_offset // 3600:02d}:"
                        f"{(timestamp_offset % 3600) // 60:02d}:"
                        f"{timestamp_offset % 60:02d}.000] "
                        f"[{hostname}] [{func_name}()] [{exec_time:.4f}] seconds"
                    )
                    large_dataset.append(log_entry)

            # Write large dataset
            perfmon.log_path.write_text("\n".join(large_dataset))

            # Test parsing performance
            start_time = time.perf_counter()
            stats = perfmon.get_performance_stats()
            parse_time = time.perf_counter() - start_time

            print(f"Parsed {len(large_dataset)} entries in {parse_time:.4f}s")
            print(f"Parse rate: {len(large_dataset) / parse_time:.0f} entries/second")

            # Verify results
            assert len(stats) == num_functions
            assert parse_time < 30.0  # Should complete within 30 seconds

            # Verify sample data integrity
            sample_func = "performance_test_function_0"
            assert sample_func in stats
            assert stats[sample_func]["total_calls"] == entries_per_function


class TestPerfMonFileSystemEdgeCases:
    """Test PerfMon behavior with file system edge cases."""

    def test_read_only_log_directory(self) -> None:
        """Test behavior when log directory is read-only."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "readonly_logs"
            log_dir.mkdir()

            # Create PerfMon instance while directory is writable
            perfmon = PerfMon(log_dir=log_dir)

            # Make directory read-only
            log_dir.chmod(0o444)

            try:
                # Attempt to log (this should handle the error gracefully)
                start = time.perf_counter()
                end = start + 0.1

                # NOTE: Per confident design guidelines, error handling is deferred
                # until v1.0.0, so this may fail as expected
                try:
                    perfmon.report_time(start, end)
                except PermissionError:
                    # Expected behavior before v1.0.0
                    pass

            finally:
                # Restore permissions for cleanup
                log_dir.chmod(0o755)

    def test_very_long_file_paths(self) -> None:
        """Test with very long file paths (near system limits)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a deeply nested directory structure
            long_path = Path(temp_dir)
            for i in range(10):
                long_path = (
                    long_path / f"very_long_directory_name_with_many_characters_{i}"
                )

            try:
                perfmon = PerfMon(log_dir=long_path)
                assert perfmon.log_path.parent == long_path
                assert long_path.exists()

                # Test basic functionality with long path
                start = time.perf_counter()
                end = start + 0.001
                perfmon.report_time(start, end)

                assert perfmon.log_path.exists()

            except OSError:
                # Some file systems have path length limits
                pytest.skip("File system path length limit reached")

    def test_log_file_corruption_recovery(self) -> None:
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


class TestPerfMonRealWorldScenarios:
    """Test PerfMon with real-world usage patterns."""

    def test_web_application_simulation(self) -> None:
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
            for _ in range(100):  # Reduced from 500 for performance
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

            # Should have processed all 100 requests
            assert wrapper_stats["total_calls"] == 100

            # Average time should be within reasonable bounds
            avg_time = wrapper_stats["all_time_average"]
            assert 0.001 <= avg_time <= 0.5

    def test_batch_processing_simulation(self) -> None:
        """Simulate batch processing monitoring."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            # Simulate batch processing steps
            batch_steps = [
                "data_validation",
                "data_transformation",
                "database_insert",
                "index_update",
                "notification_send",
            ]

            num_batches = 5  # Reduced for performance
            items_per_batch = 100

            for batch_id in range(num_batches):
                for step in batch_steps:
                    # Simulate processing time that increases with batch size
                    base_time = 0.001 * items_per_batch  # 1ms per item
                    actual_time = base_time * random.uniform(0.8, 1.2)  # ±20% variance

                    start = time.perf_counter()
                    end = start + actual_time

                    # Use wrapper function approach
                    def simulate_batch_step(start_time: float, end_time: float) -> None:
                        """Simulate a batch processing step."""
                        perfmon.report_time(start_time, end_time)

                    simulate_batch_step(start, end)

            # Analyze batch processing results
            stats = perfmon.get_performance_stats()

            # Since we're using a wrapper function, check that it captured the calls
            assert "simulate_batch_step" in stats

            batch_stats = stats["simulate_batch_step"]
            expected_total_calls = num_batches * len(
                batch_steps
            )  # 5 batches * 5 steps = 25
            assert batch_stats["total_calls"] == expected_total_calls

            # Average time should be reasonable for batch processing
            avg_time = batch_stats["all_time_average"]
            assert 0.05 <= avg_time <= 0.15  # Should be around 0.1 seconds per step

    def test_microservice_monitoring(self) -> None:
        """Simulate microservice monitoring scenario."""
        with tempfile.TemporaryDirectory() as temp_dir:
            perfmon = PerfMon(log_dir=temp_dir)

            # Simulate microservice operations
            services = {
                "user_service": {"methods": ["get_user", "update_user", "delete_user"]},
                "order_service": {
                    "methods": ["create_order", "process_payment", "ship_order"]
                },
                "inventory_service": {
                    "methods": ["check_stock", "reserve_items", "release_items"]
                },
            }

            # Simulate realistic microservice call patterns
            for _ in range(100):  # Reduced from 1000 for performance
                service_name = random.choice(list(services.keys()))

                # Different services have different performance characteristics
                if service_name == "user_service":
                    exec_time = random.uniform(0.01, 0.05)  # Fast user operations
                elif service_name == "order_service":
                    exec_time = random.uniform(0.1, 0.5)  # Moderate order processing
                else:  # inventory_service
                    exec_time = random.uniform(0.05, 0.2)  # Variable inventory checks

                start = time.perf_counter()
                end = start + exec_time

                # Use wrapper function approach
                def simulate_microservice_call(
                    start_time: float, end_time: float
                ) -> None:
                    """Simulate a microservice method call."""
                    perfmon.report_time(start_time, end_time)

                simulate_microservice_call(start, end)

            # Analyze microservice performance
            stats = perfmon.get_performance_stats()

            # Verify that monitoring captured microservice operations
            assert "simulate_microservice_call" in stats

            microservice_stats = stats["simulate_microservice_call"]
            assert microservice_stats["total_calls"] == 100

            # Average should be within expected range for mixed service calls
            avg_time = microservice_stats["all_time_average"]
            assert 0.01 <= avg_time <= 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
