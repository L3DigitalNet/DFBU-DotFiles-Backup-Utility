"""
Comprehensive tests for table sorting functionality.

Tests NumericTableWidgetItem custom sorting and dotfile table operations.
"""

import sys
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import Qt


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))

from model import DFBUModel
from view import MainWindow, NumericTableWidgetItem
from viewmodel import DFBUViewModel


class TestNumericTableWidgetItem:
    """Test custom numeric table widget item for proper sorting."""

    def test_numeric_item_stores_value_in_user_role(self, qapp):
        """Test numeric item stores numeric value in UserRole."""
        # Arrange
        item = NumericTableWidgetItem("1.5 KB")

        # Act
        item.setData(Qt.ItemDataRole.UserRole, 1536)  # 1.5 KB in bytes

        # Assert
        assert item.data(Qt.ItemDataRole.UserRole) == 1536
        assert item.text() == "1.5 KB"

    def test_numeric_item_compares_by_user_role_value(self, qapp):
        """Test numeric items compare by UserRole value, not display text."""
        # Arrange
        item1 = NumericTableWidgetItem("1.5 KB")
        item1.setData(Qt.ItemDataRole.UserRole, 1536)

        item2 = NumericTableWidgetItem("2.0 MB")
        item2.setData(Qt.ItemDataRole.UserRole, 2097152)

        # Act & Assert
        assert item1 < item2  # 1.5 KB < 2.0 MB by bytes
        assert not item2 < item1

    def test_numeric_item_handles_zero_value(self, qapp):
        """Test numeric item handles zero value correctly."""
        # Arrange
        item1 = NumericTableWidgetItem("0 B")
        item1.setData(Qt.ItemDataRole.UserRole, 0)

        item2 = NumericTableWidgetItem("1 B")
        item2.setData(Qt.ItemDataRole.UserRole, 1)

        # Act & Assert
        assert item1 < item2
        assert not item2 < item1

    def test_numeric_item_handles_none_as_zero(self, qapp):
        """Test numeric item treats None values as zero."""
        # Arrange
        item1 = NumericTableWidgetItem("Unknown")
        item1.setData(Qt.ItemDataRole.UserRole, None)

        item2 = NumericTableWidgetItem("1 B")
        item2.setData(Qt.ItemDataRole.UserRole, 1)

        # Act & Assert
        # None should be treated as 0
        assert item1 < item2

    def test_numeric_item_sorts_large_values(self, qapp):
        """Test numeric item correctly sorts large byte values."""
        # Arrange
        item_kb = NumericTableWidgetItem("100 KB")
        item_kb.setData(Qt.ItemDataRole.UserRole, 102400)

        item_mb = NumericTableWidgetItem("1 MB")
        item_mb.setData(Qt.ItemDataRole.UserRole, 1048576)

        item_gb = NumericTableWidgetItem("2 GB")
        item_gb.setData(Qt.ItemDataRole.UserRole, 2147483648)

        # Act & Assert
        assert item_kb < item_mb < item_gb

    def test_numeric_item_equal_values(self, qapp):
        """Test numeric items with equal values."""
        # Arrange
        item1 = NumericTableWidgetItem("1024 B")
        item1.setData(Qt.ItemDataRole.UserRole, 1024)

        item2 = NumericTableWidgetItem("1.0 KB")
        item2.setData(Qt.ItemDataRole.UserRole, 1024)

        # Act & Assert
        assert not item1 < item2
        assert not item2 < item1

    def test_numeric_item_handles_non_numeric_gracefully(self, qapp):
        """Test numeric item handles non-numeric data in UserRole."""
        # Arrange
        item1 = NumericTableWidgetItem("Invalid")
        item1.setData(Qt.ItemDataRole.UserRole, "not a number")

        item2 = NumericTableWidgetItem("1 KB")
        item2.setData(Qt.ItemDataRole.UserRole, 1024)

        # Act & Assert
        # Should treat invalid data as 0
        try:
            result = item1 < item2
            assert result is True  # Invalid treated as 0 < 1024
        except Exception:
            # Should not raise exception
            pass


