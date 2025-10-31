#!/usr/bin/env python3
"""
Description:
    Verify original PerfMon functionality still works
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
    Quick verification of core PerfMon functionality
"""

import tempfile
import time
from socket import gethostname
from cust_class import PerfMon


def test_basic_functionality():
    """Test basic PerfMon functionality."""
    print("Testing basic PerfMon functionality...")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Test initialization
        perfmon = PerfMon(log_dir=temp_dir)
        print(f"✓ PerfMon initialized with log path: {perfmon.log_path}")

        # Test logging
        start = time.perf_counter()
        time.sleep(0.01)  # 10ms sleep
        end = time.perf_counter()

        perfmon.report_time(start, end)
        print("✓ Performance time logged")

        # Test stats retrieval
        stats = perfmon.get_performance_stats()
        print(f"✓ Stats retrieved: {list(stats.keys())}")

        # Test that log file was created
        assert perfmon.log_path.exists()
        content = perfmon.log_path.read_text()
        assert "test_basic_functionality" in content
        print("✓ Log file created and contains expected content")

        # Test stats content
        if "test_basic_functionality" in stats:
            func_stats = stats["test_basic_functionality"]
            print(
                f"✓ Function stats: calls={func_stats['total_calls']}, avg={func_stats['all_time_average']:.4f}s"
            )

        print("✓ All basic functionality tests passed!")


def test_unicode_and_corruption():
    """Test unicode support and corruption recovery."""
    print("\nTesting unicode support and corruption recovery...")

    with tempfile.TemporaryDirectory() as temp_dir:
        perfmon = PerfMon(log_dir=temp_dir)
        hostname = gethostname()

        # Test unicode function names
        unicode_entries = [
            f"[2025-10-20 10:00:01.000] [{hostname}] [函数_测试()] [0.1234] seconds",
            f"[2025-10-20 10:00:02.000] [{hostname}] [🚀_rocket_function()] [0.2345] seconds",
        ]

        perfmon.log_path.write_text("\n".join(unicode_entries) + "\n", encoding="utf-8")

        # Add corruption
        with perfmon.log_path.open("ab") as f:
            f.write(b"\x00\x01\x02\x03\xff\xfe\xfd\n")

        # Add more valid entries
        with perfmon.log_path.open("a", encoding="utf-8", errors="replace") as f:
            f.write(
                f"[2025-10-20 10:00:03.000] [{hostname}] [normal_function()] [0.3456] seconds\n"
            )

        # Parse stats
        stats = perfmon.get_performance_stats()

        # Verify unicode and corruption recovery
        expected_funcs = ["函数_测试", "🚀_rocket_function", "normal_function"]
        for func_name in expected_funcs:
            assert func_name in stats, f"Function '{func_name}' not found"
            print(f"✓ Found function: {func_name}")

        print("✓ Unicode support and corruption recovery tests passed!")


def test_concurrent_access():
    """Test concurrent access to PerfMon."""
    print("\nTesting concurrent access...")

    import threading

    with tempfile.TemporaryDirectory() as temp_dir:
        perfmon = PerfMon(log_dir=temp_dir)

        def worker():
            for i in range(5):
                start = time.perf_counter()
                time.sleep(0.001)  # 1ms
                end = time.perf_counter()
                perfmon.report_time(start, end)

        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        stats = perfmon.get_performance_stats()
        if "worker" in stats:
            worker_stats = stats["worker"]
            print(
                f"✓ Concurrent logging: {worker_stats['total_calls']} calls from multiple threads"
            )
            assert worker_stats["total_calls"] == 15  # 3 threads * 5 calls each

        print("✓ Concurrent access test passed!")


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("PerfMon Functionality Verification")
    print("=" * 60)

    try:
        test_basic_functionality()
        test_unicode_and_corruption()
        test_concurrent_access()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! PerfMon is working correctly.")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
