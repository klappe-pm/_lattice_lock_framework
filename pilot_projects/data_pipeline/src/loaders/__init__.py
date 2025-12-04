"""
Data loaders for the pipeline.

Loaders write transformed data to target destinations
(databases, data warehouses, files, APIs).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import json


class TargetType(Enum):
    """Types of load targets."""
    DATABASE = "database"
    DATA_WAREHOUSE = "data_warehouse"
    FILE = "file"
    API = "api"


class LoadMode(Enum):
    """Modes for loading data."""
    APPEND = "append"
    UPSERT = "upsert"
    REPLACE = "replace"
    MERGE = "merge"


class JobStatus(Enum):
    """Status of a load job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class LoadTarget:
    """Configuration for a data load destination."""
    id: int
    name: str
    target_type: TargetType
    connection_config: dict[str, Any]
    table_name: str
    load_mode: LoadMode = LoadMode.APPEND
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class LoadJob:
    """Record of a data load operation."""
    id: int
    target_id: int
    records_loaded: int = 0
    records_failed: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: JobStatus = JobStatus.PENDING
    error_message: str = ""
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        if self.records_loaded < 0:
            raise ValueError("Records loaded cannot be negative")
        if self.records_failed < 0:
            raise ValueError("Records failed cannot be negative")


class BaseLoader(ABC):
    """Base class for all data loaders."""

    def __init__(self, target: LoadTarget) -> None:
        self.target = target
        self._records_loaded = 0
        self._records_failed = 0

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the target."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection to the target."""
        pass

    @abstractmethod
    def load(self, records: list[dict[str, Any]]) -> LoadJob:
        """Load records to the target."""
        pass

    @property
    def records_loaded(self) -> int:
        """Return the number of records loaded."""
        return self._records_loaded

    @property
    def records_failed(self) -> int:
        """Return the number of records that failed to load."""
        return self._records_failed


class DatabaseLoader(BaseLoader):
    """Loader for database targets."""

    def __init__(self, target: LoadTarget) -> None:
        super().__init__(target)
        self._connection = None
        self._next_job_id = 1

    def connect(self) -> bool:
        """Establish database connection."""
        self._connection = True
        return True

    def disconnect(self) -> None:
        """Close database connection."""
        self._connection = None

    def load(self, records: list[dict[str, Any]]) -> LoadJob:
        """Load records to database."""
        if not self._connection:
            raise RuntimeError("Not connected to database")

        job = LoadJob(
            id=self._next_job_id,
            target_id=self.target.id,
            started_at=datetime.utcnow(),
            status=JobStatus.RUNNING,
        )
        self._next_job_id += 1

        try:
            for record in records:
                self._records_loaded += 1
                job.records_loaded += 1

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()

        return job


class DataWarehouseLoader(BaseLoader):
    """Loader for data warehouse targets."""

    def __init__(self, target: LoadTarget) -> None:
        super().__init__(target)
        self._connection = None
        self._next_job_id = 1

    def connect(self) -> bool:
        """Establish data warehouse connection."""
        self._connection = True
        return True

    def disconnect(self) -> None:
        """Close data warehouse connection."""
        self._connection = None

    def load(self, records: list[dict[str, Any]]) -> LoadJob:
        """Load records to data warehouse."""
        if not self._connection:
            raise RuntimeError("Not connected to data warehouse")

        job = LoadJob(
            id=self._next_job_id,
            target_id=self.target.id,
            started_at=datetime.utcnow(),
            status=JobStatus.RUNNING,
        )
        self._next_job_id += 1

        try:
            batch_size = 1000
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                for record in batch:
                    self._records_loaded += 1
                    job.records_loaded += 1

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()

        return job


class FileLoader(BaseLoader):
    """Loader for file targets."""

    def __init__(self, target: LoadTarget) -> None:
        super().__init__(target)
        self._file_handle = None
        self._next_job_id = 1

    def connect(self) -> bool:
        """Open file for writing."""
        self._file_handle = True
        return True

    def disconnect(self) -> None:
        """Close file handle."""
        self._file_handle = None

    def load(self, records: list[dict[str, Any]]) -> LoadJob:
        """Load records to file."""
        if not self._file_handle:
            raise RuntimeError("File not opened")

        job = LoadJob(
            id=self._next_job_id,
            target_id=self.target.id,
            started_at=datetime.utcnow(),
            status=JobStatus.RUNNING,
        )
        self._next_job_id += 1

        try:
            for record in records:
                self._records_loaded += 1
                job.records_loaded += 1

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()

        return job


def get_loader(target: LoadTarget) -> BaseLoader:
    """Factory function to get the appropriate loader for a target."""
    loaders = {
        TargetType.DATABASE: DatabaseLoader,
        TargetType.DATA_WAREHOUSE: DataWarehouseLoader,
        TargetType.FILE: FileLoader,
    }

    loader_class = loaders.get(target.target_type)
    if not loader_class:
        raise ValueError(f"Unsupported target type: {target.target_type}")

    return loader_class(target)


__all__ = [
    "TargetType",
    "LoadMode",
    "JobStatus",
    "LoadTarget",
    "LoadJob",
    "BaseLoader",
    "DatabaseLoader",
    "DataWarehouseLoader",
    "FileLoader",
    "get_loader",
]