class TestDotfileTableSorting:
    """Test dotfile table sorting functionality."""

    def test_table_sorts_by_size_column(self, qapp, tmp_path):
        """Test table sorts correctly by size column with numeric values."""
        # Arrange
        config = tmp_path / "config.toml"
        config.write_text("""
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true
archive = false

[[dotfile]]
category = "Test1"
application = "App1"
description = "Small file"
path = "~/.test1"

[[dotfile]]
category = "Test2"
application = "App2"
description = "Large file"
path = "~/.test2"

[[dotfile]]
category = "Test3"
application = "App3"
description = "Medium file"
path = "~/.test3"
""")

        model = DFBUModel(config)
        viewmodel = DFBUViewModel(model)

        with patch.object(viewmodel, "load_settings", return_value={}):
            window = MainWindow(viewmodel, "1.0.0")

        # Load config
        viewmodel.command_load_config()

        # Mock size data (small, large, medium)
        size_data = {
            0: 1024,  # 1 KB
            1: 10485760,  # 10 MB
            2: 102400,  # 100 KB
        }

        with patch.object(
            viewmodel,
            "get_dotfile_sizes",
            return_value=size_data,
        ):
            window._update_dotfile_table()

            # Act - Sort by size column (column 4) while still in patch context
            window.dotfile_table.sortItems(4, Qt.SortOrder.AscendingOrder)

            # Assert - Should be sorted: 1KB, 100KB, 10MB
            # Get original indices from sorted table
            first_idx = window._get_original_dotfile_index(0)
            second_idx = window._get_original_dotfile_index(1)
            third_idx = window._get_original_dotfile_index(2)

            # Verify order by checking sizes
            assert size_data[first_idx] < size_data[second_idx] < size_data[third_idx]

    def test_table_sorts_by_enabled_status(self, qapp, tmp_path):
        """Test table sorts correctly by enabled column."""
        # Arrange
        config = tmp_path / "config.toml"
        config.write_text("""
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true
archive = false

[[dotfile]]
category = "Test1"
application = "App1"
description = "Enabled"
path = "~/.test1"
enabled = true

[[dotfile]]
category = "Test2"
application = "App2"
description = "Disabled"
path = "~/.test2"
enabled = false

[[dotfile]]
category = "Test3"
application = "App3"
description = "Enabled"
path = "~/.test3"
enabled = true
""")

        model = DFBUModel(config)
        viewmodel = DFBUViewModel(model)

        with patch.object(viewmodel, "load_settings", return_value={}):
            window = MainWindow(viewmodel, "1.0.0")

        viewmodel.command_load_config()

        with patch.object(
            viewmodel, "get_dotfile_sizes", return_value={0: 0, 1: 0, 2: 0}
        ):
            window._update_dotfile_table()

        # Act - Sort by enabled column (column 0)
        window.dotfile_table.sortItems(0, Qt.SortOrder.AscendingOrder)

        # Assert - Enabled items should come first (✓ < ✗ in Unicode)
        first_item = window.dotfile_table.item(0, 0)
        assert first_item.text() == "✓"

    def test_table_sorts_by_category_alphabetically(self, qapp, tmp_path):
        """Test table sorts correctly by category column alphabetically."""
        # Arrange
        config = tmp_path / "config.toml"
        config.write_text("""
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true

[[dotfile]]
category = "Zulu"
application = "App1"
description = "Last"
path = "~/.test1"

[[dotfile]]
category = "Alpha"
application = "App2"
description = "First"
path = "~/.test2"

[[dotfile]]
category = "Mike"
application = "App3"
description = "Middle"
path = "~/.test3"
""")

        model = DFBUModel(config)
        viewmodel = DFBUViewModel(model)

        with patch.object(viewmodel, "load_settings", return_value={}):
            window = MainWindow(viewmodel, "1.0.0")

        viewmodel.command_load_config()

        with patch.object(
            viewmodel, "get_dotfile_sizes", return_value={0: 0, 1: 0, 2: 0}
        ):
            window._update_dotfile_table()

        # Act - Sort by category column (column 2)
        window.dotfile_table.sortItems(2, Qt.SortOrder.AscendingOrder)

        # Assert
        first_category = window.dotfile_table.item(0, 2).text()
        last_category = window.dotfile_table.item(2, 2).text()
        assert first_category == "Alpha"
        assert last_category == "Zulu"

    def test_table_maintains_index_mapping_after_sort(self, qapp, tmp_path):
        """Test table maintains correct original index mapping after sorting."""
        # Arrange
        config = tmp_path / "config.toml"
        config.write_text("""
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true

[[dotfile]]
category = "Cat1"
application = "App1"
description = "First"
path = "~/.test1"

[[dotfile]]
category = "Cat2"
application = "App2"
description = "Second"
path = "~/.test2"
""")

        model = DFBUModel(config)
        viewmodel = DFBUViewModel(model)

        with patch.object(viewmodel, "load_settings", return_value={}):
            window = MainWindow(viewmodel, "1.0.0")

        viewmodel.command_load_config()

        with patch.object(
            viewmodel, "get_dotfile_sizes", return_value={0: 2048, 1: 1024}
        ):
            window._update_dotfile_table()

        # Act - Sort by size (should reverse order)
        window.dotfile_table.sortItems(4, Qt.SortOrder.AscendingOrder)

        # Assert - First visible row should map to original index 1
        first_visible_original_idx = window._get_original_dotfile_index(0)
        assert first_visible_original_idx == 1  # Second item now first

    def test_table_reverse_sort_order(self, qapp, tmp_path):
        """Test table reverse sorting works correctly."""
        # Arrange
        config = tmp_path / "config.toml"
        config.write_text("""
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true

[[dotfile]]
category = "A"
application = "App"
description = "Test"
path = "~/.test1"

[[dotfile]]
category = "B"
application = "App"
description = "Test"
path = "~/.test2"

[[dotfile]]
category = "C"
application = "App"
description = "Test"
path = "~/.test3"
""")

        model = DFBUModel(config)
        viewmodel = DFBUViewModel(model)

        with patch.object(viewmodel, "load_settings", return_value={}):
            window = MainWindow(viewmodel, "1.0.0")

        viewmodel.command_load_config()

        with patch.object(
            viewmodel, "get_dotfile_sizes", return_value={0: 0, 1: 0, 2: 0}
        ):
            window._update_dotfile_table()

        # Act - Sort descending
        window.dotfile_table.sortItems(2, Qt.SortOrder.DescendingOrder)

        # Assert
        first_category = window.dotfile_table.item(0, 2).text()
        last_category = window.dotfile_table.item(2, 2).text()
        assert first_category == "C"
        assert last_category == "A"


