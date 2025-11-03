---
mode: "agent"
description: "Create a new Service class for external integrations and data access"
---

# Create New Service

Create a new Service class in the `DFBU/gui/` directory for handling external integrations, file I/O, APIs, or database access.

## Overview

Services encapsulate external interactions and data access logic. They are used by ViewModels and provide a clean abstraction over external resources.

## Guidelines

### Requirements
- **ENCAPSULATE** external interactions (files, APIs, databases)
- **PROVIDE** clean interface for ViewModels
- **NO** Qt dependencies (unless absolutely necessary)
- **TYPE HINTS** on all methods and parameters
- **DOCSTRINGS** on all public APIs
- **ERROR HANDLING** with appropriate exceptions
- **PROTOCOL** interface for dependency injection

### Location
Place new service in: `DFBU/gui/[service_name].py`

### Naming Convention
- **File**: `snake_case_service.py` (e.g., `data_service.py`)
- **Class**: `PascalCaseService` (e.g., `DataService`)
- **Protocol**: `PascalCaseServiceProtocol` (e.g., `DataServiceProtocol`)

## Template Structure

### Service with Protocol
```python
"""Service for [description] operations."""
import logging
from pathlib import Path
from typing import Protocol


logger = logging.getLogger(__name__)


class DataServiceProtocol(Protocol):
    """Protocol defining data service interface.

    Use this protocol for dependency injection and testing.
    """

    def fetch_data(self) -> list[dict]:
        """Fetch data from source.

        Returns:
            List of data dictionaries.

        Raises:
            IOError: If data cannot be fetched.
        """
        ...

    def save_data(self, data: dict) -> bool:
        """Save data to source.

        Args:
            data: Data dictionary to save.

        Returns:
            True if successful, False otherwise.

        Raises:
            IOError: If data cannot be saved.
        """
        ...


class DataService:
    """Handles data persistence operations.

    Provides methods for loading and saving data from/to files.
    """

    def __init__(self, data_dir: Path):
        """Initialize service.

        Args:
            data_dir: Directory for data storage.

        Raises:
            ValueError: If data_dir is not a directory.
        """
        if not data_dir.is_dir():
            raise ValueError(f"Data directory does not exist: {data_dir}")
        self._data_dir = data_dir
        logger.info(f"DataService initialized with directory: {data_dir}")

    def fetch_data(self) -> list[dict]:
        """Fetch data from file.

        Returns:
            List of data dictionaries.

        Raises:
            IOError: If file cannot be read.
        """
        file_path = self._data_dir / "data.json"
        try:
            import json
            with open(file_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} items from {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise IOError(f"Cannot read data file: {e}") from e

    def save_data(self, data: dict) -> bool:
        """Save data to file.

        Args:
            data: Data dictionary to save.

        Returns:
            True if successful, False otherwise.

        Raises:
            IOError: If file cannot be written.
        """
        file_path = self._data_dir / "data.json"
        try:
            import json
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved data to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {e}")
            raise IOError(f"Cannot write data file: {e}") from e
```

## Service Types

### File I/O Service
```python
"""File operations service."""
import json
from pathlib import Path


class FileService:
    """Handles file I/O operations."""

    @staticmethod
    def read_json(file_path: Path) -> dict:
        """Read JSON file.

        Args:
            file_path: Path to JSON file.

        Returns:
            Parsed JSON data.

        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If file is not valid JSON.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def write_json(file_path: Path, data: dict) -> None:
        """Write JSON file.

        Args:
            file_path: Path to write JSON file.
            data: Data to write.

        Raises:
            IOError: If file cannot be written.
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def read_text(file_path: Path) -> str:
        """Read text file.

        Args:
            file_path: Path to text file.

        Returns:
            File contents as string.
        """
        return file_path.read_text(encoding='utf-8')

    @staticmethod
    def write_text(file_path: Path, content: str) -> None:
        """Write text file.

        Args:
            file_path: Path to write text file.
            content: Text content to write.
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
```

### Configuration Service
```python
"""Configuration management service."""
import json
from pathlib import Path
from typing import Any


class ConfigService:
    """Manages application configuration."""

    def __init__(self, config_file: Path):
        """Initialize configuration service.

        Args:
            config_file: Path to configuration file.
        """
        self._config_file = config_file
        self._config: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file."""
        if self._config_file.exists():
            with open(self._config_file, 'r') as f:
                self._config = json.load(f)
        else:
            self._config = self._default_config()
            self.save()

    def _default_config(self) -> dict[str, Any]:
        """Get default configuration.

        Returns:
            Default configuration dictionary.
        """
        return {
            "app_name": "My Application",
            "version": "0.1.0",
            "window_size": {"width": 800, "height": 600}
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key (supports dot notation).
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key (supports dot notation).
            value: Value to set.
        """
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def save(self) -> None:
        """Save configuration to file."""
        self._config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
```

