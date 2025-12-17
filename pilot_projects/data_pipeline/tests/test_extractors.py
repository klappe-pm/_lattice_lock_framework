"""
Tests for data extractors.

Validates extractor functionality and constraint enforcement.
"""

import pytest

from src.extractors import (
    APIExtractor,
    DatabaseExtractor,
    DataRecord,
    DataSource,
    FileExtractor,
    RecordStatus,
    SourceType,
    get_extractor,
)


class TestDataSource:
    """Tests for DataSource model."""

    def test_valid_data_source(self) -> None:
        """Test creating a valid data source."""
        source = DataSource(
            id=1,
            name="test_source",
            source_type=SourceType.DATABASE,
            connection_config={"host": "localhost"},
            schema_definition={"fields": ["id", "name"]},
        )
        assert source.name == "test_source"
        assert source.source_type == SourceType.DATABASE

    def test_empty_name_rejected(self) -> None:
        """Test that empty name is rejected."""
        with pytest.raises(ValueError, match="not be empty"):
            DataSource(
                id=1,
                name="",
                source_type=SourceType.DATABASE,
                connection_config={},
                schema_definition={},
            )


class TestDatabaseExtractor:
    """Tests for DatabaseExtractor."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.source = DataSource(
            id=1,
            name="test_db",
            source_type=SourceType.DATABASE,
            connection_config={"host": "localhost", "port": 5432},
            schema_definition={"table": "users"},
        )
        self.extractor = DatabaseExtractor(self.source)

    def test_connect(self) -> None:
        """Test connecting to database."""
        assert self.extractor.connect() is True

    def test_extract_without_connection_fails(self) -> None:
        """Test that extraction fails without connection."""
        with pytest.raises(RuntimeError, match="Not connected"):
            list(self.extractor.extract())

    def test_extract_returns_records(self) -> None:
        """Test that extraction returns records."""
        self.extractor.connect()
        records = list(self.extractor.extract())

        assert len(records) > 0
        assert all(isinstance(r, DataRecord) for r in records)
        assert all(r.status == RecordStatus.EXTRACTED for r in records)

    def test_records_extracted_count(self) -> None:
        """Test that records extracted count is tracked."""
        self.extractor.connect()
        list(self.extractor.extract())

        assert self.extractor.records_extracted > 0


class TestAPIExtractor:
    """Tests for APIExtractor."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.source = DataSource(
            id=2,
            name="test_api",
            source_type=SourceType.API,
            connection_config={"base_url": "https://api.example.com"},
            schema_definition={"endpoint": "/users"},
        )
        self.extractor = APIExtractor(self.source)

    def test_connect(self) -> None:
        """Test connecting to API."""
        assert self.extractor.connect() is True

    def test_extract_returns_records(self) -> None:
        """Test that extraction returns records."""
        self.extractor.connect()
        records = list(self.extractor.extract())

        assert len(records) > 0
        assert all(isinstance(r, DataRecord) for r in records)


class TestFileExtractor:
    """Tests for FileExtractor."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.source = DataSource(
            id=3,
            name="test_file",
            source_type=SourceType.FILE,
            connection_config={"path": "/data/input.csv"},
            schema_definition={"format": "csv"},
        )
        self.extractor = FileExtractor(self.source)

    def test_connect(self) -> None:
        """Test opening file."""
        assert self.extractor.connect() is True

    def test_extract_returns_records(self) -> None:
        """Test that extraction returns records."""
        self.extractor.connect()
        records = list(self.extractor.extract())

        assert len(records) > 0
        assert all(isinstance(r, DataRecord) for r in records)


class TestGetExtractor:
    """Tests for get_extractor factory function."""

    def test_get_database_extractor(self) -> None:
        """Test getting database extractor."""
        source = DataSource(
            id=1,
            name="db",
            source_type=SourceType.DATABASE,
            connection_config={},
            schema_definition={},
        )
        extractor = get_extractor(source)
        assert isinstance(extractor, DatabaseExtractor)

    def test_get_api_extractor(self) -> None:
        """Test getting API extractor."""
        source = DataSource(
            id=2,
            name="api",
            source_type=SourceType.API,
            connection_config={},
            schema_definition={},
        )
        extractor = get_extractor(source)
        assert isinstance(extractor, APIExtractor)

    def test_get_file_extractor(self) -> None:
        """Test getting file extractor."""
        source = DataSource(
            id=3,
            name="file",
            source_type=SourceType.FILE,
            connection_config={},
            schema_definition={},
        )
        extractor = get_extractor(source)
        assert isinstance(extractor, FileExtractor)

    def test_unsupported_source_type(self) -> None:
        """Test that unsupported source type raises error."""
        source = DataSource(
            id=4,
            name="stream",
            source_type=SourceType.STREAM,
            connection_config={},
            schema_definition={},
        )
        with pytest.raises(ValueError, match="Unsupported"):
            get_extractor(source)
