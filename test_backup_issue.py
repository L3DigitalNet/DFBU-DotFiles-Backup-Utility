#!/usr/bin/env python3
"""
Quick test to diagnose backup issue
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent / "DFBU" / "gui"))

from model import DFBUModel


# Test with default config
config_path = Path(__file__).parent / "DFBU" / "data" / "dfbu-config.toml"
print(f"Testing with config: {config_path}")
print(f"Config exists: {config_path.exists()}")

model = DFBUModel(config_path)

# Load config
success, error = model.load_config()
print(f"\nLoad config result: success={success}, error='{error}'")

if success:
    # Check options
    print("\nOptions:")
    print(f"  mirror: {model.options.get('mirror', 'NOT SET')}")
    print(f"  archive: {model.options.get('archive', 'NOT SET')}")
    print(f"  mirror_dir: {model.mirror_base_dir}")
    print(f"  archive_dir: {model.archive_base_dir}")

    # Check dotfiles
    print(f"\nDotfile count: {model.get_dotfile_count()}")

    # Check first few dotfiles
    for i in range(min(3, model.get_dotfile_count())):
        dotfile = model.get_dotfile_by_index(i)
        if dotfile:
            print(f"\nDotfile {i}:")
            print(f"  Category: {dotfile.get('category', 'N/A')}")
            print(f"  Application: {dotfile.get('application', 'N/A')}")
            print(f"  Paths: {dotfile.get('paths', dotfile.get('path', 'N/A'))}")
            print(f"  Enabled: {dotfile.get('enabled', True)}")

    # Validate paths
    print("\nValidating dotfile paths...")
    validation_results = model.validate_dotfile_paths()
    print(f"Validation results: {len(validation_results)} entries")

    # Count valid items
    valid_count = sum(1 for v in validation_results.values() if v[0])
    print(f"Valid items found: {valid_count}")

    # Show first few validation results
    for i, (idx, result) in enumerate(list(validation_results.items())[:5]):
        exists, is_dir, type_str = result
        dotfile = model.get_dotfile_by_index(idx)
        if dotfile:
            paths = dotfile.get("paths", [dotfile.get("path", "")])
            print(
                f"  [{idx}] {paths}: exists={exists}, is_dir={is_dir}, type={type_str}"
            )