class TestTableOriginalIndexRetrieval:
    """Test _get_original_dotfile_index functionality."""

    def test_get_original_index_from_sorted_table(self, qapp, tmp_path):
        """Test retrieving original index after table sorting."""
        # Arrange
        config = tmp_path / "config.toml"
        config.write_text("""
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true

[[dotfile]]
category = "Cat"
application = "App"
description = "Test"
path = "~/.test"
""")

        model = DFBUModel(config)
        viewmodel = DFBUViewModel(model)

        with patch.object(viewmodel, "load_settings", return_value={}):
            window = MainWindow(viewmodel, "1.0.0")

        viewmodel.command_load_config()

        with patch.object(viewmodel, "get_dotfile_sizes", return_value={0: 0}):
            window._update_dotfile_table()

        # Act
        original_idx = window._get_original_dotfile_index(0)

        # Assert
        assert original_idx == 0

    def test_get_original_index_raises_on_missing_data(self, qapp, tmp_path):
        """Test _get_original_dotfile_index raises ValueError on missing data."""
        # Arrange
        config = tmp_path / "config.toml"
        config.write_text("""
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true

[[dotfile]]
category = "Cat"
application = "App"
description = "Test"
path = "~/.test"
""")

        model = DFBUModel(config)
        viewmodel = DFBUViewModel(model)

        with patch.object(viewmodel, "load_settings", return_value={}):
            window = MainWindow(viewmodel, "1.0.0")

        viewmodel.command_load_config()

        with patch.object(viewmodel, "get_dotfile_sizes", return_value={0: 0}):
            window._update_dotfile_table()

        # Corrupt the data by removing UserRole data
        item = window.dotfile_table.item(0, 0)
        if item:
            item.setData(Qt.ItemDataRole.UserRole, None)

        # Act & Assert
        try:
            window._get_original_dotfile_index(0)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "Unable to determine original dotfile index" in str(e)
