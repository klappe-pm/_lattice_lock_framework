"""
Data extractors for the pipeline.

Extractors pull data from various sources (databases, APIs, files, streams)
and convert them into a common format for processing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Iterator, Optional
import json


class SourceType(Enum):
    """Types of data sources."""
    DATABASE = "database"
    API = "api"
    FILE = "file"
    STREAM = "stream"


class RecordStatus(Enum):
    """Status of a data record."""
    PENDING = "pending"
    EXTRACTED = "extracted"
    TRANSFORMED = "transformed"
    LOADED = "loaded"
    FAILED = "failed"


@dataclass
class DataSource:
    """Configuration for a data extraction source."""
    id: int
    name: str
    source_type: SourceType
    connection_config: dict[str, Any]
    schema_definition: dict[str, Any]
    is_active: bool = True
    last_sync_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if len(self.name) < 1:
            raise ValueError("Name must not be empty")


@dataclass
class DataRecord:
    """Individual data record extracted from a source."""
    id: int
    source_id: int
    record_key: str
    raw_data: dict[str, Any]
    extracted_at: Optional[datetime] = None
    status: RecordStatus = RecordStatus.PENDING
    error_message: str = ""
    created_at: Optional[datetime] = None


class BaseExtractor(ABC):
    """Base class for all data extractors."""

    def __init__(self, source: DataSource) -> None:
        self.source = source
        self._records_extracted = 0

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the data source."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the data source."""
        pass

    @abstractmethod
    def extract(self) -> Iterator[DataRecord]:
        """Extract records from the data source."""
        pass

    @property
    def records_extracted(self) -> int:
        """Return the number of records extracted."""
        return self._records_extracted


class DatabaseExtractor(BaseExtractor):
    """Extractor for database sources."""

    def __init__(self, source: DataSource) -> None:
        super().__init__(source)
        self._connection = None
        self._next_id = 1

    def connect(self) -> bool:
        """Establish database connection."""
        self._connection = True
        return True

    def disconnect(self) -> None:
        """Close database connection."""
        self._connection = None

    def extract(self) -> Iterator[DataRecord]:
        """Extract records from database."""
        if not self._connection:
            raise RuntimeError("Not connected to database")

        sample_data = [
            {"id": 1, "name": "Record 1", "value": 100},
            {"id": 2, "name": "Record 2", "value": 200},
            {"id": 3, "name": "Record 3", "value": 300},
        ]

        for data in sample_data:
            record = DataRecord(
                id=self._next_id,
                source_id=self.source.id,
                record_key=f"db_{data['id']}",
                raw_data=data,
                extracted_at=datetime.utcnow(),
                status=RecordStatus.EXTRACTED,
            )
            self._next_id += 1
            self._records_extracted += 1
            yield record


class APIExtractor(BaseExtractor):
    """Extractor for API sources."""

    def __init__(self, source: DataSource) -> None:
        super().__init__(source)
        self._session = None
        self._next_id = 1

    def connect(self) -> bool:
        """Establish API session."""
        self._session = True
        return True

    def disconnect(self) -> None:
        """Close API session."""
        self._session = None

    def extract(self) -> Iterator[DataRecord]:
        """Extract records from API."""
        if not self._session:
            raise RuntimeError("Not connected to API")

        sample_data = [
            {"endpoint": "/users", "data": {"user_id": 1, "username": "alice"}},
            {"endpoint": "/users", "data": {"user_id": 2, "username": "bob"}},
        ]

        for item in sample_data:
            record = DataRecord(
                id=self._next_id,
                source_id=self.source.id,
                record_key=f"api_{item['data']['user_id']}",
                raw_data=item["data"],
                extracted_at=datetime.utcnow(),
                status=RecordStatus.EXTRACTED,
            )
            self._next_id += 1
            self._records_extracted += 1
            yield record


class FileExtractor(BaseExtractor):
    """Extractor for file sources."""

    def __init__(self, source: DataSource) -> None:
        super().__init__(source)
        self._file_handle = None
        self._next_id = 1

    def connect(self) -> bool:
        """Open file for reading."""
        self._file_handle = True
        return True

    def disconnect(self) -> None:
        """Close file handle."""
        self._file_handle = None

    def extract(self) -> Iterator[DataRecord]:
        """Extract records from file."""
        if not self._file_handle:
            raise RuntimeError("File not opened")

        sample_data = [
            {"line": 1, "content": "First line of data"},
            {"line": 2, "content": "Second line of data"},
        ]

        for item in sample_data:
            record = DataRecord(
                id=self._next_id,
                source_id=self.source.id,
                record_key=f"file_line_{item['line']}",
                raw_data=item,
                extracted_at=datetime.utcnow(),
                status=RecordStatus.EXTRACTED,
            )
            self._next_id += 1
            self._records_extracted += 1
            yield record


def get_extractor(source: DataSource) -> BaseExtractor:
    """Factory function to get the appropriate extractor for a source."""
    extractors = {
        SourceType.DATABASE: DatabaseExtractor,
        SourceType.API: APIExtractor,
        SourceType.FILE: FileExtractor,
    }

    extractor_class = extractors.get(source.source_type)
    if not extractor_class:
        raise ValueError(f"Unsupported source type: {source.source_type}")

    return extractor_class(source)


__all__ = [
    "SourceType",
    "RecordStatus",
    "DataSource",
    "DataRecord",
    "BaseExtractor",
    "DatabaseExtractor",
    "APIExtractor",
    "FileExtractor",
    "get_extractor",
]
