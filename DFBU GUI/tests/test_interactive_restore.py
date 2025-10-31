#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Restore Test Script

Description:
    Test script to demonstrate the interactive restore functionality of
    dfbu.py by simulating user input to select restore mode and
    specify the backup directory path.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-27-2025
Date Changed: 10-27-2025
Version: 0.2.0.dev1
License: MIT

Features:
    - Simulates user input for restore mode selection
    - Tests the full restore workflow interactively
    - Uses DRY_RUN mode for safety
"""

import subprocess
from pathlib import Path


def test_interactive_restore() -> None:
    """Test the interactive restore functionality."""
    print("Testing Interactive Restore Functionality")
    print("=" * 50)

    # Prepare the input sequence
    # 2 = restore mode
    # /home/chris/GitHub/dotfiles/PC-COS = backup path
    # y = confirm path
    # n = don't proceed with restore (for safety)
    input_sequence = "2\n/home/chris/GitHub/dotfiles/PC-COS\ny\nn\n"

    # Path to the dfbu.py script
    script_path = Path(__file__).parent / "dfbu.py"
    python_path = "/home/chris/GitHub/Python/.venv/bin/python3"

    print(f"Running: {python_path} {script_path}")
    print("Input sequence:")
    print("  2 (restore mode)")
    print("  /home/chris/GitHub/dotfiles/PC-COS (backup path)")
    print("  y (confirm path)")
    print("  n (don't proceed with actual restore)")
    print("\nOutput:")
    print("-" * 50)

    try:
        # Run the script with simulated input
        result = subprocess.run(
            [python_path, str(script_path)],
            input=input_sequence,
            text=True,
            capture_output=True,
            timeout=30,
        )

        # Display the output
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print("-" * 50)
        print(f"Exit code: {result.returncode}")

        if result.returncode == 0:
            print("✅ Interactive restore test completed successfully!")
        else:
            print("❌ Interactive restore test failed!")

    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")


if __name__ == "__main__":
    test_interactive_restore()
