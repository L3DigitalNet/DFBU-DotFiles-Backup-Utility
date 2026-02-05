"""Tests for PreviewGenerator service."""

from pathlib import Path

import pytest

from gui.file_operations import FileOperations
from gui.preview_generator import PreviewGenerator


@pytest.fixture
def file_ops() -> FileOperations:
    """Create FileOperations instance."""
    return FileOperations(hostname="testhost")


@pytest.fixture
def preview_gen(file_ops: FileOperations, tmp_path: Path) -> PreviewGenerator:
    """Create PreviewGenerator instance."""
    return PreviewGenerator(
        file_ops=file_ops,
        mirror_base_dir=tmp_path / "mirror",
    )


@pytest.mark.unit
def test_preview_generator_detects_new_file(
    preview_gen: PreviewGenerator, tmp_path: Path
) -> None:
    """PreviewGenerator should detect new files."""
    # Create source file
    source = tmp_path / "source" / ".bashrc"
    source.parent.mkdir(parents=True)
    source.write_text("# Bash config")

    dotfiles = [
        {
            "application": "Bash",
            "paths": [str(source)],
            "enabled": True,
        }
    ]

    preview = preview_gen.generate_preview(
        dotfiles=dotfiles,
        hostname_subdir=True,
        date_subdir=False,
    )

    assert preview["new_count"] == 1
    assert preview["changed_count"] == 0
    assert len(preview["items"]) == 1
    assert preview["items"][0]["status"] == "new"