### API Service
```python
"""API client service."""
import requests
from typing import Any


class APIServiceProtocol(Protocol):
    """Protocol for API services."""

    def get(self, endpoint: str) -> dict:
        """GET request to endpoint."""
        ...

    def post(self, endpoint: str, data: dict) -> dict:
        """POST request to endpoint."""
        ...


class APIService:
    """HTTP API client service."""

    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize API service.

        Args:
            base_url: Base URL for API.
            timeout: Request timeout in seconds.
        """
        self._base_url = base_url.rstrip('/')
        self._timeout = timeout
        self._session = requests.Session()

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        """Send GET request.

        Args:
            endpoint: API endpoint (e.g., '/users').
            params: Query parameters.

        Returns:
            Response JSON data.

        Raises:
            requests.RequestException: If request fails.
        """
        url = f"{self._base_url}{endpoint}"
        response = self._session.get(url, params=params, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: dict) -> dict:
        """Send POST request.

        Args:
            endpoint: API endpoint.
            data: Data to post.

        Returns:
            Response JSON data.

        Raises:
            requests.RequestException: If request fails.
        """
        url = f"{self._base_url}{endpoint}"
        response = self._session.post(url, json=data, timeout=self._timeout)
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close session."""
        self._session.close()
```

### Database Service
```python
"""Database service."""
import sqlite3
from pathlib import Path
from typing import Any


class DatabaseService:
    """SQLite database service."""

    def __init__(self, db_path: Path):
        """Initialize database service.

        Args:
            db_path: Path to SQLite database file.
        """
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value INTEGER
                )
            """)
            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection.

        Returns:
            SQLite connection object.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def fetch_all(self) -> list[dict]:
        """Fetch all items.

        Returns:
            List of item dictionaries.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM items")
            return [dict(row) for row in cursor.fetchall()]

    def fetch_by_id(self, item_id: int) -> dict | None:
        """Fetch item by ID.

        Args:
            item_id: Item ID to fetch.

        Returns:
            Item dictionary or None if not found.
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def insert(self, name: str, value: int) -> int:
        """Insert new item.

        Args:
            name: Item name.
            value: Item value.

        Returns:
            ID of inserted item.
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO items (name, value) VALUES (?, ?)",
                (name, value)
            )
            conn.commit()
            return cursor.lastrowid

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None
```

## Testing Services

```python
"""Tests for DataService."""
import pytest
from pathlib import Path
import tempfile
import json

from src.services.data_service import DataService


class TestDataService:
    """Test suite for DataService."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def service(self, temp_dir):
        """Create DataService instance."""
        return DataService(temp_dir)

    def test_save_and_fetch_data(self, service, temp_dir):
        """Test saving and fetching data."""
        # Arrange
        test_data = {"id": 1, "name": "test"}

        # Act
        service.save_data(test_data)
        result = service.fetch_data()

        # Assert
        assert result == [test_data]

    def test_fetch_data_raises_ioerror_when_file_missing(self, service):
        """Test that fetch_data raises IOError when file is missing."""
        # Act & Assert
        with pytest.raises(IOError):
            service.fetch_data()
```

## Integration with MVVM

ViewModels use Services:

```python
# In ViewModel
class MyViewModel(QObject):
    def __init__(self, data_service: DataServiceProtocol):
        super().__init__()
        self._data_service = data_service

    @Slot()
    def load_data(self):
        """Load data using service."""
        try:
            data = self._data_service.fetch_data()
            self.data_loaded.emit(data)
        except IOError as e:
            self.error_occurred.emit(str(e))
```

## Checklist

- [ ] Created file in `DFBU/gui/`
- [ ] Created Protocol interface
- [ ] Implemented service class
- [ ] Proper error handling
- [ ] Type hints on all methods
- [ ] Docstrings on public APIs
- [ ] Created tests in `DFBU/tests/`
- [ ] All tests pass
- [ ] Service has single responsibility
- [ ] Updated `DFBU/gui/__init__.py` if needed

## Best Practices

- **Use protocols** for dependency injection
- **Handle errors** with specific exceptions
- **Log operations** for debugging
- **Close resources** properly
- **Test with mocks** to avoid external dependencies
- **Keep services focused** (SRP)
- **Make services stateless** when possible
