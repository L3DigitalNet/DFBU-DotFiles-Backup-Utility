#!/usr/bin/env python3
"""
Description:
    Quick test script to verify the corruption recovery functionality
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
    Test corruption recovery without pytest dependency
"""

import tempfile
from socket import gethostname
from cust_class import PerfMon


def test_corruption_recovery() -> None:
    """Test recovery from corrupted log files."""
    print("Testing corruption recovery...")

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

        print(f"Stats found: {list(stats.keys())}")

        assert "function_a" in stats, f"function_a not found in stats: {stats}"
        assert "function_b" in stats, f"function_b not found in stats: {stats}"
        assert "function_c" in stats, f"function_c not found in stats: {stats}"
        assert len(stats) == 3, f"Expected 3 stats, got {len(stats)}: {stats}"

        print("Corruption recovery test PASSED!")


if __name__ == "__main__":
    test_corruption_recovery()
