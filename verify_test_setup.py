#!/usr/bin/env python3
"""
Testing Infrastructure Verification Script

This script verifies that the testing infrastructure is correctly set up
according to test.prompt.md guidelines.

Usage:
    python verify_test_setup.py

Exit Codes:
    0 - All checks passed
    1 - One or more checks failed
"""

from __future__ import annotations

import sys
from pathlib import Path


def check_file_exists(filepath: Path, description: str) -> bool:
    """Check if a file exists."""
    if filepath.exists():
        print(f"✅ {description}: {filepath}")
        return True
    print(f"❌ {description} NOT FOUND: {filepath}")
    return False


def check_no_tests_in_root() -> bool:
    """Check that there are no test files in project root."""
    root = Path(__file__).parent
    test_files = list(root.glob("test_*.py"))

    if not test_files:
        print("✅ No test files in project root (correct)")
        return True

    print(f"❌ Found {len(test_files)} test files in project root:")
    for f in test_files:
        print(f"   - {f.name}")
    return False


def check_conftest_has_qapp() -> bool:
    """Check that conftest.py has QApplication fixture."""
    conftest = Path(__file__).parent / "DFBU" / "tests" / "conftest.py"

    if not conftest.exists():
        print("❌ conftest.py not found")
        return False

    content = conftest.read_text()
    if "def qapp" in content and "QApplication" in content:
        print("✅ conftest.py has QApplication fixture")
        return True

    print("❌ conftest.py missing QApplication fixture")
    return False


def check_pyproject_pytest_config() -> bool:
    """Check that pyproject.toml has proper pytest configuration."""
    pyproject = Path(__file__).parent / "pyproject.toml"

    if not pyproject.exists():
        print("❌ pyproject.toml not found")
        return False

    content = pyproject.read_text()

    checks = [
        ('testpaths = ["DFBU/tests"]', "testpaths configured"),
        ("pytest-qt", "pytest-qt in dependencies"),
        ("pytest-mock", "pytest-mock in dependencies"),
        ("pytest-cov", "pytest-cov in dependencies"),
    ]

    all_passed = True
    for check_str, description in checks:
        if check_str in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} missing")
            all_passed = False

    return all_passed


def main() -> int:
    """Run all verification checks."""
    print("=" * 70)
    print("Testing Infrastructure Verification")
    print("=" * 70)
    print()

    checks = [
        (
            "conftest.py exists",
            lambda: check_file_exists(
                Path(__file__).parent / "DFBU" / "tests" / "conftest.py",
                "DFBU/tests/conftest.py",
            ),
        ),
        (
            "test_viewmodel_template.py exists",
            lambda: check_file_exists(
                Path(__file__).parent / "DFBU" / "tests" / "test_viewmodel_template.py",
                "DFBU/tests/test_viewmodel_template.py",
            ),
        ),
        ("No tests in root", check_no_tests_in_root),
        ("QApplication fixture", check_conftest_has_qapp),
        ("pytest configuration", check_pyproject_pytest_config),
    ]

    results = []
    for name, check_func in checks:
        print(f"\nChecking: {name}")
        print("-" * 70)
        results.append(check_func())
        print()

    print("=" * 70)
    print("Summary")
    print("=" * 70)

    passed = sum(results)
    total = len(results)

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n✅ All checks passed! Testing infrastructure is properly set up.")
        return 0

    print(f"\n❌ {total - passed} check(s) failed. Please review the output above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
